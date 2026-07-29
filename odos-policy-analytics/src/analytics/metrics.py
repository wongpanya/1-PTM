from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.governance.privacy import minimum_group_size
from src.utils.config import PROJECT_ROOT, load_yaml


AGGREGATE_MISSING_LABEL = "ไม่ระบุ"
SAFE_NAME_COLUMNS = {"standardized_university_name"}


def aggregate_group_labels(series: pd.Series) -> pd.Series:
    """Return group labels that can mix numeric categories with the missing label."""
    return series.astype("object").where(series.notna(), AGGREGATE_MISSING_LABEL)


def cleaned_dataset_path() -> Path:
    phase4_path = PROJECT_ROOT / "data/processed/phase4/cleaned_modeling_dataset_no_pii.csv"
    if phase4_path.exists():
        return phase4_path
    return PROJECT_ROOT / "data/sample/modeling_dataset_no_pii.csv"


def load_analytics_dataset(path: str | Path | None = None) -> pd.DataFrame:
    dataset_path = Path(path) if path else cleaned_dataset_path()
    df = pd.read_csv(dataset_path)
    return ensure_dashboard_fields(remove_forbidden_display_columns(df))


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
        if column in SAFE_NAME_COLUMNS
        or not any(fragment in column.lower() for fragment in forbidden_fragments)
    ]
    return df[safe_columns].copy()


def ensure_dashboard_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Backfill safe derived fields when an older no-PII sample is loaded."""
    working = df.copy()
    if "analysis_year" not in working:
        year = pd.Series(pd.NA, index=working.index, dtype="Int64")
        for column in ("study_start_date", "graduation_expected_date", "work_start_date"):
            if column in working:
                candidate = pd.to_datetime(working[column], errors="coerce").dt.year.astype("Int64")
                year = year.fillna(candidate)
        working["analysis_year"] = year

    if "employer_sector_code" not in working and "employment_type" in working:
        rules = load_yaml("config/cleaning_rules.yaml")
        mapping = rules.get("category_mappings", {}).get("employer_sector_codes", {})
        working["employer_sector_code"] = working["employment_type"].map(mapping)

    if "target_dropout" not in working:
        status = working.get("project_condition_status", pd.Series(index=working.index, dtype=object))
        working["target_dropout"] = status.eq("ลาออก").astype(int)
    if "target_termination" not in working:
        status = working.get("project_condition_status", pd.Series(index=working.index, dtype=object))
        working["target_termination"] = status.eq("พ้นสภาพ").astype(int)
    return working


def metric_definitions() -> dict[str, Any]:
    return load_yaml("config/metrics.yaml")


def apply_filters(
    df: pd.DataFrame,
    cohorts: list[Any] | None = None,
    provinces: list[str] | None = None,
    countries: list[str] | None = None,
    field_groups: list[str] | None = None,
    analysis_years: list[Any] | None = None,
    districts: list[str] | None = None,
    regions: list[str] | None = None,
    fields: list[str] | None = None,
    universities: list[str] | None = None,
    employer_sectors: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    filters = {
        "cohort": cohorts or [],
        "province": provinces or [],
        "current_country": countries or [],
        "current_field_group": field_groups or [],
        "analysis_year": analysis_years or [],
        "district": districts or [],
        "region": regions or [],
        "current_field": fields or [],
        "standardized_university_name": universities or [],
        "employer_sector_code": employer_sectors or [],
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
    dropout = int((df["target_dropout"] == 1).sum()) if "target_dropout" in df else 0
    termination = int((df["target_termination"] == 1).sum()) if "target_termination" in df else 0
    income_available = int(len(valid_income_values(df)))
    gpa_available = int(df["gpa_numeric"].notna().sum()) if "gpa_numeric" in df else 0
    countries = int(df["current_country"].dropna().nunique()) if "current_country" in df else 0
    field_groups = int(df["current_field_group"].dropna().nunique()) if "current_field_group" in df else 0
    field_fit = fit_rate_summary(df, "field_job_fit_level")
    local_fit = fit_rate_summary(df, "local_fit_level")
    return {
        "total_recipients": distinct_total,
        "completion_count": completion,
        "completion_rate": safe_rate(completion, total),
        "scholarship_risk_count": risk,
        "scholarship_risk_rate": safe_rate(risk, total),
        "dropout_count": dropout,
        "dropout_rate": safe_rate(dropout, total),
        "termination_count": termination,
        "termination_rate": safe_rate(termination, total),
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
        "field_job_fit_count": field_fit["fit_count"],
        "field_job_fit_denominator": field_fit["denominator"],
        "field_job_fit_rate": field_fit["rate"],
        "local_fit_count": local_fit["fit_count"],
        "local_fit_denominator": local_fit["denominator"],
        "local_fit_rate": local_fit["rate"],
    }


def fit_rate_summary(df: pd.DataFrame, level_column: str, threshold: float = 2) -> dict[str, float | int]:
    """Calculate the share rated medium-or-higher among records with a fit response."""
    if level_column not in df:
        return {"fit_count": 0, "denominator": 0, "rate": 0.0}
    values = pd.to_numeric(df[level_column], errors="coerce").dropna()
    denominator = int(len(values))
    fit_count = int(values.ge(threshold).sum())
    return {
        "fit_count": fit_count,
        "denominator": denominator,
        "rate": safe_rate(fit_count, denominator),
    }


def top_counts(df: pd.DataFrame, column: str, limit: int = 10) -> pd.DataFrame:
    if column not in df:
        return pd.DataFrame(columns=[column, "count"])
    counts = aggregate_group_labels(df[column]).value_counts().head(limit)
    return pd.DataFrame({column: counts.index, "count": counts.values})


def grouped_counts(df: pd.DataFrame, columns: list[str], limit: int = 20) -> pd.DataFrame:
    missing = [column for column in columns if column not in df]
    if missing:
        return pd.DataFrame(columns=[*columns, "count"])
    working = df[columns].copy()
    for column in columns:
        working[column] = aggregate_group_labels(working[column])
    grouped = (
        working
        .groupby(columns, dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(limit)
    )
    return grouped


def remove_small_groups(
    df: pd.DataFrame,
    count_column: str = "count",
    min_size: int | None = None,
) -> pd.DataFrame:
    """Exclude small aggregate groups before they are shown in charts or tables."""
    if count_column not in df:
        return df.copy()
    threshold = int(min_size if min_size is not None else minimum_group_size())
    counts = pd.to_numeric(df[count_column], errors="coerce")
    return df.loc[counts >= threshold].copy()


def rate_by_group(df: pd.DataFrame, group_column: str, target_column: str) -> pd.DataFrame:
    if group_column not in df or target_column not in df:
        return pd.DataFrame(columns=[group_column, "count", "rate"])
    grouped = (
        df[[group_column, target_column]]
        .assign(**{group_column: aggregate_group_labels(df[group_column])})
        .groupby(group_column, dropna=False)
        .agg(count=(target_column, "size"), numerator=(target_column, "sum"))
        .reset_index()
    )
    grouped["rate"] = grouped.apply(lambda row: safe_rate(int(row["numerator"]), int(row["count"])), axis=1)
    return grouped.sort_values(["count", "rate"], ascending=[False, False])


def income_summary(df: pd.DataFrame) -> dict[str, float | int]:
    if "income_monthly_est" not in df:
        return {"records_with_income": 0, "median_income": 0.0, "average_income": 0.0}
    values = valid_income_values(df)
    if values.empty:
        return {"records_with_income": 0, "median_income": 0.0, "average_income": 0.0}
    return {
        "records_with_income": int(len(values)),
        "median_income": round(float(values.median()), 2),
        "average_income": round(float(values.mean()), 2),
    }


def valid_income_values(df: pd.DataFrame) -> pd.Series:
    """Return numeric monthly income values inside the configured valid range."""
    if "income_monthly_est" not in df:
        return pd.Series(dtype=float)
    validation = load_yaml("config/phase4_pipeline.yaml").get("validation", {})
    minimum = float(validation.get("income_min", 0))
    maximum = float(validation.get("income_max", 500000))
    values = pd.to_numeric(df["income_monthly_est"], errors="coerce").dropna()
    return values[values.between(minimum, maximum)]


def income_box_summary(
    df: pd.DataFrame,
    group_column: str,
    value_column: str = "income_monthly_est",
    min_size: int | None = None,
) -> pd.DataFrame:
    """Return privacy-safe aggregate statistics for a grouped income box plot."""
    required = {group_column, value_column}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=[group_column, "count", "minimum", "q1", "median", "q3", "maximum"])

    working = df[[group_column, value_column]].copy()
    working[group_column] = aggregate_group_labels(working[group_column])
    working[value_column] = pd.to_numeric(working[value_column], errors="coerce")
    working = working.dropna(subset=[value_column])
    validation = load_yaml("config/phase4_pipeline.yaml").get("validation", {})
    working = working[
        working[value_column].between(
            float(validation.get("income_min", 0)),
            float(validation.get("income_max", 500000)),
        )
    ]
    if working.empty:
        return pd.DataFrame(columns=[group_column, "count", "minimum", "q1", "median", "q3", "maximum"])

    summary = working.groupby(group_column, dropna=False)[value_column].agg(
        count="size",
        minimum="min",
        q1=lambda values: values.quantile(0.25),
        median="median",
        q3=lambda values: values.quantile(0.75),
        maximum="max",
    ).reset_index()
    return remove_small_groups(summary, min_size=min_size).sort_values("median", ascending=False)


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
    quality_config = definitions.get("data_quality", {})
    dashboard_fields = set(quality_config.get("dashboard_ready_fields", []))
    analytics_fields = set(quality_config.get("analytics_ready_fields", []))
    policy_fields = set(quality_config.get("policy_ready_fields", []))
    ml_features = set(quality_config.get("ml_feature_fields", quality_config.get("model_ready_fields", [])))
    ml_targets = set(quality_config.get("ml_target_fields", []))
    aggregate_only = set(quality_config.get("aggregate_only_fields", []))
    leakage_fields = set(quality_config.get("ml_leakage_fields", []))
    to_collect = set(quality_config.get("fields_to_collect", []))
    field_policies = quality_config.get("field_policies", {})
    thresholds = quality_config.get("readiness_thresholds", {})
    weights = quality_config.get("readiness_weights", {})
    ready_threshold = float(thresholds.get("field_ready_score", 70))
    completeness_weight = float(weights.get("completeness", 0.7))
    validity_weight = float(weights.get("validity", 0.3))
    completeness = field_completeness(df)

    if issues_df is None or issues_df.empty or "field" not in issues_df:
        issue_counts = pd.DataFrame(columns=["field", "format_or_standard_issues", "error_count", "warning_count"])
    else:
        working_issues = issues_df.copy()
        severity = (
            working_issues["severity"]
            if "severity" in working_issues
            else pd.Series("", index=working_issues.index)
        )
        working_issues["is_error"] = severity.eq("error").astype(int)
        working_issues["is_warning"] = severity.eq("warning").astype(int)
        issue_counts = (
            working_issues.groupby("field")
            .agg(
                format_or_standard_issues=("field", "size"),
                error_count=("is_error", "sum"),
                warning_count=("is_warning", "sum"),
            )
            .reset_index()
        )

    summary = completeness.merge(issue_counts, on="field", how="left")
    for column in ["format_or_standard_issues", "error_count", "warning_count"]:
        summary[column] = summary[column].fillna(0).astype(int)
    total = max(len(df), 1)
    summary["missing_rate"] = (100 - summary["completeness_rate"]).round(2)
    summary["issue_rate"] = (summary["format_or_standard_issues"] / total * 100).clip(upper=100).round(2)
    summary["validity_rate"] = (100 - summary["issue_rate"]).round(2)
    summary["quality_score"] = (
        summary["completeness_rate"] * completeness_weight
        + summary["validity_rate"] * validity_weight
    ).round(2)
    summary["dtype"] = summary["field"].map(lambda field: str(df[field].dtype))
    summary["expected_type"] = summary["field"].map(_expected_type)
    summary["dashboard_eligible"] = summary["field"].isin(dashboard_fields)
    summary["analytics_eligible"] = summary["field"].isin(analytics_fields)
    summary["policy_eligible"] = summary["field"].isin(policy_fields)
    summary["ml_feature"] = summary["field"].isin(ml_features)
    summary["ml_target"] = summary["field"].isin(ml_targets)
    summary["aggregate_only"] = summary["field"].isin(aggregate_only)
    summary["ml_leakage_risk"] = summary["field"].isin(leakage_fields)
    meets_quality = summary["quality_score"] >= ready_threshold
    summary["dashboard_ready"] = summary["dashboard_eligible"] & meets_quality
    summary["analytics_ready"] = summary["analytics_eligible"] & meets_quality
    summary["policy_ready"] = summary["policy_eligible"] & meets_quality
    summary["model_ready"] = (summary["ml_feature"] | summary["ml_target"]) & meets_quality
    summary["needs_more_collection"] = summary["field"].isin(to_collect)
    summary["cleaning_action"] = summary["field"].map(
        lambda field: _field_action(field, field_policies, ml_features, ml_targets, aggregate_only, leakage_fields)
    )
    summary["cleaning_reason"] = summary["field"].map(
        lambda field: _field_reason(field, field_policies, ml_features, ml_targets, aggregate_only, leakage_fields)
    )
    summary["readiness_status"] = summary.apply(
        lambda row: _readiness_status(row, ready_threshold, float(thresholds.get("high_missing_rate", 40))),
        axis=1,
    )
    return summary


def readiness_scorecard(
    quality: pd.DataFrame,
    definitions: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Summarize transparent readiness scores for each intended use case."""
    definitions = definitions or metric_definitions()
    config = definitions.get("data_quality", {})
    use_cases = {
        "Dashboard": config.get("dashboard_ready_fields", []),
        "Analytics": config.get("analytics_ready_fields", []),
        "Policy": config.get("policy_ready_fields", []),
        "ML": [*config.get("ml_feature_fields", []), *config.get("ml_target_fields", [])],
    }
    threshold = float(config.get("readiness_thresholds", {}).get("field_ready_score", 70))
    score_by_field = quality.set_index("field")["quality_score"].to_dict() if not quality.empty else {}
    rows = []
    for use_case, fields in use_cases.items():
        unique_fields = list(dict.fromkeys(fields))
        scores = [float(score_by_field.get(field, 0.0)) for field in unique_fields]
        ready_count = sum(score >= threshold for score in scores)
        score = round(sum(scores) / len(scores), 2) if scores else 0.0
        rows.append(
            {
                "use_case": use_case,
                "readiness_score": score,
                "ready_fields": ready_count,
                "required_fields": len(unique_fields),
                "status": _score_label(score),
            }
        )
    return pd.DataFrame(rows)


def group_readiness_summary(
    df: pd.DataFrame,
    group_column: str,
    definitions: dict[str, Any] | None = None,
    min_size: int | None = None,
) -> pd.DataFrame:
    """Compare data readiness across cohorts or geographies without exposing small groups."""
    definitions = definitions or metric_definitions()
    config = definitions.get("data_quality", {})
    use_cases = {
        "dashboard_readiness": config.get("dashboard_ready_fields", []),
        "policy_readiness": config.get("policy_ready_fields", []),
        "ml_readiness": [*config.get("ml_feature_fields", []), *config.get("ml_target_fields", [])],
    }
    if group_column not in df:
        return pd.DataFrame(columns=[group_column, "count", *use_cases.keys()])

    output_columns = [group_column, "count", *use_cases.keys()]
    if df.empty:
        return pd.DataFrame(columns=output_columns)

    rows = []
    working = df.assign(**{group_column: aggregate_group_labels(df[group_column])})
    for group, subset in working.groupby(group_column, dropna=False):
        row = {group_column: group, "count": int(len(subset))}
        for score_name, fields in use_cases.items():
            available = [field for field in dict.fromkeys(fields) if field in subset]
            row[score_name] = (
                round(float(subset[available].notna().mean().mean() * 100), 2)
                if available
                else 0.0
            )
        rows.append(row)
    if not rows:
        return pd.DataFrame(columns=output_columns)
    return remove_small_groups(
        pd.DataFrame(rows, columns=output_columns),
        min_size=min_size,
    ).sort_values("count", ascending=False)


def outcome_by_group(
    df: pd.DataFrame,
    group_column: str,
    min_size: int | None = None,
) -> pd.DataFrame:
    """Build aggregate education, employment, risk, and follow-up outcomes by group."""
    targets = {
        "completion_rate": "target_graduation_success",
        "employment_rate": "target_employment_ready",
        "dropout_rate": "target_dropout",
        "termination_rate": "target_termination",
        "scholarship_risk_rate": "target_scholarship_risk",
        "tracking_gap_rate": "target_tracking_risk",
    }
    required = [group_column, *targets.values()]
    if group_column not in df:
        return pd.DataFrame(columns=[group_column, "count", *targets.keys()])
    working = df.copy()
    for field in required[1:]:
        if field not in working:
            working[field] = 0
    working[group_column] = aggregate_group_labels(working[group_column])
    aggregations = {"count": ("odos_uid", "size")} if "odos_uid" in working else {"count": (group_column, "size")}
    aggregations.update({name: (field, "mean") for name, field in targets.items()})
    result = working.groupby(group_column, dropna=False).agg(**aggregations).reset_index()
    for name in targets:
        result[name] = (result[name] * 100).round(2)
    return remove_small_groups(result, min_size=min_size).sort_values("count", ascending=False)


def followup_coverage_by_group(
    df: pd.DataFrame,
    group_column: str,
    min_size: int | None = None,
) -> pd.DataFrame:
    """Measure availability of the main post-scholarship follow-up fields by group."""
    followup_fields = [
        "employment_type",
        "work_start_date",
        "income_monthly_est",
        "field_job_fit_level",
        "local_fit_level",
    ]
    if group_column not in df:
        return pd.DataFrame(columns=[group_column, "count", "followup_completeness", "tracking_gap_rate"])
    output_columns = [group_column, "count", "followup_completeness", "tracking_gap_rate"]
    if df.empty:
        return pd.DataFrame(columns=output_columns)

    working = df.assign(**{group_column: aggregate_group_labels(df[group_column])})
    rows = []
    for group, subset in working.groupby(group_column, dropna=False):
        available = [field for field in followup_fields if field in subset]
        completeness = float(subset[available].notna().mean().mean() * 100) if available else 0.0
        tracking = (
            float(pd.to_numeric(subset.get("target_tracking_risk"), errors="coerce").fillna(0).mean() * 100)
            if "target_tracking_risk" in subset
            else 0.0
        )
        rows.append(
            {
                group_column: group,
                "count": int(len(subset)),
                "followup_completeness": round(completeness, 2),
                "tracking_gap_rate": round(tracking, 2),
            }
        )
    if not rows:
        return pd.DataFrame(columns=output_columns)
    return remove_small_groups(pd.DataFrame(rows, columns=output_columns), min_size=min_size).sort_values(
        ["followup_completeness", "count"], ascending=[True, False]
    )


def _expected_type(field: str) -> str:
    if field.endswith("_date"):
        return "date"
    if field.startswith("target_") or field.endswith("_flag"):
        return "binary"
    if field.endswith("_level") or field.endswith("_years") or field.endswith("_numeric") or field.endswith("_est"):
        return "numeric"
    if field in {"source_id", "cohort", "birth_year_be", "province_code", "analysis_year"}:
        return "integer"
    return "category/text"


def _field_action(field, policies, ml_features, ml_targets, aggregate_only, leakage_fields) -> str:
    if field in policies:
        return policies[field].get("action_th", "ตรวจสอบตามนโยบายรายตัวแปร")
    if field in ml_targets:
        return "สร้างเป็น target และเก็บสูตรที่ตรวจสอบย้อนกลับได้"
    if field in leakage_fields:
        return "ใช้วิเคราะห์แบบ aggregate และตัดออกจาก ML feature"
    if field in aggregate_only:
        return "ใช้เฉพาะผลรวมและปกปิดกลุ่มขนาดเล็ก"
    if field in ml_features:
        return "ทำความสะอาดและประเมินก่อนใช้เป็น ML feature"
    if field.endswith("_date"):
        return "แปลงเป็นวันที่มาตรฐานและตรวจลำดับเวลา"
    return "ปรับค่าว่างและมาตรฐานหมวดหมู่ก่อนวิเคราะห์"


def _field_reason(field, policies, ml_features, ml_targets, aggregate_only, leakage_fields) -> str:
    if field in policies:
        return policies[field].get("reason_th", "กำหนดตามนโยบายข้อมูลของ Prototype")
    if field in ml_targets:
        return "เป็นผลลัพธ์ที่ต้องการทำนาย จึงห้ามใช้เป็น feature"
    if field in leakage_fields:
        return "เกิดพร้อมหรือหลังผลลัพธ์เป้าหมาย มีความเสี่ยงต่อ data leakage"
    if field in aggregate_only:
        return "มีความละเอียดสูง จึงอนุญาตเฉพาะการสรุปรวมตาม minimum group size"
    if field in ml_features:
        return "เป็นข้อมูลไม่ใช่ PII ที่มีศักยภาพเป็น feature เมื่อคุณภาพผ่านเกณฑ์"
    return "ใช้เพื่ออธิบายข้อมูลที่มี แต่ยังไม่ได้รับรองเป็น feature หรือ KPI หลัก"


def _readiness_status(row: pd.Series, threshold: float, high_missing_rate: float) -> str:
    if bool(row["ml_target"]):
        return "Target: ห้ามใช้เป็น feature"
    if bool(row["ml_leakage_risk"]):
        return "ตัดออกจาก ML feature"
    if float(row["missing_rate"]) >= high_missing_rate:
        return "ต้องเก็บ/ปรับปรุงข้อมูล"
    if float(row["quality_score"]) < threshold:
        return "ต้อง clean หรือทบทวนมาตรฐาน"
    if bool(row["aggregate_only"]):
        return "พร้อมใช้เฉพาะ Aggregate"
    if bool(row["dashboard_eligible"] or row["analytics_eligible"] or row["policy_eligible"] or row["ml_feature"]):
        return "พร้อมใช้"
    return "ทบทวนก่อนใช้งาน"


def _score_label(score: float) -> str:
    if score >= 85:
        return "พร้อมใช้"
    if score >= 70:
        return "พร้อมใช้แบบมีเงื่อนไข"
    return "ต้องปรับปรุง"


def load_phase4_issues() -> pd.DataFrame:
    path = PROJECT_ROOT / "data/processed/phase4/validation_issues.csv"
    if not path.exists():
        return pd.DataFrame(columns=["severity", "code", "odos_uid", "field", "message", "raw_value"])
    return pd.read_csv(path)
