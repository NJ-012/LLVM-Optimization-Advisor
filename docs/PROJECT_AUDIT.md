# Current Project Audit

**Audit date:** 2026-10-12  
**Repository:** `NJ-012/LLVM-Optimization-Advisor`  
**Branch / base commit observed:** `main` / `b4fbf133976221ef3acfec775d4b386eca2a244f`  
**Audit type:** Read-only implementation, artifact, and test review. No application, benchmark, dataset, model, Git, or deployment changes were made for this audit. This report and `CURRENT_STATUS.md` are the only intended new files.

## Evidence labels and scope

- **Verified** means observed in the checked-out source, local artifacts, or a command run during this audit.
- **Historical documentation** means an existing report or guide describes an earlier state and is not evidence that the same condition still holds.
- **Assessment** means an engineering judgment based on verified evidence.
- **Unknown / not run** means the necessary external state, tool, or safe test was unavailable or intentionally not exercised.

The audit inspected the tracked Python entry points and modules, all 11 benchmark sources, tests, current CSV artifacts, model/results presence and file types, dependency/environment files, README and project/deployment/release docs, `.gitignore`, and Git metadata. It also ran read-only CLI diagnostics, schema validation, tests, AST parsing, and Streamlit AppTest. No full timed collection, direct benchmark compilation/execution, training, or standalone model export was run because those operations either need unavailable Clang or overwrite generated artifacts.

The worktree was already dirty at audit start. Existing changes included `README.md`, `dashboard.py`, `docs/DATASET.md`, `models/reward_model.joblib`, `src/dashboard_data.py`, `tests/test_dashboard.py`, `tests/test_feedback_pipeline.py`, and an untracked `data/demo_feedback.csv`. These predate this audit; they were left untouched. The active `data/feedback.csv` SHA-256 was observed unchanged as `8D14DC82591FFC59B0E5B1FDB5D947B59FEC3C4EE00997A9938D4391105DD191`. The audit does not attribute the pre-existing changes to a particular person or session.

## 1. Executive summary

This is a local ML-assisted compiler-configuration research prototype, not an LLVM pass manager, self-tuning compiler, production optimizer, or validated performance-claim system. It discovers fixed C files, extracts 15 textual/heuristic features, measures four Clang flag configurations against an O0-built executable, trains a supervised regressor on log speedup, and exposes CLI recommendations and a read-only Streamlit dashboard. A separately recorded feedback sample can later be incorporated and used in a separately invoked retraining command.

The current repository has 11 benchmark sources, four configurations, 45 experiment rows across 11 programs (44 collection rows plus one incorporated-feedback row), one active real feedback row, four invalid archived feedback rows, three hypothetical demo rows, one tracked joblib model, and 72 tracked files under `results/`. The active experiment and feedback CSVs both pass the current schema and measurement checks. The demo file is not an input to CLI model/data paths.

The relevant focused test modules pass: dashboard **19/19** and feedback/pipeline **17/17**. The full suite runs 37 tests: **36 pass, one errors** because the native Windows environment has no `clang` executable for feature extraction. `python run.py validate` exits 1 with 9/11 checks passing for that reason. The dashboard itself rendered under Streamlit AppTest with all five tabs, a loaded recommendation model, and no app exceptions. No fresh compiler run or performance measurement was performed.

The most consequential limitations are: the checked-in collection artifact includes old measurement history with no source-revision ID (the matrix kernels have an explicit source-change warning); correctness uses exact textual output against an O0 executable rather than an independent mathematical oracle; the 15 features are rough textual counts rather than parsed semantic IR; the model ignores machine/compiler context and there is no reliable current generalization result; and ELF benchmark binaries plus machine-specific measurement artifacts are tracked in Git.

## 2. Repository map and inventory

### High-level tree

```text
.
|-- .env.example
|-- .gitignore
|-- README.md
|-- LICENSES_AND_CITATIONS.md
|-- run.py
|-- dashboard.py
|-- requirements.txt
|-- requirements-dev.txt
|-- benchmarks/                 11 fixed C kernels
|-- data/
|   |-- benchmark_manifest.csv
|   |-- experiments.csv
|   |-- experiments.pre-release.csv
|   |-- experiments.postfeedback-pre-release.csv
|   |-- feedback.csv
|   |-- feedback.pre_quarantine.csv
|   |-- feedback.quarantine.csv
|   `-- demo_feedback.csv       untracked local illustrative artifact
|-- docs/
|   |-- DATASET.md
|   |-- DEPLOYMENT.md
|   |-- ENGINEERING_AUDIT.md
|   |-- FINAL_RELEASE_REPORT.md
|   |-- PROJECT_GUIDE.md
|   `-- RELEASE_CHECKLIST.md
|-- models/
|   `-- reward_model.joblib
|-- results/                    72 tracked items: 60 extensionless ELF executables,
|                               11 .ll feature dumps, and .gitkeep
|-- src/
|   |-- benchmarks.py
|   |-- config.py
|   |-- dashboard_data.py
|   |-- data_validation.py
|   |-- features.py
|   |-- model.py
|   |-- pipeline.py
|   |-- recommendation.py
|   `-- validation.py
`-- tests/
    |-- test_dashboard.py
    |-- test_features.py
    `-- test_feedback_pipeline.py
```

No `.github` workflow files or `.streamlit` configuration files are tracked or present. The repository root has no `pyproject.toml`, setup script, or dependency lockfile. `.venv/` and `.venv-release/` are local ignored environments, not distributable reproducibility records.

### Python implementation guide

| File | Responsibilities and principal interfaces | Inputs / outputs and relationships |
|---|---|---|
| `run.py` | `main()` builds argparse subcommands and dispatches to the pipeline or release validator. | Entry point; `recommend` and `feedback` accept optional `--benchmark`, default `matrix_multiply`. |
| `dashboard.py` | Streamlit app; cached `read_csv`, shared sidebar filters, `apply_filters`, `show_table`, `chart_for`, then five tabs. | Reads configured experiment, feedback, quarantine, demo CSVs and optional model. Does not compile or execute benchmark source. |
| `src/config.py` | Defines `ROOT`, `BENCH`, `DATA`, `MODELS`, `RESULTS`, CSV/model paths, `CONFIGS`, and 15 `FEATURES`; creates artifact directories on import. | Shared path, schema, and compiler configuration source. |
| `src/features.py` | `clang_path()`, subprocess `run()`, and `extract(source)`. Invokes Clang `-S -emit-llvm -O0`, counts textual patterns and scans source. | Writes `results/<stem>_features.ll`; returns a numeric feature dict. |
| `src/benchmarks.py` | `execute`, compile helpers, `outputs_match`, `run_once`, speedup and timing aggregation, `measure`, and `collect`. | Builds references/candidates in `results/`; collection replaces `data/experiments.csv`. |
| `src/data_validation.py` | Correctness parsing, `validate_measurements`, fingerprints, idempotent append, quarantine row reasons, chart-source merge. | Shared experiment/feedback rules used by pipeline and UI. |
| `src/model.py` | `action_frame`, data signature, algorithm factory, program-grouped fold/evaluation functions, cleaning, `train`, `load`, `predict_action`. | Reads `experiments.csv`, trains, and writes `models/reward_model.joblib`; inference creates prediction rows for every configured action. |
| `src/recommendation.py` | `use_safe_fallback` and `choose_action`. | Selects O3 when validation metadata is absent/invalid or model MAE does not beat grouped median; otherwise max predicted reward. |
| `src/pipeline.py` | CLI stages: `doctor`, `collect`, `train`, `recommend`, atomic CSV helper, `feedback`, `quarantine_feedback`, `incorporate_feedback`, `evaluate`, `show_dataset`, `run_all`. | Connects compiler, data validation, model, CSV persistence, and CLI reporting. |
| `src/dashboard_data.py` | UI transformations: speedup calculation, correctness/source classification, filters, demo/feedback-history labeling, chart preparation. | Keeps chart measurements and UI annotations separate from training APIs. |
| `src/validation.py` | `validate_release()` checks Python/Clang, package imports, available experiment/feedback schemas, then invokes unittest discovery. | Implements `python run.py validate`; returns nonzero when a required check fails. |
| `tests/test_dashboard.py` | Dashboard helper, speedup, source filtering, schema validation, chart and demo-display tests. | Uses synthetic in-memory test data plus current shipped CSV checks. |
| `tests/test_feedback_pipeline.py` | Feedback validation/quarantine, timing helpers, collection correctness guard, incorporation idempotence, run-all, grouped evaluation and demo isolation tests. | Uses temporary directories/mocks for write-path tests; no current dataset/model should be changed by the test methods. |
| `tests/test_features.py` | One feature extraction smoke test for `matrix_multiply.c`. | Requires Clang and writes its generated IR under `results/`. |

### Other important files

- `data/benchmark_manifest.csv`: human/machine-readable summary of all benchmark names, purpose, workload description, source path, and type. Runtime discovery does not consume this manifest; it globs `benchmarks/*.c`.
- `data/experiments.csv`: current measurements, including collection and one incorporated feedback row.
- `data/experiments.pre-release.csv`, `data/experiments.postfeedback-pre-release.csv`: historical snapshots; not current pipeline inputs.
- `data/feedback.csv`: active raw feedback append file.
- `data/feedback.pre_quarantine.csv`: byte-preserving backup of legacy feedback before quarantine.
- `data/feedback.quarantine.csv`: archived legacy rows plus per-row validation explanation.
- `data/demo_feedback.csv`: untracked illustrative examples read by the Feedback tab only.
- `models/reward_model.joblib`: tracked serialized estimator bundle; AppTest successfully exercised its current local loading path, but no quality claim follows from loadability.
- `results/*.ll`: generated Clang IR text snapshots; `results/` also includes Linux ELF binaries. These binaries cannot execute natively on the current Windows host and are not needed to render the dashboard.
- `requirements.txt`: bounded runtime dependencies, including XGBoost optional at code level, pandas, NumPy, scikit-learn, joblib, matplotlib, Streamlit, and Altair.
- `requirements-dev.txt`: includes runtime requirements and pytest.
- `.env.example`: path examples for `ADVISOR_DATA_DIR` and `ADVISOR_MODEL_PATH`; no secrets.
- `.gitignore`: excludes local virtualenvs, caches, secrets, and files with conventional binary extensions. It does not exclude already tracked CSVs, extensionless result binaries, or joblib artifacts.
- `docs/DEPLOYMENT.md`: advises serving reviewed artifact files through hosted Streamlit and not exposing benchmark execution.
- `docs/PROJECT_GUIDE.md`: describes workflows, model, correctness and measurement limitations.
- `docs/DATASET.md`: artifact strategy, schema and limitations.
- `docs/ENGINEERING_AUDIT.md`, `docs/FINAL_RELEASE_REPORT.md`, `docs/RELEASE_CHECKLIST.md`: pre-existing engineering/release notes; see documentation consistency section.
- `LICENSES_AND_CITATIONS.md`: references external suites/libraries; there is no top-level project `LICENSE` file in the tracked inventory.

## 3. Verified architecture and execution flow

### Architecture

```mermaid
flowchart TD
    C[benchmarks/*.c] --> F[src/features.py: extract at Clang -O0]
    F --> X[15 raw IR/source features]
    C --> B[src/benchmarks.py: compile reference and configurations]
    B --> R[O0 reference output]
    B --> E[O2/O3/O3-no-vectorize/O3-no-unroll executables]
    R --> Q[Exact stdout correctness check]
    E --> Q
    Q --> T[5 timed runs; median and MAD]
    T --> D[data/experiments.csv]
    X --> D
    D --> M[src/model.py: clean correct rows; log(speedup)]
    M --> J[models/reward_model.joblib]
    X --> I[CLI inference features from current source]
    J --> I
    I --> A[src/recommendation.py: estimate configurations and apply O3 fallback]
    A --> P[recommend CLI]
    A --> G[feedback CLI: 7-repeat paired O3/candidate measurement]
    G --> H[data/feedback.csv]
    H --> V[validate / quarantine]
    V --> K[incorporate-feedback: append unseen valid rows]
    K --> D
    D --> U[explicit train command]
    H --> UI[Streamlit reads artifacts]
    D --> UI
    J --> UI
    H --> UIR[quarantined feedback history for display]
    UIR --> UI
    DEMO[data/demo_feedback.csv] -->|Feedback tab only, toggle off by default| UI
```

### Collection and feedback sequence

```mermaid
sequenceDiagram
    participant User
    participant CLI as run.py / pipeline.py
    participant Compiler as clang
    participant Bench as benchmarks.py
    participant CSV as experiments.csv / feedback.csv
    participant Model as model.py
    User->>CLI: collect
    CLI->>Bench: collect()
    loop each benchmarks/*.c and each configured bundle
        Bench->>Compiler: compile source at -O0 and configured flags
        Bench->>Bench: warmup, compare stdout to O0 reference
        Bench->>Bench: 5 subprocess timings; median and MAD
    end
    Bench->>CSV: replace experiments.csv after successful batch
    User->>CLI: train / evaluate
    CLI->>Model: validate, filter, regress log(speedup), grouped CV
    Model->>CSV: read experiments.csv
    Model->>Model: persist model bundle (train only)
    User->>CLI: feedback --benchmark NAME
    CLI->>Model: predict candidate configuration
    CLI->>Bench: build O3 baseline and selected candidate; warmup/check; 7 repeats
    Bench->>CSV: append validated feedback row atomically
    User->>CLI: incorporate-feedback, then train
    CLI->>CSV: validate and append unseen valid feedback to experiment CSV
    CLI->>Model: retrain only on explicit train stage
    User->>UI: open dashboard
    UI->>CSV: read/cached CSVs; filter and display, no compiler call
```

### Operations by mode

| Mode | Actual operations |
|---|---|
| `doctor` | Queries `PATH` for `clang`, `opt`, `llvm-config`; attempts tool version commands; imports required Python packages; prints benchmark count/config names. Only missing Clang makes the compiler condition fail; `opt` and `llvm-config` are reported but not required. |
| `collect` | Extracts features (which writes `.ll`), compiles reference/candidates, executes fixed programs with timeouts, and replaces experiments CSV after collection completes. |
| `train` | Reads and validates experiments CSV, filters rows, trains estimator and grouped CV model(s), writes joblib artifact. |
| `evaluate` | Reads and validates experiments CSV, computes grouped CV metrics in memory, does not persist a report file. |
| `recommend` | Extracts fresh features from current benchmark source (writes IR), loads trusted model, estimates each action and prints recommendation. It does not execute or measure the recommended candidate. |
| `feedback` | Same inference, then compiles/runs the selected configuration and an independently measured O3 baseline; appends a validated observation. |
| `incorporate-feedback` | Validates feedback and experiment data; maps correct labeled feedback rows to experiment schema; atomically appends unseen fingerprints. It does not train the model. |
| `quarantine-feedback` | Reads active feedback; preserves original bytes in a backup if absent, separates invalid rows with reasons, and rewrites active feedback to keep valid rows. |
| `all` | Runs doctor, collection, training, evaluation, recommendation for the alphabetically first benchmark, incorporates already-recorded feedback, and retrains. It is **destructive to existing `experiments.csv`** because collection replaces that file; it does not generate feedback. |
| Streamlit | Loads/cache-reads CSVs, validates active experiment/feedback frames for warnings, filters and renders five tabs. It does not compile or run C programs. Demo data is read only for display. |

## 4. Feature schema and data treatment

Features are raw numeric values, no scaling, imputation, or learned preprocessing is present. Each model example appends four one-hot action columns (`action_O3`, `action_O2`, `action_O3_no_vectorize`, `action_O3_no_unroll`) to the 15 fixed fields below. Program ID, compiler, platform, flags, measurement repeats, and input profile are not predictors.

| Name | Extraction in `src/features.py` | Type / limitations |
|---|---|---|
| `ir_instruction_count` | Counts non-empty IR lines after skipping selected comments/declarations/attributes/source/target lines, labels, and braces. | Integer textual heuristic, not LLVM parser instruction semantics. |
| `ir_basic_block_count` | Counts lines matching a simple IR label regex. | Integer; labels with unsupported syntax can be missed or miscounted. |
| `ir_function_count` | Counts lines matching `define`. | Integer textual count. |
| `ir_branch_count` | Counts occurrences of token `br`. | Integer textual count. |
| `ir_cond_branch_count` | Counts `br i1` occurrences. | Integer textual count, not CFG analysis. |
| `ir_load_count`, `ir_store_count` | Counts `load` and `store` token occurrences. | Integer textual counts. |
| `ir_call_count` | Counts `call` or `invoke`. | Integer textual count. |
| `ir_integer_ops` | Counts occurrences from add/sub/mul/div/rem/shift/bitwise token list. | Integer; not type-aware and token regex may count non-op text. |
| `ir_float_ops` | Counts `fadd`, `fsub`, `fmul`, `fdiv`, `frem`. | Integer textual count; does not represent all floating-point instructions. |
| `source_loop_count` | Regex count for `for`, `while`, and `do {` source patterns. | Integer heuristic; formatting/macros/loop forms may be missed. |
| `source_nested_loop_hint` | Boolean-as-int heuristic looking for a `for` nested within a nearby `for` body, with a 300-character window. | 0/1 approximate hint, not parsed nesting depth. |
| `source_array_refs` | Counts identifier followed by bracketed text. | Integer lexical count, not a semantic array-access/dependence count. |
| `source_branch_count` | Counts `if`, `switch`, `case` tokens. | Integer lexical count. |
| `source_line_count` | `splitlines()` count. | Integer source-size proxy. |

Feature IR is generated using the current source at Clang `-O0`. Collection stores feature values at measurement time. The dashboard Advisor selects stored feature rows; CLI `recommend` and `feedback` extract features from current source at inference. There is no source-revision ID to establish that historical feature rows represent the current source.

## 5. ML methodology and limitations

- `action_frame()` copies the feature columns and one-hot encodes action equality. `FEATURES` order is persisted in the bundle and checked by `load()`.
- `_clean_measurements()` retains rows whose correctness parses true and whose numeric speedup is finite and positive. It does not deduplicate identical observations and does not weight by program or context.
- Target is `y = ln(speedup_vs_o3)`, where measured speedup is `baseline_o3_seconds / runtime_seconds`.
- `_new_model()` uses `XGBRegressor` when its import succeeds; otherwise it uses `RandomForestRegressor`. The two families have fixed constructor parameters and random state 42. There is no hyperparameter search.
- Evaluation/training grouped CV uses `GroupKFold`, grouped by `program_id`, up to five folds. A fold holds out entire program identities. Training needs at least 3 programs; cross-validation metadata is computed only at 4 or more.
- Model and fold-median predictor use the same observation-level folds and log-speedup target. Reported `group_cv_log_speedup_mae` and the median comparator are MAE in **natural-log speedup units**, not seconds or percent. Top-1 accuracy is descriptive configuration-choice accuracy; the O3 policy comparison is also descriptive.
- `_grouped_cv_report()` chooses the highest predicted row and compares its configuration with the row having highest measured speedup, once per held-out program. Repeated configurations or contexts can therefore affect row-level fitting/MAE; the small current dataset is mostly one collection observation per configuration/program, plus one feedback observation.
- `train()` fits a final model on all retained rows after calculating CV metadata, then writes a dictionary to `models/reward_model.joblib`. It records `model_version=1`, model, schema, training row/program counts, data signature, and CV values; it does not store a dependency lock, source commit, artifact hash, or hardware context specification.
- Inference applies `exp(predicted_log_reward)` to each model output and fixes O3 to `1.0` because it is the speedup reference. `choose_action()` returns the insertion-order maximum when CV MAE strictly beats median MAE. `use_safe_fallback()` returns true if metrics are absent/unparseable/nonfinite or model MAE is greater than or equal to median MAE; the default action is O3.
- Missing model causes a clear CLI error; incompatible feature/config schema is rejected. Dashboard compares training signature to current experiments and reports stale/legacy status, but stale status does not prevent loading or inference. AppTest found no app exception with the present artifact.
- No confidence intervals, prediction intervals, calibration, causal evaluation, held-out final test set, context-aware features, or importance/explanation output are implemented. `program_id` does not enter the predictor matrix.
- Grouping prevents the same benchmark identity appearing across CV folds, which is a useful guard, but does not establish transfer to new compiler versions/hardware/workload sizes. The model trains over measurement contexts that can differ while context itself is not modeled.
- `evaluate_frame()` returns no CV metrics when fewer than four programs remain. O3 fallback is consequently active for missing grouped metrics, so a successful training artifact does not imply a non-O3 recommendation is eligible.

Current valid row counts and data validation are verified below; training/evaluation were **not** run against the project model or current CSV because training overwrites the tracked joblib artifact and evaluation quality was not needed to establish pipeline behavior. No current performance score is asserted here.

## 6. Benchmarking and correctness

### Compiler configurations

| Name | Clang flags |
|---|---|
| `O3` | `-O3` |
| `O2` | `-O2` |
| `O3_no_vectorize` | `-O3 -fno-vectorize -fno-slp-vectorize` |
| `O3_no_unroll` | `-O3 -fno-unroll-loops` |

These are alternatives of compiler flags, not four independent LLVM passes. `compile_one()` invokes Clang with `-std=c11`, configuration flags, `-lm`, and output path. `compile_reference()` uses `-std=c11 -O0 -lm`. Clang is the only LLVM executable used by compilation/features; `opt` and `llvm-config` are only probed by `doctor()`.

### Kernel inventory

The sources define fixed workloads using compile-time `N`; no CLI input or random input generator is present. All programs print a scalar result, so matching output observes execution but is not proof of all intermediate results.

| Program | Source-defined work and scale |
|---|---|
| `array_sum` | 1,300,000 doubles; fill, elementwise polynomial transform, sum. |
| `array_transform` | 1,800,000 doubles; fill and sum. |
| `branchy` | 5,000,000 integer iterations with two conditional branches. |
| `conditional_count` | 4,000,000 integer iterations with arithmetic reduction. |
| `dot_product` | 7,000,000 integer iterations, conditional counts and sum. |
| `loop_reduction` | 1,600,000-element double dot-product reduction. |
| `matrix_multiply` | 170×170 double matrices; three nested loops; weighted checksum over full result matrix. |
| `matrix_transpose` | 700×700 double matrix; transpose and weighted checksum over full result matrix. |
| `prefix_sum` | 1,400,000 integer prefix elements with loop-carried dependency. |
| `stencil_1d` | 500,000 doubles; 18 stencil/time iterations and center output. |
| `weighted_sum` | 1,200,000 floats; weighted reduction. |

### Timing and correctness implementation

- `collect()` finds sorted `benchmarks/*.c`, creates one context UUID for the batch, records Clang version and `platform.platform()`, and extracts features.
- For each benchmark it compiles an independent `-O0` executable from the same source and all four candidate configurations. It warms up each candidate once and stops before timing if stdout differs from the O0 reference.
- `measure(binary, 5)` runs the executable five times using `subprocess.run` via `execute`; wall time is `time.perf_counter()` around process execution and stdout capture. It rejects nonzero exits, timeouts (90 seconds), nondeterministic stdout across repeats, and nonfinite/nonpositive run durations.
- `aggregate_timings()` reports median and median absolute deviation (MAD); compilation is not inside the timer. The candidate speedup is O3 runtime divided by candidate runtime. Correctness false yields no speedup.
- The collection baseline is the O3 median from the same collection batch. The feedback path compiles/re-times O3 independently from the candidate. It uses seven repetitions; if O3 is selected, one O3 sample set is used for both candidate and baseline, satisfying the O3 self-baseline invariant.
- Feedback and collection store medians and MADs, not raw timing samples. Order is deterministic/sequential (O3 reference/config order), not randomized or interleaved.
- `outputs_match()` performs exact equality of captured stdout. Stderr is not compared. The O0 result is generated from the same source, not an independently implemented oracle; formatted floating-point output can mask numerical differences below printed precision, while floating arithmetic/optimization may also produce a different decimal string despite acceptable numerical closeness. Matrix weighted checksums cover all output cells but can collide.
- Correctness-passing means stdout matched the O0 build in this run; measurement-valid additionally requires schema/provenance/numerical checks; performance-improving means measured speedup > 1 in the same measurement context. None alone proves statistical significance or broader workload benefit.
- Benchmark subprocesses have a 90-second timeout; feature generation has a 60-second timeout. Compiler/runtime errors raise rather than create successful measurements. Full collection writes the CSV only after all benchmark rows are assembled, but the final `to_csv` replacement is not atomic.

### Fair comparison boundaries

Runtime includes process startup and stdout capture. Machine load, thermal state, cache effects, and sequential order may dominate these small programs. Only rows sharing benchmark, compiler/platform, source state, input profile, and comparable timing protocol should be treated as a fair comparison. Metadata was improved but no immutable source revision or globally unique collection-run entity exists in the experiment schema. The current matrix kernels have changed output-observation logic since historical artifact collection; the dashboard warns about this and the old rows should not be described as measurements of the present source.

## 7. Dataset and artifact audit

Counts below were read from current files on 2026-10-12. “Validation errors” uses current `validate_measurements()` for the stated kind; historical/quarantine snapshots are not active training inputs.

| Path | Rows / programs | Schema and current check | Provenance / interpretation |
|---|---:|---|---|
| `data/benchmark_manifest.csv` | 11 / 11 | 5 columns: program, description, workload, source file/type. | Source inventory; manifest is not consumed by runtime discovery. |
| `data/experiments.csv` | 45 / 11 | 32 columns; 0 current experiment validation errors; 0 exact duplicate full rows. Config counts O3=12; others=11 each. All rows report correctness true. | 44 collection rows and 1 incorporated feedback row; compiler metadata says Ubuntu Clang 18.1.3 on WSL2. Row values are machine-specific and historical. |
| `data/experiments.pre-release.csv` | 44 / 11 | 26 columns; 0 validation errors under current experiment validator. | Earlier collection snapshot without new provenance/context columns. |
| `data/experiments.postfeedback-pre-release.csv` | 45 / 11 | 32 columns; 0 validation errors. | Historical 45-row snapshot, not configured pipeline input. |
| `data/feedback.csv` | 1 / 1 | 33 columns; 0 feedback validation errors; `O3`, correctness true. | Active paired feedback sample, separate from collection input until explicit incorporation. |
| `data/feedback.pre_quarantine.csv` | 4 / 1 | Legacy 24-column form, 51 validation errors. | Original legacy feedback backup; missing measurement provenance and invalid O3 self-baselines. |
| `data/feedback.quarantine.csv` | 4 / 1 | Legacy rows plus quarantine reason; 51 validator errors as raw feedback. | Preserved rejected rows; reasons document missing provenance and O3/runtime issues. It is not valid model input. |
| `data/demo_feedback.csv` | 3 / 3 | 35 columns; feedback-shaped, with all required feedback column names. `correctness` is explicitly `Not tested (demo)` and measurement source is `demo`; intentionally not valid real feedback. | Hypothetical display-only sample values; no runtimes or predictions were actually measured/generated by a model. Not tracked at audit time. |
| `models/reward_model.joblib` | N/A | Tracked binary, 216,385 bytes at audit time; load path exercised by dashboard AppTest without error. | Model serialization is environment-sensitive and unsafe to accept from untrusted sources. No retraining or metric verification performed. |
| `results/` | 72 tracked files | 60 extensionless files have ELF magic; 11 `.ll` files are textual IR; plus directory marker. | Local Linux-built executable/IR artifacts. Extensionless ELF binaries are incompatible with native Windows execution and are not needed for dashboard rendering. |

The `.gitignore` ignores virtual environments, caches, common-extension compiled files, and secrets, but the actual experiment/feedback CSVs, joblib bundle, and result artifacts are tracked, so they are not ignored in practice. The four legacy feedback entries are backed up/quarantined rather than repaired. Demo data was not passed to the real-feedback validator, training, or incorporation by any inspected code path.

Current model/platform artifacts are bundled in the checkout. A clean clone of this repository receives tracked CSV and model files; therefore “no generated data” is not a safe assumption for the current tree. Conversely, files in `results/` are platform-specific. No current cloud deployment or artifact privacy configuration was verified.

## 8. Feedback lifecycle audit

1. `python run.py feedback --benchmark NAME` calls `pipeline.feedback(NAME)`. It validates any current active feedback rows before appending; invalid existing feedback stops the operation and points to `quarantine-feedback`.
2. It extracts features from the current C source, loads model and predicts a candidate. Safe fallback may choose O3. Prediction is recorded separately as `predicted_speedup`.
3. It compiles an O0 correctness reference, O3 baseline, and selected candidate; warms them up; checks stdout; takes seven timing samples for baseline and candidate (or one shared O3 set when O3 is the candidate).
4. It stores timestamp, program, action, runtime, O3 runtime, measured speedup, correctness, predicted estimate, context UUID, compiler version/flags, platform, input profile, repeats, MADs and features. It validates the combined frame then atomically writes active `feedback.csv`.
5. `python run.py quarantine-feedback` preserves original bytes on first quarantine if backup does not exist, archives invalid rows/reasons, and leaves valid rows active. The active checked-in CSV currently contains one valid row; the backup/quarantine each have four historical rows.
6. `python run.py incorporate-feedback` validates active feedback and existing experiments, ignores failed/unlabeled rows, converts valid rows to experiment schema, deduplicates by fingerprint, and atomically appends to `experiments.csv`.
7. A separate `python run.py train` is required after incorporation. Neither `incorporate-feedback` nor `all` creates a new feedback measurement; `all` does incorporate already saved records and retrain after first replacing experiment history with a fresh collection.
8. Streamlit displays active plus quarantined feedback and an optional display-only demo dataset. Its runtime comparison chart filters to valid real active feedback only. It does not send UI display rows to model training or incorporation.

Required provenance includes unique measurement context, LLVM/compiler identity and flags, platform, input profile, repeats, and baseline/runtime MAD; timestamp and predicted speedup are also validated. The active feedback schema also requires all static feature fields. Speedup arithmetic and the O3 self-baseline are checked. The pre-quarantine rows lack provenance; three O3 rows also violate exact candidate/baseline equality, so they cannot be upgraded by guessing.

**Exact real-feedback commands:**

```text
python run.py feedback --benchmark matrix_multiply
python run.py incorporate-feedback
python run.py train
```

The first command will append a genuine local observation only if Clang and a valid model are available. Incorporation alone does not retrain.

**Defects/risks:** feedback append uses atomic replacement but has no cross-process lock; simultaneous writers can race between read/validate and replace (not reproduced). Model feedback provenance does not encode source revision or input size beyond a fixed descriptive profile. User feedback is a single selected configuration per run, not online learning. Four old rows are quarantined rather than usable; a dashboard display label does not make them valid.

## 9. Dashboard guide

Shared state is loaded at import from repository-relative `data/` or `ADVISOR_DATA_DIR`, and model from repository-relative path or `ADVISOR_MODEL_PATH`. `read_csv()` is Streamlit-cached; absent files become empty frames; read/parse exceptions emit an error and return empty. Active experiment/feedback CSVs are validation-checked and warnings are shown. Common sidebar controls filter benchmark/config/correctness/compiler/platform. Dark styling is CSS; the chart uses corresponding axis/background colors. There is no `.streamlit` theme configuration.

| Section | Purpose and data | Controls, calculations, messages, limitations |
|---|---|---|
| Overview | Summarizes filtered experiment rows. | Five metrics: benchmark count, observation count, passing count/rate, best stored speedup; lists distinct recorded O3 baselines/contexts. Best speedup uses stored `speedup_vs_o3` after correctness status, not recomputation at the metric site. Warns that matrix results predate changed output observation. Empty state asks for collection. |
| Benchmark Explorer | Individual measured-speedup observations, sourced from collection or incorporated feedback. | Radio keeps source separate; uses shared sidebar filters and `prepare_chart_data()`, recomputes baseline/runtime speedup, checks stored arithmetic, excludes nonpassing observations, labels O3 baseline and shows context tooltips. Warns about matrix source history and legacy `feedback-run` marker. |
| Advisor | Model action estimates plus any matching measured observation. | Uses a stored feature row from `records` (experiments concatenated with active feedback), not newly extracted feature data; loads model and runs estimates. Clearly labels prediction as estimate and shows selected source/context measured speedup separately. If multiple matching measurements, directs user to Experiments. Missing features/model and load errors have messages. The sampled feature row can be historical relative to changed source. |
| Experiments | Tabular collection/incorporated rows. | Default shows selected context, runtime, stored speedup, correctness and provenance; expander reveals all columns. Common filters apply. |
| Feedback | Real active and quarantined history, optionally mixed with display-only demo rows. | Toggle `Show illustrative demo data` defaults off. Four cards summarize real total, valid, rejected/quarantined and displayed demo count. Search and benchmark/config/status filters act on display; detailed provenance and validation reason expander. History separates model estimate from measured speedup. Candidate/O3 chart admits valid real feedback only. Refresh clears Streamlit cache and reruns. Empty state gives `python run.py feedback --benchmark matrix_multiply`. |

Feedback chart compares the recorded baseline and selected runtime; for O3-as-candidate the two values are the same timed sample set by design. Demo speedups/runtimes appear in the table only with an explicit demo label and cannot enter its chart. Demo correctness is not tested; UI warning says this. The Advisor and performance charts do not treat the prediction field as a measured result.

Usability gaps: common filters do not offer a feedback-specific platform/compiler filter inside its own history controls; they use global sidebar selected values only for ordinary experiment views, not Feedback history. Feedback history can be searched on all columns. The table may be wide; two speedup columns are present. No CSV export, pagination, uncertainty visual (MAD is in expander only), context selection, raw-sample view, or automated UI tests are present. Accessibility was not assessed in a browser with assistive technology.

## 10. Environment and dependency findings

| Item | Verified current environment |
|---|---|
| OS / Python | Windows 11 host; project `.venv-release` CPython 3.12.10. README documents Python 3.10+ and recommends 3.11/3.12. |
| Runtime package versions | pandas 3.0.6, NumPy 2.5.4, scikit-learn 1.9.1, joblib 1.6.0, matplotlib 3.11.2, Streamlit 1.65.0, Altair 5.5.0, XGBoost 3.4.1. |
| Test dependency | `pytest` is declared by requirements-dev, but was not installed in `.venv-release`; unittest is available and was used. |
| Compiler tools | `clang`, `opt`, `llvm-config` not found on native Windows `PATH`. `doctor` exits 1 because Clang is absent. |
| Clang requirement | Clang is needed for feature extraction, collection, recommendations/feedback (features are freshly extracted), and one unit test. Dashboard read/render does not require Clang. |
| `opt` / `llvm-config` | Informational checks only; inspected compile paths invoke `clang` directly. |
| Hosted deployment | No GitHub workflow, `.streamlit` config, deployment provider file, authentication, or hosted status was verified. Deployment guide is procedural documentation only. |

`requirements.txt` uses compatible version ranges rather than a lock: NumPy `>=1.24,<3`, pandas `>=2,<4`, scikit-learn `>=1.3,<2`, joblib `>=1.3,<2`, matplotlib `>=3.7,<4`, Streamlit `>=1.50,<2`, Altair `>=5,<6`, XGBoost `>=2,<4`. XGBoost is optional in the model factory and doctor but listed in runtime requirements. Dashboard uses Altair, pandas and Streamlit; matplotlib is listed/checked but not imported by the inspected UI or pipeline. Python version and transitive wheels have not been tested across the entire declared range. No deployment/lockfile compatibility claim is made.

## 11. Reproducibility and safe runbook

The commands below assume the project root and a shell where the chosen Python environment is active. On Windows, install a native Clang toolchain or use the documented WSL2 Ubuntu workflow; native environment checks here have no compiler.

### Non-destructive checks and dashboard

```powershell
python --version
python -m pip install -r requirements.txt
python run.py doctor
python run.py dataset
python run.py validate
streamlit run dashboard.py
```

`doctor`/`validate` are diagnostic/read-only with respect to data/model artifacts, though unit tests create isolated temporary fixtures and Python may create ignored caches. `validate` exits nonzero when Clang or a test is unavailable/fails. Dashboard can display existing tracked data/model without Clang; verify local model compatibility and that checked-in artifacts are appropriate to disclose.

### Preserve data before collection, training, or feedback

These operations have persistent side effects: `collect` replaces experiments; `train` replaces the model; `feedback` appends real feedback; `incorporate-feedback` appends to experiments; `quarantine-feedback` rewrites active feedback and creates/updates quarantine files. Back up any artifact that must be retained outside the destination being replaced. Example PowerShell:

```powershell
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $env:TEMP "llvm-advisor-$stamp"
New-Item -ItemType Directory -Path $backup | Out-Null
Copy-Item data\experiments.csv $backup
Copy-Item data\feedback.csv $backup
Copy-Item models\reward_model.joblib $backup
```

Only when a fresh local collection is intended:

```powershell
python run.py collect
python run.py train
python run.py evaluate
python run.py recommend --benchmark matrix_multiply
```

Feedback is deliberate and separate:

```powershell
python run.py feedback --benchmark matrix_multiply
python run.py incorporate-feedback
python run.py train
```

Do not invoke `python run.py all` without backing up first: it starts with `collect` and replaces `data/experiments.csv`. Do not run `quarantine-feedback` without preserving the files and accepting its active CSV rewrite. The demo dataset is not a step in this pipeline.

### Reproduction limits

The manifest of dependencies is not locked and neither LLVM version nor host architecture is pinned. Existing CSVs are machine-specific. Collection and training may not reproduce existing observations/estimator bytes. No exact hosted deployment was confirmed. CI, compiler matrix tests, and a clean-clone test were not present/run in this audit.

## 12. Test and command execution evidence

All commands below were run using `.venv-release\Scripts\python.exe` unless noted. No successful test is inferred without an executed result.

| Command/check | Result |
|---|---|
| `python run.py doctor` | **Exit 1.** Python 3.12.10 and all checked Python packages available; Clang, `opt`, `llvm-config` absent. Doctor treats missing Clang as failure. |
| `python run.py dataset` | **Printed 11 benchmark names** and their source-list context. |
| Read-only `validate_measurements` on current experiments/feedback | **PASS, 0 errors each**. Historical experiment snapshots each had 0 errors under current experiment rules. Legacy pre-quarantine and quarantine frames produce 51 errors each when judged as active feedback, expected because these records are archived invalid feedback. |
| `python run.py validate` | **Exit 1; 9/11 checks passed.** Python/packages/active experiment CSV/feedback CSV passed; Clang blocked; unit-test group failed because `test_matrix_features` needs Clang. |
| `python -m unittest discover -s tests -p test_dashboard.py -v` | **PASS, 19 tests.** |
| `python -m unittest discover -s tests -p test_feedback_pipeline.py -v` | **PASS, 17 tests.** Tests use temporary paths/mocks for writes. |
| `python -m unittest discover -s tests -v` | **37 run, 36 passed, 1 error.** Error: `test_matrix_features` raised `RuntimeError: clang not found. Install LLVM/Clang and ensure clang is on PATH.` |
| AST parse over `run.py`, `dashboard.py`, `src/*.py`, `tests/*.py` | **PASS, 15 Python files**, using `ast.parse` (no bytecode generation). |
| `streamlit.testing.v1.AppTest` on `dashboard.py` | **PASS:** five expected tabs; no app exceptions/errors; model load/recommendation completed sufficiently to render Advisor metrics. |
| Demo toggle in earlier AppTest run during the preceding implementation task | Default-off and enabled render passed; this is corroborating workspace evidence, not a fresh benchmark/measurement. |
| `git diff --check` | Passed in the preceding workspace state. A final docs-only diff check is performed after writing this report. |
| `python -m pytest` | **NOT RUN:** pytest not installed in selected environment. |
| Feature extraction/compile matrix/full benchmark correctness/timing | **NOT RUN:** Clang absent on host. |
| `train`, `evaluate` on current model/artifact; `collect`, `feedback`, `incorporate-feedback`, `quarantine-feedback` | **NOT RUN** during audit to avoid overwriting model/data or changing pipeline state. |
| Cloud deployment/Altair compatibility in hosted environment | **NOT RUN:** no hosted environment/configuration available. |

An attempted `python -m py_compile run.py dashboard.py src\*.py tests\*.py` call passed the wildcard literally under this PowerShell invocation and errored with `[Errno 22] Invalid argument`; syntax was subsequently checked successfully with AST parsing. This failed command is not counted as a syntax pass.

## 13. Defect register and risks

Severity is an audit judgment; “confirmed” describes an observed implementation limitation/condition, not necessarily an immediate runtime crash.

| ID | Severity / category | Status and evidence | Impact / reproduction | Recommendation and regression test |
|---|---|---|---|---|
| A-01 | **High — measurement validity / source provenance** | Confirmed. `matrix_multiply.c` and `matrix_transpose.c` now emit weighted checksums over full output; existing data lacks a source revision. Dashboard explicitly warns historical rows predate the observability change. | `matrix_multiply`/`matrix_transpose` values cannot be asserted to represent current source observation. Compare source with historical collection date/data; no revision key can distinguish. | Add benchmark source hash/revision to collection and feedback schema and require it in comparisons. Test old/new source rows are not combined or presented as same revision. Preserve old files. |
| A-02 | **High — correctness oracle / scientific validity** | Confirmed limitation. Candidate stdout is compared exactly with a separately compiled O0 binary from the same source. Weighted matrix checksum can collide; scalar outputs cover only observed aggregate. | A shared logic bug in source or checksum collision can pass; floating outputs formatted to eight decimals permit sub-print-precision differences to compare equal. | Add independent expected-result tests or full-output/reference checks with justified numeric tolerances; preserve a regression proving intentionally wrong outputs fail. |
| A-03 | **High — evaluation / contextual confounding** | Confirmed. Model inputs omit compiler/version/platform/input/timing context while experiment and feedback rows may come from different contexts; model uses all passing rows. Current data reports WSL2 Clang 18.1.3, so current context variation is modest but history includes feedback separately. | Learned action reward can reflect context drift, and prediction is not conditioned on deployment machine/compiler. Grouping by program does not fix shift across platforms or source revisions. | Either normalize a defined context protocol and train/evaluate within it, or add validated context representation and leave-one-context-out evaluation. Test no context leakage and fallback under unseen context. |
| A-04 | **High — data/Git hygiene and portability** | Confirmed. CSVs, model and 72 `results/` artifacts are tracked. Sixty extensionless result files start with ELF magic; they are Linux binaries in a Windows checkout. Ignore rules/documentation do not prevent tracked artifacts. | Repo diff/clone ships machine-local measurements and opaque/executable outputs; binaries are not native Windows executables and can be mistaken for reproducible outputs. | Decide explicitly which reviewed data/model artifacts belong in Git; remove generated binaries from future committed state, add effective ignore rules for generated result paths, document artifact policy. Test clean clone dashboard and ensure no binary runtime dependency. |
| A-05 | **Medium — destructive collection / durability** | Confirmed. `benchmarks.collect()` writes `EXPERIMENTS` with direct `to_csv`, replacing file. README warns; `all` always invokes collection first. | Existing experiment history is lost when collection is run; interruption during final serialization could leave a damaged file. | Make output selection/backup explicit, write temp then atomic replace, test prior file survives injected failure and warning/opt-in for replace. |
| A-06 | **Medium — model/data weighting** | Confirmed. `_clean_measurements` retains every valid row and training/evaluation are observation-row based; no deduplication or per-program weighting. Current experiments have 12 O3 vs 11 each other actions because of one incorporated O3 feedback record. | One repeated/context observation has extra influence on fitting and observation MAE. Grouped folds prevent program identity leakage but do not equalize program or context influence. | Decide target sampling/weighting unit; report per-program/context counts; test repeated-row influence and compare program-balanced evaluation. |
| A-07 | **Medium — research claim limits** | Confirmed. 11 fixed small programs; program grouped CV is exploratory, no final external test set, no significance analysis, no prediction uncertainty. No fresh CV was run in audit. | A winner/Top-1 score cannot substantiate generalized runtime benefit. | Acquire larger, source-versioned suites and raw repeated timing data; preregister held-out protocols and compare simple policies. |
| A-08 | **Medium — output-based correctness** | Confirmed. `outputs_match()` requires exact stdout string equality; timing only begins after warmup match and timings are rejected if measured output differs from reference. | Possible false negatives due to floating-point formatting and false positives due to limited printed observables/checksum collision. | Define per-benchmark oracle and tolerance/complete output policy; add tests for numerical edge and changed unobserved output. |
| A-09 | **Medium — local code execution boundary** | Confirmed design boundary. CLI compiles and executes C with `subprocess`, timeouts but no sandbox/resource limits; dashboard reads files only and offers no upload. | Running modified/untrusted benchmark sources on a developer host can execute arbitrary native code. A timeout alone does not confine access/resources. | Keep execution restricted to trusted local/isolated CI; do not expose CLI to public requests. If expanding, use hardened sandbox and resource limits. |
| A-10 | **Medium — deployment reproducibility** | Confirmed. Requirements have ranges, no lockfile, no workflow/deployment config; current Windows host has no Clang. `doctor` fails; `validate` is red. | A clean deployment can differ in Python/Clang/XGBoost serialization; native Windows test suite incomplete. | Add CI matrix and lock/constraints for supported deployments; test clean Windows/WSL/Linux and real hosted build. Do not pin solely by guess. |
| A-11 | **Low — feature extraction fragility** | Confirmed. Regex/text counts approximate IR and source structure and are susceptible to LLVM textual syntax/source formatting. Only one smoke test asserts keys and nonzero instruction/loop count. | Feature semantics may drift by LLVM version or formatting without test failure. | Prefer LLVM parser/pass instrumentation where practical; unit-test known small IR/C fixtures and supported LLVM versions. |
| A-12 | **Low — feedback concurrent append** | Suspected, not reproduced. `feedback()` reads current CSV, validates and atomically replaces; no lock around read/append. | Concurrent CLI invocations can both read the same old frame and the later replace can discard the first new row. | Add interprocess locking or transactional storage; concurrency test with two writers. |
| A-13 | **Low — read failure presentation** | Confirmed behavior. Dashboard returns an empty DataFrame for a missing path; malformed read emits `st.error` then returns empty. | A parse failure can show both error and empty-state language, which may be mistaken for no observations. | Track load status separately from empty dataset; test missing, malformed, and genuinely empty files render distinct states. |
| A-14 | **Low — artifact version metadata** | Confirmed. Model bundle includes model/schema version and feature/action names but not pinned dependency versions, source commit/hash, or reproducibility environment. | Serialization or algorithm behavior can vary by environment; users cannot precisely recreate the artifact. | Persist environment and data/source signatures, model artifact checksum, and training command metadata; test compatibility rejection/message. |

## 14. Security and deployment assessment

- The dashboard itself reads CSV and joblib artifacts and does not compile uploaded C or launch the benchmark CLI. The Streamlit server should still be access-controlled if it exposes machine/platform data.
- `run.py collect`, `feedback`, `recommend` (feature extraction) and related compiler paths invoke subprocesses. Inputs are fixed repository source names, not an upload API, but running modified sources executes native code. Timeout is not a sandbox.
- `joblib.load()` deserializes pickle-compatible data; such files can execute code. Only load a model artifact built/trusted by the project owner; never accept a public upload or arbitrary hosted artifact. The checked-in artifact was loaded by local AppTest as part of verification.
- CSVs/platform/compiler details and model may be machine-specific. Current artifacts are tracked, so publishing the repository publishes them unless repository access controls prevent that.
- No secrets were printed or found in inspected `.env.example`; `.gitignore` excludes `.env` and Streamlit secrets path. Secret scanning was not run.
- No authentication, CSP, deployment config, GitHub Actions workflow, or hosted URL/status was verified. `docs/DEPLOYMENT.md` gives deployment instructions but is not proof of a live deployment.

## 15. Documentation consistency

| Existing documentation | Comparison with implementation/current state |
|---|---|
| `README.md` / `PROJECT_GUIDE.md` | Correctly identify configuration choices, O0-reference limits, collection 5 repeats/feedback 7 repeats, model fallback, source separation, and destructive collection. Demo-feedback description agrees with the currently uncommitted display code/data. |
| `DATASET.md` | Correctly says active feedback is separate and quarantine rows cannot be rehabilitated. Current checked-in active feedback has one complete valid row; its historical quarantine includes 4 rows. |
| `ENGINEERING_AUDIT.md` | Describes an earlier engineering change set and says no Git repository existed. Current checkout has `.git`, branch `main`, commit above; do not use that old statement as current Git state. |
| `FINAL_RELEASE_REPORT.md` | Historical report claims a prior WSL environment, 16-test suite, prior artifact load problem, and absence of Git metadata. Current environment is native Windows CPython 3.12.10; tests are now 37; current AppTest loads the current model without app error; Git metadata exists. These are historical results and should be clearly marked/versioned if retained. |
| `DEPLOYMENT.md` | Properly describes artifact-only dashboard deployment and warns against public benchmark execution. No actual deployment was verified. |
| `RELEASE_CHECKLIST.md` | Requests preserving artifacts and testing deployment; it does not imply release has happened. |
| `.gitignore` vs docs | Some docs say generated data/binaries/model are ignored by default, but these paths are currently tracked; `.gitignore` does not untrack them. This is a current inconsistency. |
| Local presentation claims | No presentation file was found among tracked project files; claims about slides/screenshots were not verifiable. |

The current README CLI labels and empty-state commands match `run.py`. Native Windows support is conditional on Clang installation; docs recommend WSL2 for toolchain consistency. The audit did not assert that the declared lower-bound Python/package matrix works.

## 16. Product readiness scorecard

Ratings are qualitative audit judgments, 0 (absent) to 5 (strong).

| Category | Rating | Rationale |
|---|---:|---|
| Core functionality | 3/5 | Collection, training, recommendation, explicit feedback, incorporation, CLI and dashboard are implemented; native current environment cannot compile because Clang absent. |
| ML methodology | 2/5 | Correct supervised log-speedup/regression and program grouping/fallback exist, but only 11 programs, no uncertainty, context predictors or external final test. |
| Correctness and benchmarking | 2/5 | O0 reference, warmups, repeated medians/MAD and output rechecks exist; weak output oracle, tiny workloads/no raw timings/sequential order limit confidence. |
| Feedback and learning loop | 3/5 | Provenance validation, quarantine, explicit incorporation and idempotence implemented; only one current real feedback, retrain is manual. |
| Dashboard usability | 4/5 | Five sections, filters, clear estimate/measurement distinction, themes, validation and demo display are present; no browser accessibility review/CSV export. |
| Testing | 3/5 | 36/37 suite passes in this host and all 36 relevant dashboard/pipeline cases pass; one compiler test blocked, no CI matrix/live browser run. |
| Documentation | 3/5 | Useful workflow and limitations documentation; release/engineering report has stale environment/Git/test statements and artifact-ignore mismatch. |
| Reproducibility | 2/5 | Fixed sources/flags/context and run commands exist; no lockfile, raw samples, source revision ID, or supported compiler matrix. |
| Security | 2/5 | UI is artifact-only and model trust is documented; native subprocess is not sandboxed and generated artifacts are tracked. |
| Deployment readiness | 2/5 | Procedural guide and environment variables exist, AppTest succeeds; no verified hosted deployment/configuration/CI and artifacts are platform-specific. |
| Research validity | 1/5 | Prototype instruments a hypothesis; dataset/protocol/evaluation do not yet support claims of generalization or causal optimization benefit. |

**Overall distinction:** This is a useful functional research prototype and demonstration UI. It is not a production-ready compiler optimization service, and it is not yet a scientifically validated result that ML recommendations improve runtime across unseen programs or systems.

## 17. Prioritized roadmap

### Stage A — Must fix before relying on results

| Task | Why / likely files | Acceptance and test plan |
|---|---|---|
| Record source revision/fingerprint per measurement and separate old matrix data from current source. | Historical matrix kernels and features lack source identity. Likely `src/benchmarks.py`, `src/pipeline.py`, `src/data_validation.py`, `src/config.py`, `dashboard.py`, CSV schema/docs. | Every new row has source digest; validator detects mismatched rows; UI/metrics cannot compare different source versions; migration preserves legacy files; unit tests cover old/new rows. |
| Improve correctness oracle for floating and aggregate kernels. | Same-source O0 and scalar/checksum output do not prove mathematical correctness. Likely `benchmarks/*.c`, `src/benchmarks.py`, tests/docs. | At least representative independent/reference checks or justified tolerances; deliberate wrong candidate detected; deterministic tests document comparison semantics. |
| Establish a supported clean environment/test matrix. | Current native run lacks Clang; no workflow/lock; local results ELF. Likely requirements/constraints, CI config, README/docs. | Clean supported Windows/WSL/Linux setup with compiler/version pinned or recorded; `doctor`, `validate`, suite, and smoke dashboard pass in CI; artifacts not unintentionally modified. |
| Decide Git policy for artifacts and model. | Data and extensionless ELF executables are tracked despite generated-artifact guidance. Likely `.gitignore`, artifact paths, README/deployment docs. | Explicitly selected reviewed data only; no unnecessary executable outputs; clean-clone smoke test; avoid erasing useful history without a documented archive. |
| Re-run measurement set for current source in preserved output location. | Current artifacts are historical and collection overwrites them. Likely `src/benchmarks.py`, config/run docs, artifact naming. | Backup existing data; new context/source digests recorded; candidate correctness validated; raw timings retained; no claim from prior rows. |

### Stage B — Reliability, clarity and evaluation

| Task | Why / likely files | Acceptance and test plan |
|---|---|---|
| Make training/evaluation program- and context-aware; document sampling. | Current observation-level learning weights repeated rows and omits platform/compiler context. Likely `src/model.py`, validation, reporting/tests. | Define/implement balanced observation unit; evaluate within and across contexts; tests show duplicate repeats do not silently bias target. |
| Capture raw sample timings and randomized/interleaved runs. | Median/MAD alone cannot reconstruct run variance; fixed order is biased. Likely `src/benchmarks.py`, schemas, data docs/dashboard. | Persist every sample/order; validate repeat counts; compare configurations under randomized balanced schedules; plot distributions, not just medians. |
| Strengthen feature extraction tests/parser. | Text regex counts drift with source and LLVM version. Likely `src/features.py`, features tests. | IR fixture with expected counts and supported clang matrix; malformed/unsupported IR errors clearly; feature generation remains stable across supported versions. |
| Improve diagnostics, state, and dashboard tests. | Missing vs malformed files can collapse into empty data; AppTest not in committed suite. Likely `dashboard.py`, `src/dashboard_data.py`, tests. | Tests cover parse failure/empty states, demo display isolation, chart labels, filter behavior, dark/light. |
| Refresh historical docs and reconcile artifact policy. | `FINAL_RELEASE_REPORT.md`/`ENGINEERING_AUDIT.md` contain outdated Git/environment/test statements. Likely docs only after implementation decisions. | Mark prior report as dated or archive it; current runbook/state evidence agrees with tested code. |

### Stage C — Research and product expansion

| Task | Why / likely files | Acceptance and test plan |
|---|---|---|
| Expand program suite/workload sizes and vary inputs responsibly. | 11 fixed small kernels are not broad coverage. | Standard-suite adapter, licensing, independent correctness tests, representative size profiles and source IDs. |
| Compare against strong, predeclared policies and held-out programs/contexts. | Current grouped CV is exploratory and fallback uses O3. | Nested/held-out protocol, median/O3/current-compiler baselines, no tuning on test folds, repeatable report and uncertainty. |
| Add runtime-aware/context-aware action selection and explainability. | Model ignores compiler/hardware and has no prediction uncertainty. | Test within-context and transfer behavior; show confidence or abstain when out-of-distribution; never convert uncertainty to a measured claim. |
| Harden execution if service use is pursued. | Native compiler subprocess is not a sandbox. | Isolated worker, resource/network/filesystem restrictions, input validation and security review before accepting external source/jobs. |
| Verify a real deployment and data governance. | No hosted status/auth config verified; artifacts may be private/machine-specific. | Confirm host, access control, artifact provenance, supported package versions, deployment smoke test, and reviewed public data. |

## 18. Glossary

- **O0 / O2 / O3:** Clang optimization-level flags; O0 is used as the project correctness reference, O3 as speedup baseline.
- **Configuration/action:** One compiler flag bundle evaluated by the advisor; not a single pass.
- **IR:** LLVM intermediate representation emitted by Clang.
- **Feature:** Numeric program/IR descriptor supplied to the reward regressor.
- **Measured speedup:** O3 baseline runtime divided by candidate runtime, from a specific paired context.
- **Predicted speedup:** Exponential inverse transform of model-predicted log speedup; estimate only.
- **Reward model:** Supervised regression on log measured speedup; this is not reinforcement learning.
- **MAD:** Median absolute deviation of run durations, a spread statistic, not a confidence interval.
- **Program-grouped CV:** Cross-validation where a benchmark program identity is held out as a group.
- **Feedback:** Separately measured selected action and O3 baseline, persisted outside experiments until explicit incorporation.
- **Quarantine:** Archived invalid feedback rows with reasons; not valid training data.
- **Demo feedback:** Hypothetical UI-only rows explicitly labelled `DEMO — NOT MEASURED`.
- **Measurement context:** Compiler/platform/input/run identity that constrains meaningful comparison; not a universally stable experiment record ID in legacy rows.

## 19. Unknowns and human confirmation

1. Which tracked CSVs/model artifacts are intentionally approved for publication versus local-only history?
2. Should current stale matrix data be kept as history only, moved to an archive, or regenerated under a new schema/source ID? No data was changed here.
3. Which exact OS/compiler/Python combinations are product-supported, rather than merely documented?
4. Is a real hosted dashboard deployed, and what are its authentication, data location, and artifact update procedures? No provider status was verified.
5. Are there presentation/research claims or an external mathematical oracle that are not present in the tracked repository?
6. Is each fixed benchmark intended to model production workloads, and should floating-point correctness use bit-exact or tolerance-based semantics?
7. Is Git policy meant to commit a trained model and dataset, or generate them in trusted CI/deployment?
8. What evaluation objective should govern fallback/selection: model error, held-out runtime regret, or a policy-level comparison?

## 20. Appendix: configuration and schemas

### CLI command surface

`run.py` subcommands: `doctor`, `collect`, `train`, `evaluate`, `all`, `dataset`, `incorporate-feedback`, `quarantine-feedback`, `validate`, `recommend --benchmark NAME`, `feedback --benchmark NAME`. `recommend` and `feedback` default benchmark to `matrix_multiply`. The parser does not expose output-path options; paths are repository-relative config constants, with environment override used by dashboard/model loading (`ADVISOR_DATA_DIR`, `ADVISOR_MODEL_PATH`).

### Artifact destinations

| Data | Path | Writer behavior |
|---|---|---|
| Collected experiments | `data/experiments.csv` | `collect` overwrites after full successful batch; `incorporate-feedback` appends unseen rows with temp+replace. |
| Active feedback | `data/feedback.csv` | `feedback` appends by temp+replace. |
| Feedback quarantine | `data/feedback.quarantine.csv` | `quarantine-feedback` appends invalid rows/reasons by temp+replace. |
| Original active feedback backup | `data/feedback.pre_quarantine.csv` | First quarantine creates byte-preserving backup only when absent. |
| Illustrative feedback | `data/demo_feedback.csv` | No CLI writer; UI reads it only. |
| Model | `models/reward_model.joblib` | `train` writes serialized dictionary; only trusted artifact should be loaded. |
| Binaries and feature IR | `results/<benchmark>_*`, `results/<benchmark>_features.ll` | Compiler/feature paths overwrite their target names. |

### CSV field groups

- Experiment core: `program_id`, `benchmark_file`, `configuration`, `runtime_seconds`, `baseline_o3_seconds`, `speedup_vs_o3`, `correctness`.
- Feedback core additions: `timestamp`, `iteration`, `predicted_speedup`.
- Shared context/provenance: `measurement_context_id`, `llvm_version`, `compiler_flags`, `baseline_compiler_flags`, `platform`, `input_profile`, `measurement_repeats`, `baseline_mad_seconds`, `runtime_mad_seconds`, `measurement_source`.
- Feature fields: all 15 names listed in §4.
- Quarantine: `quarantine_reason`.
- Demo: additionally `demo_label`; uses visibly nonmeasurement metadata and deliberately non-boolean correctness.

### Key numerical rules

- Measured speedup = `baseline_o3_seconds / runtime_seconds`; finite positive runtimes required.
- A passing row must have finite positive speedup matching arithmetic at `rel_tol=1e-6`, `abs_tol=1e-9`.
- Passing O3 candidate runtime must equal O3 baseline runtime within the same tolerance.
- Failed correctness rows may not carry a speedup label.
- Timed repetitions must be integral and at least 2; feedback requires finite nonnegative MADs.
- Model target = natural log of finite positive measured speedup; inference converts predicted target using `exp()`.
- Safe fallback triggers when grouped metrics are unavailable/nonfinite or model grouped MAE is not less than grouped-median MAE.
