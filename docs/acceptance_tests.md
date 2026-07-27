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

## Required Commands

```bash
pytest
python scripts/validate_data.py
python scripts/privacy_check.py
```

## Manual Checks

- Confirm `data/raw` contains only `README.md`.
- Confirm app labels are Thai-first.
- Confirm risk score explanations are visible.
- Confirm policy recommendation page states that recommendations are decision support only.
