import plotly.express as px
import streamlit as st

from src.analytics.metrics import (
    apply_filters,
    grouped_counts,
    load_analytics_dataset,
    metric_definitions,
    overview_metrics,
    remove_small_groups,
    top_counts,
)
from src.governance.privacy import minimum_group_size
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Overview")
render_header("Overview", "ภาพรวมผู้รับทุนและการกระจายของข้อมูลแบบไม่แสดงข้อมูลรายบุคคล")
render_database_status()


@st.cache_data(show_spinner=False)
def _load_data():
    return load_analytics_dataset()


df = _load_data()
definitions = metric_definitions()

with st.sidebar:
    st.subheader("ตัวกรอง")
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    province_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    country_options = sorted(df["current_country"].dropna().unique().tolist()) if "current_country" in df else []
    field_options = sorted(df["current_field_group"].dropna().unique().tolist()) if "current_field_group" in df else []
    cohorts = st.multiselect("รุ่น", cohort_options)
    provinces = st.multiselect("จังหวัด", province_options)
    countries = st.multiselect("ประเทศ", country_options)
    field_groups = st.multiselect("กลุ่มสาขา", field_options)

filtered = apply_filters(df, cohorts, provinces, countries, field_groups)
metrics = overview_metrics(filtered)

st.caption(f"ผลรายกลุ่มจะแสดงเฉพาะกลุ่มที่มีอย่างน้อย {minimum_group_size():,} ราย เพื่อคุ้มครองข้อมูล")

cols = st.columns(5)
cols[0].metric("ผู้รับทุนทั้งหมด", f"{metrics['total_recipients']:,}")
cols[1].metric("สำเร็จการศึกษา", f"{metrics['completion_count']:,}")
cols[2].metric("มีงานทำ", f"{metrics['employed_count']:,}")
cols[3].metric("ประเทศ", f"{metrics['countries_count']:,}")
cols[4].metric("กลุ่มสาขา", f"{metrics['field_groups_count']:,}")

st.caption("ตัวเลขทั้งหมดคำนวณจากชุดข้อมูล aggregate ที่ผ่าน Phase 4 หรือ sample no-PII และอ้างอิงนิยามใน config/metrics.yaml")

left, right = st.columns(2)
with left:
    cohort_counts = remove_small_groups(top_counts(filtered, "cohort", 20))
    st.subheader("จำนวนผู้รับทุนแต่ละรุ่น")
    st.plotly_chart(px.bar(cohort_counts, x="cohort", y="count", text_auto=True), width="stretch")

with right:
    province_counts = remove_small_groups(top_counts(filtered, "province", 20))
    st.subheader("การกระจายรายจังหวัด")
    st.plotly_chart(px.bar(province_counts, x="province", y="count", text_auto=True), width="stretch")

left, right = st.columns(2)
with left:
    district_counts = remove_small_groups(grouped_counts(filtered, ["province", "district"], 25))
    st.subheader("จังหวัดและอำเภอ")
    st.dataframe(district_counts, width="stretch", hide_index=True)

with right:
    country_counts = remove_small_groups(top_counts(filtered, "current_country", 20))
    st.subheader("การกระจายตามประเทศ")
    st.plotly_chart(px.bar(country_counts, x="current_country", y="count", text_auto=True), width="stretch")

field_country = remove_small_groups(grouped_counts(filtered, ["current_country", "current_field_group"], 30))
st.subheader("ประเทศและกลุ่มสาขา")
st.dataframe(field_country, width="stretch", hide_index=True)

with st.expander("นิยาม KPI ที่ใช้ในหน้านี้"):
    rows = []
    for key in [
        "total_recipients",
        "recipients_by_cohort",
        "completed_recipients",
        "employed_recipients",
        "countries_count",
        "field_groups_count",
    ]:
        item = definitions["metrics"][key]
        rows.append({"kpi": item["label_th"], "formula": item["formula"], "definition": item["definition_th"]})
    st.dataframe(rows, width="stretch", hide_index=True)
