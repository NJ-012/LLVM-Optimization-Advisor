# Final release report

**Verdict: READY WITH LIMITATIONS**

The changed source passes the full 16-test suite under WSL with the project validator reporting 12/12 checks passed. All 11 kernels also compiled in each configured mode and matched their standalone `-O0` output. The Streamlit page and theme toggle rendered in AppTest and a local server health check returned `ok`. Release is not fully ready for trustworthy recommendations: the existing persisted model artifact failed to deserialize in the tested Windows runtime, the available grouped-CV model did not beat its median baseline, some checked-in measurements predate the matrix-kernel observable-workload change, and no fresh timed collection was run.

## Changes delivered

- Restructured the Streamlit dashboard into Overview, Benchmark Explorer, Advisor, Experiments, and Feedback sections. Added functional benchmark/configuration/correctness/compiler/platform filters, source separation, a light/dark toggle, compact tables with expandable technical detail, baseline/run-context display, and measured-vs-estimated labeling.
- Changed measured-speedup chart inputs to retain individual values for one benchmark and one selected context. The chart labels O3 as the 1.00× baseline, shows values and axis units, and provides measurement tooltips. It detects stored speedups that conflict with baseline/runtime arithmetic.
- Added CSV/schema/data validation, finite positive runtime and feature checks, context-specific baseline consistency, O3 self-baseline checks, and idempotent feedback incorporation without changing the legacy CSV schemas.
- Changed benchmark correctness comparison to a separately compiled `-O0` executable. Matrix multiplication and transpose now print a weighted checksum covering all output cells rather than one cell.
- Changed model training to use validated measured log-speedup labels without silent clipping. Added program-grouped CV comparisons against a fold-median predictor and an O3 policy, model/schema metadata, and a safe O3 fallback when grouped validation is missing or fails to beat the median baseline. O3's predicted speedup is fixed at its mathematically defined `1.0×`.
- Added `python run.py validate`, updated diagnostics and documentation, bounded direct dependency ranges, added an environment example, deployment notes, a release checklist, and the engineering audit.

## Important data and model caveats

- The existing CSV files were preserved. At audit time `experiments.csv` contained 45 rows (11 programs × 4 configurations plus one incorporated feedback row); `feedback.csv` contained one row. The new schema/arithmetic validators found no issues.
- Existing `array_sum` collection rows use an O3 baseline of `0.012398 s` and five repeats; the independent feedback observation uses approximately `0.009941 s` and seven repeats. These remain separate contexts and are not reconciled.
- `matrix_multiply.c` and `matrix_transpose.c` changed their printed observable result to cover the full output. Their pre-existing measurements and extracted features predate that source change and the legacy schema has no source-revision ID. The dashboard displays a warning for these benchmarks; rerun collection before treating existing rows as results for the current sources. No collection was run because it overwrites `data/experiments.csv`.
- The persisted `models/reward_model.joblib` was not changed. Loading it with the available Windows XGBoost 3.4.1 failed with `input stream corrupted`; the dashboard now reports this without an unhandled app exception. Retrain in the intended deployment environment before expecting recommendations from that artifact.
- A new Random Forest training/evaluation was exercised in a temporary WSL artifact location using the existing 45 measurements (the WSL environment did not have XGBoost). Program-grouped CV log-speedup MAE was **0.049411**, versus **0.047102** for the grouped median baseline. Top-1 configuration accuracy was **0.454545**, versus **0.363636** for the O3 policy. The regression model did not beat the median baseline, so the tested fallback selects O3. These diagnostics are exploratory; 11 programs are not enough to support a generalization claim. No temporary model replaced the persisted artifact.
- Correctness is now compared to another optimization of the same source, not an independently calculated mathematical oracle. Checksums can collide. Timings still include process startup/output capture, lack raw per-run CSV storage, and are sensitive to machine load/cache state. The CSV schema has no unique experiment ID.

## Files

**Added**

- `.env.example`
- `src/data_validation.py`
- `src/recommendation.py`
- `src/validation.py`
- `docs/ENGINEERING_AUDIT.md`
- `docs/DEPLOYMENT.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/FINAL_RELEASE_REPORT.md`
- `tests/test_dashboard.py`

**Changed**

- `dashboard.py`, `run.py`, `src/benchmarks.py`, `src/model.py`, `src/pipeline.py`
- `benchmarks/matrix_multiply.c`, `benchmarks/matrix_transpose.c`
- `requirements.txt`, `.gitignore`, `README.md`, `docs/DATASET.md`, `docs/PROJECT_GUIDE.md`

**Removed:** none.

`data/experiments.csv`, `data/feedback.csv`, and `models/reward_model.joblib` were not overwritten. The workspace has no Git metadata, so no branch or Git backup could be created.

## Environment and validation

| Environment | Detected tools/libraries |
|---|---|
| Native Windows | Windows 11; CPython 3.12.10. `clang`, `opt`, and `llvm-config` not on `PATH`. The isolated release environment installed NumPy 2.5.4, pandas 3.0.6, scikit-learn 1.9.1, XGBoost 3.4.1, Streamlit 1.65.0, Altair 5.5.0, and joblib 1.6.0. |
| WSL Ubuntu-D | Linux 6.18.40.1 WSL2; CPython 3.12.3; Clang `/usr/bin/clang` 18.1.3; `opt` `/usr/bin/opt` 18.1.3; `llvm-config` `/usr/bin/llvm-config` 18.1.3. Isolated validation environment: NumPy 2.5.4, pandas 3.0.6, scikit-learn 1.9.1, joblib 1.6.0, Streamlit 1.65.0, Altair 6.3.0; XGBoost absent. |

Actual checks:

- WSL `python run.py validate`: **12/12 checks passed**, including schema checks and the full unittest suite.
- Full WSL `python -m unittest discover -s tests`: **16 tests passed**.
- Windows focused dashboard tests: **15 passed**. Windows full suite: **15 passed, 1 errored** because native Windows has no Clang for `test_matrix_features`.
- WSL compiler matrix: **11/11 programs** compiled at `-O0` and under all four configured flag bundles; all candidate stdout matched the standalone `-O0` stdout.
- Windows `py_compile`: passed for all changed Python modules.
- Streamlit AppTest: all five sections rendered; dark toggle changed state; no unhandled app exception. It displayed handled errors for the incompatible persisted model.
- Local Streamlit server health endpoint: returned `ok`.
- No fresh timed benchmark collection was run. The compiler matrix check verified output equivalence only; it did not measure or claim a performance improvement.

## Exact local commands

From the project root, in Ubuntu/WSL2 after installing the documented dependencies:

```bash
python run.py doctor
python run.py validate
python -m unittest discover -s tests
```

Preserve collection history before running a command that collects:

```bash
cp data/experiments.csv data/experiments.backup.csv
python run.py collect
python run.py train
python run.py evaluate
```

The existing full pipeline remains available but includes collection and can replace the experiment CSV:

```bash
cp data/experiments.csv data/experiments.backup.csv
python run.py all
```

To run individual advisor/feedback steps:

```bash
python run.py recommend --benchmark matrix_multiply
python run.py feedback --benchmark matrix_multiply
python run.py incorporate-feedback
python run.py train
```

To launch the dashboard:

```bash
streamlit run dashboard.py
```

Native Windows testing requires a separately installed Clang on `PATH`; the validated full compiler/test flow used WSL Ubuntu-D. On native Windows, the dashboard can run with the project Python dependencies even without Clang, but current feature extraction and benchmark commands cannot.

## Deployment steps and manual actions

1. Run `collect`, `train`, and `validate` on a trusted local/CI system after backing up data.
2. Resolve the existing model artifact compatibility problem by retraining with the exact Python/scikit-learn/XGBoost environment intended for hosting.
3. Review and approve CSV/model artifacts; do not publish private or machine-specific information without authorization.
4. Deploy `dashboard.py` with `requirements.txt` and approved artifacts. Use `ADVISOR_DATA_DIR` and `ADVISOR_MODEL_PATH` for mounted artifact locations. See [DEPLOYMENT.md](DEPLOYMENT.md).
5. Verify filters, themes, chart context, artifact/model compatibility, and access controls in the actual hosted runtime.

No hosting, authentication, automatic artifact export, trusted independent golden outputs, raw timing log, or experiment-ID migration is provisioned. Do not expose benchmark compilation/execution as a public dashboard service.
