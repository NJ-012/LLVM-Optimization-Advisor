from pathlib import Path
import os

import altair as alt
import pandas as pd
import streamlit as st

from src.config import (
    CONFIGS,
    EXPERIMENTS,
    FEATURES,
    FEEDBACK,
    FEEDBACK_QUARANTINE,
    MODEL,
)
from src.data_validation import combine_chart_sources, measurement_fingerprint, validate_measurements
from src.recommendation import use_safe_fallback
from src.dashboard_data import (
    calculate_measured_speedup,
    correctness_status,
    FEEDBACK_COLLECTION_COMMAND,
    filter_feedback_history,
    filter_observations,
    measurement_source,
    prepare_demo_feedback,
    prepare_feedback_history,
    prepare_chart_data,
)


st.set_page_config(page_title="Adaptive LLVM Advisor", layout="wide")
DATA_DIR = Path(os.environ.get("ADVISOR_DATA_DIR", str(EXPERIMENTS.parent))).expanduser()
MODEL_FILE = Path(os.environ.get("ADVISOR_MODEL_PATH", str(MODEL))).expanduser()


@st.cache_data
def read_csv(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(file_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        st.error(f"Could not read {file_path.name}: {exc}")
        return pd.DataFrame()


experiments = read_csv(str(DATA_DIR / EXPERIMENTS.name))
feedback = read_csv(str(DATA_DIR / FEEDBACK.name))
quarantined_feedback = read_csv(str(DATA_DIR / FEEDBACK_QUARANTINE.name))
demo_feedback = read_csv(str(DATA_DIR / "demo_feedback.csv"))
for frame, name in ((experiments, "experiments"), (feedback, "feedback")):
    if not frame.empty:
        issues = validate_measurements(frame, name)
        if issues:
            st.error(f"Data quality issue in {name} CSV: " + "; ".join(issues[:5]))
for frame, fallback_source in ((experiments, "collection"), (feedback, "feedback")):
    if not frame.empty:
        if "measurement_source" not in frame:
            frame["measurement_source"] = (
                frame["llvm_version"].map(measurement_source)
                if fallback_source == "collection" and "llvm_version" in frame
                else fallback_source
            )

records = pd.concat([experiments, feedback], ignore_index=True, sort=False)
chart_experiments = combine_chart_sources(experiments, feedback)
benchmark_names = sorted(set(records.get("program_id", pd.Series(dtype=str)).dropna().astype(str)))
benchmark_names = sorted(set(benchmark_names) | {p.stem for p in (EXPERIMENTS.parent.parent / "benchmarks").glob("*.c")})
configuration_names = list(CONFIGS)
BENCHMARKS_WITH_CHANGED_OBSERVABILITY = {"matrix_multiply", "matrix_transpose"}
compiler_names = (
    sorted(records["llvm_version"].dropna().astype(str).unique())
    if "llvm_version" in records
    else []
)
platform_names = (
    sorted(records["platform"].dropna().astype(str).unique())
    if "platform" in records
    else []
)

st.sidebar.header("Display")
dark_theme = st.sidebar.toggle("Dark theme", value=False)
if dark_theme:
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        .stApp { background: #101827; color: #e5e7eb; }
        [data-testid="stHeader"], [data-testid="stSidebar"] { background: #111c2d; }
        [data-testid="stMetric"], [data-testid="stExpander"] {
            background: #182438; border-radius: 0.6rem; padding: 0.5rem;
        }
        [data-testid="stMarkdownContainer"], label, .stCaption { color: #e5e7eb; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        :root { color-scheme: light; }
        .stApp { background: #f7f9fc; color: #1f2937; }
        [data-testid="stHeader"], [data-testid="stSidebar"] { background: #ffffff; }
        [data-testid="stMetric"], [data-testid="stExpander"] {
            background: #ffffff; border-radius: 0.6rem; padding: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("ML-Based Adaptive LLVM Optimization Advisor")
st.caption("Local benchmark measurements are hardware- and compiler-specific. Estimates are not measurements.")

st.sidebar.header("Filters")
benchmark = st.sidebar.selectbox(
    "Benchmark",
    benchmark_names,
    index=0 if benchmark_names else None,
    placeholder="No benchmarks available",
)
selected_configurations = st.sidebar.multiselect(
    "Configurations",
    configuration_names,
    default=configuration_names,
)
correctness_filter = st.sidebar.selectbox(
    "Correctness",
    ["All", "Passed", "Failed", "Unknown"],
)
selected_compiler = st.sidebar.selectbox("Compiler / run marker", ["All"] + compiler_names)
selected_platform = st.sidebar.selectbox("Platform", ["All"] + platform_names)


def apply_filters(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    return filter_observations(
        frame,
        benchmark=benchmark,
        configurations=selected_configurations,
        correctness=correctness_filter,
        compiler=None if selected_compiler == "All" else selected_compiler,
        platform=None if selected_platform == "All" else selected_platform,
    )


filtered_experiments = apply_filters(experiments)
filtered_feedback = apply_filters(feedback)


def show_table(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    if frame.empty:
        st.info(f"No {label} match the current filters.")
        return
    visible = [column for column in columns if column in frame.columns]
    st.dataframe(frame[visible], width="stretch", hide_index=True)
    with st.expander(f"Show all {label} columns"):
        st.dataframe(frame, width="stretch", hide_index=True)


def chart_for(source: str, chart_theme: str) -> None:
    if chart_experiments.empty or not benchmark:
        st.info("No experiment measurements are available yet. Run `python run.py collect`.")
        return
    try:
        chart_data = prepare_chart_data(
            chart_experiments,
            benchmark=benchmark,
            source=source,
            configurations=selected_configurations,
            compiler=None if selected_compiler == "All" else selected_compiler,
            platform=None if selected_platform == "All" else selected_platform,
        )
    except ValueError as exc:
        st.error(f"Cannot chart inconsistent measurements: {exc}")
        return
    if chart_data.empty:
        st.info(f"No passing {source.replace('_', ' ')} measurements match these filters.")
        return

    axis_color = "#e5e7eb" if chart_theme == "dark" else "#263445"
    baseline_color = "#f4a261" if chart_theme == "dark" else "#c2410c"
    other_color = "#5b9bd5" if chart_theme == "dark" else "#2563a6"
    plot = alt.Chart(chart_data)
    bars = plot.mark_bar().encode(
        x=alt.X(
            "measured_speedup:Q",
            title="Measured speedup vs O3 (×)",
            scale=alt.Scale(domainMin=0),
            axis=alt.Axis(format=".2f"),
        ),
        y=alt.Y("configuration_label:N", title="Configuration", sort=None),
        color=alt.condition(
            alt.datum.configuration == "O3",
            alt.value(baseline_color),
            alt.value(other_color),
        ),
        tooltip=[
            alt.Tooltip("configuration_label:N", title="Configuration"),
            alt.Tooltip("measured_speedup:Q", title="Measured speedup (×)", format=".4f"),
            alt.Tooltip("baseline_seconds:Q", title="O3 baseline (s)", format=".6f"),
            alt.Tooltip("runtime_seconds:Q", title="Configuration runtime (s)", format=".6f"),
            alt.Tooltip("measurement_source:N", title="Source"),
            alt.Tooltip("measurement_repeats:N", title="Timed repeats"),
            alt.Tooltip("llvm_version:N", title="Compiler / run marker"),
            alt.Tooltip("platform:N", title="Platform"),
            alt.Tooltip("input_profile:N", title="Input profile"),
        ],
    )
    value_labels = plot.mark_text(
        align="left", baseline="middle", dx=5, color=axis_color
    ).encode(
        x="measured_speedup:Q",
        y=alt.Y("configuration_label:N", sort=None),
        text=alt.Text("measured_speedup:Q", format=".3f"),
    )
    baseline = alt.Chart(pd.DataFrame({"speedup": [1.0]})).mark_rule(
        color=baseline_color, strokeDash=[5, 4], strokeWidth=2
    ).encode(x=alt.X("speedup:Q"))
    st.altair_chart(
        (bars + value_labels + baseline).properties(
            height=max(180, 42 * len(chart_data)),
            padding={"right": 45},
            background="#182438" if chart_theme == "dark" else "#ffffff",
        ).configure_axis(labelColor=axis_color, titleColor=axis_color, gridColor="#64748b55")
        .configure_view(strokeOpacity=0),
        width="stretch",
    )
    st.caption(
        "The dashed vertical line marks 1.00×, the O3 baseline. Bars are individual "
        "correctness-passing measurements; they are not pooled across benchmarks or sources."
    )


tabs = st.tabs(["Overview", "Benchmark Explorer", "Advisor", "Experiments", "Feedback"])
with tabs[0]:
    st.subheader("Overview")
    if benchmark in BENCHMARKS_WITH_CHANGED_OBSERVABILITY:
        st.warning(
            "This kernel's output observation was changed to cover the full result. Existing "
            "CSV rows predate that source change and have no source-revision ID; preserve them "
            "as history, but rerun collection before treating them as measurements of the current source."
        )
    metric_columns = st.columns(5)
    metric_columns[0].metric("Benchmarks in view", filtered_experiments["program_id"].nunique() if not filtered_experiments.empty else 0)
    metric_columns[1].metric("Experiment observations", len(filtered_experiments))
    passing_count = (
        filtered_experiments["correctness"].map(correctness_status).eq("Passed").sum()
        if not filtered_experiments.empty and "correctness" in filtered_experiments
        else 0
    )
    metric_columns[2].metric("Correctness-passing", int(passing_count))
    pass_rate = 100 * passing_count / len(filtered_experiments) if len(filtered_experiments) else 0
    metric_columns[3].metric("Correctness pass rate", f"{pass_rate:.1f}%")
    if not filtered_experiments.empty:
        best_rows = filtered_experiments[
            filtered_experiments["correctness"].map(correctness_status).eq("Passed")
            & filtered_experiments["speedup_vs_o3"].notna()
        ]
        best = best_rows.loc[best_rows["speedup_vs_o3"].astype(float).idxmax()] if not best_rows.empty else None
        best_label = (
            f"{best['configuration']} · {float(best['speedup_vs_o3']):.3f}×"
            if best is not None
            else "No valid measurement"
        )
    else:
        best_label = "No valid measurement"
    metric_columns[4].metric("Best measured in view", best_label)

    st.markdown("#### Recorded O3 baselines by measurement context")
    if not experiments.empty and benchmark and "baseline_o3_seconds" in experiments:
        baseline_rows = experiments[experiments["program_id"].astype(str) == benchmark].copy()
        context_columns = [
            column
            for column in ("measurement_source", "llvm_version", "platform", "measurement_repeats", "baseline_o3_seconds")
            if column in baseline_rows
        ]
        if context_columns and not baseline_rows.empty:
            contexts = (
                baseline_rows[context_columns]
                .drop_duplicates()
                .sort_values(context_columns, kind="stable")
                .rename(
                    columns={
                        "measurement_source": "Source",
                        "llvm_version": "Compiler / run marker",
                        "platform": "Platform",
                        "measurement_repeats": "Timed repeats",
                        "baseline_o3_seconds": "Recorded O3 baseline (s)",
                    }
                )
            )
            st.dataframe(contexts, width="stretch", hide_index=True)
            if contexts.get("Source", pd.Series(dtype=str)).nunique() > 1:
                st.info(
                    "These are separate measurement contexts. In particular, an incorporated "
                    "feedback run recompiles and retimes O3 independently; its baseline is not "
                    "interchangeable with the collection batch baseline."
                )
        else:
            st.info("No recorded O3 baseline is available for this benchmark.")
    else:
        st.info("No benchmark measurements are available yet. Run `python run.py collect`.")

with tabs[1]:
    st.subheader(f"Benchmark Explorer{f' · {benchmark}' if benchmark else ''}")
    if benchmark in BENCHMARKS_WITH_CHANGED_OBSERVABILITY:
        st.warning(
            "Historical measurements for this kernel predate the full-output checksum change. "
            "The CSV schema has no source-revision ID; rerun collection before comparing current-source results."
        )
    available_sources = sorted(
        chart_experiments["measurement_source"].dropna().unique().tolist()
    ) if not chart_experiments.empty else []
    source = st.radio(
        "Measurement source (kept separate)",
        available_sources,
        format_func=lambda value: {
            "collection": "Benchmark collection",
            "feedback": "Incorporated feedback",
        }.get(value, value),
        horizontal=True,
    ) if available_sources else None
    if source:
        chart_for(source, "dark" if dark_theme else "light")
    if selected_compiler == "feedback-run":
        st.info(
            "This is a legacy feedback marker; older feedback rows did not retain the "
            "actual compiler version or measurement context."
        )

with tabs[2]:
    st.subheader("Advisor")
    feature_rows = records
    if benchmark and not feature_rows.empty:
        feature_rows = feature_rows[feature_rows["program_id"].astype(str) == benchmark]
    if not benchmark or feature_rows.empty:
        st.info("Run the benchmark collection or feedback pipeline to provide benchmark features.")
    elif not MODEL_FILE.exists():
        st.info("The trained model is not available. Run `python run.py train` to generate estimates.")
    else:
        try:
            from src.model import load, predict_action
        except (ImportError, RuntimeError) as exc:
            st.error(
                f"Cannot load the advisor model: {exc}. Check the trusted model artifact "
                "and install compatible project dependencies with "
                "`python -m pip install -r requirements.txt`."
            )
        else:
            feature_row = feature_rows.iloc[0]
            missing_features = [name for name in FEATURES if name not in feature_rows or pd.isna(feature_row[name])]
            if missing_features:
                st.error(f"Cannot predict: benchmark features are missing: {', '.join(missing_features)}.")
            else:
                try:
                    model_bundle = load()
                    recommended_configuration, predictions = predict_action(
                        benchmark,
                        {name: feature_row[name] for name in FEATURES},
                        bundle=model_bundle,
                    )
                except (RuntimeError, ValueError, KeyError) as exc:
                    st.error(f"Could not generate an advisor recommendation: {exc}")
                    model_bundle = None
                if model_bundle is not None:
                    st.caption(
                        f"Model version: {model_bundle.get('model_version', 'legacy/unversioned')}; "
                        f"training rows: {model_bundle.get('trained_rows', 'unknown')}; "
                        f"training programs: {len(model_bundle.get('programs', []))}. "
                        "Exploratory grouped-CV MAE: "
                        f"{model_bundle.get('group_cv_log_speedup_mae', 'not available')} "
                        "(log-speedup units)."
                    )
                    st.warning(
                        "This is an exploratory reward model trained on a small benchmark set. "
                        "Grouped validation does not establish generalization; verify candidates "
                        "with fresh measurements before relying on the recommendation."
                    )
                    if use_safe_fallback(model_bundle):
                        st.info(
                            "Safe fallback: O3 is selected because grouped validation is "
                            "missing or did not outperform the training-fold median baseline."
                        )
                    inspected_configuration = st.selectbox(
                        "Configuration to inspect",
                        configuration_names,
                        index=configuration_names.index(recommended_configuration),
                    )
                    selected_prediction = predictions[inspected_configuration]
                    st.markdown(
                        f"**Model recommendation:** `{recommended_configuration}`  \n"
                        f"**Configuration selected for comparison:** `{inspected_configuration}`"
                    )
                    st.caption(
                        f"Predicted speedup: **{selected_prediction:.3f}× (estimate)**. "
                        "This is model output, not a measured performance result."
                    )

                    measurement_rows = feedback if source == "feedback" else experiments
                    if not measurement_rows.empty and source == "collection":
                        measurement_rows = measurement_rows[
                            measurement_rows["measurement_source"].eq("collection")
                        ]
                    matching = (
                        measurement_rows[
                            (measurement_rows["program_id"].astype(str) == benchmark)
                            & (measurement_rows["configuration"] == inspected_configuration)
                        ]
                        if not measurement_rows.empty
                        else pd.DataFrame()
                    )
                    matching = filter_observations(
                        matching,
                        compiler=None if selected_compiler == "All" else selected_compiler,
                        platform=None if selected_platform == "All" else selected_platform,
                    )
                    correctness_values = (
                        sorted(matching["correctness"].map(correctness_status).unique().tolist())
                        if not matching.empty and "correctness" in matching
                        else []
                    )
                    if matching.empty:
                        measured_label = "Not measured in this source/context"
                        correctness_label = "Not measured"
                    else:
                        if len(matching) == 1:
                            row = matching.iloc[0]
                            row_correctness = correctness_status(row.get("correctness"))
                            measured = calculate_measured_speedup(
                                row.get("baseline_o3_seconds"),
                                row.get("runtime_seconds"),
                                row.get("correctness"),
                            )
                            measured_label = (
                                f"{measured:.3f}× (measured)"
                                if measured is not None
                                else "Rejected: correctness failed"
                                if row_correctness == "Failed"
                                else "Unavailable: invalid or missing timing"
                            )
                        else:
                            measured_label = (
                                f"{len(matching)} separate observations; see Experiments"
                            )
                        correctness_label = (
                            correctness_values[0]
                            if len(correctness_values) == 1
                            else "Mixed: " + ", ".join(correctness_values)
                        )
                    cards = st.columns(3)
                    cards[0].metric("Selected configuration", inspected_configuration)
                    cards[1].metric(
                        "Predicted speedup · estimate", f"{selected_prediction:.3f}×"
                    )
                    cards[2].metric("Measured speedup", measured_label)
                    st.write(f"**Correctness status:** {correctness_label}")

with tabs[3]:
    st.subheader("Experiments")
    st.caption(
        "Detailed LLVM IR and source-feature columns remain available in the collapsed "
        "details panel so the default table stays readable."
    )
    show_table(
        filtered_experiments,
        [
            "program_id",
            "measurement_source",
            "configuration",
            "baseline_o3_seconds",
            "runtime_seconds",
            "speedup_vs_o3",
            "correctness",
            "llvm_version",
            "platform",
            "measurement_repeats",
        ],
        "experiment records",
    )

with tabs[4]:
    st.subheader("Feedback")
    st.caption(
        "Measured speedup is calculated from the recorded O3 baseline and candidate runtime. "
        "Predicted speedup is only a model estimate and is never a feedback measurement."
    )
    if st.button("Refresh feedback data"):
        st.cache_data.clear()
        st.rerun()

    real_history = prepare_feedback_history(feedback, quarantined_feedback)
    show_demo = st.toggle("Show illustrative demo data", value=False)
    display_history = real_history
    if show_demo:
        display_history = pd.concat(
            [real_history, prepare_demo_feedback(demo_feedback)],
            ignore_index=True,
            sort=False,
        )
        st.warning(
            "Demo rows are hypothetical examples only: their runtimes and speedups were "
            "not measured, their prediction values are not model outputs, and correctness "
            "was not tested. They are excluded from training, evaluation, feedback "
            "incorporation, and measured-performance charts."
        )

    valid_count = int(real_history["validation_status"].eq("Valid").sum())
    rejected_count = int(
        real_history["validation_status"].isin(["Rejected", "Quarantined"]).sum()
    )
    summary = st.columns(4)
    summary[0].metric("Total real observations", len(real_history))
    summary[1].metric("Valid observations", valid_count)
    summary[2].metric("Rejected / quarantined", rejected_count)

    st.markdown("#### Feedback history")
    st.caption(
        "A recommendation's predicted speedup is an estimate captured at selection time; "
        "the measured speedup below is an observation, and rejected rows are not accepted "
        "as valid performance evidence."
    )
    control_columns = st.columns([2, 1, 1, 1])
    search = control_columns[0].text_input(
        "Search feedback",
        placeholder="Search benchmark, compiler, reason, or context",
    )
    available_benchmarks = sorted(
        display_history.get("program_id", pd.Series(dtype=str))
        .dropna()
        .astype(str)
        .unique()
    )
    chosen_benchmarks = control_columns[1].multiselect(
        "Benchmarks", available_benchmarks, default=available_benchmarks
    )
    available_configs = sorted(
        display_history.get("configuration", pd.Series(dtype=str))
        .dropna()
        .astype(str)
        .unique()
    )
    chosen_configs = control_columns[2].multiselect(
        "Configurations", available_configs, default=available_configs
    )
    available_statuses = sorted(
        display_history.get("validation_status", pd.Series(dtype=str))
        .dropna()
        .astype(str)
        .unique()
    )
    chosen_statuses = control_columns[3].multiselect(
        "Validation status", available_statuses, default=available_statuses
    )
    history = filter_feedback_history(
        display_history,
        query=search,
        benchmarks=chosen_benchmarks,
        configurations=chosen_configs,
        validation_statuses=chosen_statuses,
    )
    summary[3].metric(
        "Demo records currently displayed",
        int(history["record_kind"].eq("Demo").sum())
        if "record_kind" in history
        else 0,
    )

    if real_history.empty:
        st.info(
            "No real feedback observations are recorded yet. Generate one with "
            f"`{FEEDBACK_COLLECTION_COMMAND}`."
        )
    elif history.empty:
        st.info("No feedback records match the current search and filters.")

    if not history.empty:
        visible = pd.DataFrame(index=history.index)
        visible["Record"] = history["record_label"]
        visible["Benchmark"] = history.get("program_id")
        visible["Compiler configuration"] = history.get("configuration")
        visible["Candidate runtime (s)"] = history.get("runtime_seconds")
        visible["O3 runtime (s)"] = history.get("baseline_o3_seconds")
        visible["Speedup vs O3 (measured / hypothetical)"] = history.get(
            "speedup_vs_o3"
        )
        visible["Predicted speedup (model estimate)"] = history.get(
            "predicted_speedup"
        )
        visible["Correctness"] = (
            history["correctness"].map(correctness_status)
            if "correctness" in history
            else "Unknown"
        )
        visible["Validation status"] = history["validation_status"]
        visible["Validation / demo note"] = history["validation_reason"]
        visible["Measurement date"] = history.get("timestamp")
        st.dataframe(visible, width="stretch", hide_index=True)
        with st.expander("Feedback provenance and validation details"):
            detail_columns = [
                column
                for column in (
                    "record_label",
                    "measurement_context_id",
                    "llvm_version",
                    "compiler_flags",
                    "baseline_compiler_flags",
                    "platform",
                    "input_profile",
                    "measurement_repeats",
                    "baseline_mad_seconds",
                    "runtime_mad_seconds",
                    "validation_reason",
                )
                if column in history
            ]
            st.dataframe(history[detail_columns], width="stretch", hide_index=True)
    else:
        st.info(
            "Try clearing the search or selecting additional benchmarks, configurations, "
            "or validation statuses."
        )

    st.markdown("#### Candidate runtime vs O3 baseline")
    chart_rows = history[
        history["record_kind"].eq("Real")
        & history["validation_status"].eq("Valid")
    ].copy() if not history.empty else pd.DataFrame()
    if chart_rows.empty:
        st.info(
            "No valid real feedback runtimes match these filters. Demo and quarantined "
            "records are intentionally excluded from this measured-runtime comparison."
        )
    else:
        chart_rows["comparison_label"] = (
            chart_rows["program_id"].astype(str)
            + " · "
            + chart_rows["configuration"].astype(str)
            + " · "
            + chart_rows["timestamp"].astype(str)
        )
        runtime_chart = chart_rows.melt(
            id_vars=["comparison_label", "program_id", "configuration", "timestamp"],
            value_vars=["baseline_o3_seconds", "runtime_seconds"],
            var_name="runtime_kind",
            value_name="plotted_runtime_seconds",
        )
        runtime_chart["runtime_kind"] = runtime_chart["runtime_kind"].map(
            {
                "baseline_o3_seconds": "O3 baseline",
                "runtime_seconds": "Candidate",
            }
        )
        runtime_plot = alt.Chart(runtime_chart).mark_bar().encode(
            x=alt.X(
                "plotted_runtime_seconds:Q",
                title="Runtime (seconds; actual feedback only)",
                scale=alt.Scale(zero=True),
            ),
            y=alt.Y("comparison_label:N", title="Feedback observation", sort=None),
            color=alt.Color("runtime_kind:N", title="Runtime"),
            yOffset="runtime_kind:N",
            tooltip=[
                alt.Tooltip("program_id:N", title="Benchmark"),
                alt.Tooltip("configuration:N", title="Candidate configuration"),
                alt.Tooltip("runtime_kind:N", title="Runtime"),
                alt.Tooltip(
                    "plotted_runtime_seconds:Q",
                    title="Runtime (s)",
                    format=".6f",
                ),
                alt.Tooltip("timestamp:N", title="Measurement date"),
            ],
        )
        st.altair_chart(
            runtime_plot.properties(
                height=max(150, 42 * len(chart_rows)),
                background="#182438" if dark_theme else "#ffffff",
            ).configure_axis(
                labelColor="#e5e7eb" if dark_theme else "#263445",
                titleColor="#e5e7eb" if dark_theme else "#263445",
                gridColor="#64748b55",
            ).configure_view(strokeOpacity=0),
            width="stretch",
        )
        st.caption(
            "This chart uses valid real feedback records only. The candidate and O3 runtimes "
            "are measured observations; predicted speedup is not plotted."
        )

    if not real_history.empty:
        feedback_fingerprints = set(measurement_fingerprint(feedback)) if not feedback.empty else set()
        experiment_fingerprints = (
            set(measurement_fingerprint(experiments))
            if not experiments.empty
            else set()
        )
        incorporated_count = len(feedback_fingerprints & experiment_fingerprints)
        st.write(
            f"**Matching experiment records:** {incorporated_count} · "
            "incorporation is separate from recording feedback."
        )
    if MODEL_FILE.exists():
        try:
            from src.model import load as load_model, training_data_signature

            bundle = load_model()
        except (ImportError, RuntimeError) as exc:
            st.error(f"Cannot inspect model training status: {exc}")
        else:
            signature = bundle.get("training_data_signature")
            current_signature = (
                training_data_signature(experiments) if not experiments.empty else None
            )
            st.write(f"**Model version:** {bundle.get('model_version', 'legacy/unversioned')}")
            if signature is None:
                st.info("This model predates training-data signatures; feedback training status is unknown.")
            elif signature == current_signature:
                st.success("The model was trained on the current valid experiment dataset.")
            else:
                st.info("Experiment data has changed since this model was trained; retrain to incorporate it.")
    else:
        st.info("No trained model is available. Recorded feedback has not affected model predictions.")
