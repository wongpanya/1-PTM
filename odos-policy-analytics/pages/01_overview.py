import plotly.express as px
import streamlit as st

from src.analytics.metrics import (
    apply_filters,
    followup_coverage_by_group,
    grouped_counts,
    income_box_summary,
    load_analytics_dataset,
    metric_definitions,
    outcome_by_group,
    overview_metrics,
    remove_small_groups,
    top_counts,
)
from src.governance.privacy import minimum_group_size
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Overview")
render_header(
    "Overview",
    "ภาพรวมโครงการในมิติประชากร การศึกษา ผลลัพธ์หลังทุน พื้นที่ เวลา และความครบถ้วนในการติดตาม",
)
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

st.caption(
    f"กำลังแสดงข้อมูล {len(filtered):,} ระเบียน; ผลรายกลุ่มต้องมีอย่างน้อย "
    f"{minimum_group_size():,} ราย และไม่มีข้อมูลระดับบุคคล"
)

cols = st.columns(5)
cols[0].metric("ผู้รับทุนทั้งหมด", f"{metrics['total_recipients']:,}")
cols[1].metric("สำเร็จการศึกษา", f"{metrics['completion_count']:,}", f"{metrics['completion_rate']:.1f}%")
cols[2].metric("มีงานทำ", f"{metrics['employed_count']:,}", f"{metrics['employment_rate']:.1f}%")
cols[3].metric("เสี่ยงติดตามไม่ครบ", f"{metrics['tracking_risk_count']:,}", f"{metrics['tracking_risk_rate']:.1f}%")
cols[4].metric("ข้อมูลรายได้", f"{metrics['income_available']:,}", f"{metrics['income_availability_rate']:.1f}%")

population_tab, education_tab, outcomes_tab, area_tab, time_tab, gaps_tab = st.tabs(
    ["ผู้รับทุน", "การศึกษา", "ผลลัพธ์หลังทุน", "พื้นที่", "แนวโน้มตามรุ่น", "ข้อมูลติดตามขาด"]
)

with population_tab:
    left, right = st.columns(2)
    with left:
        cohort_counts = remove_small_groups(top_counts(filtered, "cohort", 30))
        st.subheader("ผู้รับทุนตามรุ่น")
        st.plotly_chart(
            px.bar(cohort_counts, x="cohort", y="count", text_auto=True, labels={"cohort": "รุ่น", "count": "จำนวน"}),
            width="stretch",
        )
    with right:
        sex_counts = remove_small_groups(top_counts(filtered, "sex", 10))
        st.subheader("ผู้รับทุนตามเพศ")
        st.plotly_chart(
            px.bar(sex_counts, x="sex", y="count", text_auto=True, labels={"sex": "เพศ", "count": "จำนวน"}),
            width="stretch",
        )
    region_counts = remove_small_groups(top_counts(filtered, "region", 20))
    st.subheader("ผู้รับทุนตามภูมิภาค")
    st.plotly_chart(
        px.bar(region_counts, x="region", y="count", text_auto=True, labels={"region": "ภูมิภาค", "count": "จำนวน"}),
        width="stretch",
    )

with education_tab:
    left, right = st.columns(2)
    with left:
        status_counts = remove_small_groups(top_counts(filtered, "project_condition_status", 20))
        st.subheader("สถานะตามเงื่อนไขโครงการ")
        st.plotly_chart(
            px.bar(
                status_counts,
                x="count",
                y="project_condition_status",
                orientation="h",
                text_auto=True,
                labels={"count": "จำนวน", "project_condition_status": "สถานะ"},
            ),
            width="stretch",
        )
    with right:
        country_counts = remove_small_groups(top_counts(filtered, "current_country", 20))
        st.subheader("ประเทศที่ศึกษา/สถานะปัจจุบัน")
        st.plotly_chart(
            px.bar(
                country_counts,
                x="current_country",
                y="count",
                text_auto=True,
                labels={"current_country": "ประเทศ", "count": "จำนวน"},
            ),
            width="stretch",
        )
    field_country = remove_small_groups(grouped_counts(filtered, ["current_country", "current_field_group"], 40))
    st.subheader("ประเทศและกลุ่มสาขา")
    st.dataframe(field_country, width="stretch", hide_index=True)
    st.info("ชุดข้อมูลปัจจุบันยังไม่มีชื่อมหาวิทยาลัยที่ผ่านการทำมาตรฐาน จึงยังไม่สรุปเปรียบเทียบรายมหาวิทยาลัย")

with outcomes_tab:
    left, right = st.columns(2)
    with left:
        employment_counts = remove_small_groups(top_counts(filtered, "employment_type", 20))
        st.subheader("ประเภทการประกอบอาชีพ")
        st.plotly_chart(
            px.bar(
                employment_counts,
                x="count",
                y="employment_type",
                orientation="h",
                text_auto=True,
                labels={"count": "จำนวน", "employment_type": "ประเภทอาชีพ"},
            ),
            width="stretch",
        )
    with right:
        income_by_cohort = income_box_summary(filtered, "cohort")
        st.subheader("รายได้รายเดือนตามรุ่น (สถิติ Aggregate)")
        if income_by_cohort.empty:
            st.info("ข้อมูลรายได้ของกลุ่มที่ผ่านเกณฑ์ยังไม่เพียงพอ")
        else:
            st.plotly_chart(
                px.bar(
                    income_by_cohort,
                    x="cohort",
                    y="median",
                    error_y=income_by_cohort["q3"] - income_by_cohort["median"],
                    error_y_minus=income_by_cohort["median"] - income_by_cohort["q1"],
                    labels={"cohort": "รุ่น", "median": "รายได้มัธยฐาน (บาท/เดือน)"},
                ),
                width="stretch",
            )
    left, right = st.columns(2)
    with left:
        fit_counts = remove_small_groups(top_counts(filtered, "field_job_fit", 20))
        st.subheader("งานตรงสาขา")
        st.plotly_chart(
            px.bar(fit_counts, x="field_job_fit", y="count", text_auto=True, labels={"count": "จำนวน"}),
            width="stretch",
        )
    with right:
        local_counts = remove_small_groups(top_counts(filtered, "local_fit", 20))
        st.subheader("ความสอดคล้องกับการพัฒนาพื้นที่")
        st.plotly_chart(
            px.bar(local_counts, x="local_fit", y="count", text_auto=True, labels={"count": "จำนวน"}),
            width="stretch",
        )

with area_tab:
    province_outcomes = outcome_by_group(filtered, "province")
    st.subheader("จำนวนผู้รับทุนและผลสำเร็จรายจังหวัด")
    if province_outcomes.empty:
        st.info("ยังไม่มีกลุ่มจังหวัดที่ผ่านเกณฑ์การปกปิด")
    else:
        st.plotly_chart(
            px.scatter(
                province_outcomes,
                x="count",
                y="completion_rate",
                size="count",
                color="employment_rate",
                hover_name="province",
                labels={
                    "count": "จำนวนผู้รับทุน",
                    "completion_rate": "สำเร็จการศึกษา (%)",
                    "employment_rate": "มีงานทำ (%)",
                },
            ),
            width="stretch",
        )
        st.dataframe(province_outcomes, width="stretch", hide_index=True)
    district_counts = remove_small_groups(grouped_counts(filtered, ["province", "district"], 50))
    st.subheader("พื้นที่ระดับจังหวัดและอำเภอ")
    st.dataframe(district_counts, width="stretch", hide_index=True)

with time_tab:
    cohort_outcomes = outcome_by_group(filtered, "cohort")
    st.subheader("แนวโน้มผลลัพธ์ตามรุ่น")
    if cohort_outcomes.empty:
        st.info("ยังไม่มีกลุ่มรุ่นที่ผ่านเกณฑ์การปกปิด")
    else:
        trend = cohort_outcomes.melt(
            id_vars=["cohort", "count"],
            value_vars=["completion_rate", "employment_rate", "scholarship_risk_rate", "tracking_gap_rate"],
            var_name="outcome",
            value_name="rate",
        )
        st.plotly_chart(
            px.line(
                trend,
                x="cohort",
                y="rate",
                color="outcome",
                markers=True,
                labels={"cohort": "รุ่น", "rate": "อัตรา (%)", "outcome": "ผลลัพธ์"},
            ),
            width="stretch",
        )
        st.dataframe(cohort_outcomes, width="stretch", hide_index=True)

with gaps_tab:
    dimension_labels = {"รุ่น": "cohort", "จังหวัด": "province", "ประเทศ": "current_country", "กลุ่มสาขา": "current_field_group"}
    selected_dimension = st.selectbox("มิติสำหรับตรวจช่องว่างการติดตาม", list(dimension_labels))
    gap_column = dimension_labels[selected_dimension]
    coverage = followup_coverage_by_group(filtered, gap_column)
    if coverage.empty:
        st.info("ยังไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
    else:
        st.plotly_chart(
            px.scatter(
                coverage,
                x="followup_completeness",
                y="tracking_gap_rate",
                size="count",
                hover_name=gap_column,
                labels={
                    "followup_completeness": "ความครบถ้วนข้อมูลติดตาม (%)",
                    "tracking_gap_rate": "ความเสี่ยงติดตามไม่ครบ (%)",
                },
            ),
            width="stretch",
        )
        st.dataframe(coverage, width="stretch", hide_index=True)

with st.expander("นิยาม KPI และข้อจำกัด"):
    rows = []
    for key in [
        "total_recipients",
        "completed_recipients",
        "employed_recipients",
        "completion_rate",
        "employment_rate",
    ]:
        item = definitions["metrics"][key]
        rows.append({"kpi": item["label_th"], "formula": item["formula"], "definition": item["definition_th"]})
    st.dataframe(rows, width="stretch", hide_index=True)
