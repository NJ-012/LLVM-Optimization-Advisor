import os
import platform
import shutil
import subprocess
import sys
import time
import uuid
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pandas as pd

from .benchmarks import (
    calculate_speedup,
    compile_one,
    compile_reference,
    collect as collect_data,
    measure,
    outputs_match,
    run_once,
)
from .config import (
    BENCH,
    CONFIGS,
    EXPERIMENTS,
    FEATURES,
    FEEDBACK,
    FEEDBACK_QUARANTINE,
    RESULTS,
)
from .data_validation import (
    append_unseen_measurements,
    feedback_quarantine_rows,
    parse_correctness,
    validate_measurements,
)
from .features import clang_path, extract


def doctor():
    print("Adaptive LLVM Advisor — system check")
    print("Platform:", platform.platform())
    print("Python:", sys.version.split()[0])
    print("Python executable:", sys.executable)
    toolchain_ok = True
    for tool in ("clang", "opt", "llvm-config"):
        executable = shutil.which(tool)
        print(f"{tool}:", executable or "NOT FOUND")
        if executable:
            process = subprocess.run(
                [executable, "--version"], capture_output=True, text=True
            )
            if process.returncode:
                toolchain_ok = False
                print(" ", process.stderr.strip() or "version check failed")
            else:
                print(" ", process.stdout.splitlines()[0] if process.stdout else "available")
        elif tool == "clang":
            toolchain_ok = False
    packages_ok = True
    for package, distribution in (
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sklearn", "scikit-learn"),
        ("joblib", "joblib"),
        ("xgboost", "xgboost"),
        ("matplotlib", "matplotlib"),
        ("streamlit", "streamlit"),
        ("altair", "altair"),
    ):
        try:
            __import__(package)
            print(f"{package}: {version(distribution)}")
        except (ImportError, PackageNotFoundError):
            optional = package == "xgboost"
            print(f"{package}: not installed" + (" (optional)" if optional else ""))
            if not optional:
                packages_ok = False
    print("Benchmarks:", len(list(BENCH.glob("*.c"))))
    print("Configurations:", ", ".join(CONFIGS))
    if not shutil.which("clang"):
        print("Install Clang/LLVM. Ubuntu/WSL: sudo apt install clang llvm build-essential")
    return toolchain_ok and packages_ok


def collect():
    return collect_data() is True


def train():
    from .model import train as train_model

    train_model()
    return True


def _features(benchmark):
    source = BENCH / (benchmark + ".c")
    if not source.exists():
        available = ", ".join(path.stem for path in BENCH.glob("*.c"))
        raise RuntimeError(f"Unknown benchmark {benchmark}. Available: {available}")
    return source, extract(source)


def recommend(benchmark):
    from .model import load, predict_action
    from .recommendation import use_safe_fallback

    _, features = _features(benchmark)
    bundle = load()
    action, predictions = predict_action(benchmark, features, bundle=bundle)
    print(
        f"Benchmark: {benchmark}\nRecommended configuration: {action}\n"
        f"Predicted speedup vs O3 (model estimate): {predictions[action]:.3f}x"
    )
    if use_safe_fallback(bundle):
        print(
            "Warning: grouped validation did not beat the grouped median baseline "
            "or is unavailable; conservative policy selects O3."
        )
    print("Predictions are estimates; the actual run decides whether the choice helped.")
    print("All candidate estimates:")
    for configuration, prediction in sorted(
        predictions.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"  {configuration:18s} {prediction:.3f}x")
    return True


def _write_csv_atomically(frame, target):
    temporary = target.with_name(f".{target.stem}.{uuid.uuid4().hex}.tmp")
    try:
        frame.to_csv(temporary, index=False)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def feedback(benchmark):
    from .model import load, predict_action
    from .recommendation import use_safe_fallback

    source, features = _features(benchmark)
    bundle = load()
    action, predictions = predict_action(benchmark, features, bundle=bundle)
    if use_safe_fallback(bundle):
        print("Warning: conservative fallback selected O3 for this measurement.")

    if FEEDBACK.exists():
        existing = pd.read_csv(FEEDBACK)
        errors = validate_measurements(existing, "feedback")
        if errors:
            raise RuntimeError(
                "Existing feedback must be validated/quarantined before a new record "
                "can be appended. Run `python run.py quarantine-feedback`.\n"
                + "\n".join(errors[:10])
            )
    else:
        existing = pd.DataFrame()

    context_id = uuid.uuid4().hex
    compiler = clang_path()
    compiler_version = subprocess.run(
        [compiler, "--version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]
    base = RESULTS / f"{benchmark}_feedback_O3"
    correctness_reference = RESULTS / f"{benchmark}_feedback_correctness_O0"
    compile_reference(source, correctness_reference)
    expected_output = run_once(correctness_reference)
    compile_one(source, "O3", base)
    baseline_warmup = run_once(base)
    if not outputs_match(expected_output, baseline_warmup):
        raise RuntimeError(f"Correctness failed before timing {benchmark}/O3.")

    candidate = base
    candidate_warmup = baseline_warmup
    if action != "O3":
        candidate = RESULTS / f"{benchmark}_feedback_{action}"
        compile_one(source, action, candidate)
        candidate_warmup = run_once(candidate)
        if not outputs_match(expected_output, candidate_warmup):
            raise RuntimeError(
                f"Correctness failed before timing {benchmark}/{action}; "
                "no candidate timing was accepted."
            )

    baseline_runtime, baseline_mad, baseline_output = measure(base, 7)
    if action == "O3":
        # One O3 sample set is both the candidate and its own paired baseline.
        candidate_runtime = baseline_runtime
        candidate_mad = baseline_mad
        candidate_output = baseline_output
    else:
        candidate_runtime, candidate_mad, candidate_output = measure(candidate, 7)
    correct = all(
        outputs_match(expected_output, output)
        for output in (
            baseline_warmup,
            candidate_warmup,
            baseline_output,
            candidate_output,
        )
    )
    speedup = calculate_speedup(baseline_runtime, candidate_runtime, correct)
    row = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "program_id": benchmark,
        "configuration": action,
        "baseline_o3_seconds": baseline_runtime,
        "runtime_seconds": candidate_runtime,
        "speedup_vs_o3": speedup,
        "correctness": correct,
        "iteration": 1,
        "predicted_speedup": predictions[action],
        "measurement_context_id": context_id,
        "llvm_version": compiler_version,
        "compiler_flags": " ".join(CONFIGS[action]),
        "baseline_compiler_flags": " ".join(CONFIGS["O3"]),
        "platform": platform.platform(),
        "input_profile": "fixed source-defined input",
        "measurement_repeats": 7,
        "baseline_mad_seconds": baseline_mad,
        "runtime_mad_seconds": candidate_mad,
        "measurement_source": "feedback",
        **features,
    }
    frame = pd.concat([existing, pd.DataFrame([row])], ignore_index=True, sort=False)
    errors = validate_measurements(frame, "feedback")
    if errors:
        raise RuntimeError("New feedback record failed validation:\n" + "\n".join(errors[:10]))
    _write_csv_atomically(frame, FEEDBACK)
    print(f"Selected: {action}; correctness: {'PASS' if correct else 'FAIL'}")
    print(
        f"O3 median: {baseline_runtime:.6f}s (MAD {baseline_mad:.6f}s); "
        f"selected median: {candidate_runtime:.6f}s (MAD {candidate_mad:.6f}s)"
    )
    print(f"Measured speedup: {speedup:.3f}x" if speedup else "Speedup unavailable")
    print(f"Measurement context: {context_id}")
    print(f"Feedback saved: {FEEDBACK}")
    print(
        "Feedback is logged separately. To use it in training, run "
        "`python run.py incorporate-feedback`, then `python run.py train`."
    )
    return True


def quarantine_feedback():
    if not FEEDBACK.exists():
        print("No feedback CSV exists; nothing to quarantine.")
        return True
    original_bytes = FEEDBACK.read_bytes()
    frame = pd.read_csv(FEEDBACK)
    indices, reasons = feedback_quarantine_rows(frame)
    if not indices:
        print("All feedback rows pass validation; nothing was quarantined.")
        return True

    backup = FEEDBACK.with_name("feedback.pre_quarantine.csv")
    if not backup.exists():
        backup.write_bytes(original_bytes)
    invalid = frame.loc[sorted(indices)].copy()
    invalid["quarantine_reason"] = [reasons.get(index, "Feedback validation failed.") for index in invalid.index]
    if FEEDBACK_QUARANTINE.exists():
        prior = pd.read_csv(FEEDBACK_QUARANTINE)
        invalid = pd.concat([prior, invalid], ignore_index=True, sort=False)
    valid = frame.drop(index=list(indices))
    _write_csv_atomically(invalid, FEEDBACK_QUARANTINE)
    _write_csv_atomically(valid, FEEDBACK)
    print(f"Preserved the original file byte-for-byte at {backup}.")
    print(f"Quarantined {len(indices)} invalid row(s) at {FEEDBACK_QUARANTINE}.")
    print(f"Kept {len(valid)} validated row(s) in {FEEDBACK}.")
    print("Regenerate quarantined measurements with `python run.py feedback --benchmark <name>`.")
    return True


def incorporate_feedback():
    if not FEEDBACK.exists():
        raise RuntimeError(
            "No feedback yet. Run `python run.py feedback --benchmark matrix_multiply` first."
        )
    base = pd.read_csv(EXPERIMENTS) if EXPERIMENTS.exists() else pd.DataFrame()
    if not base.empty:
        base_errors = validate_measurements(base, "experiments")
        if base_errors:
            raise RuntimeError(
                "Invalid experiment data:\n" + "\n".join(base_errors[:20])
            )
    feedback_frame = pd.read_csv(FEEDBACK)
    errors = validate_measurements(feedback_frame, "feedback")
    if errors:
        raise RuntimeError(
            "Invalid feedback data; no records were incorporated:\n"
            + "\n".join(errors[:20])
            + "\nUse `python run.py quarantine-feedback` to preserve and isolate invalid legacy rows."
        )

    rows = []
    for _, row in feedback_frame.iterrows():
        if (
            parse_correctness(row.get("correctness")) is not True
            or pd.isna(row.get("speedup_vs_o3"))
        ):
            continue
        measurement = {
            "program_id": row["program_id"],
            "benchmark_file": row["program_id"] + ".c",
            "configuration": row["configuration"],
            "runtime_seconds": row["runtime_seconds"],
            "baseline_o3_seconds": row["baseline_o3_seconds"],
            "speedup_vs_o3": row["speedup_vs_o3"],
            "correctness": True,
            "llvm_version": row["llvm_version"],
            "platform": row["platform"],
            "input_profile": row["input_profile"],
            "measurement_repeats": row["measurement_repeats"],
            "measurement_context_id": row["measurement_context_id"],
            "compiler_flags": row["compiler_flags"],
            "baseline_compiler_flags": row["baseline_compiler_flags"],
            "baseline_mad_seconds": row["baseline_mad_seconds"],
            "runtime_mad_seconds": row["runtime_mad_seconds"],
            "measurement_source": "feedback",
            **{feature: row[feature] for feature in FEATURES},
        }
        rows.append(measurement)
    if rows:
        new_rows = pd.DataFrame(rows)
        updated = append_unseen_measurements(base, new_rows)
        added = len(updated) - len(base)
        if added == 0:
            print("No new valid feedback observations to incorporate; existing observations were preserved.")
        else:
            _write_csv_atomically(updated, EXPERIMENTS)
            print(f"Incorporated {added} new feedback observation(s) into {EXPERIMENTS}.")
    else:
        print("No correct, labeled feedback rows to incorporate.")
    return True


def evaluate():
    from .model import evaluate_frame

    if not EXPERIMENTS.exists():
        raise RuntimeError("Run collect first")
    frame = pd.read_csv(EXPERIMENTS)
    errors = validate_measurements(frame, "experiments")
    if errors:
        raise RuntimeError("Invalid experiment data:\n" + "\n".join(errors[:20]))
    report = evaluate_frame(frame)
    print("Evaluation summary (program-grouped, held-out programs)")
    print(f"Programs: {report['programs']}; observations: {report['observations']}")
    print(f"Grouped folds: {report['folds']}")
    if report["folds"] < 2:
        print("Grouped CV unavailable: at least four distinct programs are required.")
        return True
    print(
        f"{report['group_cv_model_family']} grouped CV MAE (log speedup): "
        f"{report['group_cv_log_speedup_mae']:.4f}"
    )
    print(
        "Grouped median baseline MAE (same folds/target): "
        f"{report['group_cv_median_baseline_log_speedup_mae']:.4f}"
    )
    print(f"Grouped top-1 configuration accuracy: {report['group_cv_top1_accuracy']:.3f}")
    print(f"O3 policy top-1 accuracy: {report['group_cv_o3_policy_top1_accuracy']:.3f}")
    if report["group_cv_log_speedup_mae"] >= report["group_cv_median_baseline_log_speedup_mae"]:
        print(
            "Warning: model MAE did not beat the grouped median baseline; "
            "recommendations use the conservative O3 fallback."
        )
    print("No generalization or performance improvement is claimed from this small dataset.")
    return True


def show_dataset():
    print("Dataset source: locally executed benchmark programs in benchmarks/.")
    print("This package includes 11 small, deterministic C benchmark kernels.")
    print("A machine-specific data set is generated by `python run.py collect`.")
    print("\nIncluded benchmarks:")
    for source in sorted(BENCH.glob("*.c")):
        print(" - " + source.stem)
    return True


def run_all():
    benchmark = sorted(BENCH.glob("*.c"))[0].stem
    stages = [
        ("System diagnostic", doctor),
        ("Benchmark collection", collect),
        ("Model training", train),
        ("Grouped evaluation", evaluate),
        ("Recommendation", lambda: recommend(benchmark)),
        ("Feedback incorporation", incorporate_feedback),
        ("Post-feedback training", train),
    ]
    for name, stage in stages:
        try:
            succeeded = stage()
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}", file=sys.stderr)
            return False
        if succeeded is not True:
            print(f"[FAIL] {name}: stage returned failure.", file=sys.stderr)
            return False
        print(f"[PASS] {name}")
    print("\nPipeline completed. See data/ and results/.")
    return True
