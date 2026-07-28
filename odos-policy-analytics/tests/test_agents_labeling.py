import unittest

import pandas as pd

from src.agents.registry import agent_registry, get_agent
from src.labeling.workflow import (
    label_definitions,
    label_readiness_summary,
    validate_approval_register,
    validate_label_review_frame,
)
from src.utils.config import PROJECT_ROOT


class AgentsAndLabelingTest(unittest.TestCase):
    def test_registry_contains_all_seven_agents(self):
        registry = agent_registry()
        self.assertEqual(len(registry), 7)
        self.assertEqual(
            set(registry["agent_id"]),
            {
                "data_steward",
                "analytics",
                "risk",
                "policy",
                "external_indicator",
                "governance",
                "technical",
            },
        )
        self.assertIn("self_approve_labels", get_agent("risk")["prohibited_actions"])

    def test_label_definitions_have_owner_approver_and_cutoff(self):
        definitions = label_definitions()
        self.assertGreaterEqual(len(definitions), 8)
        self.assertTrue(definitions["owner_agent"].astype(bool).all())
        self.assertTrue(definitions["human_approver_role"].astype(bool).all())
        self.assertTrue(definitions["leakage_cutoff_rule"].astype(bool).all())

    def test_project_owner_approval_enables_prototype_only(self):
        df = pd.DataFrame(
            {
                "project_condition_status": ["สำเร็จการศึกษา"],
                "study_start_date": ["2010-01-01"],
                "graduation_expected_date": ["2014-01-01"],
                "dropout_date": [None],
                "study_duration_years": [4],
                "current_status": ["สำเร็จ"],
                "employment_type": ["เอกชน"],
                "work_start_date": ["2014-06-01"],
                "field_job_fit_level": [2],
                "current_field_group": ["วิศวกรรม"],
                "local_fit_level": [2],
                "province": ["กรุงเทพมหานคร"],
            }
        )
        readiness = label_readiness_summary(df)
        self.assertTrue(readiness["prototype_ml_eligible"].any())
        self.assertFalse(readiness["production_ml_eligible"].any())
        self.assertTrue(readiness["definition_complete"].all())

    def test_review_template_passes_validation(self):
        path = PROJECT_ROOT / "data/reference/label_review_template.csv"
        frame = pd.read_csv(path)
        self.assertEqual(validate_label_review_frame(frame), [])

    def test_approved_label_requires_reviewer_and_final_value(self):
        path = PROJECT_ROOT / "data/reference/label_review_template.csv"
        frame = pd.read_csv(path).head(1)
        frame.loc[frame.index[0], "label_status"] = "approved"
        issues = validate_label_review_frame(frame)
        codes = {issue["code"] for issue in issues}
        self.assertIn("approved_without_final_label", codes)

    def test_approval_register_matches_configuration(self):
        path = PROJECT_ROOT / "data/reference/label_approval_register.csv"
        frame = pd.read_csv(path)
        self.assertEqual(validate_approval_register(frame), [])
        self.assertTrue(frame["approval_status"].eq("approved_for_prototype").all())
        self.assertFalse(frame["production_approved"].astype(bool).any())


if __name__ == "__main__":
    unittest.main()
