# Dataset strategy

## Included data
This repository includes 11 small deterministic C benchmark programs, spanning reductions, memory traversal, matrix operations, stencils, arithmetic, and branch-heavy loops. They are source benchmarks, not portable pre-recorded timing data.

## Why runtime data is generated locally
Execution time depends on CPU, OS, compiler version, compiler flags, power management, and background load. Shipping made-up or other-machine runtimes would mislead. Run `python run.py collect` to produce `data/experiments.csv` on your machine. Each program is compiled under four configurations and timed repeatedly.

A machine-readable manifest is provided at `data/benchmark_manifest.csv`. The measured runtime dataset is created by `python run.py collect`; any existing CSV artifact is machine-specific and must not be represented as portable. Collection overwrites `data/experiments.csv`, so back it up first when preserving history matters.

`data/demo_feedback.csv` contains hypothetical, schema-shaped examples for demonstrating the dashboard. They are explicitly labelled `DEMO — NOT MEASURED`, are not benchmark results, and are read only by the Feedback display when its demo toggle is enabled. The CLI pipeline reads `experiments.csv` and `feedback.csv` by their configured paths; it does not include demo data in training, evaluation, or feedback incorporation.

## Standard dataset extension: PolyBench/C
PolyBench/C 4.2.1 is a public suite of 30 numerical kernels. See the upstream repository and license: https://github.com/MatthiasJReisinger/PolyBenchC-4.2.1 . This project does not redistribute the full suite. Download it separately, review its license, then adapt kernels that compile as standalone programs or add an adapter for the PolyBench utilities. Do not simply copy PolyBench source files into `benchmarks/` without preserving required headers, utility code, and license notices.

## Schema
`program_id`, `benchmark_file`, `configuration`, `runtime_seconds`, `baseline_o3_seconds`, `speedup_vs_o3`, `correctness`, `llvm_version`, `platform`, `input_profile`, `measurement_repeats`, and static IR/source features. Newly collected rows add a measurement-context ID, selected and baseline compiler flags, and MAD values; these are additive columns, while the legacy columns remain unchanged. Feedback retains its existing columns and adds the same provenance and uncertainty fields. It is not merged until `python run.py incorporate-feedback`.

## Limitations
The included 11 kernels are a compact project dataset, not a replacement for a large standard suite. Feature extraction uses textual `-O0` LLVM IR and source heuristics; loop features are approximate. Timings include process startup and output capture, use one warm-up then five timed repetitions for collection (seven for feedback), and use the median with median absolute deviation (MAD) as a spread statistic. Correctness is checked against the O0 executable both before and after timing. Compilation is outside the execution timer. Measurements remain sensitive to load, cache state, thermal behavior, and sequential configuration order; MAD is not a confidence interval and no significance claim is made. Feedback uses its own explicitly identified O3 measurement context and is not interchangeable with a collection baseline.

The historical feedback CSV predates context provenance. In particular, O3 candidate rows were obtained by separately timing the baseline and selected configuration, so run-to-run noise made their runtime differ from the stored O3 baseline. Those rows are invalid as O3 self-baselines and cannot be upgraded by guessing a context. `python run.py quarantine-feedback` preserves the original bytes in `data/feedback.pre_quarantine.csv`, writes invalid records and reasons to `data/feedback.quarantine.csv`, and leaves them out of training; regenerate them to obtain valid measurements.

The legacy experiment schema does not contain all raw timing samples or a source revision. New rows record context identity and compiler/platform/flags metadata, but existing history remains unchanged. For research, expand to standard suites, randomize/interleave measurement order, retain raw samples, and use held-out programs with simple policy baselines.
