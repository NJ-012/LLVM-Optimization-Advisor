import importlib.util
import shutil
import subprocess
import sys

import pandas as pd

from .config import EXPERIMENTS, FEEDBACK
from .data_validation import validate_measurements


def _report(name: str, status: str, detail: str) -> bool:
    print(f"[{status}] {name}: {detail}")
    return status == "PASS"


def validate_release() -> bool:
    results = []
    results.append(_report("Python", "PASS", sys.version.split()[0]))

    clang = shutil.which("clang")
    results.append(
        _report(
            "Clang",
            "PASS" if clang else "BLOCKED",
            clang or "not found; benchmark execution and feature tests require Clang",
        )
    )
    if clang:
        version = subprocess.run(
            [clang, "--version"], capture_output=True, text=True, check=False
        )
        results.append(
            _report(
                "Clang version",
                "PASS" if version.returncode == 0 else "FAIL",
                version.stdout.splitlines()[0] if version.stdout else version.stderr.strip(),
            )
        )

    for package in ("pandas", "numpy", "sklearn", "joblib", "streamlit", "altair"):
        available = importlib.util.find_spec(package) is not None
        results.append(
            _report(
                f"Required package {package}",
                "PASS" if available else "FAIL",
                "available" if available else "not installed",
            )
        )

    for path, kind in ((EXPERIMENTS, "experiments"), (FEEDBACK, "feedback")):
        if not path.exists():
            results.append(_report(f"{kind} CSV", "SKIP", f"{path.name} has not been generated"))
            continue
        try:
            errors = validate_measurements(pd.read_csv(path), kind)
        except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
            errors = [f"could not read {path.name}: {exc}"]
        if errors:
            results.append(_report(f"{kind} CSV", "FAIL", "; ".join(errors[:5])))
        else:
            results.append(_report(f"{kind} CSV", "PASS", "schema and measurement checks passed"))

    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        capture_output=True,
        text=True,
        check=False,
    )
    print(tests.stdout, end="")
    if tests.stderr:
        print(tests.stderr, end="", file=sys.stderr)
    results.append(
        _report(
            "Unit tests",
            "PASS" if tests.returncode == 0 else "FAIL",
            f"exit code {tests.returncode}",
        )
    )
    print(f"Validation summary: {sum(results)}/{len(results)} checks passed.")
    return all(results)
