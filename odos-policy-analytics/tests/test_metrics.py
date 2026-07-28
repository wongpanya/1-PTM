import unittest

import pandas as pd

from src.analytics.metrics import (
    apply_filters,
    data_quality_summary,
    followup_coverage_by_group,
    group_readiness_summary,
    grouped_counts,
    income_box_summary,
    income_summary,
    overview_metrics,
    rate_by_group,
    readiness_scorecard,
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

    def test_income_box_summary_is_aggregate_and_suppresses_small_groups(self):
        df = pd.DataFrame({
            "field": ["A", "A", "A", "B", "B"],
            "income_monthly_est": [10000, 20000, 30000, 40000, 50000],
        })
        summary = income_box_summary(df, "field", min_size=3)
        self.assertEqual(list(summary["field"]), ["A"])
        self.assertEqual(int(summary.iloc[0]["count"]), 3)
        self.assertEqual(float(summary.iloc[0]["median"]), 20000.0)

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
        self.assertFalse(bool(income_row["model_ready"]))
        self.assertEqual(income_row["readiness_status"], "ต้องเก็บ/ปรับปรุงข้อมูล")

    def test_readiness_distinguishes_features_targets_and_leakage(self):
        df = pd.DataFrame({
            "cohort": [1, 2],
            "project_condition_status": ["completed", "active"],
            "target_graduation_success": [1, 0],
        })
        definitions = {
            "data_quality": {
                "dashboard_ready_fields": ["cohort", "target_graduation_success"],
                "analytics_ready_fields": ["cohort", "target_graduation_success"],
                "policy_ready_fields": ["cohort", "project_condition_status"],
                "ml_feature_fields": ["cohort"],
                "ml_target_fields": ["target_graduation_success"],
                "ml_leakage_fields": ["project_condition_status"],
            }
        }
        quality = data_quality_summary(df, pd.DataFrame(), definitions)
        target = quality.loc[quality["field"] == "target_graduation_success"].iloc[0]
        leakage = quality.loc[quality["field"] == "project_condition_status"].iloc[0]
        self.assertTrue(bool(target["ml_target"]))
        self.assertEqual(target["readiness_status"], "Target: ห้ามใช้เป็น feature")
        self.assertTrue(bool(leakage["ml_leakage_risk"]))
        self.assertEqual(leakage["readiness_status"], "ตัดออกจาก ML feature")
        scorecard = readiness_scorecard(quality, definitions)
        self.assertEqual(set(scorecard["use_case"]), {"Dashboard", "Analytics", "Policy", "ML"})

    def test_group_readiness_and_followup_suppress_small_groups(self):
        df = pd.DataFrame({
            "cohort": [1, 1, 1, 2, 2],
            "province": ["A", "A", "A", "B", "B"],
            "employment_type": ["private", None, "public", None, None],
            "work_start_date": ["2020-01-01", None, None, None, None],
            "income_monthly_est": [10000, None, 20000, None, None],
            "field_job_fit_level": [3, None, 2, None, None],
            "local_fit_level": [2, None, 3, None, None],
            "target_tracking_risk": [0, 1, 0, 1, 1],
            "target_graduation_success": [1, 1, 1, 0, 0],
        })
        definitions = {
            "data_quality": {
                "dashboard_ready_fields": ["cohort", "employment_type"],
                "policy_ready_fields": ["province", "employment_type"],
                "ml_feature_fields": ["cohort"],
                "ml_target_fields": ["target_graduation_success"],
            }
        }
        readiness = group_readiness_summary(df, "cohort", definitions, min_size=3)
        self.assertEqual(list(readiness["cohort"]), [1])
        coverage = followup_coverage_by_group(df, "cohort", min_size=3)
        self.assertEqual(list(coverage["cohort"]), [1])
        self.assertGreater(float(coverage.iloc[0]["followup_completeness"]), 0)

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
