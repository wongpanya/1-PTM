# ODOS Policy Analytics Prototype

Prototype เว็บวิเคราะห์ข้อมูลผู้รับทุน 1 อำเภอ 1 ทุน เพื่อพิสูจน์ว่าข้อมูลผู้รับทุนสามารถพัฒนาเป็นระบบสนับสนุนนโยบายได้จริง

ระบบนี้เป็น Prototype สำหรับสาธิตและวิเคราะห์เชิงนโยบาย ไม่ใช่ Production System และไม่ใช่ระบบตัดสินใจจัดสรรทุนอัตโนมัติ

## Main Pages

1. Overview
2. Data Quality
3. Analytics
4. Risk & Forecast
5. Policy Recommendation
6. External Indicators
7. Governance

## Repository Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run app.py
```

Default data source:

```text
data/sample/development_sample.csv
```

Validation data:

```text
data/sample/validation_data.csv
```

## Test and Validate

Run all required checks:

```bash
python scripts/run_unit_tests.py
python scripts/import_data.py
python scripts/build_database.py
python scripts/validate_data.py
python scripts/privacy_check.py
```

If `pytest` is installed, you may also run:

```bash
pytest
```

Task 3 import and validation workflow:

```bash
python scripts/import_data.py --source data/sample/modeling_dataset_no_pii.csv --dataset-name modeling_dataset_no_pii
python scripts/build_database.py
python scripts/validate_data.py
python scripts/privacy_check.py
```

Generated local outputs are written to `data/processed/` and are ignored by Git when appropriate.

## Data Policy

- `data/raw/` is local-only and must not contain committed real data.
- Committed sample data must not contain direct PII.
- The app must display aggregate results by default.
- Risk and policy recommendations must include explanations and limitations.

## Prototype Technology

- Streamlit
- Python
- Pandas
- Plotly
- SQLite/CSV
- Pytest

## Phase Status

- Phase 0: Locked
- Phase 1: Ready for prototype development, pending formal data definition sign-off
- Phase 2: Repository prepared
- Phase 3: App and central SQLite schema scaffolded
- Phase 4: Data pipeline and data quality workflow implemented

## Phase 4 Data Pipeline

Run the Excel-to-cleaned-data pipeline:

```bash
python scripts/run_phase4_pipeline.py
```

The pipeline reads the private raw Excel copy outside the public repo, checks required sheets and columns, cleans values, validates records, writes data quality scores, and records processing logs. Outputs are written to `data/processed/phase4/` and are not committed.

## Database Schema

The Phase 3 prototype database initializes these tables:

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

## Production Roadmap

Production expansion should add:

- database server
- authentication and authorization
- organization-grade security
- API integrations
- external indicator pipelines
- validated ML workflow
- PDPA workflow and audit controls
