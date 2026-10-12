# Engineering audit

## Scope and method

The audit inspected the command-line entry point, pipeline, compiler/measurement helpers, feature extraction and model code, all benchmark sources, checked-in dataset schemas, tests, dashboard, requirements, ignore rules, and project documentation. The working directory does not contain a Git repository, so no branch or Git backup could be created. Existing experiment and feedback CSV files were read and validated; they have not been rewritten.

## Architecture and execution flow

`run.py` dispatches commands to `src.pipeline`. `src.config` defines repository-relative artifact paths, 15 source/IR feature names, and four Clang flag bundles: `O3`, `O2`, `O3_no_vectorize`, and `O3_no_unroll`. Collection extracts features, compiles each fixed C program for each bundle, warms up once, takes five subprocess-wall-time observations per configuration, checks outputs against an `-O0` executable, then writes a median and speedup row into `data/experiments.csv`. Training consumes passing measured rows and persists a joblib bundle. `recommend` predicts log-speedup rewards for each flag bundle. `feedback` separately recompiles the `O3` baseline and selected configuration, takes seven timed observations, and appends to `data/feedback.csv`; incorporation is an explicit later step. The Streamlit dashboard reads these artifacts without executing benchmark programs.

The configuration names are flag bundles, not descriptions of four isolated passes. Feature extraction uses textual IR produced at `-O0` and source-text heuristics. The model is supervised regression over log speedup, not reinforcement learning.

## Findings, priority, evidence, and status

| Priority | Finding and evidence | Change / validation |
|---|---|---|
| High | Collection treated `-O3` output as its own correctness oracle. A shared miscompile or output rounding could therefore pass. The two matrix kernels observed only `c[N-1][N-1]` or `b[N-1][N-1]`, leaving much of the workload unobserved. | Collection and feedback now compare against a separately compiled `-O0` reference. Matrix kernels print a weighted checksum over every output element. Unit tests cover comparison and invalid speedup guards. This is still not an independent mathematical oracle; checksum collisions are possible. Runtime pipeline could not be executed here because Clang is unavailable. |
| High | The legacy experiment CSV has no durable run/experiment ID. Collection and feedback use different compiler/timing contexts; the same `array_sum` configuration is recorded against 0.012398 s (collection, 5 repeats) and 0.009940884999878108 s (feedback-run, 7 repeats). | Charts and Advisor comparisons now select measurement sources and compiler/platform context; validation checks baseline consistency within available context. No data was reconciled or fabricated. The CSV schema was preserved, so durable experiment identity remains a known limitation. |
| Medium | The previous dashboard median grouped configurations across programs and sources; wide raw tables obscured useful fields and predictions were not distinguished from measurements. | Replaced with benchmark/context-specific individual measurements, clear O3 baseline, estimate/measured labels, accessible details, filters, section navigation, and theme styling. Chart input and filter helpers have tests. Live Streamlit interaction could not be exercised in this environment. |
| Medium | Feedback incorporation appended a row every time it ran. The current feedback observation already appears in the experiment table. | Added exact measurement fingerprints and idempotent append; tests cover duplicate and new observations. Existing CSVs remain untouched. |
| Medium | Model training clipped log-speedup targets to a fixed interval without reporting it. Evaluation was grouped by program but only reported model MAE. | Training validates positive finite speedups and uses the measured log-speedup directly. Grouped CV now compares to a fold median baseline and reports top-1 selection beside the O3 policy. Dataset size still limits conclusions; diagnostics are exploratory. |
| Medium | CSV schemas, correctness encodings, runtime values, baseline/speedup arithmetic, and feedback values were not consistently validated before use. | Added schema/data checks used in model training, feedback incorporation, dashboard warnings, and `python run.py validate`. Current experiment (45 rows) and feedback (1 row) tables pass these checks. |
| Low | `docs/DATASET.md` incorrectly described 10 kernels; dependencies did not explicitly declare imported Altair or joblib; ignore rules were narrow. | Corrected count and limitations, declared direct imports, and expanded local-artifact/secrets ignores. |
| Low | Feature counts are textual/heuristic, including approximate loop features; timing includes process launch/output capture and configurations run sequentially. | Documented these limitations and the need for better workload sizing, randomized order, and independent program holdout. No unsupported performance claim is made. |

## Data evidence

The checked-in local experiment table has 45 rows: 11 programs × 4 configurations plus one incorporated feedback observation. `feedback.csv` has one row. For `array_sum`, collection has an O3 baseline of 0.012398 s and five repeats; its separately executed feedback observation has an O3 baseline of approximately 0.009941 s and seven repeats. The two records describe different timing runs. The audit verified their stored speedups against their own baseline/runtime values; it did not combine them.

The artifact schemas remain unchanged. Existing local CSV files and model artifacts are ignored by default; inspect/backup generated data before sharing or deploying it.

## Security and deployment boundary

The CLI compiles and executes fixed repository benchmark sources with subprocess timeouts; it is a local developer workflow, not a sandbox. The Streamlit dashboard reads artifacts only and does not provide source upload or compilation. Do not expose the local CLI as a public execution service. Joblib models must be trusted because deserialization can execute code. The dashboard deployment process is documented in [DEPLOYMENT.md](DEPLOYMENT.md).

## Validation evidence and unverified work

The native Windows Python did not have Clang, and the full Windows test run consequently could not execute feature extraction. A WSL Ubuntu-D environment was available; Clang 18.1.3 and an isolated Python test environment were used to run the complete suite and release validator successfully. All 11 benchmark sources were compiled under each of the four configurations and compared with separately compiled `-O0` output; this verifies output agreement, not timing.

Windows Streamlit AppTest verified that the application presents all five sections, the dark toggle reruns without an unhandled app exception, and an incompatible model file is reported without stopping the page. The checked-in joblib artifact is not loadable under the tested Windows XGBoost 3.4.1 (`input stream corrupted`). It was left untouched. Training/evaluation was separately exercised with a temporary WSL Random Forest model; the grouped median baseline outperformed it on log-speedup MAE for this dataset.

No full benchmark collection or timed comparison was run during this audit because collection overwrites `data/experiments.csv`. The repository folder has no Git metadata, so a branch/commit backup was unavailable; data files were preserved. Exact environment/test/model outcomes and remaining release gates are recorded in [FINAL_RELEASE_REPORT.md](FINAL_RELEASE_REPORT.md).
