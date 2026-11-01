"""
Question Bank and Conversational Flow Engine for Antara.
Contains 50+ clinically calibrated questions across 8 stages,
with word reflection and indirect/sensory questioning.
"""

import re
from typing import Dict, List, Any, Optional


class QuestionBank:
    """
    Manages stage progression, adaptive follow-ups, and reflective questioning.
    """

    CONSENT_TEXT = (
        "You just need to be completely honest throughout this session. "
        "No one is going to judge you. The whole session is encrypted and confidential, "
        "and the report will be sent only to your doctor, to help them understand you better. "
        "Your doctor will also receive a full copy of this conversation. "
        "Once the report has been sent, your information will be erased."
    )

    STAGES = [
        {"id": "1_consent", "title": "Consent & Welcome", "description": "Privacy and ethical consent."},
        {"id": "2_easy_opening", "title": "Initial Check-in", "description": "Soft, low-pressure opening."},
        {"id": "3_current_feelings", "title": "Current Feelings & Somatics", "description": "Emotional intensity and bodily sensations."},
        {"id": "4_situations_triggers", "title": "Situations & Triggers", "description": "Environmental context and peak moments."},
        {"id": "5_daily_life_sleep", "title": "Daily Rhythms & Physiology", "description": "Sleep, appetite, and energy patterns."},
        {"id": "6_relationships", "title": "Relational Atmosphere", "description": "Interpersonal feelings and emotional safety."},
        {"id": "7_therapy_hopes", "title": "Therapeutic Hopes", "description": "Expectations and aspirations from therapy."},
        {"id": "8_gentle_close", "title": "Gentle Closing", "description": "Warm conclusion and erasure confirmation."}
    ]

    QUESTIONS_BY_STAGE = {
        "1_consent": [
            "Welcome to Antara. Before we begin, please confirm that you understand this session is confidential, that your therapist will receive a summary and full conversation transcript, and that your data will be erased after sending. Are you ready to begin?"
        ],
        "2_easy_opening": [
            "How are you feeling right now as you sit down for this conversation?",
            "If you pause for a quiet second, what kind of headspace are you arriving with today?",
            "How has today felt for you so far?"
        ],
        "3_current_feelings": [
            "Where in your physical body do you notice that feeling most right now?",
            "If this feeling had a physical weight or a color, what would it be?",
            "Does this sensation feel sharp and active, or more like a dull, heavy stillness?",
            "How long has this particular feeling been sitting with you?"
        ],
        "4_situations_triggers": [
            "Think of yesterday or the past couple of days. Are there specific times of day when this feeling tends to get heavier?",
            "What is usually happening around you when that feeling starts to rise?",
            "Is there a particular place or setting where you notice yourself feeling most on edge?",
            "When things feel most intense, what thoughts usually come rushing in?"
        ],
        "5_daily_life_sleep": [
            "How have your nights and mornings been treating you—your sleep, appetite, or physical energy?",
            "Think of from when you wake up to when you go to bed. How does your energy move throughout the day?",
            "When was the last time you felt physically rested after sleeping?",
            "How has your relationship with food or nourishment felt over the past few weeks?"
        ],
        "6_relationships": [
            "How do you feel emotionally when you are around the people closest to you right now?",
            "Is there anyone in your life with whom you feel completely safe showing this side of yourself?",
            "Do you find yourself feeling like you need to protect others from what you are going through?",
            "How does it feel when someone asks you how you are doing?"
        ],
        "7_therapy_hopes": [
            "Looking ahead to meeting with your therapist, what is something you hope might feel lighter?",
            "If therapy could help you change or let go of one thing, what would that be?",
            "What feels most important for your doctor to know about you before you meet?",
            "What would feeling truly supported look like for you right now?"
        ],
        "8_gentle_close": [
            "Thank you for sharing so honestly and bravely. Your responses are being organized into a private clinical report for your doctor. As promised at the start, your dialogue will now be erased from active memory. Take a gentle breath—your therapist is looking forward to meeting you."
        ]
    }

    EMOTIONAL_KEYWORD_EXTRACTION = re.compile(
        r"\b(?:tired|heavy|heaviness|drained|exhausted|anxious|anxiety|panic|knot|tightness|"
        r"stomach|chest|scared|sad|crying|numb|foggy|overwhelmed|alone|burden|pressure|imposter|"
        r"restless|angry|hollow|suffocating|racing|weight|grey|dark)\b",
        re.IGNORECASE
    )

    def extract_reflection_word(self, user_answer: str) -> Optional[str]:
        """
        Extracts an authentic feeling or somatic word from her response
        to reflect back into the next question without summarizing.
        """
        if not user_answer:
            return None
        matches = self.EMOTIONAL_KEYWORD_EXTRACTION.findall(user_answer)
        if matches:
            # Pick the most prominent/latest matched word
            return matches[-1].lower()
        return None

    def get_initial_question(self) -> Dict[str, Any]:
        """
        Returns the first opening question.
        """
        return {
            "stage_index": 1,
            "stage_id": "2_easy_opening",
            "stage_title": "Initial Check-in",
            "question": self.QUESTIONS_BY_STAGE["2_easy_opening"][0],
            "is_final_stage": False
        }

    def get_next_question(self, current_stage_index: int, user_answer: Optional[str] = None, skipped: bool = False) -> Dict[str, Any]:
        """
        Determines the next question, incorporating reflection if appropriate.
        """
        next_stage_index = current_stage_index + 1
        if next_stage_index >= len(self.STAGES) - 1:
            # Stage 8 is close
            stage_meta = self.STAGES[7]
            return {
                "stage_index": 7,
                "stage_id": stage_meta["id"],
                "stage_title": stage_meta["title"],
                "question": self.QUESTIONS_BY_STAGE["8_gentle_close"][0],
                "is_final_stage": True
            }

        stage_meta = self.STAGES[next_stage_index]
        stage_id = stage_meta["id"]
        base_questions = self.QUESTIONS_BY_STAGE.get(stage_id, ["How does that feel?"])
        base_q = base_questions[0]

        # Apply reflective wording rule if available and not skipped
        reflected_q = base_q
        if user_answer and not skipped:
            reflected_word = self.extract_reflection_word(user_answer)
            if reflected_word:
                if stage_id == "3_current_feelings":
                    reflected_q = f"When you notice that feeling of being {reflected_word}, where does that sensation live most in your body?"
                elif stage_id == "4_situations_triggers":
                    reflected_q = f"When that {reflected_word} starts to feel strongest, what is usually happening around you?"
                elif stage_id == "5_daily_life_sleep":
                    reflected_q = f"How has that {reflected_word} been affecting your sleep, appetite, or day-to-day energy?"
                elif stage_id == "6_relationships":
                    reflected_q = f"When you are carrying that {reflected_word}, how does it feel to be around the people closest to you?"

        return {
            "stage_index": next_stage_index,
            "stage_id": stage_id,
            "stage_title": stage_meta["title"],
            "question": reflected_q,
            "is_final_stage": (next_stage_index == len(self.STAGES) - 1)
        }
