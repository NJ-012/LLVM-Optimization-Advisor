# Hosted dashboard deployment

## Architecture

Run compiler experiments on a trusted local machine or CI worker, then publish only reviewed CSV/model artifacts. The Streamlit dashboard reads `experiments.csv` and `feedback.csv`; it does not compile or execute C source. Do not deploy the benchmark CLI as a public service and do not accept uploaded source for execution.

## Prepare and review artifacts

1. In the project environment, run `python run.py collect`, `python run.py train`, and `python run.py validate`.
2. Back up the results before collection because `collect` replaces `data/experiments.csv`.
3. Review records for correctness, positive finite timings, matching speedup arithmetic, compiler/platform/input context, and private or sensitive data.
4. Preserve `data/experiments.csv` and `data/feedback.csv` as separate tables. The legacy schema has no stable experiment ID; never combine different compiler/platform/input contexts into one comparison.
5. If recommendations are required, provide the joblib model artifact produced by training. Only deploy an artifact you built or otherwise trust, and keep its Python/scikit-learn/XGBoost environment compatible. Joblib files are executable serialization formats and must not be accepted from untrusted users.

Optional artifact locations can be set with `ADVISOR_DATA_DIR` and `ADVISOR_MODEL_PATH`; see [../.env.example](../.env.example). The example contains paths only, no credentials.

## Streamlit Community Cloud or another hosted Streamlit runtime

1. Push the reviewed application source and `requirements.txt` to a private or access-controlled repository.
2. Put approved CSV artifacts in the app's `data/` directory and, if serving predictions, the trusted trained model in `models/reward_model.joblib`. Generated files are ignored by default; explicitly stage only files approved for disclosure. Do not stage local binaries, unrelated results, secrets, or private paths.
3. Configure the app entry point as `dashboard.py` and install from `requirements.txt`.
4. Deploy and verify empty states, data-quality messages, tabs, filters, theme, charts, and an Advisor recommendation against the artifact version being served. A dashboard launch alone does not validate model quality or measurement correctness.
5. To mount artifacts elsewhere, set `ADVISOR_DATA_DIR` to the directory containing both CSV files in a runtime that supports application environment variables, then restart. The default is repository-relative `data/`.

No authentication, artifact upload, database, secrets, or hosted benchmark execution is configured by this project. Restrict repository/artifact access to the intended audience. If the hosting provider cannot securely expose the data/model artifact, do not deploy those records; the app can display an empty state until approved artifacts are provided.

## Refresh procedure

Run collection/training in the trusted local environment, validate and review the new files, then replace only the approved deployment artifacts through the repository's normal review process. Do not overwrite the user's local experiment history as a deployment side effect.
