import unittest

import pandas as pd

from src.analytics.visualization import (
    aggregate_histogram,
    aggregate_proportions,
    completeness_matrix,
    funnel_summary,
    pathway_flows,
    question_options,
    readiness_for_fields,
    recommendation_for,
    visualization_config,
)


class VisualizationTest(unittest.TestCase):
    def test_config_has_four_modes_and_guided_questions(self):
        config = visualization_config()
        self.assertEqual(len(config["modes"]), 4)
        self.assertGreaterEqual(len(question_options(config)), 9)
        self.assertIn("Guided Visualization", config["modes"])

    def test_proportion_recommendation_rejects_donut_for_many_categories(self):
        recommendation = recommendation_for("proportion", category_count=8)
        self.assertEqual(recommendation["recommended_chart"], "100% Stacked Bar")
        self.assertIn("ไม่แนะนำ Donut/Pie", recommendation["compatibility_warning"])

    def test_readiness_for_fields_includes_missing_required_fields(self):
        quality = pd.DataFrame({"field": ["cohort"], "quality_score": [90.0]})
        readiness = readiness_for_fields(quality, ["cohort", "employment_type"])
        self.assertEqual(readiness["available"], 1)
        self.assertEqual(readiness["score"], 45.0)
        self.assertEqual(readiness["status"], "ต้องปรับปรุง")

    def test_aggregate_proportions_keep_full_denominator_after_suppression(self):
        df = pd.DataFrame({
            "cohort": [1] * 10,
            "status": ["A"] * 8 + ["B"] * 2,
        })
        result = aggregate_proportions(df, "status", "cohort", min_size=5)
        self.assertEqual(result["status"].tolist(), ["A"])
        self.assertEqual(float(result.iloc[0]["percent"]), 80.0)

    def test_aggregate_proportions_handles_same_category_and_group(self):
        df = pd.DataFrame({"country": ["TH"] * 8 + ["JP"] * 5})
        result = aggregate_proportions(df, "country", "country", min_size=5)
        self.assertEqual(list(result.columns), ["country", "count", "denominator", "percent"])
        self.assertEqual(int(result["count"].sum()), 13)
        self.assertAlmostEqual(float(result["percent"].sum()), 100.0, places=2)

    def test_aggregate_histogram_returns_only_bins_and_counts(self):
        df = pd.DataFrame({"income": list(range(10, 110, 10))})
        result = aggregate_histogram(df, "income", bins=2, min_size=1)
        self.assertEqual(list(result.columns), ["bin", "count"])
        self.assertEqual(int(result["count"].sum()), 10)

    def test_pathway_flows_suppress_small_paths(self):
        df = pd.DataFrame({
            "study": ["complete"] * 5 + ["active"] * 2,
            "work": ["private"] * 5 + ["tracking"] * 2,
        })
        result = pathway_flows(df, "study", "work", min_size=5)
        self.assertEqual(result.to_dict("records"), [{"source": "complete", "target": "private", "count": 5}])

    def test_completeness_matrix_suppresses_small_groups(self):
        df = pd.DataFrame({
            "cohort": [1, 1, 1, 2],
            "income": [1, None, 2, 3],
        })
        result = completeness_matrix(df, "cohort", ["income"], min_size=2)
        self.assertEqual(result["cohort"].tolist(), [1])
        self.assertAlmostEqual(float(result.iloc[0]["income"]), 66.67, places=2)

    def test_funnel_is_monotonic_and_uses_nested_subsets(self):
        df = pd.DataFrame({
            "target_graduation_success": [1, 1, 0, 1],
            "target_tracking_risk": [0, 1, 0, 0],
            "target_employment_ready": [1, 1, 1, 0],
            "employment_type": ["private", "tracking", "private", "unemployed"],
            "income_monthly_est": [20000, 30000, 40000, None],
        })
        funnel = funnel_summary(df)
        self.assertEqual(funnel["count"].tolist(), [4, 3, 2, 1, 1])
        self.assertTrue(funnel["count"].is_monotonic_decreasing)


if __name__ == "__main__":
    unittest.main()
