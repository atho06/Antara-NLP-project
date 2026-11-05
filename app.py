import streamlit as st
import re
import html
import json
import uuid
import requests

from datetime import datetime, date

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


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Antara",
    page_icon="🌷",
    layout="wide"
)


# ==========================================================
# 2. CUSTOM DESIGN
# ==========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        120deg,
        #c9d8ff 0%,
        #ead5f5 50%,
        #ffcddd 100%
    ) !important;
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

.stApp p,
.stApp li,
.stApp label,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #000000;
}

/* HEADER */

header[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background-color: #f3cce8 !important;
}

header[data-testid="stHeader"] *,
[data-testid="stToolbar"] * {
    color: #000000 !important;
    fill: #000000 !important;
}

/* SIDEBAR */

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

/* INPUT FIELDS */

[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stNumberInput"] [data-baseweb="input"] {
    background: #E8F2FF !important;
    background-color: #E8F2FF !important;
    border: 1px solid #A9C9F5 !important;
    border-radius: 14px !important;
    box-shadow: none !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #E8F2FF !important;
    background-color: #E8F2FF !important;
    color: #222222 !important;
    -webkit-text-fill-color: #222222 !important;
    border: none !important;
    box-shadow: none !important;
    caret-color: #3979e8 !important;
}

[data-testid="stTextInput"] input[type="password"],
[data-testid="stTextInput"] input[type="text"],
[data-testid="stTextInput"] input[type="email"] {
    background: #E8F2FF !important;
    background-color: #E8F2FF !important;
    color: #222222 !important;
    -webkit-text-fill-color: #222222 !important;
}

[data-testid="stTextInput"] input:-webkit-autofill,
[data-testid="stTextInput"] input:-webkit-autofill:hover,
[data-testid="stTextInput"] input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #E8F2FF inset !important;
    -webkit-text-fill-color: #222222 !important;
}

[data-testid="stTextInput"] button {
    background: #E8F2FF !important;
    color: #385b89 !important;
    border: none !important;
}

[data-testid="stTextInput"] button svg {
    fill: #385b89 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #7186a5 !important;
    opacity: 1 !important;
}

/* DATE INPUT */

[data-testid="stDateInput"] input {
    background: #E8F2FF !important;
    background-color: #E8F2FF !important;
    color: #222222 !important;
    -webkit-text-fill-color: #222222 !important;
    border: 1px solid #A9C9F5 !important;
    border-radius: 14px !important;
}

/* SELECTBOX */

.stSelectbox div[data-baseweb="select"] > div {
    background: #E8F2FF !important;
    background-color: #E8F2FF !important;
    color: #222222 !important;
    border: 1px solid #A9C9F5 !important;
    border-radius: 12px !important;
}

/* CHECKBOX */

.stCheckbox label {
    color: #000000 !important;
}

/* BUTTONS */

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

.stButton > button *,
.stDownloadButton > button *,
[data-testid="stFormSubmitButton"] button * {
    color: #253b5c !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: #9fc8ff !important;
    color: #253b5c !important;
}

/* LOGIN CARD */

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

/* FORMS */

[data-testid="stForm"] {
    background: rgba(255,255,255,0.35) !important;
    border: 1px solid rgba(255,255,255,0.65) !important;
    border-radius: 18px !important;
    padding: 18px !important;
    box-shadow: none !important;
}

/* EXPANDERS */

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.45) !important;
    border: 1px solid #d8c9ed !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    color: #000000 !important;
}

/* TABS */

.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] p {
    color: #000000 !important;
}

/* CHAT BUBBLES */

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

/* PROGRESS */

[data-testid="stProgress"] > div {
    background-color: #f3cce8 !important;
    border-radius: 20px !important;
}

[data-testid="stProgress"] div[role="progressbar"] {
    background-color: #3979e8 !important;
}

/* CHAT INPUT */

[data-testid="stChatInput"] {
    background: #E8F2FF !important;
    background-color: #E8F2FF !important;
    border: 1px solid #A9C9F5 !important;
    border-radius: 25px !important;
    box-shadow: none !important;
    overflow: hidden !important;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: #E8F2FF !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea {
    background: #E8F2FF !important;
    color: #222222 !important;
    -webkit-text-fill-color: #222222 !important;
    caret-color: #3979e8 !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #7186a5 !important;
}

[data-testid="stChatInput"] button {
    background: #b9d8ff !important;
    color: #000000 !important;
    border: none !important;
}

[data-testid="stChatInput"] button svg {
    fill: #000000 !important;
}

/* BOTTOM CHAT AREA */

[data-testid="stBottom"] {
    background: #f3cce8 !important;
    border-top: 1px solid #e6b9d8 !important;
}

[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {
    background: #f3cce8 !important;
}

/* ALERTS */

[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* HIDE FOOTER */

#MainMenu,
footer {
    visibility: hidden;
}

/* MOBILE */

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


# ==========================================================
# 3. INDIA LOCATION LOOKUP
# ==========================================================

@st.cache_data(ttl=86400, show_spinner=False)
def search_indian_post_offices(query):

    try:

        response = requests.get(
            "https://api.pincodeapi.in/api/v1/search",
            params={
                "q": query,
                "limit": 20,
                "offset": 0
            },
            timeout=12
        )

        response.raise_for_status()
        result = response.json()

        if not isinstance(result, dict) or not result.get("success"):
            return []

        data = result.get("data", {})

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get("post_offices", [])

        return []

    except (
        requests.RequestException,
        ValueError,
        TypeError
    ) as error:

        print("Location API error:", error)
        return []


def calculate_age(dob):

    if not dob:
        return ""

    today = date.today()

    return (
        today.year - dob.year
        - ((today.month, today.day) < (dob.month, dob.day))
    )


# ==========================================================
# 4. SESSION STATE
# ==========================================================

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
    "patient_email": None,
    "location_signature": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================================
# 5. SESSION MANAGEMENT
# ==========================================================

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

    if not patient_id:
        print("AUTO SAVE ERROR: Patient ID is missing.")
        return False

    if not session_id:
        return False

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

        print(
            f"AUTO SAVE SUCCESS: Session {session_id} "
            f"saved for patient {patient_id}"
        )

        return True

    except Exception as error:

        print("DATABASE SAVING ERROR:", error)
        return False


def restore_session(saved_data):

    if not isinstance(saved_data, dict):
        return False

    try:

        # Support both direct session data and wrapped database results.

        if isinstance(saved_data.get("session_data"), dict):
            saved_data = saved_data["session_data"]

        responses = saved_data.get("responses", [])
        session_id = saved_data.get("session_id")

        if not isinstance(responses, list):
            return False

        if not isinstance(session_id, str) or not session_id:
            return False

        st.session_state.session_id = session_id

        st.session_state.started = saved_data.get(
            "started", True
        )

        st.session_state.consent_given = saved_data.get(
            "consent_given", True
        )

        question_index = saved_data.get(
            "current_question_index", 0
        )

        try:
            question_index = int(question_index)
        except (ValueError, TypeError):
            question_index = 0

        st.session_state.current_question_index = max(
            0,
            min(question_index, len(all_questions))
        )

        st.session_state.responses = responses

        st.session_state.submitted = saved_data.get(
            "submitted", False
        )

        st.session_state.pending_followup = saved_data.get(
            "pending_followup"
        )

        st.session_state.pending_attempts = saved_data.get(
            "pending_attempts", {}
        )

        st.session_state.unclear_message = saved_data.get(
            "unclear_message"
        )

        st.session_state.crisis_triggered = saved_data.get(
            "crisis_triggered", False
        )

        st.session_state.crisis_acknowledged = saved_data.get(
            "crisis_acknowledged", False
        )

        st.session_state.show_recovery = False
        st.session_state.recovery_session_id = None

        return True

    except Exception as error:

        print("SESSION RESTORATION ERROR:", error)
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

    saved = auto_save()

    if (
        st.session_state.get("session_id")
        and st.session_state.get("started")
        and not saved
    ):

        st.error(
            "Your session could not be saved. "
            "Please check the database before logging out."
        )

        return

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


# ==========================================================
# 6. SESSION HISTORY
# ==========================================================

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
            key=lambda item: (
                item.get("updated_at")
                or item.get("created_at")
                or ""
            ),
            reverse=True
        )

    except Exception as error:

        print("HISTORY LOADING ERROR:", error)
        return []


# ==========================================================
# 7. COLLECT QUESTIONS
# ==========================================================

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


# ==========================================================
# 8. RESPONSE CLASSIFICATION
# ==========================================================

SKIP_WORDS = {
    "skip",
    "pass",
    "skip this",
    "don't want to answer",
    "dont want to answer",
    "i don't want to answer",
    "i dont want to answer",
    "prefer not to answer",
    "rather not say"
}

VALID_SHORT_ANSWERS = {
    "yes",
    "no",
    "yeah",
    "yep",
    "nope",
    "okay",
    "ok",
    "fine",
    "good",
    "bad",
    "maybe",
    "sometimes",
    "always",
    "never",
    "nothing",
    "everything",
    "not sure",
    "i don't know",
    "dont know",
    "idk"
}

KEYBOARD_PATTERNS = [
    r"asdfgh",
    r"asdfghjkl",
    r"qwerty",
    r"qwertyuiop",
    r"zxcvbn",
    r"zxcvbnm",
    r"dfgh",
    r"fghj",
    r"ghjk",
    r"hjkl",
    r"kjhg",
    r"lkjh",
    r"poiuy",
    r"mnbvc"
]


def classify_response(message):

    if not isinstance(message, str):
        return "unclear"

    text = re.sub(
        r"\s+",
        " ",
        message.strip().lower()
    )

    if not text:
        return "unclear"

    if text in SKIP_WORDS or text in {"-", "--", "---"}:
        return "skipped"

    if text in VALID_SHORT_ANSWERS:
        return "answered"

    if re.fullmatch(r"(.)\1{4,}", text):
        return "unclear"

    if any(
        re.search(pattern, text)
        for pattern in KEYBOARD_PATTERNS
    ):
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


# ==========================================================
# 9. CHAT MESSAGE DISPLAY
# ==========================================================

def display_message(message, sender):

    safe_message = html.escape(
        str(message)
    ).replace("\n", "<br>")

    if sender == "assistant":

        st.markdown(
            f'<div class="bot-row">'
            f'<div class="bot-bubble">{safe_message}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f'<div class="user-row">'
            f'<div class="user-bubble">{safe_message}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ==========================================================
# 10. CRISIS SAFETY SCREEN
# ==========================================================

def show_crisis_screen():

    st.error("Your safety matters.")

    st.markdown("""
    Thank you for sharing something difficult.

    I'm concerned that you may be going through something
    that needs immediate human support.

    Antara cannot assess your safety or provide emergency assistance.

    If you may hurt yourself or someone else, or are in immediate danger:

    - Contact your local emergency services.
    - In India, call 112 for emergency assistance.
    - Reach out to someone you trust who can stay with you.
    - Move away from anything you could use to hurt yourself or someone else, if possible.
    - Contact a qualified mental-health professional.

    You do not have to handle this alone.
    """)

    st.warning(
        "Your normal Antara conversation has been paused. "
        "Please seek human support."
    )

    if st.button("End this session"):

        st.session_state.submitted = True

        saved = auto_save()

        if saved:

            try:

                complete_patient_session(
                    st.session_state.patient_id,
                    st.session_state.session_id
                )

            except Exception as error:

                print("SESSION COMPLETION ERROR:", error)

        st.rerun()


# ==========================================================
# 11. LOCATION AUTOCOMPLETE
# ==========================================================

def show_location_fields():

    st.markdown("### 📍 Your Location")

    st.caption(
        "Type at least 3 letters of your locality or city "
        "to find matching Indian post offices."
    )

    search = st.text_input(
        "Search City or Locality *",
        key="location_search",
        placeholder="Example: Sarjapur"
    )

    if len(search.strip()) >= 3:

        locations = search_indian_post_offices(
            search.strip()
        )

        if locations:

            options = [
                (
                    f"{item.get('office_name', '')}, "
                    f"{item.get('district', '')}, "
                    f"{item.get('state', '')} - "
                    f"{item.get('pincode', '')}"
                )
                for item in locations
            ]

            selected_label = st.selectbox(
                "Select your locality / post office",
                options,
                key="location_selection"
            )

            selected_index = options.index(selected_label)
            selected_location = locations[selected_index]

            signature = (
                selected_location.get("office_name", ""),
                selected_location.get("district", ""),
                selected_location.get("state", ""),
                str(selected_location.get("pincode", ""))
            )

            if signature != st.session_state.location_signature:

                district_value = selected_location.get(
                    "district", ""
                )

                city_value = district_value

                if district_value.lower() == "bengaluru urban":
                    city_value = "Bengaluru"

                st.session_state.reg_locality = (
                    selected_location.get("office_name", "")
                )

                st.session_state.reg_city = city_value
                st.session_state.reg_district = district_value

                st.session_state.reg_state = (
                    selected_location.get("state", "")
                )

                st.session_state.reg_pincode = str(
                    selected_location.get("pincode", "")
                )

                st.session_state.location_signature = signature

                st.rerun()

        else:

            st.info(
                "No matching post offices found. "
                "Try another locality or PIN code."
            )

    st.markdown("### Address Details")

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Locality *",
            key="reg_locality",
            placeholder="Enter locality"
        )

        st.text_input(
            "City *",
            key="reg_city",
            placeholder="Enter city"
        )

        st.text_input(
            "District *",
            key="reg_district",
            placeholder="Enter district"
        )

    with col2:

        st.text_input(
            "State *",
            key="reg_state",
            placeholder="Enter state"
        )

        st.text_input(
            "PIN Code *",
            key="reg_pincode",
            placeholder="Enter PIN code"
        )

    st.caption(
        "You can edit these fields if the suggested address is not accurate."
    )


# ==========================================================
# 12. LOGIN AND REGISTRATION
# ==========================================================

def show_authentication_page():

    st.markdown("""
    <div class="login-card">
        <div style="font-size:55px;">🌷</div>
        <h1 style="color:#29243a;">Antara</h1>
        <p class="login-subtitle">
            A safe space to express your feelings before therapy.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    login_tab, register_tab = st.tabs([
        "Login",
        "Create Account"
    ])

    # ------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------

    with login_tab:

        st.markdown("### Welcome Back")

        with st.form("login_form"):

            email = st.text_input("Email Address")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_button:

            if not email.strip() or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                try:

                    patient = authenticate_patient(
                        email.strip().lower(),
                        password
                    )

                    if patient:

                        if isinstance(patient, dict):

                            patient_id = (
                                patient.get("patient_id")
                                or patient.get("id")
                            )

                            patient_name = (
                                patient.get("full_name")
                                or patient.get("name")
                            )

                            patient_email = (
                                patient.get("email")
                                or email.strip().lower()
                            )

                        else:

                            patient_id = patient[0]
                            patient_name = patient[1]
                            patient_email = email.strip().lower()

                        if not patient_id:

                            st.error(
                                "Your account does not have a valid patient ID. "
                                "Please contact the administrator."
                            )

                        else:

                            st.session_state.patient_id = patient_id
                            st.session_state.patient_name = patient_name
                            st.session_state.patient_email = patient_email

                            st.session_state.logged_in = True
                            st.session_state.login_role = "patient"

                            st.session_state.show_recovery = False
                            st.session_state.recovery_session_id = None

                            # CHECK FOR UNFINISHED SESSION

                            try:

                                unfinished = get_unfinished_session(
                                    patient_id
                                )

                                if isinstance(unfinished, dict):

                                    recovery_id = unfinished.get(
                                        "session_id"
                                    )

                                    if recovery_id:

                                        st.session_state.show_recovery = True

                                        st.session_state.recovery_session_id = (
                                            recovery_id
                                        )

                            except Exception as error:

                                print(
                                    "UNFINISHED SESSION LOOKUP ERROR:",
                                    error
                                )

                            st.rerun()

                    else:

                        st.error("Invalid email or password.")

                except Exception as error:

                    st.error(
                        "Unable to log in. "
                        "Please check your database connection."
                    )

                    print("LOGIN ERROR:", error)

    # ------------------------------------------------------
    # REGISTRATION
    # ------------------------------------------------------

    with register_tab:

        st.markdown("### Create Your Antara Account")

        st.caption("Fields marked with * are required.")

        st.markdown("#### Personal Information")

        full_name = st.text_input(
            "Full Name *",
            key="reg_name"
        )

        email = st.text_input(
            "Email Address *",
            key="reg_email"
        )

        phone = st.text_input(
            "Phone Number *",
            key="reg_phone"
        )

        # DATE OF BIRTH

        st.markdown("### 🎂 Date of Birth")

        dob = st.date_input(
            "Date of Birth *",
            min_value=date(1920, 1, 1),
            max_value=date.today(),
            value=date(2005, 1, 1),
            key="reg_dob"
        )

        calculated_age = calculate_age(dob)

        st.text_input(
            "Age",
            value=str(calculated_age),
            disabled=True,
            key=f"reg_age_display_{dob.isoformat()}"
        )

        # LOCATION

        show_location_fields()

        # TRUSTED CONTACT

        st.markdown("### 🩷 Trusted Emergency Contact")

        trusted_name = st.text_input(
            "Trusted Contact Name",
            key="trusted_name"
        )

        trusted_relationship = st.text_input(
            "Relationship",
            key="trusted_relationship"
        )

        trusted_phone = st.text_input(
            "Trusted Contact WhatsApp Number",
            key="trusted_phone"
        )

        emergency_consent = st.checkbox(
            "I consent to my trusted contact being contacted "
            "in an emergency, if such a feature is implemented.",
            key="emergency_consent"
        )

        trusted_agreement = st.checkbox(
            "I confirm that this trusted contact has agreed "
            "to be listed as my emergency contact.",
            key="trusted_agreement"
        )

        # ADDITIONAL INFORMATION

        st.markdown("### 🌸 Additional Information")

        pre_session_note = st.text_area(
            "Would you like to share anything before beginning?",
            key="pre_session_note"
        )

        # PASSWORD

        st.markdown("### 🔒 Account Security")

        password = st.text_input(
            "Create Password *",
            type="password",
            key="reg_password"
        )

        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            key="reg_confirm_password"
        )

        registration_consent = st.checkbox(
            "I understand how my information will be used "
            "and stored, and I voluntarily agree to continue.",
            key="registration_consent"
        )

        # REGISTER BUTTON

        if st.button(
            "Create My Account 🌷",
            use_container_width=True
        ):

            errors = []

            if not full_name.strip():
                errors.append("Please enter your full name.")

            if not email.strip():

                errors.append(
                    "Please enter your email address."
                )

            elif not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                email.strip()
            ):

                errors.append(
                    "Please enter a valid email address."
                )

            if not re.fullmatch(r"\d{10}", phone.strip()):

                errors.append(
                    "Please enter a valid 10-digit phone number."
                )

            if not st.session_state.get(
                "reg_locality", ""
            ).strip():

                errors.append("Please enter your locality.")

            if not st.session_state.get(
                "reg_city", ""
            ).strip():

                errors.append("Please enter your city.")

            if not st.session_state.get(
                "reg_district", ""
            ).strip():

                errors.append("Please enter your district.")

            if not st.session_state.get(
                "reg_state", ""
            ).strip():

                errors.append("Please enter your state.")

            if not re.fullmatch(
                r"\d{6}",
                st.session_state.get("reg_pincode", "").strip()
            ):

                errors.append(
                    "Please enter a valid 6-digit PIN code."
                )

            if len(password) < 6:

                errors.append(
                    "Password must contain at least 6 characters."
                )

            if password != confirm_password:

                errors.append("Passwords do not match.")

            if not registration_consent:

                errors.append(
                    "Please provide registration consent."
                )

            if emergency_consent:

                if not trusted_name.strip():

                    errors.append(
                        "Please enter your trusted contact's name."
                    )

                if not re.fullmatch(
                    r"\d{10}",
                    trusted_phone.strip()
                ):

                    errors.append(
                        "Please enter a valid trusted contact number."
                    )

                if not trusted_agreement:

                    errors.append(
                        "Please confirm that your trusted contact has agreed."
                    )

            if errors:

                for error in errors:
                    st.error(error)

            else:

                try:

                    result = register_patient(
                        full_name=full_name.strip(),
                        email=email.strip().lower(),
                        password=password,
                        contact_number=phone.strip(),
                        date_of_birth=dob.isoformat(),
                        age=calculated_age,
                        locality=st.session_state.get(
                            "reg_locality", ""
                        ).strip(),
                        city=st.session_state.get(
                            "reg_city", ""
                        ).strip(),
                        district=st.session_state.get(
                            "reg_district", ""
                        ).strip(),
                        state=st.session_state.get(
                            "reg_state", ""
                        ).strip(),
                        pincode=st.session_state.get(
                            "reg_pincode", ""
                        ).strip(),
                        trusted_contact_name=trusted_name.strip(),
                        trusted_contact_relationship=trusted_relationship.strip(),
                        trusted_contact_number=trusted_phone.strip(),
                        emergency_alert_consent=emergency_consent,
                        trusted_contact_agreement=trusted_agreement,
                        pre_session_note=pre_session_note.strip()
                    )

                    if result:

                        st.success(
                            "Your account has been created successfully! "
                            "Please log in."
                        )

                    else:

                        st.error(
                            "Registration failed. "
                            "This email may already be registered."
                        )

                except Exception as error:

                    st.error(
                        "Unable to create your account. "
                        "Please check your database."
                    )

                    print("REGISTRATION ERROR:", error)


# ==========================================================
# 13. SIDEBAR AND SESSION HISTORY
# ==========================================================

def show_sidebar():

    if not st.session_state.logged_in:
        return

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

                session_id = session.get("session_id")
                status = session.get("status", "unknown")

                if not session_id:
                    continue

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

                            if (
                                saved_data
                                and restore_session(saved_data)
                            ):

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
                        f"confirm_delete_{session_id}",
                        False
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

                                try:

                                    delete_patient_session(
                                        st.session_state.patient_id,
                                        session_id
                                    )

                                    if (
                                        st.session_state.session_id
                                        == session_id
                                    ):

                                        reset_session()

                                    st.session_state[
                                        f"confirm_delete_{session_id}"
                                    ] = False

                                    st.success("Session deleted.")
                                    st.rerun()

                                except Exception as error:

                                    st.error(
                                        "Unable to delete the session."
                                    )

                                    print(
                                        "SESSION DELETE ERROR:",
                                        error
                                    )

                        with cancel_col:

                            if st.button(
                                "Cancel",
                                key=f"cancel_{session_id}"
                            ):

                                st.session_state[
                                    f"confirm_delete_{session_id}"
                                ] = False

                                st.rerun()


# ==========================================================
# 14. SESSION RECOVERY
# ==========================================================

def show_recovery():

    st.markdown("""
    <div class="login-card">
        <div style="font-size:50px;">🌷</div>
        <h2 style="color:#29243a;">Welcome Back to Antara</h2>
        <p class="login-subtitle">
            We found an unfinished conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "We found an unfinished Antara session."
    )

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

            if (
                saved_data
                and restore_session(saved_data)
            ):

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


# ==========================================================
# 15. WELCOME AND CONSENT
# ==========================================================

def show_welcome():

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
    Antara is a pre-therapy intake application designed to help you express
    your feelings before meeting a qualified therapist.

    Lia will ask you a series of questions to understand your experiences.
    You can skip questions or edit your previous answers whenever you need to.
    """)

    st.markdown("### 🔒 Your information")

    st.warning("""
    This prototype stores session information in a local SQLite database.
    The database is not encrypted.

    Avoid entering real identifying or highly sensitive personal information while testing this prototype.
    """)

    st.markdown("### Important information")

    st.write("""
    - Antara does not diagnose mental-health conditions.
    - Antara does not prescribe medication or treatment.
    - Antara is not a replacement for professional therapy.
    - You can skip questions you do not wish to answer.
    - If you need immediate support, contact a qualified professional or emergency services.
    """)

    st.markdown("### Consent")

    consent = st.checkbox(
        "I understand how my conversation will be used and stored, "
        "and I voluntarily agree to continue."
    )

    if st.button(
        "Begin My Conversation 🌷",
        use_container_width=True
    ):

        if consent:

            st.session_state.started = True
            st.session_state.consent_given = True
            st.session_state.session_id = generate_session_id()

            saved = auto_save()

            if saved:
                st.rerun()

            else:

                st.session_state.started = False
                st.session_state.consent_given = False
                st.session_state.session_id = None

                st.error(
                    "Your session could not be saved. "
                    "Please try again."
                )

        else:

            st.error(
                "Please provide your consent before continuing."
            )


# ==========================================================
# 16. MAIN CHAT INTERFACE
# ==========================================================

def show_chat():

    st.title("🌷 Antara")

    st.caption(
        "A space for your feelings, before therapy."
    )

    if st.session_state.crisis_triggered:

        show_crisis_screen()
        return

    st.caption(
        f"Session ID: {st.session_state.session_id}"
    )

    current_index = st.session_state.current_question_index
    total_questions = len(all_questions)

    # ------------------------------------------------------
    # PREVIOUS CONVERSATION
    # ------------------------------------------------------

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
                response.get("edited_answer", ""),
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

    # ------------------------------------------------------
    # EDIT PREVIOUS ANSWERS
    # ------------------------------------------------------

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

                st.write(
                    response["edited_answer"]
                )

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

                                response.setdefault(
                                    "edit_history",
                                    []
                                )

                                response["edit_history"].append({
                                    "previous_answer": old_answer,
                                    "new_answer": cleaned_answer
                                })

                                response["edited_answer"] = cleaned_answer
                                response["was_edited"] = True

                                if not auto_save():

                                    st.error(
                                        "Your edit could not be saved."
                                    )

                        st.session_state[edit_key] = False
                        st.rerun()

    # ------------------------------------------------------
    # FOLLOW-UP QUESTIONS
    # ------------------------------------------------------

    if st.session_state.pending_followup is not None:

        pending = st.session_state.pending_followup

        response_index = pending["response_index"]

        display_message(
            pending["question"],
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

                status = classify_response(
                    followup_input
                )

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

                if not auto_save():

                    st.error(
                        "Your response could not be saved. "
                        "Please check your database."
                    )

                st.rerun()

        return

    # ------------------------------------------------------
    # CORE QUESTIONS
    # ------------------------------------------------------

    if current_index < total_questions:

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
            question_id,
            []
        )

        for attempt in attempts:

            display_message(
                attempt,
                "user"
            )

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

                status = classify_response(
                    user_message
                )

                attempts = st.session_state.pending_attempts.get(
                    question_id,
                    []
                )

                # UNCLEAR RESPONSE

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

                # SKIPPED RESPONSE

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

                    if not auto_save():

                        st.error(
                            "Your response could not be saved."
                        )

                    st.rerun()

                # ANSWERED RESPONSE

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

                    st.session_state.responses.append(
                        new_response
                    )

                    response_index = (
                        len(st.session_state.responses) - 1
                    )

                    st.session_state.pending_attempts.pop(
                        question_id,
                        None
                    )

                    st.session_state.unclear_message = None

                    # SAVE ANSWER BEFORE CALLING LLM

                    auto_save()

                    # GENERATE FOLLOW-UP

                    try:

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

                        if (
                            isinstance(result, dict)
                            and result.get("follow_up_needed")
                            and result.get("message")
                        ):

                            st.session_state.responses[
                                response_index
                            ]["followup_question"] = result["message"]

                            st.session_state.pending_followup = {
                                "response_index": response_index,
                                "question": result["message"]
                            }

                        else:

                            st.session_state.current_question_index += 1

                    except Exception as error:

                        print("FOLLOW-UP GENERATION ERROR:", error)

                        st.session_state.current_question_index += 1

                        st.warning(
                            "Lia couldn't generate a follow-up question. "
                            "Your answer has been saved, and you can continue."
                        )

                    auto_save()
                    st.rerun()

    # ------------------------------------------------------
    # ALL QUESTIONS COMPLETED
    # ------------------------------------------------------

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

            if auto_save():

                try:

                    complete_patient_session(
                        st.session_state.patient_id,
                        st.session_state.session_id
                    )

                except Exception as error:

                    print(
                        "SESSION COMPLETION ERROR:",
                        error
                    )

                st.rerun()

            else:

                st.session_state.submitted = False

                st.error(
                    "Unable to submit because the session "
                    "could not be saved. Please try again."
                )


# ==========================================================
# 17. FINAL THANK-YOU SCREEN
# ==========================================================

def show_thank_you():

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
        "Your session data can be imported into the "
        "Antara Clinical Intelligence Portal for review."
    )

    st.markdown(
        '<a href="http://127.0.0.1:8000/therapist" target="_blank" '
        'style="display:inline-block;padding:10px 20px;'
        'background:#6d28d9;color:white;text-decoration:none;'
        'border-radius:8px;font-weight:600;">'
        '🌸 Open Therapist Intelligence Portal</a>',
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


# ==========================================================
# 18. MAIN APPLICATION FLOW
# ==========================================================

show_sidebar()

if not st.session_state.logged_in:

    show_authentication_page()

elif st.session_state.show_recovery:

    show_recovery()

elif st.session_state.submitted:

    show_thank_you()

elif not st.session_state.started:

    show_welcome()

else:

    show_chat()