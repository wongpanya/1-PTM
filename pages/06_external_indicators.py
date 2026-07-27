import hashlib

import pandas as pd
import streamlit as st

from src.governance.audit import append_audit_event
from src.governance.privacy import aggregate_csv_bytes, append_export_log, suppress_small_groups
from src.utils.config import PROJECT_ROOT, load_yaml
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("External Indicators")
render_header("External Indicators", "ข้อมูลเสริมรายปีสำหรับต้นทุนทุน ตลาดแรงงาน เศรษฐกิจ สังคม และพื้นที่")
render_database_status()

governance = load_yaml("config/governance.yaml")
roles = governance["roles"]

with st.sidebar:
    role = st.selectbox("Role Mockup", list(roles.keys()), index=2)
    st.caption(roles[role]["description_th"])

st.info(governance["prototype_notice_th"])

template_path = PROJECT_ROOT / "data/reference/annual_external_indicators_template.csv"
template_df = pd.read_csv(template_path)

cols = st.columns(4)
cols[0].metric("Template Fields", f"{len(template_df.columns):,}")
cols[1].metric("Sample Rows", f"{len(template_df):,}")
cols[2].metric("Minimum Group Size", governance["minimum_group_size"])
cols[3].metric("Role", role)

st.subheader("Template ข้อมูลเสริมรายปี")
st.dataframe(template_df, width="stretch", hide_index=True)

st.subheader("Field Definition")
field_rows = [
    {"field": "indicator_year", "description": "ปีของตัวชี้วัด เช่น 2569"},
    {"field": "indicator_type", "description": "ประเภทตัวชี้วัด เช่น labor_market, cost, inequality"},
    {"field": "indicator_name", "description": "ชื่อตัวชี้วัด"},
    {"field": "geography_level", "description": "ระดับพื้นที่ เช่น national, province, district"},
    {"field": "geography_code", "description": "รหัสพื้นที่ เช่น TH หรือรหัสจังหวัด"},
    {"field": "field_code", "description": "รหัสสาขาหรือกลุ่มอาชีพ เช่น ICT-AI"},
    {"field": "value", "description": "ค่าตัวชี้วัด"},
    {"field": "unit", "description": "หน่วยวัด"},
    {"field": "source", "description": "หน่วยงานเจ้าของข้อมูล"},
    {"field": "source_date", "description": "วันที่เผยแพร่"},
    {"field": "update_date", "description": "วันที่นำเข้าระบบ"},
    {"field": "reliability_level", "description": "ระดับความน่าเชื่อถือ เช่น official, draft"},
    {"field": "note", "description": "หมายเหตุ"},
]
st.dataframe(field_rows, width="stretch", hide_index=True)

indicator_summary = template_df.groupby(["indicator_year", "indicator_type", "geography_level"], dropna=False).size().reset_index(name="count")
indicator_summary = suppress_small_groups(indicator_summary, min_size=1)

st.subheader("Aggregate Summary")
st.dataframe(indicator_summary, width="stretch", hide_index=True)

if roles[role]["can_import"]:
    st.subheader("Import Mockup")
    uploaded = st.file_uploader("นำเข้า external indicators CSV ตาม template", type=["csv"])
    if uploaded is not None:
        imported = pd.read_csv(uploaded)
        missing = [column for column in template_df.columns if column not in imported.columns]
        if missing:
            st.error(f"ยังขาดคอลัมน์บังคับ: {', '.join(missing)}")
        else:
            upload_fingerprint = hashlib.sha256(uploaded.getvalue()).hexdigest()
            if st.session_state.get("external_indicator_import_fingerprint") != upload_fingerprint:
                append_audit_event("external_indicator_import_mockup", {"role": role, "rows": len(imported), "columns": list(imported.columns)})
                st.session_state["external_indicator_import_fingerprint"] = upload_fingerprint
                st.success("ตรวจ schema ผ่านและบันทึก import log mockup แล้ว")
            else:
                st.info("ไฟล์นี้ผ่านการตรวจ schema แล้วใน session ปัจจุบัน")
else:
    st.warning("Role นี้ไม่เห็นเมนูนำเข้าข้อมูล")

if roles[role]["can_export_aggregate"]:
    export_name = "external_indicator_summary.csv"
    export_data = aggregate_csv_bytes(indicator_summary, export_name, role, log_export=False)
    if st.download_button(
        "Export Aggregate CSV",
        data=export_data,
        file_name=export_name,
        mime="text/csv",
    ):
        append_export_log(export_name, role, len(indicator_summary), list(indicator_summary.columns))
else:
    st.caption("Role นี้ไม่มีสิทธิ์ export ข้อมูล")
