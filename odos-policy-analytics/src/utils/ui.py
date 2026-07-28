from __future__ import annotations

import streamlit as st

from src.ingestion.data_access import database_health, database_status
from src.utils.charts import POLICY_CHART_COLORS, style_policy_chart
from src.utils.config import load_yaml
from src.utils.metrics_ui import render_metric_card_styles


def _render_metric_card_styles() -> None:
    st.html(
        """
        <style>
        div[data-testid="stMetric"] {
            position: relative;
            min-height: 7.5rem;
            padding: 1.05rem 1.05rem 0.9rem;
            overflow: hidden;
            background: linear-gradient(135deg, #FFFFFF 0%, #F1EEFF 100%);
            border: 1px solid #DDD8FF !important;
            border-radius: 8px;
            box-shadow: 0 8px 22px rgba(52, 40, 135, 0.07);
        }

        div[data-testid="stMetric"]::before {
            position: absolute;
            inset: 0 0 auto;
            height: 4px;
            background: linear-gradient(90deg, #4318FF 0%, #7B8CFF 100%);
            content: "";
        }

        div[data-testid="stMetricLabel"] {
            color: #707EAE;
            font-size: 0.84rem;
            font-weight: 600;
            line-height: 1.3;
        }

        div[data-testid="stMetricValue"] {
            color: #1B2559;
            font-size: 1.7rem;
            font-weight: 700;
            line-height: 1.15;
            overflow-wrap: anywhere;
        }

        div[data-testid="stMetricDelta"] {
            width: fit-content;
            max-width: 100%;
            margin-top: 0.35rem;
            padding: 0.18rem 0.5rem;
            border-radius: 999px;
            background-color: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(112, 126, 174, 0.16);
            font-size: 0.78rem;
            font-weight: 600;
            line-height: 1.25;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 2)
            div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #FFFFFF 0%, #EAF2FF 100%);
            border-color: #D8E2FF !important;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 2)
            div[data-testid="stMetric"]::before {
            background: linear-gradient(90deg, #5B4BFF 0%, #64B8ED 100%);
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 3)
            div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #FFFFFF 0%, #E9FAFF 100%);
            border-color: #CDEFFB !important;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 3)
            div[data-testid="stMetric"]::before {
            background: linear-gradient(90deg, #56BFE8 0%, #7B8CFF 100%);
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 4)
            div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #FFFFFF 0%, #EEF0FF 100%);
            border-color: #D7DBFF !important;
        }

        div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 4)
            div[data-testid="stMetric"]::before {
            background: linear-gradient(90deg, #6F6CFF 0%, #59C9EE 100%);
        }

        @media (max-width: 768px) {
            div[data-testid="stMetric"] {
                min-height: 7.25rem;
            }

            div[data-testid="stMetricValue"] {
                font-size: 1.55rem;
            }
        }
        </style>
        """
    )


def configure_page(page_title: str) -> None:
    config = load_yaml("config/app_config.yaml")
    app_title = config["app"]["title"]
    st.set_page_config(page_title=f"{page_title} | {app_title}", page_icon="ODOS", layout="wide")
    render_metric_card_styles()


def render_metric_grid(items: list[dict], *, columns: int = 4) -> None:
    """Render a balanced KPI grid with no more than four cards per row."""
    if not items:
        return
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


def render_header(title: str, caption: str | None = None) -> None:
    st.title(title)
    if caption:
        st.caption(caption)
    st.info(
        "Prototype นี้เป็นระบบสนับสนุนการวิเคราะห์เชิงนโยบาย ไม่ใช่ระบบตัดสินใจจัดสรรทุนอัตโนมัติ "
        "และยังไม่แสดงข้อมูลรายบุคคลหรือข้อมูลที่เป็น PII"
    )
def render_database_status() -> bool:
    ok, message = database_health()
    if ok:
        st.success(message)
    else:
        st.error(message)
        st.warning("กรุณารัน `python scripts/build_database.py` หรือ launcher Task 3 ก่อน")
    return ok


def render_table_status() -> None:
    status = database_status()
    st.subheader("สถานะตารางฐานข้อมูลกลาง")
    rows = [
        {
            "table": table,
            "status": "ready" if table in status["available_tables"] else "missing",
            "rows": status["table_counts"].get(table, 0),
        }
        for table in status["expected_tables"]
    ]
    st.dataframe(rows, width="stretch", hide_index=True)
