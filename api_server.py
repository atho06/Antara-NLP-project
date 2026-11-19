"""
Antara NLP Mobile Backend API
FastAPI REST API powering the Antara Flutter Mobile Application.
"""

import uuid
import time
import random
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

import database
from nlp_engine.emotion_analyzer import EmotionAnalyzer
from nlp_engine.crisis_classifier import CrisisClassifier
from crisis_detection import detect_crisis
from emergency_service import send_emergency_sms
from question_bank import QUESTION_BANK

# Initialize FastAPI App
app = FastAPI(
    title="Antara Mobile API",
    description="REST API for Antara Emotional Well-being Mobile Companion",
    version="2.0.0",
)

# Allow Cross-Origin Requests from mobile apps, emulators, and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure database tables exist
database.init_db()

# Initialize NLP Engines
emotion_analyzer = EmotionAnalyzer()
crisis_classifier = CrisisClassifier()

# In-memory session tracking for active chats
active_sessions: Dict[str, Dict[str, Any]] = {}
active_otps: Dict[str, str] = {}

# Continuous reflection bank for dynamic questions
CONTINUOUS_REFLECTION_QUESTIONS = [
    {"category": "gratitude", "text": "Is there one small thing that brought a tiny moment of peace or relief to you recently?"},
    {"category": "emotions", "text": "When you feel stressed or low, where in your body do you notice that tension the most?"},
    {"category": "coping", "text": "What is a gentle activity or routine that helps you feel even slightly more grounded?"},
    {"category": "self_compassion", "text": "If a dear friend were in your exact shoes right now, what kind words would you offer them?"},
    {"category": "comfort", "text": "What is a favorite song, book, show, or warm drink that always brings you a sense of comfort?"},
    {"category": "boundaries", "text": "Is there any situation or obligation right now where you feel you need to set a gentler boundary for yourself?"},
    {"category": "reflection", "text": "What is something on your mind right now that you haven't had a chance to say out loud?"},
    {"category": "growth", "text": "Looking back over the past year, in what ways have you grown or learned more about what you need?"},
    {"category": "grounding", "text": "If you could pause everything for an hour and do anything purely for your peace of mind, what would it be?"},
    {"category": "processing", "text": "Is there a recurring worry or thought pattern you notice yourself returning to often?"},
    {"category": "peace", "text": "What does feeling truly at peace look or feel like for you?"},
    {"category": "hope", "text": "What is one small hope or quiet wish you have for tomorrow?"}
]

# ----------------- Pydantic Schemas -----------------

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = ""
    trusted_contact_name: Optional[str] = ""
    trusted_contact_phone: Optional[str] = ""
    preferred_theme: Optional[str] = "lavender_peace"

class LoginRequest(BaseModel):
    email: str
    password: str

class SendOtpRequest(BaseModel):
    patient_id: str
    target_type: str  # "email", "phone", or "trusted_contact"
    contact_value: str

class VerifyOtpRequest(BaseModel):
    patient_id: str
    target_type: str  # "email", "phone", or "trusted_contact"
    otp_code: str

class UpdateProfileRequest(BaseModel):
    patient_id: str
    full_name: str
    phone: Optional[str] = ""
    trusted_contact_name: Optional[str] = ""
    trusted_contact_phone: Optional[str] = ""
    preferred_theme: Optional[str] = "lavender_peace"

class ChangePasswordRequest(BaseModel):
    patient_id: str
    current_password: str
    new_password: str

class StartSessionRequest(BaseModel):
    patient_id: str
    duration_minutes: int = 5  # 5, 10, 15, 20, 0 (unlimited)
    category: Optional[str] = "daily_routine"

class SendMessageRequest(BaseModel):
    session_id: str
    patient_id: str
    message: str
    elapsed_seconds: int = 0

class EndSessionRequest(BaseModel):
    session_id: str
    patient_id: str

class TriggerSosRequest(BaseModel):
    patient_id: str
    current_message: Optional[str] = "Manual SOS alert triggered by user."

# ----------------- Helper Functions -----------------

def clean_patient_dict(user: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(user)
    if "password_hash" in safe:
        del safe["password_hash"]
    if "salt" in safe:
        del safe["salt"]
    return safe

def generate_dynamic_question(existing_ids: set, category: str = "daily_routine") -> Dict[str, str]:
    # Check question bank
    cat_data = QUESTION_BANK.get(category, {})
    for item in cat_data.get("questions", []):
        if item["id"] not in existing_ids:
            existing_ids.add(item["id"])
            return {"id": item["id"], "text": item["question"], "category": category}

    # Search other categories
    for cat_name, data in QUESTION_BANK.items():
        for item in data.get("questions", []):
            if item["id"] not in existing_ids:
                existing_ids.add(item["id"])
                return {"id": item["id"], "text": item["question"], "category": cat_name}

    # Search reflection catalog
    for idx, prompt in enumerate(CONTINUOUS_REFLECTION_QUESTIONS):
        pid = f"REFLECT_{idx + 1}"
        if pid not in existing_ids:
            existing_ids.add(pid)
            return {"id": pid, "text": prompt["text"], "category": prompt.get("category", "reflection")}

    # Fallback
    dyn_id = f"DYN_{len(existing_ids) + 1}"
    existing_ids.add(dyn_id)
    return {
        "id": dyn_id,
        "text": "What is one gentle or forgiving thing you can do for yourself today?",
        "category": "self_compassion"
    }

# ----------------- API Endpoints -----------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Antara NLP Mobile Backend",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# --- Auth Endpoints ---

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if not req.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required")

    success = database.register_patient(
        full_name=req.full_name.strip(),
        email=req.email.strip().lower(),
        password=req.password,
        contact_number=req.phone.strip() if req.phone else "",
        trusted_contact_name=req.trusted_contact_name.strip() if req.trusted_contact_name else "",
        trusted_contact_number=req.trusted_contact_phone.strip() if req.trusted_contact_phone else ""
    )

    if not success:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    # Fetch created user
    user = database.authenticate_patient(req.email.strip().lower(), req.password)
    return {
        "status": "success",
        "message": "Account created successfully",
        "user": clean_patient_dict(user)
    }

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = database.authenticate_patient(req.email.strip().lower(), req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "status": "success",
        "message": "Login successful",
        "user": clean_patient_dict(user)
    }

# --- Verification & OTP Endpoints ---

@app.post("/api/auth/send-otp")
def send_otp(req: SendOtpRequest):
    otp = f"{random.randint(100000, 999999)}"
    key = f"{req.patient_id}_{req.target_type}"
    active_otps[key] = otp

    # In production, this would send an SMS / Email gateway message.
    # For instant mobile testing and demo, the OTP is returned directly.
    return {
        "status": "success",
        "message": f"Verification code generated for {req.target_type}",
        "otp_code": otp,
        "target": req.contact_value
    }

@app.post("/api/auth/verify-otp")
def verify_otp(req: VerifyOtpRequest):
    key = f"{req.patient_id}_{req.target_type}"
    expected = active_otps.get(key)

    if not expected or expected.strip() != req.otp_code.strip():
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    field_map = {
        "email": "email_verified",
        "phone": "phone_verified",
        "trusted_contact": "trusted_contact_verified"
    }

    column = field_map.get(req.target_type)
    if column:
        database.set_patient_verification(req.patient_id, column, 1)

    # Clean up OTP
    active_otps.pop(key, None)

    updated_user = database.get_patient_details(req.patient_id)
    return {
        "status": "success",
        "message": f"{req.target_type.replace('_', ' ').capitalize()} verified successfully",
        "user": clean_patient_dict(updated_user) if updated_user else None
    }

# --- Profile Endpoints ---

@app.get("/api/user/profile")
def get_profile(patient_id: str = Query(...)):
    user = database.get_patient_details(patient_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "user": clean_patient_dict(user)}

@app.put("/api/user/profile")
def update_profile(req: UpdateProfileRequest):
    updates = {
        "full_name": req.full_name,
        "contact_number": req.phone or "",
        "trusted_contact_name": req.trusted_contact_name or "",
        "trusted_contact_number": req.trusted_contact_phone or ""
    }
    success = database.update_patient_details(
        patient_id=req.patient_id,
        updates=updates
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update profile")

    user = database.get_patient_details(req.patient_id)
    return {"status": "success", "user": clean_patient_dict(user)}

@app.post("/api/user/change-password")
def change_password(req: ChangePasswordRequest):
    success = database.change_patient_password(
        patient_id=req.patient_id,
        current_password=req.current_password,
        new_password=req.new_password
    )
    if not success:
        raise HTTPException(status_code=400, detail="Current password incorrect or update failed")

    return {"status": "success", "message": "Password changed successfully"}

# --- Chat & Session Endpoints ---

@app.post("/api/session/start")
def start_session(req: StartSessionRequest):
    session_id = f"SESS_{uuid.uuid4().hex[:10]}"
    target_seconds = req.duration_minutes * 60 if req.duration_minutes > 0 else 0

    existing_ids = set()
    first_q = generate_dynamic_question(existing_ids, req.category or "daily_routine")

    active_sessions[session_id] = {
        "session_id": session_id,
        "patient_id": req.patient_id,
        "duration_minutes": req.duration_minutes,
        "target_seconds": target_seconds,
        "start_time": time.time(),
        "category": req.category or "daily_routine",
        "existing_ids": existing_ids,
        "current_question": first_q,
        "responses": [],
        "emotions_log": [],
        "is_completed": False
    }

    return {
        "status": "success",
        "session_id": session_id,
        "initial_message": f"Hello, I am Antara 🌷. I am here to listen with full care, without any judgment. Let's begin whenever you are ready.",
        "first_question": first_q,
        "target_seconds": target_seconds,
        "started_at": datetime.now().isoformat()
    }

@app.post("/api/session/message")
def send_message(req: SendMessageRequest):
    sess = active_sessions.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Active session not found")

    user_text = req.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # 1. Crisis & Safety Assessment
    crisis_result = crisis_classifier.check_for_crisis(user_text)
    is_crisis = crisis_result.get("is_crisis", False) or detect_crisis(user_text)

    if is_crisis:
        # Trigger emergency alert if trusted contact is configured
        patient = database.get_patient_details(req.patient_id)
        if patient and patient.get("trusted_contact_phone"):
            send_emergency_sms(
                patient_name=patient.get("full_name", "Antara User"),
                trusted_contact_phone=patient["trusted_contact_phone"],
                trusted_contact_name=patient.get("trusted_contact_name", "Trusted Contact"),
                crisis_message=user_text
            )

        safety_msg = crisis_result.get("safety_response") or (
            "I hear how much pain you are carrying right now, and I want to make sure you are safe. "
            "Please connect immediately with someone who can support you:\n\n"
            "• Tele-MANAS: 14416 (24/7, Toll-Free)\n"
            "• KIRAN Mental Health Helpline: 1800-599-0019\n"
            "• Vandrevala Foundation: +91 9999 666 555\n"
            "• International Helpline: 988"
        )

        return {
            "status": "crisis_detected",
            "reply": safety_msg,
            "is_crisis": True,
            "next_question": None,
            "is_time_up": True,
            "allow_continuation": False
        }

    # 2. NLP Emotion Analysis
    emotion_result = emotion_analyzer.score_text_emotions(user_text)
    primary_emotion = emotion_result.get("primary_emotion", "calm_grounded")
    valence = emotion_result.get("valence", 0.0)

    # Log response
    sess["responses"].append({
        "question_id": sess["current_question"]["id"],
        "question_text": sess["current_question"]["text"],
        "answer": user_text,
        "emotion": primary_emotion,
        "valence": valence,
        "timestamp": datetime.now().isoformat()
    })
    sess["emotions_log"].append(primary_emotion)

    # 3. Check Overwhelmed / Fatigue phrases
    lower_text = user_text.lower()
    fatigue_indicators = ["tired", "bored", "overwhelmed", "too much", "stop", "pause", "don't want to answer", "exhausted"]
    user_overwhelmed = any(ind in lower_text for ind in fatigue_indicators)

    # 4. Clock-time duration check
    now = time.time()
    elapsed = int(now - sess["start_time"])
    target = sess["target_seconds"]
    time_is_up = (target > 0 and elapsed >= target)

    # Build gentle response acknowledgement
    gentle_prefixes = [
        "Thank you for sharing that with me.",
        "I hear you, and it makes complete sense that you feel this way.",
        "Thank you for opening up—it takes courage to reflect like this.",
        "I appreciate you expressing that so honestly."
    ]
    ack = random.choice(gentle_prefixes)

    # If time is up or user seems overwhelmed
    if time_is_up or user_overwhelmed:
        if user_overwhelmed:
            prompt_text = "I notice this might be feeling a bit heavy or overwhelming. Remember, there is zero pressure here. Would you like to take a break and wrap up our session, or would you like to continue talking?"
        else:
            prompt_text = f"We have reached your chosen time ({sess['duration_minutes']} min). You did great today. Would you like to wrap up our session, or continue talking a little longer?"

        return {
            "status": "continuation_check",
            "reply": f"{ack}\n\n{prompt_text}",
            "is_time_up": True,
            "user_overwhelmed": user_overwhelmed,
            "is_crisis": False,
            "allow_continuation": True,
            "elapsed_seconds": elapsed,
            "emotion_snapshot": {
                "primary_emotion": primary_emotion,
                "valence": valence
            }
        }

    # 5. Generate Next Question
    next_q = generate_dynamic_question(sess["existing_ids"], sess["category"])
    sess["current_question"] = next_q

    return {
        "status": "success",
        "reply": ack,
        "next_question": next_q,
        "is_time_up": False,
        "is_crisis": False,
        "allow_continuation": False,
        "elapsed_seconds": elapsed,
        "remaining_seconds": max(0, target - elapsed) if target > 0 else 0,
        "emotion_snapshot": {
            "primary_emotion": primary_emotion,
            "valence": valence
        }
    }

@app.post("/api/session/end")
def end_session(req: EndSessionRequest):
    sess = active_sessions.get(req.session_id)
    if not sess:
        # Check database if session already ended
        saved = database.get_patient_session(req.session_id)
        if saved:
            return {"status": "success", "session": saved}
        raise HTTPException(status_code=404, detail="Session not found")

    sess["is_completed"] = True

    # Determine dominant emotion
    emotions = sess["emotions_log"]
    dominant_emotion = "calm_grounded"
    if emotions:
        dominant_emotion = max(set(emotions), key=emotions.count)

    # Compute supportive reflection summary
    num_exchanges = len(sess["responses"])
    summary_text = (
        f"In today's {sess['duration_minutes']}-minute session, you explored {num_exchanges} thoughtful reflections. "
        f"Your emotional tone centered around {dominant_emotion.replace('_', ' ')}. "
        f"Thank you for showing up for yourself and taking this time to listen inward."
    )

    # Save to SQLite database
    try:
        database.save_patient_session(
            patient_id=req.patient_id,
            session_id=sess["session_id"],
            session_data={
                "duration_minutes": sess["duration_minutes"],
                "category": sess["category"],
                "responses": sess["responses"],
                "dominant_emotion": dominant_emotion,
                "summary": summary_text,
                "completed_at": datetime.now().isoformat()
            }
        )
        database.complete_patient_session(req.patient_id, sess["session_id"])
    except Exception as e:
        print("Note: saving session record:", e)

    # Clean up from active memory
    active_sessions.pop(req.session_id, None)

    return {
        "status": "success",
        "message": "Session completed successfully",
        "session_summary": {
            "session_id": req.session_id,
            "duration_minutes": sess["duration_minutes"],
            "dominant_emotion": dominant_emotion,
            "exchanges_count": num_exchanges,
            "summary": summary_text,
            "affirmation": "Be gentle with yourself as you move through the rest of your day. Every small moment of reflection matters. 🌸"
        }
    }

@app.get("/api/session/history")
def session_history(patient_id: str = Query(...)):
    sessions = database.get_patient_sessions(patient_id)
    return {
        "status": "success",
        "sessions": sessions or []
    }

@app.post("/api/emergency/sos")
def trigger_sos(req: TriggerSosRequest):
    patient = database.get_patient_details(req.patient_id)
    contact_phone = patient.get("trusted_contact_phone") if patient else None
    contact_name = patient.get("trusted_contact_name", "Trusted Contact") if patient else "Trusted Contact"
    patient_name = patient.get("full_name", "Antara User") if patient else "Antara User"

    sent = False
    if contact_phone:
        sent = send_emergency_sms(
            patient_name=patient_name,
            trusted_contact_phone=contact_phone,
            trusted_contact_name=contact_name,
            crisis_message=req.current_message or "Manual SOS Triggered from Antara Mobile App"
        )

    return {
        "status": "success",
        "message": "Emergency SOS triggered",
        "alert_dispatched": sent,
        "trusted_contact_phone": contact_phone,
        "hotlines": [
            {"name": "Tele-MANAS (Govt. of India)", "number": "14416"},
            {"name": "KIRAN Mental Health", "number": "1800-599-0019"},
            {"name": "Vandrevala Foundation", "number": "+91 9999 666 555"},
            {"name": "Emergency Medical Services", "number": "112"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
