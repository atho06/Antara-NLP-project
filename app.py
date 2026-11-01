import streamlit as st
import re
import html
import json
import uuid

from datetime import datetime
from pathlib import Path

from question_bank import QUESTION_BANK
from llm_service import generate_followup
from crisis_detection import detect_crisis


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Antara",
    page_icon="🌷",
    layout="centered"
)


# ==================================================
# 2. CUSTOM DESIGN
# ==================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        120deg,
        #c9d8ff 0%,
        #ead5f5 50%,
        #ffcddd 100%
    );
}

.stApp p,
.stApp li,
.stApp label,
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #000000;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 6rem;
}

/* CHAT BUBBLES */

.bot-row {
    display: flex;
    justify-content: flex-start;
    margin: 18px 0;
}

.bot-bubble {
    background: #eeeaf1;
    color: #292633;
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
    background: #3979e8;
    color: white;
    padding: 13px 17px;
    border-radius: 16px 16px 5px 16px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

/* CHAT INPUT */

[data-testid="stChatInput"] {
    background: white;
    border-radius: 25px;
    border: 1px solid #c8b5e5;
}

/* BUTTONS */

.stButton > button,
.stDownloadButton > button {
    background: #ffffff !important;
    color: #29243a !important;
    border: 1px solid #d8b8e8 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    padding: 12px 18px !important;
    transition: 0.3s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #c9d8ff !important;
    color: #29243a !important;
    border: 1px solid #91b5f5 !important;
}

.stButton > button p,
.stDownloadButton > button p {
    color: #29243a !important;
}

/* EXPANDER */

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.35);
    border-radius: 12px;
}

/* DELETE BUTTON */

.st-key-delete-session-container .stButton > button:hover {
    background: #ffd6d6 !important;
    color: #a00000 !important;
    border: 1px solid #ef7777 !important;
}

.st-key-delete-session-container .stButton > button:hover p {
    color: #a00000 !important;
}

/* LOGIN CARD */

.login-card {
    background: rgba(255,255,255,0.75);
    padding: 35px;
    border-radius: 24px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0,0,0,0.06);
    margin-top: 35px;
}

.login-subtitle {
    color: #55516a;
    font-size: 16px;
}

.consent-card {
    background: rgba(255,255,255,0.75);
    padding: 25px;
    border-radius: 20px;
    margin-top: 20px;
}

/* HIDE FOOTER */

#MainMenu,
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. SESSION STORAGE
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

SESSION_FOLDER = BASE_DIR / "sessions"
SESSION_FOLDER.mkdir(exist_ok=True)

SESSION_FILE = SESSION_FOLDER / "antara_session.json"


def save_session():

    session_data = {
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

    temporary_file = SESSION_FILE.with_suffix(".tmp")

    with open(temporary_file, "w", encoding="utf-8") as file:

        json.dump(
            session_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    temporary_file.replace(SESSION_FILE)


def load_session():

    if not SESSION_FILE.exists():
        return None

    try:

        with open(SESSION_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError) as error:

        print("Session loading error:", error)

        return None


def delete_saved_session():

    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def auto_save():

    try:
        save_session()

    except OSError as error:

        st.error(
            "Unable to save your session. "
            "Please check your local storage."
        )

        print("Session saving error:", error)


# ==================================================
# 4. SESSION STATE
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
    "session_checked": False,
    "logged_in": False,
    "login_role": None,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 5. CHECK FOR PREVIOUS SESSION
# ==================================================

if not st.session_state.session_checked:

    saved_data = load_session()

    if (
        saved_data
        and saved_data.get("started")
        and not saved_data.get("submitted")
    ):

        st.session_state.show_recovery = True

    else:

        st.session_state.show_recovery = False

    st.session_state.session_checked = True


# ==================================================
# 6. COLLECT CORE QUESTIONS
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
    "yes", "no", "yeah", "yep", "nope",
    "okay", "ok", "fine", "good", "bad",
    "maybe", "sometimes", "always", "never",
    "nothing", "everything", "not sure",
    "i don't know", "dont know", "idk"
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
# 8. DISPLAY CHAT MESSAGES
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
        st.rerun()


# ==================================================
# 10. RESET SESSION
# ==================================================

def reset_session():

    delete_saved_session()

    logged_in = st.session_state.logged_in
    login_role = st.session_state.login_role

    for key, value in defaults.items():
        st.session_state[key] = value

    st.session_state.logged_in = logged_in
    st.session_state.login_role = login_role

    st.session_state.pop("antara_consent", None)

    st.session_state.session_checked = True
    st.session_state.show_recovery = False


# ==================================================
# 11. APPLICATION HEADER
# ==================================================

if st.session_state.logged_in:

    st.title("🌷 Antara")

    st.caption(
        "A space for your feelings, before therapy."
    )


# ==================================================
# 12. LOGIN PAGE
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

    # PATIENT LOGIN

    with patient_tab:

        st.markdown("### Welcome!")

        st.write(
            "Continue to your personal Antara conversation."
        )

        st.info(
            "You can start a new conversation or resume "
            "a locally saved session using your Session ID."
        )

        session_id_input = st.text_input(
            "Existing Session ID (optional)",
            placeholder="Example: ANT-20261031-2ABA9F"
        )

        if st.button(
            "Continue as Patient",
            use_container_width=True
        ):

            entered_id = session_id_input.strip()

            if entered_id:

                saved_data = load_session()

                if (
                    saved_data
                    and saved_data.get("session_id") == entered_id
                    and saved_data.get("started")
                    and not saved_data.get("submitted")
                ):

                    st.session_state.logged_in = True
                    st.session_state.login_role = "patient"
                    st.session_state.show_recovery = True

                    st.rerun()

                else:

                    st.error(
                        "No matching unfinished session was found. "
                        "Please check your Session ID."
                    )

            else:

                st.session_state.logged_in = True
                st.session_state.login_role = "patient"

                st.rerun()

    # THERAPIST LOGIN

    with therapist_tab:

        st.markdown("### Therapist Portal")

        st.write(
            "Access the therapist dashboard to review "
            "patient sessions and clinical reports."
        )

        st.text_input(
            "Email Address",
            placeholder="Enter your registered email"
        )

        st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.warning(
            "Therapist login is currently under development. "
            "It will be available once the Therapist Portal "
            "integration is completed."
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
# 13. SESSION RECOVERY
# ==================================================

elif st.session_state.show_recovery:

    st.info("We found an unfinished Antara session.")

    st.write(
        "Would you like to continue where you left off?"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Resume Previous Session",
            use_container_width=True
        ):

            saved_data = load_session()

            if saved_data:

                try:

                    responses = saved_data.get("responses", [])

                    if not isinstance(responses, list):
                        raise ValueError("Invalid response data")

                    st.session_state.started = saved_data.get(
                        "started", False
                    )

                    st.session_state.consent_given = saved_data.get(
                        "consent_given", False
                    )

                    st.session_state.session_id = saved_data.get(
                        "session_id"
                    )

                    st.session_state.current_question_index = saved_data.get(
                        "current_question_index", 0
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

                    if not st.session_state.session_id:

                        st.session_state.session_id = (
                            "ANT-"
                            + datetime.now().strftime("%Y%m%d")
                            + "-"
                            + uuid.uuid4().hex[:6].upper()
                        )

                    st.session_state.show_recovery = False

                    st.rerun()

                except (ValueError, TypeError, KeyError) as error:

                    st.error(
                        "The saved session could not be restored."
                    )

                    print("Recovery error:", error)

            else:

                st.warning("No saved session was found.")

    with col2:

        if st.button(
            "Start New Session",
            use_container_width=True
        ):

            reset_session()
            st.rerun()


# ==================================================
# 14. WELCOME AND CONSENT
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
    This prototype saves session information locally
    in application storage and allows you to download
    your responses as a JSON file.

    Local JSON storage is not encrypted. Avoid entering
    real identifying or highly sensitive personal
    information while testing this prototype.
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

            st.session_state.session_id = (
                "ANT-"
                + datetime.now().strftime("%Y%m%d")
                + "-"
                + uuid.uuid4().hex[:6].upper()
            )

            st.session_state.antara_consent = True

            auto_save()
            st.rerun()

        else:

            st.error(
                "Please provide your consent before continuing."
            )


# ==================================================
# 15. MAIN CHAT INTERFACE
# ==================================================

elif (
    st.session_state.logged_in
    and st.session_state.started
    and not st.session_state.submitted
):

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

        # HANDLE PENDING AI FOLLOW-UP

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
                st.rerun()


# ==================================================
# 16. FINAL THANK-YOU SCREEN
# ==================================================

elif st.session_state.submitted:

    st.markdown("""
<div style="background:rgba(255,255,255,0.65);padding:35px 25px;border-radius:22px;text-align:center;margin-top:25px;box-shadow:0 4px 15px rgba(0,0,0,0.06);">
<div style="font-size:55px;">🌷</div>
<h1 style="color:#29243a;">Thank You</h1>
<p style="color:#55516a;font-size:17px;">Thank you for sharing your feelings with honesty. Every feeling deserves to be heard.</p>
<p style="color:#55516a;font-size:15px;">Your Antara session has ended.</p>
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

    # JSON DATA

    session_data = {
        "application": "Antara",
        "session_id": st.session_state.session_id,
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

    # THERAPIST PORTAL

    st.divider()

    st.markdown("### 🩷 Therapist Portal")

    st.info(
        "Your therapist portal integration is currently pending. "
        "Once connected, your session data can be transferred "
        "for therapist review."
    )

    # START NEW SESSION

    st.divider()

    st.markdown("### 🌷 Start Again")

    st.write(
        "Whenever you're ready, you can begin a new session."
    )

    if st.button(
        "🌷 Start New Session",
        use_container_width=True
    ):

        reset_session()
        st.rerun()

    # DELETE LOCAL SESSION

    with st.expander("🗑️ Delete locally saved session"):

        st.warning(
            "This deletes the locally saved session from "
            "Antara's application storage. It does not delete "
            "JSON files you have already downloaded."
        )

        with st.container(key="delete-session-container"):

            if st.button(
                "Delete Local Session",
                type="secondary",
                use_container_width=True
            ):

                reset_session()
                st.rerun()