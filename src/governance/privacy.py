from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

from src.governance.audit import append_audit_event
from src.utils.config import PROJECT_ROOT, load_yaml


FORBIDDEN_COLUMNS = {
    "contact_name",
    "contact_phone",
    "contract_no",
    "employment_cert_doc_no",
    "workplace_address",
    "officer_notes",
    "other_comments",
    "employer",
    "job_title",
    "income_raw",
    "gpa_raw",
}

PII_PATTERNS = {
    "thai_phone": re.compile(r"(?<!\d)(?:0\d{1,2}[-\s]?\d{3}[-\s]?\d{4}|0\d{8,9})(?!\d)"),
    "email": re.compile(r"(?<!\S)[^@\s]+@[^@\s]+\.[^@\s]+(?!\S)"),
    "thai_citizen_id_like": re.compile(r"(?<!\d)\d{13}(?!\d)"),
}

AGGREGATE_REQUIRED_COLUMNS = {"count"}


def forbidden_columns_present(columns) -> list[str]:
    return sorted(FORBIDDEN_COLUMNS.intersection(set(columns)))


def assert_no_forbidden_columns(columns) -> None:
    present = forbidden_columns_present(columns)
    if present:
        raise ValueError(f"Forbidden columns present: {', '.join(present)}")


def mask_pii_value(value):
    if value is None or str(value).lower() in {"nan", "none"}:
        return value
    text = str(value)
    for pattern in PII_PATTERNS.values():
        text = pattern.sub("[MASKED]", text)
    return text


def mask_pii_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    safe = df.drop(columns=forbidden_columns_present(df.columns), errors="ignore").copy()
    for column in safe.columns:
        if safe[column].map(lambda value: isinstance(value, str)).any():
            safe[column] = safe[column].map(mask_pii_value)
    return safe


def find_pii_in_text(text: str) -> list[str]:
    findings = []
    for name, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            findings.append(name)
    return findings


def assert_no_pii_text(text: str) -> None:
    findings = find_pii_in_text(text)
    if findings:
        raise ValueError(f"PII-like values detected: {', '.join(findings)}")


def minimum_group_size() -> int:
    return int(load_yaml("config/governance.yaml").get("minimum_group_size", 5))


def role_can(role: str, capability: str) -> bool:
    """Return whether a configured mock role has a governance capability."""
    roles = load_yaml("config/governance.yaml").get("roles", {})
    return bool(roles.get(role, {}).get(capability, False))


def suppress_small_groups(df: pd.DataFrame, count_column: str = "count", min_size: int | None = None) -> pd.DataFrame:
    min_size = int(min_size if min_size is not None else minimum_group_size())
    if count_column not in df:
        return df.copy()
    safe = df.copy().astype(object)
    mask = pd.to_numeric(safe[count_column], errors="coerce").fillna(0) < min_size
    for column in safe.columns:
        if column != count_column:
            safe.loc[mask, column] = "ปกปิด"
    safe.loc[mask, count_column] = f"<{min_size}"
    safe["suppressed"] = mask
    return safe


def assert_aggregate_export(df: pd.DataFrame) -> None:
    assert_no_forbidden_columns(df.columns)
    if not AGGREGATE_REQUIRED_COLUMNS.intersection(set(df.columns)):
        raise ValueError("Aggregate export must include a count-like aggregate column")
    assert_no_pii_text(df.to_csv(index=False))


def aggregate_csv_bytes(
    df: pd.DataFrame,
    export_name: str,
    role: str = "Unknown",
    log_export: bool = True,
) -> bytes:
    """Build a safe aggregate export and optionally record a completed export."""
    if not role_can(role, "can_export_aggregate"):
        raise PermissionError(f"Role is not allowed to export aggregate data: {role}")
    assert_no_forbidden_columns(df.columns)
    safe = mask_pii_dataframe(df)
    assert_aggregate_export(safe)
    csv_text = safe.to_csv(index=False)
    if log_export:
        append_export_log(export_name, role, len(safe), list(safe.columns))
    return csv_text.encode("utf-8-sig")


def append_export_log(export_name: str, role: str, row_count: int, columns: list[str]) -> Path:
    config = load_yaml("config/governance.yaml")
    log_path = PROJECT_ROOT / config["export"]["export_log_path"]
    return append_audit_event(
        "aggregate_export",
        {"export_name": export_name, "role": role, "row_count": row_count, "columns": columns},
        path=log_path,
    )
