"""
Inconsistency and Contradiction Detector for Antara Pre-Therapy Intake.
Flags discrepancies between stated mood and lived distress,
performance masking, and intra-session contradictions.
"""

import re
from typing import Dict, List, Any


class InconsistencyDetector:
    """
    Detects semantic and affective discrepancies across interview answers:
    - Overt positivity vs somatic distress
    - Relational harmony vs hidden alienation
    - Linguistic masking (concessive reversals)
    """

    POSITIVE_ASSERTIONS = [
        r"\b(?:completely\s+fine|peaceful|totally\s+happy|life\s+is\s+great|nothing\s+to\s+complain\s+about)\b",
        r"\b(?:i'?m\s+(?:great|really\s+good|wonderful|fine|doing\s+well))\b",
        r"\b(?:everything\s+is\s+(?:fine|good|okay))\b",
        r"\b(?:no\s+problems?|nothing\s+bothering\s+me)\b"
    ]

    SEVERE_DISTRESS_TERMS = [
        r"\b(?:panic\s+attacks?|cold\s+sweats?|trembling|shaking|heart\s+hammering)\b",
        r"\b(?:can'?t\s+sleep\s+in\s+weeks|wake\s+up\s+at\s+3\s*(?::\s*30)?\s*am|haven'?t\s+slept)\b",
        r"\b(?:crying\s+(?:silently|every\s+night|in\s+the\s+shower)|tears)\b",
        r"\b(?:nausea|nauseous|stomach\s+knotted|constricted|choking)\b",
        r"\b(?:suffocating|drowning|dreading|dread\s+opening)\b",
        r"\b(?:hollow|utterly\s+alienated|completely\s+isolated)\b"
    ]

    MASKING_MARKERS = [
        r"\b(?:put\s+on\s+a\s+(?:bright\s+)?smile|act\s+like\s+the\s+life\s+of\s+the\s+party)\b",
        r"\b(?:pretending\s+i\s+have\s+it\s+all\s+together|taking\s+off\s+this\s+mask)\b",
        r"\b(?:smile\s+in\s+front\s+of\s+.*and\s+cry\s+(?:silently)?)\b",
        r"\b(?:tell\s+everyone\s+.*fine|don'?t\s+want\s+to\s+be\s+a\s+burden)\b"
    ]

    CONCESSIVE_SPLIT = re.compile(r"\b(?:but|yet|however|though|except)\b", re.IGNORECASE)

    def detect_inconsistencies(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans full session for cross-stage and intra-answer contradictions.
        """
        flags = []
        opening_statement = None
        opening_step = None
        somatic_statements = []
        daily_life_statements = []
        relational_statements = []

        # Categorize responses by stage
        for item in transcript:
            if item.get("isSkipped"):
                continue
            stage = item.get("stage", "")
            answer = item.get("finalAnswer") or ""
            step = item.get("step")

            if "2_easy_opening" in stage:
                opening_statement = answer
                opening_step = step
            elif "3_current_feelings" in stage:
                somatic_statements.append({"step": step, "stage": stage, "answer": answer})
            elif "5_daily_life" in stage:
                daily_life_statements.append({"step": step, "stage": stage, "answer": answer})
            elif "6_relationships" in stage:
                relational_statements.append({"step": step, "stage": stage, "answer": answer})

            # Check intra-sentence masking
            for mask_regex in self.MASKING_MARKERS:
                match = re.search(mask_regex, answer, re.IGNORECASE)
                if match:
                    flags.append({
                        "type": "Emotional Masking & Facade",
                        "severity": "High",
                        "step": step,
                        "stage": stage,
                        "explanation": "Client explicitly describes presenting a cheerful or composed exterior while harboring hidden emotional pain or exhaustion.",
                        "evidence_quote": answer,
                        "key_marker": match.group(0)
                    })

        # 1. Compare Stated Opening Mood vs. Somatic / Physiological Distress
        if opening_statement:
            has_positive_opening = any(
                re.search(pat, opening_statement, re.IGNORECASE) for pat in self.POSITIVE_ASSERTIONS
            )

            if has_positive_opening:
                # Check somatic answers
                for som in somatic_statements:
                    distress_hits = [
                        re.search(pat, som["answer"], re.IGNORECASE)
                        for pat in self.SEVERE_DISTRESS_TERMS
                    ]
                    distress_hits = [h.group(0) for h in distress_hits if h]
                    if distress_hits:
                        flags.append({
                            "type": "Stated Mood vs. Somatic Reality",
                            "severity": "High",
                            "step_comparison": f"Step {opening_step} vs Step {som['step']}",
                            "explanation": "Client initially presented as fine, happy, or unbothered in the opening check-in, but later reported acute physical distress and somatic symptoms.",
                            "primary_statement": f"Opening check-in: \"{opening_statement}\"",
                            "contrasting_statement": f"Somatic observation: \"{som['answer']}\"",
                            "discrepancy_markers": distress_hits
                        })

                # Check daily life / sleep answers
                for dl in daily_life_statements:
                    distress_hits = [
                        re.search(pat, dl["answer"], re.IGNORECASE)
                        for pat in self.SEVERE_DISTRESS_TERMS
                    ]
                    distress_hits = [h.group(0) for h in distress_hits if h]
                    if distress_hits:
                        flags.append({
                            "type": "Stated Mood vs. Daily Functioning Disruption",
                            "severity": "High",
                            "step_comparison": f"Step {opening_step} vs Step {dl['step']}",
                            "explanation": "Client verbally stated no major issues upon entry, but disclosed severe sleep impairment, nausea, or panic attacks under daily life scrutiny.",
                            "primary_statement": f"Opening check-in: \"{opening_statement}\"",
                            "contrasting_statement": f"Daily life observation: \"{dl['answer']}\"",
                            "discrepancy_markers": distress_hits
                        })

        # 2. Concessive Intra-Answer Inversions (e.g., "I'm fine, BUT I wake up crying")
        for item in transcript:
            if item.get("isSkipped") or "consent" in item.get("stage", ""):
                continue
            answer = item.get("finalAnswer") or ""
            parts = self.CONCESSIVE_SPLIT.split(answer)
            if len(parts) >= 2:
                first_part = parts[0]
                second_part = parts[1]
                positive_intro = any(re.search(p, first_part, re.IGNORECASE) for p in self.POSITIVE_ASSERTIONS + [r"\b(?:fine|okay|alright)\b"])
                negative_reversal = any(re.search(d, second_part, re.IGNORECASE) for d in self.SEVERE_DISTRESS_TERMS)

                if positive_intro and negative_reversal:
                    flags.append({
                        "type": "Concessive Emotional Inversion",
                        "severity": "Moderate",
                        "step": item.get("step"),
                        "stage": item.get("stage"),
                        "explanation": "Client opened the sentence with a socially compliant reassurance ('I'm fine/okay') before immediately overturning it with distress.",
                        "evidence_quote": answer,
                        "first_clause": first_part.strip(),
                        "reversal_clause": second_part.strip()
                    })

        # Remove duplicate flags
        unique_flags = []
        seen = set()
        for f in flags:
            key = (f.get("type"), f.get("step"), f.get("step_comparison"))
            if key not in seen:
                seen.add(key)
                unique_flags.append(f)

        return {
            "has_inconsistencies": len(unique_flags) > 0,
            "total_flags": len(unique_flags),
            "severity_summary": "High" if any(f.get("severity") == "High" for f in unique_flags) else ("Moderate" if unique_flags else "None Detected"),
            "flags": unique_flags
        }
