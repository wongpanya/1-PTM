# Phase 7: External Indicators and Governance

Phase 7 adds annual external indicator templates and prototype governance controls.

## External Indicators

Template file:

- `data/reference/annual_external_indicators_template.csv`

Required fields:

- `indicator_year`
- `indicator_type`
- `indicator_name`
- `geography_level`
- `geography_code`
- `field_code`
- `value`
- `unit`
- `source`
- `source_date`
- `update_date`
- `reliability_level`
- `note`

The template supports annual data that may vary by year, such as labor market demand, scholarship cost, inequality indicators, workforce demand, and other economic or social indicators.

## Governance Controls

Configured in `config/governance.yaml`:

- Prototype notice
- Minimum group size
- Role mockup: Admin, Analyst, Viewer
- Aggregate-only export policy
- Data use notice

## Privacy Controls

Implemented controls:

- Forbidden column detection
- PII-like pattern masking for phone, email, and 13-digit identifiers
- Minimum group size suppression
- Aggregate export validation
- Export log
- Audit log

## Role Behavior

- Admin can use import mockup and aggregate export.
- Analyst can view and export aggregate data.
- Viewer cannot import, export, or view audit logs.

## Acceptance Notes

- Export data must be aggregate-only.
- Small groups below the configured minimum group size are masked.
- The app displays a prototype notice.
- Audit and export events are written to local JSONL logs under `data/processed/`.
