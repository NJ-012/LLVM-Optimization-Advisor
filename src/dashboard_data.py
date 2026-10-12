import math
from typing import Iterable

import pandas as pd


_TRUE_VALUES = {"true", "1", "yes", "pass", "passed"}
_FALSE_VALUES = {"false", "0", "no", "fail", "failed"}


def correctness_status(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    if isinstance(value, bool):
        return "Passed" if value else "Failed"
    normalized = str(value).strip().lower()
    if normalized in _TRUE_VALUES:
        return "Passed"
    if normalized in _FALSE_VALUES:
        return "Failed"
    return "Unknown"


def measurement_source(llvm_version: object) -> str:
    if isinstance(llvm_version, str) and llvm_version.strip().lower() == "feedback-run":
        return "feedback"
    return "collection"


def calculate_measured_speedup(
    baseline_seconds: object,
    runtime_seconds: object,
    correctness: object,
) -> float | None:
    if correctness_status(correctness) != "Passed":
        return None
    try:
        baseline = float(baseline_seconds)
        runtime = float(runtime_seconds)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(baseline) or not math.isfinite(runtime) or baseline <= 0 or runtime <= 0:
        return None
    return baseline / runtime


def filter_observations(
    observations: pd.DataFrame,
    *,
    benchmark: str | None = None,
    configurations: Iterable[str] | None = None,
    correctness: str = "All",
    compiler: str | None = None,
    platform: str | None = None,
) -> pd.DataFrame:
    filtered = observations
    if benchmark and "program_id" in filtered:
        filtered = filtered[filtered["program_id"].astype(str).eq(benchmark)]
    if configurations is not None and "configuration" in filtered:
        filtered = filtered[filtered["configuration"].isin(set(configurations))]
    if correctness != "All" and "correctness" in filtered:
        filtered = filtered[
            filtered["correctness"].map(correctness_status).eq(correctness)
        ]
    if compiler and "llvm_version" in filtered:
        filtered = filtered[filtered["llvm_version"].astype(str).eq(compiler)]
    if platform and "platform" in filtered:
        filtered = filtered[filtered["platform"].astype(str).eq(platform)]
    return filtered.copy()


def prepare_chart_data(
    experiments: pd.DataFrame,
    benchmark: str,
    source: str,
    configurations: Iterable[str] | None = None,
    compiler: str | None = None,
    platform: str | None = None,
) -> pd.DataFrame:
    """Return individual valid observations; never aggregate across experiments."""
    columns = [
        "configuration",
        "configuration_label",
        "measured_speedup",
        "baseline_seconds",
        "runtime_seconds",
        "measurement_source",
        "measurement_repeats",
        "platform",
        "llvm_version",
        "input_profile",
    ]
    if experiments.empty:
        return pd.DataFrame(columns=columns)

    if "measurement_source" in experiments:
        source_values = experiments["measurement_source"].astype(str)
    elif "llvm_version" in experiments:
        source_values = experiments["llvm_version"].map(measurement_source)
    else:
        source_values = pd.Series("collection", index=experiments.index)
    selected = experiments[
        experiments["program_id"].astype(str).eq(str(benchmark))
        & source_values.eq(source)
    ]
    selected = filter_observations(
        selected,
        configurations=configurations,
        compiler=compiler,
        platform=platform,
    )
    observations = []
    for row_number, (_, row) in enumerate(selected.iterrows(), start=1):
        configuration = str(row.get("configuration", ""))
        speedup = calculate_measured_speedup(
            row.get("baseline_o3_seconds"),
            row.get("runtime_seconds"),
            row.get("correctness"),
        )
        if speedup is None:
            continue
        stored_speedup = row.get("speedup_vs_o3")
        if pd.notna(stored_speedup):
            try:
                stored = float(stored_speedup)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid stored speedup in experiment row {row_number}.") from exc
            if not math.isclose(speedup, stored, rel_tol=1e-6, abs_tol=1e-9):
                raise ValueError(
                    f"Stored speedup {stored:.9g} does not match "
                    f"baseline/runtime {speedup:.9g} for {benchmark}/{configuration}."
                )
        observations.append(
            {
                "configuration": configuration,
                "measured_speedup": speedup,
                "baseline_seconds": float(row["baseline_o3_seconds"]),
                "runtime_seconds": float(row["runtime_seconds"]),
                "measurement_source": source,
                "measurement_repeats": row.get("measurement_repeats"),
                "platform": row.get("platform"),
                "llvm_version": row.get("llvm_version"),
                "input_profile": row.get("input_profile"),
                "_row_number": row_number,
            }
        )

    counts: dict[str, int] = {}
    for observation in observations:
        counts[observation["configuration"]] = counts.get(observation["configuration"], 0) + 1
    seen: dict[str, int] = {}
    for observation in observations:
        configuration = observation["configuration"]
        seen[configuration] = seen.get(configuration, 0) + 1
        label = f"{configuration} (baseline)" if configuration == "O3" else configuration
        if counts[configuration] > 1:
            label = f"{label} · observation {seen[configuration]}"
        observation["configuration_label"] = label

    result = pd.DataFrame(observations, columns=columns + ["_row_number"])
    return result[columns]
