import pandas as pd
import plotly.express as px
import streamlit as st

from src.agents.registry import agent_registry
from src.analytics.metrics import apply_filters, load_analytics_dataset
from src.labeling.workflow import label_definitions, label_readiness_summary
from src.risk.individual_prediction import (
    approved_individual_targets,
    create_prediction_cases,
    ensure_prediction_tables,
    fit_prototype_artifact,
    get_prediction_case,
    individual_prediction_config,
    list_prediction_cases,
    predict_new_cases,
    prediction_review_history,
    submit_domain_approval,
    submit_human_review,
    validate_individual_import,
)
from src.risk.ml_models import (
    DEFAULT_TARGET,
    MODEL_SPECS,
    TARGET_SPECS,
    available_target_columns,
    feature_readiness,
    forecast_objective_frame,
    forecast_objectives,
    modelable_forecast_objectives,
    policy_interpretation,
    prediction_overview,
    results_to_metrics_frame,
    segment_prediction_summary,
    target_objective_links,
    target_summary,
    train_model_suite,
)
from src.risk.scoring import graduation_dataframe, score_dataframe, score_row
from src.utils.appearance_v1 import render_appearance
from src.utils.chart_surfaces_v2 import render_chart
from src.utils.charts import POLICY_CHART_GRADIENT, style_policy_chart
from src.utils.config import PROJECT_ROOT, load_yaml
from src.utils.metric_surfaces_v2 import render_metric_surface_styles
from src.utils.selection_pipeline_v1 import render_selection_pipeline
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Risk & Forecast")
render_metric_surface_styles()
render_appearance()
render_header(
    "Risk & Forecast",
    "Policy forecast workspace สำหรับดูภาพรวม พยากรณ์รายกรณี และส่งต่อให้มนุษย์ทบทวน",
)
ensure_prediction_tables()
render_database_status()


@st.cache_data(show_spinner=False)
def _load_data():
    return load_analytics_dataset()


@st.cache_data(show_spinner=False)
def _train_ml_models(data: pd.DataFrame, target: str, selected_models: list[str]):
    return train_model_suite(data, target=target, selected_models=selected_models)


@st.cache_resource(show_spinner=False)
def _fit_individual_model(data: pd.DataFrame, target: str):
    return fit_prototype_artifact(data, target)


df = _load_data()
rules = load_yaml("config/risk_rules.yaml")
risk_config = rules["risk_score"]

with st.sidebar:
    st.markdown("**ODOS Policy Forecast**")
    st.caption("พื้นที่ทดลองพยากรณ์เพื่อสนับสนุนการวางแผนนโยบาย")
    st.subheader("Workflow")
    st.markdown(
        """
        - :material/monitoring: ภาพรวม
        - :material/query_stats: พยากรณ์ด้วย ML
        - :material/person_search: พยากรณ์รายกรณี
        - :material/fact_check: ทบทวนและกำกับดูแล
        """
    )
    st.subheader("กรองข้อมูล")
    st.caption("ตัวกรองนี้มีผลกับทุกมุมมองในหน้านี้")
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    province_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    field_options = sorted(df["current_field_group"].dropna().unique().tolist()) if "current_field_group" in df else []
    cohorts = st.multiselect("รุ่น", cohort_options, placeholder="ทุกรุ่น")
    provinces = st.multiselect("จังหวัด", province_options, placeholder="ทุกจังหวัด")
    field_groups = st.multiselect("กลุ่มสาขา", field_options, placeholder="ทุกกลุ่มสาขา")

filtered = apply_filters(df, cohorts=cohorts, provinces=provinces, field_groups=field_groups)
risk_df = score_dataframe(filtered)
graduation_df = graduation_dataframe(filtered)

st.caption(f"กำลังวิเคราะห์ข้อมูล {len(filtered):,} รายการตามตัวกรองปัจจุบัน")
dashboard_cols = st.columns(4)
dashboard_cols[0].metric(
    "ข้อมูลที่ใช้ประเมิน",
    f"{len(filtered):,}",
    help="จำนวนข้อมูลหลังใช้ตัวกรองด้านซ้าย",
    border=True,
)
dashboard_cols[1].metric(
    "กลุ่มควรติดตาม",
    f"{int((risk_df['risk_level'] == 'High').sum()):,}" if not risk_df.empty else "0",
    help="จำนวนรายการที่เข้าเกณฑ์ความเสี่ยงสูงจากกฎประเมิน",
    border=True,
)
dashboard_cols[2].metric(
    "คำถามพยากรณ์พร้อมใช้",
    f"{len(modelable_forecast_objectives()):,}",
    help="Key Forecast Objectives ที่เชื่อมกับ target และโมเดลได้แล้ว",
    border=True,
)
dashboard_cols[3].metric(
    "Target รายกรณี",
    f"{len(approved_individual_targets()):,}",
    help="Target ที่เปิดให้ทดสอบพยากรณ์ข้อมูลรายใหม่ผ่าน workflow ทบทวนโดยมนุษย์",
    border=True,
)

with st.container(border=True):
    st.markdown("**เริ่มจากคำถามเชิงนโยบาย ไม่ใช่ชื่อคอลัมน์**")
    st.write(
        "เลือกมุมมองด้านล่างตามงานที่ต้องการทำ: ดูสถานการณ์รวม ทดลองโมเดล "
        "พยากรณ์ข้อมูลรายใหม่ หรือทบทวนผลก่อนนำไปใช้ประกอบการตัดสินใจ"
    )
    st.caption(
        "ผลลัพธ์ทั้งหมดเป็นสัญญาณประกอบการวางแผน ต้องตรวจสอบบริบทและคุณภาพข้อมูลก่อนใช้จริง"
    )

mode_cols = st.columns(4)
with mode_cols[0].container(border=True, height="stretch"):
    st.markdown("**:material/monitoring: ดูภาพรวม**")
    st.caption("เริ่มจากสถานการณ์รวมและปัจจัยที่ควรติดตาม")
    st.markdown(":blue-badge[สำหรับผู้บริหารและนักวิเคราะห์]")
with mode_cols[1].container(border=True, height="stretch"):
    st.markdown("**:material/query_stats: ทดลองโมเดล**")
    st.caption("เลือกคำถามเชิงนโยบาย แล้วดูคุณภาพของโมเดล")
    st.markdown(":orange-badge[สำหรับวิเคราะห์เชิงนโยบาย]")
with mode_cols[2].container(border=True, height="stretch"):
    st.markdown("**:material/person_search: พยากรณ์รายกรณี**")
    st.caption("ใช้ข้อมูลตัวอย่างหรือ CSV แล้วส่งให้มนุษย์ทบทวน")
    st.markdown(":green-badge[สำหรับเจ้าหน้าที่ปฏิบัติงาน]")
with mode_cols[3].container(border=True, height="stretch"):
    st.markdown("**:material/fact_check: ทบทวนและกำกับดูแล**")
    st.caption("ตรวจ queue, สิทธิ์, label readiness และข้อจำกัด")
    st.markdown(":violet-badge[สำหรับผู้ทบทวนและผู้ดูแล]")

overview_tab, forecast_tab, individual_tab, governance_tab = st.tabs(
    [
        ":material/monitoring: ภาพรวมความเสี่ยง",
        ":material/query_stats: พยากรณ์ด้วย ML",
        ":material/person_search: พยากรณ์รายกรณี",
        ":material/fact_check: การกำกับดูแล",
    ],
    key="risk_forecast_main_tabs_v1",
    on_change="rerun",
)

if overview_tab.open:
    with overview_tab:
        with st.container(border=True):
            st.markdown("**มุมมองนี้ตอบคำถามว่า ตอนนี้สถานการณ์รวมเป็นอย่างไร**")
            st.caption(
                "ใช้สำหรับอ่านภาพรวมจากกฎประเมินเดิม ก่อนลงลึกไปทดลองโมเดลหรือพยากรณ์รายกรณี"
            )
        st.subheader("สถานการณ์จากกฎประเมินความเสี่ยง")
        st.caption("ส่วนนี้เป็นคะแนนจากกฎที่กำหนดไว้ ไม่ใช่ผลจากโมเดล ML")

        cols = st.columns(4)
        cols[0].metric("จำนวนที่ประเมิน", f"{len(risk_df):,}", border=True)
        cols[1].metric(
            "คะแนนความเสี่ยงเฉลี่ย",
            f"{risk_df['risk_score'].mean():.2f}" if not risk_df.empty else "0.00",
            border=True,
        )
        cols[2].metric(
            "ความเสี่ยงสูง",
            f"{int((risk_df['risk_level'] == 'High').sum()):,}" if not risk_df.empty else "0",
            border=True,
        )
        cols[3].metric("เวอร์ชันกฎ", rules["risk_score"]["rule_version"], border=True)

        left, right = st.columns(2)
        with left:
            st.markdown("**ระดับความเสี่ยง**")
            level_counts = risk_df["risk_level"].value_counts().reset_index() if not risk_df.empty else None
            if level_counts is not None:
                level_counts.columns = ["ระดับความเสี่ยง", "จำนวน"]
                risk_level_chart = px.bar(
                    level_counts,
                    x="ระดับความเสี่ยง",
                    y="จำนวน",
                    text_auto=True,
                    color="ระดับความเสี่ยง",
                    color_discrete_sequence=POLICY_CHART_GRADIENT,
                )
                risk_level_chart.update_traces(
                    marker_line_width=0,
                    textposition="outside",
                    cliponaxis=False,
                )
                render_chart(
                    style_policy_chart(risk_level_chart),
                    width="stretch",
                )
        with right:
            st.markdown("**สถานะการสำเร็จการศึกษา**")
            status_counts = (
                graduation_df["graduation_status_label"].value_counts().reset_index()
                if not graduation_df.empty
                else None
            )
            if status_counts is not None:
                status_counts.columns = ["สถานะ", "จำนวน"]
                graduation_status_chart = px.bar(
                    status_counts,
                    x="สถานะ",
                    y="จำนวน",
                    text_auto=True,
                    color="สถานะ",
                    color_discrete_sequence=POLICY_CHART_GRADIENT,
                )
                graduation_status_chart.update_traces(
                    marker_line_width=0,
                    textposition="outside",
                    cliponaxis=False,
                )
                render_chart(
                    style_policy_chart(graduation_status_chart),
                    width="stretch",
                )

        st.subheader("ปัจจัยที่ทำให้เกิดคะแนน")
        component_rows = []
        for _, record in filtered.iterrows():
            result = score_row(record.to_dict(), config=risk_config)
            for component in result["components"]:
                if component["triggered"]:
                    component_rows.append(
                        {
                            "ปัจจัย": component["component"],
                            "คะแนน": component["score"],
                            "คำอธิบาย": component["explanation_th"],
                        }
                    )
        if component_rows:
            component_df = (
                pd.DataFrame(component_rows)
                .groupby(["ปัจจัย", "คะแนน", "คำอธิบาย"])
                .size()
                .reset_index(name="จำนวนครั้งที่พบ")
                .sort_values("จำนวนครั้งที่พบ", ascending=False)
            )
            st.dataframe(
                component_df,
                width="stretch",
                height=360,
                hide_index=True,
                column_config={
                    "คะแนน": st.column_config.NumberColumn("คะแนน", format="%.1f"),
                    "จำนวนครั้งที่พบ": st.column_config.NumberColumn("จำนวนครั้งที่พบ", format="%d"),
                },
            )
        else:
            st.info("ไม่พบปัจจัยความเสี่ยงในข้อมูลที่กรอง", icon=":material/info:")

        with st.expander("ดูข้อมูลผลประเมินแบบรวม", icon=":material/table_chart:"):
            display_columns = [
                "cohort",
                "province",
                "current_country",
                "current_field_group",
                "risk_score",
                "risk_level",
                "triggered_components",
                "rule_version",
                "calculated_at",
            ]
            st.dataframe(
                risk_df[display_columns].head(200),
                width="stretch",
                height=420,
                hide_index=True,
                column_config={
                    "risk_score": st.column_config.ProgressColumn(
                        "risk_score",
                        min_value=0,
                        max_value=100,
                        format="%.1f",
                    ),
                    "risk_level": st.column_config.TextColumn("risk_level"),
                },
            )

        with st.expander("ดูผล Graduation Success จากกฎ", icon=":material/school:"):
            st.dataframe(
                graduation_df.drop(columns=["odos_uid"], errors="ignore").head(200),
                width="stretch",
                height=420,
                hide_index=True,
            )

if forecast_tab.open:
    with forecast_tab:
        with st.container(border=True):
            st.markdown("**เส้นทางทดลองโมเดล**")
            step_cols = st.columns(4)
            step_cols[0].caption("1. เลือกคำถาม")
            step_cols[1].caption("2. เลือกวิธีประเมิน")
            step_cols[2].caption("3. อ่านผลโมเดล")
            step_cols[3].caption("4. แปลผลเชิงนโยบาย")
            st.caption(
                "เหมาะสำหรับทดลองและเปรียบเทียบโมเดลจากข้อมูลรวม ยังไม่ใช่การพยากรณ์บุคคลใหม่"
            )
        st.subheader("1. เลือกคำถามที่ต้องการพยากรณ์")
        st.write("เริ่มจากสิ่งที่อยากรู้ ระบบจะเลือก target ที่เชื่อมกับคำถามนั้นให้โดยอัตโนมัติ")

        setup_mode = st.segmented_control(
            "วิธีเลือกเป้าหมาย",
            options=["objective", "target"],
            default="objective",
            format_func=lambda value: (
                "เลือกคำถามเชิงนโยบาย (แนะนำ)" if value == "objective" else "เลือก target column เอง (ขั้นสูง)"
            ),
            key="risk_forecast_setup_mode_v1",
            width="stretch",
        )

        objectives = forecast_objectives()
        if setup_mode == "objective":
            objective_keys = modelable_forecast_objectives()
            objective_icons = {
                "scholarship_risk": ":material/shield:",
                "graduation_success": ":material/school:",
                "employment_income": ":material/work:",
                "future_scholarship_fields": ":material/account_tree:",
                "area_based_allocation": ":material/location_on:",
            }
            selected_objective_key = render_selection_pipeline(
                "อยากให้ระบบช่วยตอบคำถามเรื่องใด",
                [
                    {
                        "id": key,
                        "value": key,
                        "title": objectives[key]["framework_item"],
                        "description": TARGET_SPECS[objectives[key]["target"]]["question"],
                        "meta": TARGET_SPECS[objectives[key]["target"]]["label"],
                        "icon": objective_icons.get(key, ":material/insights:"),
                    }
                    for key in objective_keys
                ],
                state_key="risk_forecast_objective_pipeline_v1",
                default="scholarship_risk" if "scholarship_risk" in objective_keys else objective_keys[0],
                columns=3,
            )
            selected_objective = objectives[selected_objective_key]
            selected_target = selected_objective.get("target") or DEFAULT_TARGET
        else:
            target_options = available_target_columns(filtered)
            selected_target = st.selectbox(
                "เลือก target column",
                options=target_options,
                index=target_options.index(DEFAULT_TARGET) if DEFAULT_TARGET in target_options else 0,
                format_func=lambda target: f"{TARGET_SPECS[target]['label']} · {target}",
                key="risk_target_column_selector_v1",
            )
            selected_objective = None

        target_spec = TARGET_SPECS[selected_target]
        with st.container(border=True):
            st.markdown(f"**คำถามที่กำลังพยากรณ์: {target_spec['question']}?**")
            st.write(
                f"โมเดลจะเรียนรู้เพื่อแยกผู้ที่ “{target_spec['positive_label']}” "
                "จากข้อมูลบริบทที่มีอยู่ โดยผลลัพธ์ใช้เพื่อช่วยวางแผนและติดตามเท่านั้น"
            )
            if selected_objective:
                status_label = (
                    "พร้อมทดลองโมเดล"
                    if selected_objective["status"] == "model_ready"
                    else "ใช้ตัวแทนชั่วคราว"
                )
                st.caption(
                    f"{selected_objective['framework_item']} · {status_label} · "
                    f"ระบบเลือก {selected_target}"
                )
                st.warning(selected_objective["caveat"], icon=":material/warning:")
            else:
                links = target_objective_links(selected_target)
                st.caption(f"โหมดขั้นสูง · target ที่เลือก: {selected_target}")
                if links:
                    linked_names = ", ".join(
                        f"{item['framework_item']} {item['forecast_objective']}" for item in links
                    )
                    st.info(f"target นี้เชื่อมโยงกับ {linked_names}", icon=":material/link:")
                else:
                    st.warning(
                        "target นี้เป็นเป้าหมายเชิงเทคนิค และยังไม่ได้แทน Key Forecast Objective โดยตรง",
                        icon=":material/warning:",
                    )

        target_info = target_summary(filtered, selected_target)
        feature_report = feature_readiness(filtered, selected_target)
        summary_cols = st.columns(3)
        summary_cols[0].metric(
            "ข้อมูลที่ใช้ประเมิน",
            f"{int(target_info.get('records', 0)):,}",
            border=True,
        )
        summary_cols[1].metric(
            f"พบ “{target_spec['positive_label']}”",
            f"{int(target_info.get('positive_count', 0)):,}",
            border=True,
        )
        summary_cols[2].metric(
            "สัดส่วนที่เข้าเงื่อนไข",
            f"{float(target_info.get('positive_rate', 0.0)):.2f}%",
            border=True,
        )

        st.subheader("2. เลือกวิธีประเมิน")
        customize_models = st.toggle(
            "เลือกโมเดลเอง",
            value=False,
            help="เปิดเมื่อต้องการเปรียบเทียบโมเดลรายตัวหรือกำหนดสมาชิกของ Vote Ensemble",
            key="risk_customize_models_v1",
        )
        if customize_models:
            model_options = list(MODEL_SPECS)
            selected_model_keys = st.multiselect(
                "โมเดลที่ต้องการประมวลผลและแสดงผล",
                options=model_options,
                default=model_options,
                format_func=lambda key: MODEL_SPECS[key]["label"],
                key="risk_ml_model_selector_v3",
                placeholder="เลือกอย่างน้อย 1 โมเดล",
            )
            st.caption(
                "หากเลือก Vote Ensemble ร่วมกับ base model อย่างน้อย 2 โมเดล "
                "ระบบจะรวมคะแนนจาก base model ที่เลือก"
            )
        else:
            selected_model_keys = ["vote_ensemble"]
            st.info(
                "ระบบจะใช้ Vote Ensemble ซึ่งรวมความเห็นจาก base model ทั้ง 5 แบบ "
                "เหมาะสำหรับเริ่มต้นโดยไม่ต้องเลือกอัลกอริทึมเอง",
                icon=":material/auto_awesome:",
            )

        filter_signature = (
            tuple(cohorts),
            tuple(provinces),
            tuple(field_groups),
            len(filtered),
        )
        run_key = (selected_target, tuple(selected_model_keys), filter_signature)
        run_models = st.button(
            "ประมวลผลและดูผลพยากรณ์",
            type="primary",
            icon=":material/play_arrow:",
            disabled=not selected_model_keys or not target_info["ready"],
            key="risk_run_models_v1",
        )

        if not target_info["ready"]:
            st.warning(str(target_info["reason"]), icon=":material/warning:")
        elif not selected_model_keys:
            st.warning("กรุณาเลือกอย่างน้อย 1 โมเดล", icon=":material/warning:")

        if run_models:
            try:
                with st.spinner("กำลังฝึกและประเมินโมเดล..."):
                    model_results = _train_ml_models(filtered, selected_target, selected_model_keys)
                st.session_state["risk_forecast_last_run"] = {
                    "key": run_key,
                    "results": model_results,
                }
            except RuntimeError as exc:
                st.error(str(exc))
            except ValueError as exc:
                st.warning(str(exc))

        saved_run = st.session_state.get("risk_forecast_last_run")
        if saved_run and saved_run["key"] == run_key:
            model_results = saved_run["results"]
            best_result = max(model_results, key=lambda item: float(item.metrics.get("f1", 0.0)))

            st.subheader("3. อ่านผลลัพธ์")
            st.success(
                f"โมเดลที่สมดุลที่สุดในชุดที่เลือกคือ {best_result.label}",
                icon=":material/check_circle:",
            )
            result_cols = st.columns(3)
            result_cols[0].metric(
                "ตรวจพบกลุ่มเข้าเงื่อนไข",
                f"{float(best_result.metrics.get('recall', 0.0)) * 100:.1f}%",
                help="จากผู้ที่เข้าเงื่อนไขจริง 100 คน โมเดลตรวจพบได้กี่คน (Recall)",
                border=True,
            )
            result_cols[1].metric(
                "ความแม่นของคำเตือน",
                f"{float(best_result.metrics.get('precision', 0.0)) * 100:.1f}%",
                help="จากผู้ที่โมเดลแจ้งว่าเข้าเงื่อนไข 100 คน เป็นจริงกี่คน (Precision)",
                border=True,
            )
            result_cols[2].metric(
                "คะแนนสมดุล",
                f"{float(best_result.metrics.get('f1', 0.0)) * 100:.1f}%",
                help="คะแนนรวมความสมดุลระหว่างการตรวจพบและความแม่นของคำเตือน (F1)",
                border=True,
            )
            st.caption(
                "ผลนี้เป็นการทดสอบกับข้อมูล validation แบบรวม ไม่ใช่คำตัดสินรายบุคคล "
                "และยังไม่อนุญาตให้นำไปใช้ตัดสินใจจริง"
            )

            st.subheader("4. แปลผลเพื่อวางแผนนโยบาย")
            with st.expander("ปรับเกณฑ์แนวโน้มสำหรับการวางแผน", icon=":material/tune:"):
                policy_threshold = st.slider(
                    "เกณฑ์ความน่าจะเป็น",
                    min_value=0.10,
                    max_value=0.90,
                    value=0.50,
                    step=0.05,
                    help=(
                        "ค่าต่ำจะครอบคลุมคนมากขึ้นแต่มีคำเตือนผิดมากขึ้น "
                        "ค่าสูงจะเลือกเฉพาะแนวโน้มที่ชัดขึ้น ค่านี้ไม่ทำให้โมเดลฝึกใหม่"
                    ),
                    key=f"risk_policy_threshold_{selected_target}",
                )
                st.caption(
                    "เกณฑ์ 0.50 เป็นค่าเริ่มต้นของ Prototype ยังไม่ใช่เกณฑ์ที่ผ่านการรับรองเชิงนโยบาย"
                )

            overview = prediction_overview(best_result, selected_target, policy_threshold)
            guidance = policy_interpretation(best_result, selected_target, policy_threshold)
            direction_word = "เข้าเงื่อนไขความเสี่ยง" if guidance["direction"] == "risk" else "เข้าเงื่อนไขผลลัพธ์เชิงบวก"

            trend_cols = st.columns(3)
            trend_cols[0].metric(
                f"โมเดลจัดว่า{direction_word}",
                f"{float(overview['forecast_positive_rate']):.1f}%",
                delta=f"{float(overview['forecast_actual_gap']):+.1f} จุดจากค่าจริง",
                delta_color="off",
                border=True,
            )
            trend_cols[1].metric(
                "อัตราที่เกิดขึ้นจริงใน validation",
                f"{float(overview['actual_positive_rate']):.1f}%",
                border=True,
            )
            trend_cols[2].metric(
                "ความน่าจะเป็นเฉลี่ย",
                f"{float(overview['average_probability']):.1f}%",
                border=True,
            )

            with st.container(border=True):
                st.markdown("**ความหมายของสัญญาณ**")
                st.write(guidance["signal"])
                st.write(guidance["implication"])
                st.caption(
                    "ตัวเลขนี้สรุปจาก validation set เพื่อประเมินรูปแบบของโมเดล "
                    "ยังไม่ใช่การพยากรณ์ข้อมูลบุคคลใหม่หรือหลักฐานเชิงสาเหตุ"
                )
            if abs(float(overview["forecast_actual_gap"])) >= 10:
                st.warning(guidance["reliability_note"], icon=":material/model_training:")
            else:
                st.info(guidance["reliability_note"], icon=":material/check_circle:")

            group_labels = {
                "cohort": "รุ่น",
                "region": "ภูมิภาค",
                "province": "จังหวัด",
                "current_country": "ประเทศปัจจุบัน",
                "current_field_group": "กลุ่มสาขา",
            }
            group_options = [
                column
                for column in group_labels
                if column in best_result.validation_predictions.columns
            ]
            selected_group = st.selectbox(
                "ดูแนวโน้มแยกตาม",
                options=group_options,
                format_func=lambda column: group_labels[column],
                key=f"risk_policy_group_{selected_target}",
            )
            segment_summary = segment_prediction_summary(
                best_result,
                selected_group,
                threshold=policy_threshold,
                minimum_group_size=10,
            )
            if segment_summary.empty:
                st.info(
                    "ไม่มีบางกลุ่มที่มีอย่างน้อย 10 รายการใน validation set "
                    "จึงยังไม่แสดงผลเพื่อป้องกันการตีความจากกลุ่มที่เล็กเกินไป",
                    icon=":material/privacy_tip:",
                )
            else:
                display_segments = segment_summary.rename(
                    columns={
                        selected_group: group_labels[selected_group],
                        "records": "จำนวนข้อมูล",
                        "average_probability": "ความน่าจะเป็นเฉลี่ย (%)",
                        "forecast_positive_rate": f"แนวโน้ม {target_spec['positive_label']} (%)",
                        "actual_positive_rate": "เกิดขึ้นจริง (%)",
                    }
                )
                st.bar_chart(
                    display_segments.head(15),
                    x=group_labels[selected_group],
                    y=f"แนวโน้ม {target_spec['positive_label']} (%)",
                    horizontal=True,
                )
                st.dataframe(
                    display_segments,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "ความน่าจะเป็นเฉลี่ย (%)": st.column_config.ProgressColumn(
                            "ความน่าจะเป็นเฉลี่ย",
                            min_value=0,
                            max_value=100,
                            format="%.1f%%",
                        ),
                        f"แนวโน้ม {target_spec['positive_label']} (%)": st.column_config.NumberColumn(
                            f"แนวโน้ม {target_spec['positive_label']}",
                            format="%.1f%%",
                        ),
                        "เกิดขึ้นจริง (%)": st.column_config.NumberColumn(
                            "เกิดขึ้นจริง",
                            format="%.1f%%",
                        ),
                    },
                )
                st.caption(
                    "แสดงเฉพาะกลุ่มที่มีอย่างน้อย 10 รายการ ผลต่างระหว่างค่าพยากรณ์กับค่าจริง "
                    "ควรใช้ตรวจสอบโมเดลก่อนใช้ประกอบนโยบาย"
                )

            policy_left, policy_right = st.columns(2)
            with policy_left:
                with st.container(border=True):
                    st.markdown("**เป้าหมายนโยบาย**")
                    st.write(guidance["policy_goal"])
                    st.markdown("**ประเด็นสำหรับพิจารณา**")
                    st.dataframe(
                        pd.DataFrame(
                            {"แนวทาง": guidance["policy_actions"]}
                        ),
                        width="stretch",
                        hide_index=True,
                    )
            with policy_right:
                with st.container(border=True):
                    st.markdown("**ตัวชี้วัดสำหรับติดตามผล**")
                    st.dataframe(
                        pd.DataFrame(
                            {"ตัวชี้วัด": guidance["monitoring_kpis"]}
                        ),
                        width="stretch",
                        hide_index=True,
                    )
                    st.markdown("**ปัจจัยที่ควรนำไปตรวจสอบต่อ**")
                    st.dataframe(
                        best_result.feature_importance[["feature", "importance"]].head(5),
                        width="stretch",
                        hide_index=True,
                    )
                    st.caption(
                        "Feature importance บอกความสัมพันธ์ที่โมเดลใช้พยากรณ์ "
                        "ไม่ได้ยืนยันว่าปัจจัยนั้นเป็นสาเหตุของผลลัพธ์"
                    )

            st.info(
                "การพยากรณ์ข้อมูลบุคคลใหม่ยังไม่เปิดใน Prototype นี้ "
                "จนกว่าจะกำหนดสิทธิ์ผู้ใช้ การอนุมัติ และกระบวนการทบทวนโดยมนุษย์",
                icon=":material/lock:",
            )

            with st.expander("ดูผลเปรียบเทียบและรายละเอียดเชิงเทคนิค", icon=":material/tune:"):
                st.dataframe(results_to_metrics_frame(model_results), width="stretch", hide_index=True)
                st.markdown(
                    "**อ่านค่าอย่างย่อ:** Recall เน้นไม่ให้พลาดกลุ่มที่ควรติดตาม · "
                    "Precision เน้นลดคำเตือนผิด · F1 ดูสมดุลของทั้งสองค่า · "
                    "PR AUC เหมาะกับกรณีที่กลุ่มเป้าหมายมีจำนวนน้อย"
                )
                with st.expander("ดู Features ที่ใช้และเหตุผลการคัดเลือก"):
                    st.dataframe(
                        feature_report,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "completeness_rate": st.column_config.NumberColumn(
                                "ความครบถ้วน", format="%.2f%%"
                            ),
                        },
                    )
                    st.info(
                        "ระบบตัดข้อมูลที่เผยผลลัพธ์ล่วงหน้า ข้อมูลระบุตัวบุคคล "
                        "และ target columns ออกจาก Features เพื่อป้องกันข้อมูลรั่วไหล",
                        icon=":material/security:",
                    )

                for result in model_results:
                    with st.expander(result.label, expanded=len(model_results) == 1):
                        st.write(result.purpose)
                        metric_cols = st.columns(4)
                        metric_cols[0].metric("F1", f"{float(result.metrics.get('f1', 0.0)):.3f}")
                        metric_cols[1].metric("Recall", f"{float(result.metrics.get('recall', 0.0)):.3f}")
                        metric_cols[2].metric("Precision", f"{float(result.metrics.get('precision', 0.0)):.3f}")
                        metric_cols[3].metric("PR AUC", f"{float(result.metrics.get('pr_auc', 0.0)):.3f}")
                        left_model, right_model = st.columns(2)
                        with left_model:
                            st.markdown("**ผลทายถูกและทายผิด**")
                            st.dataframe(result.confusion_matrix, width="stretch", hide_index=True)
                        with right_model:
                            st.markdown("**Features ที่มีอิทธิพลสูง**")
                            st.bar_chart(
                                result.feature_importance,
                                x="feature",
                                y="importance",
                                horizontal=True,
                            )
        elif saved_run:
            st.info(
                "เป้าหมาย ตัวกรอง หรือรายชื่อโมเดลเปลี่ยนแล้ว กด “ประมวลผลและดูผลพยากรณ์” อีกครั้ง",
                icon=":material/refresh:",
            )

if individual_tab.open:
    with individual_tab:
        with st.container(border=True):
            st.markdown("**เส้นทางพยากรณ์รายกรณี**")
            case_step_cols = st.columns(4)
            case_step_cols[0].caption("1. เลือกบทบาท")
            case_step_cols[1].caption("2. เลือกคำถาม")
            case_step_cols[2].caption("3. เลือกข้อมูล")
            case_step_cols[3].caption("4. ส่งทบทวน")
            st.caption(
                "เหมาะสำหรับ CSV รายใหม่ที่ไม่ระบุตัวบุคคล ผลจะถูกส่งเข้ากระบวนการ Human review ก่อนใช้ต่อ"
            )
        ensure_prediction_tables()
        individual_config = individual_prediction_config()
        governance_config = load_yaml("config/governance.yaml")
        workflow_roles = [
            "CaseOfficer",
            "HumanReviewer",
            "DomainApprover",
            "ModelOwner",
            "DPOAuditor",
        ]
        workflow_role_labels = {
            "CaseOfficer": "สร้างคำพยากรณ์",
            "HumanReviewer": "ทบทวนผลพยากรณ์",
            "DomainApprover": "อนุมัติแผนช่วยเหลือ",
            "ModelOwner": "ตรวจทะเบียนโมเดล",
            "DPOAuditor": "ตรวจประวัติและสิทธิ์",
        }

        st.subheader("ประเมินแนวโน้มของข้อมูลรายใหม่")
        st.write(
            "เลือกเรื่องที่ต้องการทราบ แล้วนำเข้าข้อมูลที่ไม่ระบุตัวบุคคล "
            "ระบบจะส่งผลให้เจ้าหน้าที่อีกคนทบทวนก่อนนำไปวางแผนช่วยเหลือ"
        )
        st.caption(
            "ผลนี้เป็นสัญญาณประกอบการติดตาม ไม่ใช่คำตัดสินสิทธิหรือการอนุมัติอัตโนมัติ"
        )

        with st.expander(
            "สิทธิ์และบทบาทสำหรับทดสอบระบบ",
            icon=":material/manage_accounts:",
        ):
            identity_left, identity_right = st.columns(2)
            with identity_left:
                prototype_role = st.selectbox(
                    "งานที่ต้องการทดสอบ",
                    options=workflow_roles,
                    format_func=lambda role: workflow_role_labels[role],
                    key="individual_prediction_role_v1",
                )
            with identity_right:
                prototype_actor = st.text_input(
                    "รหัสผู้ปฏิบัติงาน",
                    value="case-officer-01",
                    help="ใช้รหัสภายใน 3-40 ตัวอักษร ห้ามกรอกชื่อ เบอร์โทร อีเมล หรือเลขบัตรประชาชน",
                    key="individual_prediction_actor_v1",
                ).strip()
            st.caption(
                f"กำลังทดสอบในบทบาท {prototype_role}: "
                f"{governance_config['roles'][prototype_role]['description_th']}"
            )

        if prototype_role == "CaseOfficer":
            st.markdown("**ขั้นตอน 1 จาก 3 · เลือกสิ่งที่ต้องการทราบ**")
            approved_targets = approved_individual_targets()
            individual_target = st.selectbox(
                "ต้องการประเมินแนวโน้มเรื่องใด",
                options=approved_targets,
                format_func=lambda target: TARGET_SPECS[target]["question"],
                key="individual_prediction_target_v1",
            )
            target_spec = TARGET_SPECS[individual_target]
            target_approval = individual_config["approved_targets"][individual_target]
            with st.container(border=True):
                st.markdown(f"**กำลังประเมิน: {target_spec['question']}?**")
                st.write(
                    f"ผลที่ได้คือความน่าจะเป็นของ “{target_spec['positive_label']}” "
                    "สำหรับแต่ละรายการในไฟล์"
                )
                st.caption(target_approval["interpretation_notice"])
                with st.expander(
                    "ดูรายละเอียดทางเทคนิค",
                    icon=":material/settings:",
                ):
                    st.write(f"Target column: `{individual_target}`")
                    st.write(
                        f"Model: `{target_approval['model_key']}` · "
                        f"Version: `{target_approval['model_version']}` · "
                        f"Threshold: `{float(target_approval['threshold']):.2f}`"
                    )

            st.markdown("**ขั้นตอน 2 จาก 3 · เลือกข้อมูลที่จะประเมิน**")
            template_path = PROJECT_ROOT / "data/reference/individual_prediction_template.csv"
            sample_path = PROJECT_ROOT / "data/reference/individual_prediction_test_cases.csv"
            data_source = st.segmented_control(
                "แหล่งข้อมูล",
                options=["sample", "upload"],
                default="sample",
                format_func=lambda value: (
                    "ทดลองด้วยข้อมูลตัวอย่าง 12 รายการ"
                    if value == "sample"
                    else "อัปโหลด CSV ของฉัน"
                ),
                key="individual_prediction_data_source_v1",
                width="stretch",
            )

            cleaned_cases = None
            import_issues = []
            imported_cases = None
            if data_source == "sample":
                imported_cases = pd.read_csv(sample_path)
                st.info(
                    "เลือกข้อมูลตัวอย่างแล้ว สามารถตรวจข้อมูลและไปขั้นตอนถัดไปได้ทันที",
                    icon=":material/science:",
                )
            else:
                uploaded_cases = st.file_uploader(
                    "เลือกไฟล์ CSV",
                    type=["csv"],
                    key="individual_prediction_csv_v1",
                    help="ระบบจะปฏิเสธคอลัมน์นอก template และตรวจข้อมูลระบุตัวบุคคลเบื้องต้น",
                )
                with st.container(horizontal=True):
                    st.download_button(
                        "ดาวน์โหลด CSV template",
                        data=template_path.read_bytes(),
                        file_name=template_path.name,
                        mime="text/csv",
                        icon=":material/download:",
                    )
                    st.download_button(
                        "ดาวน์โหลดข้อมูลตัวอย่าง",
                        data=sample_path.read_bytes(),
                        file_name=sample_path.name,
                        mime="text/csv",
                        icon=":material/download:",
                    )
                st.caption(
                    "ใช้ case_reference ที่ไม่ระบุตัวบุคคล และอัปโหลดได้สูงสุด "
                    f"{individual_config['maximum_rows_per_import']} รายการต่อครั้ง"
                )
                if uploaded_cases is not None:
                    uploaded_cases.seek(0)
                    imported_cases = uploaded_cases

            if imported_cases is not None:
                try:
                    if not isinstance(imported_cases, pd.DataFrame):
                        imported_cases = pd.read_csv(imported_cases)
                    cleaned_cases, import_issues = validate_individual_import(imported_cases)
                except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as exc:
                    st.error(f"อ่าน CSV ไม่สำเร็จ: {exc}")
                else:
                    error_issues = [
                        issue for issue in import_issues if issue["severity"] == "error"
                    ]
                    warning_issues = [
                        issue for issue in import_issues if issue["severity"] == "warning"
                    ]
                    if error_issues:
                        st.error(
                            "ยังใช้ข้อมูลชุดนี้ไม่ได้ กรุณาแก้รายการที่ระบุแล้วอัปโหลดใหม่",
                            icon=":material/error:",
                        )
                    elif warning_issues:
                        st.warning(
                            f"อ่านได้ {len(cleaned_cases):,} รายการ แต่มีจุดที่ผู้ทบทวนต้องตรวจเพิ่ม",
                            icon=":material/warning:",
                        )
                    else:
                        st.success(
                            f"พร้อมประเมิน {len(cleaned_cases):,} รายการ",
                            icon=":material/check_circle:",
                        )
                    with st.expander(
                        f"ตรวจข้อมูลที่อ่านได้ ({len(cleaned_cases):,} รายการ)",
                        icon=":material/table_view:",
                    ):
                        if import_issues:
                            st.dataframe(
                                pd.DataFrame(import_issues),
                                width="stretch",
                                hide_index=True,
                            )
                        st.dataframe(
                            cleaned_cases.head(100),
                            width="stretch",
                            hide_index=True,
                            column_config={
                                "feature_completeness": st.column_config.ProgressColumn(
                                    "ความครบถ้วนของข้อมูล",
                                    min_value=0,
                                    max_value=100,
                                    format="%.1f%%",
                                )
                            },
                        )

            st.markdown("**ขั้นตอน 3 จาก 3 · ตรวจสอบและส่งให้ผู้ทบทวน**")
            if cleaned_cases is None:
                st.info(
                    "เลือกข้อมูลตัวอย่างหรืออัปโหลด CSV ที่ถูกต้องเพื่อดำเนินการต่อ",
                    icon=":material/upload_file:",
                )
            else:
                review_summary = st.columns(3)
                review_summary[0].metric(
                    "เรื่องที่ประเมิน",
                    target_spec["label"],
                    border=True,
                )
                review_summary[1].metric(
                    "จำนวนรายการ",
                    f"{len(cleaned_cases):,}",
                    border=True,
                )
                review_summary[2].metric(
                    "ขั้นตอนถัดไป",
                    "เจ้าหน้าที่ทบทวน",
                    border=True,
                )

            has_errors = any(
                issue["severity"] == "error" for issue in import_issues
            )
            with st.form("individual_prediction_confirmation_v1"):
                purpose_confirmed = st.checkbox(
                    "ยืนยันว่าใช้ผลเพื่อการติดตามหรือช่วยเหลือ และจะไม่ใช้ผลนี้เพียงอย่างเดียวตัดสินสิทธิ",
                    key="individual_prediction_purpose_confirm_v1",
                )
                create_predictions = st.form_submit_button(
                    "ประเมินแนวโน้มและส่งให้ผู้ทบทวน",
                    type="primary",
                    icon=":material/send:",
                    disabled=(cleaned_cases is None or has_errors or not prototype_actor),
                )
            if create_predictions and not purpose_confirmed:
                st.error("กรุณายืนยันเงื่อนไขการใช้ผลก่อนส่งให้ผู้ทบทวน")
                create_predictions = False
            if create_predictions and has_errors:
                st.error("ข้อมูลยังมีข้อผิดพลาด จึงยังส่งประเมินไม่ได้")
                create_predictions = False
            if create_predictions and cleaned_cases is not None:
                try:
                    with st.spinner("กำลังประเมินแนวโน้มและสร้างรายการสำหรับผู้ทบทวน..."):
                        artifact = _fit_individual_model(df, individual_target)
                        predictions = predict_new_cases(artifact, cleaned_cases)
                        created_ids = create_prediction_cases(
                            predictions,
                            actor=prototype_actor,
                            role=prototype_role,
                        )
                    st.session_state["individual_prediction_last_results"] = predictions
                    st.session_state["individual_prediction_last_model_metrics"] = (
                        artifact.validation_metrics
                    )
                    st.session_state["individual_prediction_last_target"] = (
                        individual_target
                    )
                    st.success(
                        f"ส่ง {len(created_ids)} รายการให้ผู้ทบทวนแล้ว",
                        icon=":material/check_circle:",
                    )
                except (PermissionError, ValueError, RuntimeError) as exc:
                    st.error(str(exc))

            last_predictions = st.session_state.get("individual_prediction_last_results")
            last_target = st.session_state.get("individual_prediction_last_target")
            if (
                isinstance(last_predictions, pd.DataFrame)
                and not last_predictions.empty
                and last_target == individual_target
            ):
                st.subheader("ผลเบื้องต้นที่ส่งให้ผู้ทบทวน")
                st.info(
                    "รายการเหล่านี้ยังไม่ใช่ผลอนุมัติ เจ้าหน้าที่ผู้ทบทวนต้องตรวจบริบทและคุณภาพข้อมูลก่อน",
                    icon=":material/pending_actions:",
                )
                tendency_counts = (
                    last_predictions["tendency_band"]
                    .value_counts()
                    .rename_axis("ระดับแนวโน้ม")
                    .reset_index(name="จำนวน")
                )
                st.dataframe(
                    tendency_counts,
                    width="stretch",
                    hide_index=True,
                )
                model_metrics = st.session_state.get(
                    "individual_prediction_last_model_metrics",
                    {},
                )
                display_predictions = last_predictions[
                    [
                        "case_reference",
                        "target_label",
                        "probability",
                        "tendency_band",
                        "interpretation",
                        "data_quality_score",
                        "data_warnings",
                        "status",
                    ]
                ].copy()
                display_predictions["data_warnings"] = display_predictions[
                    "data_warnings"
                ].map(lambda values: " · ".join(values) if values else "ไม่พบ")
                st.dataframe(
                    display_predictions,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "probability": st.column_config.ProgressColumn(
                            "ความน่าจะเป็น",
                            min_value=0,
                            max_value=1,
                            format="%.1f%%",
                        ),
                        "data_quality_score": st.column_config.ProgressColumn(
                            "คุณภาพข้อมูล",
                            min_value=0,
                            max_value=100,
                            format="%.1f%%",
                        ),
                    },
                )
                with st.expander(
                    "ดูคุณภาพของโมเดลที่ใช้",
                    icon=":material/query_stats:",
                ):
                    validation_cols = st.columns(4)
                    validation_cols[0].metric(
                        "ค้นพบเคสที่เข้าเงื่อนไข",
                        f"{float(model_metrics.get('recall', 0.0)) * 100:.1f}%",
                        help="Recall: จากเคสที่เข้าเงื่อนไขจริง โมเดลค้นพบได้กี่เปอร์เซ็นต์",
                        border=True,
                    )
                    validation_cols[1].metric(
                        "ความแม่นของเคสที่แจ้ง",
                        f"{float(model_metrics.get('precision', 0.0)) * 100:.1f}%",
                        help="Precision: จากเคสที่โมเดลแจ้ง มีเคสเข้าเงื่อนไขจริงกี่เปอร์เซ็นต์",
                        border=True,
                    )
                    validation_cols[2].metric(
                        "PR AUC",
                        f"{float(model_metrics.get('pr_auc', 0.0)):.3f}",
                        border=True,
                    )
                    validation_cols[3].metric(
                        "ความคลาดเคลื่อน probability",
                        f"{float(model_metrics.get('brier_score', 0.0)):.3f}",
                        help="Brier score ยิ่งใกล้ 0 ยิ่งดี",
                        border=True,
                    )

        case_queue = pd.DataFrame()
        if prototype_actor:
            try:
                case_queue = list_prediction_cases(prototype_role, prototype_actor)
            except ValueError as exc:
                st.warning(str(exc))

        if prototype_role == "HumanReviewer":
            st.subheader("รายการที่รอตรวจสอบ")
            st.caption(
                "ตรวจความครบถ้วนของข้อมูลและบริบททีละรายการ ก่อนส่งต่อให้ผู้อนุมัติแผนช่วยเหลือ"
            )
            if case_queue.empty:
                st.info("ขณะนี้ไม่มีรายการที่รอตรวจสอบ")
            else:
                st.metric("รอตรวจสอบ", f"{len(case_queue):,} รายการ", border=True)
                review_case_id = st.selectbox(
                    "เลือกรายการ",
                    options=case_queue["case_id"].tolist(),
                    format_func=lambda case_id: (
                        f"{case_queue.loc[case_queue['case_id'] == case_id, 'case_reference'].iloc[0]} · "
                        f"{case_queue.loc[case_queue['case_id'] == case_id, 'interpretation'].iloc[0]}"
                    ),
                    key="individual_review_case_v1",
                )
                with st.expander("ดูรายการทั้งหมดในคิว", icon=":material/list:"):
                    st.dataframe(case_queue, width="stretch", hide_index=True)
                review_case = get_prediction_case(
                    review_case_id,
                    prototype_role,
                    prototype_actor,
                )
                review_cols = st.columns(3)
                review_cols[0].metric(
                    "ความน่าจะเป็น",
                    f"{float(review_case['probability']) * 100:.1f}%",
                    border=True,
                )
                review_cols[1].metric(
                    "ระดับแนวโน้ม",
                    review_case["tendency_band"],
                    border=True,
                )
                review_cols[2].metric(
                    "คุณภาพข้อมูล",
                    f"{float(review_case['data_quality_score']):.1f}%",
                    border=True,
                )
                st.warning(
                    individual_config["approved_targets"][review_case["target"]][
                        "interpretation_notice"
                    ],
                    icon=":material/info:",
                )
                with st.expander("ดู Features และคำเตือนข้อมูล"):
                    st.dataframe(
                        pd.DataFrame(
                            [{"feature": key, "value": value} for key, value in review_case["features"].items()]
                        ),
                        width="stretch",
                        hide_index=True,
                    )
                    if review_case["data_warnings"]:
                        st.warning(" · ".join(review_case["data_warnings"]))
                    else:
                        st.caption("ไม่พบคำเตือนข้อมูล")
                with st.form("individual_human_review_form_v1"):
                    review_decision = st.selectbox(
                        "ข้อสรุปหลังตรวจสอบ",
                        options=list(individual_config["review_decisions"]),
                        format_func=lambda key: individual_config["review_decisions"][key],
                    )
                    review_reason = st.text_area(
                        "เหตุผลและบริบทที่โมเดลอาจไม่เห็น",
                        placeholder="ระบุหลักฐาน บริบท และเหตุผลอย่างน้อย 10 ตัวอักษร",
                    )
                    submit_review = st.form_submit_button(
                        "บันทึก Human review",
                        type="primary",
                        icon=":material/fact_check:",
                    )
                if submit_review:
                    try:
                        next_status = submit_human_review(
                            review_case_id,
                            review_decision,
                            review_reason,
                            prototype_actor,
                            prototype_role,
                        )
                        st.success(f"บันทึกแล้ว สถานะใหม่: {next_status}")
                        st.rerun()
                    except (PermissionError, ValueError) as exc:
                        st.error(str(exc))

        elif prototype_role == "DomainApprover":
            st.subheader("รายการที่รออนุมัติแผนช่วยเหลือ")
            st.caption(
                "พิจารณาผลโมเดลพร้อมเหตุผลของผู้ทบทวนและหลักฐานอื่นก่อนอนุมัติ"
            )
            if case_queue.empty:
                st.info("ขณะนี้ไม่มีรายการที่รออนุมัติ")
            else:
                st.metric("รออนุมัติ", f"{len(case_queue):,} รายการ", border=True)
                approval_case_id = st.selectbox(
                    "เลือกรายการ",
                    options=case_queue["case_id"].tolist(),
                    format_func=lambda case_id: (
                        f"{case_queue.loc[case_queue['case_id'] == case_id, 'case_reference'].iloc[0]} · "
                        f"{case_queue.loc[case_queue['case_id'] == case_id, 'review_decision'].iloc[0]}"
                    ),
                    key="individual_approval_case_v1",
                )
                with st.expander("ดูรายการทั้งหมดในคิว", icon=":material/list:"):
                    st.dataframe(case_queue, width="stretch", hide_index=True)
                approval_case = get_prediction_case(
                    approval_case_id,
                    prototype_role,
                    prototype_actor,
                )
                with st.container(border=True):
                    st.markdown(f"**{approval_case['case_reference']} · {approval_case['interpretation']}**")
                    st.write(f"Human review: {approval_case['review_decision']}")
                    st.write(approval_case["review_reason"])
                    st.warning(
                        individual_config["approved_targets"][approval_case["target"]][
                            "interpretation_notice"
                        ],
                        icon=":material/info:",
                    )
                    st.caption(
                        "ผู้อนุมัติต้องพิจารณาหลักฐานอื่นร่วมด้วย "
                        "และห้ามใช้ผลนี้เพื่อยกเลิกทุน ลดสิทธิ หรือปฏิเสธสิทธิอัตโนมัติ"
                    )
                with st.form("individual_domain_approval_form_v1"):
                    approval_decision = st.selectbox(
                        "ผลการอนุมัติ",
                        options=list(individual_config["approval_decisions"]),
                        format_func=lambda key: individual_config["approval_decisions"][key],
                    )
                    action_plan = st.text_area(
                        "แผนช่วยเหลือหรือเหตุผลการอนุมัติ",
                        placeholder="ระบุแนวทาง ผู้รับผิดชอบ หรือเหตุผลอย่างน้อย 10 ตัวอักษร",
                    )
                    submit_approval = st.form_submit_button(
                        "บันทึก Domain approval",
                        type="primary",
                        icon=":material/approval:",
                    )
                if submit_approval:
                    try:
                        next_status = submit_domain_approval(
                            approval_case_id,
                            approval_decision,
                            action_plan,
                            prototype_actor,
                            prototype_role,
                        )
                        st.success(f"บันทึกแล้ว สถานะใหม่: {next_status}")
                        st.rerun()
                    except (PermissionError, ValueError) as exc:
                        st.error(str(exc))

        elif prototype_role == "CaseOfficer":
            with st.expander("ดูรายการที่ฉันเคยส่ง", icon=":material/history:"):
                if case_queue.empty:
                    st.caption("ยังไม่มีรายการ")
                else:
                    st.dataframe(case_queue, width="stretch", hide_index=True)

        elif prototype_role in {"DPOAuditor", "Admin"}:
            st.subheader("ตรวจสอบประวัติและการใช้สิทธิ์")
            if case_queue.empty:
                st.info("ยังไม่มีรายการในขอบเขตสิทธิ์นี้")
            else:
                st.dataframe(case_queue, width="stretch", hide_index=True)
                audit_case_id = st.selectbox(
                    "เลือกรายการเพื่อดูประวัติ",
                    options=case_queue["case_id"].tolist(),
                    key="individual_audit_case_v1",
                )
                st.dataframe(
                    prediction_review_history(audit_case_id),
                    width="stretch",
                    hide_index=True,
                )

        elif prototype_role == "ModelOwner":
            st.subheader("Model registry สำหรับรายกรณี")
            registry_rows = []
            for target, approval in individual_config["approved_targets"].items():
                registry_rows.append(
                    {
                        "target": target,
                        "target_label": TARGET_SPECS[target]["label"],
                        **approval,
                    }
                )
            st.dataframe(pd.DataFrame(registry_rows), width="stretch", hide_index=True)
            st.warning(
                "ModelOwner ดูแลเวอร์ชันและ Threshold แต่ไม่มีสิทธิ์สร้าง ทบทวน หรืออนุมัติเคส",
                icon=":material/admin_panel_settings:",
            )

if governance_tab.open:
    with governance_tab:
        with st.container(border=True):
            st.markdown("**มุมมองนี้ตอบคำถามว่า ผลพยากรณ์พร้อมใช้แค่ไหนและใครต้องรับรอง**")
            st.caption(
                "ใช้ตรวจ label readiness, สิทธิ์ของ agent, ข้อจำกัดของกฎ และเงื่อนไขก่อนขยับไปใช้จริง"
            )
        st.subheader("ความพร้อมและข้อจำกัดก่อนนำผลไปใช้")
        st.warning(
            "ทุก target และโมเดลในหน้านี้ได้รับอนุญาตสำหรับการทดลอง Prototype เท่านั้น "
            "ยังไม่ผ่านการรับรองสำหรับ Production หรือการตัดสินใจรายบุคคล",
            icon=":material/warning:",
        )

        label_readiness = label_readiness_summary(filtered)
        approved_labels = int(label_readiness["approval_status"].eq("approved").sum())
        prototype_approved_labels = int(
            label_readiness["approval_status"].eq("approved_for_prototype").sum()
        )
        prototype_eligible_labels = int(label_readiness["prototype_ml_eligible"].sum())

        label_cols = st.columns(4)
        label_cols[0].metric("Labels ทั้งหมด", f"{len(label_readiness):,}", border=True)
        label_cols[1].metric(
            "รับรองเพื่อ Prototype",
            f"{prototype_approved_labels:,}/{len(label_readiness):,}",
            border=True,
        )
        label_cols[2].metric(
            "พร้อมทดลอง ML",
            f"{prototype_eligible_labels:,}/{len(label_readiness):,}",
            border=True,
        )
        label_cols[3].metric(
            "รับรองเพื่อ Production",
            f"{approved_labels:,}/{len(label_readiness):,}",
            border=True,
        )

        with st.expander("ดูความพร้อมของ Key Forecast Objectives", expanded=True):
            st.dataframe(forecast_objective_frame(), width="stretch", hide_index=True)
            st.caption(
                "รายการสถานะ data_gap จะยังไม่ถูกนำมาสร้างโมเดล "
                "และจะเก็บไว้สำหรับแผนจัดหาข้อมูลและเอกสารในขั้นถัดไป"
            )

        with st.expander("ดูรายละเอียด Label และผู้อนุมัติ"):
            st.dataframe(
                label_readiness[
                    [
                        "priority",
                        "label_th",
                        "evidence_completeness",
                        "approval_status",
                        "readiness_score",
                        "prototype_ml_eligible",
                        "production_ml_eligible",
                        "owner_agent",
                        "human_approver_role",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )
            template_path = PROJECT_ROOT / "data/reference/label_review_template.csv"
            st.download_button(
                "ดาวน์โหลดแบบฟอร์มทบทวน Label",
                data=template_path.read_bytes(),
                file_name="label_review_template.csv",
                mime="text/csv",
                icon=":material/download:",
            )

        with st.expander("ดูหน้าที่ของ Agent และข้อกำหนดการอนุมัติ"):
            st.dataframe(
                agent_registry()[
                    [
                        "agent_name",
                        "human_owner_th",
                        "mission_th",
                        "label_responsibility",
                        "required_human_approval",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )
            st.dataframe(
                label_definitions()[
                    [
                        "priority",
                        "target_name",
                        "label_version",
                        "owner_agent",
                        "human_approver_role",
                        "approval_status",
                        "leakage_cutoff_rule",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

        with st.expander("ดูข้อจำกัดของกฎประเมินความเสี่ยง"):
            st.write(f"สถานะการรับรอง Risk: {rules['risk_score']['expert_approval_status']}")
            st.write(f"เวอร์ชันกฎ Graduation: {rules['graduation_success']['rule_version']}")
            st.dataframe(
                [{"ข้อจำกัด": item} for item in rules["risk_score"]["limitations_th"]],
                width="stretch",
                hide_index=True,
            )
