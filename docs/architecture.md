# Architecture

## Prototype Architecture

```text
No-PII CSV sample
      |
      v
src/ingestion/loaders.py
      |
      +--> Phase 3 SQLite schema
      +--> Streamlit shell and navigation
      +--> Data Quality report surface
      +--> Risk/Policy placeholder tables
      +--> Governance checks
```

## Layers

- Data: `data/sample` and `data/reference`
- Config: `config/*.yaml`
- Business logic: `src/*`
- UI: `app.py` and `pages/*.py`
- Validation: `scripts/*.py` and `tests/*.py`

## Phase 3 Database Tables

- `students`
- `education_records`
- `employment_records`
- `scholarship_status`
- `geography_reference`
- `external_indicators`
- `data_import_log`
- `risk_scores`
- `policy_recommendations`
- `audit_logs`

## Data Source

The prototype reads no-PII CSV files generated from Phase 1:

- `data/sample/development_sample.csv`
- `data/sample/validation_data.csv`

Raw Excel files are intentionally excluded from the repository.

## Governance

The app must default to aggregate outputs and must not expose direct PII. Privacy checks are enforced through:

- `.gitignore`
- `scripts/privacy_check.py`
- `src/governance/privacy.py`
- `tests/test_privacy.py`
