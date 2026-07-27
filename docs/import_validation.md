# Task 3: Data Import and Validation

## Purpose

Task 3 implements the prototype data import and validation workflow. It imports no-PII CSV data, validates schema and privacy rules, builds a local SQLite database, and writes audit/report outputs.

## Commands

```bash
python scripts/import_data.py --source data/sample/modeling_dataset_no_pii.csv --dataset-name modeling_dataset_no_pii
python scripts/build_database.py
python scripts/validate_data.py
python scripts/privacy_check.py
```

Windows launcher:

```text
launchers/003_task3_import_validate.bat
```

## Inputs

- `data/sample/modeling_dataset_no_pii.csv`
- `data/sample/development_sample.csv`
- `data/sample/validation_data.csv`
- `config/validation_schema.yaml`
- `config/column_mapping.yaml`

## Local Outputs

Generated files are local runtime artifacts and should not be committed:

- `data/processed/imported/modeling_dataset_no_pii.csv`
- `data/processed/odos_policy_analytics.sqlite`
- `data/processed/audit_log.jsonl`
- `data/processed/reports/validation_report.json`
- `data/processed/reports/validation_report.md`
- `data/processed/reports/validation_issues.csv`

## Validation Coverage

The validation workflow checks:

- dataset existence
- row count threshold
- required columns
- forbidden privacy columns
- duplicate primary keys
- missing primary keys
- allowed target/split values
- required column completeness threshold
- expected development/validation split value

## Privacy Coverage

The privacy workflow checks:

- no forbidden columns in no-PII datasets
- no committed/local files inside `data/raw` except `README.md`

## SQLite Tables

`scripts/build_database.py` builds:

- `modeling_dataset_no_pii`
- `students`
- `education`
- `employment`

## Audit Log

Import and database build actions append JSONL events to:

```text
data/processed/audit_log.jsonl
```

## Scope Note

This task does not import raw Excel files into the public prototype repository. Raw Excel import remains out of scope until an admin-only workflow, stronger validation, and explicit privacy review are added.
