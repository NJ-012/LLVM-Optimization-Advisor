# Release checklist

## Before collecting

- [ ] Confirm Clang, `opt`, `llvm-config`, Python, and package versions with `python run.py doctor`.
- [ ] Back up `data/experiments.csv`, `data/feedback.csv`, and any trusted model artifact.
- [ ] Review the fixed C benchmark sources and compiler flag bundles.
- [ ] Run `python run.py collect` only when replacing the local collection CSV is intended.
- [ ] Run `python run.py validate`; investigate every failure or blocked check.

## Before training or publishing results

- [ ] Confirm CSV correctness, finite positive runtimes, baseline context, and speedup arithmetic.
- [ ] Keep feedback and collection sources identifiable; do not pool different workload/compiler/platform contexts.
- [ ] Run `python run.py train` and record grouped model-versus-baseline diagnostics.
- [ ] Do not claim improvements unless supported by new measurements and suitable repeated/held-out experiments.
- [ ] Confirm the model artifact loads in the intended runtime and is from a trusted source.

## Dashboard and deployment

- [ ] Run `python -m unittest discover -s tests`.
- [ ] Run `streamlit run dashboard.py`; verify five sections, filters, both themes, chart tooltips, empty states, and Advisor status.
- [ ] Confirm dashboard package versions and model serialization compatibility in deployment.
- [ ] Review CSV/model data for private or machine-specific information before publication.
- [ ] Keep benchmark compilation/execution out of public dashboard requests.
- [ ] Configure authentication/access control where artifacts are not public.
- [ ] Follow [DEPLOYMENT.md](DEPLOYMENT.md); no hosting or authentication is provisioned by this repository.

## Remaining manual decision

- [ ] Decide whether the existing experiment history should be preserved, archived, or replaced before running `python run.py all`.
