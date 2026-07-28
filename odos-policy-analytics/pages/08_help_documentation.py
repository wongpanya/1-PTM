from __future__ import annotations

import streamlit as st

from src.help.assistant import (
    ask_ollama,
    list_ollama_models,
    load_help_documents,
    search_help_documents,
)
from src.utils.appearance_v1 import render_appearance
from src.utils.ui import configure_page, render_header


configure_page("Help & Documentation")
render_appearance()
render_header(
    "Help & Documentation",
    "ค้นหาคู่มือ เรียนรู้ขั้นตอนสำคัญ และถามผู้ช่วย AI ที่ทำงานภายในเครื่อง",
)

st.html(
    """
    <style>
    .st-key-help_docs_card,
    .st-key-help_ai_card,
    .st-key-help_faq_card,
    .st-key-help_privacy_card {
        min-height: 10.5rem;
        padding: 1rem 1.05rem;
        border-radius: 8px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    }

    .st-key-help_docs_card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F3EDFF 100%);
        border-color: #DED3F8 !important;
    }

    .st-key-help_ai_card {
        background: linear-gradient(145deg, #FFFFFF 0%, #E7F9FC 100%);
        border-color: #CDEEF4 !important;
    }

    .st-key-help_faq_card {
        background: linear-gradient(145deg, #FFFFFF 0%, #E8FAF3 100%);
        border-color: #CFEFE2 !important;
    }

    .st-key-help_privacy_card {
        background: linear-gradient(145deg, #FFFFFF 0%, #FFF4DE 100%);
        border-color: #F5E2B8 !important;
    }
    </style>
    """
)


def _open_section(section: str) -> None:
    st.session_state["help_active_section_v1"] = section


st.session_state.setdefault("help_active_section_v1", "documentation")
search_query = st.text_input(
    "ค้นหาเอกสารและคำถามที่พบบ่อย",
    placeholder="เช่น พยากรณ์รายกรณี, target, การนำเข้า CSV, privacy...",
    icon=":material/search:",
)

if search_query:
    results = search_help_documents(search_query)
    st.subheader(f"ผลการค้นหา ({len(results):,})")
    if not results:
        st.info("ไม่พบคำที่ค้นหา ลองใช้คำสั้นลงหรือเลือกคู่มือด้านล่าง")
    for result in results:
        with st.expander(result["title"], icon=":material/article:"):
            st.write(result["excerpt"])
            st.caption(f"เอกสาร: docs/{result['slug']}.md")

st.subheader("Quick Links")
quick_links = [
    (
        "help_docs_card",
        ":material/menu_book:",
        "Documentation",
        "คู่มือการใช้งานทุกหน้าและกระบวนการสำคัญ",
        "documentation",
    ),
    (
        "help_ai_card",
        ":material/neurology:",
        "AI-assisted integration",
        "ถามตอบจากเอกสารด้วย Local AI โดยไม่มีค่า API",
        "ai",
    ),
    (
        "help_faq_card",
        ":material/contact_support:",
        "FAQ",
        "คำตอบสั้นสำหรับปัญหาที่พบบ่อย",
        "faq",
    ),
    (
        "help_privacy_card",
        ":material/admin_panel_settings:",
        "Privacy & Governance",
        "ข้อจำกัด สิทธิ์ และการทบทวนโดยมนุษย์",
        "privacy",
    ),
]
columns = st.columns(4, gap="small")
for column, (card_key, icon, title, description, section) in zip(
    columns,
    quick_links,
    strict=True,
):
    with column:
        with st.container(border=True, key=card_key):
            st.markdown(f"#### {icon} {title}")
            st.caption(description)
            st.button(
                "เปิด",
                key=f"open_help_{section}_v1",
                icon=":material/arrow_forward:",
                type=(
                    "primary"
                    if st.session_state["help_active_section_v1"] == section
                    else "secondary"
                ),
                width="stretch",
                on_click=_open_section,
                args=(section,),
            )

active_section = st.session_state["help_active_section_v1"]
st.divider()

if active_section == "documentation":
    st.subheader("Documentation")
    documents = load_help_documents()
    selected_slug = st.selectbox(
        "เลือกเอกสาร",
        [document.slug for document in documents],
        format_func=lambda slug: next(
            document.title for document in documents if document.slug == slug
        ),
    )
    selected_document = next(
        document for document in documents if document.slug == selected_slug
    )
    with st.container(border=True):
        st.markdown(selected_document.content)
        st.caption(f"แหล่งข้อมูล: docs/{selected_document.path.name}")

elif active_section == "ai":
    st.subheader("AI-assisted integration")
    st.info(
        "โหมดนี้ใช้ Ollama และโมเดลที่รันบนเครื่อง จึงไม่มีค่า API "
        "คำถามจะส่งเฉพาะข้อความและส่วนที่เกี่ยวข้องจากเอกสารในโครงการ ไม่ส่งฐานข้อมูลผู้รับทุนหรือ PII",
        icon=":material/security:",
    )
    left, right = st.columns([2, 1])
    endpoint = left.text_input(
        "Local AI endpoint",
        value="http://localhost:11434",
        help="เพื่อความปลอดภัย ระบบอนุญาตเฉพาะ localhost เท่านั้น",
    )
    check_connection = right.button(
        "ตรวจสอบ",
        icon=":material/cable:",
        width="stretch",
        type="primary",
    )

    models = []
    if check_connection or st.session_state.get("help_ollama_connected_v1"):
        try:
            models = list_ollama_models(endpoint)
            st.session_state["help_ollama_connected_v1"] = True
            st.session_state["help_ollama_models_v1"] = models
        except (ConnectionError, ValueError) as exc:
            st.session_state["help_ollama_connected_v1"] = False
            st.warning(str(exc))
    else:
        models = st.session_state.get("help_ollama_models_v1", [])

    if models:
        st.success(f"Local AI พร้อมใช้งาน · พบ {len(models):,} โมเดล")
        selected_model = st.selectbox("โมเดล", models)
        st.session_state.setdefault("help_ai_history_v1", [])
        for message in st.session_state["help_ai_history_v1"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input(
            "ถามเกี่ยวกับการใช้งานระบบ เอกสาร หรือขั้นตอนพยากรณ์...",
            key="help_ai_prompt_v1",
        )
        if prompt:
            history = st.session_state["help_ai_history_v1"]
            history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("กำลังค้นเอกสารและเรียบเรียงคำตอบ..."):
                    try:
                        answer = ask_ollama(
                            prompt,
                            model=selected_model,
                            base_url=endpoint,
                            history=history[:-1],
                        )
                    except (ConnectionError, ValueError) as exc:
                        answer = f"ยังตอบด้วย Local AI ไม่ได้: {exc}"
                    st.markdown(answer)
            history.append({"role": "assistant", "content": answer})
    else:
        st.warning("ยังไม่พบ Local AI บนเครื่อง แต่การค้นหาเอกสารด้านบนยังใช้งานได้ตามปกติ")
        with st.container(border=True):
            st.markdown("#### ติดตั้งครั้งแรกบน Windows")
            st.code("winget install Ollama.Ollama", language="powershell")
            st.code("ollama pull qwen2.5:3b", language="powershell")
            st.caption(
                "หลังติดตั้งและดาวน์โหลดโมเดล ให้เปิด Ollama แล้วกลับมากด “ตรวจสอบ” "
                "โมเดล 3B เหมาะสำหรับทดลองบนเครื่องทั่วไป แต่ความเร็วขึ้นอยู่กับ RAM/CPU/GPU"
            )

elif active_section == "faq":
    st.subheader("Frequently Asked Questions")
    faq_items = [
        (
            "ทำไมผลพยากรณ์จึงใช้ตัดสินใจอัตโนมัติไม่ได้?",
            "โมเดลเป็นเครื่องมือช่วยคัดกรองและวางแผน ต้องตรวจคุณภาพข้อมูล บริบท "
            "และให้ผู้มีอำนาจทบทวนก่อนนำไปใช้ทุกครั้ง",
        ),
        (
            "ควรเลือก Key Forecast Objective หรือ target column?",
            "ผู้ใช้ทั่วไปควรเริ่มจาก Key Forecast Objective ส่วน target column "
            "เหมาะกับนักวิเคราะห์ที่เข้าใจนิยาม label และ feature leakage แล้ว",
        ),
        (
            "AI ฟรีจริงหรือไม่?",
            "Ollama ไม่มีค่า API เพราะประมวลผลบนเครื่อง แต่ผู้ใช้รับผิดชอบทรัพยากรเครื่อง "
            "พื้นที่จัดเก็บ และการติดตั้งโมเดลเอง",
        ),
        (
            "AI สามารถเห็นข้อมูลรายบุคคลหรือไม่?",
            "หน้า Help ส่งเฉพาะคำถามและข้อความจากเอกสาร ไม่เชื่อมฐานข้อมูลบุคคล "
            "และ endpoint ถูกจำกัดไว้ที่ localhost",
        ),
    ]
    for question, answer in faq_items:
        with st.expander(question, icon=":material/help:"):
            st.write(answer)

else:
    st.subheader("Privacy & Governance")
    st.warning(
        "ห้ามวางชื่อ เลขบัตร อีเมล เบอร์โทรศัพท์ หรือข้อมูลระบุตัวบุคคลในช่องถาม AI",
        icon=":material/warning:",
    )
    st.markdown(
        """
        - AI ใช้เพื่ออธิบายเอกสารและช่วยนำทางการใช้งาน ไม่อนุมัติหรือปฏิเสธสิทธิ์
        - ผลพยากรณ์รายกรณีต้องผ่านสิทธิ์ผู้ใช้ การอนุมัติ และ Human Review
        - ควรเก็บ audit trail ของการนำผลไปใช้และเหตุผลประกอบการตัดสินใจ
        - หากเปลี่ยนไปใช้ AI ภายนอก ต้องผ่านการประเมิน Privacy, DPA และนโยบายหน่วยงานก่อน
        """
    )

st.info(
    "**Pro tip — AI-assisted integration:** เริ่มจากค้นเอกสารโดยไม่ใช้ AI "
    "แล้วจึงเปิด Local AI เมื่อต้องการสรุปหรือถามต่อหลายขั้นตอน",
    icon=":material/lightbulb:",
)
