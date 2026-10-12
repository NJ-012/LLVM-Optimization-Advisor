# ML-Based Adaptive Optimization Advisor for LLVM

A local prototype connecting static LLVM IR/source features, a supervised reward model, compiler-configuration comparisons, runtime measurements, and a separately logged feedback loop. The four choices are flag configurations—not isolated LLVM passes.

## Architecture and data flow

1. `src/features.py` runs Clang at `-O0` to extract textual IR counts and source-text heuristics.
2. `src/benchmarks.py` compiles each fixed C kernel under the configurations in `src/config.py`, verifies output against a separately compiled `-O0` reference before timing, warms up once, and records the median of five subprocess wall-clock timings with median absolute deviation (MAD).
3. `data/experiments.csv` stores collection measurements. `src/model.py` fits XGBoost when available (Random Forest fallback), using log measured speedup as the target and program-grouped cross-validation for diagnostic comparisons.
4. `recommend` predicts each configuration's reward. `feedback` records one explicitly identified measurement context: the selected candidate and its independently measured O3 baseline, or one shared O3 sample set when O3 itself is selected. `incorporate-feedback` adds only validated records idempotently.
5. `dashboard.py` reads artifacts only; it does not compile or execute benchmark code. Overview, Explorer, Advisor, Experiments, and Feedback views distinguish predictions from observations and keep collection and feedback contexts separate.

Speedup uses `baseline runtime / candidate runtime`; values above `1.0×` indicate a faster candidate in that measurement context. The correctness reference is an `-O0` executable of the same source, not an independent mathematical oracle. Matrix kernels print a weighted checksum of the full output so work is observable, but checksums can collide. Timings include process launch and output capture, and are sensitive to CPU load, cache state, and run order. See [docs/DATASET.md](docs/DATASET.md) and [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md).

## Requirements and installation

- Python 3.10 or newer (3.11/3.12 recommended).
- Clang on `PATH` for benchmark compilation and the feature-extraction test.
- Python packages in `requirements.txt`; XGBoost is preferred, with Random Forest as fallback.
- Windows users should use Ubuntu on WSL2 for LLVM toolchain consistency. `perf` is optional and not used by the current pipeline.

### Ubuntu / WSL2

Run these commands in the Ubuntu shell from the project directory:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip clang llvm build-essential
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py doctor
python run.py validate
```

### Native Windows PowerShell

If Clang and LLVM are installed and available on `PATH`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py doctor
python run.py validate
```

PowerShell execution policy may need to permit activation scripts; alternatively run `.\.venv\Scripts\python.exe` directly. `python run.py doctor` reports missing Clang; it does not install tools.

## Commands

```text
python run.py doctor
python run.py dataset
python run.py collect
python run.py train
python run.py recommend --benchmark matrix_multiply
python run.py feedback --benchmark matrix_multiply
python run.py incorporate-feedback
python run.py evaluate
python run.py all
python run.py validate
python -m unittest discover -s tests
python -m pytest
streamlit run dashboard.py
```

Install development test dependencies with `python -m pip install -r requirements-dev.txt`.

`collect` replaces `data/experiments.csv`; back it up before rerunning if existing history matters. `feedback` intentionally measures a new observation and appends it to `data/feedback.csv`; it is not run by `all`. `incorporate-feedback` preserves existing rows and deduplicates by measurement-context identity. `all` is a repeatable batch workflow, not a feedback generator: it runs diagnostics, collection, training, grouped evaluation, recommendation, incorporates already-recorded validated feedback, and retrains. Each `all` run performs a fresh collection and therefore overwrites `data/experiments.csv`.

Feedback records must include a unique measurement context, compiler/version and flags, platform, input profile, repetition count, and timing MADs. The old feedback CSV lacks this provenance and contains O3 rows whose separately timed O3 candidate runtime does not equal the baseline value. Do not edit those records to force a pass. Run `python run.py quarantine-feedback` to preserve an exact byte-for-byte backup at `data/feedback.pre_quarantine.csv`, copy invalid rows with reasons to `data/feedback.quarantine.csv`, and leave only validated records in the active feedback file. Regenerate quarantined observations with `python run.py feedback --benchmark <name>`. The pipeline will reject malformed feedback without incorporating any rows.

`validate` checks the Python/toolchain environment, available artifact schemas and measurement consistency, then runs the full unittest suite. Missing generated datasets are reported as skipped; missing required tools or failing tests produce a nonzero exit rather than being presented as passed.

## Dashboard

The dashboard offers Overview, Benchmark Explorer, Advisor, Experiments, and Feedback sections. Sidebar filters include benchmark, configuration, correctness, compiler/run marker, and platform. The speedup chart shows individual measurements for one benchmark and source, labels the O3 baseline, and includes source/timing tooltips. Feedback includes validation/quarantine history and a candidate-versus-O3 runtime chart. Its `Show illustrative demo data` toggle is off by default; enabled examples from `data/demo_feedback.csv` are labelled `DEMO — NOT MEASURED` and are used only for display. Demo rows are never read by collection, training, evaluation, or feedback incorporation. Predicted speedup remains an estimate and is kept distinct from measured speedup. Detailed IR/platform/source features are available in an expander. A sidebar control switches light/dark styling.

The dashboard needs no compiler; it reads CSVs from `data/` and an optional local model artifact. For a mounted/exported artifact directory, set `ADVISOR_DATA_DIR` to the directory containing `experiments.csv` and `feedback.csv` before launch. It only displays existing data and never executes uploaded C code.

## Data and evaluation limits

There are 11 fixed source benchmarks. The current checked-in/local artifact set contains machine-specific measurements; use `python run.py collect` to produce measurements on the machine under study. Different compiler/platform/input contexts are not a single comparable experiment. Compiler version, platform, and input profile are retained as available context, but the legacy CSV schema has no durable experiment/run ID; retain artifacts and context when exporting.

Training and `evaluate` report program-grouped cross-validation only when there are at least four unique programs, together with program and observation counts. The model and grouped-median baseline use identical held-out program folds and the same log-speedup target; hyperparameters are fixed rather than selected from held-out results. A model that does not beat the median baseline is not used to select an optimization: the conservative O3 fallback is explicitly warned about in the CLI and dashboard. Top-1 accuracy is descriptive, not evidence of a runtime improvement. These are exploratory diagnostics on a small set, not a validated deployment claim. Static features include text heuristics and do not describe optimized IR; timing includes process startup/output capture. The five/seven-repeat median and MAD do not remove CPU-load, cache, thermal, or ordering effects, and this pipeline does not claim statistical significance.

## Troubleshooting

- `clang not found`: install LLVM/Clang and ensure `clang` is on `PATH` in the same shell used to run Python.
- `Need at least three distinct benchmark programs to train`: run `python run.py collect` to generate sufficient local training rows.
- Invalid CSV/schema or inconsistent baseline/speedup: inspect the reported row/context; do not edit measurements to force validation.
- Dashboard module missing: activate the project environment and run `python -m pip install -r requirements.txt`.
- Preserve current timings: copy `data/experiments.csv` before collection; generated CSVs, binaries, and model files are ignored by default.

## Release and deployment documents

- [Engineering audit](docs/ENGINEERING_AUDIT.md)
- [Hosted dashboard deployment guide](docs/DEPLOYMENT.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Final release report](docs/FINAL_RELEASE_REPORT.md)

No hosted deployment is configured by default. Review machine-specific data and model artifacts before making them accessible to a hosted application.
