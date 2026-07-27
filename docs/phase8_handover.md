# Phase 8 Handover

## Delivery status

Phase 8 closes the Prototype testing and handover work. It demonstrates that the current sample can be imported, cleaned, validated, analyzed, scored, governed, and shown through the Streamlit interface without exposing direct identifiers.

Run the automated acceptance suite:

```bash
python scripts/phase8_acceptance.py
```

Run the full project checks:

```bash
python scripts/run_unit_tests.py
python scripts/validate_data.py
python scripts/privacy_check.py
```

## Executive trial scenario

1. Start the app with `streamlit run app.py`.
2. Open Overview and record the total recipients, completion count, employment count, country count, and field-group count.
3. Apply one cohort and one province filter. Confirm that all KPI values and charts update to the filtered population.
4. Open Data Quality and review missing fields, validation issues, dashboard readiness, and model readiness.
5. Open Analytics and compare completion, employment, income, field-job fit, and local fit by cohort or field group.
6. Open Risk & Forecast and inspect the score, risk level, triggered components, calculation time, rule version, and limitations.
7. Open Policy Recommendation, change a weight, and confirm that ranking scores recalculate. Treat the result as analysis for expert review, not an automatic funding decision.
8. Open External Indicators as Admin and verify that the annual template and CSV schema check are available. Switch to Viewer and confirm import is unavailable.
9. Open Governance, verify the Prototype notice, minimum group-size masking, audit/export visibility, and aggregate-only export behavior.

## Known limitations

- This is a local SQLite and Streamlit Prototype, not a production database or multi-user service.
- Role selection is a mockup; production authentication, authorization, and identity lifecycle are not implemented.
- External indicators are template/sample data. The production version needs verified annual sources, owners, update schedules, and quality agreements.
- Area recommendation does not invent placeholder values for inequality need or workforce demand. Until verified indicators are supplied and mapped, the Area Ranking calculates only from available recipient-data evidence and clearly reports the excluded external weight.
- Risk scores are rule-based prototypes. Rule weights and thresholds require formal expert approval before operational use.
- Graduation forecasting does not enable machine learning. A validated train/test design, leakage review, calibration, and monitoring are still required.
- Upload validation is a prototype schema check. It does not yet provide a production staging area, approval workflow, rollback, or asynchronous processing.
- Export is aggregate-only, but production deployment still needs server-side authentication, authorization, encryption, retention rules, and incident response.
- The current data quality result includes warnings that must be resolved or accepted by the data owner before policy use.

## Additional data to procure

- Official annual labor-market demand by field and geography, with source date and reliability level.
- Verified annual scholarship cost and living-cost indicators by destination or geography.
- Official inequality and local development indicators at the level used for policy analysis.
- Follow-up outcomes with consistent reporting dates, employment sector, occupation group, income band, and return-to-area status.
- A maintained geography and field taxonomy with codes, effective dates, and mapping history.
- Expert-approved risk rules, KPI definitions, thresholds, recommendation weights, and sign-off records.
- Production security requirements: user directory, role ownership, audit retention, encryption, backup, recovery, and PDPA operating procedures.

## Phase 9 entry criteria

Move to Production planning only after the data owner signs off definitions and data quality, the policy owner signs off rules and recommendations, legal/governance owners approve the data-use design, and a funded hosting/security plan exists.
