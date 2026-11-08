"""
Theme and Trigger Extractor for Antara Pre-Therapy Intake.
Extracts clinical life domains, situational and somatic triggers,
direct verbatim concern quotes, and therapeutic aspirations.
"""

import re
from typing import Dict, List, Any


class ThemeExtractor:
    """
    Extracts recurring thematic domains, situational triggers,
    and client goals from pre-therapy conversational transcripts.
    """

    THEME_CLUSTERS = {
        "Work & Performance Pressure": [
            "work", "job", "career", "manager", "team", "presentations", "deadlines",
            "imposter", "failing", "expectations", "college", "projects", "emails",
            "performance", "academic", "office", "boss"
        ],
        "Interpersonal & Emotional Isolation": [
            "partner", "husband", "boyfriend", "parents", "family", "friends",
            "burden", "isolated", "alienated", "lonely", "alone", "unpaid caregiver",
            "caregiver", "nobody asks", "hollow", "mask", "pretending"
        ],
        "Somatic & Physiological Dysregulation": [
            "chest", "stomach", "knot", "tightness", "neck", "shoulders", "nausea",
            "nauseous", "sleep", "insomnia", "3 am", "3:30 am", "cold sweats",
            "exhausted", "headache", "throat", "choking", "cement", "limbs"
        ],
        "Perfectionism & Self-Criticism": [
            "imposter", "weak", "cracking", "failure", "guilt", "guilty",
            "exhale", "permission to rest", "say no", "holding it together",
            "broken", "flawed"
        ]
    }

    TRIGGER_PATTERNS = [
        r"\b(?:sunday\s+evenings?|monday\s+mornings?)\b",
        r"\b(?:right\s+before\s+.*(?:presentations?|speaking|meetings?))\b",
        r"\b(?:wake\s+up\s+at\s+\d+(?::\d+)?\s*(?:am|pm)?)\b",
        r"\b(?:before\s+logging\s+on|opening\s+my\s+emails?)\b",
        r"\b(?:messages?\s+after\s+\d+\s*(?:pm|am))\b",
        r"\b(?:family\s+asks?\s+me\s+to\s+solve|chaos|arguments?)\b",
        r"\b(?:hearing\s+my\s+phone\s+ring)\b"
    ]

    def extract_themes_and_triggers(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the full transcript for themes, triggers, verbatim quotes, and therapy goals.
        """
        detected_themes = {}
        all_text = " ".join([item.get("finalAnswer") or "" for item in transcript if not item.get("isSkipped")]).lower()

        # Score thematic clusters
        for theme_name, keywords in self.THEME_CLUSTERS.items():
            matches = []
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", all_text):
                    matches.append(kw)
            if matches:
                detected_themes[theme_name] = {
                    "matched_keywords": matches,
                    "relevance_score": len(matches)
                }

        # Extract triggers
        found_triggers = []
        for item in transcript:
            if item.get("isSkipped"):
                continue
            ans = item.get("finalAnswer") or ""
            for pat in self.TRIGGER_PATTERNS:
                for match in re.finditer(pat, ans, re.IGNORECASE):
                    found_triggers.append({
                        "trigger": match.group(0),
                        "context": ans,
                        "stage": item.get("stage")
                    })

        # Extract Main Concerns in Her Own Stated Words (Direct Verbatim Quotes)
        verbatim_quotes = []
        therapy_hopes = None

        for item in transcript:
            if item.get("isSkipped") or "consent" in str(item.get("stage", "")).lower():
                continue

            ans = (item.get("finalAnswer") or "").strip()
            orig = (item.get("originalAnswer") or "").strip()
            stage = item.get("stage", "")
            q_text = item.get("question") or ""
            q_lower = q_text.lower()
            stage_lower = str(stage).lower()
            qid_lower = str(item.get("question_id") or "").lower()

            # If matching therapy goals / hopes, store as therapy hopes
            if any(k in q_lower or k in stage_lower or k in qid_lower for k in [
                "therapy", "hope", "goal", "outcome", "change one thing", "expect", "looking for", "7"
            ]):
                if ans:
                    therapy_hopes = {
                        "raw_quote": ans,
                        "question": q_text or "Therapeutic Hopes & Intentions",
                        "stage": stage
                    }

            # Select emotionally informative answers as key direct quotes
            is_concern = any(term in ans.lower() for term in [
                "imposter", "cracking", "exhale", "guilty", "guilt", "suffocating", "drowning",
                "tightness", "knot", "nauseous", "nausea", "mask", "pretending", "caregiver",
                "running on empty", "battery", "cold sweats", "burden", "alienated", "lonely",
                "alone", "grey block", "shaking", "panic", "anxious", "anxiety", "worried", "worry",
                "argument", "arguments", "conflict", "overwhelmed", "exhausted", "foggy", "stress",
                "pressure", "expectations", "sleep", "insomnia", "tired", "sad", "crying", "scared",
                "fear", "afraid", "numb", "shut down", "freeze", "failure", "failing", "nobody understands"
            ])
            if is_concern and len(ans) > 8:
                verbatim_quotes.append({
                    "quote": ans,
                    "stage": stage,
                    "step": item.get("step")
                })

        # If too few quotes found, pull the most substantive non-empty client answers
        if len(verbatim_quotes) < 2:
            substantive = [
                item for item in transcript
                if not item.get("isSkipped") and len((item.get("finalAnswer") or "").strip()) > 15
                and not any(v["quote"] == item.get("finalAnswer") for v in verbatim_quotes)
                and "consent" not in str(item.get("stage", "")).lower()
            ]
            substantive.sort(key=lambda x: len((x.get("finalAnswer") or "").strip()), reverse=True)
            for item in substantive[:4 - len(verbatim_quotes)]:
                verbatim_quotes.append({
                    "quote": item.get("finalAnswer"),
                    "stage": item.get("stage"),
                    "step": item.get("step")
                })

        # Rank detected themes by relevance
        sorted_themes = sorted(
            detected_themes.items(),
            key=lambda x: x[1]["relevance_score"],
            reverse=True
        )

        return {
            "themes": [{"name": k, "keywords": v["matched_keywords"]} for k, v in sorted_themes],
            "triggers": found_triggers,
            "verbatim_concerns": verbatim_quotes[:4],  # Top verbatim concerns
            "therapy_hopes": therapy_hopes
        }
