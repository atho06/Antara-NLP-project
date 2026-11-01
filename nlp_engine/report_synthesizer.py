"""
Clinical Report Synthesizer for Antara Pre-Therapy Intake.
Integrates all NLP extractors into a structured, clinical-grade briefing
for the attending therapist.
"""

import os
import datetime
from typing import Dict, List, Any

from nlp_engine.hedging_detector import HedgingDetector
from nlp_engine.emotion_analyzer import EmotionAnalyzer
from nlp_engine.inconsistency_detector import InconsistencyDetector
from nlp_engine.edit_analyzer import EditAnalyzer
from nlp_engine.theme_extractor import ThemeExtractor


class ReportSynthesizer:
    """
    Coordinates linguistic, emotional, and structural analysis into
    the comprehensive 6-part therapist report.
    """

    MANDATORY_DISCLAIMER = (
        "AI-Generated Observations from Self-Reported Intake Data. "
        "For clinical reference only. Not a medical or psychological diagnosis."
    )

    def __init__(self):
        self.hedging_detector = HedgingDetector()
        self.emotion_analyzer = EmotionAnalyzer()
        self.inconsistency_detector = InconsistencyDetector()
        self.edit_analyzer = EditAnalyzer()
        self.theme_extractor = ThemeExtractor()

    def generate_full_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a completed session JSON and constructs the 6-section report.
        """
        session_id = session_data.get("sessionId", "session_unknown")
        client_name = session_data.get("clientPseudonym", "Client")
        started_at = session_data.get("startedAt", "")
        completed_at = session_data.get("completedAt", "")
        transcript = session_data.get("transcript", [])
        crisis_triggered = session_data.get("crisisTriggered", False)

        # 1. Run all individual NLP extractors
        hedging_res = self.hedging_detector.analyze_transcript(transcript)
        emotion_res = self.emotion_analyzer.analyze_trajectory(transcript)
        inconsistency_res = self.inconsistency_detector.detect_inconsistencies(transcript)
        edit_res = self.edit_analyzer.analyze_transcript_edits(transcript)
        theme_res = self.theme_extractor.extract_themes_and_triggers(transcript)

        # 2. Build Section 1: Main Concerns in Her Own Stated Words
        main_concerns = {
            "verbatim_quotes": theme_res["verbatim_concerns"],
            "summary_takeaway": (
                f"Client primarily articulates distress through somatic sensations, "
                f"workplace pressure, and internal self-judgment."
            )
        }

        # 3. Build Section 2: Key Emotions & Trajectory
        key_emotions = {
            "start_emotion": emotion_res["start_emotion"],
            "end_emotion": emotion_res["end_emotion"],
            "peak_distress_stage": emotion_res["peak_distress_stage"],
            "average_valence": emotion_res["average_valence"],
            "trajectory_arc_narrative": emotion_res["trajectory_arc_narrative"],
            "distribution": emotion_res["overall_distribution"],
            "step_timeline": emotion_res["timeline"]
        }

        # 4. Build Section 3: Recurring Themes & Triggers
        themes_and_triggers = {
            "primary_themes": theme_res["themes"],
            "situational_triggers": theme_res["triggers"]
        }

        # 5. Build Section 4: Observations (Inconsistencies, Hedging, Avoided Topics, Edits)
        observations = {
            "hedging_analysis": {
                "level": hedging_res["hedging_level"],
                "total_hedges": hedging_res["total_hedges"],
                "percentage_answers_hedged": hedging_res["hedged_answer_percentage"],
                "interpretation": hedging_res["clinical_interpretation"],
                "category_distribution": hedging_res["category_distribution"],
                "highlighted_examples": hedging_res["highlighted_instances"][:3]
            },
            "inconsistencies": {
                "detected": inconsistency_res["has_inconsistencies"],
                "total_flags": inconsistency_res["total_flags"],
                "severity": inconsistency_res["severity_summary"],
                "items": inconsistency_res["flags"]
            },
            "avoided_topics": {
                "total_skipped": hedging_res["skipped_count"],
                "skipped_items": hedging_res["skipped_details"]
            },
            "edited_answers": {
                "total_edits": edit_res["total_edits"],
                "sanitization_detected": edit_res["total_sanitizations"] > 0,
                "sanitization_count": edit_res["total_sanitizations"],
                "clinical_takeaway": edit_res["clinical_takeaway"],
                "records": edit_res["records"]
            }
        }

        # 6. Build Section 5: What She Wants from Therapy
        therapy_wants = {
            "verbatim_hope": theme_res["therapy_hopes"]["raw_quote"] if theme_res["therapy_hopes"] else "No explicit therapy goal stated.",
            "question_prompt": theme_res["therapy_hopes"]["question"] if theme_res["therapy_hopes"] else ""
        }

        # 7. Build Section 6: Attached Full Conversation with Markers
        annotated_transcript = []
        for item in transcript:
            is_edited = item.get("isEdited", False)
            is_skipped = item.get("isSkipped", False)

            markers = []
            if is_edited:
                markers.append("[edited]")
            if is_skipped:
                markers.append("[skipped]")

            marker_label = " ".join(markers) if markers else "[verbatim]"

            annotated_transcript.append({
                "step": item.get("step"),
                "stage": item.get("stage"),
                "question": item.get("question"),
                "final_answer": item.get("finalAnswer"),
                "original_answer": item.get("originalAnswer") if is_edited else None,
                "marker": marker_label,
                "is_edited": is_edited,
                "is_skipped": is_skipped,
                "timestamp": item.get("timestamp")
            })

        # Assemble full report structure
        return {
            "metadata": {
                "sessionId": session_id,
                "clientPseudonym": client_name,
                "generatedAt": datetime.datetime.now().isoformat(),
                "startedAt": started_at,
                "completedAt": completed_at,
                "crisisTriggered": crisis_triggered,
                "disclaimer": self.MANDATORY_DISCLAIMER
            },
            "section1_main_concerns": main_concerns,
            "section2_emotions_and_trajectory": key_emotions,
            "section3_themes_and_triggers": themes_and_triggers,
            "section4_clinical_observations": observations,
            "section5_therapy_goals": therapy_wants,
            "section6_attached_transcript": annotated_transcript
        }
