from __future__ import annotations

from typing import Any

import pandas as pd

from src.agents.registry import agent_config
from src.utils.config import load_yaml


def labeling_config() -> dict[str, Any]:
    return load_yaml("config/labeling.yaml")


def label_definitions() -> pd.DataFrame:
    rows = []
    for target_name, item in labeling_config().get("targets", {}).items():
        rows.append(
            {
                "target_name": target_name,
                "priority": int(item["priority"]),
                "label_th": item["label_th"],
                "label_version": item["label_version"],
                "label_type": item["label_type"],
                "allowed_values": ", ".join(str(value) for value in item.get("allowed_values", [])),
                "evidence_fields": ", ".join(item.get("evidence_fields", [])),
                "owner_agent": item["owner_agent"],
                "human_approver_role": item["human_approver_role"],
                "approval_status": item["approval_status"],
                "leakage_cutoff_rule": item["leakage_cutoff_rule"],
            }
        )
    return pd.DataFrame(rows).sort_values(["priority", "target_name"]).reset_index(drop=True)


def label_readiness_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    agents = agent_config().get("agents", {})
    config = labeling_config()
    prototype_states = set(config["workflow"].get("prototype_eligible_states", []))
    production_states = set(config["workflow"].get("production_eligible_states", []))
    for target_name, item in config.get("targets", {}).items():
        evidence = list(item.get("evidence_fields", []))
        available = [field for field in evidence if field in df]
        evidence_completeness = (
            float(df[available].notna().mean().mean() * 100)
            if available and not df.empty
            else 0.0
        )
        definition_complete = all(
            [
                item.get("label_version"),
                item.get("allowed_values"),
                item.get("leakage_cutoff_rule"),
                item.get("human_approver_role"),
                item.get("owner_agent") in agents,
            ]
        )
        approval_status = item.get("approval_status")
        prototype_approved = approval_status in prototype_states
        production_approved = approval_status in production_states
        score = round(
            (40.0 if definition_complete else 0.0)
            + min(evidence_completeness, 100.0) * 0.3
            + (30.0 if prototype_approved else 0.0),
            2,
        )
        rows.append(
            {
                "target_name": target_name,
                "priority": int(item["priority"]),
                "label_th": item["label_th"],
                "definition_complete": bool(definition_complete),
                "evidence_fields_available": f"{len(available)}/{len(evidence)}",
                "evidence_completeness": round(evidence_completeness, 2),
                "approval_status": approval_status,
                "readiness_score": score,
                "prototype_ml_eligible": bool(prototype_approved and score >= 85),
                "production_ml_eligible": bool(production_approved and score >= 85),
                "ml_eligible": bool(prototype_approved and score >= 85),
                "owner_agent": item["owner_agent"],
                "human_approver_role": item["human_approver_role"],
            }
        )
    return pd.DataFrame(rows).sort_values(["priority", "target_name"]).reset_index(drop=True)


def validate_label_review_frame(frame: pd.DataFrame) -> list[dict[str, str]]:
    config = labeling_config()
    template = config["review_template"]
    targets = config.get("targets", {})
    lifecycle = set(config["workflow"]["lifecycle"])
    issues: list[dict[str, str]] = []

    missing = [column for column in template["required_columns"] if column not in frame]
    if missing:
        issues.append({"code": "missing_columns", "detail": ", ".join(missing)})
        return issues

    forbidden = [
        column
        for column in frame.columns
        if column.lower() in {item.lower() for item in template.get("forbidden_columns", [])}
    ]
    if forbidden:
        issues.append({"code": "forbidden_columns", "detail": ", ".join(forbidden)})

    for index, row in frame.iterrows():
        target_name = str(row["target_name"]).strip()
        if target_name not in targets:
            issues.append({"code": "unknown_target", "detail": f"row {index + 2}: {target_name}"})
            continue
        status = str(row["label_status"]).strip()
        if status not in lifecycle:
            issues.append({"code": "invalid_status", "detail": f"row {index + 2}: {status}"})
        allowed = {str(value) for value in targets[target_name].get("allowed_values", [])}
        for column in ("proposed_label", "final_label"):
            value = row[column]
            if pd.notna(value) and str(value).strip() and str(value).strip().removesuffix(".0") not in allowed:
                issues.append(
                    {
                        "code": "invalid_label",
                        "detail": f"row {index + 2}: {column}={value} is not allowed for {target_name}",
                    }
                )
        if status == "approved":
            if pd.isna(row["final_label"]) or not str(row["final_label"]).strip():
                issues.append({"code": "approved_without_final_label", "detail": f"row {index + 2}"})
            if pd.isna(row["human_reviewer_role"]) or not str(row["human_reviewer_role"]).strip():
                issues.append({"code": "approved_without_reviewer", "detail": f"row {index + 2}"})
    return issues


def validate_approval_register(frame: pd.DataFrame) -> list[dict[str, str]]:
    definitions = labeling_config().get("targets", {})
    required = {
        "target_name",
        "label_version",
        "approval_status",
        "approval_scope",
        "approved_by_role",
        "approved_at",
        "production_approved",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        return [{"code": "missing_approval_columns", "detail": ", ".join(missing)}]

    issues: list[dict[str, str]] = []
    if set(frame["target_name"]) != set(definitions):
        issues.append({"code": "approval_target_mismatch", "detail": "Approval register must contain every configured target once"})
    if frame["target_name"].duplicated().any():
        issues.append({"code": "duplicate_approval_target", "detail": "Each target may appear only once"})

    for index, row in frame.iterrows():
        target_name = str(row["target_name"]).strip()
        if target_name not in definitions:
            continue
        if str(row["label_version"]).strip() != definitions[target_name]["label_version"]:
            issues.append({"code": "approval_version_mismatch", "detail": f"row {index + 2}: {target_name}"})
        if str(row["approval_status"]).strip() != definitions[target_name]["approval_status"]:
            issues.append({"code": "approval_status_mismatch", "detail": f"row {index + 2}: {target_name}"})
        production_value = str(row["production_approved"]).strip().lower()
        if row["approval_status"] == "approved_for_prototype" and production_value in {"true", "1", "yes"}:
            issues.append({"code": "prototype_marked_as_production", "detail": f"row {index + 2}: {target_name}"})
    return issues
