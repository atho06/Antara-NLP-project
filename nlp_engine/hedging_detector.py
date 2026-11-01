"""
Hedging and Avoidance Detector for Antara Pre-Therapy Intake.
Analyzes linguistic minimization, epistemic modals, approximators,
and downplaying markers in client responses.
"""

import re
from typing import Dict, List, Any


class HedgingDetector:
    """
    Detects minimizing language, hedging markers, and avoidance behavior
    in pre-therapy transcripts.
    """

    HEDGE_PATTERNS = {
        "minimizers": [
            r"\b(?:it'?s\s+(?:fine|okay|whatever|alright|nothing|not\s+a\s+big\s+deal))\b",
            r"\b(?:not\s+a\s+big\s+deal|no\s+big\s+deal|not\s+really\s+important)\b",
            r"\b(?:probably\s+nothing|nothing\s+too\s+(?:dramatic|serious|bad))\b",
            r"\b(?:just\s+normal\s+(?:stress|tiredness|fatigue|anxiety|stage\s+fright))\b",
            r"\b(?:i\s+manage|i'?m\s+fine|i'?m\s+okay|i\s+guess\s+i'?m\s+fine)\b",
            r"\b(?:could\s+be\s+worse|others\s+have\s+it\s+worse)\b",
            r"\b(?:it\s+doesn'?t\s+matter|doesn'?t\s+really\s+matter)\b",
        ],
        "epistemic_modals": [
            r"\b(?:i\s+guess)\b",
            r"\b(?:i\s+suppose)\b",
            r"\b(?:sort\s+of)\b",
            r"\b(?:kind\s+of)\b",
            r"\b(?:maybe)\b",
            r"\b(?:perhaps)\b",
            r"\b(?:more\s+or\s+less)\b",
            r"\b(?:i\s+feel\s+like\s+maybe)\b",
        ],
        "diminutives": [
            r"\b(?:just)\b",
            r"\b(?:a\s+bit)\b",
            r"\b(?:a\s+little)\b",
            r"\b(?:only)\b",
            r"\b(?:merely)\b",
            r"\b(?:slightly)\b",
        ],
        "self_doubt_vagueness": [
            r"\b(?:not\s+really\s+sure)\b",
            r"\b(?:hard\s+to\s+say)\b",
            r"\b(?:i\s+don'?t\s+know|idk)\b",
            r"\b(?:don'?t\s+want\s+to\s+be\s+a\s+burden)\b",
            r"\b(?:everyone\s+has\s+their\s+own\s+problems)\b",
        ]
    }

    def __init__(self):
        # Precompile regular expressions for efficiency
        self.compiled_patterns = {
            category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for category, patterns in self.HEDGE_PATTERNS.items()
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes a single utterance for hedging cues.
        """
        if not text:
            return {"hedge_count": 0, "categories": {}, "matches": []}

        matches_found = []
        category_counts = {cat: 0 for cat in self.HEDGE_PATTERNS}

        for category, regex_list in self.compiled_patterns.items():
            for regex in regex_list:
                for match in regex.finditer(text):
                    matched_text = match.group(0).lower().strip()
                    matches_found.append({
                        "phrase": matched_text,
                        "category": category,
                        "start": match.start(),
                        "end": match.end()
                    })
                    category_counts[category] += 1

        word_count = max(len(text.split()), 1)
        density = (len(matches_found) / word_count) * 100

        return {
            "hedge_count": len(matches_found),
            "density_per_100_words": round(density, 2),
            "category_counts": category_counts,
            "matches": matches_found,
            "has_hedge": len(matches_found) > 0
        }

    def analyze_transcript(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the complete session transcript for hedging and avoidance patterns.
        """
        total_answers = 0
        hedged_answers = 0
        total_hedges = 0
        skipped_count = 0
        skipped_stages = []
        stage_breakdowns = []
        overall_category_counts = {cat: 0 for cat in self.HEDGE_PATTERNS}
        highlighted_instances = []

        for item in transcript:
            stage = item.get("stage", "unknown")
            question = item.get("question", "")
            is_skipped = item.get("isSkipped", False)
            answer = item.get("finalAnswer") or ""

            if is_skipped:
                skipped_count += 1
                skipped_stages.append({
                    "stage": stage,
                    "question": question,
                    "step": item.get("step")
                })
                continue

            # We don't grade consent step for linguistic hedging
            if "consent" in stage.lower():
                continue

            total_answers += 1
            analysis = self.analyze_text(answer)

            if analysis["has_hedge"]:
                hedged_answers += 1
                total_hedges += analysis["hedge_count"]
                for cat, count in analysis["category_counts"].items():
                    overall_category_counts[cat] += count

                highlighted_instances.append({
                    "step": item.get("step"),
                    "stage": stage,
                    "question": question,
                    "answer": answer,
                    "hedge_count": analysis["hedge_count"],
                    "matched_phrases": [m["phrase"] for m in analysis["matches"]],
                    "categories": [m["category"] for m in analysis["matches"]]
                })

            stage_breakdowns.append({
                "step": item.get("step"),
                "stage": stage,
                "answer_length": len(answer.split()),
                "hedge_count": analysis["hedge_count"],
                "has_hedge": analysis["has_hedge"]
            })

        hedged_answer_percentage = round((hedged_answers / max(total_answers, 1)) * 100, 1)

        # Determine clinical significance / severity label
        if hedged_answer_percentage >= 50 or total_hedges >= 6:
            hedging_level = "High"
            interpretation = "Pervasive minimization and hedging across responses. The client routinely softens distress and downplays the legitimacy of her suffering."
        elif hedged_answer_percentage >= 25 or total_hedges >= 3:
            hedging_level = "Moderate"
            interpretation = "Noticeable hedging in specific thematic areas. The client occasionally minimizes symptoms when discussing somatic or interpersonal distress."
        else:
            hedging_level = "Low"
            interpretation = "Minimal hedging detected. The client appears relatively direct in describing her emotional state."

        return {
            "hedging_level": hedging_level,
            "total_hedges": total_hedges,
            "hedged_answers_count": hedged_answers,
            "total_evaluated_answers": total_answers,
            "hedged_answer_percentage": hedged_answer_percentage,
            "category_distribution": overall_category_counts,
            "skipped_count": skipped_count,
            "skipped_details": skipped_stages,
            "highlighted_instances": highlighted_instances,
            "clinical_interpretation": interpretation
        }
