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
    update_patient_details,
    change_patient_password,
    set_patient_verification,
    get_connection,
    hash_password
)
from emergency_service import send_emergency_sms, get_emergency_alerts_for_patient
from theme_manager import apply_theme_css, render_theme_toggle


# ==========================================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================================

st.set_page_config(
    page_title="Antara",
    page_icon="🌷",
    layout="wide"
)

apply_theme_css()


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

TIME_DURATION_SECONDS = {
    "5 minutes": 5 * 60,
    "10 minutes": 10 * 60,
    "15 minutes": 15 * 60,
    "20 minutes": 20 * 60,
    "I have plenty of time": 24 * 60 * 60
}

def get_session_target_seconds():
    time_choice = st.session_state.get("time_available")
    return TIME_DURATION_SECONDS.get(time_choice, 5 * 60)

def get_elapsed_seconds():
    start = st.session_state.get("chat_started_at")
    if not start:
        return 0
    try:
        return max(0, datetime.now().timestamp() - float(start))
    except (ValueError, TypeError):
        return 0

def is_session_time_up():
    target = get_session_target_seconds()
    if target >= 24 * 60 * 60:
        return False
    return get_elapsed_seconds() >= target

def get_session_time_remaining():
    target = get_session_target_seconds()
    elapsed = get_elapsed_seconds()
    return max(0, target - elapsed)

CONVERSATION_MODES = {
    "Quick check-in": "gentle and focused",
    "Regular conversation": "balanced and thoughtful",
    "Detailed conversation": "deep and comprehensive",
    "I want to talk freely": "open and unhurried"
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
    "login_role": "patient",
    "patient_id": None,
    "patient_name": None,
    "patient_email": None,

    "emergency_alert_sent": False,
    "last_emergency_receipt": None,
    "app_theme": "⚙️ System",

    "show_dashboard": True,
    "show_settings": False,
    "show_otp_ui_email": False,
    "show_otp_ui_patient_phone": False,
    "show_otp_ui_trusted_phone": False,

    "started": False,
    "consent_given": False,
    "session_id": None,
    "submitted": False,

    "conversation_step": "introduction",
    "chat_started_at": None,
    "time_available": None,
    "conversation_mode": "Regular conversation",

    "emotional_theme": [],
    "selected_questions": [],
    "current_question_index": 0,
    "responses": [],

    "pending_followup": None,
    "unclear_message": None,

    "pending_engagement_check": False,
    "eng_check_3_done": False,
    "eng_check_6_done": False,

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


# ==========================================================
# 4B. EMAIL & CONTACT VERIFICATION HELPERS
# ==========================================================

def validate_email_format(email: str):
    email = str(email or "").strip().lower()
    if not email:
        return False, "Email address cannot be empty."
    if not re.fullmatch(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False, "Please enter a valid email format (e.g. name@example.com)."
    return True, "Valid email format."


def validate_phone_format(phone: str):
    clean = re.sub(r"[^\d+]", "", str(phone or "").strip())
    digits = re.sub(r"\D", "", clean)
    if not digits:
        return False, "Phone number cannot be empty."
    if len(digits) < 10:
        return False, "Phone number must contain at least 10 digits."
    if len(digits) > 15:
        return False, "Phone number cannot exceed 15 digits."
    return True, "Valid phone number format."


def send_verification_otp(channel: str, recipient: str, user_name: str = "User"):
    import secrets
    clean_recipient = str(recipient or "").strip()
    if not clean_recipient:
        return {"success": False, "error": "Recipient is required."}

    otp = f"{secrets.randbelow(900000) + 100000}"
    st.session_state[f"otp_store_{channel}"] = {
        "code": otp,
        "recipient": clean_recipient,
        "sent_at": datetime.now().timestamp()
    }
    st.session_state[f"show_otp_ui_{channel}"] = True

    # If it's a mobile number, dispatch verification SMS
    if "phone" in channel:
        clean_phone = re.sub(r"[^\d+]", "", clean_recipient)
        try:
            send_emergency_sms(
                patient_id=str(st.session_state.get("patient_id") or "PAT-VERIFY"),
                session_id=str(st.session_state.get("session_id") or "SESSION-VERIFY"),
                contact_name=clean_recipient,
                contact_number=clean_phone,
                user_name=user_name,
                reason=f"Verification OTP: {otp}"
            )
        except Exception as e:
            print("OTP SMS dispatch notice:", e)

    return {
        "success": True,
        "code": otp,
        "recipient": clean_recipient,
        "channel": channel
    }


def verify_entered_otp(channel: str, entered_code: str, patient_id: str):
    stored = st.session_state.get(f"otp_store_{channel}")
    if not stored:
        return False, "No active verification code found. Please click 'Verify'."

    # Expiration check (10 minutes)
    if datetime.now().timestamp() - float(stored.get("sent_at", 0)) > 600:
        return False, "Verification code has expired. Please request a new one."

    if str(entered_code or "").strip() != str(stored.get("code", "")).strip():
        return False, "Invalid verification code. Please check and try again."

    field_map = {
        "email": "email_verified",
        "patient_phone": "phone_verified",
        "trusted_phone": "trusted_contact_verified"
    }
    target_field = field_map.get(channel)
    if target_field and patient_id:
        set_patient_verification(patient_id, target_field, 1)

    st.session_state.pop(f"otp_store_{channel}", None)
    st.session_state[f"show_otp_ui_{channel}"] = False
    return True, "Verification successful! 🌸"


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
        "chat_started_at",
        "time_available",
        "conversation_mode",
        "emotional_theme",
        "selected_questions",
        "current_question_index",
        "responses",
        "pending_followup",
        "pending_engagement_check",
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
            "chat_started_at",
            "time_available",
            "conversation_mode",
            "emotional_theme",
            "selected_questions",
            "current_question_index",
            "responses",
            "pending_followup",
            "pending_engagement_check",
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
            A safe space to express your feelings, practice self-care, and find support.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

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

            valid_em, em_err = validate_email_format(email)
            if not valid_em:
                errors.append(em_err)

            valid_p, p_err = validate_phone_format(phone)
            if not valid_p:
                errors.append(f"Phone Number: {p_err}")

            if trusted_phone.strip():
                valid_tp, tp_err = validate_phone_format(trusted_phone)
                if not valid_tp:
                    errors.append(f"Trusted Contact Phone: {tp_err}")

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

                valid_tp, tp_err = validate_phone_format(trusted_phone)
                if not valid_tp:
                    errors.append(f"Trusted Contact Phone: {tp_err}")

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

    with st.sidebar:

        st.markdown("""
        <div class="sidebar-profile">
            <div class="sidebar-logo">🌷</div>
            <div class="sidebar-title">Antara</div>
            <p style="text-align:center;margin:4px 0 0 0;font-size:13px;">
                Your Personal Wellness & Self-Care Space
            </p>
        </div>
        """, unsafe_allow_html=True)

        render_theme_toggle(sidebar=True)

        if not st.session_state.logged_in:
            st.caption("Sign in to access your confidential wellness conversations.")
            st.divider()
            if st.session_state.get("show_settings", False):
                if st.button("❌ Close Settings", key="sidebar_close_settings_loggedout", use_container_width=True):
                    st.session_state.show_settings = False
                    st.rerun()
            else:
                if st.button("⚙️ Settings", key="sidebar_open_settings_loggedout", use_container_width=True):
                    st.session_state.show_settings = True
                    st.rerun()
            st.caption("🌷 Antara | Your feelings matter.")
            return

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

        if st.session_state.started and not st.session_state.get("show_dashboard", False):
            if st.button(
                "⬅️ Back to Dashboard",
                key="sidebar_back_to_dashboard",
                use_container_width=True
            ):
                st.session_state.show_dashboard = True
                auto_save()
                st.rerun()

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

        st.markdown("### 🆘 Real-World Help")
        st.caption("If you feel overwhelmed or in danger, Antara can alert your trusted emergency contact.")
        if st.button("🚨 Alert Emergency Contact", key="sidebar_emergency_btn", use_container_width=True):
            st.session_state.crisis_triggered = True
            st.session_state.emergency_alert_sent = False
            auto_save()
            st.rerun()

        st.divider()

        # ⚙️ Settings at the bottom of the sidebar
        if st.session_state.get("show_settings", False):
            if st.button("❌ Close Settings", key="sidebar_close_settings_btn", use_container_width=True):
                st.session_state.show_settings = False
                st.rerun()
        else:
            if st.button("⚙️ Settings", key="sidebar_open_settings_btn", use_container_width=True):
                st.session_state.show_settings = True
                st.rerun()

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
    Antara is a conversational self-help and emotional wellness companion.
    Lia is here to provide a calm, supportive space to express your feelings,
    reflect on your well-being, and practice grounding activities.

    You can chat freely, skip questions, or pause whenever you need.
    """)

    st.info("""
    💡 **Self-Help & Emergency Safety:**  
    Antara is a supportive AI companion and does not replace medical or psychological diagnosis.
    If at any time you need real-world help or express acute distress, Antara can connect you to emergency helplines and dispatch an alert text to your trusted contact.
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
            st.session_state.chat_started_at = None
            st.session_state.eng_check_3_done = False
            st.session_state.eng_check_6_done = False
            st.session_state.pending_engagement_check = False

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

    unique = []
    seen = set()

    for question in selected:
        if question["category"] != "closing" and question["id"] not in seen:
            unique.append(question)
            seen.add(question["id"])

    st.session_state.selected_questions = unique
    st.session_state.current_question_index = 0
    st.session_state.chat_started_at = datetime.now().timestamp()
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

    st.error("🚨 Real-World Safety Circuit-Breaker Triggered")

    st.markdown("""
    **Your safety and well-being matter most.**  
    Antara noticed you may be in acute distress or in need of immediate real-world human support.
    Conversational chat has been paused to prioritize your safety.
    """)

    patient = None
    try:
        patient = get_patient_details(st.session_state.patient_id)
    except Exception as error:
        print("PATIENT DETAILS ERROR:", error)

    if patient:
        name = patient.get("trusted_contact_name") or ""
        relationship = patient.get("trusted_contact_relationship") or ""
        number = patient.get("trusted_contact_number") or ""
        consent = bool(patient.get("emergency_alert_consent"))
        agreement = bool(patient.get("trusted_contact_agreement"))
        user_name = patient.get("full_name") or "Antara User"
        user_loc = f"{patient.get('locality') or ''}, {patient.get('city') or ''}".strip(", ")

        if number and consent and agreement:
            # Automatically dispatch text alert if not already sent during this trigger
            if not st.session_state.get("emergency_alert_sent"):
                receipt = send_emergency_sms(
                    patient_id=st.session_state.patient_id,
                    session_id=st.session_state.session_id or "SESSION_ALERT",
                    contact_name=name,
                    contact_number=number,
                    user_name=user_name,
                    reason="indicated acute distress or requested real-world help",
                    location=user_loc
                )
                st.session_state.emergency_alert_sent = True
                st.session_state.last_emergency_receipt = receipt

            receipt = st.session_state.get("last_emergency_receipt") or {}
            st.markdown(f"""
            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:14px; padding:18px; margin:16px 0;">
                <h4 style="margin:0 0 8px 0; color:#991b1b;">📨 Emergency Alert Dispatched to Your Trusted Contact</h4>
                <p style="margin:0 0 10px 0; color:#7f1d1d; font-size:14px;">
                    A text alert has been automatically sent to <strong>{html.escape(name)}</strong> ({html.escape(relationship)}) at <code>{html.escape(number)}</code>:
                </p>
                <div style="background:white; border-left:4px solid #ef4444; padding:10px 14px; border-radius:6px; font-size:13px; color:#374151;">
                    <em>"{html.escape(receipt.get('message_body', 'Antara Safety Alert: User needs immediate support.'))}"</em>
                </div>
                <p style="margin:10px 0 0 0; color:#991b1b; font-size:12px;">
                    <strong>Status:</strong> ✅ {html.escape(receipt.get('status', 'DISPATCHED'))} &nbsp;•&nbsp; 
                    <strong>Time:</strong> {html.escape(receipt.get('dispatched_at', 'Just now'))} &nbsp;•&nbsp;
                    <strong>Ref ID:</strong> <code>{html.escape(receipt.get('alert_id', 'N/A'))}</code>
                </p>
            </div>
            """, unsafe_allow_html=True)

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                phone_link = re.sub(r"[^0-9+]", "", number)
                st.markdown(
                    f'<a href="tel:{html.escape(phone_link, quote=True)}" style="display:block; text-align:center; padding:12px 20px; background:#e0f2fe; color:#0369a1; border-radius:12px; font-weight:700; text-decoration:none;">📞 Call {html.escape(name)} Now</a>',
                    unsafe_allow_html=True
                )
            with c_btn2:
                if st.button("🔄 Re-send Emergency Alert SMS", use_container_width=True):
                    receipt = send_emergency_sms(
                        patient_id=st.session_state.patient_id,
                        session_id=st.session_state.session_id or "SESSION_ALERT",
                        contact_name=name,
                        contact_number=number,
                        user_name=user_name,
                        reason="manual re-dispatch requested",
                        location=user_loc
                    )
                    st.session_state.last_emergency_receipt = receipt
                    st.success(f"Emergency alert text re-dispatched to {name}!")
                    st.rerun()
        else:
            st.info(
                "No trusted emergency contact is currently configured with SMS alert consent on your account. "
                "You can add one anytime in your account details."
            )
    else:
        st.warning("We couldn't retrieve your saved contact information.")

    st.divider()
    st.markdown("### 📞 24/7 Professional Helplines")

    hl1, hl2, hl3 = st.columns(3)
    with hl1:
        st.markdown("""
        **🚨 All-India Emergency**  
        **Dial 112** (Police & Medical)  
        """)
        st.markdown(
            '<a href="tel:112" style="display:inline-block; padding:8px 16px; background:#fee2e2; color:#991b1b; border-radius:8px; font-weight:600; text-decoration:none;">📞 Call 112</a>',
            unsafe_allow_html=True
        )
    with hl2:
        st.markdown("""
        **🧠 Tele-MANAS (Govt of India)**  
        **14416** / **1800-891-4416**  
        """)
        st.markdown(
            '<a href="tel:14416" style="display:inline-block; padding:8px 16px; background:#e0e7ff; color:#3730a3; border-radius:8px; font-weight:600; text-decoration:none;">📞 Call 14416</a>',
            unsafe_allow_html=True
        )
    with hl3:
        st.markdown("""
        **🌸 Kiran Mental Health**  
        **1800-599-0019** (Toll-Free)  
        """)
        st.markdown(
            '<a href="tel:18005990019" style="display:inline-block; padding:8px 16px; background:#f3e8ff; color:#6b21a8; border-radius:8px; font-weight:600; text-decoration:none;">📞 Call Kiran</a>',
            unsafe_allow_html=True
        )

    st.write("")
    st.divider()

    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("🌷 I Feel Safe Now — Return to My Space", use_container_width=True):
            st.session_state.crisis_triggered = False
            st.session_state.emergency_alert_sent = False
            st.session_state.submitted = False
            st.session_state.show_dashboard = True
            st.rerun()

    with col_act2:
        if st.button("End Session & Rest", use_container_width=True):
            session_id = st.session_state.session_id
            patient_id = st.session_state.patient_id
            try:
                st.session_state.submitted = True
                if auto_save():
                    complete_patient_session(patient_id, session_id)
            except Exception as e:
                print("Error ending session:", e)
            st.session_state.crisis_triggered = False
            st.session_state.show_dashboard = True
            st.rerun()


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

    btn_col1, btn_col2 = st.columns([1, 2])
    with btn_col1:
        if st.button("⬅️ Dashboard", key="intro_back_dashboard", use_container_width=True):
            st.session_state.show_dashboard = True
            auto_save()
            st.rerun()

    with btn_col2:
        if st.button(
            "Continue ➡️",
            key="intro_continue",
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

    btn_col1, btn_col2 = st.columns([1, 2])
    with btn_col1:
        if st.button("⬅️ Back", key="time_back_intro", use_container_width=True):
            st.session_state.conversation_step = "introduction"
            auto_save()
            st.rerun()

    with btn_col2:
        if st.button(
            "Continue ➡️",
            key="time_continue",
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

    btn_col1, btn_col2 = st.columns([1, 2])
    with btn_col1:
        if st.button("⬅️ Back", key="emotion_back_time", use_container_width=True):
            st.session_state.conversation_step = "time"
            auto_save()
            st.rerun()

    with btn_col2:
        if st.button(
            "Continue ➡️",
            key="emotion_continue",
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

    qid = question.get("id", "")
    if qid in QUESTION_OPTIONS:
        return QUESTION_OPTIONS[qid]

    cat = question.get("category", "")
    if cat == "mindfulness":
        return ["I notice something quiet and peaceful", "I feel a bit restless right now", "Something else"]
    elif cat in ["comfort", "habits"]:
        return ["It's been okay", "It could definitely be better", "Something else"]
    elif cat in ["strengths", "self_compassion", "growth"]:
        return ["My resilience and patience", "Taking things one day at a time", "Something else"]
    elif cat in ["reflection", "processing", "emotions", "open_reflection"]:
        return ["I'm still reflecting on this", "It's hard to put into words", "Something else"]

    return [
        "I'm still thinking about it",
        "It's hard to put into words",
        "Something else"
    ]


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

    # Initialize clock start time if not yet set
    if not st.session_state.get("chat_started_at"):
        st.session_state.chat_started_at = datetime.now().timestamp()

    # Real-time clock check: Has the user's chosen session duration elapsed?
    if is_session_time_up():
        st.session_state.conversation_step = "continuation_check"
        auto_save()
        st.rerun()
        return

    # Dynamic continuous question generation: If questions are exhausted but time remains, generate more!
    questions = st.session_state.selected_questions
    index = st.session_state.current_question_index

    if index >= len(questions):
        extend_conversation_questions()
        questions = st.session_state.selected_questions
        if index >= len(questions):
            st.session_state.conversation_step = "continuation_check"
            auto_save()
            st.rerun()
            return

    # Periodic Engagement & Fatigue Check-in (triggers after 3 and 8 questions)
    answered_count = len([r for r in st.session_state.responses if r.get("status") in ["answered", "skipped"]])
    if (
        (answered_count >= 3 and not st.session_state.get("eng_check_3_done", False))
        or (answered_count >= 8 and not st.session_state.get("eng_check_6_done", False))
    ):
        if answered_count >= 8:
            st.session_state.eng_check_6_done = True
        else:
            st.session_state.eng_check_3_done = True
        st.session_state.pending_engagement_check = True
        auto_save()
        st.rerun()
        return

    show_previous_conversation()

    question = questions[index]

    # Time-based progress bar and status caption
    target_sec = get_session_target_seconds()
    elapsed_sec = get_elapsed_seconds()

    if target_sec < 24 * 60 * 60:
        time_ratio = min(1.0, elapsed_sec / max(target_sec, 1))
        st.progress(time_ratio)
        mins_left = max(0, int(round((target_sec - elapsed_sec) / 60)))
        if mins_left > 0:
            st.caption(
                f"⏱️ ~{mins_left} min remaining of your "
                f"{st.session_state.get('time_available', 'session')} · Question {index + 1}"
            )
        else:
            st.caption(
                f"⏱️ Final moments of your "
                f"{st.session_state.get('time_available', 'session')} · Question {index + 1}"
            )
    else:
        st.caption(f"🌿 Open conversation · Question {index + 1}")

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

    nav_back_col1, nav_back_col2 = st.columns([1, 1])
    with nav_back_col1:
        if index > 0:
            if st.button("⬅️ Previous question", key=f"prev_{question['id']}", use_container_width=True):
                st.session_state.current_question_index -= 1
                if st.session_state.responses and len(st.session_state.responses) > st.session_state.current_question_index:
                    st.session_state.responses.pop()
                auto_save()
                st.rerun()
        else:
            if st.button("⬅️ Back to Feelings check-in", key=f"prev_to_emotion_{question['id']}", use_container_width=True):
                st.session_state.conversation_step = "emotion"
                auto_save()
                st.rerun()

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        if st.button(
            "Skip question",
            key=f"skip_{question['id']}",
            use_container_width=True
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
            "Pause",
            key=f"pause_{question['id']}",
            use_container_width=True
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

    with c3:

        if st.button(
            "🌿 Need break?",
            key=f"checkin_{question['id']}",
            use_container_width=True,
            help="Take a breather, switch activities, or check in with Lia"
        ):
            st.session_state.pending_engagement_check = True
            if auto_save():
                st.rerun()
            else:
                st.error("Unable to save your progress.")

    with c4:

        if st.button(
            "🏁 Wrap up",
            key=f"wrap_{question['id']}",
            use_container_width=True,
            help="Ready to conclude or wrap up your session"
        ):
            st.session_state.conversation_step = "continuation_check"
            if auto_save():
                st.rerun()
            else:
                st.error("Unable to save your progress.")

    if not st.session_state.pending_followup:
        show_answer_editor()


# ==========================================================
# 20B. ENGAGEMENT & FATIGUE CHECK-IN
# ==========================================================

def show_engagement_check():

    show_previous_conversation()

    check_message = (
        "Hey, let's take a gentle pause for a moment 🌿\n\n"
        "We've been talking for a bit, and I want to make sure you're feeling comfortable. "
        "Antara is your safe space—it should never feel like an interrogation, a test, or a boring questionnaire.\n\n"
        "How is this conversation feeling for you right now?"
    )
    display_message(check_message, "assistant")

    st.markdown(
        '<div class="quick-heading">'
        'How would you like to proceed?'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "😊 I'm doing good, let's keep talking",
            key="eng_keep_going",
            use_container_width=True
        ):
            st.session_state.pending_engagement_check = False
            st.session_state.responses.append({
                "question_id": "CHECKIN_CONTINUE",
                "category": "engagement",
                "question": "How are you feeling about our conversation right now?",
                "original_answer": "I'm doing good, let's keep talking 😊",
                "edited_answer": "I'm doing good, let's keep talking 😊",
                "status": "answered",
                "lia_acknowledgement": "Glad to hear that! We'll keep going at whatever pace feels comfortable for you 🌸",
                "followup_question": None,
                "followup_answer": None,
                "followup_skipped": False,
                "was_edited": False
            })
            auto_save()
            st.rerun()

    with col2:
        if st.button(
            "🫂 It's feeling a bit heavy / overwhelming",
            key="eng_overwhelmed",
            use_container_width=True
        ):
            st.session_state.pending_engagement_check = False
            st.session_state.responses.append({
                "question_id": "CHECKIN_OVERWHELMED",
                "category": "engagement",
                "question": "How are you feeling about our conversation right now?",
                "original_answer": "It's feeling a bit heavy / overwhelming 🫂",
                "edited_answer": "It's feeling a bit heavy / overwhelming 🫂",
                "status": "answered",
                "lia_acknowledgement": "Thank you for being open with me. It is completely okay to feel overwhelmed. Let's stop the questions and take a quiet, calming break together 💗",
                "followup_question": None,
                "followup_answer": None,
                "followup_skipped": False,
                "was_edited": False
            })
            st.session_state.conversation_step = "wellness"
            auto_save()
            st.rerun()

    col3, col4 = st.columns(2)

    with col3:
        if st.button(
            "🥱 A bit bored / tired of answering questions",
            key="eng_bored",
            use_container_width=True
        ):
            st.session_state.pending_engagement_check = False
            st.session_state.responses.append({
                "question_id": "CHECKIN_BORED",
                "category": "engagement",
                "question": "How are you feeling about our conversation right now?",
                "original_answer": "A bit bored / tired of answering questions 🥱",
                "edited_answer": "A bit bored / tired of answering questions 🥱",
                "status": "answered",
                "lia_acknowledgement": "I completely understand! Answering question after question gets tedious fast. Let's skip the rest of the questions and do something relaxing instead 🌷",
                "followup_question": None,
                "followup_answer": None,
                "followup_skipped": False,
                "was_edited": False
            })
            st.session_state.conversation_step = "wellness"
            auto_save()
            st.rerun()

    with col4:
        if st.button(
            "🌿 I'd like to wrap up for today",
            key="eng_wrap_up",
            use_container_width=True
        ):
            st.session_state.pending_engagement_check = False
            st.session_state.responses.append({
                "question_id": "CHECKIN_WRAPUP",
                "category": "engagement",
                "question": "How are you feeling about our conversation right now?",
                "original_answer": "I'd like to wrap up for today 🌿",
                "edited_answer": "I'd like to wrap up for today 🌿",
                "status": "answered",
                "lia_acknowledgement": "You did wonderfully today. Taking care of yourself means knowing when you've done enough. Let's wrap things up gently 🌸",
                "followup_question": None,
                "followup_answer": None,
                "followup_skipped": False,
                "was_edited": False
            })
            st.session_state.conversation_step = "closing"
            auto_save()
            st.rerun()


# ==========================================================
# 20C. EXTEND CONVERSATION & CONTINUATION CHECK
# ==========================================================

CONTINUOUS_REFLECTION_QUESTIONS = [
    {"category": "strengths", "text": "What is one strength or quality in yourself that has helped you get through hard days in the past?"},
    {"category": "coping", "text": "When everything feels like too much, what is one small activity or place that helps you feel safe?"},
    {"category": "mindfulness", "text": "Take a gentle breath. If you look around your space right now, what is one calming or grounding thing you notice?"},
    {"category": "self_compassion", "text": "If a dear friend came to you carrying the same weight you're carrying today, what gentle words would you say to them?"},
    {"category": "reflection", "text": "What is something that has been taking up a lot of your mental energy lately?"},
    {"category": "reflection", "text": "What is one thing you wish someone in your life understood a little better about your day-to-day experience?"},
    {"category": "habits", "text": "How has your sleep or rest been feeling over the past few nights?"},
    {"category": "comfort", "text": "What is a favorite song, book, show, or warm drink that always brings you a sense of comfort?"},
    {"category": "boundaries", "text": "Is there any situation or obligation right now where you feel you need to set a gentler boundary for yourself?"},
    {"category": "gratitude", "text": "Even on tough days, was there one tiny moment—like warm sunshine, a kind smile, or a quiet moment—that felt okay?"},
    {"category": "emotions", "text": "When you feel stressed or low, where in your body do you notice that tension the most?"},
    {"category": "goals", "text": "What is something small you're quietly hoping for or looking forward to in the coming weeks?"},
    {"category": "creativity", "text": "Do you have any hobbies, music, or creative outlets that help you express what words sometimes can't?"},
    {"category": "support", "text": "Who is one person or community in your life that makes you feel heard or accepted as you are?"},
    {"category": "self_care", "text": "What is one kind, forgiving thing you can give yourself permission to do (or not do) today?"},
    {"category": "reflection", "text": "What is something on your mind right now that you haven't had a chance to say out loud?"},
    {"category": "growth", "text": "Looking back over the past year, in what ways have you grown or learned more about what you need?"},
    {"category": "grounding", "text": "If you could pause everything for an hour and do anything purely for your peace of mind, what would it be?"},
    {"category": "processing", "text": "Is there a recurring worry or thought pattern you notice yourself returning to often?"},
    {"category": "peace", "text": "What does feeling truly at peace look or feel like for you?"}
]

def extend_conversation_questions():

    existing_ids = {
        q["id"] for q in st.session_state.selected_questions
    }
    new_questions = []

    # 1. Exhaust any remaining structured questions from all question bank categories
    categories = [
        "daily_routine",
        "therapy_goals",
        "general",
        "relationships",
        "stress",
        "sadness",
        "loneliness",
        "physical_health"
    ]

    for cat in categories:
        cat_data = QUESTION_BANK.get(cat, {})
        for item in cat_data.get("questions", []):
            if item["id"] not in existing_ids:
                new_questions.append({
                    "category": cat,
                    "id": item["id"],
                    "text": item["question"]
                })
                existing_ids.add(item["id"])
            if len(new_questions) >= 4:
                break
        if len(new_questions) >= 4:
            break

    # 2. Draw from the continuous reflection questions catalog
    if len(new_questions) < 4:
        for idx, prompt_item in enumerate(CONTINUOUS_REFLECTION_QUESTIONS):
            prompt_id = f"REFLECT_{idx + 1}"
            if prompt_id not in existing_ids:
                new_questions.append({
                    "category": prompt_item.get("category", "open_reflection"),
                    "id": prompt_id,
                    "text": prompt_item["text"]
                })
                existing_ids.add(prompt_id)
            if len(new_questions) >= 4:
                break

    # 3. Dynamic fallback generator so questions never run dry
    if not new_questions:
        curr_len = len(st.session_state.selected_questions)
        dynamic_prompts = [
            "What is something on your mind right now that you haven't had a chance to say out loud?",
            "If there is one thing you wish someone understood about what you're feeling, what would it be?",
            "What is something small that brought you even a little comfort recently?",
            "Looking ahead, what is one kind thing you can do for yourself today?",
            "How does your energy feel right at this moment?",
            "What is a thought or feeling that has felt heavy this week?"
        ]
        for i, text in enumerate(dynamic_prompts):
            dyn_id = f"DYN_REFLECT_{curr_len + i + 1}"
            if dyn_id not in existing_ids:
                new_questions.append({
                    "category": "open_reflection",
                    "id": dyn_id,
                    "text": text
                })
                existing_ids.add(dyn_id)
            if len(new_questions) >= 4:
                break

    st.session_state.selected_questions.extend(new_questions)


def show_continuation_check():

    show_previous_conversation()

    time_choice = st.session_state.get("time_available", "our planned time")
    continuation_message = (
        f"Our planned {time_choice} check-in time for today is complete 🌸.\n\n"
        "Antara is your safe, unhurried space—our conversation never has to end abruptly. "
        "If you still have things on your mind that you'd like to share or explore, Lia is right here with you.\n\n"
        "Would you like to keep talking and continue our conversation, or are you ready to wrap up for today?"
    )
    display_message(continuation_message, "assistant")

    st.markdown(
        '<div class="quick-heading">'
        'Would you like to continue or finish?'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "💬 Keep Talking (+5 more minutes)",
            key="btn_keep_talking_5m",
            use_container_width=True
        ):
            st.session_state.chat_started_at = datetime.now().timestamp()
            st.session_state.time_available = "5 minutes"
            extend_conversation_questions()
            st.session_state.conversation_step = "questions"
            st.session_state.responses.append({
                "question_id": "CONT_EXTEND_5M",
                "category": "continuation",
                "question": "Would you like to continue our conversation or wrap up?",
                "original_answer": "I'd like to keep talking (+5 minutes) 💬",
                "edited_answer": "I'd like to keep talking (+5 minutes) 💬",
                "status": "answered",
                "lia_acknowledgement": "I'm so glad you want to stay and chat a bit longer. Let's keep going at whatever pace feels good 💗",
                "followup_question": None,
                "followup_answer": None,
                "followup_skipped": False,
                "was_edited": False
            })
            auto_save()
            st.rerun()

    with col2:
        if st.button(
            "✨ Keep Talking Freely (No Time Limit)",
            key="btn_keep_talking_free",
            use_container_width=True
        ):
            st.session_state.chat_started_at = datetime.now().timestamp()
            st.session_state.time_available = "I have plenty of time"
            extend_conversation_questions()
            st.session_state.conversation_step = "questions"
            st.session_state.responses.append({
                "question_id": "CONT_EXTEND_FREE",
                "category": "continuation",
                "question": "Would you like to continue our conversation or wrap up?",
                "original_answer": "I want to talk freely with no time limit ✨",
                "edited_answer": "I want to talk freely with no time limit ✨",
                "status": "answered",
                "lia_acknowledgement": "Take all the time you need. I'm right here with you 🌿",
                "followup_question": None,
                "followup_answer": None,
                "followup_skipped": False,
                "was_edited": False
            })
            auto_save()
            st.rerun()

    col3, col4 = st.columns([1, 1])

    with col3:
        if st.button(
            "🌿 Ready to Wrap Up for Today",
            key="btn_wrap_up_cont",
            use_container_width=True
        ):
            st.session_state.conversation_step = "wellness"
            st.session_state.responses.append({
                "question_id": "CONT_WRAPUP",
                "category": "continuation",
                "question": "Would you like to continue our conversation or wrap up?",
                "original_answer": "I'm ready to wrap up for today 🌿",
                "edited_answer": "I'm ready to wrap up for today 🌿",
                "status": "answered",
                "lia_acknowledgement": "You did wonderfully today. Thank you for sharing your time and thoughts with me 🌸",
                "followup_question": None,
                "followup_answer": None,
                "followup_skipped": False,
                "was_edited": False
            })
            auto_save()
            st.rerun()

    with col4:
        if st.button(
            "🌷 Go Directly to Completion",
            key="btn_direct_close_cont",
            use_container_width=True
        ):
            st.session_state.conversation_step = "closing"
            auto_save()
            st.rerun()
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

    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:
        if st.button(
            "💬 Continue Conversation Instead",
            key="closing_back_to_chat",
            use_container_width=True
        ):
            st.session_state.chat_started_at = datetime.now().timestamp()
            st.session_state.time_available = "5 minutes"
            extend_conversation_questions()
            st.session_state.conversation_step = "questions"
            auto_save()
            st.rerun()

    with btn_col2:
        if st.button(
            "Complete My Session 🌷",
            key="btn_complete_session_final",
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
        <h1 style="color:#29243a;">Thank You for Sharing</h1>
        <p class="login-subtitle">
            Taking time to acknowledge your emotions is an important act of self-care.
            Every feeling deserves gentle understanding and space to breathe.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("activity_suggested"):
        act_data = st.session_state.get("activity_data", {})
        title = act_data.get("title", "Grounding Technique") if isinstance(act_data, dict) else "Grounding Technique"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.85); border:1px solid #ead5f5; border-radius:16px; padding:18px; margin:16px 0;">
            <h4 style="margin:0 0 6px 0; color:#582f7c;">🧘 Gentle Wellness Reminder: {html.escape(title)}</h4>
            <p style="margin:0; color:#625c73; font-size:14px;">
                Remember you can always return to this exercise or take slow, deep breaths whenever life feels heavy.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🌷 Return to My Wellness Space",
            use_container_width=True
        ):
            st.session_state.submitted = False
            st.session_state.started = False
            st.session_state.show_dashboard = True
            st.rerun()

    with col2:
        if st.button(
            "💬 Start a New Conversation",
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
    # DASHBOARD STYLING & STATUS COLORS
    # ------------------------------------------------------

    st.markdown("""
    <style>
    .status-completed {
        color: #10b981;
        font-weight: 700;
    }

    .status-progress {
        color: #f59e0b;
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

        home_btn_c1, home_btn_c2 = st.columns([1, 1])

        with home_btn_c1:
            if st.button(
                "🌷 Start a New Conversation",
                key="home_new_session",
                use_container_width=True
            ):

                start_new_session()

                st.session_state.show_dashboard = False

                st.rerun()

        with home_btn_c2:
            if st.button(
                "⚙️ Settings & Preferences",
                key="home_open_settings",
                use_container_width=True
            ):
                st.session_state.show_settings = True
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

            # Verification Status Summary
            em_v = bool(patient.get("email_verified", 0))
            ph_v = bool(patient.get("phone_verified", 0))
            tc_v = bool(patient.get("trusted_contact_verified", 0))

            v_col1, v_col2, v_col3 = st.columns(3)
            with v_col1:
                st.caption("📧 Email Verification")
                st.markdown("🟢 **Verified**" if em_v else "🟠 **Unverified**")
            with v_col2:
                st.caption("📱 Mobile Verification")
                st.markdown("🟢 **Verified**" if ph_v else "🟠 **Unverified**")
            with v_col3:
                st.caption("🆘 Safety Contact")
                st.markdown("🟢 **Verified**" if tc_v else "🟠 **Unverified**")

            if not (em_v and ph_v and tc_v):
                st.info("💡 Complete verification for your email and contact numbers in **⚙️ Settings** to activate verified safety alerts.")
                if st.button("⚙️ Open Settings to Verify", key="dash_profile_to_settings", use_container_width=True):
                    st.session_state.show_settings = True
                    st.rerun()

            st.write("")

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

                    valid_p, p_err = validate_phone_format(phone)
                    if not valid_p:
                        errors.append(f"Phone Number: {p_err}")

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

                        old_p = str(patient.get("phone") or "").strip()
                        new_p = phone.strip()
                        updates = {
                            "full_name": full_name.strip(),
                            "phone": new_p,
                            "date_of_birth": date_of_birth.strip(),
                            "age": calculated_age,
                            "locality": locality.strip(),
                            "city": city.strip(),
                            "district": district.strip(),
                            "state": state.strip(),
                            "pincode": pincode.strip()
                        }
                        if old_p and new_p != old_p:
                            updates["phone_verified"] = 0

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

    top_nav1, top_nav2 = st.columns([1, 3])
    with top_nav1:
        if st.button("⬅️ Dashboard", key="chat_top_back_dashboard", use_container_width=True, help="Save & return to your dashboard"):
            st.session_state.show_dashboard = True
            auto_save()
            st.rerun()

    with top_nav2:
        st.caption(
            f"Session ID: {st.session_state.session_id}"
        )

    st.title("🌷 Antara")

    st.caption(
        "A space for your feelings, emotional wellness & self-care."
    )

    if st.session_state.crisis_triggered:

        show_crisis_screen()
        return

    if st.session_state.pending_followup:

        show_followup()
        return

    if st.session_state.get("pending_engagement_check", False):

        show_engagement_check()
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

    elif step == "continuation_check":

        show_continuation_check()

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
# 26. SETTINGS & PREFERENCES
# ==========================================================

def show_settings_page():

    # Top Header & Back Navigation
    col_title, col_btn = st.columns([3, 1])

    with col_title:
        st.markdown("""
        <div style="margin-bottom: 8px;">
            <h1 style="margin:0; font-size:1.85rem; font-weight:700;">⚙️ Settings & Preferences</h1>
            <p style="margin:4px 0 0 0; opacity:0.8; font-size:0.95rem;">
                Manage your account, emergency safety network, conversation flow, themes, and data.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        if st.session_state.started and not st.session_state.get("show_dashboard", False):
            back_lbl = "⬅️ Back to Chat"
        else:
            back_lbl = "⬅️ Back to Dashboard"

        if st.button(back_lbl, key="settings_top_back_btn", use_container_width=True):
            st.session_state.show_settings = False
            st.rerun()

    st.write("")

    tab_account, tab_emergency, tab_theme, tab_conv, tab_privacy, tab_about = st.tabs([
        "👤 Account Details",
        "🆘 Emergency Contacts",
        "🎨 Theme & Visuals",
        "💬 Conversation",
        "🛡️ Privacy & Data",
        "ℹ️ About Antara"
    ])

    patient_id = st.session_state.get("patient_id")
    patient = get_patient_details(patient_id) if patient_id else {}
    if not patient:
        patient = {}

    # ==========================================================
    # TAB 1: 👤 ACCOUNT DETAILS
    # ==========================================================
    with tab_account:
        if not st.session_state.logged_in:
            st.info("Please sign in or create an account to view and update your personal details.")
        else:
            st.markdown("### 👤 Personal Account Information")
            st.caption("Keep your profile information up-to-date for your personalized wellness companion.")

            is_email_verified = bool(patient.get("email_verified", 0))
            is_phone_verified = bool(patient.get("phone_verified", 0))

            acc_col1, acc_col2 = st.columns(2)
            with acc_col1:
                st.text_input("Account ID", value=str(patient_id or ""), disabled=True, help="Your unique confidential identifier.")
                acc_name = st.text_input("Full Name", value=patient.get("full_name") or st.session_state.patient_name or "", key="set_acc_name")
                acc_phone = st.text_input("Phone Number", value=patient.get("phone") or "", key="set_acc_phone", placeholder="+91...")

                # Phone verification status & trigger
                valid_phone, phone_msg = validate_phone_format(acc_phone)
                if acc_phone and not valid_phone:
                    st.caption(f"⚠️ {phone_msg}")

                if is_phone_verified and acc_phone.strip() == str(patient.get("phone") or "").strip() and acc_phone.strip():
                    st.markdown("🟢 **Phone Number Verified** ✅")
                else:
                    phone_v_c1, phone_v_c2 = st.columns([1, 1])
                    with phone_v_c1:
                        st.markdown("🟠 **Phone Unverified** ⚠️")
                    with phone_v_c2:
                        if st.button("📱 Verify Phone", key="btn_init_phone_verify", use_container_width=True):
                            if not valid_phone:
                                st.error(phone_msg)
                            else:
                                update_patient_details(patient_id, {"phone": acc_phone.strip()})
                                send_verification_otp("patient_phone", acc_phone.strip(), patient.get("full_name") or "User")
                                st.session_state.show_otp_ui_patient_phone = True
                                st.rerun()

                if st.session_state.get("show_otp_ui_patient_phone", False):
                    otp_store = st.session_state.get("otp_store_patient_phone", {})
                    st.info(f"📱 SMS verification code sent to **{acc_phone}**! *(Demo OTP: `{otp_store.get('code', '123456')}`)*")
                    otp_p_in, otp_p_btn = st.columns([2, 1])
                    with otp_p_in:
                        entered_p_otp = st.text_input("Enter 6-digit SMS OTP", key="input_phone_otp", max_chars=6)
                    with otp_p_btn:
                        if st.button("Confirm OTP", key="btn_confirm_phone_otp", use_container_width=True):
                            ok, msg = verify_entered_otp("patient_phone", entered_p_otp, patient_id)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                acc_age = st.number_input("Age", min_value=10, max_value=120, value=int(patient.get("age") or 21), key="set_acc_age")

            with acc_col2:
                email_val = str(st.session_state.patient_email or patient.get("email") or "")
                st.text_input("Email Address", value=email_val, disabled=True, help="Registered email address.")

                # Email verification status & trigger
                if is_email_verified:
                    st.markdown("🟢 **Email Verified & Confirmed** ✅")
                else:
                    email_v_c1, email_v_c2 = st.columns([1, 1])
                    with email_v_c1:
                        st.markdown("🟠 **Email Unverified** ⚠️")
                    with email_v_c2:
                        if st.button("✉️ Verify Email", key="btn_init_email_verify", use_container_width=True):
                            send_verification_otp("email", email_val, patient.get("full_name") or "User")
                            st.session_state.show_otp_ui_email = True
                            st.rerun()

                if st.session_state.get("show_otp_ui_email", False):
                    otp_store = st.session_state.get("otp_store_email", {})
                    st.info(f"📩 Verification email sent to **{email_val}**! *(Demo OTP: `{otp_store.get('code', '123456')}`)*")
                    otp_e_in, otp_e_btn = st.columns([2, 1])
                    with otp_e_in:
                        entered_e_otp = st.text_input("Enter 6-digit Email OTP", key="input_email_otp", max_chars=6)
                    with otp_e_btn:
                        if st.button("Confirm Code", key="btn_confirm_email_otp", use_container_width=True):
                            ok, msg = verify_entered_otp("email", entered_e_otp, patient_id)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                acc_dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=patient.get("date_of_birth") or "", key="set_acc_dob", placeholder="YYYY-MM-DD")
                acc_city = st.text_input("City", value=patient.get("city") or "", key="set_acc_city")
                acc_state = st.text_input("State", value=patient.get("state") or "", key="set_acc_state")

            loc_col1, loc_col2 = st.columns(2)
            with loc_col1:
                acc_locality = st.text_input("Locality / Area", value=patient.get("locality") or "", key="set_acc_locality")
            with loc_col2:
                acc_pincode = st.text_input("Pincode", value=patient.get("pincode") or "", key="set_acc_pincode")

            acc_note = st.text_area(
                "Personal Pre-Session Notes (Optional notes or topics you'd like Lia to keep in mind)",
                value=patient.get("pre_session_note") or "",
                key="set_acc_notes"
            )

            if st.button("💾 Save Profile Changes", key="btn_save_profile_settings", use_container_width=True):
                old_phone = str(patient.get("phone") or "").strip()
                new_phone = acc_phone.strip()
                updates = {
                    "full_name": acc_name.strip(),
                    "phone": new_phone,
                    "age": int(acc_age),
                    "date_of_birth": acc_dob.strip(),
                    "city": acc_city.strip(),
                    "state": acc_state.strip(),
                    "locality": acc_locality.strip(),
                    "pincode": acc_pincode.strip(),
                    "pre_session_note": acc_note.strip()
                }
                # If phone number changed, reset verification
                if old_phone and new_phone != old_phone:
                    updates["phone_verified"] = 0

                success = update_patient_details(patient_id, updates)
                if success:
                    st.session_state.patient_name = acc_name.strip()
                    st.success("✅ Profile information updated successfully! 🌸")
                    st.rerun()
                else:
                    st.error("Unable to save profile changes. Please try again.")

            st.write("")
            st.divider()

            # Security / Change Password Section
            st.markdown("### 🔒 Security & Password")
            st.caption("Change your account password below.")

            pwd_col1, pwd_col2 = st.columns(2)
            with pwd_col1:
                cur_pwd = st.text_input("Current Password", type="password", key="set_cur_pwd")
            with pwd_col2:
                new_pwd = st.text_input("New Password (min 6 characters)", type="password", key="set_new_pwd")
                confirm_pwd = st.text_input("Confirm New Password", type="password", key="set_confirm_pwd")

            if st.button("🔑 Update Password", key="btn_update_password", use_container_width=True):
                if not cur_pwd or not new_pwd:
                    st.warning("Please fill out all password fields.")
                elif new_pwd != confirm_pwd:
                    st.error("New password and confirmation do not match.")
                elif len(new_pwd) < 6:
                    st.error("New password must be at least 6 characters.")
                else:
                    ok, msg = change_patient_password(patient_id, cur_pwd, new_pwd)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

    # ==========================================================
    # TAB 2: 🆘 EMERGENCY CONTACTS
    # ==========================================================
    with tab_emergency:
        st.markdown("### 🆘 Trusted Emergency Safety Contact")
        st.write(
            "Antara is a self-help wellness tool. If you ever express acute distress, crisis, or ask for help, "
            "Antara can automatically dispatch an urgent SMS notification to your trusted contact."
        )

        is_tc_verified = bool(patient.get("trusted_contact_verified", 0))

        emg_col1, emg_col2 = st.columns(2)
        with emg_col1:
            emg_name = st.text_input(
                "Trusted Contact Full Name",
                value=patient.get("trusted_contact_name") or "",
                key="set_emg_name",
                placeholder="e.g., Mom, Sarah, Alex..."
            )
            rel_options = ["Parent", "Partner / Spouse", "Sibling", "Close Friend", "Therapist / Counselor", "Guardian", "Relative", "Other"]
            cur_rel = patient.get("trusted_contact_relationship") or "Parent"
            rel_idx = rel_options.index(cur_rel) if cur_rel in rel_options else 0
            emg_rel = st.selectbox("Relationship to you", rel_options, index=rel_idx, key="set_emg_rel")

        with emg_col2:
            emg_phone = st.text_input(
                "Contact Phone Number (Include country code e.g. +91XXXXXXXXXX)",
                value=patient.get("trusted_contact_number") or "",
                key="set_emg_phone",
                placeholder="+91..."
            )

            # Format check
            valid_tc, tc_msg = validate_phone_format(emg_phone)
            if emg_phone and not valid_tc:
                st.caption(f"⚠️ {tc_msg}")

            # Contact number verification badge & trigger
            if is_tc_verified and emg_phone.strip() == str(patient.get("trusted_contact_number") or "").strip() and emg_phone.strip():
                st.markdown("🟢 **Contact Number Verified & Safety Link Active** ✅")
            else:
                tc_v_c1, tc_v_c2 = st.columns([1, 1])
                with tc_v_c1:
                    st.markdown("🟠 **Contact Unverified** ⚠️")
                with tc_v_c2:
                    if st.button("📲 Verify Number", key="btn_init_tc_verify", use_container_width=True):
                        if not valid_tc:
                            st.error(tc_msg)
                        else:
                            update_patient_details(patient_id, {
                                "trusted_contact_name": emg_name.strip(),
                                "trusted_contact_number": emg_phone.strip(),
                                "trusted_contact_relationship": emg_rel
                            })
                            send_verification_otp("trusted_phone", emg_phone.strip(), patient.get("full_name") or "User")
                            st.session_state.show_otp_ui_trusted_phone = True
                            st.rerun()

            if st.session_state.get("show_otp_ui_trusted_phone", False):
                otp_store = st.session_state.get("otp_store_trusted_phone", {})
                st.info(f"📲 Confirmation SMS sent to **{emg_name} ({emg_phone})**! *(Demo OTP: `{otp_store.get('code', '123456')}`)*")
                otp_tc_in, otp_tc_btn = st.columns([2, 1])
                with otp_tc_in:
                    entered_tc_otp = st.text_input("Enter 6-digit Contact OTP", key="input_tc_otp", max_chars=6)
                with otp_tc_btn:
                    if st.button("Confirm Contact", key="btn_confirm_tc_otp", use_container_width=True):
                        ok, msg = verify_entered_otp("trusted_phone", entered_tc_otp, patient_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            emg_consent = st.checkbox(
                "I give consent for Antara to dispatch an emergency SMS alert to this contact if severe distress is detected",
                value=bool(patient.get("emergency_alert_consent", 1)),
                key="set_emg_consent"
            )
            emg_agree = st.checkbox(
                "I have informed this person that they are listed as my emergency contact",
                value=bool(patient.get("trusted_contact_agreement", 1)),
                key="set_emg_agree"
            )

        decline_reason = ""
        if not emg_consent:
            decline_reason = st.text_input(
                "Reason for declining automated emergency alert (Optional)",
                value=patient.get("reason_for_declining") or "",
                key="set_emg_decline"
            )

        if st.button("💾 Save Emergency Contact Details", key="btn_save_emergency_contact", use_container_width=True):
            if patient_id:
                old_tc_phone = str(patient.get("trusted_contact_number") or "").strip()
                new_tc_phone = emg_phone.strip()
                emg_updates = {
                    "trusted_contact_name": emg_name.strip(),
                    "trusted_contact_relationship": emg_rel,
                    "trusted_contact_number": new_tc_phone,
                    "emergency_alert_consent": 1 if emg_consent else 0,
                    "trusted_contact_agreement": 1 if emg_agree else 0,
                    "reason_for_declining": decline_reason.strip()
                }
                # Reset verification if number changed
                if old_tc_phone and new_tc_phone != old_tc_phone:
                    emg_updates["trusted_contact_verified"] = 0

                success = update_patient_details(patient_id, emg_updates)
                if success:
                    st.success("✅ Emergency contact details saved! 💗")
                    st.rerun()
                else:
                    st.error("Unable to save emergency contact.")
            else:
                st.info("Sign in to save this permanently.")

        st.write("")
        st.divider()

        st.markdown("#### 📲 Test Emergency Dispatch")
        st.caption("Verify your contact number with a live test alert (Twilio or verified safety receipt).")

        if st.button("🚨 Send Test Alert to My Contact", key="btn_send_test_alert", use_container_width=True):
            target_phone = emg_phone.strip() or patient.get("trusted_contact_number")
            target_name = emg_name.strip() or patient.get("trusted_contact_name") or "Emergency Contact"
            if not target_phone:
                st.warning("Please enter a valid phone number above first.")
            else:
                with st.spinner("Dispatching test alert..."):
                    res = send_emergency_sms(
                        patient_id=str(patient_id or "TEST-USER"),
                        session_id=str(st.session_state.session_id or "TEST-SESSION"),
                        contact_name=target_name,
                        contact_number=target_phone,
                        user_name=str(st.session_state.patient_name or "Antara User"),
                        reason="Test SMS Notification from Settings"
                    )
                if res.get("success"):
                    st.success(f"✅ Alert dispatched! Alert ID: `{res.get('alert_id')}` via `{res.get('provider')}` at {res.get('timestamp')}")
                else:
                    st.error(f"❌ Failed: {res.get('error')}")

        st.write("")
        st.markdown("#### 📞 24/7 Crisis Helplines Directory")
        st.caption("Confidential, free, professional support available 24 hours a day.")

        hl_col1, hl_col2 = st.columns(2)
        with hl_col1:
            st.markdown("""
            - **Tele-MANAS (Govt. of India)**: `14416` or `1800-891-4416`
            - **Vandrevala Foundation**: `9999 666 555`
            - **KIRAN Mental Health**: `1800-599-0019`
            """)
        with hl_col2:
            st.markdown("""
            - **NIMHANS Psychosocial Helpline**: `080-46110007`
            - **AASRA Suicide Prevention**: `9820466726`
            - **Emergency Ambulance**: `112`
            """)

    # ==========================================================
    # TAB 3: 🎨 THEME & VISUALS
    # ==========================================================
    with tab_theme:
        st.markdown("### 🎨 Theme & Visual Preferences")
        st.caption("Tailor Antara's appearance to whatever feels most relaxing and comfortable for your eyes.")

        cur_theme = st.session_state.get("app_theme", "⚙️ System")
        theme_options = ["⚙️ System", "☀️ Light", "🌙 Dark"]
        t_idx = theme_options.index(cur_theme) if cur_theme in theme_options else 0

        selected_theme = st.radio(
            "Select Appearance Theme:",
            theme_options,
            index=t_idx,
            key="set_theme_radio",
            horizontal=True
        )
        if selected_theme != cur_theme:
            st.session_state.app_theme = selected_theme
            st.rerun()

        st.write("")
        st.info("✨ **Gradual Fade Transition:** Antara uses smooth 0.85s keyframe bloom transitions for natural, gentle theme switching that doesn't jar your eyes.")

        st.markdown("#### 👁️ Text & Readability")
        font_scale = st.radio(
            "Reading Size / Legibility:",
            ["Normal (Default)", "Comfortable (+10%)", "Large (+20%)"],
            index=0,
            key="set_font_scale_radio",
            horizontal=True
        )
        st.session_state.font_scale = font_scale

        st.markdown("#### 🎨 Live Palette Preview")
        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            st.markdown("""
            <div style="padding:14px; border-radius:12px; border:1px solid #d8c9ed; margin-bottom:10px;">
                <p style="margin:0; font-weight:600; font-size:13px;">Assistant Message Bubble</p>
                <p style="margin:6px 0 0 0; font-size:14px;">"Take all the time you need. I'm right here with you 🌸"</p>
            </div>
            """, unsafe_allow_html=True)
        with preview_col2:
            st.markdown("""
            <div style="padding:14px; border-radius:12px; border:1px solid #c7d2fe; margin-bottom:10px; text-align:right;">
                <p style="margin:0; font-weight:600; font-size:13px;">User Message Bubble</p>
                <p style="margin:6px 0 0 0; font-size:14px;">"I'm feeling a little calmer now, thank you."</p>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================================
    # TAB 4: 💬 CONVERSATION PREFERENCES
    # ==========================================================
    with tab_conv:
        st.markdown("### 💬 Conversation & Chat Experience")
        st.caption("Set your default chat durations, pacing, and interaction style.")

        dur_col1, dur_col2 = st.columns(2)
        with dur_col1:
            def_dur = st.session_state.get("time_available") or "5 minutes"
            dur_idx = TIME_OPTIONS.index(def_dur) if def_dur in TIME_OPTIONS else 0
            pref_dur = st.selectbox("Default Check-in Duration", TIME_OPTIONS, index=dur_idx, key="set_pref_duration")

            pref_mode = st.radio(
                "Conversation Depth & Style",
                list(CONVERSATION_MODES.keys()),
                index=1,
                key="set_pref_mode"
            )

        with dur_col2:
            pref_checkin = st.radio(
                "Engagement & Fatigue Check-ins",
                [
                    "Standard (Periodic check-ins after 3 and 8 questions)",
                    "Frequent (Check in every 3 questions)",
                    "Only On-Demand (Only when I click 'Need a break?')"
                ],
                index=0,
                key="set_pref_checkin_freq"
            )

            pref_quick = st.checkbox("Show quick-reply buttons under questions", value=True, key="set_pref_quick_opts")
            pref_ack = st.checkbox("Show Lia's empathetic reflection after answers", value=True, key="set_pref_ack")

        if st.button("💾 Save Conversation Preferences", key="btn_save_conv_prefs", use_container_width=True):
            st.session_state.time_available = pref_dur
            st.session_state.conversation_mode = pref_mode
            st.session_state.pref_checkin_freq = pref_checkin
            st.session_state.pref_quick_opts = pref_quick
            st.session_state.pref_ack = pref_ack
            st.success("✅ Conversation preferences saved!")

    # ==========================================================
    # TAB 5: 🛡️ PRIVACY & DATA MANAGEMENT
    # ==========================================================
    with tab_privacy:
        st.markdown("### 🛡️ Privacy & Confidentiality")
        st.write(
            "Antara is built from the ground up for strict confidentiality. "
            "All sessions, reflections, and contact details are stored **locally in your private SQLite database** "
            "with PBKDF2 password encryption. Your conversations are never sold or sent to third-party ad networks."
        )

        sessions = get_history() if st.session_state.logged_in else []
        completed_sessions = [s for s in sessions if s.get("status") == "completed"]
        in_progress_sessions = [s for s in sessions if s.get("status") == "in_progress"]

        st.markdown("#### 📊 Your Data Footprint")
        stat_c1, stat_c2, stat_c3 = st.columns(3)
        with stat_c1:
            st.metric("Total Sessions", len(sessions))
        with stat_c2:
            st.metric("Completed", len(completed_sessions))
        with stat_c3:
            st.metric("In Progress", len(in_progress_sessions))

        st.write("")
        st.markdown("#### 📥 Export My Conversation History")
        st.caption("You own your wellness journey. Download a full copy of your transcripts at any time.")

        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            # JSON Export
            json_export_data = {
                "patient_id": patient_id,
                "patient_name": st.session_state.patient_name,
                "exported_at": datetime.now().isoformat(),
                "total_sessions": len(sessions),
                "sessions": sessions
            }
            st.download_button(
                label="📥 Download JSON Export",
                data=json.dumps(json_export_data, indent=2),
                file_name=f"antara_wellness_data_{patient_id or 'guest'}.json",
                mime="application/json",
                use_container_width=True
            )

        with exp_c2:
            # Plaintext summary
            txt_lines = [
                f"Antara Wellness Companion — Personal Transcript Export",
                f"Patient ID: {patient_id}",
                f"Exported At: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
                f"Total Sessions: {len(sessions)}",
                "=" * 50,
                ""
            ]
            for s in sessions:
                txt_lines.append(f"Session ID: {s.get('session_id')} | Status: {s.get('status')} | Date: {s.get('created_at')}")
                txt_lines.append("-" * 40)
            txt_content = "\n".join(txt_lines)

            st.download_button(
                label="📄 Download Plaintext Summary (.txt)",
                data=txt_content,
                file_name=f"antara_summary_{patient_id or 'guest'}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.write("")
        st.divider()

        st.markdown("#### 🧹 Session Clean-up")
        if st.session_state.started and not st.session_state.submitted:
            st.warning("You currently have an active in-progress conversation.")
            if st.button("🗑️ Discard In-Progress Session & Return to Dashboard", key="btn_discard_active_session"):
                st.session_state.started = False
                st.session_state.show_dashboard = True
                st.session_state.show_settings = False
                st.rerun()

    # ==========================================================
    # TAB 6: ℹ️ ABOUT ANTARA
    # ==========================================================
    with tab_about:
        st.markdown("### ℹ️ About Antara")
        st.markdown("""
        **Antara** is a conversational self-help and emotional wellness companion.
        Designed with empathy, cognitive reframing, and crisis safety at its core, 
        Antara provides a gentle, unhurried space for daily emotional reflection and self-compassion.

        ---

        #### ⚙️ Technical System Info
        - **Version**: `Antara v2.4 (NLP Self-Help Edition)`
        - **NLP Engine**: Hybrid Architecture (Local LLM + Resilient Fallback Heuristics)
        - **Storage**: Local SQLite Database with PBKDF2 Password Hashing
        - **Emergency Alert**: Automated Twilio SMS Gateway & Fallback
        - **Design System**: Smooth CSS Keyframe Bloom & Multi-Theme Engine

        ---

        #### 💡 Disclaimer
        Antara is designed strictly as a supportive self-help conversational tool. 
        It does not diagnose medical or psychological conditions, nor does it provide psychiatric medical advice. 
        In emergency situations, always reach out to real-world healthcare professionals or local emergency helplines.
        """)


# ==========================================================
# 27. MAIN APPLICATION
# ==========================================================

show_sidebar()

if st.session_state.get("show_settings", False):

    show_settings_page()

elif not st.session_state.logged_in:

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