# Deployment

## Recommended Free Deployment Options

1. Streamlit Community Cloud
2. Hugging Face Spaces

## Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a new Streamlit app.
3. Set main file path to `app.py`.
4. Confirm `requirements.txt` is detected.
5. Deploy.

## Environment Variables

Use `.env.example` as the reference:

```text
APP_ENV=development
ODOS_DATA_SOURCE=data/sample/development_sample.csv
ODOS_VALIDATION_DATA=data/sample/validation_data.csv
ODOS_ALLOW_UPLOAD=false
ODOS_PRIVACY_MODE=strict
```

## Data Safety

- Do not upload raw Excel files to public hosting.
- Use no-PII sample files only.
- Disable upload in public prototype demos unless an admin validation workflow exists.

## Local Handover Test

Run the complete Prototype acceptance check from the repository root:

```bash
python scripts/phase8_acceptance.py
```

This check does not publish data. It uses the no-PII sample and the private Phase 1 raw copy already configured for the local prototype. It verifies the data pipeline, KPI and filter behavior, rule-based risk output, traceable policy ranking, role-based aggregate export, privacy artifacts, source syntax, and runtime dependencies.

For a clean-machine rehearsal, create a new virtual environment and run:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/phase8_acceptance.py
streamlit run app.py
```

The Prototype must be hosted only with no-PII samples. Raw Excel data and any direct identifiers remain outside the repository and must not be uploaded to a public service.
