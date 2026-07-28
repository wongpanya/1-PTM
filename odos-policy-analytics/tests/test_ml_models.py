import importlib.util
import unittest

import pandas as pd

from src.risk.ml_models import (
    BASE_MODEL_KEYS,
    DEFAULT_TARGET,
    MODEL_SPECS,
    TARGET_SPECS,
    available_model_features,
    available_target_columns,
    feature_readiness,
    forecast_objective_frame,
    forecast_objectives,
    modelable_forecast_objectives,
    policy_interpretation,
    prediction_overview,
    segment_prediction_summary,
    target_summary,
    target_objective_links,
    train_model_suite,
)


def sample_modeling_frame():
    return pd.DataFrame(
        {
            "cohort": [1, 1, 2, 2, 3, 3, 4, 4],
            "sex": ["F", "M", "F", "M", "F", "M", "F", "M"],
            "region": ["North", "North", "South", "South", "East", "East", "West", "West"],
            "province": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "current_country": ["Thailand", "Japan", "Thailand", "Japan", "Thailand", "Japan", "Thailand", "Japan"],
            "current_field_group": ["Engineering", "Arts", "Engineering", "Arts", "Science", "Health", "Science", "Health"],
            "gpa_numeric": [3.1, 2.2, 3.3, 2.1, 3.4, 2.0, 3.5, 1.9],
            "study_duration_years": [4.0, 6.0, 4.1, 6.2, 4.2, 6.3, 4.0, 6.4],
            "project_condition_status": ["leak"] * 8,
            DEFAULT_TARGET: [0, 1, 0, 1, 0, 1, 0, 1],
            "target_graduation_success": [1, 0, 1, 0, 1, 0, 1, 0],
            "target_tracking_risk": [0, 1, 0, 1, 0, 1, 0, 1],
            "target_employment_ready": [1, 0, 1, 0, 1, 0, 1, 0],
            "target_field_mismatch": [0, 1, 0, 1, 0, 1, 0, 1],
            "target_local_mismatch": [0, 1, 0, 1, 0, 1, 0, 1],
            "split": ["development", "development", "development", "development", "validation", "validation", "validation", "validation"],
        }
    )


class MLModelsTest(unittest.TestCase):
    def test_feature_readiness_selects_configured_non_leakage_features(self):
        df = sample_modeling_frame()
        features = available_model_features(df)
        self.assertIn("cohort", features)
        self.assertIn("gpa_numeric", features)
        self.assertNotIn("project_condition_status", features)
        self.assertNotIn(DEFAULT_TARGET, features)

        report = feature_readiness(df)
        selected = report[report["status"] == "selected"]["feature"].tolist()
        self.assertIn("study_duration_years", selected)

    def test_target_summary_requires_two_classes(self):
        summary = target_summary(sample_modeling_frame())
        self.assertTrue(summary["ready"])
        self.assertEqual(summary["positive_count"], 4)
        self.assertEqual(summary["negative_count"], 4)

    def test_forecast_objectives_map_research_framework_to_targets(self):
        objectives = forecast_objectives()
        self.assertEqual(objectives["scholarship_risk"]["target"], DEFAULT_TARGET)
        self.assertEqual(objectives["graduation_success"]["target"], "target_graduation_success")
        self.assertEqual(objectives["workforce_demand"]["status"], "data_gap")
        self.assertIn("scholarship_risk", modelable_forecast_objectives())
        self.assertIn("future_scholarship_fields", modelable_forecast_objectives())
        self.assertNotIn("national_impact", modelable_forecast_objectives())
        self.assertEqual(objectives["brain_drain_risk"]["status"], "data_gap")

        frame = forecast_objective_frame()
        self.assertIn("caveat_or_data_gap", frame.columns)
        self.assertGreaterEqual(len(frame), 9)

    def test_advanced_target_selection_links_targets_to_objectives(self):
        targets = available_target_columns(sample_modeling_frame())
        self.assertEqual(set(targets), set(TARGET_SPECS))

        direct_links = target_objective_links("target_graduation_success")
        self.assertEqual(direct_links[0]["objective_key"], "graduation_success")
        self.assertEqual(direct_links[0]["relation"], "direct")

        supporting_links = target_objective_links("target_tracking_risk")
        self.assertIn("scholarship_risk", {item["objective_key"] for item in supporting_links})
        self.assertIn("brain_drain_risk", {item["objective_key"] for item in supporting_links})

    @unittest.skipIf(importlib.util.find_spec("sklearn") is None, "scikit-learn is not installed")
    def test_train_model_suite_returns_five_base_models_and_vote_ensemble(self):
        results = train_model_suite(sample_modeling_frame())
        self.assertEqual(len(results), 6)
        self.assertEqual(set(BASE_MODEL_KEYS), {"logistic_regression", "decision_tree", "random_forest", "naive_bayes", "calibrated_svm"})
        self.assertEqual(set(result.key for result in results), set(MODEL_SPECS))
        self.assertIn("vote_ensemble", {result.key for result in results})
        for result in results:
            self.assertIn("f1", result.metrics)
            self.assertFalse(result.confusion_matrix.empty)
            self.assertFalse(result.feature_importance.empty)
            self.assertFalse(result.validation_predictions.empty)
            self.assertIn("positive_probability", result.validation_predictions.columns)
            self.assertNotIn("odos_uid", result.validation_predictions.columns)

    @unittest.skipIf(importlib.util.find_spec("sklearn") is None, "scikit-learn is not installed")
    def test_train_model_suite_respects_user_selected_models(self):
        selected = ["logistic_regression", "naive_bayes", "vote_ensemble"]
        results = train_model_suite(sample_modeling_frame(), selected_models=selected)
        self.assertEqual([result.key for result in results], selected)

    @unittest.skipIf(importlib.util.find_spec("sklearn") is None, "scikit-learn is not installed")
    def test_prediction_interpretation_supports_aggregate_policy_planning(self):
        result = train_model_suite(
            sample_modeling_frame(),
            selected_models=["logistic_regression"],
        )[0]

        overview = prediction_overview(result, DEFAULT_TARGET)
        self.assertEqual(overview["records"], 4)
        self.assertEqual(overview["direction"], "risk")

        segments = segment_prediction_summary(
            result,
            "cohort",
            minimum_group_size=1,
        )
        self.assertFalse(segments.empty)
        self.assertIn("forecast_positive_rate", segments.columns)

        guidance = policy_interpretation(result, DEFAULT_TARGET)
        self.assertTrue(guidance["policy_actions"])
        self.assertTrue(guidance["monitoring_kpis"])
        self.assertIn("reliability_note", guidance)


if __name__ == "__main__":
    unittest.main()
