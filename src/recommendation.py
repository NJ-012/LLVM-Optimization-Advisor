import math
from collections.abc import Mapping


def use_safe_fallback(bundle: Mapping[str, object]) -> bool:
    try:
        model_error = float(bundle["group_cv_log_speedup_mae"])
        baseline_error = float(bundle["group_cv_median_baseline_log_speedup_mae"])
    except (KeyError, TypeError, ValueError):
        return True
    return (
        not math.isfinite(model_error)
        or not math.isfinite(baseline_error)
        or model_error >= baseline_error
    )


def choose_action(
    predictions: Mapping[str, float],
    bundle: Mapping[str, object],
    default_action: str = "O3",
) -> str:
    if use_safe_fallback(bundle):
        return default_action
    if not predictions:
        raise ValueError("No configuration predictions are available.")
    return max(predictions, key=predictions.__getitem__)
