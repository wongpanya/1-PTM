import unittest

import pandas as pd

from src.validation.schema import load_validation_schema, validate_dataframe


def valid_minimum_frame(extra=None):
    data = {
        "odos_uid": ["ODOS00001"],
        "cohort": [1],
        "province": ["A"],
        "project_condition_status": ["สำเร็จการศึกษา"],
        "current_field_group": ["field"],
        "employment_type": ["ภาครัฐ"],
        "target_graduation_success": [1],
        "target_scholarship_risk": [0],
        "target_tracking_risk": [0],
        "target_employment_ready": [1],
        "target_field_mismatch": [0],
        "target_local_mismatch": [0],
    }
    if extra:
        data.update(extra)
    return pd.DataFrame(data)


class ValidationSchemaTest(unittest.TestCase):
    def test_validate_dataframe_detects_forbidden_column(self):
        schema = load_validation_schema()
        issues = validate_dataframe(valid_minimum_frame({"contact_phone": ["secret"]}), "test", schema)
        self.assertTrue(any(issue.code == "forbidden_column_present" for issue in issues))

    def test_validate_dataframe_accepts_minimum_valid_shape(self):
        schema = load_validation_schema()
        issues = validate_dataframe(valid_minimum_frame(), "test", schema)
        self.assertEqual([issue for issue in issues if issue.severity == "error"], [])


if __name__ == "__main__":
    unittest.main()
