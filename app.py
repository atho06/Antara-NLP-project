import streamlit as st
import re
import html
import json
import uuid

from datetime import datetime

from question_bank import QUESTION_BANK
from llm_service import generate_followup
from crisis_detection import detect_crisis

from database import (
    register_patient,
    authenticate_patient,
    save_patient_session,
    get_patient_session,
    get_patient_sessions,
    delete_patient_session,
    get_unfinished_session,
    complete_patient_session
)


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Antara",
    page_icon="🌷",
    layout="wide"
)


# ==================================================
# 2. CUSTOM DESIGN
# ==================================================

st.markdown("""
<style>

/* ================================================
   MAIN BACKGROUND
================================================ */

.stApp {
    background: linear-gradient(
        120deg,
        #c9d8ff 0%,
        #ead5f5 50%,
        #ffcddd 100%
    ) !important;
}

/* ================================================
   GENERAL TEXT
================================================ */

.stApp p,
.stApp li,
.stApp label,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #000000;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

/* ================================================
   TOP TOOLBAR
================================================ */

header[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background-color: #f3cce8 !important;
}

header[data-testid="stHeader"] *,
[data-testid="stToolbar"] * {
    color: #000000 !important;
    fill: #000000 !important;
}

/* ================================================
   SIDEBAR: KEEP LIGHT BLUE
================================================ */

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: #b9d8ff !important;
}

section[data-testid="stSidebar"] * {
    color: #000000 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: #e8f2ff !important;
    color: #253b5c !important;
    border: 1px solid #91baf0 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    min-height: 45px;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #d5e7ff !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #e8f2ff !important;
    border: 1px solid #b9cde8 !important;
    border-radius: 12px !important;
}

/* ================================================
   INPUT FIELDS
================================================ */

[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextArea"] [data-baseweb="textarea"] {
    background: #e8f2ff !important;
    background-color: #e8f2ff !important;
    border: 1px solid #a9c9f5 !important;
    border-radius: 14px !important;
    box-shadow: none !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {
    background: transparent !important;
    color: #000000 !important;
    border: none !important;
    box-shadow: none !important;
    caret-color: #3979e8 !important;
}

[data-testid="stTextInput"] input[type="password"],
[data-testid="stTextInput"] input[type="text"],
[data-testid="stTextInput"] input[type="email"] {
    background: transparent !important;
    color: #000000 !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stTextInput"] button {
    background: #e8f2ff !important;
    color: #385b89 !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stTextInput"] button svg {
    fill: #385b89 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #7186a5 !important;
    opacity: 1 !important;
}

/* ================================================
   CHAT BUBBLES
================================================ */

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
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 18px 0;
}

.user-bubble {
    background: #3979e8 !important;
    color: #ffffff !important;
    padding: 13px 17px;
    border-radius: 16px 16px 5px 16px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

/* ================================================
   BUTTONS
================================================ */

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

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: #9fc8ff !important;
    color: #253b5c !important;
    border-color: #78a9ed !important;
}

.stButton > button p,
.stDownloadButton > button p,
[data-testid="stFormSubmitButton"] button p {
    color: #253b5c !important;
}

/* ================================================
   LOGIN CARD
================================================ */

.login-card {
    background: rgba(255,255,255,0.90) !important;
    padding: 35px;
    border-radius: 24px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0,0,0,0.06);
    margin-top: 35px;
    border: 1px solid #d8c9ed !important;
}

.login-subtitle {
    color: #55516a !important;
    font-size: 16px;
}

/* ================================================
   SECTION HEADINGS
================================================ */

.section-heading {
    background: #b9d8ff !important;
    color: #253b5c !important;
    padding: 18px 22px;
    border: 1px solid #91baf0 !important;
    border-radius: 15px;
    font-size: 22px;
    font-weight: 700;
    margin: 18px 0;
}

/* ================================================
   REGISTRATION AND LOGIN FORM BOX
================================================ */

[data-testid="stForm"] {
    background: rgba(255,255,255,0.35) !important;
    border: 1px solid rgba(255,255,255,0.65) !important;
    border-radius: 18px !important;
    padding: 18px !important;
    box-shadow: none !important;
}

/* ================================================
   EXPANDERS
================================================ */

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.45) !important;
    border: 1px solid #d8c9ed !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    color: #000000 !important;
}

/* ================================================
   TABS
================================================ */

.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] p {
    color: #000000 !important;
}

/* ================================================
   CHECKBOX
================================================ */

.stCheckbox label {
    color: #000000 !important;
}

/* ================================================
   DROPDOWNS
================================================ */

.stSelectbox div[data-baseweb="select"] > div {
    background: #e8f2ff !important;
    color: #000000 !important;
    border-color: #a9c9f5 !important;
}

/* ================================================
   PROGRESS BAR
================================================ */

[data-testid="stProgress"] > div {
    background-color: #f3cce8 !important;
    border-radius: 20px !important;
}

[data-testid="stProgress"] div[role="progressbar"] {
    background-color: #3979e8 !important;
}

/* ================================================
   CHAT INPUT: REMOVE ALL BLACK INNER AREAS
================================================ */

/* Outer chat input */

[data-testid="stChatInput"] {
    background: #e8f2ff !important;
    background-color: #e8f2ff !important;
    border: 1px solid #a9c9f5 !important;
    border-radius: 25px !important;
    box-shadow: none !important;
    overflow: hidden !important;
}

/* All inner chat input containers */

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: #e8f2ff !important;
    background-color: #e8f2ff !important;
    border: none !important;
    box-shadow: none !important;
}

/* Actual textarea */

[data-testid="stChatInput"] textarea {
    background: #e8f2ff !important;
    background-color: #e8f2ff !important;
    color: #000000 !important;
    caret-color: #3979e8 !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Placeholder */

[data-testid="stChatInput"] textarea::placeholder {
    color: #7186a5 !important;
    opacity: 1 !important;
}

/* Remove dark pseudo elements */

[data-testid="stChatInput"]::before,
[data-testid="stChatInput"]::after,
[data-testid="stChatInput"] div::before,
[data-testid="stChatInput"] div::after {
    background: #e8f2ff !important;
    box-shadow: none !important;
}

/* Send button */

[data-testid="stChatInput"] button {
    background: #b9d8ff !important;
    background-color: #b9d8ff !important;
    color: #000000 !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 20px 20px 0 !important;
}

[data-testid="stChatInput"] button:hover {
    background: #9fc8ff !important;
}

[data-testid="stChatInput"] button svg {
    fill: #000000 !important;
    color: #000000 !important;
}

/* ================================================
   BOTTOM DASHBOARD: SAME PINK AS TOP
================================================ */

[data-testid="stBottom"] {
    background: #f3cce8 !important;
    background-color: #f3cce8 !important;
    border-top: 1px solid #e6b9d8 !important;
    box-shadow: none !important;
}

[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottom"] > div > div > div {
    background: #f3cce8 !important;
    background-color: #f3cce8 !important;
    box-shadow: none !important;
}

/* Ensure chat input remains light blue */

[data-testid="stBottom"] [data-testid="stChatInput"],
[data-testid="stBottom"] [data-testid="stChatInput"] > div,
[data-testid="stBottom"] [data-testid="stChatInput"] > div > div,
[data-testid="stBottom"] [data-testid="stChatInput"] textarea {
    background: #e8f2ff !important;
    background-color: #e8f2ff !important;
}

/* ================================================
   ALERTS
================================================ */

[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* ================================================
   REMOVE UNWANTED DEFAULT BACKGROUNDS
================================================ */

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: transparent !important;
}

/* ================================================
   HIDE FOOTER
================================================ */

#MainMenu,
footer {
    visibility: hidden;
}

/* ================================================
   RESPONSIVE DESIGN
================================================ */

@media screen and (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .login-card {
        padding: 22px;
    }

    .bot-bubble,
    .user-bubble {
        max-width: 90%;
    }

}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. SESSION STATE
# ==================================================

defaults = {
    "started": False,
    "consent_given": False,
    "session_id": None,
    "current_question_index": 0,
    "responses": [],
    "submitted": False,
    "pending_followup": None,
    "pending_attempts": {},
    "unclear_message": None,
    "crisis_triggered": False,
    "crisis_acknowledged": False,
    "show_recovery": False,
    "recovery_session_id": None,
    "logged_in": False,
    "login_role": None,
    "patient_id": None,
    "patient_name": None,
    "patient_email": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 4. SESSION MANAGEMENT
# ==================================================

def generate_session_id():
    return (
        "ANT-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )


def get_session_data():
    return {
        "application": "Antara",
        "session_id": st.session_state.session_id,
        "saved_at": datetime.now().isoformat(),
        "started": st.session_state.started,
        "consent_given": st.session_state.consent_given,
        "current_question_index": st.session_state.current_question_index,
        "responses": st.session_state.responses,
        "submitted": st.session_state.submitted,
        "pending_followup": st.session_state.pending_followup,
        "pending_attempts": st.session_state.pending_attempts,
        "unclear_message": st.session_state.unclear_message,
        "crisis_triggered": st.session_state.crisis_triggered,
        "crisis_acknowledged": st.session_state.crisis_acknowledged
    }


def auto_save():

    patient_id = st.session_state.get("patient_id")
    session_id = st.session_state.get("session_id")

    if not patient_id or not session_id:
        return

    try:
        status = (
            "completed"
            if st.session_state.submitted
            else "in_progress"
        )

        save_patient_session(
            patient_id,
            session_id,
            get_session_data(),
            status
        )

    except Exception as error:
        st.error("Unable to save your session.")
        print("Database saving error:", error)


def restore_session(saved_data):

    if not isinstance(saved_data, dict):
        return False

    try:
        responses = saved_data.get("responses", [])

        if not isinstance(responses, list):
            return False

        session_id = saved_data.get("session_id")

        if not isinstance(session_id, str) or not session_id:
            return False

        st.session_state.session_id = session_id
        st.session_state.started = saved_data.get("started", False)
        st.session_state.consent_given = saved_data.get("consent_given", False)
        st.session_state.current_question_index = saved_data.get(
            "current_question_index", 0
        )
        st.session_state.responses = responses
        st.session_state.submitted = saved_data.get("submitted", False)
        st.session_state.pending_followup = saved_data.get("pending_followup")
        st.session_state.pending_attempts = saved_data.get(
            "pending_attempts", {}
        )
        st.session_state.unclear_message = saved_data.get("unclear_message")
        st.session_state.crisis_triggered = saved_data.get(
            "crisis_triggered", False
        )
        st.session_state.crisis_acknowledged = saved_data.get(
            "crisis_acknowledged", False
        )

        return True

    except (ValueError, TypeError, KeyError) as error:
        print("Session restoration error:", error)
        return False


def reset_session():

    patient_id = st.session_state.patient_id
    patient_name = st.session_state.patient_name
    patient_email = st.session_state.patient_email

    for key, value in defaults.items():
        st.session_state[key] = value

    st.session_state.logged_in = True
    st.session_state.login_role = "patient"
    st.session_state.patient_id = patient_id
    st.session_state.patient_name = patient_name
    st.session_state.patient_email = patient_email


def start_new_session():
    reset_session()
    st.session_state.show_recovery = False
    st.session_state.recovery_session_id = None


def logout():

    auto_save()

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


# ==================================================
# 5. SESSION HISTORY
# ==================================================

def get_history():

    patient_id = st.session_state.get("patient_id")

    if not patient_id:
        return []

    try:
        sessions = get_patient_sessions(patient_id)

        if not isinstance(sessions, list):
            return []

        return sorted(
            sessions,
            key=lambda item: item.get("updated_at", ""),
            reverse=True
        )

    except Exception as error:
        print("History loading error:", error)
        return []


# ==================================================
# 6. COLLECT QUESTIONS
# ==================================================

all_questions = []

for stage_number, stage_data in QUESTION_BANK.items():

    if stage_number == 1:
        continue

    for question in stage_data["questions"]:

        all_questions.append({
            "stage": stage_number,
            "stage_name": stage_data["name"],
            "id": question["id"],
            "text": question["text"]
        })


# ==================================================
# 7. RESPONSE CLASSIFICATION
# ==================================================

SKIP_WORDS = {
    "skip", "pass", "skip this",
    "don't want to answer",
    "dont want to answer",
    "i don't want to answer",
    "i dont want to answer",
    "prefer not to answer",
    "rather not say"
}

VALID_SHORT_ANSWERS = {
    "yes", "no", "yeah", "yep", "nope",
    "okay", "ok", "fine", "good", "bad",
    "maybe", "sometimes", "always", "never",
    "nothing", "everything", "not sure",
    "i don't know", "dont know", "idk"
}

KEYBOARD_PATTERNS = [
    r"asdfgh", r"asdfghjkl", r"qwerty",
    r"qwertyuiop", r"zxcvbn", r"zxcvbnm",
    r"dfgh", r"fghj", r"ghjk", r"hjkl",
    r"kjhg", r"lkjh", r"poiuy", r"mnbvc"
]


def classify_response(message):

    if not isinstance(message, str):
        return "unclear"

    text = re.sub(r"\s+", " ", message.strip().lower())

    if not text:
        return "unclear"

    if text in SKIP_WORDS or text in {"-", "--", "---"}:
        return "skipped"

    if text in VALID_SHORT_ANSWERS:
        return "answered"

    if re.fullmatch(r"(.)\1{4,}", text):
        return "unclear"

    for pattern in KEYBOARD_PATTERNS:
        if re.search(pattern, text):
            return "unclear"

    if (
        len(text) <= 3
        and text.isalpha()
        and text not in VALID_SHORT_ANSWERS
    ):
        return "unclear"

    if not re.search(r"[a-zA-Z]", text):
        return "unclear"

    return "answered"


# ==================================================
# 8. CHAT MESSAGE DISPLAY
# ==================================================

def display_message(message, sender):

    safe_message = html.escape(
        str(message)
    ).replace("\n", "<br>")

    if sender == "assistant":

        st.markdown(
            f"""
            <div class="bot-row">
                <div class="bot-bubble">
                    {safe_message}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="user-row">
                <div class="user-bubble">
                    {safe_message}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==================================================
# 9. CRISIS SAFETY SCREEN
# ==================================================

def show_crisis_screen():

    st.error("Your safety matters.")

    st.markdown("""
    Thank you for sharing something difficult.

    I'm concerned that you may be going through
    something that needs immediate human support.

    Antara cannot assess your safety or provide
    emergency assistance.

    If you may hurt yourself or someone else, or
    are in immediate danger:

    - Contact your local emergency services.
    - In India, call 112 for emergency assistance.
    - Reach out to someone you trust who can stay with you.
    - Move away from anything you could use to hurt
      yourself or someone else, if possible.
    - Contact a qualified mental-health professional.

    You do not have to handle this alone.
    """)

    st.warning(
        "Your normal Antara conversation has been paused. "
        "Please seek human support."
    )

    if st.button("End this session"):

        st.session_state.submitted = True
        auto_save()

        try:
            complete_patient_session(
                st.session_state.patient_id,
                st.session_state.session_id
            )
        except Exception as error:
            print("Session completion error:", error)

        st.rerun()


# ==================================================
# 10. SIDEBAR
# ==================================================

if st.session_state.logged_in:

    with st.sidebar:

        st.markdown("### 🌷 Your Account")

        st.write(
            f"Welcome, **{st.session_state.patient_name}**"
        )

        st.caption(st.session_state.patient_email)

        if st.button(
            "Logout",
            key="logout_button",
            use_container_width=True
        ):
            logout()

        st.divider()

        st.markdown("### 📂 Session History")

        history = get_history()

        if not history:
            st.caption("No previous sessions yet.")

        else:

            for session in history:

                session_id = session["session_id"]
                status = session["status"]

                with st.expander(
                    f"{session_id} | {status}"
                ):

                    st.caption(
                        f"Created: {session.get('created_at', 'N/A')}"
                    )

                    st.caption(
                        f"Last updated: {session.get('updated_at', 'N/A')}"
                    )

                    if status == "in_progress":

                        if st.button(
                            "Resume Session",
                            key=f"history_resume_{session_id}",
                            use_container_width=True
                        ):

                            saved_data = get_patient_session(
                                st.session_state.patient_id,
                                session_id
                            )

                            if saved_data and restore_session(saved_data):

                                st.session_state.show_recovery = False
                                st.session_state.recovery_session_id = None
                                st.rerun()

                            else:
                                st.error(
                                    "Unable to restore this session."
                                )

                    if st.button(
                        "Delete Session",
                        key=f"history_delete_{session_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"confirm_delete_{session_id}"
                        ] = True

                    if st.session_state.get(
                        f"confirm_delete_{session_id}", False
                    ):

                        st.warning(
                            "Are you sure you want to delete this session?"
                        )

                        confirm_col, cancel_col = st.columns(2)

                        with confirm_col:

                            if st.button(
                                "Confirm",
                                key=f"confirm_{session_id}"
                            ):

                                delete_patient_session(
                                    st.session_state.patient_id,
                                    session_id
                                )

                                if st.session_state.session_id == session_id:
                                    reset_session()

                                st.session_state[
                                    f"confirm_delete_{session_id}"
                                ] = False

                                st.success("Session deleted.")
                                st.rerun()

                        with cancel_col:

                            if st.button(
                                "Cancel",
                                key=f"cancel_{session_id}"
                            ):

                                st.session_state[
                                    f"confirm_delete_{session_id}"
                                ] = False

                                st.rerun()


# ==================================================
# 11. LOGIN PAGE
# ==================================================

if not st.session_state.logged_in:

    st.markdown("""
    <div class="login-card">
        <div style="font-size:65px;">🌷</div>
        <h1 style="color:#29243a;">Welcome to Antara</h1>
        <p class="login-subtitle">
            A safe space to express your feelings
            before therapy.
        </p>
        <p class="login-subtitle">
            Please choose how you would like to continue.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    patient_tab, therapist_tab = st.tabs([
        "🌸 Patient Login",
        "🩷 Therapist Login"
    ])

    with patient_tab:

        register_tab, login_tab = st.tabs([
            "Create Account",
            "Login"
        ])

        with register_tab:

            st.markdown(
                '<div class="section-heading">Create Your Account 🌷</div>',
                unsafe_allow_html=True
            )

            with st.form("patient_registration"):

                full_name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name"
                )

                email = st.text_input(
                    "Email Address",
                    placeholder="example@gmail.com"
                )

                password = st.text_input(
                    "Create Password",
                    type="password",
                    placeholder="Create a strong password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password"
                )

                register_button = st.form_submit_button(
                    "Create Account 🌷",
                    use_container_width=True
                )

                if register_button:

                    if not all([
                        full_name.strip(),
                        email.strip(),
                        password,
                        confirm_password
                    ]):
                        st.error("Please fill in all fields.")

                    elif password != confirm_password:
                        st.error("Passwords do not match.")

                    else:

                        success, message = register_patient(
                            full_name.strip(),
                            email.strip(),
                            password
                        )

                        if success:
                            st.success(
                                "Account created successfully! "
                                "Please log in."
                            )
                        else:
                            st.error(message)

        with login_tab:

            st.markdown(
                '<div class="section-heading">Welcome Back 🌷</div>',
                unsafe_allow_html=True
            )

            with st.form("patient_login"):

                login_email = st.text_input(
                    "Email Address",
                    placeholder="Enter your registered email"
                )

                login_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                login_button = st.form_submit_button(
                    "Login 🌷",
                    use_container_width=True
                )

                if login_button:

                    if not login_email.strip() or not login_password:
                        st.error(
                            "Please enter your email and password."
                        )

                    else:

                        patient = authenticate_patient(
                            login_email.strip(),
                            login_password
                        )

                        if patient:

                            st.session_state.logged_in = True
                            st.session_state.login_role = "patient"

                            st.session_state.patient_id = (
                                patient["patient_id"]
                            )

                            st.session_state.patient_name = (
                                patient["full_name"]
                            )

                            st.session_state.patient_email = (
                                patient["email"]
                            )

                            unfinished = get_unfinished_session(
                                st.session_state.patient_id
                            )

                            if unfinished:

                                st.session_state.show_recovery = True

                                st.session_state.recovery_session_id = (
                                    unfinished["session_id"]
                                )

                            else:

                                st.session_state.show_recovery = False
                                st.session_state.recovery_session_id = None

                            st.rerun()

                        else:
                            st.error(
                                "Incorrect email or password."
                            )

    with therapist_tab:

        st.markdown(
            '<div class="section-heading">Therapist Portal 🩷</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Access the therapist dashboard to review "
            "patient sessions and clinical reports."
        )

        st.text_input(
            "Email Address",
            placeholder="Enter your registered email",
            key="therapist_email"
        )

        st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="therapist_password"
        )

        st.warning(
            "Therapist login is currently under development."
        )

        st.button(
            "Therapist Login",
            disabled=True,
            use_container_width=True
        )

    st.caption(
        "Antara is a pre-therapy intake application, "
        "not a replacement for professional mental-health care."
    )


# ==================================================
# 12. SESSION RECOVERY
# ==================================================

elif st.session_state.show_recovery:

    st.info("We found an unfinished Antara session.")

    st.write(
        "Would you like to continue where you left off?"
    )

    st.caption(
        f"Session ID: {st.session_state.recovery_session_id}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Resume Previous Session",
            use_container_width=True
        ):

            saved_data = get_patient_session(
                st.session_state.patient_id,
                st.session_state.recovery_session_id
            )

            if saved_data and restore_session(saved_data):

                st.session_state.show_recovery = False
                st.session_state.recovery_session_id = None
                st.rerun()

            else:
                st.error(
                    "The saved session could not be restored."
                )

    with col2:

        if st.button(
            "Start New Session",
            use_container_width=True
        ):

            start_new_session()
            st.rerun()


# ==================================================
# 13. WELCOME AND CONSENT
# ==================================================

elif st.session_state.logged_in and not st.session_state.started:

    st.markdown("""
    <div class="login-card">
        <div style="font-size:55px;">🌷</div>
        <h2 style="color:#29243a;">Welcome to Antara</h2>
        <p class="login-subtitle">
            Before we begin, let's understand how this space works.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🌸 A little about Antara")

    st.write("""
    Antara is a pre-therapy intake application designed
    to help you express your feelings before meeting
    a qualified therapist.

    Lia will ask you a series of questions to understand
    your experiences. You can skip questions or edit
    your previous answers whenever you need to.
    """)

    st.markdown("### 🔒 Your information")

    st.warning("""
    This prototype stores session information in a local
    SQLite database. The database is not encrypted.

    Avoid entering real identifying or highly sensitive
    personal information while testing this prototype.
    """)

    st.markdown("### Important information")

    st.write("""
    - Antara does not diagnose mental-health conditions.
    - Antara does not prescribe medication or treatment.
    - Antara is not a replacement for professional therapy.
    - You can skip questions you do not wish to answer.
    - If you need immediate support, contact a qualified
      professional or emergency services.
    """)

    st.markdown("### Consent")

    consent = st.checkbox(
        "I understand how my conversation will be used "
        "and stored, and I voluntarily agree to continue."
    )

    if st.button(
        "Begin My Conversation 🌷",
        use_container_width=True
    ):

        if consent:

            st.session_state.started = True
            st.session_state.consent_given = True
            st.session_state.session_id = generate_session_id()

            auto_save()
            st.rerun()

        else:
            st.error(
                "Please provide your consent before continuing."
            )


# ==================================================
# 14. MAIN CHAT INTERFACE
# ==================================================

elif (
    st.session_state.logged_in
    and st.session_state.started
    and not st.session_state.submitted
):

    st.title("🌷 Antara")

    st.caption(
        "A space for your feelings, before therapy."
    )

    if st.session_state.crisis_triggered:

        show_crisis_screen()

    else:

        st.caption(
            f"Session ID: {st.session_state.session_id}"
        )

        current_index = st.session_state.current_question_index
        total_questions = len(all_questions)

        # DISPLAY PREVIOUS CONVERSATION

        for response_index, response in enumerate(
            st.session_state.responses
        ):

            display_message(
                response["question"],
                "assistant"
            )

            if response["status"] == "skipped":

                display_message(
                    "Question skipped",
                    "user"
                )

            else:

                display_message(
                    response["edited_answer"],
                    "user"
                )

            if response.get("followup_question"):

                is_current_followup = (
                    st.session_state.pending_followup is not None
                    and st.session_state.pending_followup.get(
                        "response_index"
                    ) == response_index
                )

                if not is_current_followup:

                    display_message(
                        response["followup_question"],
                        "assistant"
                    )

                    if response.get("followup_answer"):

                        display_message(
                            response["followup_answer"],
                            "user"
                        )

                    elif response.get("followup_skipped"):

                        display_message(
                            "Follow-up skipped",
                            "user"
                        )

            if response.get("was_edited", False):
                st.caption("✏️ Answer edited")

        # EDIT PREVIOUS ANSWERS

        if st.session_state.responses:

            with st.expander("✏️ Edit previous answers"):

                for response_index, response in enumerate(
                    st.session_state.responses
                ):

                    st.markdown(
                        f"**{response['question']}**"
                    )

                    if response["status"] == "skipped":
                        st.caption("Skipped")
                        continue

                    st.write(response["edited_answer"])

                    question_id = response["question_id"]
                    edit_key = f"edit_mode_{question_id}"

                    if st.button(
                        "Edit",
                        key=f"edit_button_{question_id}_{response_index}"
                    ):
                        st.session_state[edit_key] = True

                    if st.session_state.get(edit_key, False):

                        new_answer = st.text_area(
                            "Update your answer",
                            value=response["edited_answer"],
                            key=f"edit_text_{question_id}"
                        )

                        if st.button(
                            "Save",
                            key=f"save_{question_id}"
                        ):

                            if new_answer.strip():

                                old_answer = response["edited_answer"]
                                cleaned_answer = new_answer.strip()

                                if old_answer != cleaned_answer:

                                    if "edit_history" not in response:
                                        response["edit_history"] = []

                                    response["edit_history"].append({
                                        "previous_answer": old_answer,
                                        "new_answer": cleaned_answer
                                    })

                                    response["edited_answer"] = cleaned_answer
                                    response["was_edited"] = True
                                    auto_save()

                            st.session_state[edit_key] = False
                            st.rerun()

        # HANDLE PENDING FOLLOW-UP

        if st.session_state.pending_followup is not None:

            pending = st.session_state.pending_followup

            response_index = pending["response_index"]
            followup_question = pending["question"]

            display_message(
                followup_question,
                "assistant"
            )

            if st.session_state.unclear_message:
                display_message(
                    st.session_state.unclear_message,
                    "assistant"
                )

            followup_input = st.chat_input(
                "Answer or type 'skip'..."
            )

            if followup_input:

                if detect_crisis(followup_input):

                    st.session_state.crisis_triggered = True
                    auto_save()
                    st.rerun()

                else:

                    status = classify_response(followup_input)

                    if status == "unclear":

                        st.session_state.unclear_message = (
                            "I couldn't quite understand that response. "
                            "Would you like to try again or skip this question?"
                        )

                        auto_save()
                        st.rerun()

                    elif status == "skipped":

                        st.session_state.responses[
                            response_index
                        ]["followup_skipped"] = True

                    else:

                        st.session_state.responses[
                            response_index
                        ]["followup_answer"] = followup_input

                    st.session_state.pending_followup = None
                    st.session_state.unclear_message = None
                    st.session_state.current_question_index += 1

                    auto_save()
                    st.rerun()

        # DISPLAY CORE QUESTION

        elif current_index < total_questions:

            current_question = all_questions[current_index]
            question_id = current_question["id"]

            st.progress(
                min(
                    (current_index + 1) / total_questions,
                    1.0
                )
            )

            st.caption(
                f"Stage {current_question['stage']}: "
                f"{current_question['stage_name']}"
            )

            display_message(
                current_question["text"],
                "assistant"
            )

            attempts = st.session_state.pending_attempts.get(
                question_id, []
            )

            for attempt in attempts:
                display_message(attempt, "user")

            if st.session_state.unclear_message:
                display_message(
                    st.session_state.unclear_message,
                    "assistant"
                )

            user_message = st.chat_input(
                "Type your response or enter 'skip'..."
            )

            if user_message:

                if detect_crisis(user_message):

                    st.session_state.crisis_triggered = True
                    auto_save()
                    st.rerun()

                else:

                    status = classify_response(user_message)

                    attempts = st.session_state.pending_attempts.get(
                        question_id, []
                    )

                    if status == "unclear":

                        attempts.append(user_message)

                        st.session_state.pending_attempts[
                            question_id
                        ] = attempts

                        st.session_state.unclear_message = (
                            "I couldn't quite understand that response. "
                            "Would you like to try again or skip this question?"
                        )

                        auto_save()
                        st.rerun()

                    elif status == "skipped":

                        st.session_state.responses.append({

                            "stage": current_question["stage"],
                            "stage_name": current_question["stage_name"],
                            "question_id": question_id,
                            "question": current_question["text"],
                            "original_answer": None,
                            "edited_answer": None,
                            "was_edited": False,
                            "edit_history": [],
                            "status": "skipped",
                            "skipped": True,
                            "followup_question": None,
                            "followup_answer": None,
                            "followup_skipped": False

                        })

                        st.session_state.pending_attempts.pop(
                            question_id,
                            None
                        )

                        st.session_state.unclear_message = None
                        st.session_state.current_question_index += 1

                        auto_save()
                        st.rerun()

                    else:

                        new_response = {

                            "stage": current_question["stage"],
                            "stage_name": current_question["stage_name"],
                            "question_id": question_id,
                            "question": current_question["text"],
                            "original_answer": user_message,
                            "edited_answer": user_message,
                            "was_edited": False,
                            "edit_history": [],
                            "status": "answered",
                            "skipped": False,
                            "followup_question": None,
                            "followup_answer": None,
                            "followup_skipped": False

                        }

                        st.session_state.responses.append(new_response)

                        response_index = (
                            len(st.session_state.responses) - 1
                        )

                        st.session_state.pending_attempts.pop(
                            question_id,
                            None
                        )

                        st.session_state.unclear_message = None

                        auto_save()

                        with st.spinner("Lia is thinking..."):

                            history = []

                            for item in st.session_state.responses[:-1]:

                                if item["status"] == "answered":

                                    history.append({
                                        "role": "user",
                                        "content": (
                                            item["question"]
                                            + "\n"
                                            + item["edited_answer"]
                                        )
                                    })

                                    if item.get("followup_question"):

                                        history.append({
                                            "role": "assistant",
                                            "content": item["followup_question"]
                                        })

                                        if item.get("followup_answer"):

                                            history.append({
                                                "role": "user",
                                                "content": item["followup_answer"]
                                            })

                            result = generate_followup(
                                current_question["text"],
                                user_message,
                                history
                            )

                        if result["follow_up_needed"]:

                            st.session_state.responses[
                                response_index
                            ]["followup_question"] = result["message"]

                            st.session_state.pending_followup = {
                                "response_index": response_index,
                                "question": result["message"]
                            }

                        else:

                            st.session_state.current_question_index += 1

                        auto_save()
                        st.rerun()

        # ALL QUESTIONS COMPLETED

        else:

            st.success(
                "You've completed all the questions!"
            )

            st.write(
                f"Total core questions processed: "
                f"{len(st.session_state.responses)}"
            )

            if st.button("Submit Session"):

                st.session_state.submitted = True
                auto_save()

                try:
                    complete_patient_session(
                        st.session_state.patient_id,
                        st.session_state.session_id
                    )
                except Exception as error:
                    print("Session completion error:", error)

                st.rerun()


# ==================================================
# 15. FINAL THANK-YOU SCREEN
# ==================================================

elif st.session_state.submitted:

    st.markdown("""
    <div style="
        background:rgba(255,255,255,0.85);
        padding:35px 25px;
        border-radius:22px;
        text-align:center;
        margin-top:25px;
        border:1px solid #c0d5f3;
        box-shadow:0 4px 15px rgba(0,0,0,0.06);
    ">
        <div style="font-size:55px;">🌷</div>
        <h1 style="color:#29243a;">Thank You</h1>
        <p style="color:#55516a;font-size:17px;">
            Thank you for sharing your feelings with honesty.
            Every feeling deserves to be heard.
        </p>
        <p style="color:#55516a;font-size:15px;">
            Your Antara session has ended.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🌸 Session Details")

    st.info(
        f"**Session ID:** {st.session_state.session_id}"
    )

    st.write(
        f"**Questions processed:** "
        f"{len(st.session_state.responses)}"
    )

    st.write("**Session status:** Ended")

    session_data = {
        "application": "Antara",
        "session_id": st.session_state.session_id,
        "patient_id": st.session_state.patient_id,
        "session_date": datetime.now().isoformat(),
        "total_questions": len(st.session_state.responses),
        "crisis_triggered": st.session_state.crisis_triggered,
        "responses": st.session_state.responses
    }

    json_data = json.dumps(
        session_data,
        indent=4,
        ensure_ascii=False
    )

    st.divider()

    st.markdown("### 📄 Your Session Report")

    st.write(
        "Your conversation data is ready to be downloaded."
    )

    st.download_button(
        label="📥 Download Session Data (JSON)",
        data=json_data,
        file_name=f"{st.session_state.session_id}.json",
        mime="application/json",
        use_container_width=True
    )

    st.divider()

    st.markdown("### 🩷 Therapist Portal")

    st.success(
        "Your clinical report is ready for therapist review in the Antara Clinical Intelligence Portal. "
        "You can import your downloaded session JSON there or view case studies."
    )
    st.markdown(
        '<a href="http://127.0.0.1:8000/therapist" target="_blank" style="display:inline-block;padding:10px 20px;background:#6d28d9;color:white;text-decoration:none;border-radius:8px;font-weight:600;">🌸 Open Therapist Intelligence Portal</a>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 🌷 Start Again")

    st.write(
        "Whenever you're ready, you can begin a new session."
    )

    if st.button(
        "🌷 Start New Session",
        use_container_width=True
    ):

        start_new_session()
        st.rerun()