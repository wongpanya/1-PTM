from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any
from uuid import uuid4

import pandas as pd

from src.governance.audit import append_audit_event
from src.governance.privacy import (
    assert_no_pii_text,
    forbidden_columns_present,
    role_can,
)
from src.ingestion.database import get_connection
from src.risk.ml_models import (
    BASE_MODEL_KEYS,
    MODEL_SPECS,
    TARGET_SPECS,
    _estimator,
    _feature_importance,
    _sklearn,
    available_model_features,
    train_model_suite,
)
from src.utils.config import load_yaml


CASE_REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,40}$")
INDIVIDUAL_CONFIG_PATH = "config/individual_prediction.yaml"
PREDICTION_TABLES = {"model_registry", "prediction_cases", "prediction_reviews"}


@dataclass(frozen=True)
class PrototypeModelArtifact:
    target: str
    model_key: str
    model_version: str
    threshold: float
    features: list[str]
    pipeline: Any
    validation_metrics: dict[str, float | int | str]
    feature_importance: pd.DataFrame
    category_values: dict[str, set[str]]
    trained_at: str


def individual_prediction_config() -> dict[str, Any]:
    return load_yaml(INDIVIDUAL_CONFIG_PATH)


def approved_individual_targets() -> list[str]:
    return list(individual_prediction_config()["approved_targets"])


def import_template_columns() -> list[str]:
    return list(individual_prediction_config()["required_columns"])


def ensure_prediction_tables() -> None:
    schema = load_yaml("config/database_schema.yaml")["tables"]
    with closing(get_connection()) as conn, conn:
        for table_name in PREDICTION_TABLES:
            definition = schema[table_name]
            primary_key = definition.get("primary_key")
            column_defs = []
            for name, column_type in definition["columns"].items():
                suffix = " PRIMARY KEY" if name == primary_key else ""
                column_defs.append(f'"{name}" {column_type}{suffix}')
            conn.execute(
                f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(column_defs)})'
            )


def validate_individual_import(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    config = individual_prediction_config()
    required = import_template_columns()
    issues: list[dict[str, str]] = []
    cleaned = frame.copy()

    missing_columns = [column for column in required if column not in cleaned.columns]
    unexpected_columns = [column for column in cleaned.columns if column not in required]
    if missing_columns:
        issues.append(
            {"severity": "error", "code": "missing_columns", "detail": ", ".join(missing_columns)}
        )
    if unexpected_columns:
        issues.append(
            {
                "severity": "error",
                "code": "unexpected_columns",
                "detail": ", ".join(unexpected_columns),
            }
        )
    forbidden = forbidden_columns_present(cleaned.columns)
    if forbidden:
        issues.append(
            {"severity": "error", "code": "forbidden_columns", "detail": ", ".join(forbidden)}
        )
    target_columns = [column for column in cleaned.columns if column.startswith("target_")]
    if target_columns:
        issues.append(
            {"severity": "error", "code": "target_columns", "detail": ", ".join(target_columns)}
        )
    if len(cleaned) == 0:
        issues.append({"severity": "error", "code": "empty_file", "detail": "CSV ไม่มีข้อมูล"})
    if len(cleaned) > int(config["maximum_rows_per_import"]):
        issues.append(
            {
                "severity": "error",
                "code": "too_many_rows",
                "detail": f"รับได้ไม่เกิน {config['maximum_rows_per_import']} รายการต่อครั้ง",
            }
        )
    try:
        assert_no_pii_text(cleaned.to_csv(index=False))
    except ValueError as exc:
        issues.append({"severity": "error", "code": "pii_detected", "detail": str(exc)})

    if missing_columns:
        return cleaned, issues

    cleaned = cleaned[required].copy()
    cleaned["case_reference"] = cleaned["case_reference"].fillna("").astype(str).str.strip()
    invalid_refs = cleaned[
        ~cleaned["case_reference"].map(lambda value: bool(CASE_REFERENCE_PATTERN.fullmatch(value)))
    ]
    if not invalid_refs.empty:
        issues.append(
            {
                "severity": "error",
                "code": "invalid_case_reference",
                "detail": "case_reference ต้องเป็น A-Z, a-z, 0-9, _ หรือ - ความยาว 3-40 ตัวอักษร",
            }
        )
    if cleaned["case_reference"].duplicated().any():
        issues.append(
            {"severity": "error", "code": "duplicate_case_reference", "detail": "case_reference ซ้ำ"}
        )

    approved_purposes = set(config["approved_purposes"])
    invalid_purposes = sorted(
        set(cleaned["purpose_code"].dropna().astype(str)).difference(approved_purposes)
    )
    if invalid_purposes:
        issues.append(
            {
                "severity": "error",
                "code": "invalid_purpose",
                "detail": ", ".join(invalid_purposes),
            }
        )

    for column in ["cohort", "gpa_numeric", "study_duration_years"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    _append_range_issue(issues, cleaned, "cohort", 1, 20)
    _append_range_issue(issues, cleaned, "gpa_numeric", 0, 4)
    _append_range_issue(issues, cleaned, "study_duration_years", 0, 20)

    feature_columns = [column for column in required if column not in {"case_reference", "purpose_code"}]
    cleaned["feature_completeness"] = (
        cleaned[feature_columns].notna().mean(axis=1).mul(100).round(1)
    )
    low_completeness = int((cleaned["feature_completeness"] < 75).sum())
    if low_completeness:
        issues.append(
            {
                "severity": "warning",
                "code": "low_completeness",
                "detail": f"{low_completeness} รายการมี Features ครบถ้วนน้อยกว่า 75%",
            }
        )
    return cleaned, issues


def fit_prototype_artifact(
    training_data: pd.DataFrame,
    target: str,
    random_state: int = 42,
) -> PrototypeModelArtifact:
    config = individual_prediction_config()
    if target not in config["approved_targets"]:
        raise PermissionError(f"Target is not approved for individual prototype: {target}")
    approval = config["approved_targets"][target]
    model_key = str(approval["model_key"])
    features = available_model_features(training_data, target)
    validation_result = train_model_suite(
        training_data,
        target=target,
        selected_models=[model_key],
        random_state=random_state,
    )[0]

    working = training_data[[*features, target]].copy()
    working[target] = pd.to_numeric(working[target], errors="coerce")
    working = working.dropna(subset=[target])
    working[target] = working[target].astype(int)
    numeric_features = [
        feature for feature in features if pd.api.types.is_numeric_dtype(working[feature])
    ]
    categorical_features = [feature for feature in features if feature not in numeric_features]
    sklearn = _sklearn()
    preprocessor = sklearn["ColumnTransformer"](
        transformers=[
            (
                "categorical",
                sklearn["Pipeline"](
                    steps=[
                        ("imputer", sklearn["SimpleImputer"](strategy="most_frequent")),
                        (
                            "onehot",
                            sklearn["OneHotEncoder"](
                                handle_unknown="ignore",
                                sparse_output=False,
                            ),
                        ),
                    ]
                ),
                categorical_features,
            ),
            (
                "numeric",
                sklearn["Pipeline"](
                    steps=[
                        ("imputer", sklearn["SimpleImputer"](strategy="median")),
                        ("scaler", sklearn["StandardScaler"]()),
                    ]
                ),
                numeric_features,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    estimator = _estimator(model_key, random_state, sklearn, BASE_MODEL_KEYS)
    pipeline = sklearn["Pipeline"](
        steps=[("preprocess", preprocessor), ("model", estimator)]
    )
    pipeline.fit(working[features], working[target])
    category_values = {
        feature: set(working[feature].dropna().astype(str))
        for feature in categorical_features
    }
    artifact = PrototypeModelArtifact(
        target=target,
        model_key=model_key,
        model_version=str(approval["model_version"]),
        threshold=float(approval["threshold"]),
        features=features,
        pipeline=pipeline,
        validation_metrics=validation_result.metrics,
        feature_importance=_feature_importance(pipeline, model_key),
        category_values=category_values,
        trained_at=datetime.now(timezone.utc).isoformat(),
    )
    register_model_artifact(artifact, str(approval["approver_role"]))
    return artifact


def predict_new_cases(
    artifact: PrototypeModelArtifact,
    cleaned_import: pd.DataFrame,
) -> pd.DataFrame:
    missing = [feature for feature in artifact.features if feature not in cleaned_import.columns]
    if missing:
        raise ValueError(f"Missing model features: {', '.join(missing)}")
    probabilities = artifact.pipeline.predict_proba(cleaned_import[artifact.features])[:, 1]
    spec = TARGET_SPECS[artifact.target]
    rows = []
    for position, (_, record) in enumerate(cleaned_import.iterrows()):
        probability = float(probabilities[position])
        band = _tendency_band(probability)
        direction_text = "ความเสี่ยง" if spec["direction"] == "risk" else "ผลลัพธ์เชิงบวก"
        warnings = _case_data_warnings(record, artifact)
        rows.append(
            {
                "case_id": str(uuid4()),
                "case_reference": str(record["case_reference"]),
                "purpose_code": str(record["purpose_code"]),
                "target": artifact.target,
                "target_label": str(spec["label"]),
                "model_key": artifact.model_key,
                "model_label": MODEL_SPECS[artifact.model_key]["label"],
                "model_version": artifact.model_version,
                "probability": round(probability, 6),
                "threshold": artifact.threshold,
                "tendency_band": band,
                "interpretation": f"แนวโน้ม{direction_text}{band}",
                "data_quality_score": float(record.get("feature_completeness", 100.0)),
                "data_warnings": warnings,
                "features": {
                    feature: _json_value(record.get(feature))
                    for feature in artifact.features
                },
                "status": "pending_review",
            }
        )
    return pd.DataFrame(rows)


def register_model_artifact(artifact: PrototypeModelArtifact, approved_by_role: str) -> None:
    ensure_prediction_tables()
    config = individual_prediction_config()["approved_targets"][artifact.target]
    with closing(get_connection()) as conn, conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO model_registry
            (model_version, target, model_key, status, threshold, metrics_json,
             approved_by_role, registered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact.model_version,
                artifact.target,
                artifact.model_key,
                config["status"],
                artifact.threshold,
                json.dumps(artifact.validation_metrics, ensure_ascii=False),
                approved_by_role,
                artifact.trained_at,
            ),
        )


def create_prediction_cases(predictions: pd.DataFrame, actor: str, role: str) -> list[str]:
    if not role_can(role, "can_predict_individual"):
        raise PermissionError(f"Role cannot create individual predictions: {role}")
    _validate_actor(actor)
    ensure_prediction_tables()
    created_at = datetime.now(timezone.utc).isoformat()
    created_ids = []
    with closing(get_connection()) as conn, conn:
        for _, row in predictions.iterrows():
            existing = conn.execute(
                """
                SELECT case_id FROM prediction_cases
                WHERE case_reference = ? AND target = ?
                AND status NOT IN ('closed_no_action', 'cancelled')
                """,
                (row["case_reference"], row["target"]),
            ).fetchone()
            if existing:
                raise ValueError(
                    f"Open case already exists: {row['case_reference']} / {row['target']}"
                )
            conn.execute(
                """
                INSERT INTO prediction_cases
                (case_id, case_reference, target, purpose_code, model_key, model_version,
                 probability, threshold, tendency_band, interpretation, data_quality_score,
                 data_warnings_json, features_json, status, created_by, created_role, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["case_id"],
                    row["case_reference"],
                    row["target"],
                    row["purpose_code"],
                    row["model_key"],
                    row["model_version"],
                    float(row["probability"]),
                    float(row["threshold"]),
                    row["tendency_band"],
                    row["interpretation"],
                    float(row["data_quality_score"]),
                    json.dumps(row["data_warnings"], ensure_ascii=False),
                    json.dumps(row["features"], ensure_ascii=False),
                    "pending_review",
                    actor,
                    role,
                    created_at,
                ),
            )
            _insert_db_audit(
                conn,
                "individual_prediction_created",
                actor,
                {
                    "case_id": row["case_id"],
                    "case_reference": row["case_reference"],
                    "target": row["target"],
                    "model_version": row["model_version"],
                },
            )
            created_ids.append(str(row["case_id"]))
    append_audit_event(
        "individual_prediction_batch_created",
        {"actor": actor, "role": role, "case_count": len(created_ids)},
    )
    return created_ids


def list_prediction_cases(role: str, actor: str) -> pd.DataFrame:
    ensure_prediction_tables()
    _validate_actor(actor)
    columns = """
        case_id, case_reference, target, purpose_code, model_version, probability,
        threshold, tendency_band, interpretation, data_quality_score, status,
        created_by, created_role, created_at, reviewed_by, reviewed_at,
        review_decision, review_reason, approved_by, approved_at,
        approval_decision, action_plan
    """
    params: tuple[Any, ...] = ()
    where = ""
    if role == "CaseOfficer":
        where = "WHERE created_by = ?"
        params = (actor,)
    elif role == "HumanReviewer":
        where = "WHERE status IN ('pending_review', 'needs_information')"
    elif role == "DomainApprover":
        where = "WHERE status IN ('pending_approval', 'approved_for_support', 'closed_no_action')"
    elif role not in {"DPOAuditor", "Admin"}:
        return pd.DataFrame()
    with closing(get_connection()) as conn, conn:
        return pd.read_sql_query(
            f"SELECT {columns} FROM prediction_cases {where} ORDER BY created_at DESC",
            conn,
            params=params,
        )


def get_prediction_case(case_id: str, role: str, actor: str) -> dict[str, Any]:
    cases = list_prediction_cases(role, actor)
    match = cases[cases["case_id"] == case_id] if not cases.empty else pd.DataFrame()
    if match.empty:
        raise PermissionError("Case is not available for this role or actor")
    with closing(get_connection()) as conn, conn:
        row = conn.execute(
            "SELECT * FROM prediction_cases WHERE case_id = ?",
            (case_id,),
        ).fetchone()
    output = dict(row)
    output["features"] = json.loads(output.get("features_json") or "{}")
    output["data_warnings"] = json.loads(output.get("data_warnings_json") or "[]")
    return output


def submit_human_review(
    case_id: str,
    decision: str,
    reason: str,
    actor: str,
    role: str,
) -> str:
    if not role_can(role, "can_review_individual"):
        raise PermissionError(f"Role cannot review individual predictions: {role}")
    _validate_actor(actor)
    config = individual_prediction_config()
    if decision not in config["review_decisions"]:
        raise ValueError(f"Unknown review decision: {decision}")
    if len(reason.strip()) < 10:
        raise ValueError("Review reason must contain at least 10 characters")
    ensure_prediction_tables()
    reviewed_at = datetime.now(timezone.utc).isoformat()
    with closing(get_connection()) as conn, conn:
        case = conn.execute(
            "SELECT * FROM prediction_cases WHERE case_id = ?",
            (case_id,),
        ).fetchone()
        if not case or case["status"] not in {"pending_review", "needs_information"}:
            raise ValueError("Case is not ready for human review")
        if case["created_by"] == actor:
            raise PermissionError("Case creator cannot review the same case")
        next_status = "needs_information" if decision == "needs_information" else "pending_approval"
        conn.execute(
            """
            UPDATE prediction_cases
            SET status = ?, reviewed_by = ?, reviewed_at = ?,
                review_decision = ?, review_reason = ?
            WHERE case_id = ?
            """,
            (next_status, actor, reviewed_at, decision, reason.strip(), case_id),
        )
        _insert_review(conn, case_id, "human_review", decision, reason, actor, role, reviewed_at)
        _insert_db_audit(
            conn,
            "individual_prediction_reviewed",
            actor,
            {"case_id": case_id, "decision": decision, "next_status": next_status},
        )
    return next_status


def submit_domain_approval(
    case_id: str,
    decision: str,
    action_plan: str,
    actor: str,
    role: str,
) -> str:
    if not role_can(role, "can_approve_individual"):
        raise PermissionError(f"Role cannot approve individual predictions: {role}")
    _validate_actor(actor)
    config = individual_prediction_config()
    if decision not in config["approval_decisions"]:
        raise ValueError(f"Unknown approval decision: {decision}")
    if len(action_plan.strip()) < 10:
        raise ValueError("Action plan or approval reason must contain at least 10 characters")
    ensure_prediction_tables()
    approved_at = datetime.now(timezone.utc).isoformat()
    with closing(get_connection()) as conn, conn:
        case = conn.execute(
            "SELECT * FROM prediction_cases WHERE case_id = ?",
            (case_id,),
        ).fetchone()
        if not case or case["status"] != "pending_approval":
            raise ValueError("Case is not ready for domain approval")
        if actor in {case["created_by"], case["reviewed_by"]}:
            raise PermissionError("Creator, reviewer, and approver must be different actors")
        next_status = {
            "approve_support": "approved_for_support",
            "return_for_review": "pending_review",
            "close_no_action": "closed_no_action",
        }[decision]
        conn.execute(
            """
            UPDATE prediction_cases
            SET status = ?, approved_by = ?, approved_at = ?,
                approval_decision = ?, action_plan = ?
            WHERE case_id = ?
            """,
            (next_status, actor, approved_at, decision, action_plan.strip(), case_id),
        )
        _insert_review(
            conn,
            case_id,
            "domain_approval",
            decision,
            action_plan,
            actor,
            role,
            approved_at,
        )
        _insert_db_audit(
            conn,
            "individual_prediction_approved",
            actor,
            {"case_id": case_id, "decision": decision, "next_status": next_status},
        )
    return next_status


def prediction_review_history(case_id: str) -> pd.DataFrame:
    ensure_prediction_tables()
    with closing(get_connection()) as conn, conn:
        return pd.read_sql_query(
            """
            SELECT stage, decision, reason, actor, actor_role, created_at
            FROM prediction_reviews
            WHERE case_id = ?
            ORDER BY created_at
            """,
            conn,
            params=(case_id,),
        )


def _append_range_issue(
    issues: list[dict[str, str]],
    frame: pd.DataFrame,
    column: str,
    minimum: float,
    maximum: float,
) -> None:
    invalid = frame[column].notna() & ~frame[column].between(minimum, maximum)
    if invalid.any():
        issues.append(
            {
                "severity": "error",
                "code": f"invalid_{column}",
                "detail": f"{column} ต้องอยู่ระหว่าง {minimum:g}-{maximum:g}",
            }
        )


def _case_data_warnings(
    record: pd.Series,
    artifact: PrototypeModelArtifact,
) -> list[str]:
    warnings = []
    missing = [feature for feature in artifact.features if pd.isna(record.get(feature))]
    if missing:
        warnings.append(f"ข้อมูลขาด: {', '.join(missing)}")
    for feature, known_values in artifact.category_values.items():
        value = record.get(feature)
        if pd.notna(value) and str(value) not in known_values:
            warnings.append(f"{feature} ไม่เคยปรากฏในข้อมูลฝึก")
    return warnings


def _tendency_band(probability: float) -> str:
    if probability < 0.3:
        return "ต่ำ"
    if probability < 0.6:
        return "ปานกลาง"
    return "สูง"


def _validate_actor(actor: str) -> None:
    if not CASE_REFERENCE_PATTERN.fullmatch(actor.strip()):
        raise ValueError("Actor ID must be 3-40 characters using A-Z, a-z, 0-9, _ or -")


def _json_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def _insert_review(
    conn,
    case_id: str,
    stage: str,
    decision: str,
    reason: str,
    actor: str,
    role: str,
    created_at: str,
) -> None:
    conn.execute(
        """
        INSERT INTO prediction_reviews
        (review_id, case_id, stage, decision, reason, actor, actor_role, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (str(uuid4()), case_id, stage, decision, reason.strip(), actor, role, created_at),
    )


def _insert_db_audit(conn, event_type: str, actor: str, detail: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO audit_logs
        (audit_id, event_type, event_time, actor, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(uuid4()),
            event_type,
            datetime.now(timezone.utc).isoformat(),
            actor,
            json.dumps(detail, ensure_ascii=False),
        ),
    )
