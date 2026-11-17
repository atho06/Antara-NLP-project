"""
Antara Theme Manager
Supports:
- ☀️ Light Mode (gentle pastel lavender & pink gradient with soft blue accents)
- 🌙 Dark Mode (calming midnight slate & obsidian with soft violet highlights)
- ⚙️ System Mode (automatically follows user's OS / browser color scheme)
"""

import streamlit as st

THEME_OPTIONS = ["⚙️ System", "☀️ Light", "🌙 Dark"]

# CSS rules for Light Mode
LIGHT_CSS_RULES = """
.stApp {
    background: linear-gradient(120deg, #c9d8ff 0%, #ead5f5 50%, #ffcddd 100%) !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: transparent !important;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.stApp p, .stApp li, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: #29243a !important;
}

header[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: #f3cce8 !important;
}

header[data-testid="stHeader"] *,
[data-testid="stToolbar"] * {
    color: #29243a !important;
    fill: #29243a !important;
}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: #b9d8ff !important;
}

section[data-testid="stSidebar"] * {
    color: #253b5c !important;
}

.sidebar-profile {
    background: rgba(255, 255, 255, 0.70) !important;
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 18px;
    border: 1px solid rgba(255, 255, 255, 0.85);
}

.sidebar-title {
    text-align: center;
    font-size: 23px;
    font-weight: 700;
    color: #344c78 !important;
}

.sidebar-email {
    color: #55516a !important;
    font-size: 13px;
    overflow-wrap: anywhere;
}

.sidebar-heading {
    font-size: 17px;
    font-weight: 700;
    color: #344c78 !important;
    margin-top: 20px;
    margin-bottom: 12px;
}

section[data-testid="stSidebar"] .stButton > button {
    background: #e8f2ff !important;
    color: #253b5c !important;
    border: 1px solid #91baf0 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    min-height: 45px;
}

[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stNumberInput"] [data-baseweb="input"] {
    background: #E8F2FF !important;
    border: 1px solid #A9C9F5 !important;
    border-radius: 14px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #E8F2FF !important;
    color: #222 !important;
    -webkit-text-fill-color: #222 !important;
    border: none !important;
    caret-color: #3979e8 !important;
}

[data-testid="stDateInput"] input {
    background: #E8F2FF !important;
    color: #222 !important;
    border: 1px solid #A9C9F5 !important;
    border-radius: 14px !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: #E8F2FF !important;
    border: 1px solid #A9C9F5 !important;
    border-radius: 12px !important;
}

.stSelectbox div[data-baseweb="select"] * {
    color: #222 !important;
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
    background: #b9d8ff !important;
    color: #253b5c !important;
    border: 1px solid #91baf0 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    padding: 12px 18px !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background: #9fc8ff !important;
}

.login-card {
    background: rgba(255, 255, 255, .90) !important;
    padding: 35px;
    border-radius: 24px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0, 0, 0, .06);
    margin-top: 25px;
    border: 1px solid #d8c9ed;
}

.login-subtitle {
    color: #55516a !important;
    font-size: 16px;
}

[data-testid="stForm"] {
    background: rgba(255, 255, 255, .45) !important;
    border: 1px solid rgba(255, 255, 255, .75) !important;
    border-radius: 18px !important;
    padding: 18px !important;
}

.bot-row {
    display: flex;
    justify-content: flex-start;
    margin: 18px 0;
}

.bot-bubble {
    background: #eeeaf1 !important;
    color: #292633 !important;
    padding: 13px 17px;
    border-radius: 16px 16px 16px 5px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
    border: 1px solid #ddd6e8;
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 18px 0;
}

.user-bubble {
    background: #3979e8 !important;
    color: #fff !important;
    padding: 13px 17px;
    border-radius: 16px 16px 5px 16px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

[data-testid="stProgress"] {
    background: transparent !important;
}

[data-testid="stProgress"] > div {
    background: #E8F2FF !important;
    border-radius: 20px !important;
    height: 10px !important;
    overflow: hidden !important;
}

[data-testid="stProgress"] div[role="progressbar"] {
    background: #3979e8 !important;
    border-radius: 20px !important;
}

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottomBlockContainer"] {
    background: #b9d8ff !important;
}

[data-testid="stBottom"] {
    border-top: 1px solid #91baf0 !important;
}

[data-testid="stChatInput"] {
    background: #E8F2FF !important;
    border: 2px solid #91baf0 !important;
    border-radius: 25px !important;
    overflow: hidden !important;
}

[data-testid="stChatInput"] textarea {
    background: #E8F2FF !important;
    color: #222 !important;
}

.quick-heading {
    color: #57455f !important;
    font-size: 14px;
    font-weight: 600;
    margin-top: 15px;
    margin-bottom: 8px;
}

.dashboard-welcome {
    background: rgba(255, 255, 255, 0.88) !important;
    padding: 28px;
    border-radius: 22px;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 5px 20px rgba(70, 60, 100, 0.07);
    margin-bottom: 25px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.88) !important;
    padding: 23px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 4px 15px rgba(70, 60, 100, 0.06);
    min-height: 125px;
}

.activity-card {
    background: rgba(255, 255, 255, 0.85) !important;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e8ddf0;
    margin-bottom: 12px;
}

[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.70) !important;
    border: 1px solid #d8c9ed !important;
    border-radius: 14px !important;
}
"""

# CSS rules for Dark Mode
DARK_CSS_RULES = """
.stApp {
    background: linear-gradient(135deg, #0b0c16 0%, #151327 50%, #1e152f 100%) !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: transparent !important;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.stApp p, .stApp li, .stApp label {
    color: #cbd5e1 !important;
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: #f8fafc !important;
}

header[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: #141126 !important;
    border-bottom: 1px solid #282444 !important;
}

header[data-testid="stHeader"] *,
[data-testid="stToolbar"] * {
    color: #f1f5f9 !important;
    fill: #f1f5f9 !important;
}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: #0f101d !important;
    border-right: 1px solid #282444 !important;
}

section[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}

.sidebar-profile {
    background: rgba(25, 23, 42, 0.85) !important;
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 18px;
    border: 1px solid #363056 !important;
}

.sidebar-title {
    text-align: center;
    font-size: 23px;
    font-weight: 700;
    color: #e9d5ff !important;
}

.sidebar-email {
    color: #94a3b8 !important;
    font-size: 13px;
    overflow-wrap: anywhere;
}

.sidebar-heading {
    font-size: 17px;
    font-weight: 700;
    color: #e9d5ff !important;
    margin-top: 20px;
    margin-bottom: 12px;
}

section[data-testid="stSidebar"] .stButton > button {
    background: #1e1b33 !important;
    color: #e9d5ff !important;
    border: 1px solid #3d3563 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    min-height: 45px;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2e284e !important;
    color: #ffffff !important;
    border-color: #7c5ebd !important;
}

[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stNumberInput"] [data-baseweb="input"] {
    background: #19162e !important;
    border: 1px solid #3c3461 !important;
    border-radius: 14px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #19162e !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    border: none !important;
    caret-color: #c084fc !important;
}

[data-testid="stDateInput"] input {
    background: #19162e !important;
    color: #f1f5f9 !important;
    border: 1px solid #3c3461 !important;
    border-radius: 14px !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: #19162e !important;
    border: 1px solid #3c3461 !important;
    border-radius: 12px !important;
}

.stSelectbox div[data-baseweb="select"] * {
    color: #f1f5f9 !important;
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
    background: #2f2549 !important;
    color: #f5e8ff !important;
    border: 1px solid #5a4585 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    padding: 12px 18px !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background: #443468 !important;
    color: #ffffff !important;
    border-color: #8b5cf6 !important;
}

.login-card {
    background: rgba(22, 19, 36, 0.88) !important;
    padding: 35px;
    border-radius: 24px;
    text-align: center;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
    margin-top: 25px;
    border: 1px solid #373059 !important;
}

.login-subtitle {
    color: #94a3b8 !important;
    font-size: 16px;
}

[data-testid="stForm"] {
    background: rgba(20, 18, 35, 0.65) !important;
    border: 1px solid #373059 !important;
    border-radius: 18px !important;
    padding: 18px !important;
}

.bot-row {
    display: flex;
    justify-content: flex-start;
    margin: 18px 0;
}

.bot-bubble {
    background: #24203a !important;
    color: #f1f5f9 !important;
    padding: 13px 17px;
    border-radius: 16px 16px 16px 5px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
    border: 1px solid #3c3461 !important;
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 18px 0;
}

.user-bubble {
    background: #5b4699 !important;
    color: #ffffff !important;
    padding: 13px 17px;
    border-radius: 16px 16px 5px 16px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
    border: 1px solid #7c5ebd !important;
}

[data-testid="stProgress"] {
    background: transparent !important;
}

[data-testid="stProgress"] > div {
    background: #19162e !important;
    border-radius: 20px !important;
    height: 10px !important;
    overflow: hidden !important;
}

[data-testid="stProgress"] div[role="progressbar"] {
    background: #a855f7 !important;
    border-radius: 20px !important;
}

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottomBlockContainer"] {
    background: #0f101d !important;
}

[data-testid="stBottom"] {
    border-top: 1px solid #282444 !important;
}

[data-testid="stChatInput"] {
    background: #19162e !important;
    border: 2px solid #5a4585 !important;
    border-radius: 25px !important;
    overflow: hidden !important;
}

[data-testid="stChatInput"] textarea {
    background: #19162e !important;
    color: #f1f5f9 !important;
}

.quick-heading {
    color: #e9d5ff !important;
    font-size: 14px;
    font-weight: 600;
    margin-top: 15px;
    margin-bottom: 8px;
}

.dashboard-welcome {
    background: rgba(22, 19, 36, 0.88) !important;
    padding: 28px;
    border-radius: 22px;
    border: 1px solid #373059 !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.40);
    margin-bottom: 25px;
}

.stat-card {
    background: rgba(22, 19, 36, 0.88) !important;
    padding: 23px;
    border-radius: 20px;
    border: 1px solid #373059 !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    min-height: 125px;
}

.stat-number {
    color: #e9d5ff !important;
}

.stat-label {
    color: #94a3b8 !important;
}

.activity-card {
    background: rgba(25, 22, 42, 0.85) !important;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #3c3461 !important;
    margin-bottom: 12px;
}

[data-testid="stExpander"] {
    background: rgba(25, 22, 42, 0.75) !important;
    border: 1px solid #3c3461 !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] * {
    color: #f1f5f9 !important;
}
"""

# Common CSS (independent of theme)
COMMON_CSS = """
#MainMenu, footer {
    visibility: hidden;
}

/* Smooth gradual theme transitions */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.login-card,
.dashboard-welcome,
.stat-card,
.activity-card,
.bot-bubble,
.user-bubble,
.sidebar-profile,
[data-testid="stForm"],
.stButton > button,
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
div[data-baseweb="select"] > div {
    transition: background 0.9s cubic-bezier(0.25, 0.8, 0.25, 1),
                background-color 0.9s cubic-bezier(0.25, 0.8, 0.25, 1),
                color 0.65s ease-in-out,
                border-color 0.85s ease-in-out,
                box-shadow 0.9s ease-in-out !important;
}

@keyframes themeGradualFade {
    0% {
        opacity: 0.75;
        filter: blur(1px);
    }
    100% {
        opacity: 1;
        filter: blur(0px);
    }
}

.stApp {
    animation: themeGradualFade 0.85s cubic-bezier(0.25, 1, 0.5, 1) !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .login-card {
        padding: 22px;
    }

    .bot-bubble, .user-bubble {
        max-width: 90%;
    }
}
"""


def get_theme_css(theme_mode: str) -> str:
    """Returns the comprehensive CSS stylesheet for the requested theme mode."""
    if "Dark" in theme_mode:
        return f"<style>\n{DARK_CSS_RULES}\n{COMMON_CSS}\n</style>"
    elif "Light" in theme_mode:
        return f"<style>\n{LIGHT_CSS_RULES}\n{COMMON_CSS}\n</style>"
    else:
        # System Mode: default to Light, and use media query for Dark
        return f"""<style>
{LIGHT_CSS_RULES}
{COMMON_CSS}

@media (prefers-color-scheme: dark) {{
{DARK_CSS_RULES}
}}
</style>"""


def apply_theme_css():
    """Injects the theme CSS into the current Streamlit render cycle."""
    current_theme = st.session_state.get("app_theme", "⚙️ System")
    css = get_theme_css(current_theme)
    st.markdown(css, unsafe_allow_html=True)


def render_theme_toggle(sidebar: bool = True):
    """Renders a sleek theme toggle in the UI (sidebar or main)."""
    current_theme = st.session_state.get("app_theme", "⚙️ System")
    idx = THEME_OPTIONS.index(current_theme) if current_theme in THEME_OPTIONS else 0

    container = st.sidebar if sidebar else st
    selected = container.selectbox(
        "🌓 App Theme",
        THEME_OPTIONS,
        index=idx,
        key="app_theme_picker",
        help="Select Light, Dark, or System mode"
    )

    if selected != current_theme:
        st.session_state.app_theme = selected
        st.rerun()
