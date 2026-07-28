from __future__ import annotations

import streamlit as st


THEME_KEY = "odos_appearance_theme_v1"
ACCENT_KEY = "odos_appearance_accent_v1"

ACCENTS = {
    "violet": {
        "label": "Violet",
        "base": "#7C3AED",
        "light": "#8B5CF6",
        "soft": "#F3E8FF",
    },
    "cyan": {
        "label": "Cyan",
        "base": "#06B6D4",
        "light": "#22D3EE",
        "soft": "#E6F9FC",
    },
    "green": {
        "label": "Green",
        "base": "#10B981",
        "light": "#34D399",
        "soft": "#E8F9F3",
    },
    "coral": {
        "label": "Coral",
        "base": "#EF4444",
        "light": "#FB7185",
        "soft": "#FEECEC",
    },
    "orange": {
        "label": "Orange",
        "base": "#F59E0B",
        "light": "#FBBF24",
        "soft": "#FFF6E3",
    },
}


def _set_accent(accent: str) -> None:
    st.session_state[ACCENT_KEY] = accent


def _dark_theme_rules() -> str:
    return """
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {
            background-color: #0F172A !important;
        }

        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-color: #273449 !important;
        }

        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: #F8FAFC !important;
        }

        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] li {
            color: #CBD5E1;
        }

        .stApp div[data-testid="stMetric"] {
            background: linear-gradient(145deg, #182235 0%, #111827 100%) !important;
            border-color: #334155 !important;
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18) !important;
        }

        .stApp div[data-testid="stMetricLabel"] {
            color: #A8B5C7 !important;
        }

        .stApp div[data-testid="stMetricValue"] {
            color: #F8FAFC !important;
        }

        .stApp div[data-testid="stMetricDelta"] {
            background-color: #202C40 !important;
            border-color: #334155 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stExpander"],
        [data-testid="stPopoverBody"] {
            background-color: #151F31 !important;
            border-color: #334155 !important;
        }

        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stFileUploaderDropzone"] {
            background-color: #182235 !important;
            border-color: #3B4A61 !important;
            color: #F8FAFC !important;
        }

        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            border-color: #334155 !important;
        }

        [data-testid="stCaptionContainer"],
        [data-testid="stWidgetLabel"] p {
            color: #A8B5C7 !important;
        }
    """


def _render_runtime_styles(theme: str, accent_name: str) -> None:
    accent = ACCENTS[accent_name]
    swatch_rules = []
    for name, values in ACCENTS.items():
        selected = name == accent_name
        ring = (
            f"0 0 0 2px #FFFFFF, 0 0 0 4px {values['base']}"
            if selected
            else "0 1px 3px rgba(15, 23, 42, 0.15)"
        )
        swatch_rules.append(
            f"""
            .st-key-appearance_swatch_{name}_v1 button {{
                width: 2rem !important;
                min-width: 2rem !important;
                height: 2rem !important;
                min-height: 2rem !important;
                padding: 0 !important;
                border: 2px solid #FFFFFF !important;
                border-radius: 999px !important;
                background: {values["base"]} !important;
                box-shadow: {ring} !important;
                color: transparent !important;
                font-size: 0 !important;
            }}
            """
        )

    common_rules = f"""
        :root {{
            --odos-accent: {accent["base"]};
            --odos-accent-light: {accent["light"]};
            --odos-accent-soft: {accent["soft"]};
        }}

        button[kind="primary"] {{
            background: linear-gradient(
                135deg,
                var(--odos-accent) 0%,
                var(--odos-accent-light) 100%
            ) !important;
            border-color: var(--odos-accent) !important;
            box-shadow: 0 5px 14px color-mix(in srgb, var(--odos-accent) 24%, transparent);
        }}

        button[aria-pressed="true"],
        [data-baseweb="tab"][aria-selected="true"] {{
            color: var(--odos-accent) !important;
            border-color: var(--odos-accent) !important;
            background-color: var(--odos-accent-soft) !important;
        }}

        [data-testid="stSidebarNavLink"][aria-current="page"] {{
            color: var(--odos-accent) !important;
            background-color: var(--odos-accent-soft) !important;
        }}

        a:not([data-testid="stSidebarNavLink"]) {{
            color: var(--odos-accent);
        }}

        {"".join(swatch_rules)}
    """

    if theme == "Dark":
        theme_rules = _dark_theme_rules()
    elif theme == "System":
        theme_rules = f"@media (prefers-color-scheme: dark) {{{_dark_theme_rules()}}}"
    else:
        theme_rules = ""

    st.html(f"<style>{common_rules}{theme_rules}</style>")


def render_appearance() -> None:
    """Render a persistent app-wide appearance selector in the sidebar."""
    st.session_state.setdefault(THEME_KEY, "Light")
    st.session_state.setdefault(ACCENT_KEY, "violet")

    with st.sidebar.expander("Appearance", icon=":material/palette:"):
        theme = st.segmented_control(
            "Theme",
            ["Dark", "Light", "System"],
            key=THEME_KEY,
            selection_mode="single",
            required=True,
            width="stretch",
            persist_state="session",
        )
        st.caption("Accent color")
        columns = st.columns(len(ACCENTS), gap="small")
        for column, (name, values) in zip(columns, ACCENTS.items(), strict=True):
            with column:
                st.button(
                    values["label"],
                    key=f"appearance_swatch_{name}_v1",
                    help=values["label"],
                    on_click=_set_accent,
                    args=(name,),
                )

    accent_name = st.session_state.get(ACCENT_KEY, "violet")
    if accent_name not in ACCENTS:
        accent_name = "violet"
    _render_runtime_styles(theme or "Light", accent_name)
