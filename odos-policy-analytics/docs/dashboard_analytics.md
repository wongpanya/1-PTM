# Phase 5: Dashboard and Analytics

Phase 5 turns the Phase 4 cleaned no-PII dataset into aggregate dashboards for prototype policy analysis.

## Data Source

The dashboard reads `data/processed/phase4/cleaned_modeling_dataset_no_pii.csv` when available. If Phase 4 has not been run in a fresh environment, it falls back to `data/sample/modeling_dataset_no_pii.csv`.

No raw Excel file is read during dashboard runtime.

## Pages

### Overview

- Total scholarship recipients
- Recipients by cohort
- Completed recipients
- Employed recipients
- Number of countries and field groups
- Distribution by province and district
- Distribution by country and field group

### Data Quality

- Completeness by field
- Missing values by field
- Format or standard issues from Phase 4 validation
- Fields ready for dashboard use
- Fields ready for model use
- Fields that should be collected in later phases

### Analytics

- Completion Rate
- Dropout or scholarship-risk Rate
- Employment Rate
- Selectable dashboard views: KPI comparison bar chart, donut proportion chart, aggregate income box plot, cohort outcome line chart, and country-field heatmap
- Field-Job Fit
- Local Development Fit
- Outcome comparison by cohort
- Comparison by country and field group

## Metric Traceability

All KPI definitions, formulas, source columns, and limitations are documented in `config/metrics.yaml`.

## Privacy

The pages display aggregate tables and charts only. The shared analytics loader removes obvious forbidden display columns before dashboard use. Box plots use aggregate quartile statistics rather than row-level income values, and all grouped views exclude groups below the configured minimum size.

## Limitations

- The dashboard summarizes available prototype data only.
- Dropout Rate uses the Phase 4 scholarship-risk target as a proxy until official dropout status definitions are formally confirmed.
- Income charts use converted monthly income estimates and exclude missing or non-convertible values.
- Results should support policy discussion, not automated scholarship allocation.
