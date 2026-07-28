import unittest

import pandas as pd

from src.risk.scoring import graduation_dataframe, graduation_status, score_dataframe, score_row


class RiskScoreTest(unittest.TestCase):
    def test_score_row_with_components(self):
        row = {
            "target_scholarship_risk": 1,
            "target_tracking_risk": 1,
            "target_field_mismatch": 0,
            "target_local_mismatch": 1,
            "project_condition_status": None,
            "current_status": "ไม่พบในฐานข้อมูล",
            "employment_type": None,
            "current_country": "ญี่ปุ่น",
            "restart_thailand_date": None,
        }
        result = score_row(row)
        self.assertEqual(result["risk_score"], 100)
        self.assertEqual(result["risk_level"], "High")
        self.assertEqual(result["rule_version"], "risk-rules-0.2-prototype")
        self.assertTrue(result["limitations_th"])
        triggered = [component for component in result["components"] if component["triggered"]]
        self.assertEqual(len(triggered), 7)

    def test_score_row_no_risk(self):
        row = {
            "target_scholarship_risk": 0,
            "target_tracking_risk": 0,
            "target_field_mismatch": 0,
            "target_local_mismatch": 0,
            "project_condition_status": "สำเร็จการศึกษา",
            "current_status": "มีข้อมูล",
            "employment_type": "ภาคเอกชน",
            "current_country": "ประเทศไทย",
            "restart_thailand_date": "2024-01-01",
        }
        self.assertEqual(score_row(row)["risk_score"], 0)

    def test_score_dataframe_keeps_explanatory_columns(self):
        df = pd.DataFrame({
            "odos_uid": ["ODOS00001"],
            "cohort": [1],
            "province": ["A"],
            "current_country": ["ประเทศไทย"],
            "current_field_group": ["Engineering"],
            "target_scholarship_risk": [0],
            "target_tracking_risk": [0],
            "target_field_mismatch": [0],
            "target_local_mismatch": [0],
            "project_condition_status": ["สำเร็จการศึกษา"],
            "current_status": ["มีข้อมูล"],
            "employment_type": ["ภาคเอกชน"],
            "restart_thailand_date": ["2024-01-01"],
        })
        result = score_dataframe(df)
        self.assertIn("risk_score", result.columns)
        self.assertIn("rule_version", result.columns)

    def test_graduation_status_rules(self):
        on_time = graduation_status({
            "target_graduation_success": 1,
            "study_duration_years": 4.0,
            "project_condition_status": "สำเร็จการศึกษา",
            "target_scholarship_risk": 0,
        })
        exited = graduation_status({
            "target_graduation_success": 0,
            "study_duration_years": None,
            "project_condition_status": "ลาออก",
            "target_scholarship_risk": 1,
        })
        self.assertEqual(on_time["graduation_status"], "on_time")
        self.assertEqual(exited["graduation_status"], "exited")

    def test_graduation_dataframe(self):
        df = pd.DataFrame({
            "odos_uid": ["ODOS00001"],
            "cohort": [1],
            "province": ["A"],
            "current_field_group": ["Engineering"],
            "target_graduation_success": [1],
            "study_duration_years": [5.0],
            "project_condition_status": ["สำเร็จการศึกษา"],
            "target_scholarship_risk": [0],
        })
        result = graduation_dataframe(df)
        self.assertEqual(result.iloc[0]["graduation_status"], "delayed")


if __name__ == "__main__":
    unittest.main()
