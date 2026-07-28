from __future__ import annotations

from typing import Any

import pandas as pd

from src.analytics.metrics import (
    AGGREGATE_MISSING_LABEL,
    remove_small_groups,
    safe_rate,
    valid_income_values,
)
from src.governance.privacy import minimum_group_size
from src.utils.config import load_yaml


def visualization_config() -> dict[str, Any]:
    return load_yaml("config/visualization.yaml")


def question_options(config: dict[str, Any] | None = None) -> dict[str, str]:
    config = config or visualization_config()
    return {item["label_th"]: key for key, item in config.get("questions", {}).items()}


def recommendation_for(
    question_key: str,
    category_count: int | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or visualization_config()
    recommendation = dict(config.get("questions", {}).get(question_key, {}))
    recommendation["question_key"] = question_key
    recommendation["compatibility_warning"] = ""
    if (
        question_key == "proportion"
        and category_count is not None
        and category_count > 5
    ):
        recommendation["recommended_chart"] = "100% Stacked Bar"
        recommendation["compatibility_warning"] = (
            f"พบ {category_count} หมวดหมู่ จึงไม่แนะนำ Donut/Pie และใช้ 100% Stacked Bar แทน"
        )
    return recommendation


def readiness_for_fields(
    quality: pd.DataFrame,
    fields: list[str],
) -> dict[str, Any]:
    if quality.empty or not fields:
        return {"score": 0.0, "available": 0, "required": len(fields), "status": "ต้องปรับปรุง"}
    indexed = quality.set_index("field")
    scores = [
        float(indexed.loc[field, "quality_score"]) if field in indexed.index else 0.0
        for field in fields
    ]
    score = round(sum(scores) / len(scores), 2)
    available = sum(field in indexed.index for field in fields)
    status = "พร้อมใช้" if score >= 85 else "พร้อมใช้แบบมีเงื่อนไข" if score >= 70 else "ต้องปรับปรุง"
    return {"score": score, "available": available, "required": len(fields), "status": status}


def aggregate_proportions(
    df: pd.DataFrame,
    category_column: str,
    group_column: str | None = None,
    min_size: int | None = None,
) -> pd.DataFrame:
    if group_column == category_column:
        group_column = None
    required = [category_column] + ([group_column] if group_column else [])
    if any(column not in df for column in required):
        return pd.DataFrame(columns=[*required, "count", "percent"])
    working = df[required].fillna(AGGREGATE_MISSING_LABEL)
    grouped = working.groupby(required, dropna=False).size().reset_index(name="count")
    if group_column:
        totals = grouped.groupby(group_column)["count"].sum().rename("denominator")
        grouped = grouped.merge(totals, on=group_column, how="left")
    else:
        grouped["denominator"] = int(grouped["count"].sum())
    grouped = remove_small_groups(grouped, min_size=min_size)
    if grouped.empty:
        grouped["percent"] = pd.Series(dtype=float)
        return grouped
    grouped["percent"] = (grouped["count"] / grouped["denominator"] * 100).round(2)
    return grouped.sort_values("count", ascending=False)


def aggregate_histogram(
    df: pd.DataFrame,
    value_column: str,
    bins: int = 10,
    min_size: int | None = None,
) -> pd.DataFrame:
    if value_column not in df:
        return pd.DataFrame(columns=["bin", "count"])
    values = (
        valid_income_values(df)
        if value_column == "income_monthly_est"
        else pd.to_numeric(df[value_column], errors="coerce").dropna()
    )
    if values.empty or values.nunique() < 2:
        return pd.DataFrame(columns=["bin", "count"])
    bucket = pd.cut(values, bins=bins, duplicates="drop")
    result = bucket.value_counts(sort=False).rename_axis("interval").reset_index(name="count")
    result["bin"] = result["interval"].map(lambda value: f"{value.left:,.0f}-{value.right:,.0f}")
    return remove_small_groups(result[["bin", "count"]], min_size=min_size)


def pathway_flows(
    df: pd.DataFrame,
    source_column: str,
    target_column: str,
    min_size: int | None = None,
    limit: int = 30,
) -> pd.DataFrame:
    if source_column not in df or target_column not in df:
        return pd.DataFrame(columns=["source", "target", "count"])
    working = df[[source_column, target_column]].fillna(AGGREGATE_MISSING_LABEL)
    result = (
        working.groupby([source_column, target_column], dropna=False)
        .size()
        .reset_index(name="count")
        .rename(columns={source_column: "source", target_column: "target"})
    )
    return (
        remove_small_groups(result, min_size=min_size)
        .sort_values("count", ascending=False)
        .head(limit)
    )


def completeness_matrix(
    df: pd.DataFrame,
    group_column: str,
    fields: list[str],
    min_size: int | None = None,
) -> pd.DataFrame:
    available = [field for field in fields if field in df]
    if group_column not in df or not available:
        return pd.DataFrame(columns=[group_column, "count", *available])
    threshold = int(min_size if min_size is not None else minimum_group_size())
    working = df.assign(**{group_column: df[group_column].fillna(AGGREGATE_MISSING_LABEL)})
    rows = []
    for group, subset in working.groupby(group_column, dropna=False):
        if len(subset) < threshold:
            continue
        row = {group_column: group, "count": int(len(subset))}
        row.update(
            {
                field: round(float(subset[field].notna().mean() * 100), 2)
                for field in available
            }
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("count", ascending=False) if rows else pd.DataFrame(
        columns=[group_column, "count", *available]
    )


def funnel_summary(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    completed_flag = _binary_series(df, "target_graduation_success")
    tracking_flag = _binary_series(df, "target_tracking_risk")
    employment_flag = _binary_series(df, "target_employment_ready")
    completed_mask = completed_flag.eq(1)
    followed_mask = (
        completed_mask
        & tracking_flag.eq(0)
        & (df["employment_type"].notna() if "employment_type" in df else False)
    )
    employed_mask = followed_mask & employment_flag.eq(1)
    income_mask = employed_mask & (df["income_monthly_est"].notna() if "income_monthly_est" in df else False)
    completed = int(completed_mask.sum())
    followed = int(followed_mask.sum())
    employed = int(employed_mask.sum())
    income = int(income_mask.sum())
    return pd.DataFrame(
        {
            "stage": ["ผู้รับทุน", "สำเร็จการศึกษา", "มีข้อมูลติดตามงาน", "มีงานทำ", "มีข้อมูลรายได้"],
            "count": [total, completed, followed, employed, income],
            "rate_from_total": [
                safe_rate(total, total),
                safe_rate(completed, total),
                safe_rate(followed, total),
                safe_rate(employed, total),
                safe_rate(income, total),
            ],
        }
    )


def _binary_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df:
        return pd.Series(0, index=df.index, dtype=int)
    return pd.to_numeric(df[column], errors="coerce").fillna(0)
