"""
Emotion and Trajectory Analyzer for Antara Pre-Therapy Intake.
Tracks multi-dimensional emotional states, valence, intensity,
and trajectory across all stages of the intake session.
"""

import re
from typing import Dict, List, Any


class EmotionAnalyzer:
    """
    Classifies granular clinical emotions, assesses somatic valence,
    and maps the emotional trajectory from intake opening to therapy aspirations.
    """

    EMOTION_LEXICONS = {
        "anxiety_fear": {
            "keywords": [
                "anxious", "anxiety", "panic", "scared", "fear", "terrified", "racing",
                "dread", "hammering", "trembling", "shaking", "nervous", "stage fright",
                "tightness", "knot", "cold sweats", "nauseous", "nausea", "on edge",
                "worried", "worry", "freaking out", "hyperventilating"
            ],
            "valence": -0.7,
            "color": "#ef4444"
        },
        "sadness_despair": {
            "keywords": [
                "sad", "sadness", "crying", "tears", "depressed", "hopeless", "drowning",
                "broken", "miserable", "sorrow", "grief", "gloomy", "heavy", "weeping",
                "sobbing", "despair", "darkness", "empty", "lonely", "alienated"
            ],
            "valence": -0.8,
            "color": "#3b82f6"
        },
        "overwhelm_burnout": {
            "keywords": [
                "overwhelmed", "overwhelming", "exhausted", "exhaustion", "drained",
                "running on empty", "suffocating", "wet cement", "cracking", "burden",
                "burnout", "too much", "weary", "weariness", "foggy", "clamped",
                "battery", "depleted", "collapse", "overloaded", "failing"
            ],
            "valence": -0.75,
            "color": "#8b5cf6"
        },
        "guilt_shame": {
            "keywords": [
                "guilt", "guilty", "shame", "ashamed", "imposter", "burden", "weak",
                "failure", "broken", "flawed", "my fault", "blame myself", "pretending",
                "mask", "fraud", "embarrassed"
            ],
            "valence": -0.65,
            "color": "#f59e0b"
        },
        "anger_resentment": {
            "keywords": [
                "angry", "anger", "resentful", "resentment", "frustrated", "irritated",
                "bitter", "furious", "unpaid caregiver", "mad", "unfair", "annoyed"
            ],
            "valence": -0.6,
            "color": "#dc2626"
        },
        "numbness_detachment": {
            "keywords": [
                "numb", "numbness", "shut down", "freeze", "frozen", "detached",
                "hollow", "void", "nothing", "grey block", "cement", "alienated",
                "guarded", "dissociated", "blank"
            ],
            "valence": -0.5,
            "color": "#64748b"
        },
        "hope_readiness": {
            "keywords": [
                "hope", "hoping", "heal", "healing", "lighter", "exhale", "learn",
                "work toward", "change", "resilience", "stop feeling", "better",
                "grow", "understand", "tools", "permission to rest", "peace"
            ],
            "valence": 0.7,
            "color": "#10b981"
        },
        "positive_calm": {
            "keywords": [
                "fine", "okay", "peaceful", "happy", "great", "content", "calm",
                "cheerful", "relaxed", "managing", "alright"
            ],
            "valence": 0.5,
            "color": "#06b6d4"
        }
    }

    STAGE_NAMES = {
        "1_consent": "Consent & Boundary Setting",
        "2_easy_opening": "Initial Check-in",
        "3_current_feelings": "Somatic & Bodily Sensations",
        "4_situations_triggers": "Triggers & Peak Situations",
        "5_daily_life_sleep": "Daily Rhythms & Physiology",
        "6_relationships": "Interpersonal & Relational Atmosphere",
        "7_therapy_hopes": "Therapeutic Hopes & Intentions"
    }

    def score_text_emotions(self, text: str) -> Dict[str, Any]:
        """
        Calculates emotion scores, primary emotion, intensity, and valence for text.
        """
        if not text:
            return {
                "primary_emotion": "unspecified",
                "scores": {},
                "valence": 0.0,
                "intensity": 0.0,
                "matched_terms": []
            }

        text_lower = text.lower()
        scores = {}
        matched_terms = []
        weighted_valence = 0.0
        total_hits = 0

        for emotion, meta in self.EMOTION_LEXICONS.items():
            count = 0
            for kw in meta["keywords"]:
                # Match word boundary or exact phrase
                pattern = r"\b" + re.escape(kw) + r"\b"
                hits = len(re.findall(pattern, text_lower))
                if hits > 0:
                    count += hits
                    matched_terms.append({"emotion": emotion, "term": kw, "count": hits})

            if count > 0:
                scores[emotion] = count
                total_hits += count
                weighted_valence += count * meta["valence"]

        if total_hits > 0:
            final_valence = round(weighted_valence / total_hits, 2)
            # Find dominant emotion
            primary_emotion = max(scores, key=scores.get)
            intensity = min(round(total_hits / 3.0, 2), 1.0)
        else:
            primary_emotion = "neutral_subdued"
            final_valence = -0.1
            intensity = 0.2

        return {
            "primary_emotion": primary_emotion,
            "scores": scores,
            "valence": final_valence,
            "intensity": intensity,
            "matched_terms": matched_terms
        }

    def analyze_trajectory(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Maps emotional trajectory step-by-step and stage-by-stage across the session.
        """
        timeline = []
        overall_emotion_distribution = {e: 0 for e in self.EMOTION_LEXICONS}
        valence_points = []
        somatic_emotions = []
        relational_emotions = []
        therapy_intentions = []

        for item in transcript:
            stage_key = item.get("stage", "")
            if "consent" in stage_key.lower():
                continue

            stage_label = self.STAGE_NAMES.get(stage_key, stage_key.replace("_", " ").title())
            is_skipped = item.get("isSkipped", False)
            answer = item.get("finalAnswer") or ""

            if is_skipped:
                timeline.append({
                    "step": item.get("step"),
                    "stage_key": stage_key,
                    "stage_label": stage_label,
                    "status": "skipped",
                    "primary_emotion": "avoided / skipped",
                    "valence": 0.0,
                    "intensity": 0.0,
                    "summary_quote": "[Question Skipped by Client]"
                })
                continue

            scored = self.score_text_emotions(answer)
            for em, count in scored["scores"].items():
                overall_emotion_distribution[em] += count

            valence_points.append(scored["valence"])

            # Collect stage-specific focus
            if "current_feelings" in stage_key or "3" in stage_key:
                somatic_emotions.append(scored["primary_emotion"])
            elif "relationships" in stage_key or "6" in stage_key:
                relational_emotions.append(scored["primary_emotion"])
            elif "therapy_hopes" in stage_key or "7" in stage_key:
                therapy_intentions.append(scored["primary_emotion"])

            # Formulate short quote preview
            quote_snippet = answer if len(answer) <= 90 else answer[:87] + "..."

            timeline.append({
                "step": item.get("step"),
                "stage_key": stage_key,
                "stage_label": stage_label,
                "status": "answered",
                "primary_emotion": scored["primary_emotion"],
                "valence": scored["valence"],
                "intensity": scored["intensity"],
                "summary_quote": quote_snippet,
                "matched_terms": [m["term"] for m in scored["matched_terms"]]
            })

        # Calculate Trajectory Arc Narrative
        first_step = next((t for t in timeline if t["status"] == "answered"), None)
        last_step = next((t for t in reversed(timeline) if t["status"] == "answered"), None)

        start_emotion = first_step["primary_emotion"] if first_step else "neutral"
        end_emotion = last_step["primary_emotion"] if last_step else "neutral"

        # Determine peak distress step
        peak_step = None
        min_valence = 1.0
        for t in timeline:
            if t["status"] == "answered" and t["valence"] < min_valence:
                min_valence = t["valence"]
                peak_step = t

        arc_narrative = (
            f"Conversation opened with {start_emotion.replace('_', ' ')}. "
            f"Distress peaked in {peak_step['stage_label'] if peak_step else 'middle stages'} "
            f"around somatic and daily life descriptions, before concluding with {end_emotion.replace('_', ' ')} "
            f"during therapy goal exploration."
        )

        return {
            "timeline": timeline,
            "overall_distribution": overall_emotion_distribution,
            "start_emotion": start_emotion,
            "end_emotion": end_emotion,
            "peak_distress_stage": peak_step["stage_label"] if peak_step else "None",
            "average_valence": round(sum(valence_points) / max(len(valence_points), 1), 2),
            "trajectory_arc_narrative": arc_narrative
        }
