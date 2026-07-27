import pandas as pd


def field_recommendations(df: pd.DataFrame, min_records: int = 20) -> pd.DataFrame:
    required = {"current_field_group", "target_graduation_success", "target_employment_ready", "target_field_mismatch"}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    grouped = df.groupby("current_field_group", dropna=False).agg(
        records=("odos_uid", "count"),
        completion_rate=("target_graduation_success", "mean"),
        employment_ready_rate=("target_employment_ready", "mean"),
        mismatch_rate=("target_field_mismatch", "mean"),
    ).reset_index()
    grouped = grouped[grouped["records"] >= min_records].copy()
    grouped["policy_score"] = (
        grouped["completion_rate"] * 45
        + grouped["employment_ready_rate"] * 35
        + (1 - grouped["mismatch_rate"]) * 20
    ).round(2)
    return grouped.sort_values("policy_score", ascending=False)
