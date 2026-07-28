from __future__ import annotations

import hashlib
import importlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analytics.metrics import apply_filters, overview_metrics
from src.governance.privacy import (
    aggregate_csv_bytes,
    find_pii_in_text,
    role_can,
)
from src.ingestion.importer import import_csv
from src.pipeline.phase4 import run_phase4_pipeline
from src.policy.recommendations import field_recommendations
from src.risk.scoring import score_row
from src.utils.config import PROJECT_ROOT, load_yaml
from src.validation.schema import validate_dataframe


class AcceptanceFailure(RuntimeError):
    pass


def _check(name: str, condition: bool, detail: str, results: list[dict]) -> None:
    results.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    if not condition:
        raise AcceptanceFailure(f"{name}: {detail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text_files_under(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() not in {".xlsx", ".db", ".sqlite"}]


def check_repository(results: list[dict]) -> None:
    required = [
        "README.md",
        "AGENTS.md",
        "PROJECT_SCOPE.md",
        "requirements.txt",
        ".env.example",
        "app.py",
        "docs/phase8_handover.md",
    ]
    missing = [item for item in required if not (PROJECT_ROOT / item).exists()]
    _check("repository_artifacts", not missing, f"missing={missing}", results)

    raw_entries = {path.name for path in (PROJECT_ROOT / "data/raw").iterdir()}
    _check("raw_data_untouched", raw_entries <= {"README.md"}, f"data/raw entries={sorted(raw_entries)}", results)

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=PROJECT_ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    _check("git_history", bool(tracked), f"tracked_files={len(tracked)}", results)

    secret_pattern = re.compile(r"(?im)\b(?:password|secret|api[_-]?key)\s*[:=]\s*['\"]?[^#\r\n]+")
    secret_hits = []
    for relative in tracked:
        path = PROJECT_ROOT / relative
        if path.suffix.lower() in {".pyc", ".xlsx", ".db", ".sqlite"} or not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if secret_pattern.search(text):
            secret_hits.append(relative)
    _check("no_secrets", not secret_hits, f"secret_like_files={secret_hits}", results)

    data_hits = []
    data_root = PROJECT_ROOT / "data"
    for path in _text_files_under(data_root):
        text = path.read_text(encoding="utf-8", errors="replace")
        findings = find_pii_in_text(text)
        if findings:
            data_hits.append({"file": str(path.relative_to(PROJECT_ROOT)), "patterns": findings})
    _check("no_pii_in_data_artifacts", not data_hits, f"hits={data_hits}", results)


def check_data_pipeline(results: list[dict]) -> pd.DataFrame:
    first = run_phase4_pipeline()
    cleaned_path = Path(first["outputs"]["cleaned_dataset"])
    cleaned = pd.read_csv(cleaned_path)
    _check("pipeline_row_traceability", first["rows_read"] == first["cleaned_rows"] == len(cleaned), str(first), results)
    first_hash = _sha256(cleaned_path)
    second = run_phase4_pipeline()
    second_hash = _sha256(Path(second["outputs"]["cleaned_dataset"]))
    _check("pipeline_reproducible", first_hash == second_hash and second["duplicate_source"], "same cleaned hash and duplicate source detected", results)

    schema = load_yaml("config/validation_schema.yaml")
    issues = validate_dataframe(cleaned, "phase8_cleaned", schema)
    errors = [issue.as_dict() for issue in issues if issue.severity == "error"]
    _check("data_validation", not errors, f"errors={errors[:5]}", results)
    _check("unique_ids", not cleaned["odos_uid"].duplicated().any(), "odos_uid has no duplicates", results)

    start = pd.to_datetime(cleaned.get("study_start_date"), errors="coerce")
    graduation = pd.to_datetime(cleaned.get("graduation_expected_date"), errors="coerce")
    dropout = pd.to_datetime(cleaned.get("study_end_dropout_date"), errors="coerce")
    work_start = pd.to_datetime(cleaned.get("work_start_date"), errors="coerce")
    bad_dates = (
        (graduation.notna() & start.notna() & (graduation < start))
        | (dropout.notna() & start.notna() & (dropout < start))
        | (work_start.notna() & start.notna() & (work_start < start))
    ).sum()
    issue_frame = pd.read_csv(first["outputs"]["validation_issues"])
    recorded_date_issues = int(issue_frame["code"].astype(str).str.contains("date", case=False, na=False).sum()) if not issue_frame.empty else 0
    _check("date_relationships_recorded", int(bad_dates) == recorded_date_issues, f"invalid={int(bad_dates)}, recorded={recorded_date_issues}", results)
    _check("processing_evidence", all(Path(value).exists() for value in first["outputs"].values()), "all pipeline outputs exist", results)
    return cleaned


def check_functional(cleaned: pd.DataFrame, results: list[dict]) -> None:
    sample = PROJECT_ROOT / "data/sample/modeling_dataset_no_pii.csv"
    with tempfile.TemporaryDirectory(prefix="odos_phase8_") as temp_dir:
        imported, issues = import_csv(sample, "phase8_upload", temp_dir)
        _check("upload_import", imported.status == "passed" and imported.rows > 0 and not [item for item in issues if item["severity"] == "error"], imported.as_dict(), results)

    filters = {"cohort": [cleaned["cohort"].dropna().iloc[0]]}
    filtered = apply_filters(cleaned, cohorts=filters["cohort"])
    expected = int((cleaned["cohort"] == filters["cohort"][0]).sum())
    _check("filters", len(filtered) == expected and len(filtered) <= len(cleaned), f"filtered={len(filtered)}, expected={expected}", results)

    metrics = overview_metrics(filtered)
    expected_completion = int((filtered["target_graduation_success"] == 1).sum())
    expected_employment = int((filtered["target_employment_ready"] == 1).sum())
    _check("kpi_calculation", metrics["completion_count"] == expected_completion and metrics["employed_count"] == expected_employment, str(metrics), results)

    risk = score_row({
        "target_scholarship_risk": 1,
        "target_tracking_risk": 1,
        "target_field_mismatch": 1,
        "target_local_mismatch": 1,
        "project_condition_status": None,
        "current_status": None,
        "employment_type": None,
        "current_country": "Japan",
        "restart_thailand_date": None,
    })
    _check("risk_score", 0 <= risk["risk_score"] <= 100 and risk["components"] and risk["calculated_at"] and risk["rule_version"], str(risk), results)

    synthetic = pd.DataFrame({
        "odos_uid": ["a", "b", "c", "d"],
        "current_field_group": ["A", "A", "B", "B"],
        "target_graduation_success": [1, 1, 0, 0],
        "target_employment_ready": [1, 1, 0, 0],
        "field_job_fit_level": [3, 3, 1, 1],
        "income_monthly_est": [30000, 30000, 10000, 10000],
        "local_fit_level": [3, 3, 1, 1],
    })
    rec_default = field_recommendations(synthetic, min_records=1)
    rec_changed = field_recommendations(synthetic, min_records=1, weights={"completion_rate": 1, "employment_rate": 1, "field_job_fit": 1, "income_outcome": 1, "local_development_fit": 1, "data_completeness": 20})
    _check("policy_recommendation", not rec_default.empty and not rec_changed.empty and not rec_default["policy_score"].equals(rec_changed["policy_score"]), "ranking recalculates after weights change", results)

    required_pages = [PROJECT_ROOT / "pages" / f"0{index}_{name}.py" for index, name in enumerate(["overview", "data_quality", "analytics", "risk_forecast", "policy_recommendation", "external_indicators", "governance"], start=1)]
    page_text = "\n".join(path.read_text(encoding="utf-8") for path in required_pages)
    _check("ui_controls", "st.file_uploader" in page_text and "st.download_button" in page_text and "st.multiselect" in page_text, "upload/filter/export controls present", results)


def check_governance(results: list[dict]) -> None:
    _check("role_permissions", role_can("Admin", "can_import") and role_can("Analyst", "can_export_aggregate") and not role_can("Viewer", "can_export_aggregate"), "Admin import, Analyst aggregate export, Viewer denied", results)
    aggregate = pd.DataFrame({"province": ["A"], "count": [10]})
    exported = aggregate_csv_bytes(aggregate, "phase8_acceptance.csv", "Analyst").decode("utf-8-sig")
    _check("aggregate_export", "province" in exported and "count" in exported and not find_pii_in_text(exported), "aggregate CSV exported without PII patterns", results)
    viewer_denied = False
    try:
        aggregate_csv_bytes(aggregate, "phase8_viewer.csv", "Viewer")
    except PermissionError:
        viewer_denied = True
    _check("export_permissions", viewer_denied, "Viewer export denied at service layer", results)


def check_deployment(results: list[dict]) -> None:
    required_modules = {"streamlit": "streamlit", "pandas": "pandas", "plotly": "plotly", "yaml": "yaml", "pytest": "pytest", "openpyxl": "openpyxl"}
    missing = []
    for label, module in required_modules.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(label)
    _check("requirements_runtime", not missing, f"missing_modules={missing}", results)
    py_files = list(PROJECT_ROOT.glob("*.py")) + list((PROJECT_ROOT / "pages").glob("*.py")) + list((PROJECT_ROOT / "src").rglob("*.py")) + list((PROJECT_ROOT / "scripts").glob("*.py"))
    compile_failures = []
    for path in py_files:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as error:
            compile_failures.append(f"{path}: {error}")
    _check("python_syntax", not compile_failures, f"failures={compile_failures}", results)


def main() -> int:
    results: list[dict] = []
    try:
        check_repository(results)
        cleaned = check_data_pipeline(results)
        check_functional(cleaned, results)
        check_governance(results)
        check_deployment(results)
    except Exception as error:
        results.append({"name": "phase8_acceptance", "status": "FAIL", "detail": str(error)})

    passed = sum(item["status"] == "PASS" for item in results)
    failed = sum(item["status"] == "FAIL" for item in results)
    print(json.dumps({"status": "passed" if failed == 0 else "failed", "passed": passed, "failed": failed, "checks": results}, ensure_ascii=True, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
