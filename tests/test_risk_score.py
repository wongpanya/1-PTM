from src.risk.scoring import score_row


def test_score_row_with_components():
    row = {
        "target_scholarship_risk": 1,
        "target_tracking_risk": 1,
        "target_field_mismatch": 0,
        "target_local_mismatch": 1,
        "income_monthly_est": None,
        "gpa_numeric": 3.2,
        "target_employment_ready": 0,
    }
    result = score_row(row)
    assert result["risk_score"] == 80
    assert len(result["components"]) == 5


def test_score_row_no_risk():
    row = {
        "target_scholarship_risk": 0,
        "target_tracking_risk": 0,
        "target_field_mismatch": 0,
        "target_local_mismatch": 0,
        "income_monthly_est": 30000,
        "gpa_numeric": 3.2,
        "target_employment_ready": 1,
    }
    assert score_row(row)["risk_score"] == 0
