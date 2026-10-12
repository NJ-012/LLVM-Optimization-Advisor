# Project guide

## Exact project
Build an ML advisor that analyzes C benchmark programs via LLVM IR features, estimates relative speedup for a small set of LLVM compiler configurations, chooses a configuration, measures it, and stores feedback for retraining.

## Why configurations instead of named passes?
Clang/LLVM does not expose every desired transformation as a stable, universally available standalone command. `-O2`, `-O3`, `-fno-vectorize`, `-fno-slp-vectorize`, and `-fno-unroll-loops` are practical command-line controls. These choices are configuration alternatives, not isolated independent passes. Do not call them “four independent optimization passes” in the report.

## Run workflow
1. `python run.py doctor`
2. `python run.py collect`
3. `python run.py train`
4. `python run.py evaluate`
5. `python run.py recommend --benchmark matrix_multiply`
6. `python run.py feedback --benchmark matrix_multiply` to intentionally create a fresh, paired measurement.
7. `python run.py incorporate-feedback`
8. `python run.py train`
9. Optional dashboard: `streamlit run dashboard.py`

`python run.py all` is a repeatable batch, not a feedback generator. It runs diagnostics, collection, training, grouped evaluation, recommendation, incorporation of already logged feedback, and retraining. Collection overwrites `data/experiments.csv`; back it up first if its history must be retained. Run `feedback` explicitly when a new observation is intended.

Legacy feedback without measurement-context provenance, or with invalid O3 self-baselines, must not be edited into validity. `python run.py quarantine-feedback` makes an exact original-file backup and isolates invalid rows with reasons before new measurements are recorded.

## ML model
An XGBoost regressor (with Random Forest fallback) learns estimated log speedup from static features plus a one-hot configuration choice. At inference time, it predicts reward for each configuration and chooses the highest estimate. This is a simple supervised reward model, not reinforcement learning. Feedback is measured and logged; `incorporate-feedback` adds valid observations to the experiment table and retraining incorporates them.

## Correctness and measurement
The collector checks each candidate's output against a separately compiled `-O0` reference before accepting timings and checks deterministic output again during repetitions. Matrix multiplication and transpose print weighted checksums over every output element; this observes more work but is not an independent mathematical oracle and can collide. Collection performs one warm-up and five timed runs; feedback uses seven. Reported runtime is the median and spread is median absolute deviation (MAD); compilation is outside the execution timer. Collection and feedback are distinct contexts, and feedback stores the compiler, flags, platform, benchmark identity, unique context ID, and input profile. Very short runtimes are noisy; consider larger benchmark sizes, randomized/interleaved order, independent references, and raw observations before making performance claims.

Grouped evaluation holds out entire program identities. It compares the model and training-fold median baseline on identical folds and log-speedup targets, and reports program/observation counts. Model selection is fixed before folds; no held-out tuning is performed. When grouped MAE does not beat the median baseline or is unavailable, recommendations conservatively select O3 and display a warning. The metrics are exploratory and do not establish generalization, statistical significance, or expected performance gains.

## Honest success criteria
A successful engineering prototype completes the pipeline and records reproducible data. The research hypothesis is supported only if experiments show feedback ML performs better than static ML or relevant baselines under a fair protocol. It is acceptable if it does not.
