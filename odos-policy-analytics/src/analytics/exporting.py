from __future__ import annotations

import pandas as pd

from src.analytics.metrics import (
    income_summary,
    outcome_by_group,
    overview_metrics,
)


EXPORT_DIMENSIONS = [
    "analysis_year",
    "cohort",
    "region",
    "province",
    "district",
    "current_country",
    "current_field_group",
    "current_field",
    "standardized_university_name",
    "employer_sector_code",
]


def build_dashboard_export(df: pd.DataFrame, page_name: str) -> pd.DataFrame:
    """Build a privacy-safe long-form aggregate report from the filtered dataset."""
    metrics = overview_metrics(df)
    income = income_summary(df)
    rows = [
        _summary_row(page_name, "total_recipients", metrics["total_recipients"], metrics["total_recipients"]),
        _rate_row(page_name, "completion_rate", metrics["completion_rate"], metrics["completion_count"], len(df)),
        _rate_row(page_name, "dropout_rate", metrics["dropout_rate"], metrics["dropout_count"], len(df)),
        _rate_row(page_name, "termination_rate", metrics["termination_rate"], metrics["termination_count"], len(df)),
        _rate_row(
            page_name,
            "scholarship_risk_rate",
            metrics["scholarship_risk_rate"],
            metrics["scholarship_risk_count"],
            len(df),
        ),
        _rate_row(page_name, "employment_rate", metrics["employment_rate"], metrics["employed_count"], len(df)),
        _summary_row(
            page_name,
            "average_income",
            income["average_income"],
            income["records_with_income"],
            income["records_with_income"],
        ),
        _summary_row(
            page_name,
            "median_income",
            income["median_income"],
            income["records_with_income"],
            income["records_with_income"],
        ),
        _rate_row(
            page_name,
            "field_job_fit_rate",
            metrics["field_job_fit_rate"],
            metrics["field_job_fit_count"],
            metrics["field_job_fit_denominator"],
        ),
        _rate_row(
            page_name,
            "local_fit_rate",
            metrics["local_fit_rate"],
            metrics["local_fit_count"],
            metrics["local_fit_denominator"],
        ),
        _rate_row(
            page_name,
            "tracking_gap_rate",
            metrics["tracking_risk_rate"],
            metrics["tracking_risk_count"],
            len(df),
        ),
    ]

    for dimension in EXPORT_DIMENSIONS:
        if dimension not in df:
            continue
        grouped = outcome_by_group(df, dimension)
        for record in grouped.to_dict("records"):
            category = record[dimension]
            count = int(record["count"])
            rows.append(
                {
                    "page": page_name,
                    "section": "breakdown",
                    "dimension": dimension,
                    "category": category,
                    "metric": "recipient_count",
                    "value": count,
                    "count": count,
                    "denominator": count,
                }
            )
            for metric in (
                "completion_rate",
                "dropout_rate",
                "termination_rate",
                "scholarship_risk_rate",
                "employment_rate",
                "tracking_gap_rate",
            ):
                rows.append(
                    {
                        "page": page_name,
                        "section": "breakdown",
                        "dimension": dimension,
                        "category": category,
                        "metric": metric,
                        "value": record[metric],
                        "count": count,
                        "denominator": count,
                    }
                )
    return pd.DataFrame(rows)


def _summary_row(
    page_name: str,
    metric: str,
    value: float | int,
    count: int,
    denominator: int | None = None,
) -> dict:
    return {
        "page": page_name,
        "section": "summary",
        "dimension": "all_filtered_records",
        "category": "ทั้งหมด",
        "metric": metric,
        "value": value,
        "count": int(count),
        "denominator": int(denominator if denominator is not None else count),
    }


def _rate_row(page_name: str, metric: str, value: float, count: int, denominator: int) -> dict:
    return _summary_row(page_name, metric, value, count, denominator)
