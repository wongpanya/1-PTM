import unittest

import pandas as pd

from src.analytics.exporting import build_dashboard_export
from src.governance.privacy import aggregate_csv_bytes


class DashboardExportTest(unittest.TestCase):
    def test_filtered_export_is_aggregate_and_contains_new_kpis(self):
        rows = 5
        df = pd.DataFrame({
            "odos_uid": [f"id-{index}" for index in range(rows)],
            "analysis_year": [2010] * rows,
            "cohort": [1] * rows,
            "province": ["A"] * rows,
            "current_field_group": ["ICT"] * rows,
            "standardized_university_name": ["University A"] * rows,
            "employer_sector_code": ["PRIVATE"] * rows,
            "target_graduation_success": [1, 1, 1, 0, 0],
            "target_dropout": [0, 0, 0, 1, 0],
            "target_termination": [0, 0, 0, 0, 1],
            "target_scholarship_risk": [0, 0, 0, 1, 1],
            "target_tracking_risk": [0, 0, 0, 0, 0],
            "target_employment_ready": [1, 1, 1, 0, 0],
            "income_monthly_est": [10000, 20000, 30000, None, None],
            "field_job_fit_level": [2, 3, 1, None, None],
            "local_fit_level": [2, 2, 1, None, None],
        })

        report = build_dashboard_export(df, "Overview")
        metrics = set(report["metric"])
        self.assertIn("dropout_rate", metrics)
        self.assertIn("termination_rate", metrics)
        self.assertIn("scholarship_risk_rate", metrics)
        self.assertIn("average_income", metrics)
        self.assertIn("field_job_fit_rate", metrics)
        self.assertIn("denominator", report.columns)
        self.assertNotIn("odos_uid", report.columns)

        exported = aggregate_csv_bytes(report, "overview.csv", "Analyst", log_export=False)
        self.assertIn(b"field_job_fit_rate", exported)

    def test_export_handles_nullable_numeric_group_labels(self):
        rows = 7
        df = pd.DataFrame({
            "odos_uid": [f"id-{index}" for index in range(rows)],
            "analysis_year": pd.Series([2024, 2024, 2024, 2024, 2024, None, None], dtype="Int64"),
            "cohort": pd.Series([1, 1, 1, 1, 1, None, None], dtype="Int64"),
            "province": ["A"] * rows,
            "target_graduation_success": [1, 1, 1, 1, 1, 0, 0],
            "target_dropout": [0, 0, 0, 0, 0, 1, 0],
            "target_termination": [0, 0, 0, 0, 0, 0, 1],
            "target_scholarship_risk": [0, 0, 0, 0, 0, 1, 1],
            "target_tracking_risk": [0, 0, 0, 0, 0, 0, 0],
            "target_employment_ready": [1, 1, 1, 1, 1, 0, 0],
        })

        report = build_dashboard_export(df, "Overview")

        self.assertIn("analysis_year", set(report["dimension"]))
        self.assertIn("cohort", set(report["dimension"]))
        self.assertIn("recipient_count", set(report["metric"]))


if __name__ == "__main__":
    unittest.main()
