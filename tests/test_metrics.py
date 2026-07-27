import pandas as pd

from src.analytics.metrics import overview_metrics, safe_rate, top_counts


def test_safe_rate():
    assert safe_rate(1, 4) == 25.0
    assert safe_rate(1, 0) == 0.0


def test_overview_metrics():
    df = pd.DataFrame({
        "odos_uid": ["a", "b"],
        "target_graduation_success": [1, 0],
        "target_scholarship_risk": [0, 1],
        "target_tracking_risk": [0, 1],
        "income_monthly_est": [10000, None],
        "gpa_numeric": [3.0, None],
    })
    metrics = overview_metrics(df)
    assert metrics["total_recipients"] == 2
    assert metrics["completion_rate"] == 50.0
    assert metrics["income_availability_rate"] == 50.0


def test_top_counts():
    df = pd.DataFrame({"region": ["A", "A", None]})
    result = top_counts(df, "region")
    assert list(result.columns) == ["region", "count"]
    assert result.iloc[0]["count"] == 2
