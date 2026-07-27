import streamlit as st

from src.governance.privacy import FORBIDDEN_COLUMNS
from src.ingestion.data_access import scalar
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Governance")
render_header("Governance", "พื้นที่ธรรมาภิบาลข้อมูลและ privacy controls")

if render_database_status():
    audit_count = scalar("SELECT COUNT(*) FROM audit_logs") or 0
    import_count = scalar("SELECT COUNT(*) FROM data_import_log") or 0
    cols = st.columns(2)
    cols[0].metric("audit logs", f"{int(audit_count):,}")
    cols[1].metric("data import logs", f"{int(import_count):,}")

st.subheader("ข้อมูลที่ห้ามแสดงหรือ export")
st.dataframe([{"forbidden_column": column} for column in sorted(FORBIDDEN_COLUMNS)], use_container_width=True, hide_index=True)
