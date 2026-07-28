import plotly.express as px
import streamlit as st

from src.analytics.exporting import build_dashboard_export
from src.analytics.metrics import (
    apply_filters,
    followup_coverage_by_group,
    grouped_counts,
    income_box_summary,
    income_summary,
    load_analytics_dataset,
    metric_definitions,
    outcome_by_group,
    overview_metrics,
    remove_small_groups,
    top_counts,
)
from src.governance.privacy import (
    aggregate_csv_bytes,
    append_export_log,
    minimum_group_size,
    role_can,
)
from src.utils.appearance_v1 import render_appearance
from src.utils.chart_surfaces_v2 import render_chart
from src.utils.metric_surfaces_v2 import render_metric_surface_styles
from src.utils.metrics_ui import render_metric_grid
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Overview")
render_metric_surface_styles()
render_appearance()
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
    year_options = sorted(df["analysis_year"].dropna().astype(int).unique().tolist()) if "analysis_year" in df else []
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    region_options = sorted(df["region"].dropna().unique().tolist()) if "region" in df else []
    province_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    district_options = sorted(df["district"].dropna().unique().tolist()) if "district" in df else []
    country_options = sorted(df["current_country"].dropna().unique().tolist()) if "current_country" in df else []
    field_options = sorted(df["current_field_group"].dropna().unique().tolist()) if "current_field_group" in df else []
    detailed_field_options = sorted(df["current_field"].dropna().unique().tolist()) if "current_field" in df else []
    university_options = (
        sorted(df["standardized_university_name"].dropna().unique().tolist())
        if "standardized_university_name" in df
        else []
    )
    employer_sector_options = (
        sorted(df["employer_sector_code"].dropna().unique().tolist())
        if "employer_sector_code" in df
        else []
    )
    analysis_years = st.multiselect("ปีวิเคราะห์", year_options)
    cohorts = st.multiselect("รุ่น", cohort_options)
    regions = st.multiselect("ภูมิภาค", region_options)
    provinces = st.multiselect("จังหวัด", province_options)
    districts = st.multiselect("อำเภอ", district_options)
    countries = st.multiselect("ประเทศ", country_options)
    field_groups = st.multiselect("กลุ่มสาขา", field_options)
    detailed_fields = st.multiselect("สาขารายละเอียด", detailed_field_options)
    universities = st.multiselect("มหาวิทยาลัยมาตรฐาน", university_options)
    employer_sectors = st.multiselect("รหัสภาคส่วนผู้จ้าง", employer_sector_options)
    st.divider()
    export_role = st.selectbox("สิทธิ์สำหรับ Export", ["Analyst", "Admin", "Viewer"], index=0)

filtered = apply_filters(
    df,
    cohorts=cohorts,
    provinces=provinces,
    countries=countries,
    field_groups=field_groups,
    analysis_years=analysis_years,
    districts=districts,
    regions=regions,
    fields=detailed_fields,
    universities=universities,
    employer_sectors=employer_sectors,
)
if filtered.empty:
    st.warning("ไม่พบข้อมูลตามชุดตัวกรองนี้ กรุณาลดเงื่อนไขหรือเลือกตัวกรองใหม่")
metrics = overview_metrics(filtered)
income = income_summary(filtered)

st.caption(
    f"กำลังแสดงข้อมูล {len(filtered):,} ระเบียน; ผลรายกลุ่มต้องมีอย่างน้อย "
    f"{minimum_group_size():,} ราย และไม่มีข้อมูลระดับบุคคล | "
    "ปีวิเคราะห์ = ปีเริ่มศึกษา; หากไม่มีจึงใช้ปีคาดว่าจะสำเร็จและปีเริ่มงานตามลำดับ"
)

st.markdown("#### :material/database: ฐานข้อมูลโครงการ")
st.caption("ขนาดประชากรและความพร้อมของข้อมูลที่ใช้ติดตามผล")
render_metric_grid(
    [
        {
            "label": "ผู้รับทุนทั้งหมด",
            "value": f"{metrics['total_recipients']:,}",
            "delta": "รายในชุดข้อมูลที่กรอง",
        },
        {
            "label": "เสี่ยงติดตามไม่ครบ",
            "value": f"{metrics['tracking_risk_count']:,}",
            "delta": f"{metrics['tracking_risk_rate']:.1f}% ของผู้รับทุน",
        },
        {
            "label": "ข้อมูลรายได้",
            "value": f"{metrics['income_available']:,}",
            "delta": f"ครอบคลุม {metrics['income_availability_rate']:.1f}%",
        },
    ]
)

st.markdown("#### :material/school: ผลลัพธ์การศึกษาและการทำงาน")
render_metric_grid(
    [
        {
            "label": "สำเร็จการศึกษา",
            "value": f"{metrics['completion_count']:,}",
            "delta": f"{metrics['completion_rate']:.1f}% ของผู้รับทุน",
        },
        {
            "label": "มีงานทำ",
            "value": f"{metrics['employed_count']:,}",
            "delta": f"{metrics['employment_rate']:.1f}% ของข้อมูลติดตาม",
        },
        {
            "label": "ออกจากทุนกลางคัน",
            "value": f"{metrics['dropout_rate']:.1f}%",
            "delta": f"{metrics['dropout_count']:,} จาก {len(filtered):,} ราย",
        },
        {
            "label": "ยุติทุน",
            "value": f"{metrics['termination_rate']:.1f}%",
            "delta": f"{metrics['termination_count']:,} จาก {len(filtered):,} ราย",
        },
    ]
)

st.markdown("#### :material/shield: ความเสี่ยงและความสอดคล้อง")
render_metric_grid(
    [
        {
            "label": "ความเสี่ยงทุน",
            "value": f"{metrics['scholarship_risk_rate']:.1f}%",
            "delta": f"{metrics['scholarship_risk_count']:,} จาก {len(filtered):,} ราย",
        },
        {
            "label": "งานตรงสาขา",
            "value": f"{metrics['field_job_fit_rate']:.1f}%",
            "delta": (
                f"{metrics['field_job_fit_count']:,} จาก "
                f"{metrics['field_job_fit_denominator']:,} ราย"
            ),
        },
        {
            "label": "งานสอดคล้องท้องถิ่น",
            "value": f"{metrics['local_fit_rate']:.1f}%",
            "delta": (
                f"{metrics['local_fit_count']:,} จาก "
                f"{metrics['local_fit_denominator']:,} ราย"
            ),
        },
    ]
)

population_tab, education_tab, outcomes_tab, area_tab, time_tab, gaps_tab = st.tabs(
    ["ผู้รับทุน", "การศึกษา", "ผลลัพธ์หลังทุน", "พื้นที่", "แนวโน้มตามรุ่น", "ข้อมูลติดตามขาด"]
)

with population_tab:
    left, right = st.columns(2)
    with left:
        cohort_counts = remove_small_groups(top_counts(filtered, "cohort", 30))
        st.subheader("ผู้รับทุนตามรุ่น")
        render_chart(
            px.bar(cohort_counts, x="cohort", y="count", text_auto=True, labels={"cohort": "รุ่น", "count": "จำนวน"}),
            width="stretch",
        )
    with right:
        sex_counts = remove_small_groups(top_counts(filtered, "sex", 10))
        st.subheader("ผู้รับทุนตามเพศ")
        render_chart(
            px.bar(sex_counts, x="sex", y="count", text_auto=True, labels={"sex": "เพศ", "count": "จำนวน"}),
            width="stretch",
        )
    region_counts = remove_small_groups(top_counts(filtered, "region", 20))
    st.subheader("ผู้รับทุนตามภูมิภาค")
    render_chart(
        px.bar(region_counts, x="region", y="count", text_auto=True, labels={"region": "ภูมิภาค", "count": "จำนวน"}),
        width="stretch",
    )

with education_tab:
    left, right = st.columns(2)
    with left:
        status_counts = remove_small_groups(top_counts(filtered, "project_condition_status", 20))
        st.subheader("สถานะตามเงื่อนไขโครงการ")
        render_chart(
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
        render_chart(
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
    university_counts = remove_small_groups(top_counts(filtered, "standardized_university_name", 25))
    st.subheader("มหาวิทยาลัยปัจจุบันที่ผ่านการ Normalize/Alias Mapping")
    if university_counts.empty:
        st.info("ไม่มีข้อมูลมหาวิทยาลัยหรือไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
    else:
        render_chart(
            px.bar(
                university_counts.sort_values("count"),
                x="count",
                y="standardized_university_name",
                orientation="h",
                labels={"count": "จำนวน", "standardized_university_name": "มหาวิทยาลัย"},
            ),
            width="stretch",
        )
    st.caption("ยังเป็นการทำมาตรฐานระดับข้อความ ไม่ใช่รหัสทะเบียนสถาบันทางการ")

with outcomes_tab:
    income_cols = st.columns(3)
    income_cols[0].metric("รายได้เฉลี่ย", f"{income['average_income']:,.0f} บาท/เดือน")
    income_cols[1].metric("รายได้มัธยฐาน", f"{income['median_income']:,.0f} บาท/เดือน")
    income_cols[2].metric("จำนวนข้อมูลรายได้", f"{income['records_with_income']:,} ระเบียน")
    left, right = st.columns(2)
    with left:
        employment_counts = remove_small_groups(top_counts(filtered, "employment_type", 20))
        st.subheader("ประเภทการประกอบอาชีพ")
        render_chart(
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
        sector_counts = remove_small_groups(top_counts(filtered, "employer_sector_code", 20))
        st.subheader("รหัสภาคส่วนผู้จ้าง")
        render_chart(
            px.bar(
                sector_counts,
                x="employer_sector_code",
                y="count",
                text_auto=True,
                labels={"employer_sector_code": "รหัสภาคส่วน", "count": "จำนวน"},
            ),
            width="stretch",
        )
    left, right = st.columns(2)
    with left:
        income_by_cohort = income_box_summary(filtered, "cohort")
        st.subheader("รายได้รายเดือนตามรุ่น (สถิติ Aggregate)")
        if income_by_cohort.empty:
            st.info("ข้อมูลรายได้ของกลุ่มที่ผ่านเกณฑ์ยังไม่เพียงพอ")
        else:
            render_chart(
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
    with right:
        fit_counts = remove_small_groups(top_counts(filtered, "field_job_fit", 20))
        st.subheader("งานตรงสาขา")
        render_chart(
            px.bar(fit_counts, x="field_job_fit", y="count", text_auto=True, labels={"count": "จำนวน"}),
            width="stretch",
        )
    left, right = st.columns(2)
    with left:
        local_counts = remove_small_groups(top_counts(filtered, "local_fit", 20))
        st.subheader("ความสอดคล้องกับการพัฒนาพื้นที่")
        render_chart(
            px.bar(local_counts, x="local_fit", y="count", text_auto=True, labels={"count": "จำนวน"}),
            width="stretch",
        )
    with right:
        st.subheader("ตัวตั้งและ Denominator ของ Fit KPI")
        st.dataframe(
            [
                {
                    "KPI": "Field-Job Fit",
                    "ผ่านเกณฑ์ระดับ >= 2": metrics["field_job_fit_count"],
                    "มีข้อมูล": metrics["field_job_fit_denominator"],
                    "อัตรา (%)": metrics["field_job_fit_rate"],
                },
                {
                    "KPI": "Local Fit",
                    "ผ่านเกณฑ์ระดับ >= 2": metrics["local_fit_count"],
                    "มีข้อมูล": metrics["local_fit_denominator"],
                    "อัตรา (%)": metrics["local_fit_rate"],
                },
            ],
            width="stretch",
            hide_index=True,
        )

with area_tab:
    province_outcomes = outcome_by_group(filtered, "province")
    st.subheader("จำนวนผู้รับทุนและผลสำเร็จรายจังหวัด")
    if province_outcomes.empty:
        st.info("ยังไม่มีกลุ่มจังหวัดที่ผ่านเกณฑ์การปกปิด")
    else:
        render_chart(
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
        render_chart(
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
        render_chart(
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
        "dropout_rate",
        "termination_rate",
        "scholarship_risk_rate",
        "employment_rate",
        "average_income",
        "median_income",
        "field_job_fit_rate",
        "local_development_fit_rate",
    ]:
        item = definitions["metrics"][key]
        rows.append({"kpi": item["label_th"], "formula": item["formula"], "definition": item["definition_th"]})
    st.dataframe(rows, width="stretch", hide_index=True)

st.subheader("Export รายงาน Aggregate ตาม Filter")
export_name = "overview_filtered_aggregate.csv"
export_report = build_dashboard_export(filtered, "Overview")
if role_can(export_role, "can_export_aggregate"):
    export_data = aggregate_csv_bytes(export_report, export_name, export_role, log_export=False)
    if st.download_button(
        "Export Overview Aggregate CSV",
        data=export_data,
        file_name=export_name,
        mime="text/csv",
    ):
        append_export_log(export_name, export_role, len(export_report), list(export_report.columns))
else:
    st.caption("Viewer ไม่มีสิทธิ์ Export ข้อมูล")
