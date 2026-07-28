from __future__ import annotations

import streamlit as st


_CARD_COLORS = [
    ("#7C3AED", "#F3EDFF", "#DED3F8"),
    ("#06B6D4", "#E7F9FC", "#CDEEF4"),
    ("#10B981", "#E8FAF3", "#CFEFE2"),
    ("#EF4444", "#FEEBEC", "#F8D2D5"),
    ("#F59E0B", "#FFF4DE", "#F5E2B8"),
]


def _select_value(state_key: str, value: str) -> None:
    st.session_state[state_key] = value


def render_selection_pipeline(
    label: str,
    items: list[dict[str, str]],
    *,
    state_key: str,
    default: str,
    columns: int = 3,
) -> str:
    """Render a visible card pipeline and return the selected item value."""
    values = [item["value"] for item in items]
    if not values:
        raise ValueError("Selection pipeline requires at least one item.")
    if default not in values:
        default = values[0]
    if st.session_state.get(state_key) not in values:
        st.session_state[state_key] = default

    selected = st.session_state[state_key]
    st.markdown(f"**{label}**")
    st.caption(f"แสดงตัวเลือกทั้งหมด {len(items):,} รายการ · เลือกการ์ดเพื่อดำเนินการต่อ")

    style_rules = []
    for index, item in enumerate(items):
        accent, surface, border = _CARD_COLORS[index % len(_CARD_COLORS)]
        item_id = item.get("id", str(index))
        card_key = f"{state_key}_{item_id}_card"
        is_selected = item["value"] == selected
        selected_rules = (
            f"border-color: {accent} !important;"
            f"box-shadow: 0 0 0 2px {accent}, 0 10px 24px rgba(15, 23, 42, 0.08) !important;"
            if is_selected
            else "box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05) !important;"
        )
        style_rules.append(
            f"""
            .st-key-{card_key} {{
                position: relative;
                min-height: 11.5rem;
                padding: 0.95rem 1rem 0.85rem;
                background: linear-gradient(145deg, #FFFFFF 0%, {surface} 100%);
                border: 1px solid {border} !important;
                border-radius: 8px;
                {selected_rules}
            }}

            .st-key-{card_key}::before {{
                position: absolute;
                inset: 0 0 auto;
                height: 4px;
                border-radius: 8px 8px 0 0;
                background: {accent};
                content: "";
            }}

            .st-key-{card_key} [data-testid="stMarkdownContainer"] h4 {{
                margin: 0;
                color: #1F2937;
                font-size: 0.98rem;
                line-height: 1.35;
            }}
            """
        )

    st.html(f"<style>{''.join(style_rules)}</style>")

    columns = max(1, min(columns, 4))
    for start in range(0, len(items), columns):
        row_items = items[start : start + columns]
        row = st.columns(columns, gap="small")
        for offset, (column, item) in enumerate(zip(row, row_items)):
            item_id = item.get("id", str(start + offset))
            card_key = f"{state_key}_{item_id}_card"
            is_selected = item["value"] == selected
            with column:
                with st.container(border=True, key=card_key):
                    icon = item.get("icon", ":material/insights:")
                    st.markdown(f"#### {icon} {item['title']}")
                    st.caption(item["description"])
                    if item.get("meta"):
                        st.caption(item["meta"])
                    st.button(
                        "เลือกแล้ว" if is_selected else "เลือกคำถามนี้",
                        key=f"{state_key}_{item_id}_action",
                        type="primary" if is_selected else "secondary",
                        icon=":material/check_circle:" if is_selected else ":material/arrow_forward:",
                        width="stretch",
                        on_click=_select_value,
                        args=(state_key, item["value"]),
                    )

    return st.session_state[state_key]
