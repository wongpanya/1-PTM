import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src.ingestion.database import get_connection as database_connection
from src.ingestion.database import initialize_database
from src.risk.individual_prediction import (
    approved_individual_targets,
    create_prediction_cases,
    fit_prototype_artifact,
    import_template_columns,
    list_prediction_cases,
    predict_new_cases,
    submit_domain_approval,
    submit_human_review,
    validate_individual_import,
)
from src.risk.ml_models import DEFAULT_TARGET, TARGET_SPECS
from src.utils.config import PROJECT_ROOT


class IndividualPredictionTest(unittest.TestCase):
    def test_csv_template_and_test_cases_follow_approved_schema(self):
        template = pd.read_csv(
            PROJECT_ROOT / "data/reference/individual_prediction_template.csv"
        )
        sample = pd.read_csv(
            PROJECT_ROOT / "data/reference/individual_prediction_test_cases.csv"
        )
        self.assertEqual(list(template.columns), import_template_columns())
        self.assertEqual(list(sample.columns), import_template_columns())
        self.assertEqual(len(sample), 12)

        cleaned, issues = validate_individual_import(sample)
        self.assertFalse([issue for issue in issues if issue["severity"] == "error"])
        self.assertEqual(len(cleaned), 12)
        self.assertIn("feature_completeness", cleaned.columns)

    def test_all_six_targets_are_approved_for_internal_prototype(self):
        self.assertEqual(set(approved_individual_targets()), set(TARGET_SPECS))

    def test_import_rejects_pii_and_unexpected_columns(self):
        sample = pd.read_csv(
            PROJECT_ROOT / "data/reference/individual_prediction_test_cases.csv"
        ).head(1)
        sample["contact_phone"] = "0812345678"
        _, issues = validate_individual_import(sample)
        codes = {issue["code"] for issue in issues}
        self.assertIn("unexpected_columns", codes)
        self.assertIn("forbidden_columns", codes)
        self.assertIn("pii_detected", codes)

    @unittest.skipIf(importlib.util.find_spec("sklearn") is None, "scikit-learn is not installed")
    def test_new_cases_are_predicted_without_personal_identifiers(self):
        training = pd.read_csv(
            PROJECT_ROOT / "data/sample/modeling_dataset_no_pii.csv"
        )
        sample = pd.read_csv(
            PROJECT_ROOT / "data/reference/individual_prediction_test_cases.csv"
        ).head(3)
        cleaned, issues = validate_individual_import(sample)
        self.assertFalse([issue for issue in issues if issue["severity"] == "error"])

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "prediction.sqlite"
            initialize_database(db_path=db_path)
            with patch(
                "src.risk.individual_prediction.get_connection",
                side_effect=lambda: database_connection(db_path),
            ):
                artifact = fit_prototype_artifact(training, DEFAULT_TARGET)
                predictions = predict_new_cases(artifact, cleaned)

        self.assertEqual(len(predictions), 3)
        self.assertTrue(predictions["probability"].between(0, 1).all())
        self.assertTrue(predictions["status"].eq("pending_review").all())
        self.assertNotIn("odos_uid", predictions.columns)

    def test_creator_reviewer_and_approver_must_be_different(self):
        prediction = pd.DataFrame(
            [
                {
                    "case_id": "CASE-ID-001",
                    "case_reference": "WORKFLOW-001",
                    "purpose_code": "prototype_evaluation",
                    "target": DEFAULT_TARGET,
                    "model_key": "vote_ensemble",
                    "model_version": "test-model-v1",
                    "probability": 0.72,
                    "threshold": 0.5,
                    "tendency_band": "สูง",
                    "interpretation": "แนวโน้มความเสี่ยงสูง",
                    "data_quality_score": 100.0,
                    "data_warnings": [],
                    "features": {"cohort": 1},
                }
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "workflow.sqlite"
            initialize_database(db_path=db_path)
            with patch(
                "src.risk.individual_prediction.get_connection",
                side_effect=lambda: database_connection(db_path),
            ):
                create_prediction_cases(prediction, "officer-01", "CaseOfficer")
                with self.assertRaises(PermissionError):
                    submit_human_review(
                        "CASE-ID-001",
                        "confirm",
                        "ข้อมูลครบถ้วนและควรส่งพิจารณา",
                        "officer-01",
                        "HumanReviewer",
                    )
                status = submit_human_review(
                    "CASE-ID-001",
                    "confirm",
                    "ข้อมูลครบถ้วนและควรส่งพิจารณา",
                    "reviewer-01",
                    "HumanReviewer",
                )
                self.assertEqual(status, "pending_approval")
                with self.assertRaises(PermissionError):
                    submit_domain_approval(
                        "CASE-ID-001",
                        "approve_support",
                        "จัดเจ้าหน้าที่ติดตามและให้คำปรึกษา",
                        "reviewer-01",
                        "DomainApprover",
                    )
                status = submit_domain_approval(
                    "CASE-ID-001",
                    "approve_support",
                    "จัดเจ้าหน้าที่ติดตามและให้คำปรึกษา",
                    "approver-01",
                    "DomainApprover",
                )
                self.assertEqual(status, "approved_for_support")
                cases = list_prediction_cases("CaseOfficer", "officer-01")
                self.assertEqual(cases.iloc[0]["status"], "approved_for_support")


if __name__ == "__main__":
    unittest.main()
