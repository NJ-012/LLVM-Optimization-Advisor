# Current Project Status

**Observed:** 2026-10-12, Windows 11 host, CPython 3.12.10, branch `main`, base commit `b4fbf133976221ef3acfec775d4b386eca2a244f`.

## What works

- The CLI exposes doctor, dataset, collect, train, evaluate, recommend, feedback, incorporate, quarantine, all, and validate commands.
- The existing experiment and active feedback CSVs pass current schema and speedup consistency checks: 45 experiment rows / 11 programs and 1 active feedback row.
- Focused dashboard and feedback/pipeline tests pass: 19 and 17 tests respectively.
- Streamlit AppTest rendered Overview, Benchmark Explorer, Advisor, Experiments, and Feedback without app exceptions in this environment.
- Feedback recording, provenance validation, quarantine, idempotent incorporation, and explicit retraining are implemented as separate steps.
- The Feedback tab offers clearly labelled display-only demo rows behind an off-by-default toggle. `data/demo_feedback.csv` does not enter model training, evaluation, or incorporation paths.

## Partial or limited

- Recommendation and benchmarking need Clang; current native Windows `PATH` has no `clang`, `opt`, or `llvm-config`. The dashboard itself renders without Clang.
- Correctness compares exact stdout with the same source compiled at `-O0`; this is useful as a guard but not an independent mathematical oracle.
- The dataset is small and machine-specific. Features are raw textual/heuristic counts; the model does not condition on compiler or platform.
- Historical experiment rows have no source-revision ID; matrix benchmark sources changed their full-output checksum. UI warns against treating old measurements as current-source results.
- The bundled model loaded during AppTest; its quality was not evaluated during this audit.
- Four legacy feedback rows are quarantined with recorded reasons. They are not valid active feedback; one separate current feedback row validates.
- Local model/data/results files are tracked by Git, including Linux ELF result binaries in a Windows checkout.
- No CI workflow or hosted deployment status/configuration was verified.

## Broken / currently failing

- `python run.py doctor` exits 1 because Clang is missing (packages are present).
- `python run.py validate` exits 1: 9/11 checks passed; one compiler-dependent feature test errors due to missing Clang.
- Full unittest suite: 37 run, 36 passed, one error in `test_matrix_features` for the same missing Clang.
- A prior release report's statements that Git metadata was absent, that the suite had 16 tests, and that the persisted model failed to load do not describe this observed checkout/runtime.

## Not implemented or not verified

- No independent mathematical correctness oracle, raw per-run timing storage, randomized/interleaved schedule, context-aware prediction, prediction uncertainty, final external test set, or scientific performance validation.
- No clean-clone matrix, live browser accessibility review, CI build, or hosted deployment check.
- No training/evaluation run against the tracked model during this audit because it would replace the artifact; no fresh timed benchmark collection was run.

## Current checks

- `python run.py doctor`: exit 1; Clang/LLVM executables missing.
- `python run.py dataset`: lists 11 source benchmarks.
- Current experiment/feedback validators: 0 errors each.
- `python run.py validate`: exit 1, 9/11 release checks passed; Clang-dependent test error.
- `python -m unittest discover -s tests -p test_dashboard.py -v`: 19 passed.
- `python -m unittest discover -s tests -p test_feedback_pipeline.py -v`: 17 passed.
- `python -m unittest discover -s tests -v`: 36 passed, 1 error (Clang unavailable).
- Python AST syntax parse: 15 source/test files passed.
- Streamlit AppTest: all five tabs rendered; no app errors; local model recommendation path rendered.
- `pytest` was not installed in the selected environment; pytest runner not run.

## Environment and deployment

Windows 11, CPython 3.12.10; pandas 3.0.6, NumPy 2.5.4, scikit-learn 1.9.1, joblib 1.6.0, matplotlib 3.11.2, Streamlit 1.65.0, Altair 5.5.0, XGBoost 3.4.1. `pytest` is declared by `requirements-dev.txt` but unavailable in this environment. The README recommends WSL2 for LLVM consistency. No hosted deployment configuration or status was verified.

## Next five recommended tasks

1. Add immutable benchmark source fingerprints/revision identifiers to measurement rows and prevent comparisons across source revisions.
2. Replace/augment same-source stdout correctness checks with independent reference tests and explicit floating-point comparison rules.
3. Establish a supported clean environment/CI matrix with Clang and a reproducible dependency/LLVM specification.
4. Decide whether machine-specific CSVs, the model, and tracked ELF result binaries belong in Git; update the artifact policy accordingly.
5. Recollect measurements for current benchmark sources into a preserved, versioned artifact set, retaining raw samples and avoiding overwrites of historical data.

See [PROJECT_AUDIT.md](./PROJECT_AUDIT.md) for the detailed architecture, evidence, artifact schemas, audit findings, risk register, and staged roadmap.
