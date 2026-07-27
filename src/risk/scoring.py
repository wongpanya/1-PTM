from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.utils.config import load_yaml


def _is_missing(value) -> bool:
    return value is None or value == "" or str(value).lower() in {"nan", "nat", "none"}


def score_row(row: dict, config_path: str = "config/risk_rules.yaml", config: dict[str, Any] | None = None) -> dict:
    config = config or load_yaml(config_path)["risk_score"]
    score = 0
    components = []
    for name, rule in config["components"].items():
        triggered = _evaluate_rule(row, rule)
        component_score = int(rule["weight"]) if triggered else 0
        if triggered:
            score += component_score
        components.append(
            {
                "component": name,
                "triggered": triggered,
                "score": component_score,
                "weight": int(rule["weight"]),
                "explanation_th": rule["explanation_th"],
            }
        )
    bounded_score = min(score, int(config["max_score"]))
    return {
        "risk_score": bounded_score,
        "risk_level": risk_level(bounded_score, config),
        "components": components,
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "rule_version": config["rule_version"],
        "limitations_th": config.get("limitations_th", []),
        "expert_approval_status": config.get("expert_approval_status", "unknown"),
    }


def score_dataframe(df: pd.DataFrame, config_path: str = "config/risk_rules.yaml") -> pd.DataFrame:
    rows = []
    config = load_yaml(config_path)["risk_score"]
    for _, record in df.iterrows():
        result = score_row(record.to_dict(), config_path, config)
        triggered = [component["component"] for component in result["components"] if component["triggered"]]
        rows.append(
            {
                "odos_uid": record.get("odos_uid"),
                "cohort": record.get("cohort"),
                "province": record.get("province"),
                "current_country": record.get("current_country"),
                "current_field_group": record.get("current_field_group"),
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "triggered_components": ", ".join(triggered),
                "rule_version": result["rule_version"],
                "calculated_at": result["calculated_at"],
            }
        )
    return pd.DataFrame(rows)


def risk_level(score: int, config: dict[str, Any] | None = None) -> str:
    config = config or load_yaml("config/risk_rules.yaml")["risk_score"]
    for level_name, threshold in config["levels"].items():
        if int(threshold["min"]) <= score <= int(threshold["max"]):
            return threshold["label_th"]
    return "High"


def graduation_status(row: dict, config_path: str = "config/risk_rules.yaml", config: dict[str, Any] | None = None) -> dict:
    config = config or load_yaml(config_path)["graduation_success"]
    for name, rule in config["statuses"].items():
        if rule.get("condition") == "fallback":
            continue
        if _evaluate_rule(row, rule):
            return {
                "graduation_status": name,
                "graduation_status_label": rule["label_th"],
                "rule_version": config["rule_version"],
                "explanation_th": _graduation_explanation(name),
            }
    fallback = config["statuses"]["unknown"]
    return {
        "graduation_status": "unknown",
        "graduation_status_label": fallback["label_th"],
        "rule_version": config["rule_version"],
        "explanation_th": _graduation_explanation("unknown"),
    }


def graduation_dataframe(df: pd.DataFrame, config_path: str = "config/risk_rules.yaml") -> pd.DataFrame:
    rows = []
    config = load_yaml(config_path)["graduation_success"]
    for _, record in df.iterrows():
        result = graduation_status(record.to_dict(), config_path, config)
        rows.append(
            {
                "odos_uid": record.get("odos_uid"),
                "cohort": record.get("cohort"),
                "province": record.get("province"),
                "current_field_group": record.get("current_field_group"),
                **result,
            }
        )
    return pd.DataFrame(rows)


def _graduation_explanation(status: str) -> str:
    explanations = {
        "on_time": "สำเร็จการศึกษาและระยะเวลาศึกษาไม่เกินเกณฑ์ Prototype",
        "delayed": "สำเร็จการศึกษาแต่ระยะเวลาศึกษาเกินเกณฑ์ Prototype",
        "studying": "สถานะโครงการระบุว่าอยู่ระหว่างศึกษา",
        "over_duration_risk": "อยู่ในกลุ่มเสี่ยงด้านสถานะทุนตามตัวแปรเป้าหมาย Phase 4",
        "exited": "สถานะโครงการมีข้อความที่สื่อถึงลาออก พ้นสภาพ หรือสละสิทธิ์",
        "unknown": "ข้อมูลยังไม่พอสำหรับจำแนกสถานะด้วยกฎ Prototype",
    }
    return explanations[status]


def _evaluate_rule(row: dict, rule: dict[str, Any]) -> bool:
    if "positive_when_all" in rule:
        return all(_evaluate_condition(row, condition) for condition in rule["positive_when_all"])
    if "condition_any" in rule:
        return any(_evaluate_condition(row, condition) for condition in rule["condition_any"])
    condition = rule.get("positive_when") or rule.get("condition")
    if " and " in str(condition):
        return all(_evaluate_condition(row, part.strip()) for part in str(condition).split(" and "))
    return _evaluate_condition(row, str(condition))


def _evaluate_condition(row: dict, condition: str) -> bool:
    condition = condition.strip()
    if condition == "fallback":
        return True
    if " is not null" in condition:
        field = condition.split(" is not null")[0].strip()
        return not _is_missing(row.get(field))
    if " is null" in condition:
        field = condition.split(" is null")[0].strip()
        return _is_missing(row.get(field))
    if " contains " in condition:
        field, expected = condition.split(" contains ", 1)
        value = row.get(field.strip())
        return not _is_missing(value) and expected.strip() in str(value)
    for operator in [">=", "<=", "!=", ">", "<", "=="]:
        if f" {operator} " in condition:
            field, expected = condition.split(f" {operator} ", 1)
            return _compare(row.get(field.strip()), expected.strip().strip('"'), operator)
    return False


def _compare(value, expected: str, operator: str) -> bool:
    if operator == "!=":
        return str(value) != expected and not _is_missing(value)
    if operator == "==":
        return str(value) == expected
    try:
        left = float(value)
        right = float(expected)
    except (TypeError, ValueError):
        return False
    if operator == ">=":
        return left >= right
    if operator == "<=":
        return left <= right
    if operator == ">":
        return left > right
    if operator == "<":
        return left < right
    return False
