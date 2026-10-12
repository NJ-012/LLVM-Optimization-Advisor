warning: in the working copy of 'README.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/DATASET.md', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/README.md b/README.md[m
[1mindex 1dc1a14..3e66106 100644[m
[1m--- a/README.md[m
[1m+++ b/README.md[m
[36m@@ -75,7 +75,7 @@[m [mFeedback records must include a unique measurement context, compiler/version and[m
 [m
 ## Dashboard[m
 [m
[31m-The dashboard offers Overview, Benchmark Explorer, Advisor, Experiments, and Feedback sections. Sidebar filters include benchmark, configuration, correctness, compiler/run marker, and platform. The speedup chart shows individual measurements for one benchmark and source, labels the O3 baseline, and includes source/timing tooltips. Detailed IR/platform/source features are available in an expander. Estimated model recommendations remain visibly distinct from measured results. A sidebar control switches light/dark styling.[m
[32m+[m[32mThe dashboard offers Overview, Benchmark Explorer, Advisor, Experiments, and Feedback sections. Sidebar filters include benchmark, configuration, correctness, compiler/run marker, and platform. The speedup chart shows individual measurements for one benchmark and source, labels the O3 baseline, and includes source/timing tooltips. Feedback includes validation/quarantine history and a candidate-versus-O3 runtime chart. Its `Show illustrative demo data` toggle is off by default; enabled examples from `data/demo_feedback.csv` are labelled `DEMO — NOT MEASURED` and are used only for display. Demo rows are never read by collection, training, evaluation, or feedback incorporation. Predicted speedup remains an estimate and is kept distinct from measured speedup. Detailed IR/platform/source features are available in an expander. A sidebar control switches light/dark styling.[m
 [m
 The dashboard needs no compiler; it reads CSVs from `data/` and an optional local model artifact. For a mounted/exported artifact directory, set `ADVISOR_DATA_DIR` to the directory containing `experiments.csv` and `feedback.csv` before launch. It only displays existing data and never executes uploaded C code.[m
 [m
[1mdiff --git a/docs/DATASET.md b/docs/DATASET.md[m
[1mindex 9c33ac8..8980190 100644[m
[1m--- a/docs/DATASET.md[m
[1m+++ b/docs/DATASET.md[m
[36m@@ -8,6 +8,8 @@[m [mExecution time depends on CPU, OS, compiler version, compiler flags, power manag[m
 [m
 A machine-readable manifest is provided at `data/benchmark_manifest.csv`. The measured runtime dataset is created by `python run.py collect`; any existing CSV artifact is machine-specific and must not be represented as portable. Collection overwrites `data/experiments.csv`, so back it up first when preserving history matters.[m
 [m
[32m+[m[32m`data/demo_feedback.csv` contains hypothetical, schema-shaped examples for demonstrating the dashboard. They are explicitly labelled `DEMO — NOT MEASURED`, are not benchmark results, and are read only by the Feedback display when its demo toggle is enabled. The CLI pipeline reads `experiments.csv` and `feedback.csv` by their configured paths; it does not include demo data in training, evaluation, or feedback incorporation.[m
[32m+[m
 ## Standard dataset extension: PolyBench/C[m
 PolyBench/C 4.2.1 is a public suite of 30 numerical kernels. See the upstream repository and license: https://github.com/MatthiasJReisinger/PolyBenchC-4.2.1 . This project does not redistribute the full suite. Download it separately, review its license, then adapt kernels that compile as standalone programs or add an adapter for the PolyBench utilities. Do not simply copy PolyBench source files into `benchmarks/` without preserving required headers, utility code, and license notices.[m
 [m
