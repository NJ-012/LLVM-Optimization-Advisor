import math
import re

import pandas as pd

from .config import CONFIGS, FEATURES


EXPERIMENT_COLUMNS = {
    "program_id",
    "configuration",
    "baseline_o3_seconds",
    "runtime_seconds",
    "speedup_vs_o3",
    "correctness",
    *FEATURES,
}
FEEDBACK_COLUMNS = {
    "timestamp",
    "program_id",
    "configuration",
    "baseline_o3_seconds",
    "runtime_seconds",
    "speedup_vs_o3",
    "correctness",
    "iteration",
    "predicted_speedup",
    *FEATURES,
}
FEEDBACK_PROVENANCE_COLUMNS = {
    "measurement_context_id",
    "llvm_version",
    "compiler_flags",
    "baseline_compiler_flags",
    "platform",
    "input_profile",
    "measurement_repeats",
    "baseline_mad_seconds",
    "runtime_mad_seconds",
}
_TRUE_VALUES = {"true", "1", "yes", "pass", "passed"}
_FALSE_VALUES = {"false", "0", "no", "fail", "failed"}


def parse_correctness(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return None
    normalized = str(value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return None


def validate_measurements(frame: pd.DataFrame, kind: str) -> list[str]:
    if kind not in {"experiments", "feedback"}:
        raise ValueError(f"Unknown measurement kind: {kind!r}.")
    required = EXPERIMENT_COLUMNS if kind == "experiments" else FEEDBACK_COLUMNS
    missing = required - set(frame.columns)
    if missing:
        return [f"{kind}: missing required columns: {', '.join(sorted(missing))}"]
    errors = []

    for index, row in frame.iterrows():
        location = f"{kind} row {index + 2}"
        if pd.isna(row["program_id"]) or not str(row["program_id"]).strip():
            errors.append(f"{location}: program_id is empty.")
        if row["configuration"] not in CONFIGS:
            errors.append(f"{location}: unknown configuration {row['configuration']!r}.")

        correctness = parse_correctness(row["correctness"])
        if correctness is None:
            errors.append(f"{location}: correctness must be a recognized boolean value.")

        numeric_values: dict[str, float] = {}
        for column in ("baseline_o3_seconds", "runtime_seconds"):
            try:
                value = float(row[column])
            except (TypeError, ValueError):
                errors.append(f"{location}: {column} must be a finite positive number.")
                continue
            if not math.isfinite(value) or value <= 0:
                errors.append(f"{location}: {column} must be a finite positive number.")
                continue
            numeric_values[column] = value

        try:
            speedup = float(row["speedup_vs_o3"])
        except (TypeError, ValueError):
            speedup = math.nan
        if correctness is True:
            if not math.isfinite(speedup) or speedup <= 0:
                errors.append(f"{location}: passing measurements require a finite positive speedup.")
            elif len(numeric_values) == 2:
                expected = numeric_values["baseline_o3_seconds"] / numeric_values["runtime_seconds"]
                if not math.isclose(speedup, expected, rel_tol=1e-6, abs_tol=1e-9):
                    errors.append(
                        f"{location}: speedup_vs_o3 does not match baseline_o3_seconds/runtime_seconds."
                    )
            if row["configuration"] == "O3" and len(numeric_values) == 2:
                if not math.isclose(
                    numeric_values["baseline_o3_seconds"],
                    numeric_values["runtime_seconds"],
                    rel_tol=1e-6,
                    abs_tol=1e-9,
                ):
                    errors.append(
                        f"{location}: O3 runtime must match its own baseline runtime."
                    )
        elif correctness is False and not pd.isna(row["speedup_vs_o3"]):
            errors.append(f"{location}: failed correctness must not have a speedup label.")

        for column in FEATURES:
            try:
                value = float(row[column])
            except (TypeError, ValueError):
                errors.append(f"{location}: feature {column} must be numeric.")
                continue
            if not math.isfinite(value):
                errors.append(f"{location}: feature {column} must be finite.")

        if kind == "experiments" and "measurement_context_id" in frame:
            context_id = row.get("measurement_context_id")
            if pd.notna(context_id) and str(context_id).strip():
                for column in (
                    "llvm_version",
                    "platform",
                    "input_profile",
                    "compiler_flags",
                    "baseline_compiler_flags",
                    "measurement_repeats",
                    "baseline_mad_seconds",
                    "runtime_mad_seconds",
                    "measurement_source",
                ):
                    if column not in frame or pd.isna(row.get(column)):
                        errors.append(
                            f"{location}: {column} is required for a contextualized measurement."
                        )
                if "compiler_flags" in frame and pd.notna(row.get("compiler_flags")):
                    expected_flags = " ".join(CONFIGS.get(row["configuration"], []))
                    if str(row["compiler_flags"]).strip() != expected_flags:
                        errors.append(
                            f"{location}: compiler_flags do not match the configuration."
                        )
                if "baseline_compiler_flags" in frame and pd.notna(row.get("baseline_compiler_flags")):
                    if str(row["baseline_compiler_flags"]).strip() != " ".join(CONFIGS["O3"]):
                        errors.append(f"{location}: baseline_compiler_flags must identify O3.")
                try:
                    repeats = float(row.get("measurement_repeats"))
                except (TypeError, ValueError):
                    repeats = math.nan
                if not math.isfinite(repeats) or repeats < 2 or not repeats.is_integer():
                    errors.append(
                        f"{location}: measurement_repeats must be an integer of at least two."
                    )
                for column in ("baseline_mad_seconds", "runtime_mad_seconds"):
                    try:
                        mad = float(row.get(column))
                    except (TypeError, ValueError):
                        mad = math.nan
                    if not math.isfinite(mad) or mad < 0:
                        errors.append(
                            f"{location}: {column} must be finite and non-negative."
                        )

        if kind == "feedback":
            for column in FEEDBACK_PROVENANCE_COLUMNS:
                if column not in frame or pd.isna(row.get(column)) or not str(row[column]).strip():
                    errors.append(
                        f"{location}: {column} is required to establish feedback measurement provenance."
                    )
            if (
                "measurement_source" in frame
                and pd.notna(row.get("measurement_source"))
                and row.get("measurement_source") != "feedback"
            ):
                errors.append(f"{location}: measurement_source must be 'feedback'.")
            if "measurement_context_id" in frame:
                context_id = str(row.get("measurement_context_id", "")).strip()
                if context_id and frame["measurement_context_id"].astype(str).duplicated().any():
                    errors.append(f"{location}: measurement_context_id must identify one feedback experiment.")
            if "compiler_flags" in frame and pd.notna(row.get("compiler_flags")):
                expected_flags = " ".join(CONFIGS.get(row["configuration"], []))
                if str(row["compiler_flags"]).strip() != expected_flags:
                    errors.append(f"{location}: compiler_flags do not match the selected configuration.")
            if "baseline_compiler_flags" in frame and pd.notna(row.get("baseline_compiler_flags")):
                if str(row["baseline_compiler_flags"]).strip() != " ".join(CONFIGS["O3"]):
                    errors.append(f"{location}: baseline_compiler_flags must identify the O3 baseline.")
            try:
                repeats = float(row.get("measurement_repeats"))
            except (TypeError, ValueError):
                repeats = math.nan
            if not math.isfinite(repeats) or repeats < 2 or not repeats.is_integer():
                errors.append(f"{location}: measurement_repeats must be an integer of at least two.")
            for column in ("baseline_mad_seconds", "runtime_mad_seconds"):
                try:
                    mad = float(row.get(column))
                except (TypeError, ValueError):
                    mad = math.nan
                if not math.isfinite(mad) or mad < 0:
                    errors.append(f"{location}: {column} must be finite and non-negative.")
            try:
                timestamp = pd.to_datetime(row["timestamp"], errors="raise")
                if pd.isna(timestamp):
                    raise ValueError
            except (TypeError, ValueError, OverflowError):
                errors.append(f"{location}: timestamp must identify when the feedback was measured.")
            try:
                estimate = float(row["predicted_speedup"])
            except (TypeError, ValueError):
                estimate = math.nan
            if not math.isfinite(estimate) or estimate <= 0:
                errors.append(f"{location}: predicted_speedup must be finite and positive.")

    if kind == "experiments":
        context = [
            column
            for column in (
                "program_id",
                "llvm_version",
                "platform",
                "input_profile",
                "measurement_context_id",
            )
            if column in frame
        ]
        if context and "baseline_o3_seconds" in frame:
            distinct = frame.groupby(context, dropna=False)["baseline_o3_seconds"].nunique(dropna=False)
            for key, count in distinct[distinct > 1].items():
                errors.append(
                    f"{kind}: baseline_o3_seconds varies within measurement context {key!r}."
                )
    return errors


def measurement_fingerprint(frame: pd.DataFrame) -> pd.Series:
    columns = [
        "program_id",
        "configuration",
        "baseline_o3_seconds",
        "runtime_seconds",
        "speedup_vs_o3",
        "correctness",
    ]
    values = frame[columns].copy()
    if "measurement_context_id" in frame:
        values["measurement_context_id"] = frame["measurement_context_id"]
    else:
        values["measurement_context_id"] = "<legacy-context>"
    return values.astype("string").fillna("<NA>").agg("\x1f".join, axis=1)


def append_unseen_measurements(base: pd.DataFrame, additions: pd.DataFrame) -> pd.DataFrame:
    if additions.empty:
        return base.copy()
    existing = set(measurement_fingerprint(base)) if not base.empty else set()
    fingerprints = measurement_fingerprint(additions)
    unseen = additions[
        ~fingerprints.isin(existing) & ~fingerprints.duplicated(keep="first")
    ]
    if unseen.empty:
        return base.copy()
    return pd.concat([base, unseen], ignore_index=True, sort=False)


def feedback_quarantine_rows(frame: pd.DataFrame) -> tuple[set[int], dict[int, str]]:
    """Return dataframe indices that must be quarantined and their validation reasons."""
    errors = validate_measurements(frame, "feedback")
    if not errors:
        return set(), {}

    row_reasons: dict[int, list[str]] = {}
    has_global_error = False
    for error in errors:
        match = re.match(r"feedback row (\d+):", error)
        if match:
            index = int(match.group(1)) - 2
            row_reasons.setdefault(index, []).append(error)
        else:
            has_global_error = True

    if has_global_error:
        return set(frame.index), {index: "; ".join(errors) for index in frame.index}
    return set(row_reasons), {index: "; ".join(reasons) for index, reasons in row_reasons.items()}


def combine_chart_sources(experiments: pd.DataFrame, feedback: pd.DataFrame) -> pd.DataFrame:
    collection = experiments
    if not collection.empty:
        if "measurement_source" in collection:
            collection = collection[collection["measurement_source"].eq("collection")]
        elif "llvm_version" in collection:
            collection = collection[
                ~collection["llvm_version"].map(measurement_source).eq("feedback")
            ]
    return pd.concat([collection, feedback], ignore_index=True, sort=False)
