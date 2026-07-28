# Phase 5: Dashboard and Analytics

Phase 5 turns the Phase 4 cleaned no-PII dataset into aggregate dashboards for prototype policy analysis.

## Data Source

The dashboard reads `data/processed/phase4/cleaned_modeling_dataset_no_pii.csv` when available. If Phase 4 has not been run in a fresh environment, it falls back to `data/sample/modeling_dataset_no_pii.csv`.

No raw Excel file is read during dashboard runtime.

## Pages

### Overview

- Shared filters for analysis year, cohort, region, province, district, country, field group, detailed field, standardized university, and employer-sector code
- Population views by cohort, sex, region, province, and district
- Education views by scholarship condition status, country, field group, and normalized current university
- Post-scholarship views for employment type, employer-sector code, aggregate income, field-job fit, and local-development fit
- Area comparison for recipient volume, completion, and employment outcomes
- Outcome trends by cohort
- Follow-up data gaps by cohort, province, country, and field group
- Aggregate CSV export reflects the active filters and is limited by the role mockup

`analysis_year` is the study-start year. The graduation-expected year and work-start year are used as fallbacks, in that order, when the study-start date is missing.

`standardized_university_name` applies whitespace normalization and approved alias mappings. It is not yet an official university registry code.

`employer_sector_code` is derived from employment type and does not expose employer names:

- `GOV`
- `PRIVATE`
- `SOE`
- `SELF`
- `NPO`
- `OTHER`

### Data Quality

- Dashboard, Analytics, Policy, and ML readiness scorecards
- Completeness, validity, issue rate, and quality score by field
- Cleaning action and reason by field
- ML feature, ML target, aggregate-only, and leakage-risk classification
- Readiness comparison by cohort, province, country, and field group
- Fields that should be collected in later phases
- Aggregate issue summary without student identifiers

### Analytics

- Completion Rate
- Dropout Rate, Termination Rate, and Scholarship Risk Rate as separate KPIs
- Employment Rate
- Average and median valid monthly income with the number of records used
- Field-Job Fit and Local Fit rates with numerator and denominator
- Four selectable modes:
  - `Executive View` for KPI bullet charts, an aggregate funnel, and cohort outcome gaps
  - `Guided Visualization` for choosing the policy question before the chart
  - `Custom Visualization` for analyst-controlled chart and dimension selection
  - `Data Quality View` for visualization readiness and missingness analysis
- Guided questions cover ranking, proportion, trend, distribution, relationship, pathway, geography, missingness, and multi-KPI comparison.
- Supported charts include Dot Plot, Treemap, 100% Stacked Bar, Donut, Line, Bubble, Aggregate Box Plot, Aggregate Histogram, Heatmap, Sankey, Funnel, and Dumbbell.
- Every guided recommendation displays the reason, alternatives, required-field readiness, and interpretation warning.
- Donut is automatically replaced with a 100% Stacked Bar when more than five categories are present.
- Field-Job Fit
- Local Development Fit
- Outcome comparison by cohort
- Comparison by country and field group
- Aggregate CSV export reflects the active filters and records the completed export event

## Metric Traceability

All KPI definitions, formulas, source columns, and limitations are documented in `config/metrics.yaml`.

## Privacy

The pages display aggregate tables and charts only. The shared analytics loader removes obvious forbidden display columns before dashboard use. Box plots use aggregate quartile statistics, histograms use aggregate bin counts, and Sankey charts use aggregate flows. All grouped views exclude groups below the configured minimum size.

Proportion denominators are calculated before small groups are suppressed, so
displayed percentages do not overstate the remaining visible categories.

Visualization recommendations and compatibility rules are defined in
`config/visualization.yaml`.

## Limitations

- The dashboard summarizes available prototype data only.
- Readiness scores measure data availability and validation quality, not causal validity or final model performance.
- ML targets remain rule-based prototype targets until domain experts certify the definitions.
- Dropout Rate uses the Phase 4 scholarship-risk target as a proxy until official dropout status definitions are formally confirmed.
- Income charts use converted monthly income estimates and exclude missing or non-convertible values.
- Income KPIs and distributions exclude values outside the configured validation range of 0-500,000 baht per month.
- University standardization is text-based; Production still needs official institution reference codes.
- Employer-sector codes describe sectors only and never expose employer or agency names.
- Results should support policy discussion, not automated scholarship allocation.
