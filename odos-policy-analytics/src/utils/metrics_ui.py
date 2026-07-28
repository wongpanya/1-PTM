from __future__ import annotations

import streamlit as st


def render_metric_card_styles() -> None:
    st.html(
        """
        <style>
        div[data-testid="stMetric"] {
            position: relative;
            min-height: 7.35rem;
            padding: 1.05rem 1.1rem 0.95rem;
            overflow: hidden;
            background: linear-gradient(180deg, #FFFFFF 0%, #FFFFFF 70%, #F3EDFF 100%);
            border: 1px solid #E5EAF2 !important;
            border-radius: 8px;
            box-shadow: 0 6px 18px rgba(31, 41, 55, 0.05);
        }

        div[data-testid="stMetric"]::before {
            display: none;
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B;
            font-size: 0.84rem;
            font-weight: 600;
            line-height: 1.35;
        }

        div[data-testid="stMetricLabel"]::before {
            display: inline-block;
            width: 0.55rem;
            height: 0.55rem;
            margin-right: 0.45rem;
            border-radius: 999px;
            background-color: #7C3AED;
            content: "";
        }

        div[data-testid="stMetricValue"] {
            color: #1F2937;
            font-size: 1.72rem;
            font-weight: 700;
            line-height: 1.15;
            overflow-wrap: anywhere;
        }

        div[data-testid="stMetricDelta"] {
            width: fit-content;
            max-width: 100%;
            margin-top: 0.4rem;
            padding: 0.16rem 0.48rem;
            border: 1px solid #E5EAF2;
            border-radius: 999px;
            background-color: rgba(255, 255, 255, 0.88);
            font-size: 0.76rem;
            font-weight: 500;
            line-height: 1.3;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 2)
            div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #FFFFFF 70%, #E8FAFD 100%);
            border-color: #D9EEF3 !important;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 2)
            div[data-testid="stMetric"]::before {
            display: none;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 2)
            div[data-testid="stMetricLabel"]::before {
            background-color: #06B6D4;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 3)
            div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #FFFFFF 70%, #E9FBF4 100%);
            border-color: #D8F0E6 !important;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 3)
            div[data-testid="stMetric"]::before {
            display: none;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 3)
            div[data-testid="stMetricLabel"]::before {
            background-color: #10B981;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 4)
            div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #FFFFFF 70%, #FFF7E6 100%);
            border-color: #F3E6C8 !important;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 4)
            div[data-testid="stMetric"]::before {
            display: none;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 4)
            div[data-testid="stMetricLabel"]::before {
            background-color: #F59E0B;
        }

        @media (max-width: 768px) {
            div[data-testid="stMetric"] {
                min-height: 7.1rem;
            }

            div[data-testid="stMetricValue"] {
                font-size: 1.52rem;
            }
        }
        </style>
        """
    )


def render_metric_grid(items: list[dict], *, columns: int = 4) -> None:
    """Render a balanced, formal KPI grid with up to four cards per row."""
    if not items:
        return
    render_metric_card_styles()
    columns = max(1, min(columns, 4))
    for start in range(0, len(items), columns):
        row_items = items[start : start + columns]
        row = st.columns(len(row_items), gap="small")
        for column, item in zip(row, row_items, strict=True):
            column.metric(
                label=item["label"],
                value=item["value"],
                delta=item.get("delta"),
                delta_color=item.get("delta_color", "gray"),
                delta_arrow=item.get("delta_arrow", "off"),
                help=item.get("help"),
                border=True,
                height="stretch",
            )
