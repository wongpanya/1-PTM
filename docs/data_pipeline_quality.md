# Phase 4: Data Pipeline and Data Quality

## Purpose

Phase 4 implements a repeatable Excel-to-cleaned-data pipeline for the ODOS Policy Analytics Prototype.

## Input

Default raw source:

```text
../phase1_outputs/raw/690724 DB_ODOS Students+.xlsx
```

The raw file is read-only and remains outside the public prototype repository.

## Pipeline Steps

1. Read Excel workbook.
2. Check required sheets: `DB_Students`, `Remark`.
3. Check required columns.
4. Read rows with source `ID`.
5. Clean and standardize selected no-PII fields.
6. Convert spreadsheet errors such as `#NUM!` to missing values.
7. Parse dates and income.
8. Calculate study duration from source dates.
9. Validate duplicate IDs, date order, income range, dictionary values, and key-field completeness.
10. Write cleaned data, validation issues, processing log, and before-after report.

## Outputs

Runtime outputs are local-only and ignored by Git:

- `data/processed/phase4/cleaned_modeling_dataset_no_pii.csv`
- `data/processed/phase4/validation_issues.csv`
- `data/processed/phase4/processing_log.jsonl`
- `data/processed/phase4/before_after_report.json`
- `data/processed/phase4/before_after_report.md`
- `data/processed/phase4/latest_import_manifest.json`

## Quality Scores

- Completeness Score
- Validity Score
- Uniqueness Score
- Consistency Score

## Rules

- Raw data is never modified.
- Pipeline output is deterministic for cleaned data.
- Processing log records timestamps and source hash.
- Failed/invalid records are not deleted; issues are recorded in `validation_issues.csv`.
- Excel formula errors such as `#NUM!` are treated as missing values, not analytical values.

## Command

```bash
python scripts/run_phase4_pipeline.py
```

Windows launcher:

```text
launchers/04_phase4_data_pipeline.bat
```
