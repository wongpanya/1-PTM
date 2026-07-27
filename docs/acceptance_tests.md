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

Phase 4 is accepted when:

- Raw data is not modified.
- Pipeline can be run repeatedly and produces the same cleaned dataset.
- Processing log exists.
- Before-after report exists.
- Validation issues are recorded instead of silently deleting records.
- Data quality scores are produced.
- Every core transformation has tests.

Phase 5 is accepted when:

- Overview, Data Quality, and Analytics pages render from aggregate no-PII data.
- KPI formulas and definitions are documented in `config/metrics.yaml`.
- Filters are applied through shared analytics functions.
- Dashboard tables and charts do not display row-level student records.
- Data Quality shows completeness, missing values, format or standard issues, and field readiness.
- Analytics shows completion, dropout proxy, employment, income, field-job fit, local fit, and comparisons by cohort/country/field.
- Metrics have unit tests that can be compared with SQL or spreadsheet samples.

Phase 6 is accepted when:

- Every risk score has component explanations, calculated timestamp, rule version, and limitations.
- Risk level Low, Medium, and High is derived from `config/risk_rules.yaml`.
- Graduation success uses rule-based status classes and documents ML readiness requirements.
- Policy recommendation rankings come from formulas and weights in `config/policy_recommendation.yaml`.
- Changing weights recalculates recommendation scores.
- Analysis results are separated from policy recommendation text.
- Recommendations include evidence columns, formula, weights, rule version, and limitations.
- No unsupported AI-generated recommendation text is used.

Phase 7 is accepted when:

- External indicator template has the required annual fields.
- PII masking removes forbidden columns and masks PII-like values.
- Viewer role cannot import data, export data, or view audit logs.
- Important import/export actions are written to audit/export logs.
- The system displays a Prototype notice.
- Groups smaller than the minimum group size are suppressed.
- Export is aggregate-only and privacy tests pass.

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
