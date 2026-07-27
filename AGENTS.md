# ODOS Policy Analytics Development Rules

## Project Goal

Build an explainable prototype for scholarship policy analytics. The system demonstrates how ODOS scholarship data can support policy analysis, not automatic scholarship allocation.

## Mandatory Rules

- Never expose names, phone numbers, detailed addresses, contract identifiers, certificate/document numbers, or officer notes in the app, samples, logs, exports, screenshots, or documentation.
- Do not modify files in `data/raw`.
- Do not commit real raw Excel files or any dataset containing direct PII.
- Use `phase1_outputs` from the parent workspace only as a private local source; public repository data must be no-PII.
- All cleaning rules must come from `config/cleaning_rules.yaml`.
- All metrics must be traceable to `config/metrics.yaml`.
- Risk scores must show component scores and explanations.
- Do not generate policy claims unsupported by available data.
- Display aggregate results by default.
- Add tests for every data transformation or risk scoring rule.
- Use Thai labels in the user interface. English technical labels may be used in module names and chart titles when helpful.
- Keep code modular and documented.
- Keep recommendations as decision support, not automatic decisions.
- Show data limitations whenever risk, forecast, or policy recommendation results are displayed.

## Repository Structure Rules

- `app.py` controls app entry and shared navigation.
- `pages/` contains Streamlit pages only.
- `src/ingestion/` contains data loading logic.
- `src/cleaning/` contains cleaning and normalization logic.
- `src/validation/` contains data quality and privacy validation.
- `src/analytics/` contains metrics and aggregate analytics.
- `src/risk/` contains risk score logic.
- `src/policy/` contains recommendation logic.
- `src/governance/` contains PII masking, audit, and access policy logic.
- `src/utils/` contains shared helpers.
- `config/` is the source of truth for mappings, rules, metrics, and risk weights.
- `tests/` must cover cleaning, metrics, risk score, and privacy checks.
- `data/raw/` is local-only and must not contain committed real data.
- `data/sample/` may contain no-PII development and validation samples only.

## Validation

Before completing a development task, run:

```bash
pytest
python scripts/validate_data.py
python scripts/privacy_check.py
```

If dependencies are not installed yet, create the environment first:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Definition of Done

- Code runs locally.
- Tests pass.
- Privacy check passes.
- No direct PII appears in committed sample data.
- Dashboard defaults to aggregate results.
- Risk and recommendation output includes explanations.
- README commands stay current.
