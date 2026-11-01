"""
Crisis Safety Classifier for Antara Pre-Therapy Intake.
Immediate circuit-breaker for self-harm, suicidal ideation, or acute crisis.
Provides fixed compassionate responses with verified helpline resources.
"""

import re
from typing import Dict, Any


class CrisisClassifier:
    """
    Scans input for crisis markers and triggers an immediate non-improvising
    safety circuit-breaker.
    """

    CRISIS_PATTERNS = [
        r"\b(?:suicide|suicidal|kill(?:ing)?\s+myself|end(?:ing)?\s+my\s+life|want(?:ing)?\s+to\s+die)\b",
        r"\b(?:better\s+off\s+dead|no\s+reason\s+to\s+live|don'?t\s+want\s+to\s+(?:wake\s+up|live|exist))\b",
        r"\b(?:self[- ]?harm|cut(?:ting)?\s+myself|hurt(?:ing)?\s+myself|bleed\s+out)\b",
        r"\b(?:hang(?:ing)?\s+myself|overdos(?:e|ing)|slit(?:ting)?\s+my\s+wrists?)\b",
        r"\b(?:abuse|abus(?:ed|ing)\s+me|physically\s+hurt(?:ing)?\s+me|beats?\s+me)\b"
    ]

    FIXED_CRISIS_MESSAGE = (
        "I hear how much pain you are carrying right now, and I want to make sure you are safe. "
        "Because I am an automated pre-therapy tool and not a human counselor, I cannot provide "
        "crisis support. Please reach out right now to someone who can help you in this moment:\n\n"
        "• **Tele-MANAS (Govt. of India)**: Call **14416** or **1800-891-4416** (24/7, Toll-Free)\n"
        "• **KIRAN Mental Health Helpline**: **1800-599-0019** (24/7, Toll-Free)\n"
        "• **Vandrevala Foundation**: **+91 9999 666 555** (24/7 Free Counseling)\n"
        "• **iCall Psychosocial Helpline**: **+91 9152 987 821** (Mon-Sat, 10 AM - 8 PM)\n"
        "• **International Crisis Line**: Dial **988** or visit **findahelpline.com**\n\n"
        "Your safety is the absolute priority. Please connect with one of these confidential services or a trusted loved one."
    )

    def __init__(self):
        self.compiled_regexes = [
            re.compile(pat, re.IGNORECASE) for pat in self.CRISIS_PATTERNS
        ]

    def check_for_crisis(self, text: str) -> Dict[str, Any]:
        """
        Evaluates text for crisis markers.
        """
        if not text:
            return {"is_crisis": False, "matched_patterns": []}

        matches = []
        for regex in self.compiled_regexes:
            match = regex.search(text)
            if match:
                matches.append(match.group(0))

        is_crisis = len(matches) > 0
        return {
            "is_crisis": is_crisis,
            "matched_patterns": matches,
            "safety_response": self.FIXED_CRISIS_MESSAGE if is_crisis else None
        }
