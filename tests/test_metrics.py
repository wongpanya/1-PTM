import unittest

import pandas as pd

from src.analytics.metrics import (
    apply_filters,
    data_quality_summary,
    grouped_counts,
    income_summary,
    overview_metrics,
    rate_by_group,
    remove_small_groups,
    remove_forbidden_display_columns,
    safe_rate,
    top_counts,
)


class MetricsTest(unittest.TestCase):
    def test_safe_rate(self):
        self.assertEqual(safe_rate(1, 4), 25.0)
        self.assertEqual(safe_rate(1, 0), 0.0)

    def test_overview_metrics(self):
        df = pd.DataFrame({
            "odos_uid": ["a", "b"],
            "target_graduation_success": [1, 0],
            "target_scholarship_risk": [0, 1],
            "target_tracking_risk": [0, 1],
            "target_employment_ready": [1, 0],
            "income_monthly_est": [10000, None],
            "gpa_numeric": [3.0, None],
            "current_country": ["ไทย", "ญี่ปุ่น"],
            "current_field_group": ["วิศวกรรม", "แพทย์"],
        })
        metrics = overview_metrics(df)
        self.assertEqual(metrics["total_recipients"], 2)
        self.assertEqual(metrics["completion_rate"], 50.0)
        self.assertEqual(metrics["employment_rate"], 50.0)
        self.assertEqual(metrics["income_availability_rate"], 50.0)
        self.assertEqual(metrics["countries_count"], 2)

    def test_top_counts(self):
        df = pd.DataFrame({"region": ["A", "A", None]})
        result = top_counts(df, "region")
        self.assertEqual(list(result.columns), ["region", "count"])
        self.assertEqual(result.iloc[0]["count"], 2)

    def test_filters_and_grouped_rates(self):
        df = pd.DataFrame({
            "cohort": [1, 1, 2],
            "province": ["A", "B", "A"],
            "current_country": ["TH", "JP", "TH"],
            "current_field_group": ["ENG", "MED", "ENG"],
            "target_graduation_success": [1, 0, 1],
        })
        filtered = apply_filters(df, cohorts=[1], provinces=["A"])
        self.assertEqual(len(filtered), 1)
        grouped = rate_by_group(df, "cohort", "target_graduation_success")
        self.assertEqual(float(grouped.loc[grouped["cohort"] == 1, "rate"].iloc[0]), 50.0)

    def test_income_and_grouped_counts(self):
        df = pd.DataFrame({
            "current_country": ["TH", "TH", "JP"],
            "current_field_group": ["ENG", "MED", "ENG"],
            "income_monthly_est": [10000, 30000, None],
        })
        summary = income_summary(df)
        self.assertEqual(summary["records_with_income"], 2)
        self.assertEqual(summary["median_income"], 20000)
        grouped = grouped_counts(df, ["current_country", "current_field_group"])
        self.assertIn("count", grouped.columns)

    def test_data_quality_summary_marks_readiness_and_issues(self):
        df = pd.DataFrame({
            "odos_uid": ["a", "b"],
            "cohort": [1, 2],
            "income_monthly_est": [10000, None],
            "target_graduation_success": [1, 0],
        })
        issues = pd.DataFrame({"field": ["income_monthly_est", "income_monthly_est"]})
        definitions = {
            "data_quality": {
                "dashboard_ready_fields": ["odos_uid", "cohort"],
                "model_ready_fields": ["income_monthly_est", "target_graduation_success"],
                "fields_to_collect": ["verified_income_band"],
            }
        }
        quality = data_quality_summary(df, issues, definitions)
        income_row = quality.loc[quality["field"] == "income_monthly_est"].iloc[0]
        self.assertEqual(int(income_row["missing_count"]), 1)
        self.assertEqual(int(income_row["format_or_standard_issues"]), 2)
        self.assertTrue(bool(income_row["model_ready"]))

    def test_remove_forbidden_display_columns(self):
        df = pd.DataFrame({"odos_uid": ["a"], "phone_number": ["x"], "contract_id": ["y"]})
        safe = remove_forbidden_display_columns(df)
        self.assertEqual(list(safe.columns), ["odos_uid"])

    def test_remove_small_groups(self):
        df = pd.DataFrame({"province": ["A", "B"], "count": [4, 5]})
        safe = remove_small_groups(df, min_size=5)
        self.assertEqual(safe.to_dict("records"), [{"province": "B", "count": 5}])


if __name__ == "__main__":
    unittest.main()
