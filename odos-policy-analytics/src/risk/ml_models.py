from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.analytics.metrics import metric_definitions


DEFAULT_TARGET = "target_scholarship_risk"
TARGET_SPECS: dict[str, dict[str, Any]] = {
    "target_scholarship_risk": {
        "label": "ความเสี่ยงสถานะทุน",
        "question": "ใครบ้างมีแนวโน้มเข้าสู่สถานะทุนที่ควรติดตาม",
        "positive_label": "มีความเสี่ยง",
        "direction": "risk",
        "policy_goal": "ลดจำนวนผู้รับทุนที่เข้าสู่สถานะเสี่ยงด้วยการช่วยเหลือก่อนเกิดปัญหา",
        "policy_actions": [
            "จัดระบบติดตามเชิงรุกสำหรับกลุ่มที่มีแนวโน้มสูง",
            "ทบทวนปัจจัยด้านผลการเรียนและระยะเวลาศึกษาในระดับกลุ่ม",
            "กำหนดช่องทางส่งต่อให้ผู้เชี่ยวชาญพิจารณาก่อนดำเนินการ",
        ],
        "monitoring_kpis": ["อัตราความเสี่ยงสถานะทุน", "อัตราการติดตามสำเร็จ", "อัตราการคลี่คลายสถานะเสี่ยง"],
    },
    "target_graduation_success": {
        "label": "โอกาสสำเร็จการศึกษา",
        "question": "ใครบ้างมีแนวโน้มสำเร็จการศึกษา",
        "positive_label": "สำเร็จการศึกษา",
        "direction": "opportunity",
        "policy_goal": "เพิ่มโอกาสสำเร็จการศึกษาด้วยการสนับสนุนที่ตรงกับกลุ่มเป้าหมาย",
        "policy_actions": [
            "วางแผนให้คำปรึกษาและสนับสนุนการเรียนในกลุ่มที่มีแนวโน้มสำเร็จต่ำ",
            "ศึกษารูปแบบของกลุ่มที่มีแนวโน้มสำเร็จสูงเพื่อนำมาต่อยอด",
            "ติดตามความก้าวหน้าเป็นรอบโดยไม่ใช้ผลโมเดลตัดสินรายบุคคล",
        ],
        "monitoring_kpis": ["อัตราสำเร็จการศึกษา", "ระยะเวลาศึกษาเฉลี่ย", "อัตราการคงอยู่ในโครงการ"],
    },
    "target_tracking_risk": {
        "label": "ความเสี่ยงติดตามข้อมูลไม่ได้",
        "question": "ใครบ้างมีแนวโน้มขาดการติดตามข้อมูล",
        "positive_label": "ติดตามข้อมูลไม่ได้",
        "direction": "risk",
        "policy_goal": "ลดช่องว่างการติดตามและเพิ่มความต่อเนื่องของข้อมูลผลลัพธ์",
        "policy_actions": [
            "จัดลำดับกลุ่มสำหรับการปรับปรุงช่องทางติดตามข้อมูล",
            "ทบทวนรอบเวลาและเจ้าของข้อมูลในพื้นที่ที่มีแนวโน้มสูง",
            "เพิ่มช่องทางยืนยันสถานะโดยคำนึงถึงความเป็นส่วนตัว",
        ],
        "monitoring_kpis": ["อัตราติดตามข้อมูลไม่ได้", "ระยะเวลาปิดเคสติดตาม", "ความครบถ้วนของข้อมูลติดตาม"],
    },
    "target_employment_ready": {
        "label": "ความพร้อมด้านการมีงานทำ",
        "question": "ใครบ้างมีแนวโน้มมีงานทำหรือมีผลลัพธ์การจ้างงาน",
        "positive_label": "มีงานทำหรือพร้อมจ้างงาน",
        "direction": "opportunity",
        "policy_goal": "เพิ่มความพร้อมและผลลัพธ์ด้านการจ้างงานหลังสำเร็จการศึกษา",
        "policy_actions": [
            "จัดกิจกรรมเตรียมทักษะอาชีพสำหรับกลุ่มที่มีแนวโน้มต่ำ",
            "เชื่อมโยงนายจ้างและโอกาสฝึกงานตามสาขาและพื้นที่",
            "ติดตามผลการจ้างงานและรายได้แยกเป็น target ในอนาคต",
        ],
        "monitoring_kpis": ["อัตรามีงานทำ", "ระยะเวลาหางาน", "อัตราเข้าร่วมกิจกรรมเตรียมอาชีพ"],
    },
    "target_field_mismatch": {
        "label": "ความเสี่ยงทำงานไม่ตรงสาขา",
        "question": "ใครบ้างมีแนวโน้มทำงานไม่สอดคล้องกับสาขาที่เรียน",
        "positive_label": "งานไม่ตรงสาขา",
        "direction": "risk",
        "policy_goal": "เพิ่มความสอดคล้องระหว่างสาขาทุน ทักษะ และโอกาสการทำงาน",
        "policy_actions": [
            "ทบทวนกลุ่มสาขาที่มีแนวโน้มไม่ตรงสาขาสูง",
            "เชื่อมข้อมูลความต้องการกำลังคนภายนอกก่อนปรับสาขาทุน",
            "ออกแบบการพัฒนาทักษะเสริมและการจับคู่งานตามสาขา",
        ],
        "monitoring_kpis": ["อัตรางานไม่ตรงสาขา", "อัตราจับคู่งานตามสาขา", "ความต้องการกำลังคนรายสาขา"],
    },
    "target_local_mismatch": {
        "label": "ความเสี่ยงงานไม่สอดคล้องกับท้องถิ่น",
        "question": "ใครบ้างมีแนวโน้มทำงานไม่สอดคล้องกับพื้นที่หรือท้องถิ่น",
        "positive_label": "งานไม่สอดคล้องกับท้องถิ่น",
        "direction": "risk",
        "policy_goal": "เพิ่มความสอดคล้องระหว่างการจัดสรรทุนกับความต้องการของพื้นที่",
        "policy_actions": [
            "ทบทวนพื้นที่ที่มีแนวโน้มความไม่สอดคล้องสูง",
            "เชื่อมข้อมูลความต้องการแรงงานและแผนพัฒนาจังหวัด",
            "ประเมินมาตรการจูงใจและเครือข่ายงานในพื้นที่",
        ],
        "monitoring_kpis": ["อัตรางานไม่สอดคล้องพื้นที่", "อัตราทำงานในพื้นที่เป้าหมาย", "จำนวนตำแหน่งงานที่เชื่อมโยงได้"],
    },
}
DEFAULT_FEATURES = [
    "cohort",
    "sex",
    "region",
    "province",
    "current_country",
    "current_field_group",
    "gpa_numeric",
    "study_duration_years",
]

KEY_FORECAST_OBJECTIVES: dict[str, dict[str, Any]] = {
    "scholarship_risk": {
        "label": "Scholarship Risk Forecast",
        "framework_item": "#10 Scholarship Risk",
        "target": "target_scholarship_risk",
        "status": "model_ready",
        "description": "Predict whether a recipient is in a prototype scholarship-risk status.",
        "caveat": "Use as an early-warning review signal, not an automated funding decision.",
        "supporting_targets": ["target_tracking_risk"],
    },
    "graduation_success": {
        "label": "Graduation Success Forecast",
        "framework_item": "#6 Graduation Success",
        "target": "target_graduation_success",
        "status": "model_ready",
        "description": "Predict likelihood of successful graduation from available no-PII features.",
        "caveat": "Current labels are historical prototype outcomes, not live longitudinal progression.",
        "supporting_targets": [],
    },
    "employment_income": {
        "label": "Employment & Income Forecast",
        "framework_item": "#4 Employment & Income",
        "target": "target_employment_ready",
        "status": "prototype_proxy",
        "description": "Predict employment-ready status as the currently available proxy for employment outcome.",
        "caveat": "Income forecasting still needs a separate regression target and verified income bands.",
        "supporting_targets": [],
    },
    "future_scholarship_fields": {
        "label": "Future Scholarship Fields",
        "framework_item": "#2 Future Scholarship Fields",
        "target": "target_field_mismatch",
        "status": "prototype_proxy",
        "description": "Use field-job mismatch as a proxy signal for fields that may need policy review.",
        "caveat": "Needs external workforce demand data before it can recommend future scholarship fields.",
        "supporting_targets": [],
    },
    "area_based_allocation": {
        "label": "Area-based Allocation",
        "framework_item": "#7 Area-based Allocation",
        "target": "target_local_mismatch",
        "status": "prototype_proxy",
        "description": "Use local-fit mismatch as a proxy for area-based allocation review.",
        "caveat": "Best interpreted at aggregate province/region level with minimum group-size controls.",
        "supporting_targets": [],
    },
    "brain_drain_risk": {
        "label": "Brain Drain Risk",
        "framework_item": "#5 Brain Drain Risk",
        "target": None,
        "status": "data_gap",
        "description": "Forecast the risk that scholarship recipients do not return or contribute domestically.",
        "caveat": "Needs verified return dates, residence and work location, overseas employment, and follow-up periods.",
        "supporting_targets": ["target_tracking_risk", "target_local_mismatch"],
    },
    "workforce_demand": {
        "label": "Future Workforce Demand",
        "framework_item": "#1 Future Workforce Demand",
        "target": None,
        "status": "data_gap",
        "description": "Forecast future labor demand by field, area, and time period.",
        "caveat": "Needs labor market demand, shortage occupations, industry growth, and time-series data.",
        "supporting_targets": [],
    },
    "roi_sroi": {
        "label": "ROI & SROI Forecast",
        "framework_item": "#3 ROI & SROI Forecast",
        "target": None,
        "status": "data_gap",
        "description": "Forecast economic and social return from scholarship investment.",
        "caveat": "Needs cost, tuition, living expense, exchange-rate, social value proxy, and weighting data.",
        "supporting_targets": [],
    },
    "future_leadership": {
        "label": "Future Leadership",
        "framework_item": "#8 Future Leadership",
        "target": None,
        "status": "data_gap",
        "description": "Forecast future leadership or high-impact contribution potential.",
        "caveat": "Needs leadership roles, research output, patents, awards, and organization-level outcomes.",
        "supporting_targets": [],
    },
    "national_impact": {
        "label": "National Impact Forecast",
        "framework_item": "#9 National Impact Forecast",
        "target": None,
        "status": "data_gap",
        "description": "Forecast contribution to GDP, innovation, productivity, and national development.",
        "caveat": "Needs GDP linkage, sector contribution, patents, startups, productivity, and public-impact data.",
        "supporting_targets": [],
    },
}

MODEL_SPECS: dict[str, dict[str, str]] = {
    "logistic_regression": {
        "label": "Logistic Regression",
        "purpose": "Baseline model with interpretable directional coefficients.",
    },
    "decision_tree": {
        "label": "Decision Tree",
        "purpose": "Explainable rule-style model for policy review.",
    },
    "random_forest": {
        "label": "Random Forest",
        "purpose": "Ensemble model for non-linear patterns and robust feature importance.",
    },
    "naive_bayes": {
        "label": "Naive Bayes",
        "purpose": "Probabilistic baseline that learns class likelihoods from encoded features.",
    },
    "calibrated_svm": {
        "label": "Calibrated SVM",
        "purpose": "Margin-based model with calibrated probabilities for voting.",
    },
    "vote_ensemble": {
        "label": "Vote Ensemble",
        "purpose": "Soft-voting ensemble that averages probability estimates from the five ML base models.",
    },
}

BASE_MODEL_KEYS = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "naive_bayes",
    "calibrated_svm",
]


@dataclass(frozen=True)
class ModelResult:
    key: str
    label: str
    purpose: str
    metrics: dict[str, float | int | str]
    confusion_matrix: pd.DataFrame
    feature_importance: pd.DataFrame
    validation_predictions: pd.DataFrame


def forecast_objectives() -> dict[str, dict[str, Any]]:
    return KEY_FORECAST_OBJECTIVES


def modelable_forecast_objectives() -> list[str]:
    return [
        key
        for key, objective in KEY_FORECAST_OBJECTIVES.items()
        if objective.get("target") and objective.get("status") in {"model_ready", "prototype_proxy"}
    ]


def forecast_objective_frame() -> pd.DataFrame:
    rows = []
    for key, objective in KEY_FORECAST_OBJECTIVES.items():
        rows.append(
            {
                "objective_key": key,
                "forecast_objective": objective["label"],
                "framework_item": objective["framework_item"],
                "target": objective.get("target") or "not_available",
                "status": objective["status"],
                "description": objective["description"],
                "caveat_or_data_gap": objective["caveat"],
            }
        )
    return pd.DataFrame(rows)


def available_target_columns(df: pd.DataFrame) -> list[str]:
    configured = metric_definitions().get("data_quality", {}).get("ml_target_fields", TARGET_SPECS)
    return [target for target in configured if target in df.columns and target in TARGET_SPECS]


def target_objective_links(target: str) -> list[dict[str, str]]:
    links = []
    for key, objective in KEY_FORECAST_OBJECTIVES.items():
        relation = None
        if objective.get("target") == target:
            relation = "direct"
        elif target in objective.get("supporting_targets", []):
            relation = "supporting"
        if relation:
            links.append(
                {
                    "objective_key": key,
                    "forecast_objective": objective["label"],
                    "framework_item": objective["framework_item"],
                    "relation": relation,
                    "status": objective["status"],
                }
            )
    return links


def prediction_overview(
    result: ModelResult,
    target: str,
    threshold: float = 0.5,
) -> dict[str, float | int | str]:
    predictions = result.validation_predictions
    if predictions.empty:
        return {
            "target": target,
            "records": 0,
            "average_probability": 0.0,
            "forecast_positive_rate": 0.0,
            "actual_positive_rate": 0.0,
            "forecast_actual_gap": 0.0,
            "high_tendency_rate": 0.0,
            "direction": str(TARGET_SPECS[target]["direction"]),
        }
    probability = pd.to_numeric(predictions["positive_probability"], errors="coerce").fillna(0.0)
    actual = pd.to_numeric(predictions["actual"], errors="coerce").fillna(0.0)
    return {
        "target": target,
        "records": int(len(predictions)),
        "average_probability": round(float(probability.mean() * 100), 2),
        "forecast_positive_rate": round(float((probability >= threshold).mean() * 100), 2),
        "actual_positive_rate": round(float(actual.mean() * 100), 2),
        "forecast_actual_gap": round(
            float(((probability >= threshold).mean() - actual.mean()) * 100),
            2,
        ),
        "high_tendency_rate": round(float((probability >= 0.6).mean() * 100), 2),
        "direction": str(TARGET_SPECS[target]["direction"]),
        "threshold": round(float(threshold), 2),
    }


def segment_prediction_summary(
    result: ModelResult,
    group_by: str,
    threshold: float = 0.5,
    minimum_group_size: int = 10,
) -> pd.DataFrame:
    predictions = result.validation_predictions
    if predictions.empty or group_by not in predictions.columns:
        return pd.DataFrame()

    working = predictions[[group_by, "actual", "positive_probability"]].copy()
    working[group_by] = working[group_by].fillna("ไม่ระบุ").astype(str)
    working["forecast_positive"] = (
        pd.to_numeric(working["positive_probability"], errors="coerce").fillna(0.0) >= threshold
    ).astype(int)
    summary = (
        working.groupby(group_by, dropna=False)
        .agg(
            records=("actual", "size"),
            average_probability=("positive_probability", "mean"),
            forecast_positive_rate=("forecast_positive", "mean"),
            actual_positive_rate=("actual", "mean"),
        )
        .reset_index()
    )
    summary = summary[summary["records"] >= minimum_group_size].copy()
    for column in ["average_probability", "forecast_positive_rate", "actual_positive_rate"]:
        summary[column] = (pd.to_numeric(summary[column], errors="coerce") * 100).round(2)
    return summary.sort_values(
        ["forecast_positive_rate", "records"],
        ascending=[False, False],
    ).reset_index(drop=True)


def policy_interpretation(
    result: ModelResult,
    target: str,
    threshold: float = 0.5,
) -> dict[str, Any]:
    overview = prediction_overview(result, target, threshold)
    spec = TARGET_SPECS[target]
    rate = float(overview["forecast_positive_rate"])
    actual_rate = float(overview["actual_positive_rate"])
    forecast_actual_gap = float(overview["forecast_actual_gap"])
    if spec["direction"] == "risk":
        signal = (
            f"โมเดลจัดให้ {rate:.1f}% ของ validation set มีแนวโน้ม “{spec['positive_label']}” "
            f"ที่เกณฑ์ {threshold:.2f}"
        )
        implication = "ควรใช้ผลระดับกลุ่มเพื่อค้นหาจุดที่ต้องเฝ้าระวังและออกแบบการช่วยเหลือเชิงป้องกัน"
    else:
        signal = (
            f"โมเดลจัดให้ {rate:.1f}% ของ validation set มีแนวโน้ม “{spec['positive_label']}” "
            f"ที่เกณฑ์ {threshold:.2f}"
        )
        implication = "ควรศึกษาทั้งกลุ่มที่มีแนวโน้มต่ำเพื่อเสริมการสนับสนุน และกลุ่มที่มีแนวโน้มสูงเพื่อต่อยอดสิ่งที่ได้ผล"
    if abs(forecast_actual_gap) >= 10:
        reliability_note = (
            f"โมเดลจัดเข้าเงื่อนไข {rate:.1f}% แต่เกิดขึ้นจริง {actual_rate:.1f}% "
            f"ต่างกัน {forecast_actual_gap:+.1f} จุดเปอร์เซ็นต์ จึงไม่ควรใช้จำนวนที่โมเดลแจ้ง "
            "เป็นประมาณการความต้องการงบประมาณโดยตรง ต้องทบทวน threshold และ calibration ก่อน"
        )
    else:
        reliability_note = (
            f"อัตราที่โมเดลจัดเข้าเงื่อนไขต่างจากอัตราที่เกิดขึ้นจริง "
            f"{forecast_actual_gap:+.1f} จุดเปอร์เซ็นต์ ควรติดตามความต่างนี้ทุกรอบข้อมูล"
        )
    return {
        "signal": signal,
        "implication": implication,
        "reliability_note": reliability_note,
        "policy_goal": spec["policy_goal"],
        "policy_actions": list(spec["policy_actions"]),
        "monitoring_kpis": list(spec["monitoring_kpis"]),
        "direction": spec["direction"],
    }


def configured_ml_features() -> list[str]:
    config = metric_definitions().get("data_quality", {})
    return list(config.get("ml_feature_fields", DEFAULT_FEATURES))


def leakage_fields() -> set[str]:
    config = metric_definitions().get("data_quality", {})
    leakage = set(config.get("ml_leakage_fields", []))
    targets = set(config.get("ml_target_fields", []))
    aggregate_only = set(config.get("aggregate_only_fields", []))
    return leakage | targets | aggregate_only


def available_model_features(df: pd.DataFrame, target: str = DEFAULT_TARGET) -> list[str]:
    blocked = leakage_fields() | {target}
    return [feature for feature in configured_ml_features() if feature in df.columns and feature not in blocked]


def feature_readiness(df: pd.DataFrame, target: str = DEFAULT_TARGET) -> pd.DataFrame:
    rows = []
    selected = set(available_model_features(df, target))
    blocked = leakage_fields() | {target}
    for feature in configured_ml_features():
        exists = feature in df.columns
        completeness = float(df[feature].notna().mean() * 100) if exists and len(df) else 0.0
        rows.append(
            {
                "feature": feature,
                "status": "selected" if feature in selected else "excluded",
                "reason": _feature_reason(feature, exists, completeness, blocked),
                "completeness_rate": round(completeness, 2),
                "unique_values": int(df[feature].nunique(dropna=True)) if exists else 0,
                "dtype": str(df[feature].dtype) if exists else "missing",
            }
        )
    return pd.DataFrame(rows)


def target_summary(df: pd.DataFrame, target: str = DEFAULT_TARGET) -> dict[str, Any]:
    if target not in df:
        return {"target": target, "ready": False, "reason": "Target column is missing."}
    values = pd.to_numeric(df[target], errors="coerce").dropna().astype(int)
    counts = values.value_counts().to_dict()
    positive = int(counts.get(1, 0))
    negative = int(counts.get(0, 0))
    ready = positive > 0 and negative > 0
    return {
        "target": target,
        "ready": ready,
        "records": int(len(values)),
        "positive_count": positive,
        "negative_count": negative,
        "positive_rate": round(positive / len(values) * 100, 2) if len(values) else 0.0,
        "reason": "Binary classes are available." if ready else "Target needs both positive and negative classes.",
    }


def train_model_suite(
    df: pd.DataFrame,
    target: str = DEFAULT_TARGET,
    selected_models: list[str] | None = None,
    random_state: int = 42,
) -> list[ModelResult]:
    sklearn = _sklearn()
    features = available_model_features(df, target)
    if not features:
        raise ValueError("No configured ML features are available.")
    summary = target_summary(df, target)
    if not summary["ready"]:
        raise ValueError(str(summary["reason"]))

    working = df[[*features, target, *(["split"] if "split" in df else [])]].copy()
    working[target] = pd.to_numeric(working[target], errors="coerce")
    working = working.dropna(subset=[target])
    working[target] = working[target].astype(int)
    train_df, test_df, split_label = _train_test_frames(working, target, random_state, sklearn)

    numeric_features = [feature for feature in features if pd.api.types.is_numeric_dtype(working[feature])]
    categorical_features = [feature for feature in features if feature not in numeric_features]
    preprocessor = sklearn["ColumnTransformer"](
        transformers=[
            (
                "categorical",
                sklearn["Pipeline"](
                    steps=[
                        ("imputer", sklearn["SimpleImputer"](strategy="most_frequent")),
                        ("onehot", sklearn["OneHotEncoder"](handle_unknown="ignore", sparse_output=False)),
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

    model_keys = selected_models or list(MODEL_SPECS)
    ensemble_base_keys = _selected_ensemble_base_keys(model_keys)
    results = []
    for key in model_keys:
        estimator = _estimator(key, random_state, sklearn, ensemble_base_keys)
        pipeline = sklearn["Pipeline"](
            steps=[
                ("preprocess", preprocessor),
                ("model", estimator),
            ]
        )
        x_train = train_df[features]
        y_train = train_df[target]
        x_test = test_df[features]
        y_test = test_df[target]
        pipeline.fit(x_train, y_train)
        y_pred = pipeline.predict(x_test)
        y_score = _positive_scores(pipeline, x_test)
        spec = MODEL_SPECS[key]
        metrics = _metrics(y_test, y_pred, y_score, split_label, len(train_df), len(test_df), sklearn)
        if key == "vote_ensemble":
            metrics["ensemble_base_models"] = ", ".join(MODEL_SPECS[base_key]["label"] for base_key in ensemble_base_keys)
            metrics["ensemble_base_count"] = len(ensemble_base_keys)
        results.append(
            ModelResult(
                key=key,
                label=spec["label"],
                purpose=spec["purpose"],
                metrics=metrics,
                confusion_matrix=_confusion_matrix(y_test, y_pred, sklearn),
                feature_importance=_feature_importance(pipeline, key),
                validation_predictions=_validation_prediction_frame(
                    test_df,
                    target,
                    y_pred,
                    y_score,
                ),
            )
        )
    return results


def results_to_metrics_frame(results: list[ModelResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append({"model": result.label, **result.metrics})
    return pd.DataFrame(rows)


def _feature_reason(feature: str, exists: bool, completeness: float, blocked: set[str]) -> str:
    if not exists:
        return "Missing from dataset."
    if feature in blocked:
        return "Excluded to prevent leakage or row-level identification."
    if completeness < 60:
        return "Selected, but low completeness should be reviewed."
    return "Selected as a non-PII contextual predictor."


def _train_test_frames(df: pd.DataFrame, target: str, random_state: int, sklearn: dict[str, Any]):
    if "split" in df and {"development", "validation"}.issubset(set(df["split"].dropna())):
        train_df = df[df["split"] == "development"].copy()
        test_df = df[df["split"] == "validation"].copy()
        return train_df, test_df, "development/validation"
    train_df, test_df = sklearn["train_test_split"](
        df,
        test_size=0.25,
        stratify=df[target],
        random_state=random_state,
    )
    return train_df.copy(), test_df.copy(), "stratified random"


def _selected_ensemble_base_keys(model_keys: list[str]) -> list[str]:
    selected_base_keys = [key for key in model_keys if key in BASE_MODEL_KEYS]
    return selected_base_keys if len(selected_base_keys) >= 2 else BASE_MODEL_KEYS


def _estimator(
    key: str,
    random_state: int,
    sklearn: dict[str, Any],
    ensemble_base_keys: list[str] | None = None,
):
    if key == "logistic_regression":
        return sklearn["LogisticRegression"](max_iter=1000, class_weight="balanced", random_state=random_state)
    if key == "decision_tree":
        return sklearn["DecisionTreeClassifier"](max_depth=4, min_samples_leaf=25, class_weight="balanced", random_state=random_state)
    if key == "random_forest":
        return sklearn["RandomForestClassifier"](
            n_estimators=200,
            max_depth=7,
            min_samples_leaf=10,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )
    if key == "naive_bayes":
        return sklearn["GaussianNB"]()
    if key == "calibrated_svm":
        return sklearn["CalibratedClassifierCV"](
            estimator=sklearn["LinearSVC"](
                C=1.0,
                class_weight="balanced",
                random_state=random_state,
                dual="auto",
            ),
            cv=2,
            ensemble=False,
        )
    if key == "vote_ensemble":
        base_keys = ensemble_base_keys or BASE_MODEL_KEYS
        estimators = [(base_key, _estimator(base_key, random_state, sklearn, base_keys)) for base_key in base_keys]
        return sklearn["VotingClassifier"](estimators=estimators, voting="soft", n_jobs=-1)
    raise ValueError(f"Unsupported model key: {key}")


def _positive_scores(pipeline, x_test: pd.DataFrame):
    if hasattr(pipeline, "predict_proba"):
        return pipeline.predict_proba(x_test)[:, 1]
    if hasattr(pipeline, "decision_function"):
        return pipeline.decision_function(x_test)
    return None


def _metrics(y_test, y_pred, y_score, split_label: str, train_rows: int, test_rows: int, sklearn: dict[str, Any]) -> dict[str, float | int | str]:
    output: dict[str, float | int | str] = {
        "split": split_label,
        "train_rows": int(train_rows),
        "validation_rows": int(test_rows),
        "accuracy": round(float(sklearn["accuracy_score"](y_test, y_pred)), 4),
        "balanced_accuracy": round(float(sklearn["balanced_accuracy_score"](y_test, y_pred)), 4),
        "precision": round(float(sklearn["precision_score"](y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(sklearn["recall_score"](y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(sklearn["f1_score"](y_test, y_pred, zero_division=0)), 4),
    }
    if y_score is not None and len(set(y_test)) == 2:
        output["roc_auc"] = round(float(sklearn["roc_auc_score"](y_test, y_score)), 4)
        output["pr_auc"] = round(float(sklearn["average_precision_score"](y_test, y_score)), 4)
        output["brier_score"] = round(float(sklearn["brier_score_loss"](y_test, y_score)), 4)
    return output


def _confusion_matrix(y_test, y_pred, sklearn: dict[str, Any]) -> pd.DataFrame:
    matrix = sklearn["confusion_matrix"](y_test, y_pred, labels=[0, 1])
    return pd.DataFrame(
        [
            {"actual": "0 - ไม่เข้าเงื่อนไข", "predicted_0": int(matrix[0][0]), "predicted_1": int(matrix[0][1])},
            {"actual": "1 - เข้าเงื่อนไข", "predicted_0": int(matrix[1][0]), "predicted_1": int(matrix[1][1])},
        ]
    )


def _validation_prediction_frame(
    test_df: pd.DataFrame,
    target: str,
    y_pred,
    y_score,
) -> pd.DataFrame:
    group_columns = [
        column
        for column in ["cohort", "region", "province", "current_country", "current_field_group"]
        if column in test_df.columns
    ]
    predictions = test_df[group_columns].reset_index(drop=True).copy()
    predictions["actual"] = pd.to_numeric(test_df[target], errors="coerce").reset_index(drop=True)
    predictions["predicted"] = pd.Series(y_pred).reset_index(drop=True).astype(int)
    score_values = y_score if y_score is not None else y_pred
    predictions["positive_probability"] = (
        pd.to_numeric(pd.Series(score_values), errors="coerce").fillna(0.0).clip(0.0, 1.0)
    )
    predictions["tendency_band"] = pd.cut(
        predictions["positive_probability"],
        bins=[-0.001, 0.3, 0.6, 1.0],
        labels=["ต่ำ", "ปานกลาง", "สูง"],
        include_lowest=True,
    ).astype(str)
    return predictions


def _feature_importance(pipeline, key: str, limit: int = 15) -> pd.DataFrame:
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    model = pipeline.named_steps["model"]
    if key == "logistic_regression":
        values = model.coef_[0]
        rows = [
            {"feature": str(name), "importance": round(float(abs(value)), 6), "direction": "positive" if value >= 0 else "negative"}
            for name, value in zip(names, values)
        ]
    elif hasattr(model, "feature_importances_"):
        rows = [
            {"feature": str(name), "importance": round(float(value), 6), "direction": "importance"}
            for name, value in zip(names, model.feature_importances_)
        ]
    elif key == "naive_bayes" and hasattr(model, "theta_") and len(model.theta_) == 2:
        values = abs(model.theta_[1] - model.theta_[0])
        rows = [
            {"feature": str(name), "importance": round(float(value), 6), "direction": "class-mean-difference"}
            for name, value in zip(names, values)
        ]
    else:
        rows = _permutation_importance(pipeline, limit)
        return pd.DataFrame(rows)
    return pd.DataFrame(rows).sort_values("importance", ascending=False).head(limit).reset_index(drop=True)


def _permutation_importance(pipeline, limit: int = 15) -> list[dict[str, float | str]]:
    preprocessor = pipeline.named_steps["preprocess"]
    names = preprocessor.get_feature_names_out()
    model = pipeline.named_steps["model"]
    if hasattr(model, "coef_"):
        values = abs(model.coef_[0])
    elif hasattr(model, "estimators_"):
        values_by_model = []
        for fitted in model.estimators_:
            if hasattr(fitted, "feature_importances_"):
                values_by_model.append(fitted.feature_importances_)
            elif hasattr(fitted, "coef_"):
                values_by_model.append(abs(fitted.coef_[0]))
        values = sum(values_by_model) / len(values_by_model) if values_by_model else [0] * len(names)
    else:
        values = [0] * len(names)
    rows = [
        {"feature": str(name), "importance": round(float(value), 6), "direction": "model-derived"}
        for name, value in zip(names, values)
    ]
    return pd.DataFrame(rows).sort_values("importance", ascending=False).head(limit).reset_index(drop=True).to_dict("records")


def _sklearn() -> dict[str, Any]:
    try:
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.compose import ColumnTransformer
        from sklearn.ensemble import RandomForestClassifier, VotingClassifier
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import (
            accuracy_score,
            average_precision_score,
            balanced_accuracy_score,
            brier_score_loss,
            confusion_matrix,
            f1_score,
            precision_score,
            recall_score,
            roc_auc_score,
        )
        from sklearn.model_selection import train_test_split
        from sklearn.naive_bayes import GaussianNB
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler
        from sklearn.svm import LinearSVC
        from sklearn.tree import DecisionTreeClassifier
    except ImportError as exc:
        raise RuntimeError("scikit-learn is required for ML model training. Install requirements.txt first.") from exc
    return locals()
