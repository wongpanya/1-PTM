# Acceptance Tests

Phase 2 is accepted when:

- Repository opens locally.
- Git history exists.
- `AGENTS.md` exists and defines project rules.
- No real raw data with PII is committed.
- `README.md` includes install, run, and test commands.
- App skeleton has 7 pages.
- Config files exist for columns, cleaning, metrics, and risk rules.
- Tests exist for cleaning, metrics, risk score, and privacy.

Task 3 is accepted when:

- `scripts/import_data.py` imports no-PII CSV data into `data/processed/imported`.
- `scripts/build_database.py` builds a local SQLite database.
- `scripts/validate_data.py` writes validation reports.
- `scripts/privacy_check.py` passes.
- import/database actions append to audit log.
- generated processed data remains untracked by Git.

Phase 3 is accepted when:

- `streamlit run app.py` starts successfully.
- The app home page returns HTTP 200 locally.
- Seven page files exist under `pages/`.
- The database initializes all required Phase 3 tables.
- App pages use the SQLite data access layer.
- The app does not display row-level PII.
- Basic unit tests pass.

## Required Commands

```bash
python scripts/run_unit_tests.py
python scripts/validate_data.py
python scripts/privacy_check.py
```

Task 3 workflow:

```bash
python scripts/import_data.py
python scripts/build_database.py
python scripts/validate_data.py
python scripts/privacy_check.py
```

## Manual Checks

- Confirm `data/raw` contains only `README.md`.
- Confirm app labels are Thai-first.
- Confirm risk score explanations are visible.
- Confirm policy recommendation page states that recommendations are decision support only.
