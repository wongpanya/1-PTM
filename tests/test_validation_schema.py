import pandas as pd

from src.validation.schema import load_validation_schema, validate_dataframe


def test_validate_dataframe_detects_forbidden_column():
    schema = load_validation_schema()
    df = pd.DataFrame({
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
        "contact_phone": ["secret"],
    })
    issues = validate_dataframe(df, "test", schema)
    assert any(issue.code == "forbidden_column_present" for issue in issues)


def test_validate_dataframe_accepts_minimum_valid_shape():
    schema = load_validation_schema()
    df = pd.DataFrame({
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
    })
    issues = validate_dataframe(df, "test", schema)
    assert [issue for issue in issues if issue.severity == "error"] == []
