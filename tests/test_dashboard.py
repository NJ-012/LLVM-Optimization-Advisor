import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.dashboard_data import (
    FEEDBACK_COLLECTION_COMMAND,
    calculate_measured_speedup,
    correctness_status,
    filter_feedback_history,
    filter_observations,
    measurement_source,
    prepare_demo_feedback,
    prepare_feedback_history,
    prepare_chart_data,
)
from src.data_validation import (
    FEEDBACK_COLUMNS,
    append_unseen_measurements,
    combine_chart_sources,
    measurement_fingerprint,
    validate_measurements,
)
from src.config import CONFIGS, EXPERIMENTS, FEEDBACK, FEATURES
from src.benchmarks import calculate_speedup, compile_one, compile_reference, outputs_match
from src.recommendation import choose_action, use_safe_fallback


class DashboardDataTests(unittest.TestCase):
    def setUp(self):
        self.experiments = pd.DataFrame(
            [
                {
                    "program_id": "array_sum",
                    "configuration": "O3",
                    "baseline_o3_seconds": 0.012398,
                    "runtime_seconds": 0.012398,
                    "speedup_vs_o3": 1.0,
                    "correctness": True,
                    "llvm_version": "clang 18.1.3",
                    "platform": "linux-test",
                    "measurement_repeats": 5,
                },
                {
                    "program_id": "array_sum",
                    "configuration": "O3_no_vectorize",
                    "baseline_o3_seconds": 0.012398,
                    "runtime_seconds": 0.009374,
                    "speedup_vs_o3": 0.012398 / 0.009374,
                    "correctness": "True",
                    "llvm_version": "clang 18.1.3",
                    "platform": "linux-test",
                    "measurement_repeats": 5,
                },
                {
                    "program_id": "array_sum",
                    "configuration": "O3_no_vectorize",
                    "baseline_o3_seconds": 0.009941,
                    "runtime_seconds": 0.009682,
                    "speedup_vs_o3": 0.009941 / 0.009682,
                    "correctness": True,
                    "llvm_version": "feedback-run",
                    "platform": "linux-test",
                    "measurement_repeats": 7,
                },
                {
                    "program_id": "array_sum",
                    "configuration": "O2",
                    "baseline_o3_seconds": 0.012398,
                    "runtime_seconds": 0.01,
                    "speedup_vs_o3": 0.012398 / 0.01,
                    "correctness": False,
                    "llvm_version": "clang 18.1.3",
                    "platform": "linux-test",
                    "measurement_repeats": 5,
                },
                {
                    "program_id": "dot_product",
                    "configuration": "O2",
                    "baseline_o3_seconds": 10.0,
                    "runtime_seconds": 1.0,
                    "speedup_vs_o3": 10.0,
                    "correctness": True,
                    "llvm_version": "clang 18.1.3",
                    "platform": "linux-test",
                    "measurement_repeats": 5,
                },
            ]
        )

    def test_speedup_is_baseline_divided_by_runtime_only_when_correct(self):
        self.assertEqual(calculate_measured_speedup(10, 5, True), 2.0)
        self.assertIsNone(calculate_measured_speedup(10, 5, False))
        self.assertIsNone(calculate_measured_speedup(0, 5, True))
        self.assertIsNone(calculate_measured_speedup(10, float("inf"), True))

    def test_benchmark_speedup_and_output_reference_guards(self):
        self.assertEqual(calculate_speedup(10, 5, True), 2.0)
        self.assertIsNone(calculate_speedup(10, 5, False))
        self.assertIsNone(calculate_speedup(float("nan"), 5, True))
        self.assertTrue(outputs_match("reference", "reference"))
        self.assertFalse(outputs_match("reference", "candidate"))

    def test_compiler_configuration_flags_and_o0_reference_command(self):
        with patch("src.benchmarks.clang_path", return_value="clang"), patch(
            "src.benchmarks.execute"
        ) as execute:
            compile_one("kernel.c", "O3_no_vectorize", "kernel.exe")
            execute.assert_called_once_with(
                ["clang", "kernel.c", "-std=c11", *CONFIGS["O3_no_vectorize"], "-lm", "-o", "kernel.exe"]
            )
            execute.reset_mock()
            compile_reference("kernel.c", "reference.exe")
            execute.assert_called_once_with(
                ["clang", "kernel.c", "-std=c11", "-O0", "-lm", "-o", "reference.exe"]
            )

    def test_correctness_and_sources_are_classified(self):
        self.assertEqual(correctness_status("1"), "Passed")
        self.assertEqual(correctness_status("False"), "Failed")
        self.assertEqual(correctness_status(None), "Unknown")
        self.assertEqual(measurement_source("feedback-run"), "feedback")
        self.assertEqual(measurement_source("clang 18.1.3"), "collection")

    def test_feedback_empty_state_has_exact_real_collection_command(self):
        history = prepare_feedback_history(pd.DataFrame(), pd.DataFrame())
        self.assertTrue(history.empty)
        self.assertEqual(
            FEEDBACK_COLLECTION_COMMAND,
            "python run.py feedback --benchmark matrix_multiply",
        )

    def test_feedback_history_marks_validation_and_preserves_input_csv(self):
        import tempfile
        from pathlib import Path

        real = pd.DataFrame(
            [
                {
                    "timestamp": "2026-10-12 08:00:00",
                    "program_id": "matrix_multiply",
                    "configuration": "O3",
                    "baseline_o3_seconds": 0.01,
                    "runtime_seconds": 0.01,
                    "speedup_vs_o3": 1.0,
                    "correctness": True,
                    "iteration": 1,
                    "predicted_speedup": 1.0,
                    **{feature: 1 for feature in FEATURES},
                }
            ]
        )
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "feedback.csv"
            real.to_csv(source, index=False)
            original = source.read_bytes()
            history = prepare_feedback_history(real, pd.DataFrame())
            self.assertEqual(source.read_bytes(), original)
        self.assertEqual(history["validation_status"].tolist(), ["Rejected"])
        self.assertIn("measurement_context_id is required", history.iloc[0]["validation_reason"])

    def test_demo_records_are_separately_marked_and_filterable(self):
        demo = pd.DataFrame(
            [
                {
                    "program_id": "dot_product",
                    "configuration": "O2",
                    "runtime_seconds": 0.008,
                }
            ]
        )
        marked = prepare_demo_feedback(demo)
        self.assertEqual(marked.iloc[0]["record_label"], "DEMO — NOT MEASURED")
        self.assertEqual(marked.iloc[0]["validation_status"], "DEMO — NOT MEASURED")
        filtered = filter_feedback_history(
            marked,
            query="not measured",
            benchmarks=["dot_product"],
            configurations=["O2"],
            validation_statuses=["DEMO — NOT MEASURED"],
        )
        self.assertEqual(len(filtered), 1)
        self.assertNotIn("record_kind", demo.columns)

    def test_shipped_demo_csv_is_schema_shaped_and_does_not_claim_correctness(self):
        demo_path = Path(__file__).resolve().parents[1] / "data" / "demo_feedback.csv"
        demo = pd.read_csv(demo_path)
        self.assertTrue(FEEDBACK_COLUMNS.issubset(demo.columns))
        self.assertEqual(len(demo), 3)
        self.assertTrue(demo["demo_label"].eq("DEMO — NOT MEASURED").all())
        self.assertTrue(demo["measurement_source"].eq("demo").all())
        self.assertTrue(demo["correctness"].eq("Not tested (demo)").all())
        self.assertTrue(demo["configuration"].isin(CONFIGS).all())

    def test_chart_keeps_sources_separate_and_does_not_pool_benchmarks(self):
        collection = prepare_chart_data(self.experiments, "array_sum", "collection")
        feedback = prepare_chart_data(self.experiments, "array_sum", "feedback")

        self.assertEqual(collection["configuration"].tolist(), ["O3", "O3_no_vectorize"])
        self.assertAlmostEqual(collection.iloc[1]["measured_speedup"], 0.012398 / 0.009374)
        self.assertEqual(collection.iloc[0]["configuration_label"], "O3 (baseline)")
        self.assertEqual(feedback["configuration"].tolist(), ["O3_no_vectorize"])
        self.assertAlmostEqual(feedback.iloc[0]["baseline_seconds"], 0.009941)
        self.assertAlmostEqual(feedback.iloc[0]["measured_speedup"], 0.009941 / 0.009682)
        self.assertTrue(collection["measurement_source"].eq("collection").all())
        self.assertTrue(feedback["measurement_source"].eq("feedback").all())

    def test_chart_configuration_filter_preserves_individual_values(self):
        chart_data = prepare_chart_data(
            self.experiments,
            "array_sum",
            "collection",
            configurations=["O3_no_vectorize"],
        )
        self.assertEqual(chart_data["configuration"].tolist(), ["O3_no_vectorize"])
        self.assertEqual(chart_data["measurement_repeats"].tolist(), [5])

    def test_chart_keeps_repeated_observations_instead_of_aggregating(self):
        repeated = pd.concat(
            [
                self.experiments,
                self.experiments.iloc[[1]].assign(
                    runtime_seconds=0.010,
                    speedup_vs_o3=0.012398 / 0.010,
                ),
            ],
            ignore_index=True,
        )
        chart_data = prepare_chart_data(repeated, "array_sum", "collection")
        rows = chart_data[chart_data["configuration"] == "O3_no_vectorize"]

        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows.iloc[0]["measured_speedup"], 0.012398 / 0.009374)
        self.assertAlmostEqual(rows.iloc[1]["measured_speedup"], 0.012398 / 0.010)
        self.assertEqual(rows["configuration_label"].tolist(), [
            "O3_no_vectorize · observation 1",
            "O3_no_vectorize · observation 2",
        ])

    def test_chart_rejects_stored_speedup_that_disagrees_with_times(self):
        inconsistent = self.experiments.copy()
        inconsistent.loc[1, "speedup_vs_o3"] = 1.0
        with self.assertRaisesRegex(ValueError, "does not match baseline/runtime"):
            prepare_chart_data(inconsistent, "array_sum", "collection")

    def test_filters_apply_to_benchmark_configuration_correctness_and_context(self):
        filtered = filter_observations(
            self.experiments,
            benchmark="array_sum",
            configurations=["O3_no_vectorize", "O2"],
            correctness="Passed",
            compiler="clang 18.1.3",
            platform="linux-test",
        )
        self.assertEqual(filtered["program_id"].unique().tolist(), ["array_sum"])
        self.assertEqual(filtered["configuration"].tolist(), ["O3_no_vectorize"])

    def test_shipped_data_schemas_and_baseline_contexts_validate(self):
        experiment_errors = validate_measurements(pd.read_csv(EXPERIMENTS), "experiments")
        self.assertEqual(experiment_errors, [])
        feedback = pd.read_csv(FEEDBACK)
        feedback_errors = validate_measurements(feedback, "feedback")
        if feedback_errors:
            self.assertTrue(
                any(
                    "measurement_context_id is required" in error
                    or "measurement_source is required" in error
                    or "O3 runtime must match its own baseline runtime" in error
                    for error in feedback_errors
                )
            )

    def test_o3_must_match_its_own_baseline_runtime(self):
        inconsistent = pd.read_csv(EXPERIMENTS)
        row = inconsistent.index[inconsistent.configuration.eq("O3")][0]
        inconsistent.loc[row, "runtime_seconds"] *= 1.1
        errors = validate_measurements(inconsistent, "experiments")
        self.assertTrue(any("O3 runtime must match" in error for error in errors))

    def test_data_validation_rejects_context_baseline_mismatch(self):
        inconsistent = pd.read_csv(EXPERIMENTS).iloc[:4].copy()
        inconsistent.loc[inconsistent.index[1], "baseline_o3_seconds"] = 0.5
        errors = validate_measurements(inconsistent, "experiments")
        self.assertTrue(any("baseline_o3_seconds varies" in error for error in errors))

    def test_measurement_fingerprints_support_idempotent_feedback_merges(self):
        fingerprints = measurement_fingerprint(self.experiments.iloc[[1, 1]])
        self.assertEqual(fingerprints.iloc[0], fingerprints.iloc[1])
        base = self.experiments.iloc[[1]].copy()
        merged = append_unseen_measurements(base, self.experiments.iloc[[1]])
        self.assertEqual(len(merged), 1)
        appended = append_unseen_measurements(base, self.experiments.iloc[[2]])
        self.assertEqual(len(appended), 2)

    def test_chart_sources_do_not_duplicate_incorporated_feedback(self):
        experiments = self.experiments.assign(
            measurement_source=self.experiments["llvm_version"].map(measurement_source)
        )
        feedback = experiments[experiments["measurement_source"].eq("feedback")].copy()
        combined = combine_chart_sources(experiments, feedback)
        self.assertEqual(
            combined["measurement_source"].tolist(),
            ["collection", "collection", "collection", "collection", "feedback"],
        )
        chart = prepare_chart_data(combined, "array_sum", "feedback")
        self.assertEqual(len(chart), 1)

    def test_recommendation_falls_back_when_grouped_cv_is_missing_or_weaker(self):
        predictions = {"O3": 1.0, "O2": 1.8}
        weak_validation = {
            "group_cv_log_speedup_mae": 0.05,
            "group_cv_median_baseline_log_speedup_mae": 0.04,
        }
        self.assertTrue(use_safe_fallback(weak_validation))
        self.assertEqual(choose_action(predictions, weak_validation), "O3")
        self.assertEqual(choose_action(predictions, {}), "O3")
        validated = {
            "group_cv_log_speedup_mae": 0.03,
            "group_cv_median_baseline_log_speedup_mae": 0.04,
        }
        self.assertFalse(use_safe_fallback(validated))
        self.assertEqual(choose_action(predictions, validated), "O2")


if __name__ == "__main__":
    unittest.main()
