from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_yaml


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    dataset: str
    field: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "dataset": self.dataset,
            "field": self.field or "",
        }


def load_validation_schema(path: str = "config/validation_schema.yaml") -> dict[str, Any]:
    return load_yaml(path)


def resolve_dataset_path(path: str | Path) -> Path:
    dataset_path = Path(path)
    if not dataset_path.is_absolute():
        dataset_path = PROJECT_ROOT / dataset_path
    return dataset_path


def validate_dataframe(df: pd.DataFrame, dataset_name: str, schema: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = set(schema.get("required_columns", []))
    forbidden = set(schema.get("forbidden_columns", []))
    primary_key = schema.get("primary_key", "odos_uid")
    thresholds = schema.get("quality_thresholds", {})

    missing_required = sorted(required.difference(df.columns))
    for column in missing_required:
        issues.append(ValidationIssue("error", "missing_required_column", f"Missing required column: {column}", dataset_name, column))

    forbidden_present = sorted(forbidden.intersection(df.columns))
    severity = "error" if thresholds.get("require_no_forbidden_columns", True) else "warning"
    for column in forbidden_present:
        issues.append(ValidationIssue(severity, "forbidden_column_present", f"Forbidden column present: {column}", dataset_name, column))

    if primary_key in df.columns:
        duplicated = int(df[primary_key].duplicated().sum())
        if duplicated > thresholds.get("max_duplicate_primary_keys", 0):
            issues.append(ValidationIssue("error", "duplicate_primary_key", f"Duplicated primary keys: {duplicated}", dataset_name, primary_key))
        missing_pk = int(df[primary_key].isna().sum())
        if missing_pk:
            issues.append(ValidationIssue("error", "missing_primary_key", f"Missing primary keys: {missing_pk}", dataset_name, primary_key))

    allowed_values = schema.get("allowed_values", {})
    for column, allowed in allowed_values.items():
        if column not in df.columns:
            continue
        normalized_allowed = {str(value) for value in allowed}
        values = set(df[column].dropna().astype(str).unique())
        invalid = sorted(values.difference(normalized_allowed))
        if invalid:
            issues.append(
                ValidationIssue(
                    "error",
                    "invalid_allowed_value",
                    f"Invalid values in {column}: {invalid[:10]}",
                    dataset_name,
                    column,
                )
            )

    min_completeness = thresholds.get("min_required_column_completeness_pct", 0)
    for column in sorted(required.intersection(df.columns)):
        completeness = float(df[column].notna().mean() * 100) if len(df) else 0
        if completeness < min_completeness:
            issues.append(
                ValidationIssue(
                    "warning",
                    "low_required_completeness",
                    f"Completeness below threshold: {completeness:.2f}%",
                    dataset_name,
                    column,
                )
            )

    return issues


def validate_dataset_file(path: str | Path, dataset_name: str, schema: dict[str, Any]) -> tuple[pd.DataFrame | None, list[ValidationIssue]]:
    resolved = resolve_dataset_path(path)
    if not resolved.exists():
        return None, [ValidationIssue("error", "missing_dataset", f"Dataset not found: {resolved}", dataset_name)]
    df = pd.read_csv(resolved)
    dataset_rules = schema.get("datasets", {}).get(dataset_name, {})
    min_rows = int(dataset_rules.get("min_rows", 1))
    issues: list[ValidationIssue] = []
    if len(df) < min_rows:
        issues.append(ValidationIssue("error", "dataset_too_small", f"Expected at least {min_rows} rows, found {len(df)}", dataset_name))
    expected_split = dataset_rules.get("expected_split")
    if expected_split and "split" in df.columns:
        unexpected = int((df["split"].astype(str) != str(expected_split)).sum())
        if unexpected:
            issues.append(ValidationIssue("error", "unexpected_split_value", f"Rows with unexpected split value: {unexpected}", dataset_name, "split"))
    issues.extend(validate_dataframe(df, dataset_name, schema))
    return df, issues


def validation_summary(df: pd.DataFrame, dataset_name: str, schema: dict[str, Any]) -> dict[str, Any]:
    primary_key = schema.get("primary_key", "odos_uid")
    required = schema.get("required_columns", [])
    return {
        "dataset": dataset_name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "primary_key": primary_key,
        "unique_primary_keys": int(df[primary_key].nunique()) if primary_key in df.columns else 0,
        "required_columns_present": int(sum(1 for column in required if column in df.columns)),
        "required_columns_total": int(len(required)),
    }
