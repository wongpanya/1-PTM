import csv
import json
from pathlib import Path


ROOT = Path(r"C:\Users\Wongpanya.Nu\Documents\1-PTM")

REQUIRED_FILES = [
    "phase1_outputs/raw/690724 DB_ODOS Students+.xlsx",
    "phase1_outputs/raw/RAW_DATA_MANIFEST.md",
    "phase1_outputs/samples/development_sample.csv",
    "phase1_outputs/samples/validation_data.csv",
    "phase1_outputs/samples/modeling_dataset_no_pii.csv",
    "phase1_outputs/data/data_dictionary.csv",
    "docs/phase1/DATA_DICTIONARY_GUIDE.md",
    "docs/phase1/CLEANING_RULES.md",
    "docs/phase1/TARGET_VARIABLES.md",
    "docs/phase1/DATA_DEFINITION_SIGNOFF.md",
    "docs/phase1/PHASE1_ACCEPTANCE_CHECKLIST.md",
    "phase1_outputs/reports/phase1_data_splits_summary.json",
]

FORBIDDEN_SAMPLE_COLUMNS = {
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

TARGET_COLUMNS = {
    "target_graduation_success",
    "target_scholarship_risk",
    "target_tracking_risk",
    "target_employment_ready",
    "target_field_mismatch",
    "target_local_mismatch",
}


def read_header_and_count(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        count = sum(1 for _ in reader)
    return header, count


def main():
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).exists()]
    dev_header, dev_count = read_header_and_count(ROOT / "phase1_outputs/samples/development_sample.csv")
    val_header, val_count = read_header_and_count(ROOT / "phase1_outputs/samples/validation_data.csv")
    dict_header, dict_count = read_header_and_count(ROOT / "phase1_outputs/data/data_dictionary.csv")
    forbidden_present = sorted(FORBIDDEN_SAMPLE_COLUMNS.intersection(dev_header).union(FORBIDDEN_SAMPLE_COLUMNS.intersection(val_header)))
    targets_missing = sorted(TARGET_COLUMNS.difference(dev_header).union(TARGET_COLUMNS.difference(val_header)))
    summary = {
        "missing_required_files": missing,
        "development_rows": dev_count,
        "validation_rows": val_count,
        "total_split_rows": dev_count + val_count,
        "data_dictionary_fields": dict_count,
        "forbidden_sample_columns_present": forbidden_present,
        "target_columns_missing": targets_missing,
        "phase1_ready_for_prototype": not missing and not forbidden_present and not targets_missing and dev_count > 0 and val_count > 0 and dict_count == 112,
        "formal_data_definition_signoff": "pending",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
