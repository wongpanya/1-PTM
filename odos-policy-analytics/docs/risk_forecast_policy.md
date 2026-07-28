# Phase 6: Risk, Forecast, and Policy Recommendation

Phase 6 implements explainable prototype logic for risk scoring, graduation status classification, and policy recommendation ranking.

## Risk Score

The first version is rule-based. Rules, weights, levels, version, and limitations are stored in `config/risk_rules.yaml`.

The system reports:

- Total risk score
- Risk level: Low, Medium, High
- Triggered components and component scores
- Calculation timestamp
- Rule version
- Expert approval status
- Limitations

The configured score weights are prototype values and must be reviewed by project experts before production use.

## Graduation Success

The prototype implements rule-based classification:

- On-time completion
- Delayed completion
- Studying
- Over-duration risk
- Exited
- Unknown

Explainable ML is documented as a later-stage option only. It is not enabled in this prototype phase because official outcome definitions, cohort/time-based train-test split, and leakage controls must be locked first.

## Policy Recommendation

Policy recommendations are rankings derived from data and configurable weights in `config/policy_recommendation.yaml`.

The system separates:

- Analysis result: measured rates, records, and computed score
- Policy recommendation: suggested consideration text with limitations

Recommendation types:

- Field Recommendation
- Area-based Allocation

Every output includes formula, weights, rule version, evidence columns, and limitations.

## Constraints

- No recommendation is generated from unsupported AI text.
- Changing weights recalculates scores immediately.
- External inequality and workforce demand are placeholders until Phase 7 external indicators are populated.
- Results support policy discussion, not automatic allocation.
