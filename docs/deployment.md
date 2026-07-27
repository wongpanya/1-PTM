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
