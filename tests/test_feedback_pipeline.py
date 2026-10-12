import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.dummy import DummyRegressor

from src import model, pipeline
from src import benchmarks
from src.benchmarks import aggregate_timings, calculate_speedup
from src.config import CONFIGS, FEATURES
from src.data_validation import feedback_quarantine_rows, validate_measurements


def feedback_row(configuration="O3", baseline=0.01, runtime=None, context="run-1"):
    runtime = baseline if runtime is None and configuration == "O3" else runtime
    runtime = 0.008 if runtime is None else runtime
    row = {
        "timestamp": "2026-10-12 08:00:00",
        "program_id": "array_sum",
        "configuration": configuration,
        "baseline_o3_seconds": baseline,
        "runtime_seconds": runtime,
        "speedup_vs_o3": baseline / runtime,
        "correctness": True,
        "iteration": 1,
        "predicted_speedup": 1.0,
        "measurement_context_id": context,
        "llvm_version": "clang version test",
        "compiler_flags": " ".join(CONFIGS[configuration]),
        "baseline_compiler_flags": " ".join(CONFIGS["O3"]),
        "platform": "test-platform",
        "input_profile": "fixed source-defined input",
        "measurement_repeats": 7,
        "baseline_mad_seconds": 0.0001,
        "runtime_mad_seconds": 0.0001,
        "measurement_source": "feedback",
    }
    row.update({feature: 1 for feature in FEATURES})
    return row


class FeedbackValidationTests(unittest.TestCase):
    def test_valid_o3_record_uses_the_same_runtime_as_its_baseline(self):
        frame = pd.DataFrame([feedback_row()])
        self.assertEqual(validate_measurements(frame, "feedback"), [])

    def test_valid_non_o3_candidate_uses_paired_o3_baseline(self):
        row = feedback_row(
            "O3_no_vectorize",
            baseline=0.01,
            runtime=0.008,
        )
        self.assertEqual(validate_measurements(pd.DataFrame([row]), "feedback"), [])

    def test_mismatched_o3_baseline_is_rejected(self):
        row = feedback_row("O3", baseline=0.01, runtime=0.0102)
        row["speedup_vs_o3"] = row["baseline_o3_seconds"] / row["runtime_seconds"]
        errors = validate_measurements(pd.DataFrame([row]), "feedback")
        self.assertTrue(any("O3 runtime must match its own baseline runtime" in error for error in errors))

    def test_candidate_speedup_must_match_its_paired_runtimes(self):
        row = feedback_row("O3_no_unroll", baseline=0.01, runtime=0.008)
        row["speedup_vs_o3"] = 1.0
        errors = validate_measurements(pd.DataFrame([row]), "feedback")
        self.assertTrue(any("does not match baseline_o3_seconds/runtime_seconds" in error for error in errors))

    def test_malformed_feedback_and_missing_context_are_rejected(self):
        row = feedback_row()
        row["runtime_seconds"] = float("nan")
        row["measurement_context_id"] = ""
        row["measurement_repeats"] = 1
        errors = validate_measurements(pd.DataFrame([row]), "feedback")
        self.assertTrue(any("runtime_seconds must be a finite positive number" in error for error in errors))
        self.assertTrue(any("measurement_context_id is required" in error for error in errors))
        self.assertTrue(any("measurement_repeats must be an integer" in error for error in errors))

    def test_quarantine_identifies_legacy_records_and_preserves_row_identity(self):
        valid = feedback_row("O3_no_vectorize", baseline=0.01, runtime=0.008)
        legacy = feedback_row("O3", baseline=0.01, runtime=0.009)
        legacy["speedup_vs_o3"] = 0.01 / 0.009
        legacy.pop("measurement_context_id")
        frame = pd.DataFrame([valid, legacy])
        indices, reasons = feedback_quarantine_rows(frame)
        self.assertEqual(indices, {1})
        self.assertIn("O3 runtime must match", reasons[1])

    def test_quarantine_writes_exact_backup_and_separate_invalid_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            feedback_path = folder / "feedback.csv"
            quarantine_path = folder / "feedback.quarantine.csv"
            legacy = feedback_row("O3", baseline=0.01, runtime=0.009)
            legacy["speedup_vs_o3"] = 0.01 / 0.009
            legacy.pop("measurement_context_id")
            pd.DataFrame([legacy]).to_csv(feedback_path, index=False)
            original = feedback_path.read_bytes()
            with patch.object(pipeline, "FEEDBACK", feedback_path), patch.object(
                pipeline, "FEEDBACK_QUARANTINE", quarantine_path
            ):
                self.assertTrue(pipeline.quarantine_feedback())
            self.assertEqual(
                feedback_path.with_name("feedback.pre_quarantine.csv").read_bytes(),
                original,
            )
            self.assertEqual(len(pd.read_csv(feedback_path)), 0)
            quarantined = pd.read_csv(quarantine_path)
            self.assertEqual(len(quarantined), 1)
            self.assertIn("O3 runtime must match", quarantined.iloc[0]["quarantine_reason"])


class MeasurementTests(unittest.TestCase):
    def test_speedup_requires_correctness_and_finite_positive_runtimes(self):
        self.assertEqual(calculate_speedup(0.02, 0.01, True), 2.0)
        for baseline, candidate in (
            (0, 1),
            (1, -1),
            (float("nan"), 1),
            (1, float("inf")),
        ):
            self.assertIsNone(calculate_speedup(baseline, candidate, True))
        self.assertIsNone(calculate_speedup(1, 0.5, False))

    def test_aggregation_reports_median_and_median_absolute_deviation(self):
        median, mad = aggregate_timings([1, 2, 3, 100, 2])
        self.assertEqual(median, 2)
        self.assertEqual(mad, 1)

    def test_aggregation_rejects_invalid_or_insufficient_samples(self):
        for timings in ([1], [1, 0], [1, float("nan")]):
            with self.assertRaises(ValueError):
                aggregate_timings(timings)

    def test_collection_does_not_start_timing_before_correctness_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            sources = folder / "benchmarks"
            results = folder / "results"
            sources.mkdir()
            results.mkdir()
            for name in ("one", "two", "three"):
                (sources / f"{name}.c").write_text("int main(void) { return 0; }\n")
            experiments = folder / "experiments.csv"
            experiments.write_text("original data\n")
            with (
                patch.object(benchmarks, "BENCH", sources),
                patch.object(benchmarks, "RESULTS", results),
                patch.object(benchmarks, "EXPERIMENTS", experiments),
                patch.object(benchmarks, "clang_path", return_value="clang"),
                patch.object(benchmarks, "execute", return_value="clang test"),
                patch.object(benchmarks, "extract", return_value={feature: 1 for feature in FEATURES}),
                patch.object(benchmarks, "compile_reference"),
                patch.object(benchmarks, "compile_one"),
                patch.object(
                    benchmarks,
                    "run_once",
                    side_effect=lambda binary: (
                        "incorrect"
                        if str(binary).endswith("_O2")
                        else "expected"
                    ),
                ),
                patch.object(benchmarks, "measure") as timing,
            ):
                with self.assertRaisesRegex(RuntimeError, "Correctness failed before timing"):
                    benchmarks.collect()
            timing.assert_not_called()
            self.assertEqual(experiments.read_text(), "original data\n")


class PipelineTests(unittest.TestCase):
    def test_incorporation_is_idempotent_per_measurement_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            feedback_path = folder / "feedback.csv"
            experiments_path = folder / "experiments.csv"
            demo_path = folder / "demo_feedback.csv"
            pd.DataFrame([feedback_row("O3_no_vectorize")]).to_csv(
                feedback_path, index=False
            )
            demo = feedback_row("O2", context="demo-only")
            demo["program_id"] = "dot_product"
            demo["measurement_source"] = "demo"
            pd.DataFrame([demo]).to_csv(demo_path, index=False)
            original_feedback = feedback_path.read_bytes()
            with patch.object(pipeline, "FEEDBACK", feedback_path), patch.object(
                pipeline, "EXPERIMENTS", experiments_path
            ):
                self.assertTrue(pipeline.incorporate_feedback())
                self.assertTrue(pipeline.incorporate_feedback())
            experiments = pd.read_csv(experiments_path)
            self.assertEqual(len(experiments), 1)
            self.assertEqual(experiments.iloc[0]["measurement_source"], "feedback")
            self.assertEqual(experiments.iloc[0]["program_id"], "array_sum")
            self.assertEqual(feedback_path.read_bytes(), original_feedback)
            self.assertTrue(demo_path.exists())

    def test_run_all_is_repeatable_and_never_generates_fresh_feedback(self):
        with (
            patch.object(pipeline, "doctor", return_value=True),
            patch.object(pipeline, "collect", return_value=True),
            patch.object(pipeline, "train", return_value=True),
            patch.object(pipeline, "evaluate", return_value=True),
            patch.object(pipeline, "recommend", return_value=True),
            patch.object(pipeline, "incorporate_feedback", return_value=True),
            patch.object(pipeline, "feedback") as feedback_command,
        ):
            self.assertTrue(pipeline.run_all())
            feedback_command.assert_not_called()

    def test_run_all_stops_and_reports_a_failed_stage(self):
        with (
            patch.object(pipeline, "doctor", return_value=True),
            patch.object(pipeline, "collect", return_value=False),
            patch.object(pipeline, "train") as train_stage,
            patch("builtins.print") as print_output,
        ):
            self.assertFalse(pipeline.run_all())
            train_stage.assert_not_called()
            self.assertTrue(
                any("[FAIL] Benchmark collection" in str(call) for call in print_output.call_args_list)
            )


class ModelEvaluationTests(unittest.TestCase):
    def setUp(self):
        records = []
        for program in ("p1", "p2", "p3", "p4", "p5"):
            for index, configuration in enumerate(CONFIGS):
                runtime = 1.0 / (1.0 + (index * 0.1) + len(program) * 0.01)
                row = {
                    "program_id": program,
                    "configuration": configuration,
                    "speedup_vs_o3": 1.0 / runtime,
                    "correctness": True,
                }
                row.update({feature: float(len(program)) for feature in FEATURES})
                records.append(row)
        self.frame = pd.DataFrame(records)

    def test_grouped_folds_keep_each_program_out_of_its_training_fold(self):
        splits = model._grouped_splits(self.frame)
        self.assertEqual(len(splits), 5)
        for train_indices, test_indices in splits:
            train_programs = set(self.frame.iloc[train_indices]["program_id"])
            test_programs = set(self.frame.iloc[test_indices]["program_id"])
            self.assertTrue(train_programs.isdisjoint(test_programs))

    def test_evaluation_reports_program_and_observation_counts_against_same_fold_baseline(self):
        with patch.object(model, "_new_model", return_value=DummyRegressor(strategy="median")):
            report = model.evaluate_frame(self.frame)
        self.assertEqual(report["programs"], 5)
        self.assertEqual(report["observations"], 20)
        self.assertEqual(report["folds"], 5)
        self.assertGreaterEqual(report["group_cv_median_baseline_log_speedup_mae"], 0)
        self.assertGreaterEqual(report["group_cv_log_speedup_mae"], 0)

    def test_training_uses_experiment_csv_not_neighboring_demo_feedback(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            experiments_path = folder / "experiments.csv"
            demo_path = folder / "demo_feedback.csv"
            model_path = folder / "reward_model.joblib"
            rows = []
            for program in ("p1", "p2", "p3"):
                row = {
                    "program_id": program,
                    "configuration": "O3",
                    "baseline_o3_seconds": 0.01,
                    "runtime_seconds": 0.01,
                    "speedup_vs_o3": 1.0,
                    "correctness": True,
                }
                row.update({feature: 1 for feature in FEATURES})
                rows.append(row)
            pd.DataFrame(rows).to_csv(experiments_path, index=False)
            pd.DataFrame([{"program_id": "demo-only"}]).to_csv(
                demo_path, index=False
            )
            with (
                patch.object(model, "EXPERIMENTS", experiments_path),
                patch.object(model, "MODEL", model_path),
                patch.object(
                    model,
                    "_new_model",
                    return_value=DummyRegressor(strategy="mean"),
                ),
            ):
                bundle = model.train()
            self.assertEqual(bundle["trained_rows"], 3)
            self.assertEqual(set(bundle["programs"]), {"p1", "p2", "p3"})
            self.assertTrue(demo_path.exists())


if __name__ == "__main__":
    unittest.main()
