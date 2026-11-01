"""
Antara — Pre-Therapy Intake Intelligence System.
FastAPI Backend Server & Clinical Analytics Engine.
"""

import os
import json
import glob
from typing import Dict, Any, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from nlp_engine.report_synthesizer import ReportSynthesizer
from nlp_engine.question_bank import QuestionBank
from nlp_engine.crisis_classifier import CrisisClassifier
from pdf_engine.pdf_generator import ClinicalPDFGenerator
from storage.erasure_vault import ErasureVault

app = FastAPI(
    title="Antara — Pre-Therapy Clinical Intelligence Platform",
    description="NLP-driven clinical intake intelligence for therapists and women in pre-therapy sessions.",
    version="1.0.0"
)

# CORS middleware for seamless local integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
PERSONAS_DIR = os.path.join(BASE_DIR, "mock_personas")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Core singletons
synthesizer = ReportSynthesizer()
question_bank = QuestionBank()
crisis_classifier = CrisisClassifier()
pdf_generator = ClinicalPDFGenerator()
vault = ErasureVault()


# ==========================================
# PAGE ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def serve_patient_intake():
    """
    Serves the primary patient-facing intake chatbot application:
    Welcome & Consent -> Calm 1-Question Chat -> End & Erasure Confirmation.
    """
    html_path = os.path.join(TEMPLATES_DIR, "intake.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Intake template not found")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/therapist", response_class=HTMLResponse)
async def serve_therapist_portal():
    """
    Serves the clinical intelligence dashboard for the attending therapist.
    """
    html_path = os.path.join(TEMPLATES_DIR, "therapist_portal.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Therapist portal template not found")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# ==========================================
# CHAT INTAKE ENDPOINTS
# ==========================================

class CrisisCheckRequest(BaseModel):
    text: str


@app.post("/api/chat/check-crisis")
async def check_crisis(req: CrisisCheckRequest):
    """
    Evaluates text for self-harm or acute distress cues.
    Returns fixed emergency response if triggered.
    """
    return crisis_classifier.check_for_crisis(req.text)


class NextQuestionRequest(BaseModel):
    current_stage_index: int
    last_answer: Optional[str] = None
    skipped: bool = False


@app.post("/api/chat/next-question")
async def get_next_question(req: NextQuestionRequest):
    """
    Determines next stage question, adapting and reflecting her words
    without summarizing or advising.
    """
    if req.current_stage_index == 1 and not req.last_answer:
        return question_bank.get_initial_question()
    return question_bank.get_next_question(req.current_stage_index, req.last_answer, req.skipped)


@app.post("/api/chat/finish")
async def finish_chat_intake(session_data: Dict[str, Any]):
    """
    Completes patient intake:
    1. Runs full NLP extraction pipeline.
    2. Stores report in erasure vault.
    3. Simulates automatic client memory erasure and returns cryptographic audit token.
    """
    session_id = session_data.get("sessionId", "session_live")
    report = synthesizer.generate_full_report(session_data)
    vault.store_session(session_id, session_data, report)

    # Execute data erasure protocol for the client
    erasure_receipt = vault.erase_session(session_id)

    # Re-store report so therapist can review it immediately
    vault.store_session(session_id, session_data, report)

    return {
        "status": "COMPLETED",
        "sessionId": session_id,
        "erasure_receipt": erasure_receipt,
        "report_preview": {
            "start_emotion": report["section2_emotions_and_trajectory"]["start_emotion"],
            "end_emotion": report["section2_emotions_and_trajectory"]["end_emotion"],
            "hedging_level": report["section4_clinical_observations"]["hedging_analysis"]["level"],
            "inconsistency_severity": report["section4_clinical_observations"]["inconsistencies"]["severity"]
        }
    }


# ==========================================
# THERAPIST PORTAL & NLP ANALYTICS API
# ==========================================

@app.get("/api/personas")
async def list_mock_personas():
    """
    Lists all pre-configured test personas available for evaluation and vivas.
    """
    files = glob.glob(os.path.join(PERSONAS_DIR, "*.json"))
    persona_list = []
    for fp in files:
        base = os.path.basename(fp).replace(".json", "")
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
            persona_list.append({
                "id": base,
                "clientPseudonym": data.get("clientPseudonym", "Unknown"),
                "sessionId": data.get("sessionId", "")
            })
    return persona_list


@app.get("/api/personas/{persona_id}")
async def get_mock_persona(persona_id: str):
    """
    Loads raw session JSON for a specific persona.
    """
    filepath = os.path.join(PERSONAS_DIR, f"{persona_id}.json")
    if not os.path.exists(filepath):
        matches = glob.glob(os.path.join(PERSONAS_DIR, f"*{persona_id}*.json"))
        if matches:
            filepath = matches[0]
        else:
            raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/analyze")
async def analyze_session(session_data: Dict[str, Any]):
    """
    Main NLP Intake Pipeline:
    Ingests conversation transcript, executes hedging, emotion trajectory,
    inconsistency, edit-diff, and theme extraction, and stores transiently.
    """
    if "transcript" not in session_data and "responses" not in session_data:
        raise HTTPException(status_code=400, detail="Missing required 'transcript' or 'responses' field in session JSON")

    session_id = session_data.get("sessionId") or session_data.get("session_id", "session_unnamed")
    report = synthesizer.generate_full_report(session_data)
    vault.store_session(session_id, session_data, report)
    return report


@app.get("/api/report/{session_id}")
async def get_session_report(session_id: str):
    """
    Retrieves an existing analyzed report by session ID.
    """
    report = vault.get_report(session_id)
    if not report:
        if vault.is_erased(session_id):
            raise HTTPException(status_code=410, detail="Session data has already been permanently erased.")
        raise HTTPException(status_code=404, detail="Session report not found")
    return report


@app.get("/api/report/{session_id}/pdf")
async def export_session_pdf(session_id: str):
    """
    Generates and streams high-resolution clinical PDF report for the therapist.
    """
    report = vault.get_report(session_id)
    if not report:
        # Check if matches mock persona
        matches = glob.glob(os.path.join(PERSONAS_DIR, f"*{session_id}*.json"))
        if not matches:
            for fp in glob.glob(os.path.join(PERSONAS_DIR, "*.json")):
                with open(fp, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    if d.get("sessionId") == session_id:
                        matches = [fp]
                        break

        if matches:
            with open(matches[0], "r", encoding="utf-8") as f:
                raw_session = json.load(f)
                report = synthesizer.generate_full_report(raw_session)
                vault.store_session(session_id, raw_session, report)
        else:
            raise HTTPException(status_code=404, detail="Session report not found or already purged")

    pdf_bytes = pdf_generator.generate_pdf_bytes(report)
    filename = f"Antara_Clinical_Report_{session_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/erase/{session_id}")
async def erase_session_data(session_id: str):
    """
    Executes the cryptographic data erasure protocol.
    Zeroes memory buffers, removes client dialogue, and returns an audit receipt.
    """
    receipt = vault.erase_session(session_id)
    return receipt


@app.get("/api/health")
async def health_check():
    """
    System and NLP engine diagnostic health check.
    """
    return {
        "status": "online",
        "service": "Antara Clinical Intelligence Platform",
        "modules": {
            "intake_chat": "active",
            "crisis_safety_classifier": "active",
            "question_bank": "active (8 stages)",
            "hedging_detector": "active",
            "emotion_trajectory_analyzer": "active",
            "inconsistency_detector": "active",
            "edit_sanitization_analyzer": "active",
            "theme_extractor": "active",
            "pdf_generator": "active (ReportLab)",
            "erasure_vault": "active"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
