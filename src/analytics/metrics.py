import pandas as pd


def safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 2)


def overview_metrics(df: pd.DataFrame) -> dict:
    total = len(df)
    completion = int((df["target_graduation_success"] == 1).sum()) if "target_graduation_success" in df else 0
    risk = int((df["target_scholarship_risk"] == 1).sum()) if "target_scholarship_risk" in df else 0
    tracking = int((df["target_tracking_risk"] == 1).sum()) if "target_tracking_risk" in df else 0
    income_available = int(df["income_monthly_est"].notna().sum()) if "income_monthly_est" in df else 0
    gpa_available = int(df["gpa_numeric"].notna().sum()) if "gpa_numeric" in df else 0
    return {
        "total_recipients": total,
        "completion_count": completion,
        "completion_rate": safe_rate(completion, total),
        "scholarship_risk_count": risk,
        "scholarship_risk_rate": safe_rate(risk, total),
        "tracking_risk_count": tracking,
        "tracking_risk_rate": safe_rate(tracking, total),
        "income_available": income_available,
        "income_availability_rate": safe_rate(income_available, total),
        "gpa_available": gpa_available,
        "gpa_availability_rate": safe_rate(gpa_available, total),
    }


def top_counts(df: pd.DataFrame, column: str, limit: int = 10) -> pd.DataFrame:
    if column not in df:
        return pd.DataFrame(columns=[column, "count"])
    counts = df[column].fillna("ไม่ระบุ").value_counts().head(limit)
    return pd.DataFrame({column: counts.index, "count": counts.values})
