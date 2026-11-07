import streamlit as st
import re
import html
import json
import uuid
import requests

from copy import deepcopy
from datetime import datetime, date

from question_bank import (
    QUESTION_BANK,
    QUESTION_OPTIONS,
    WELLNESS_ACTIVITIES
)

from llm_service import (
    generate_followup,
    generate_followup_acknowledgement
)

from crisis_detection import detect_crisis

from database import (
    register_patient,
    authenticate_patient,
    save_patient_session,
    get_patient_session,
    get_patient_sessions,
    delete_patient_session,
    get_unfinished_session,
    complete_patient_session,
    get_patient_details,
    update_patient_details
)


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Antara",
    page_icon="🌷",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        120deg,#c9d8ff 0%,#ead5f5 50%,#ffcddd 100%
    ) !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: transparent !important;
}

.block-container {
    max-width:1100px;
    padding-top:2rem;
    padding-bottom:5rem;
}

.stApp p,.stApp li,.stApp label,
.stApp h1,.stApp h2,.stApp h3,.stApp h4 {
    color:#000;
}

header[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background:#f3cce8 !important;
}

header[data-testid="stHeader"] *,
[data-testid="stToolbar"] * {
    color:#000 !important;
    fill:#000 !important;
}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background:#b9d8ff !important;
}

section[data-testid="stSidebar"] * {
    color:#000 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background:#e8f2ff !important;
    color:#253b5c !important;
    border:1px solid #91baf0 !important;
    border-radius:14px !important;
    font-weight:600 !important;
    min-height:45px;
}

[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stNumberInput"] [data-baseweb="input"] {
    background:#E8F2FF !important;
    border:1px solid #A9C9F5 !important;
    border-radius:14px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background:#E8F2FF !important;
    color:#222 !important;
    -webkit-text-fill-color:#222 !important;
    border:none !important;
    caret-color:#3979e8 !important;
}

[data-testid="stDateInput"] input {
    background:#E8F2FF !important;
    color:#222 !important;
    border:1px solid #A9C9F5 !important;
    border-radius:14px !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background:#E8F2FF !important;
    border:1px solid #A9C9F5 !important;
    border-radius:12px !important;
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
    background:#b9d8ff !important;
    color:#253b5c !important;
    border:1px solid #91baf0 !important;
    border-radius:14px !important;
    font-weight:600 !important;
    padding:12px 18px !important;
    box-shadow:none !important;
}

.stButton > button:hover {
    background:#9fc8ff !important;
}

.login-card {
    background:rgba(255,255,255,.90);
    padding:35px;
    border-radius:24px;
    text-align:center;
    box-shadow:0 5px 20px rgba(0,0,0,.06);
    margin-top:25px;
    border:1px solid #d8c9ed;
}

.login-subtitle {
    color:#55516a !important;
    font-size:16px;
}

[data-testid="stForm"] {
    background:rgba(255,255,255,.35) !important;
    border:1px solid rgba(255,255,255,.65) !important;
    border-radius:18px !important;
    padding:18px !important;
}

.bot-row {
    display:flex;
    justify-content:flex-start;
    margin:18px 0;
}

.bot-bubble {
    background:#eeeaf1;
    color:#292633;
    padding:13px 17px;
    border-radius:16px 16px 16px 5px;
    max-width:75%;
    font-size:15px;
    line-height:1.6;
    overflow-wrap:anywhere;
}

.user-row {
    display:flex;
    justify-content:flex-end;
    margin:18px 0;
}

.user-bubble {
    background:#3979e8;
    color:#fff;
    padding:13px 17px;
    border-radius:16px 16px 5px 16px;
    max-width:75%;
    font-size:15px;
    line-height:1.6;
    overflow-wrap:anywhere;
}

[data-testid="stProgress"] {
    background:transparent !important;
}

[data-testid="stProgress"] > div {
    background:#E8F2FF !important;
    border-radius:20px !important;
    height:10px !important;
    overflow:hidden !important;
}

[data-testid="stProgress"] div[role="progressbar"] {
    background:#3979e8 !important;
    border-radius:20px !important;
}

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottomBlockContainer"] {
    background:#b9d8ff !important;
}

[data-testid="stBottom"] {
    border-top:1px solid #91baf0 !important;
}

[data-testid="stChatInput"] {
    background:#E8F2FF !important;
    border:2px solid #91baf0 !important;
    border-radius:25px !important;
    overflow:hidden !important;
}

[data-testid="stChatInput"] textarea {
    background:#E8F2FF !important;
    color:#222 !important;
}

.quick-heading {
    color:#57455f;
    font-size:14px;
    font-weight:600;
    margin-top:15px;
    margin-bottom:8px;
}

#MainMenu,footer {
    visibility:hidden;
}

@media(max-width:768px) {
    .block-container {
        padding-left:1rem;
        padding-right:1rem;
    }

    .login-card {
        padding:22px;
    }

    .bot-bubble,.user-bubble {
        max-width:90%;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# 2. CONSTANTS
# ==========================================================

TIME_OPTIONS = [
    "5 minutes",
    "10 minutes",
    "15 minutes",
    "20 minutes",
    "I have plenty of time"
]

TIME_LIMITS = {
    "5 minutes": 5,
    "10 minutes": 8,
    "15 minutes": 11,
    "20 minutes": 14,
    "I have plenty of time": 100
}

CONVERSATION_MODES = {
    "Quick check-in": 5,
    "Regular conversation": 9,
    "Detailed conversation": 16,
    "I want to talk freely": 100
}

EMOTION_OPTIONS = QUESTION_BANK["emotional_checkin"]["options"]

BRANCH_MAP = {
    "stressed": "stress",
    "stress": "stress",
    "anxious": "stress",
    "worried": "stress",
    "overwhelmed": "stress",
    "angry": "stress",
    "frustrated": "stress",
    "sad": "sadness",
    "low": "sadness",
    "lonely": "loneliness",
    "disconnected": "loneliness",
    "exhausted": "physical_health",
    "tired": "physical_health",
    "sleep": "physical_health",
    "pain": "physical_health",
    "physical": "physical_health"
}

BRANCH_ORDER = [
    "stress",
    "sadness",
    "loneliness",
    "physical_health"
]


# ==========================================================
# 3. SESSION DEFAULTS
# ==========================================================

DEFAULTS = {
    "logged_in": False,
    "login_role": None,
    "patient_id": None,
    "patient_name": None,
    "patient_email": None,

    "show_dashboard": True,

    "started": False,
    "consent_given": False,
    "session_id": None,
    "submitted": False,

    "conversation_step": "introduction",
    "time_available": None,
    "conversation_mode": "Regular conversation",

    "emotional_theme": [],
    "selected_questions": [],
    "current_question_index": 0,
    "responses": [],

    "pending_followup": None,
    "unclear_message": None,

    "activity_suggested": False,
    "activity_data": None,
    "activity_answered": False,

    "crisis_triggered": False,

    "show_recovery": False,
    "recovery_session_id": None,

    "location_signature": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = deepcopy(value)


def format_session_date(value):

    if not value:
        return "Date unavailable"

    try:
        dt = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        return dt.strftime("%d %b %Y, %I:%M %p")

    except (ValueError, TypeError):
        return str(value)


# ==========================================================
# 4. GENERAL HELPERS
# ==========================================================

def generate_session_id():

    return (
        "ANT-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )


def calculate_age(dob):

    if not dob:
        return ""

    today = date.today()

    return (
        today.year - dob.year
        - ((today.month, today.day) < (dob.month, dob.day))
    )


def display_message(message, sender="assistant"):

    safe = html.escape(str(message)).replace("\n", "<br>")

    if sender == "assistant":

        st.markdown(
            f'<div class="bot-row">'
            f'<div class="bot-bubble">{safe}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f'<div class="user-row">'
            f'<div class="user-bubble">{safe}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ==========================================================
# 5. SESSION STORAGE
# ==========================================================

def get_session_data():

    keys = [
        "started",
        "consent_given",
        "submitted",
        "conversation_step",
        "paused_from_step",
        "time_available",
        "conversation_mode",
        "emotional_theme",
        "selected_questions",
        "current_question_index",
        "responses",
        "pending_followup",
        "unclear_message",
        "activity_suggested",
        "activity_data",
        "activity_answered",
        "crisis_triggered"
    ]

    data = {
        key: st.session_state.get(key)
        for key in keys
    }

    data.update({
        "application": "Antara",
        "session_id": st.session_state.session_id,
        "saved_at": datetime.now().isoformat()
    })

    return data


def auto_save():

    patient_id = st.session_state.get("patient_id")
    session_id = st.session_state.get("session_id")

    if not patient_id or not session_id:
        return False

    try:

        status = (
            "completed"
            if st.session_state.submitted
            else "in_progress"
        )

        result = save_patient_session(
            patient_id,
            session_id,
            get_session_data(),
            status
        )

        return result is True

    except Exception as error:

        print("AUTO SAVE ERROR:", error)

        return False


def restore_session(saved_data):

    try:

        if not isinstance(saved_data, dict):
            return False

        if isinstance(saved_data.get("session_data"), dict):
            saved_data = saved_data["session_data"]

        if not saved_data.get("session_id"):
            return False

        st.session_state.session_id = saved_data["session_id"]

        keys = [
            "started",
            "consent_given",
            "submitted",
            "conversation_step",
            "time_available",
            "conversation_mode",
            "emotional_theme",
            "selected_questions",
            "current_question_index",
            "responses",
            "pending_followup",
            "unclear_message",
            "activity_suggested",
            "activity_data",
            "activity_answered",
            "crisis_triggered"
        ]

        for key in keys:

            if key in saved_data:
                st.session_state[key] = saved_data[key]

        if not isinstance(st.session_state.responses, list):
            st.session_state.responses = []

        if not isinstance(st.session_state.selected_questions, list):
            st.session_state.selected_questions = []

        st.session_state.current_question_index = max(
            0,
            min(
                int(st.session_state.current_question_index or 0),
                len(st.session_state.selected_questions)
            )
        )

        st.session_state.started = True
        st.session_state.show_recovery = False
        st.session_state.show_dashboard = False

        return True

    except Exception as error:

        print("RESTORE ERROR:", error)

        return False


def get_history():

    patient_id = st.session_state.get("patient_id")

    if not patient_id:
        return []

    try:

        history = get_patient_sessions(patient_id)

        return history if isinstance(history, list) else []

    except Exception as error:

        print("SESSION HISTORY ERROR:", error)

        return []


def reset_session():

    patient_id = st.session_state.patient_id
    patient_name = st.session_state.patient_name
    patient_email = st.session_state.patient_email

    for key, value in DEFAULTS.items():
        st.session_state[key] = deepcopy(value)

    st.session_state.logged_in = True
    st.session_state.login_role = "patient"

    st.session_state.patient_id = patient_id
    st.session_state.patient_name = patient_name
    st.session_state.patient_email = patient_email


def start_new_session():

    reset_session()


def logout():

    if (
        st.session_state.started
        and not st.session_state.submitted
        and st.session_state.session_id
    ):

        if not auto_save():

            st.error(
                "Your session could not be saved. Please try again."
            )

            return

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()
# ==========================================================
# 6. LOCATION LOOKUP
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

    except Exception as error:

        print("LOCATION ERROR:", error)
        return []


def show_location_fields():

    st.markdown("### 📍 Your Location")

    st.caption(
        "Type at least 3 letters of your locality or city."
    )

    search = st.text_input(
        "Search City or Locality *",
        key="location_search"
    )

    if len(search.strip()) >= 3:

        locations = search_indian_post_offices(
            search.strip()
        )

        if locations:

            labels = [
                f"{x.get('office_name','')}, "
                f"{x.get('district','')}, "
                f"{x.get('state','')} - "
                f"{x.get('pincode','')}"
                for x in locations
            ]

            label = st.selectbox(
                "Select your locality",
                labels,
                key="location_selection"
            )

            selected = locations[labels.index(label)]

            signature = (
                selected.get("office_name", ""),
                selected.get("district", ""),
                selected.get("state", ""),
                str(selected.get("pincode", ""))
            )

            if signature != st.session_state.location_signature:

                district = selected.get("district", "")

                st.session_state.reg_locality = selected.get(
                    "office_name", ""
                )

                st.session_state.reg_city = (
                    "Bengaluru"
                    if district.lower() == "bengaluru urban"
                    else district
                )

                st.session_state.reg_district = district

                st.session_state.reg_state = selected.get(
                    "state", ""
                )

                st.session_state.reg_pincode = str(
                    selected.get("pincode", "")
                )

                st.session_state.location_signature = signature

                st.rerun()

        else:

            st.info(
                "No matching locations found. "
                "You can enter your location manually below."
            )

    c1, c2 = st.columns(2)

    with c1:

        st.text_input(
            "Locality *",
            key="reg_locality"
        )

        st.text_input(
            "City *",
            key="reg_city"
        )

        st.text_input(
            "District *",
            key="reg_district"
        )

    with c2:

        st.text_input(
            "State *",
            key="reg_state"
        )

        st.text_input(
            "PIN Code *",
            key="reg_pincode"
        )


# ==========================================================
# 7. LOGIN AND REGISTRATION
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

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

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
                    "Enter your email and password."
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

                            patient_email = patient.get(
                                "email",
                                email.strip().lower()
                            )

                        else:

                            patient_id, patient_name = (
                                patient[0],
                                patient[1]
                            )

                            patient_email = email.strip().lower()

                        if not patient_id:

                            st.error(
                                "Patient ID is missing."
                            )

                        else:

                            st.session_state.patient_id = patient_id

                            st.session_state.patient_name = (
                                patient_name
                            )

                            st.session_state.patient_email = (
                                patient_email
                            )

                            st.session_state.logged_in = True
                            st.session_state.login_role = "patient"
                            st.session_state.show_dashboard = True

                            unfinished = get_unfinished_session(
                                patient_id
                            )

                            if (
                                isinstance(unfinished, dict)
                                and unfinished.get("session_id")
                            ):

                                st.session_state.show_recovery = True

                                st.session_state.recovery_session_id = (
                                    unfinished["session_id"]
                                )

                            else:

                                st.session_state.show_recovery = False

                            st.rerun()

                    else:

                        st.error(
                            "Invalid email or password."
                        )

                except Exception as error:

                    st.error(
                        "Unable to log in."
                    )

                    print("LOGIN ERROR:", error)

    # ------------------------------------------------------
    # REGISTRATION
    # ------------------------------------------------------

    with register_tab:

        st.markdown("### Create Your Antara Account")

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

        dob = st.date_input(
            "Date of Birth *",
            min_value=date(1920, 1, 1),
            max_value=date.today(),
            value=date(2005, 1, 1),
            key="reg_dob"
        )

        st.text_input(
            "Age",
            value=str(calculate_age(dob)),
            disabled=True
        )

        show_location_fields()

        st.markdown(
            "### 🩷 Trusted Emergency Contact"
        )

        trusted_name = st.text_input(
            "Trusted Contact Name",
            key="trusted_name"
        )

        trusted_relationship = st.text_input(
            "Relationship",
            key="trusted_relationship"
        )

        trusted_phone = st.text_input(
            "Trusted Contact Phone Number",
            key="trusted_phone"
        )

        emergency_consent = st.checkbox(
            "I consent to my trusted contact being contacted "
            "in an emergency, if this feature is implemented."
        )

        trusted_agreement = st.checkbox(
            "I confirm that this person has agreed to be listed "
            "as my trusted contact."
        )

        pre_session_note = st.text_area(
            "Anything you would like to share before beginning?"
        )

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
            "I understand how my information will be stored "
            "and voluntarily agree to continue."
        )

        if st.button(
            "Create My Account 🌷",
            use_container_width=True
        ):

            errors = []

            if not full_name.strip():
                errors.append("Enter your full name.")

            if not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                email.strip()
            ):

                errors.append(
                    "Enter a valid email address."
                )

            if not re.fullmatch(
                r"\d{10}",
                phone.strip()
            ):

                errors.append(
                    "Enter a valid 10-digit phone number."
                )

            for field, label in [
                ("reg_locality", "Locality"),
                ("reg_city", "City"),
                ("reg_district", "District"),
                ("reg_state", "State")
            ]:

                if not st.session_state.get(
                    field, ""
                ).strip():

                    errors.append(
                        f"Enter your {label.lower()}."
                    )

            if not re.fullmatch(
                r"\d{6}",
                st.session_state.get(
                    "reg_pincode", ""
                ).strip()
            ):

                errors.append(
                    "Enter a valid 6-digit PIN code."
                )

            if len(password) < 6:

                errors.append(
                    "Password must have at least 6 characters."
                )

            if password != confirm_password:

                errors.append(
                    "Passwords do not match."
                )

            if not registration_consent:

                errors.append(
                    "Please provide registration consent."
                )

            if emergency_consent:

                if not trusted_name.strip():

                    errors.append(
                        "Enter your trusted contact's name."
                    )

                if not re.fullmatch(
                    r"\d{10}",
                    trusted_phone.strip()
                ):

                    errors.append(
                        "Enter a valid trusted contact number."
                    )

                if not trusted_agreement:

                    errors.append(
                        "Confirm your trusted contact's agreement."
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
                        age=calculate_age(dob),
                        locality=st.session_state.reg_locality.strip(),
                        city=st.session_state.reg_city.strip(),
                        district=st.session_state.reg_district.strip(),
                        state=st.session_state.reg_state.strip(),
                        pincode=st.session_state.reg_pincode.strip(),
                        trusted_contact_name=trusted_name.strip(),
                        trusted_contact_relationship=trusted_relationship.strip(),
                        trusted_contact_number=trusted_phone.strip(),
                        emergency_alert_consent=emergency_consent,
                        trusted_contact_agreement=trusted_agreement,
                        pre_session_note=pre_session_note.strip()
                    )

                    if result:

                        st.success(
                            "Account created successfully! "
                            "Please log in."
                        )

                    else:

                        st.error(
                            "Registration failed. This email may "
                            "already be registered."
                        )

                except Exception as error:

                    st.error(
                        "Unable to create your account."
                    )

                    print("REGISTRATION ERROR:", error)


# ==========================================================
# 8. IMPROVED SIDEBAR
# ==========================================================

def show_sidebar():

    if not st.session_state.logged_in:
        return

    st.markdown("""
    <style>

    [data-testid="stSidebar"] {
        background: #b9d8ff !important;
    }

    .sidebar-profile {
        background: rgba(255,255,255,0.65);
        padding: 20px;
        border-radius: 18px;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.8);
    }

    .sidebar-logo {
        font-size: 32px;
        text-align: center;
    }

    .sidebar-title {
        text-align: center;
        font-size: 23px;
        font-weight: 700;
        color: #344c78;
    }

    .sidebar-email {
        color: #55516a;
        font-size: 13px;
        overflow-wrap: anywhere;
    }

    .sidebar-heading {
        font-size: 17px;
        font-weight: 700;
        color: #344c78;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        st.markdown("""
        <div class="sidebar-profile">
            <div class="sidebar-logo">🌷</div>
            <div class="sidebar-title">Antara</div>
            <p style="text-align:center;color:#625c73;">
                Your Personal Wellness Space
            </p>
        </div>
        """, unsafe_allow_html=True)

        first_name = (
            st.session_state.patient_name or "Patient"
        )

        st.markdown(
            f"### Welcome, {html.escape(first_name.split()[0])}!"
        )

        st.markdown(
            f'<div class="sidebar-email">'
            f'{html.escape(str(st.session_state.patient_email or ""))}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "🚪 Logout",
            key="sidebar_logout",
            use_container_width=True
        ):

            logout()

        st.divider()

        st.markdown(
            '<div class="sidebar-heading">'
            '📂 Your Session History'
            '</div>',
            unsafe_allow_html=True
        )

        history = get_history()

        if not history:

            st.caption(
                "Your conversations will appear here."
            )

        else:

            for index, item in enumerate(history):

                sid = item.get("session_id")

                if not sid:
                    continue

                status = item.get(
                    "status", "unknown"
                )

                if status == "completed":
                    icon = "🌸"
                elif status == "in_progress":
                    icon = "💬"
                else:
                    icon = "📋"

                with st.expander(
                    f"{icon} Session {index + 1}"
                ):

                    st.caption(f"ID: {sid}")

                    st.caption(
                        f"Status: {status.replace('_', ' ').title()}"
                    )

                    session_date = format_session_date(
                        item.get("updated_at")
                        or item.get("created_at")
                    )

                    st.caption(
                        f"Last activity: {session_date}"
                    )

                    if status == "in_progress":

                        if st.button(
                            "▶️ Resume",
                            key=f"sidebar_resume_{sid}",
                            use_container_width=True
                        ):

                            saved = get_patient_session(
                                st.session_state.patient_id,
                                sid
                            )

                            if saved and restore_session(saved):
                                st.rerun()
                            else:
                                st.error(
                                    "Unable to restore this session."
                                )

                    if st.button(
                        "🗑️ Delete Session",
                        key=f"sidebar_delete_{sid}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"show_confirm_delete_{sid}"
                        ] = True

                    if st.session_state.get(
                        f"show_confirm_delete_{sid}",
                        False
                    ):

                        st.warning(
                            "Are you sure you want to delete this session?"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "Yes",
                                key=f"yes_delete_{sid}"
                            ):

                                try:

                                    deleted = delete_patient_session(
                                        st.session_state.patient_id,
                                        sid
                                    )

                                    if deleted:

                                        st.session_state[
                                            f"show_confirm_delete_{sid}"
                                        ] = False

                                        st.success(
                                            "Session deleted."
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            "Unable to delete this session."
                                        )

                                except Exception as error:

                                    st.error(
                                        "Unable to delete session."
                                    )

                                    print(error)

                        with col2:

                            if st.button(
                                "No",
                                key=f"no_delete_{sid}"
                            ):

                                st.session_state[
                                    f"show_confirm_delete_{sid}"
                                ] = False

                                st.rerun()

        st.divider()

        st.caption(
            "🌷 Antara | Your feelings matter."
        )


# ==========================================================
# 9. SESSION RECOVERY
# ==========================================================

def show_recovery():

    st.markdown("""
    <div class="login-card">
        <div style="font-size:50px;">🌷</div>
        <h2 style="color:#29243a;">
            Welcome Back to Antara
        </h2>
        <p class="login-subtitle">
            We saved your unfinished conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        f"Session: {st.session_state.recovery_session_id}"
    )

    st.write(
        "Would you like to continue where you left off?"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Resume Conversation",
            use_container_width=True
        ):

            saved = get_patient_session(
                st.session_state.patient_id,
                st.session_state.recovery_session_id
            )

            if saved and restore_session(saved):
                st.rerun()
            else:
                st.error("Unable to restore session.")

    with c2:

        if st.button(
            "Start New Conversation",
            use_container_width=True
        ):

            st.session_state.show_recovery = False

            start_new_session()

            st.session_state.show_dashboard = False

            st.rerun()


# ==========================================================
# 10. WELCOME AND CONSENT
# ==========================================================

def show_welcome():

    st.markdown("""
    <div class="login-card">
        <div style="font-size:55px;">🌷</div>
        <h2 style="color:#29243a;">Welcome to Antara</h2>
        <p class="login-subtitle">
            A space where your feelings matter.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### A little about Antara")

    st.write("""
    Antara is a pre-therapy intake application designed to help
    you express your feelings before meeting a qualified therapist.

    Lia will guide you through a conversation based on your responses.
    You can skip questions or pause whenever you need.
    """)

    st.warning("""
    This prototype stores information in a local SQLite database,
    which is not encrypted. Avoid entering real identifying or highly
    sensitive personal information while testing.

    Antara does not diagnose conditions or replace professional care.
    """)

    consent = st.checkbox(
        "I understand how my conversation will be used and stored, "
        "and I voluntarily agree to continue.",
        key="welcome_consent"
    )

    if st.button(
        "Begin My Conversation 🌷",
        use_container_width=True
    ):

        if not consent:

            st.error("Please provide your consent.")

        else:

            st.session_state.session_id = generate_session_id()

            st.session_state.started = True
            st.session_state.consent_given = True
            st.session_state.submitted = False

            st.session_state.show_dashboard = False

            st.session_state.conversation_step = "introduction"

            st.session_state.responses = []
            st.session_state.selected_questions = []
            st.session_state.current_question_index = 0

            st.session_state.pending_followup = None
            st.session_state.emotional_theme = []

            st.session_state.activity_data = None
            st.session_state.activity_answered = False

            st.session_state.crisis_triggered = False

            if auto_save():

                st.success("Your session has started!")
                st.rerun()

            else:

                st.session_state.started = False
                st.session_state.consent_given = False
                st.session_state.session_id = None

                st.error(
                    "Unable to create your session. "
                    "Please check your database and terminal."
                )


# ==========================================================
# 11. ADAPTIVE QUESTION FLOW
# ==========================================================

def build_question_flow():

    selected = []

    themes = st.session_state.emotional_theme or []

    theme_text = " ".join(
        str(x).lower() for x in themes
    )

    branches = []

    for branch in BRANCH_ORDER:

        if any(
            keyword in theme_text
            for keyword, mapped in BRANCH_MAP.items()
            if mapped == branch
        ):

            branches.append(branch)

    def add_questions(category, limit=None):

        category_data = QUESTION_BANK.get(category, {})

        for item in category_data.get(
            "questions", []
        )[:limit]:

            selected.append({
                "category": category,
                "id": item["id"],
                "text": item["question"]
            })

    add_questions("general", 2)

    for branch in branches:

        add_questions(
            branch,
            3 if branch != "physical_health" else 2
        )

    add_questions("daily_routine", 2)

    relationship_terms = [
        "relationship",
        "family",
        "partner",
        "friend",
        "people",
        "conflict"
    ]

    if any(
        term in theme_text
        for term in relationship_terms
    ):

        add_questions("relationships", 2)

    add_questions("therapy_goals", 2)
    add_questions("closing", 1)

    unique = []
    seen = set()

    for question in selected:

        if question["id"] not in seen:

            unique.append(question)
            seen.add(question["id"])

    mode_limit = CONVERSATION_MODES.get(
        st.session_state.conversation_mode,
        9
    )

    time_limit = TIME_LIMITS.get(
        st.session_state.time_available,
        100
    )

    limit = min(mode_limit, time_limit)

    closing = [
        q for q in unique
        if q["category"] == "closing"
    ]

    others = [
        q for q in unique
        if q["category"] != "closing"
    ]

    flow = (
        others[:max(0, limit - len(closing))]
        + closing
    )

    st.session_state.selected_questions = flow

    st.session_state.current_question_index = 0
# ==========================================================
# 12. WELLNESS ACTIVITIES
# ==========================================================

def get_activity_for_theme(theme):

    if isinstance(theme, list):
        theme = " ".join(theme)

    theme = str(theme).lower()

    if any(x in theme for x in [
        "anxious", "worried", "stress", "overwhelmed"
    ]):
        return "grounding"

    if any(x in theme for x in ["sad", "low"]):
        return "journaling"

    if any(x in theme for x in [
        "lonely", "disconnected"
    ]):
        return "social_connection"

    if any(x in theme for x in [
        "tired", "exhausted"
    ]):
        return "nature"

    return "visualization"


def show_wellness_activity():

    st.markdown("### 🌷 A Little Moment for Yourself")

    st.write(
        "Would you like to try a small activity, "
        "or would you prefer to finish our conversation?"
    )

    if not st.session_state.activity_data:

        key = get_activity_for_theme(
            st.session_state.emotional_theme
        )

        activity = (
            WELLNESS_ACTIVITIES.get(key)
            or WELLNESS_ACTIVITIES.get("visualization")
        )

        if not activity:

            st.warning(
                "No activity is configured. "
                "You can continue to the closing screen."
            )

            if st.button("Continue"):

                st.session_state.conversation_step = "closing"

                auto_save()
                st.rerun()

            return

        st.session_state.activity_data = {
            "key": key,
            **activity
        }

    activity = st.session_state.activity_data

    st.markdown(
        f"#### {activity.get('title', 'A moment for yourself')}"
    )

    st.write(
        activity.get(
            "description",
            "Take a quiet moment for yourself."
        )
    )

    st.caption(
        f"Suggested duration: "
        f"{activity.get('duration', 'A few minutes')}"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "I'll try this 💗",
            use_container_width=True
        ):

            st.session_state.activity_answered = True

            st.session_state.responses.append({
                "question_id": "WELLNESS_ACTIVITY",
                "question": activity.get(
                    "title",
                    "Wellness activity"
                ),
                "original_answer": "Accepted",
                "edited_answer": "Accepted",
                "status": "wellness_activity"
            })

            st.session_state.conversation_step = "closing"

            if auto_save():
                st.rerun()
            else:
                st.error("Unable to save your selection.")

    with c2:

        if st.button(
            "Skip for now",
            use_container_width=True
        ):

            st.session_state.activity_answered = True

            st.session_state.conversation_step = "closing"

            if auto_save():
                st.rerun()
            else:
                st.error("Unable to save your selection.")


# ==========================================================
# 13. CRISIS SUPPORT
# ==========================================================

def show_crisis_screen():

    st.error("Your safety matters. ❤️")

    st.markdown("""
    If you are in immediate danger, please move to a safer
    place if possible and seek support from someone you trust.

    You do not need to complete this questionnaire right now.
    """)

    st.markdown("### 📞 Emergency Support")

    st.markdown("**India Emergency Number: 112**")

    st.markdown(
        '<a href="tel:112" style="display:inline-block;'
        'padding:12px 22px;background:#b9d8ff;'
        'color:#253b5c;border-radius:12px;'
        'text-decoration:none;font-weight:600;">'
        '📞 Call Emergency Services (112)</a>',
        unsafe_allow_html=True
    )

    st.divider()

    try:

        patient = get_patient_details(
            st.session_state.patient_id
        )

    except Exception as error:

        print("PATIENT DETAILS ERROR:", error)
        patient = None

    if patient:

        name = patient.get("trusted_contact_name") or ""

        relationship = patient.get(
            "trusted_contact_relationship"
        ) or ""

        number = patient.get(
            "trusted_contact_number"
        ) or ""

        consent = bool(
            patient.get("emergency_alert_consent")
        )

        agreement = bool(
            patient.get("trusted_contact_agreement")
        )

        if number and consent and agreement:

            st.markdown("### 🩷 Your Trusted Contact")

            st.write(f"**Name:** {name}")
            st.write(f"**Relationship:** {relationship}")
            st.write(f"**Phone:** {number}")

            phone_link = re.sub(
                r"[^0-9+]",
                "",
                number
            )

            st.markdown(
                f'<a href="tel:{html.escape(phone_link, quote=True)}" '
                'style="display:inline-block;'
                'padding:12px 22px;'
                'background:#b9d8ff;'
                'color:#253b5c;'
                'border-radius:12px;'
                'text-decoration:none;'
                'font-weight:600;">'
                '📞 Call Trusted Contact</a>',
                unsafe_allow_html=True
            )

        else:

            st.info(
                "No trusted contact is available for emergency "
                "contact under your current consent settings."
            )

    else:

        st.warning(
            "We couldn't retrieve your saved contact information."
        )

    st.warning(
        "Your normal conversation has been paused. "
        "Please seek immediate human support if you are unsafe."
    )

    if st.button("End This Session"):

        session_id = st.session_state.session_id
        patient_id = st.session_state.patient_id

        try:

            st.session_state.submitted = True

            if auto_save():

                complete_patient_session(
                    patient_id,
                    session_id
                )

                st.rerun()

            else:

                st.session_state.submitted = False

                st.error(
                    "Unable to save your session. Please try again."
                )

        except Exception as error:

            st.session_state.submitted = False

            st.error(
                "Unable to complete your session."
            )

            print("CRISIS COMPLETION ERROR:", error)


# ==========================================================
# 14. INTRODUCTION AND TIME SELECTION
# ==========================================================

def show_introduction():

    display_message(
        QUESTION_BANK["introduction"]["message"],
        "assistant"
    )

    st.write(
        "There's no pressure to share everything. "
        "We can go at your pace. 💗"
    )

    if st.button(
        "Continue",
        use_container_width=True
    ):

        st.session_state.conversation_step = "time"

        if auto_save():
            st.rerun()
        else:
            st.error("Unable to save your progress.")


def show_time_selection():

    display_message(
        "Before we begin, how much time would you like "
        "to spend with me today?",
        "assistant"
    )

    time_choice = st.radio(
        "Available time",
        TIME_OPTIONS,
        key="time_choice"
    )

    mode_choice = st.radio(
        "How would you like our conversation to be?",
        list(CONVERSATION_MODES.keys()),
        index=1,
        key="mode_choice"
    )

    if st.button(
        "Continue",
        use_container_width=True
    ):

        st.session_state.time_available = time_choice

        st.session_state.conversation_mode = mode_choice

        st.session_state.conversation_step = "emotion"

        if auto_save():
            st.rerun()
        else:
            st.error("Unable to save your progress.")


# ==========================================================
# 15. EMOTIONAL CHECK-IN
# ==========================================================

def show_emotional_checkin():

    display_message(
        "Let's start with you. How have you been feeling lately? "
        "You can choose more than one. 💗",
        "assistant"
    )

    st.caption(
        "It's completely okay if you're experiencing several feelings."
    )

    emotions = st.multiselect(
        "Choose all the feelings that describe you:",
        EMOTION_OPTIONS,
        key="emotion_choice",
        placeholder="Select your feelings..."
    )

    extra = st.text_input(
        "Something else? (Optional)",
        key="additional_feeling"
    )

    if st.button(
        "Continue",
        use_container_width=True
    ):

        chosen = list(emotions)

        if extra.strip():
            chosen.append(extra.strip())

        if not chosen:

            st.warning(
                "Choose at least one feeling, or select "
                "'I don't really know how I feel'."
            )

            return

        st.session_state.emotional_theme = chosen

        st.session_state.responses.append({
            "question_id": "EMOTION_01",
            "question": QUESTION_BANK[
                "emotional_checkin"
            ]["question"],
            "original_answer": chosen,
            "edited_answer": chosen,
            "status": "answered"
        })

        build_question_flow()

        st.session_state.conversation_step = "questions"

        if auto_save():
            st.rerun()
        else:
            st.error("Unable to save your emotional check-in.")


# ==========================================================
# 16. LIA'S CONVERSATION MEMORY
# ==========================================================

def get_quick_options(question):

    return QUESTION_OPTIONS.get(
        question.get("id"),
        []
    )


def get_llm_history():

    history = []

    for response in st.session_state.responses:

        if response.get("question_id") == "EMOTION_01":

            answer = response.get(
                "edited_answer", []
            )

            if isinstance(answer, list):

                answer = ", ".join(
                    map(str, answer)
                )

            history.append({
                "role": "user",
                "content": (
                    "Initial emotional check-in: "
                    + str(answer)
                )
            })

            continue

        if response.get("status") != "answered":
            continue

        question = response.get("question", "")

        answer = response.get("edited_answer", "")

        if isinstance(answer, list):

            answer = ", ".join(
                map(str, answer)
            )

        history.append({
            "role": "user",
            "content": (
                f"Question: {question}\nAnswer: {answer}"
            )
        })

        acknowledgement = response.get(
            "lia_acknowledgement"
        )

        if acknowledgement:

            history.append({
                "role": "assistant",
                "content": acknowledgement
            })

        followup_question = response.get(
            "followup_question"
        )

        followup_answer = response.get(
            "followup_answer"
        )

        if followup_question:

            history.append({
                "role": "assistant",
                "content": followup_question
            })

        if followup_answer:

            history.append({
                "role": "user",
                "content": (
                    "Follow-up answer: "
                    + str(followup_answer)
                )
            })

        followup_ack = response.get(
            "followup_acknowledgement"
        )

        if followup_ack:

            history.append({
                "role": "assistant",
                "content": followup_ack
            })

    return history[-16:]


# ==========================================================
# 17. SAVE ANSWER AND GENERATE LIA'S RESPONSE
# ==========================================================

def save_question_answer(question, answer):

    # Crisis detection is independent of the LLM.

    if detect_crisis(answer):

        st.session_state.crisis_triggered = True

        auto_save()
        st.rerun()

        return

    prior_history = get_llm_history()

    response_data = {
        "question_id": question["id"],
        "category": question["category"],
        "question": question["text"],
        "original_answer": answer,
        "edited_answer": answer,
        "status": "answered",
        "lia_acknowledgement": "",
        "followup_question": None,
        "followup_answer": None,
        "followup_skipped": False,
        "was_edited": False
    }

    st.session_state.responses.append(response_data)

    response_index = (
        len(st.session_state.responses) - 1
    )

    if not auto_save():

        st.error(
            "Your answer could not be saved. Please try again."
        )

        st.session_state.responses.pop()

        return

    answer_text = (
        ", ".join(map(str, answer))
        if isinstance(answer, list)
        else str(answer)
    )

    try:

        with st.spinner("Lia is thinking..."):

            result = generate_followup(
                question["text"],
                answer_text,
                prior_history
            )

        if not isinstance(result, dict):
            result = {}

        acknowledgement = (
            result.get("acknowledgement")
            or result.get("message")
            or ""
        )

        followup = result.get(
            "follow_up_question"
        )

        st.session_state.responses[
            response_index
        ]["lia_acknowledgement"] = str(
            acknowledgement
        ).strip()

        if (
            result.get("follow_up_needed")
            and isinstance(followup, str)
            and followup.strip()
        ):

            st.session_state.responses[
                response_index
            ]["followup_question"] = followup.strip()

            st.session_state.pending_followup = {
                "response_index": response_index,
                "question": followup.strip()
            }

        else:

            st.session_state.current_question_index += 1

    except Exception as error:

        print("LLM ERROR:", error)

        st.session_state.responses[
            response_index
        ]["lia_acknowledgement"] = (
            "Thank you for sharing that with me. 💗"
        )

        st.session_state.current_question_index += 1

    if not auto_save():

        st.error(
            "Your response could not be saved. "
            "Please try again."
        )

        return

    st.rerun()


# ==========================================================
# 18. DISPLAY PREVIOUS CONVERSATION
# ==========================================================

def show_previous_conversation():

    for response in st.session_state.responses:

        if response.get("question_id") == "EMOTION_01":
            continue

        if response.get("status") == "wellness_activity":
            continue

        if response.get("status") == "skipped":

            display_message(
                response.get("question", ""),
                "assistant"
            )

            display_message(
                "Skipped",
                "user"
            )

            continue

        if response.get("status") != "answered":
            continue

        display_message(
            response.get("question", ""),
            "assistant"
        )

        answer = response.get("edited_answer", "")

        if isinstance(answer, list):
            answer = ", ".join(map(str, answer))

        display_message(answer, "user")

        acknowledgement = response.get(
            "lia_acknowledgement"
        )

        if acknowledgement:

            display_message(
                acknowledgement,
                "assistant"
            )

        followup_question = response.get(
            "followup_question"
        )

        if followup_question:

            display_message(
                followup_question,
                "assistant"
            )

        followup_answer = response.get(
            "followup_answer"
        )

        if followup_answer:

            display_message(
                followup_answer,
                "user"
            )

        followup_acknowledgement = response.get(
            "followup_acknowledgement"
        )

        if followup_acknowledgement:

            display_message(
                followup_acknowledgement,
                "assistant"
            )


# ==========================================================
# 19. EDIT PREVIOUS ANSWERS
# ==========================================================

def show_answer_editor():

    editable = [
        (i, item)
        for i, item in enumerate(st.session_state.responses)
        if item.get("status") == "answered"
        and item.get("question_id") != "EMOTION_01"
    ]

    if not editable:
        return

    with st.expander(
        "✏️ Review your conversation and edit answers"
    ):

        st.caption(
            "Review your complete conversation with Lia. "
            "You can edit your answers whenever needed."
        )

        for index, item in editable:

            with st.container(border=True):

                st.markdown(
                    f"**Question:** {item.get('question', '')}"
                )

                current = item.get(
                    "edited_answer", ""
                )

                if isinstance(current, list):
                    current = ", ".join(map(str, current))

                st.markdown("**Your answer:**")

                st.write(
                    current if current else "No answer"
                )

                acknowledgement = item.get(
                    "lia_acknowledgement"
                )

                if acknowledgement:

                    st.markdown("**🌷 Lia's response:**")

                    display_message(
                        acknowledgement,
                        "assistant"
                    )

                followup_question = item.get(
                    "followup_question"
                )

                if followup_question:

                    st.markdown(
                        "**Lia's follow-up question:**"
                    )

                    display_message(
                        followup_question,
                        "assistant"
                    )

                    followup_answer = item.get(
                        "followup_answer"
                    )

                    if followup_answer:

                        st.markdown(
                            "**Your follow-up answer:**"
                        )

                        display_message(
                            followup_answer,
                            "user"
                        )

                    elif item.get("followup_skipped"):

                        st.caption(
                            "Follow-up question skipped."
                        )

                st.divider()

                with st.form(f"edit_answer_{index}"):

                    revised = st.text_area(
                        "Edit your answer",
                        value=str(current),
                        key=f"edit_text_{index}"
                    )

                    if st.form_submit_button(
                        "Save edited answer"
                    ):

                        if not revised.strip():

                            st.warning(
                                "Your answer cannot be empty."
                            )

                        else:

                            original_item = deepcopy(item)

                            if "original_answer_before_edit" not in item:

                                item["original_answer_before_edit"] = (
                                    item.get("original_answer")
                                )

                            item["edited_answer"] = revised.strip()
                            item["was_edited"] = True

                            if auto_save():

                                st.success(
                                    "Your edited answer has been saved."
                                )

                                st.rerun()

                            else:

                                st.session_state.responses[index] = (
                                    original_item
                                )

                                st.error(
                                    "Unable to save your edited answer."
                                )


# ==========================================================
# 20. QUESTION SCREEN
# ==========================================================

def show_questions():

    questions = st.session_state.selected_questions

    index = st.session_state.current_question_index

    if index >= len(questions):

        st.session_state.conversation_step = "wellness"

        auto_save()
        st.rerun()

        return

    show_previous_conversation()

    question = questions[index]

    st.progress(
        min(
            (index + 1) / max(len(questions), 1),
            1.0
        )
    )

    st.caption(
        f"Question {index + 1} of {len(questions)}"
    )

    display_message(
        question["text"],
        "assistant"
    )

    st.markdown(
        '<div class="quick-heading">'
        'Choose a quick response or type your own answer.'
        '</div>',
        unsafe_allow_html=True
    )

    options = get_quick_options(question)

    columns = st.columns(2)

    for i, option in enumerate(options):

        with columns[i % 2]:

            if st.button(
                option,
                key=f"quick_{question['id']}_{i}",
                use_container_width=True
            ):

                if option.strip().lower() == "something else":

                    st.session_state[
                        f"show_custom_{question['id']}"
                    ] = True

                    st.rerun()

                else:

                    save_question_answer(
                        question,
                        option
                    )

    custom_key = f"show_custom_{question['id']}"

    if options and not st.session_state.get(
        custom_key, False
    ):

        if st.button(
            "Write my own answer",
            key=f"own_{question['id']}"
        ):

            st.session_state[custom_key] = True
            st.rerun()

    if not options or st.session_state.get(
        custom_key, False
    ):

        custom = st.text_area(
            "Your answer",
            key=f"custom_answer_{question['id']}"
        )

        if st.button(
            "Send my answer",
            key=f"send_custom_{question['id']}"
        ):

            if custom.strip():

                st.session_state[custom_key] = False

                save_question_answer(
                    question,
                    custom.strip()
                )

            else:

                st.warning(
                    "Please enter an answer."
                )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Skip this question",
            key=f"skip_{question['id']}"
        ):

            st.session_state.responses.append({
                "question_id": question["id"],
                "category": question["category"],
                "question": question["text"],
                "original_answer": None,
                "edited_answer": None,
                "status": "skipped"
            })

            st.session_state.current_question_index += 1

            if auto_save():
                st.rerun()
            else:
                st.error("Unable to save your progress.")

    with c2:

        if st.button(
            "Pause conversation",
            key=f"pause_{question['id']}"
        ):

            previous_step = st.session_state.conversation_step

            st.session_state.paused_from_step = previous_step
            st.session_state.conversation_step = "paused"

            if auto_save():
                st.rerun()
            else:
                st.session_state.conversation_step = previous_step

                st.error(
                    "Unable to save your conversation."
                )

    if not st.session_state.pending_followup:
        show_answer_editor()
# ==========================================================
# 21. FOLLOW-UP QUESTIONS
# ==========================================================

def show_followup():

    pending = st.session_state.pending_followup

    if not pending:
        return

    idx = pending.get("response_index")

    if (
        idx is None
        or idx >= len(st.session_state.responses)
    ):

        st.error(
            "Unable to load the follow-up question."
        )

        return

    response = st.session_state.responses[idx]

    acknowledgement = response.get(
        "lia_acknowledgement"
    )

    if acknowledgement:

        display_message(
            acknowledgement,
            "assistant"
        )

    display_message(
        pending["question"],
        "assistant"
    )

    st.caption(
        "You can answer briefly or skip this question."
    )

    answer = st.chat_input(
        "Share your thoughts..."
    )

    if answer:

        if detect_crisis(answer):

            st.session_state.crisis_triggered = True

            auto_save()
            st.rerun()

            return

        prior_history = get_llm_history()

        try:

            with st.spinner("Lia is listening..."):

                followup_ack = (
                    generate_followup_acknowledgement(
                        response.get("question", ""),
                        response.get("edited_answer", ""),
                        pending["question"],
                        answer.strip(),
                        prior_history
                    )
                )

            original_response = deepcopy(response)

            response["followup_answer"] = answer.strip()

            response["followup_acknowledgement"] = (
                followup_ack
            )

            st.session_state.pending_followup = None

            st.session_state.current_question_index += 1

            if not auto_save():

                st.session_state.responses[idx] = original_response

                st.session_state.pending_followup = pending

                st.session_state.current_question_index -= 1

                st.error(
                    "Unable to save your follow-up answer. "
                    "Please try again."
                )

                return

            st.rerun()

        except Exception as error:

            print("FOLLOW-UP ERROR:", error)

            st.error(
                "Unable to process your response. Please try again."
            )

    if st.button("Skip follow-up"):

        original_response = deepcopy(response)

        response["followup_skipped"] = True

        st.session_state.pending_followup = None

        st.session_state.current_question_index += 1

        if auto_save():

            st.rerun()

        else:

            st.session_state.responses[idx] = original_response

            st.session_state.pending_followup = pending

            st.session_state.current_question_index -= 1

            st.error(
                "Unable to save your progress."
            )


# ==========================================================
# 22. WELLNESS SCREEN
# ==========================================================

def show_wellness():

    if st.session_state.activity_answered:

        st.session_state.conversation_step = "closing"

        if auto_save():
            st.rerun()
        else:
            st.error("Unable to save your progress.")

        return

    show_wellness_activity()


# ==========================================================
# 23. CLOSING SCREEN
# ==========================================================

def show_closing():

    st.title("🌷 Thank You for Sharing")

    st.write(
        "Thank you for taking the time to share your thoughts. "
        "Remember, taking care of yourself is important."
    )

    st.write(
        "You're almost done with your Antara session."
    )

    if st.button(
        "Complete My Session",
        use_container_width=True
    ):

        try:

            st.session_state.submitted = True

            if not auto_save():

                st.session_state.submitted = False

                st.error(
                    "Unable to save your session. Please try again."
                )

                return

            complete_patient_session(
                st.session_state.patient_id,
                st.session_state.session_id
            )

            st.success(
                "Your session has been completed!"
            )

            st.rerun()

        except Exception as error:

            st.session_state.submitted = False

            st.error(
                "Unable to complete your session."
            )

            print("SESSION COMPLETION ERROR:", error)


# ==========================================================
# 24. THANK YOU AND REPORT
# ==========================================================

def show_thank_you():

    st.markdown("""
    <div class="login-card">
        <div style="font-size:55px;">🌷</div>
        <h1 style="color:#29243a;">Thank You</h1>
        <p class="login-subtitle">
            Thank you for sharing your feelings with Lia.
            Every feeling deserves to be heard.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🌸 Your Session Details")

    st.info(
        f"Session ID: {st.session_state.session_id}"
    )

    st.write(
        f"**Responses:** {len(st.session_state.responses)}"
    )

    report = {
        "application": "Antara",
        "session_id": st.session_state.session_id,
        "patient_id": st.session_state.patient_id,
        "session_date": datetime.now().isoformat(),
        "time_available": st.session_state.time_available,
        "conversation_mode": st.session_state.conversation_mode,
        "emotional_theme": st.session_state.emotional_theme,
        "responses": st.session_state.responses,
        "crisis_triggered": st.session_state.crisis_triggered
    }

    st.download_button(
        "📥 Download Session Report",
        data=json.dumps(
            report,
            indent=4,
            ensure_ascii=False
        ),
        file_name=f"{st.session_state.session_id}.json",
        mime="application/json",
        use_container_width=True
    )

    st.divider()

    st.markdown("### 🩷 Therapist Portal")

    st.caption(
        "Open your locally configured therapist portal, "
        "if that service is running."
    )

    st.markdown(
        '<a href="http://127.0.0.1:8000/therapist" '
        'target="_blank">🌸 Open Therapist Portal</a>',
        unsafe_allow_html=True
    )

    st.divider()

    if st.button(
        "🌷 Back to My Dashboard",
        use_container_width=True
    ):

        st.session_state.submitted = False
        st.session_state.started = False
        st.session_state.show_dashboard = True

        st.rerun()

    if st.button(
        "🌷 Start a New Session",
        use_container_width=True
    ):

        start_new_session()

        st.session_state.show_dashboard = False

        st.rerun()


# ==========================================================
# 25. PATIENT DASHBOARD
# ==========================================================

def show_patient_dashboard():

    patient_id = st.session_state.patient_id

    sessions = get_history()

    completed_sessions = [
        s for s in sessions
        if s.get("status") == "completed"
    ]

    active_sessions = [
        s for s in sessions
        if s.get("status") == "in_progress"
    ]

    # ------------------------------------------------------
    # DASHBOARD STYLING
    # ------------------------------------------------------

    st.markdown("""
    <style>

    .dashboard-welcome {
        background: rgba(255,255,255,0.88);
        padding: 28px;
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,0.9);
        box-shadow: 0 5px 20px rgba(70,60,100,0.07);
        margin-bottom: 25px;
    }

    .dashboard-welcome h1 {
        color: #29243a;
        font-size: 30px;
        margin-bottom: 8px;
    }

    .dashboard-welcome p {
        color: #625c73;
        font-size: 16px;
    }

    .stat-card {
        background: rgba(255,255,255,0.88);
        padding: 23px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.9);
        box-shadow: 0 4px 15px rgba(70,60,100,0.06);
        min-height: 125px;
    }

    .stat-icon {
        font-size: 25px;
        margin-bottom: 8px;
    }

    .stat-number {
        font-size: 30px;
        font-weight: 700;
        color: #344c78;
    }

    .stat-label {
        color: #696477;
        font-size: 14px;
    }

    .section-heading {
        color: #29243a;
        font-size: 23px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .activity-card {
        background: rgba(255,255,255,0.85);
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #e8ddf0;
        margin-bottom: 12px;
    }

    .activity-card p {
        color: #625c73;
        margin-bottom: 5px;
    }

    .status-completed {
        color: #247a58;
        font-weight: 700;
    }

    .status-progress {
        color: #a36b20;
        font-weight: 700;
    }

    .welcome-icon {
        font-size: 35px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # WELCOME SECTION
    # ------------------------------------------------------

    patient_name = (
        st.session_state.patient_name or "there"
    )

    first_name = patient_name.split()[0]

    st.markdown(f"""
    <div class="dashboard-welcome">
        <div class="welcome-icon">🌷</div>
        <h1>Welcome back, {html.escape(first_name)}!</h1>
        <p>
            Your personal wellness space is here.
            Take a moment for yourself today.
        </p>
        <p>
            Every feeling matters. Every step counts. 💗
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # STATISTICS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">Your Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-number">{len(sessions)}</div>
            <div class="stat-label">Total Sessions</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">🌸</div>
            <div class="stat-number">{len(completed_sessions)}</div>
            <div class="stat-label">Completed Sessions</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">💬</div>
            <div class="stat-number">{len(active_sessions)}</div>
            <div class="stat-label">Ongoing Sessions</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.divider()

    # ------------------------------------------------------
    # DASHBOARD TABS
    # ------------------------------------------------------

    home_tab, sessions_tab, profile_tab, progress_tab = st.tabs([
        "🏠 Home",
        "📋 My Sessions",
        "👤 My Profile",
        "📈 My Progress"
    ])

    # ======================================================
    # HOME TAB
    # ======================================================

    with home_tab:

        st.markdown(
            '<div class="section-heading">Your Wellness Space</div>',
            unsafe_allow_html=True
        )

        st.write(
            "A little space for yourself, your thoughts "
            "and your feelings."
        )

        if active_sessions:

            st.info(
                "💗 You have an unfinished conversation. "
                "You can continue where you left off."
            )

            for session in active_sessions:

                sid = session.get("session_id")

                st.markdown(
                    f"**Unfinished session:** `{sid}`"
                )

                if st.button(
                    "▶️ Resume Previous Conversation",
                    key=f"home_resume_{sid}",
                    use_container_width=True
                ):

                    saved_data = get_patient_session(
                        patient_id,
                        sid
                    )

                    if saved_data and restore_session(saved_data):

                        st.rerun()

                    else:

                        st.error(
                            "Unable to restore your session."
                        )

        else:

            st.markdown("""
            <div class="activity-card">
                <h3 style="color:#344c78;">
                    🌷 Ready to talk?
                </h3>
                <p>
                    Start a new conversation with Lia.
                    Share your thoughts at your own pace.
                </p>
            </div>
            """, unsafe_allow_html=True)

        if st.button(
            "🌷 Start a New Conversation",
            key="home_new_session",
            use_container_width=True
        ):

            start_new_session()

            st.session_state.show_dashboard = False

            st.rerun()

        # RECENT ACTIVITY

        st.divider()

        st.markdown(
            '<div class="section-heading">Your Recent Activity</div>',
            unsafe_allow_html=True
        )

        if sessions:

            for session in sessions[:3]:

                status = session.get(
                    "status",
                    "unknown"
                )

                session_date = format_session_date(
                    session.get("updated_at")
                    or session.get("created_at")
                )

                if status == "completed":
                    status_label = "🌸 Completed"

                elif status == "in_progress":
                    status_label = "🟡 In Progress"

                else:
                    status_label = status.replace(
                        "_", " "
                    ).title()

                st.markdown(f"""
                <div class="activity-card">
                    <p><b>{status_label}</b></p>
                    <p>Session ID: {html.escape(str(session.get("session_id", "")))}</p>
                    <p>Last activity: {html.escape(str(session_date))}</p>
                </div>
                """, unsafe_allow_html=True)

        else:

            st.info(
                "Your recent activities will appear here."
            )

    # ======================================================
    # MY SESSIONS TAB
    # ======================================================

    with sessions_tab:

        st.markdown(
            '<div class="section-heading">Your Session History</div>',
            unsafe_allow_html=True
        )

        if not sessions:

            st.info(
                "You haven't had any conversations yet."
            )

        else:

            for index, session in enumerate(sessions):

                sid = session.get("session_id")

                status = session.get(
                    "status",
                    "unknown"
                )

                session_date = format_session_date(
                    session.get("updated_at")
                    or session.get("created_at")
                )

                if status == "completed":
                    icon = "🌸"

                elif status == "in_progress":
                    icon = "💬"

                else:
                    icon = "📋"

                with st.expander(
                    f"{icon} Session {index + 1} | "
                    f"{status.replace('_', ' ').title()}"
                ):

                    st.write(f"**Session ID:** {sid}")

                    st.write(f"**Date:** {session_date}")

                    st.write(
                        f"**Status:** "
                        f"{status.replace('_', ' ').title()}"
                    )

                    if status == "in_progress":

                        if st.button(
                            "▶️ Resume Session",
                            key=f"history_resume_{sid}"
                        ):

                            saved_data = get_patient_session(
                                patient_id,
                                sid
                            )

                            if saved_data and restore_session(saved_data):

                                st.rerun()

                            else:

                                st.error(
                                    "Unable to restore your session."
                                )

                    elif status == "completed":

                        if st.button(
                            "View Responses",
                            key=f"history_view_{sid}"
                        ):

                            saved_data = get_patient_session(
                                patient_id,
                                sid
                            )

                            if saved_data:

                                session_data = saved_data

                                if isinstance(
                                    saved_data.get("session_data"),
                                    dict
                                ):

                                    session_data = saved_data[
                                        "session_data"
                                    ]

                                responses = session_data.get(
                                    "responses",
                                    []
                                )

                                if responses:

                                    for response in responses:

                                        if not isinstance(response, dict):
                                            continue

                                        question = response.get(
                                            "question",
                                            ""
                                        )

                                        answer = response.get(
                                            "edited_answer"
                                        )

                                        if answer is None:
                                            continue

                                        if isinstance(answer, list):

                                            answer = ", ".join(
                                                map(str, answer)
                                            )

                                        st.markdown(
                                            f"**{question}**"
                                        )

                                        st.write(answer)

                                        st.divider()

                                else:

                                    st.info(
                                        "No responses are available."
                                    )

                            else:

                                st.error(
                                    "Unable to retrieve session details."
                                )

    # ======================================================
    # MY PROFILE TAB
    # ======================================================

    with profile_tab:

        st.markdown(
            '<div class="section-heading">Your Personal Information</div>',
            unsafe_allow_html=True
        )

        try:

            patient = get_patient_details(patient_id)

        except Exception as error:

            print("PROFILE RETRIEVAL ERROR:", error)
            patient = None

        if patient:

            with st.form("patient_profile_form"):

                st.markdown("#### 👤 Basic Information")

                full_name = st.text_input(
                    "Full Name",
                    value=patient.get("full_name") or ""
                )

                date_of_birth = st.text_input(
                    "Date of Birth (YYYY-MM-DD)",
                    value=str(
                        patient.get("date_of_birth") or ""
                    )
                )

                # Calculate age from date of birth.

                calculated_age = 0

                if date_of_birth.strip():

                    try:

                        dob_value = datetime.strptime(
                            date_of_birth.strip(),
                            "%Y-%m-%d"
                        ).date()

                        calculated_age = calculate_age(
                            dob_value
                        )

                    except ValueError:

                        calculated_age = 0

                st.number_input(
                    "Age",
                    min_value=0,
                    max_value=120,
                    value=int(calculated_age),
                    disabled=True
                )

                st.divider()

                st.markdown("#### 📞 Contact Information")

                phone = st.text_input(
                    "Phone Number",
                    value=str(patient.get("phone") or "")
                )

                st.divider()

                st.markdown("#### 📍 Location Details")

                locality = st.text_input(
                    "Locality",
                    value=patient.get("locality") or ""
                )

                city = st.text_input(
                    "City",
                    value=patient.get("city") or ""
                )

                district = st.text_input(
                    "District",
                    value=patient.get("district") or ""
                )

                state = st.text_input(
                    "State",
                    value=patient.get("state") or ""
                )

                pincode = st.text_input(
                    "PIN Code",
                    value=str(patient.get("pincode") or "")
                )

                save_profile = st.form_submit_button(
                    "💾 Save Profile Changes",
                    use_container_width=True
                )

                if save_profile:

                    errors = []

                    if not full_name.strip():

                        errors.append(
                            "Full name cannot be empty."
                        )

                    if not re.fullmatch(
                        r"\d{10}",
                        phone.strip()
                    ):

                        errors.append(
                            "Enter a valid 10-digit phone number."
                        )

                    if not date_of_birth.strip():

                        errors.append(
                            "Date of birth cannot be empty."
                        )

                    else:

                        try:

                            dob_value = datetime.strptime(
                                date_of_birth.strip(),
                                "%Y-%m-%d"
                            ).date()

                            if dob_value > date.today():

                                errors.append(
                                    "Date of birth cannot be in the future."
                                )

                            elif dob_value < date(1920, 1, 1):

                                errors.append(
                                    "Enter a valid date of birth."
                                )

                            else:

                                calculated_age = calculate_age(
                                    dob_value
                                )

                        except ValueError:

                            errors.append(
                                "Enter date of birth in YYYY-MM-DD format."
                            )

                    if pincode.strip() and not re.fullmatch(
                        r"\d{6}",
                        pincode.strip()
                    ):

                        errors.append(
                            "Enter a valid 6-digit PIN code."
                        )

                    if errors:

                        for error in errors:
                            st.error(error)

                    else:

                        updates = {
                            "full_name": full_name.strip(),
                            "phone": phone.strip(),
                            "date_of_birth": date_of_birth.strip(),
                            "age": calculated_age,
                            "locality": locality.strip(),
                            "city": city.strip(),
                            "district": district.strip(),
                            "state": state.strip(),
                            "pincode": pincode.strip()
                        }

                        try:

                            success = update_patient_details(
                                patient_id,
                                updates
                            )

                            if success:

                                st.session_state.patient_name = (
                                    full_name.strip()
                                )

                                st.success(
                                    "Your profile has been updated! 🌷"
                                )

                                st.rerun()

                            else:

                                st.error(
                                    "Unable to update your profile."
                                )

                        except Exception as error:

                            st.error(
                                "An error occurred while updating your profile."
                            )

                            print(
                                "PROFILE UPDATE ERROR:",
                                error
                            )

        else:

            st.error(
                "Unable to retrieve your profile."
            )

    # ======================================================
    # MY PROGRESS TAB
    # ======================================================

    with progress_tab:

        st.markdown(
            '<div class="section-heading">Your Activity Overview</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Here is an overview of your activity on Antara."
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "🌸 Completed Sessions",
                len(completed_sessions)
            )

        with col2:

            st.metric(
                "💬 Ongoing Sessions",
                len(active_sessions)
            )

        st.divider()

        st.markdown("#### Your Session Journey")

        if sessions:

            for index, session in enumerate(sessions):

                status = session.get(
                    "status",
                    "unknown"
                )

                session_date = format_session_date(
                    session.get("updated_at")
                    or session.get("created_at")
                )

                if status == "completed":

                    st.success(
                        f"🌸 Session {index + 1} completed"
                    )

                elif status == "in_progress":

                    st.warning(
                        f"💬 Session {index + 1} in progress"
                    )

                else:

                    st.info(
                        f"Session {index + 1}: {status}"
                    )

                st.caption(session_date)

        else:

            st.info(
                "Your session activity will appear here "
                "after you start your first conversation."
            )

        st.divider()

        st.caption(
            "This dashboard displays application activity only. "
            "It does not measure mental health improvement "
            "or provide a clinical assessment."
        )


# ==========================================================
# 26. CHAT ROUTER
# ==========================================================

def show_chat():

    if not st.session_state.get("session_id"):

        st.error(
            "Your session ID is missing. "
            "Please log out and log in again to recover your session."
        )

        return

    st.title("🌷 Antara")

    st.caption(
        "A space for your feelings, before therapy."
    )

    st.caption(
        f"Session ID: {st.session_state.session_id}"
    )

    if st.session_state.crisis_triggered:

        show_crisis_screen()
        return

    if st.session_state.pending_followup:

        show_followup()
        return

    step = st.session_state.conversation_step

    if step == "introduction":

        show_introduction()

    elif step == "time":

        show_time_selection()

    elif step == "emotion":

        show_emotional_checkin()

    elif step == "questions":

        show_questions()

    elif step == "wellness":

        show_wellness()

    elif step == "closing":

        show_closing()

    elif step == "paused":

        st.info(
            "Your conversation is paused. "
            "You can continue whenever you're ready."
        )

        if st.button("Continue Conversation"):

            previous_step = st.session_state.get(
                "paused_from_step",
                "questions"
            )

            st.session_state.conversation_step = (
                previous_step
                if previous_step != "paused"
                else "questions"
            )

            if auto_save():
                st.rerun()
            else:
                st.session_state.conversation_step = "paused"

                st.error(
                    "Unable to save your progress."
                )


# ==========================================================
# 27. MAIN APPLICATION
# ==========================================================

show_sidebar()

if not st.session_state.logged_in:

    show_authentication_page()

elif st.session_state.show_recovery:

    show_recovery()

elif st.session_state.submitted:

    show_thank_you()

elif st.session_state.get("show_dashboard", False):

    show_patient_dashboard()

elif not st.session_state.started:

    show_welcome()

else:

    show_chat()