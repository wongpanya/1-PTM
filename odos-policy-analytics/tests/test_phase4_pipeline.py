import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

from src.pipeline.phase4 import run_phase4_pipeline
from src.utils.config import PROJECT_ROOT


class Phase4PipelineTest(unittest.TestCase):
    def test_pipeline_outputs_are_created_and_reproducible(self):
        result1 = run_phase4_pipeline()
        cleaned_path = Path(result1["outputs"]["cleaned_dataset"])
        issues_path = Path(result1["outputs"]["validation_issues"])
        report_path = Path(result1["outputs"]["before_after_report_json"])
        field_report_path = Path(result1["outputs"]["field_cleaning_report"])
        log_path = Path(result1["outputs"]["processing_log"])

        self.assertTrue(cleaned_path.exists())
        self.assertTrue(issues_path.exists())
        self.assertTrue(report_path.exists())
        self.assertTrue(field_report_path.exists())
        self.assertTrue(log_path.exists())

        first_hash = _sha256(cleaned_path)
        result2 = run_phase4_pipeline()
        second_hash = _sha256(Path(result2["outputs"]["cleaned_dataset"]))
        self.assertEqual(first_hash, second_hash)
        self.assertEqual(result2["duplicate_source"], True)

        df = pd.read_csv(cleaned_path)
        self.assertEqual(len(df), 3091)
        self.assertNotIn("income_raw", df.columns)
        self.assertNotIn("contract_no", df.columns)
        self.assertIn("analysis_year", df.columns)
        self.assertIn("standardized_university_name", df.columns)
        self.assertIn("employer_sector_code", df.columns)
        self.assertIn("target_dropout", df.columns)
        self.assertIn("target_termination", df.columns)
        self.assertEqual(int(df["target_dropout"].sum()), 100)
        self.assertEqual(int(df["target_termination"].sum()), 50)
        self.assertGreater(int(df["analysis_year"].notna().sum()), 3000)
        self.assertGreater(int(df["standardized_university_name"].notna().sum()), 2900)
        self.assertEqual(
            set(df["employer_sector_code"].dropna().unique()),
            {"GOV", "PRIVATE", "SOE", "SELF", "NPO", "OTHER"},
        )

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIn("quality_scores", report)
        self.assertIn("issue_count_by_column", report)
        self.assertIn("structure_validation", report)
        self.assertIn("readiness_scores", report)
        self.assertEqual(report["structure_validation"]["missing_sheets"], [])
        self.assertEqual(report["structure_validation"]["missing_columns"], [])

        field_report = pd.read_csv(field_report_path)
        self.assertIn("cleaning_action", field_report.columns)
        self.assertIn("cleaning_reason", field_report.columns)
        self.assertIn("ml_leakage_risk", field_report.columns)

        issues = pd.read_csv(issues_path)
        self.assertIn("completed_without_employment_followup", set(issues["code"]))
        self.assertIn("employed_without_work_start_date", set(issues["code"]))

    def test_raw_file_is_outside_repo_and_not_modified(self):
        raw = (PROJECT_ROOT / "../phase1_outputs/raw/690724 DB_ODOS Students+.xlsx").resolve()
        self.assertTrue(raw.exists())
        self.assertFalse(str(raw).startswith(str(PROJECT_ROOT / "data/raw")))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
