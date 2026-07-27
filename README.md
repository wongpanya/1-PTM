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
pytest
python scripts/validate_data.py
python scripts/privacy_check.py
```

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

## Production Roadmap

Production expansion should add:

- database server
- authentication and authorization
- organization-grade security
- API integrations
- external indicator pipelines
- validated ML workflow
- PDPA workflow and audit controls
