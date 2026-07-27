from __future__ import annotations

import pandas as pd

from src.analytics.metrics import safe_rate
from src.utils.config import load_yaml


def field_recommendations(
    df: pd.DataFrame,
    config_path: str = "config/policy_recommendation.yaml",
    min_records: int | None = None,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    config = load_yaml(config_path)["policy_recommendation"]
    field_config = config["field_recommendation"]
    weights = weights or field_config["weights"]
    min_records = int(min_records if min_records is not None else config["minimum_records"])
    required = {
        "current_field_group",
        "target_graduation_success",
        "target_employment_ready",
        "field_job_fit_level",
        "income_monthly_est",
        "local_fit_level",
    }
    if not required.issubset(df.columns):
        return pd.DataFrame()

    working = df.copy()
    working["field_job_fit_ready"] = pd.to_numeric(working["field_job_fit_level"], errors="coerce").fillna(0) >= 2
    working["local_fit_ready"] = pd.to_numeric(working["local_fit_level"], errors="coerce").fillna(0) >= 2
    working["income_monthly_est"] = pd.to_numeric(working["income_monthly_est"], errors="coerce")
    evidence_columns = [column for column in field_config["evidence_columns"] if column in working]
    working["data_completeness_row"] = working[evidence_columns].notna().mean(axis=1)
    grouped = working.groupby("current_field_group", dropna=False).agg(
        records=("odos_uid", "count"),
        completion_rate=("target_graduation_success", "mean"),
        employment_rate=("target_employment_ready", "mean"),
        field_job_fit=("field_job_fit_ready", "mean"),
        income_outcome=("income_monthly_est", "median"),
        local_development_fit=("local_fit_ready", "mean"),
        data_completeness=("data_completeness_row", "mean"),
    ).reset_index()
    grouped = grouped[grouped["records"] >= min_records].copy()
    if grouped.empty:
        return grouped

    grouped["income_outcome"] = _normalize_series(grouped["income_outcome"])
    for column in ["completion_rate", "employment_rate", "field_job_fit", "local_development_fit", "data_completeness"]:
        grouped[column] = grouped[column].fillna(0)
    grouped["policy_score"] = _weighted_score(grouped, weights)
    grouped["formula"] = field_config["formula"]
    grouped["weights"] = _weights_text(weights)
    grouped["rule_version"] = config["rule_version"]
    grouped["recommendation_type"] = "field_recommendation"
    grouped["analysis_result"] = grouped.apply(
        lambda row: (
            f"Completion {row['completion_rate'] * 100:.1f}%, Employment {row['employment_rate'] * 100:.1f}%, "
            f"Field fit {row['field_job_fit'] * 100:.1f}%, Local fit {row['local_development_fit'] * 100:.1f}%"
        ),
        axis=1,
    )
    grouped["policy_recommendation"] = "พิจารณาจัดลำดับความสำคัญของกลุ่มสาขานี้ตามคะแนนรวมและข้อจำกัดของข้อมูล"
    grouped["limitations_th"] = " | ".join(config.get("limitations_th", []))
    return grouped.sort_values("policy_score", ascending=False)


def area_recommendations(
    df: pd.DataFrame,
    config_path: str = "config/policy_recommendation.yaml",
    min_records: int | None = None,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    config = load_yaml(config_path)["policy_recommendation"]
    area_config = config["area_based_allocation"]
    weights = weights or area_config["weights"]
    min_records = int(min_records if min_records is not None else config["minimum_records"])
    required = {"province", "target_graduation_success", "local_fit_level"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    working = df.copy()
    working["local_return_fit"] = pd.to_numeric(working["local_fit_level"], errors="coerce").fillna(0) >= 2
    grouped = working.groupby("province", dropna=False).agg(
        records=("odos_uid", "count"),
        area_success=("target_graduation_success", "mean"),
        local_return_fit=("local_return_fit", "mean"),
    ).reset_index()
    grouped = grouped[grouped["records"] >= min_records].copy()
    if grouped.empty:
        return grouped

    grouped["existing_recipient_base"] = _normalize_inverse(grouped["records"])
    grouped["external_inequality_need"] = pd.NA
    grouped["workforce_demand"] = pd.NA
    grouped["external_indicator_status"] = "not_available_in_prototype"
    grouped["policy_score"], grouped["available_weight"] = _weighted_score_available(grouped, weights)
    grouped["formula"] = area_config["formula"]
    grouped["weights"] = _weights_text(weights)
    grouped["rule_version"] = config["rule_version"]
    grouped["recommendation_type"] = "area_based_allocation"
    grouped["analysis_result"] = grouped.apply(
        lambda row: (
            f"Records {int(row['records'])}, Success {row['area_success'] * 100:.1f}%, "
            f"Local fit {row['local_return_fit'] * 100:.1f}%"
        ),
        axis=1,
    )
    grouped["policy_recommendation"] = "ผลจัดอันดับเบื้องต้นจากข้อมูลผู้รับทุน โดยยังไม่ใช้ตัวชี้วัดภายนอกในการคำนวณ"
    grouped["limitations_th"] = " | ".join(config.get("limitations_th", []))
    return grouped.sort_values("policy_score", ascending=False)


def recommendation_summary(df: pd.DataFrame) -> dict[str, int | float]:
    return {
        "records": int(len(df)),
        "completion_rate": safe_rate(int((df.get("target_graduation_success", pd.Series(dtype=int)) == 1).sum()), len(df)),
        "employment_rate": safe_rate(int((df.get("target_employment_ready", pd.Series(dtype=int)) == 1).sum()), len(df)),
    }


def _weighted_score(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    total_weight = sum(float(value) for value in weights.values()) or 1
    score = pd.Series(0.0, index=df.index)
    for column, weight in weights.items():
        if column in df:
            score += pd.to_numeric(df[column], errors="coerce").fillna(0) * float(weight)
    return (score / total_weight * 100).round(2)


def _weighted_score_available(df: pd.DataFrame, weights: dict[str, float]) -> tuple[pd.Series, pd.Series]:
    """Calculate from available evidence without inventing values for missing indicators."""
    weighted_score = pd.Series(0.0, index=df.index)
    available_weight = pd.Series(0.0, index=df.index)
    for column, weight in weights.items():
        if column not in df:
            continue
        numeric = pd.to_numeric(df[column], errors="coerce")
        present = numeric.notna()
        weighted_score += numeric.fillna(0) * float(weight)
        available_weight += present.astype(float) * float(weight)
    score = weighted_score.div(available_weight.where(available_weight > 0)).mul(100).round(2)
    return score, available_weight.round(2)


def _normalize_series(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    max_value = values.max()
    if max_value <= 0:
        return pd.Series(0.0, index=series.index)
    return (values / max_value).clip(0, 1)


def _normalize_inverse(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    max_value = values.max()
    if max_value <= 0:
        return pd.Series(0.0, index=series.index)
    return (1 - values / max_value).clip(0, 1)


def _weights_text(weights: dict[str, float]) -> str:
    return ", ".join(f"{key}={value}" for key, value in weights.items())
