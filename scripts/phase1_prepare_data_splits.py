import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(r"C:\Users\Wongpanya.Nu\Documents\1-PTM")
DATA_DIR = ROOT / "phase1_outputs" / "data"
SAMPLE_DIR = ROOT / "phase1_outputs" / "samples"
REPORT_DIR = ROOT / "phase1_outputs" / "reports"
CORE_PATH = DATA_DIR / "core_scholarship_dataset.csv"


SAFE_COLUMNS = [
    "odos_uid",
    "source_id",
    "cohort",
    "round",
    "scholarship_type",
    "cohort_round",
    "sex",
    "birth_year_be",
    "high_school_track",
    "region",
    "province_code",
    "province",
    "district",
    "economic_corridor",
    "initial_status",
    "initial_country",
    "initial_field_group",
    "initial_field",
    "study_start_date",
    "study_end_dropout_date",
    "graduation_expected_date",
    "restart_thailand_date",
    "project_condition_status",
    "overall_status",
    "after_m6_status",
    "current_status",
    "current_continent",
    "current_country",
    "current_field_group",
    "current_field",
    "program_funding_years",
    "funding_period_academic_year",
    "contract_status",
    "latest_degree",
    "gpa_numeric",
    "study_duration_years",
    "ocs_report_date",
    "moe_report_date",
    "masters_country",
    "masters_field_group",
    "masters_field",
    "doctoral_country",
    "doctoral_field_group",
    "doctoral_field",
    "employment_type",
    "employment_detail",
    "employment_evidence_status",
    "workplace_province_country",
    "work_start_date",
    "income_monthly_est",
    "welfare",
    "domicile_employment_relation",
    "field_job_fit",
    "field_job_fit_level",
    "local_fit",
    "local_fit_level",
    "job_satisfaction",
    "job_satisfaction_level",
    "wants_government",
    "wants_government_flag",
    "desired_government_position",
    "wants_moe",
    "desired_agency_other",
]

EXCLUDED_COLUMNS = [
    "high_school_name",
    "initial_university",
    "initial_city_state",
    "current_university",
    "current_city_province",
    "employer",
    "job_title",
    "income_raw",
    "gpa_raw",
    "other_comments",
    "officer_notes",
]


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def text_value(row, key):
    value = row.get(key)
    if value is None:
        return ""
    return str(value).strip()


def is_success(row):
    return 1 if text_value(row, "project_condition_status") == "สำเร็จการศึกษา" else 0


def is_scholarship_risk(row):
    status = text_value(row, "project_condition_status")
    risky = {"ลาออก", "พ้นสภาพ", "เกินระยะเวลารับทุน", "สละสิทธิ์"}
    return 1 if status in risky else 0


def is_tracking_risk(row):
    employment = text_value(row, "employment_type")
    status = text_value(row, "current_status")
    if "อยู่ระหว่างติดตามข้อมูล" in employment:
        return 1
    if "ไม่พบในฐานข้อมูล" in status:
        return 1
    return 0


def is_employment_ready(row):
    employment = text_value(row, "employment_type")
    positive = {"ภาคเอกชน", "ภาครัฐ", "รัฐวิสาหกิจ", "ธุรกิจส่วนตัว", "องค์กรเอกชนเพื่อสาธารณประโยชน์"}
    return 1 if employment in positive else 0


def is_field_mismatch(row):
    level = text_value(row, "field_job_fit_level")
    return 1 if level in {"0", "1", "0.0", "1.0"} else 0


def is_local_mismatch(row):
    level = text_value(row, "local_fit_level")
    return 1 if level in {"0", "1", "0.0", "1.0"} else 0


def split_bucket(odos_uid):
    digest = hashlib.sha256(odos_uid.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def main():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rows = read_csv(CORE_PATH)
    safe_columns = [c for c in SAFE_COLUMNS if c in rows[0]]
    target_columns = [
        "target_graduation_success",
        "target_scholarship_risk",
        "target_tracking_risk",
        "target_employment_ready",
        "target_field_mismatch",
        "target_local_mismatch",
    ]
    output_columns = safe_columns + target_columns + ["split"]

    sanitized = []
    for row in rows:
        safe_row = {col: row.get(col, "") for col in safe_columns}
        safe_row["target_graduation_success"] = is_success(row)
        safe_row["target_scholarship_risk"] = is_scholarship_risk(row)
        safe_row["target_tracking_risk"] = is_tracking_risk(row)
        safe_row["target_employment_ready"] = is_employment_ready(row)
        safe_row["target_field_mismatch"] = is_field_mismatch(row)
        safe_row["target_local_mismatch"] = is_local_mismatch(row)
        safe_row["split"] = "validation" if split_bucket(safe_row["odos_uid"]) >= 80 else "development"
        sanitized.append(safe_row)

    development = [row for row in sanitized if row["split"] == "development"]
    validation = [row for row in sanitized if row["split"] == "validation"]

    write_csv(SAMPLE_DIR / "development_sample.csv", development, output_columns)
    write_csv(SAMPLE_DIR / "validation_data.csv", validation, output_columns)
    write_csv(SAMPLE_DIR / "modeling_dataset_no_pii.csv", sanitized, output_columns)

    summary = {
        "source": str(CORE_PATH),
        "split_method": "deterministic SHA256 hash of odos_uid; bucket 0-79 development, 80-99 validation",
        "total_rows": len(sanitized),
        "development_rows": len(development),
        "validation_rows": len(validation),
        "safe_columns_count": len(safe_columns),
        "target_columns": target_columns,
        "excluded_columns_due_to_privacy_or_free_text": EXCLUDED_COLUMNS,
    }
    (REPORT_DIR / "phase1_data_splits_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
