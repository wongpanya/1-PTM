import unittest

import pandas as pd

from src.policy.recommendations import area_recommendations, field_recommendations, recommendation_summary


class PolicyRecommendationTest(unittest.TestCase):
    def sample_df(self):
        return pd.DataFrame({
            "odos_uid": [f"ODOS{i:05d}" for i in range(1, 7)],
            "current_field_group": ["A", "A", "A", "B", "B", "B"],
            "province": ["X", "X", "Y", "Y", "Y", "Z"],
            "target_graduation_success": [1, 1, 1, 1, 0, 0],
            "target_employment_ready": [1, 1, 1, 0, 0, 0],
            "field_job_fit_level": [3, 3, 2, 1, 1, 0],
            "income_monthly_est": [50000, 40000, 45000, 10000, 12000, 9000],
            "local_fit_level": [3, 2, 3, 1, 0, 1],
        })

    def test_field_recommendations_are_traceable(self):
        result = field_recommendations(self.sample_df(), min_records=1)
        self.assertFalse(result.empty)
        self.assertIn("policy_score", result.columns)
        self.assertIn("analysis_result", result.columns)
        self.assertIn("policy_recommendation", result.columns)
        self.assertIn("weights", result.columns)
        self.assertGreater(result.iloc[0]["policy_score"], result.iloc[-1]["policy_score"])

    def test_weight_change_recalculates_field_score(self):
        df = self.sample_df()
        default = field_recommendations(df, min_records=1)
        changed = field_recommendations(
            df,
            min_records=1,
            weights={
                "completion_rate": 0,
                "employment_rate": 0,
                "field_job_fit": 0,
                "income_outcome": 100,
                "local_development_fit": 0,
                "data_completeness": 0,
            },
        )
        default_b = default.loc[default["current_field_group"] == "B", "policy_score"].iloc[0]
        changed_b = changed.loc[changed["current_field_group"] == "B", "policy_score"].iloc[0]
        self.assertNotEqual(float(default_b), float(changed_b))

    def test_area_recommendations_include_external_placeholders(self):
        result = area_recommendations(self.sample_df(), min_records=1)
        self.assertFalse(result.empty)
        self.assertIn("external_inequality_need", result.columns)
        self.assertIn("workforce_demand", result.columns)
        self.assertIn("limitations_th", result.columns)

    def test_recommendation_summary(self):
        summary = recommendation_summary(self.sample_df())
        self.assertEqual(summary["records"], 6)
        self.assertEqual(summary["completion_rate"], 66.67)


if __name__ == "__main__":
    unittest.main()
