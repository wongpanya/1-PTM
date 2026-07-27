from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_yaml


AGGREGATE_MISSING_LABEL = "ไม่ระบุ"


def cleaned_dataset_path() -> Path:
    phase4_path = PROJECT_ROOT / "data/processed/phase4/cleaned_modeling_dataset_no_pii.csv"
    if phase4_path.exists():
        return phase4_path
    return PROJECT_ROOT / "data/sample/modeling_dataset_no_pii.csv"


def load_analytics_dataset(path: str | Path | None = None) -> pd.DataFrame:
    dataset_path = Path(path) if path else cleaned_dataset_path()
    df = pd.read_csv(dataset_path)
    return remove_forbidden_display_columns(df)


def remove_forbidden_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    forbidden_fragments = [
        "name",
        "phone",
        "tel",
        "address",
        "contract",
        "citizen",
        "passport",
        "email",
    ]
    safe_columns = [
        column
        for column in df.columns
        if not any(fragment in column.lower() for fragment in forbidden_fragments)
    ]
    return df[safe_columns].copy()


def metric_definitions() -> dict[str, Any]:
    return load_yaml("config/metrics.yaml")


def apply_filters(
    df: pd.DataFrame,
    cohorts: list[Any] | None = None,
    provinces: list[str] | None = None,
    countries: list[str] | None = None,
    field_groups: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    filters = {
        "cohort": cohorts or [],
        "province": provinces or [],
        "current_country": countries or [],
        "current_field_group": field_groups or [],
    }
    for column, values in filters.items():
        if values and column in filtered:
            filtered = filtered[filtered[column].isin(values)]
    return filtered


def safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 2)


def overview_metrics(df: pd.DataFrame) -> dict:
    total = len(df)
    distinct_total = int(df["odos_uid"].nunique()) if "odos_uid" in df else total
    completion = int((df["target_graduation_success"] == 1).sum()) if "target_graduation_success" in df else 0
    risk = int((df["target_scholarship_risk"] == 1).sum()) if "target_scholarship_risk" in df else 0
    tracking = int((df["target_tracking_risk"] == 1).sum()) if "target_tracking_risk" in df else 0
    employed = int((df["target_employment_ready"] == 1).sum()) if "target_employment_ready" in df else 0
    income_available = int(df["income_monthly_est"].notna().sum()) if "income_monthly_est" in df else 0
    gpa_available = int(df["gpa_numeric"].notna().sum()) if "gpa_numeric" in df else 0
    countries = int(df["current_country"].dropna().nunique()) if "current_country" in df else 0
    field_groups = int(df["current_field_group"].dropna().nunique()) if "current_field_group" in df else 0
    return {
        "total_recipients": distinct_total,
        "completion_count": completion,
        "completion_rate": safe_rate(completion, total),
        "scholarship_risk_count": risk,
        "scholarship_risk_rate": safe_rate(risk, total),
        "tracking_risk_count": tracking,
        "tracking_risk_rate": safe_rate(tracking, total),
        "employed_count": employed,
        "employment_rate": safe_rate(employed, total),
        "income_available": income_available,
        "income_availability_rate": safe_rate(income_available, total),
        "gpa_available": gpa_available,
        "gpa_availability_rate": safe_rate(gpa_available, total),
        "countries_count": countries,
        "field_groups_count": field_groups,
    }


def top_counts(df: pd.DataFrame, column: str, limit: int = 10) -> pd.DataFrame:
    if column not in df:
        return pd.DataFrame(columns=[column, "count"])
    counts = df[column].fillna(AGGREGATE_MISSING_LABEL).value_counts().head(limit)
    return pd.DataFrame({column: counts.index, "count": counts.values})


def grouped_counts(df: pd.DataFrame, columns: list[str], limit: int = 20) -> pd.DataFrame:
    missing = [column for column in columns if column not in df]
    if missing:
        return pd.DataFrame(columns=[*columns, "count"])
    grouped = (
        df[columns]
        .fillna(AGGREGATE_MISSING_LABEL)
        .groupby(columns, dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(limit)
    )
    return grouped


def rate_by_group(df: pd.DataFrame, group_column: str, target_column: str) -> pd.DataFrame:
    if group_column not in df or target_column not in df:
        return pd.DataFrame(columns=[group_column, "count", "rate"])
    grouped = (
        df[[group_column, target_column]]
        .assign(**{group_column: df[group_column].fillna(AGGREGATE_MISSING_LABEL)})
        .groupby(group_column, dropna=False)
        .agg(count=(target_column, "size"), numerator=(target_column, "sum"))
        .reset_index()
    )
    grouped["rate"] = grouped.apply(lambda row: safe_rate(int(row["numerator"]), int(row["count"])), axis=1)
    return grouped.sort_values(["count", "rate"], ascending=[False, False])


def income_summary(df: pd.DataFrame) -> dict[str, float | int]:
    if "income_monthly_est" not in df:
        return {"records_with_income": 0, "median_income": 0.0, "average_income": 0.0}
    values = pd.to_numeric(df["income_monthly_est"], errors="coerce").dropna()
    if values.empty:
        return {"records_with_income": 0, "median_income": 0.0, "average_income": 0.0}
    return {
        "records_with_income": int(len(values)),
        "median_income": round(float(values.median()), 2),
        "average_income": round(float(values.mean()), 2),
    }


def field_completeness(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = max(len(df), 1)
    for column in df.columns:
        null_count = int(df[column].isna().sum())
        rows.append(
            {
                "field": column,
                "complete_count": int(total - null_count),
                "missing_count": null_count,
                "completeness_rate": safe_rate(total - null_count, total),
            }
        )
    return pd.DataFrame(rows).sort_values(["completeness_rate", "field"], ascending=[True, True])


def data_quality_summary(df: pd.DataFrame, issues_df: pd.DataFrame | None, definitions: dict[str, Any] | None = None) -> pd.DataFrame:
    definitions = definitions or metric_definitions()
    dashboard_ready = set(definitions.get("data_quality", {}).get("dashboard_ready_fields", []))
    model_ready = set(definitions.get("data_quality", {}).get("model_ready_fields", []))
    to_collect = set(definitions.get("data_quality", {}).get("fields_to_collect", []))
    completeness = field_completeness(df)
    if issues_df is None or issues_df.empty or "field" not in issues_df:
        issue_counts = pd.DataFrame(columns=["field", "format_or_standard_issues"])
    else:
        issue_counts = issues_df.groupby("field").size().reset_index(name="format_or_standard_issues")
    summary = completeness.merge(issue_counts, on="field", how="left")
    summary["format_or_standard_issues"] = summary["format_or_standard_issues"].fillna(0).astype(int)
    summary["dashboard_ready"] = summary["field"].isin(dashboard_ready)
    summary["model_ready"] = summary["field"].isin(model_ready)
    summary["needs_more_collection"] = summary["field"].isin(to_collect)
    return summary


def load_phase4_issues() -> pd.DataFrame:
    path = PROJECT_ROOT / "data/processed/phase4/validation_issues.csv"
    if not path.exists():
        return pd.DataFrame(columns=["severity", "code", "odos_uid", "field", "message", "raw_value"])
    return pd.read_csv(path)
