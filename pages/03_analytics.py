import plotly.express as px
import streamlit as st

from src.analytics.metrics import (
    apply_filters,
    grouped_counts,
    income_summary,
    load_analytics_dataset,
    metric_definitions,
    overview_metrics,
    rate_by_group,
    remove_small_groups,
    top_counts,
)
from src.governance.privacy import minimum_group_size
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Analytics")
render_header("Analytics", "KPI และการเปรียบเทียบผลลัพธ์จากข้อมูลที่มีอยู่ใน Prototype")
render_database_status()


@st.cache_data(show_spinner=False)
def _load_data():
    return load_analytics_dataset()


df = _load_data()
definitions = metric_definitions()

with st.sidebar:
    st.subheader("ตัวกรอง")
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    country_options = sorted(df["current_country"].dropna().unique().tolist()) if "current_country" in df else []
    field_options = sorted(df["current_field_group"].dropna().unique().tolist()) if "current_field_group" in df else []
    provinces_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    cohorts = st.multiselect("รุ่น", cohort_options)
    countries = st.multiselect("ประเทศ", country_options)
    field_groups = st.multiselect("กลุ่มสาขา", field_options)
    provinces = st.multiselect("จังหวัด", provinces_options)

filtered = apply_filters(df, cohorts, provinces, countries, field_groups)
metrics = overview_metrics(filtered)
income = income_summary(filtered)

st.caption(f"ผลรายกลุ่มจะแสดงเฉพาะกลุ่มที่มีอย่างน้อย {minimum_group_size():,} ราย เพื่อคุ้มครองข้อมูล")

cols = st.columns(5)
cols[0].metric("Completion Rate", f"{metrics['completion_rate']:.2f}%")
cols[1].metric("Dropout Rate", f"{metrics['scholarship_risk_rate']:.2f}%")
cols[2].metric("Employment Rate", f"{metrics['employment_rate']:.2f}%")
cols[3].metric("Median Income", f"{income['median_income']:,.0f}")
cols[4].metric("Income Records", f"{income['records_with_income']:,}")

left, right = st.columns(2)
with left:
    cohort_completion = remove_small_groups(rate_by_group(filtered, "cohort", "target_graduation_success"))
    st.subheader("Completion Rate ตามรุ่น")
    st.plotly_chart(px.bar(cohort_completion, x="cohort", y="rate", text_auto=True), width="stretch")

with right:
    cohort_employment = remove_small_groups(rate_by_group(filtered, "cohort", "target_employment_ready"))
    st.subheader("Employment Rate ตามรุ่น")
    st.plotly_chart(px.bar(cohort_employment, x="cohort", y="rate", text_auto=True), width="stretch")

left, right = st.columns(2)
with left:
    income_df = filtered[["income_monthly_est"]].dropna() if "income_monthly_est" in filtered else filtered
    st.subheader("Income Distribution")
    if "income_monthly_est" in income_df and not income_df.empty:
        st.plotly_chart(px.histogram(income_df, x="income_monthly_est", nbins=30), width="stretch")
    else:
        st.info("ไม่มีข้อมูลรายได้ที่แปลงเป็นตัวเลขได้ในชุดที่กรอง")

with right:
    fit_counts = remove_small_groups(top_counts(filtered, "field_job_fit", 10))
    st.subheader("Field-Job Fit")
    st.plotly_chart(px.bar(fit_counts, x="field_job_fit", y="count", text_auto=True), width="stretch")

left, right = st.columns(2)
with left:
    local_fit_counts = remove_small_groups(top_counts(filtered, "local_fit", 10))
    st.subheader("Local Development Fit")
    st.plotly_chart(px.bar(local_fit_counts, x="local_fit", y="count", text_auto=True), width="stretch")

with right:
    dropout_by_cohort = remove_small_groups(rate_by_group(filtered, "cohort", "target_scholarship_risk"))
    st.subheader("Dropout/Risk Rate ตามรุ่น")
    st.plotly_chart(px.bar(dropout_by_cohort, x="cohort", y="rate", text_auto=True), width="stretch")

left, right = st.columns(2)
with left:
    country_outcomes = remove_small_groups(grouped_counts(filtered, ["current_country", "current_field_group"], 30))
    st.subheader("จำนวนตามประเทศและสาขา")
    st.dataframe(country_outcomes, width="stretch", hide_index=True)

with right:
    field_completion = remove_small_groups(rate_by_group(filtered, "current_field_group", "target_graduation_success")).head(20)
    st.subheader("Completion Rate ตามกลุ่มสาขา")
    st.plotly_chart(px.bar(field_completion, x="current_field_group", y="rate", text_auto=True), width="stretch")

with st.expander("นิยาม KPI ที่ใช้ในหน้านี้"):
    rows = []
    for key in [
        "completion_rate",
        "dropout_rate",
        "employment_rate",
        "income_distribution",
        "field_job_fit_rate",
        "local_development_fit_rate",
    ]:
        item = definitions["metrics"][key]
        rows.append({"kpi": item["label_th"], "formula": item["formula"], "definition": item["definition_th"]})
    st.dataframe(rows, width="stretch", hide_index=True)
