from __future__ import annotations

import streamlit as st

from src.ingestion.data_access import database_health, database_status
from src.utils.config import load_yaml


def configure_page(page_title: str) -> None:
    config = load_yaml("config/app_config.yaml")
    app_title = config["app"]["title"]
    st.set_page_config(page_title=f"{page_title} | {app_title}", page_icon="ODOS", layout="wide")


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
    st.dataframe(rows, use_container_width=True, hide_index=True)
