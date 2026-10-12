import math
import platform
import statistics
import subprocess
import time
import uuid

import pandas as pd

from .config import BENCH, CONFIGS, EXPERIMENTS, FEATURES, RESULTS
from .features import clang_path, extract


def execute(cmd, timeout=90):
    process = subprocess.run(
        [str(item) for item in cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if process.returncode:
        raise RuntimeError(
            f"Command failed: {' '.join(map(str, cmd))}\n{process.stderr}"
        )
    return process.stdout.strip()


def compile_one(src, config, out):
    execute([clang_path(), src, "-std=c11", *CONFIGS[config], "-lm", "-o", out])


def compile_reference(src, out):
    execute([clang_path(), src, "-std=c11", "-O0", "-lm", "-o", out])


def outputs_match(expected, candidate):
    return expected == candidate


def run_once(binary):
    return execute([binary], timeout=90)


def calculate_speedup(baseline, candidate, correctness):
    if not correctness:
        return None
    try:
        baseline = float(baseline)
        candidate = float(candidate)
    except (TypeError, ValueError):
        return None
    if (
        not math.isfinite(baseline)
        or not math.isfinite(candidate)
        or baseline <= 0
        or candidate <= 0
    ):
        return None
    return baseline / candidate


def aggregate_timings(timings):
    values = [float(value) for value in timings]
    if len(values) < 2:
        raise ValueError("At least two timed repetitions are required.")
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("Runtime measurements must be finite and positive.")
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return median, mad


def measure(binary, repeats=5):
    if repeats < 2:
        raise ValueError("repeats must be at least two")
    timings = []
    outputs = []
    for _ in range(repeats):
        start = time.perf_counter()
        output = run_once(binary)
        timings.append(time.perf_counter() - start)
        outputs.append(output)
    if len(set(outputs)) != 1:
        raise RuntimeError(f"Non-deterministic output: {binary}")
    median, mad = aggregate_timings(timings)
    return median, mad, outputs[0]


def median_time(binary, repeats=5):
    median, _, output = measure(binary, repeats)
    return median, output


def collect():
    compiler = clang_path()
    if not compiler:
        raise RuntimeError("clang not found; run python run.py doctor")
    sources = sorted(BENCH.glob("*.c"))
    if len(sources) < 3:
        raise RuntimeError("Expected at least three benchmark C files")

    context_id = uuid.uuid4().hex
    compiler_version = execute([compiler, "--version"]).splitlines()[0]
    host_platform = platform.platform()
    rows = []
    print(
        f"Collecting {len(sources)} benchmarks × {len(CONFIGS)} configurations "
        "× 5 timed runs (median; uncertainty = median absolute deviation)"
    )
    for source in sources:
        print(f"\n[{source.stem}]")
        features = extract(source)
        reference = RESULTS / f"{source.stem}_correctness_O0"
        compile_reference(source, reference)
        expected_output = run_once(reference)

        binaries = {}
        warmup_outputs = {}
        for configuration in CONFIGS:
            binary = RESULTS / f"{source.stem}_{configuration}"
            compile_one(source, configuration, binary)
            binaries[configuration] = binary
            warmup_outputs[configuration] = run_once(binary)
            if not outputs_match(expected_output, warmup_outputs[configuration]):
                raise RuntimeError(
                    f"Correctness failed before timing {source.stem}/{configuration}; "
                    "no timing for this candidate was accepted."
                )

        timings = {}
        dispersions = {}
        outputs = {}
        for configuration, binary in binaries.items():
            runtime, mad, output = measure(binary, 5)
            if not outputs_match(expected_output, output):
                raise RuntimeError(
                    f"Correctness changed during timing {source.stem}/{configuration}; "
                    "the collection was not written."
                )
            timings[configuration] = runtime
            dispersions[configuration] = mad
            outputs[configuration] = output
            print(f"  {configuration:18s} {runtime:.6f}s (MAD {mad:.6f}s)")

        for configuration in CONFIGS:
            correct = outputs_match(expected_output, outputs[configuration])
            speedup = calculate_speedup(
                timings["O3"], timings[configuration], correct
            )
            row = {
                "program_id": source.stem,
                "benchmark_file": source.name,
                "configuration": configuration,
                "runtime_seconds": timings[configuration],
                "baseline_o3_seconds": timings["O3"],
                "speedup_vs_o3": speedup,
                "correctness": correct,
                "llvm_version": compiler_version,
                "platform": host_platform,
                "input_profile": "fixed source-defined input",
                "measurement_repeats": 5,
                "measurement_context_id": context_id,
                "compiler_flags": " ".join(CONFIGS[configuration]),
                "baseline_compiler_flags": " ".join(CONFIGS["O3"]),
                "baseline_mad_seconds": dispersions["O3"],
                "runtime_mad_seconds": dispersions[configuration],
                "measurement_source": "collection",
                **features,
            }
            rows.append(row)

    frame = pd.DataFrame(rows)
    frame.to_csv(EXPERIMENTS, index=False)
    print(f"\nWrote {len(frame)} records to {EXPERIMENTS}")
    return True
