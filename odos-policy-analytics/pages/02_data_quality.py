import plotly.express as px
import streamlit as st

from src.analytics.metrics import (
    data_quality_summary,
    load_analytics_dataset,
    load_phase4_issues,
    metric_definitions,
)
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Data Quality")
render_header("Data Quality", "ความพร้อมของข้อมูลรายฟิลด์สำหรับ Dashboard และ Model")
render_database_status()


@st.cache_data(show_spinner=False)
def _load_quality_inputs():
    return load_analytics_dataset(), load_phase4_issues(), metric_definitions()


df, issues_df, definitions = _load_quality_inputs()
quality = data_quality_summary(df, issues_df, definitions)

total_fields = len(quality)
dashboard_ready = int(quality["dashboard_ready"].sum())
model_ready = int(quality["model_ready"].sum())
needs_collection = len(definitions.get("data_quality", {}).get("fields_to_collect", []))
issue_total = int(quality["format_or_standard_issues"].sum())

cols = st.columns(5)
cols[0].metric("จำนวนฟิลด์", f"{total_fields:,}")
cols[1].metric("พร้อมใช้ Dashboard", f"{dashboard_ready:,}")
cols[2].metric("พร้อมใช้ Model", f"{model_ready:,}")
cols[3].metric("ค่าผิดรูปแบบ/ไม่ตรงมาตรฐาน", f"{issue_total:,}")
cols[4].metric("ควรเก็บเพิ่ม", f"{needs_collection:,}")

left, right = st.columns(2)
with left:
    missing = quality.sort_values("missing_count", ascending=False).head(20)
    st.subheader("จำนวนค่าว่างรายฟิลด์")
    st.plotly_chart(px.bar(missing, x="field", y="missing_count", text_auto=True), width="stretch")

with right:
    issues = quality.sort_values("format_or_standard_issues", ascending=False).head(20)
    st.subheader("จำนวนค่าผิดรูปแบบหรือไม่ตรงมาตรฐาน")
    st.plotly_chart(px.bar(issues, x="field", y="format_or_standard_issues", text_auto=True), width="stretch")

st.subheader("ความครบถ้วนรายฟิลด์")
st.dataframe(
    quality[
        [
            "field",
            "complete_count",
            "missing_count",
            "completeness_rate",
            "format_or_standard_issues",
            "dashboard_ready",
            "model_ready",
            "needs_more_collection",
        ]
    ],
    width="stretch",
    hide_index=True,
)

left, right, third = st.columns(3)
with left:
    st.subheader("ฟิลด์พร้อมใช้กับ Dashboard")
    st.dataframe(
        quality.loc[quality["dashboard_ready"], ["field", "completeness_rate", "format_or_standard_issues"]],
        width="stretch",
        hide_index=True,
    )

with right:
    st.subheader("ฟิลด์พร้อมใช้กับ Model")
    st.dataframe(
        quality.loc[quality["model_ready"], ["field", "completeness_rate", "format_or_standard_issues"]],
        width="stretch",
        hide_index=True,
    )

with third:
    st.subheader("ฟิลด์ที่ต้องเก็บเพิ่มเติม")
    st.dataframe(
        [{"field": field} for field in definitions.get("data_quality", {}).get("fields_to_collect", [])],
        width="stretch",
        hide_index=True,
    )

with st.expander("นิยาม Data Quality"):
    st.markdown(
        """
- Completeness: สัดส่วนรายการที่ไม่เป็นค่าว่างในแต่ละฟิลด์
- ค่าผิดรูปแบบ/ไม่ตรงมาตรฐาน: จำนวน issue จาก Phase 4 validation ที่ผูกกับฟิลด์นั้น
- Dashboard Ready: ฟิลด์ที่นิยามไว้ใน `config/metrics.yaml` ว่าใช้สรุปผลบน Dashboard ได้
- Model Ready: ฟิลด์ที่นิยามไว้ใน `config/metrics.yaml` ว่าเป็น candidate สำหรับแบบจำลองใน Phase ถัดไป
"""
    )
