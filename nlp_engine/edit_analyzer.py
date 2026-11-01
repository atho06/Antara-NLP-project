"""
Edit Diff and Self-Censorship Analyzer for Antara Pre-Therapy Intake.
Compares original vs edited answers to detect vulnerability retraction,
emotional sanitization, and downplaying before therapist viewing.
"""

import difflib
import re
from typing import Dict, List, Any


class EditAnalyzer:
    """
    Analyzes answer revisions to uncover self-censorship, vulnerability retraction,
    and differences between initial gut responses and sanitized submissions.
    """

    RAW_VULNERABILITY_TERMS = [
        r"\b(?:drowning|suffocating|choking|clamped\s+shut)\b",
        r"\b(?:crying\s+(?:silently|in\s+the\s+shower)|tears|breaking\s+down)\b",
        r"\b(?:trembling|shaking|panic|terrified)\b",
        r"\b(?:broken|weak|failing|hate\s+myself|hopeless)\b",
        r"\b(?:utterly\s+alienated|haven'?t\s+slept\s+in\s+3\s+months|dreading\s+daylight)\b"
    ]

    SANITIZED_SUBSTITUTES = [
        r"\b(?:managing\s+okay|a\s+bit\s+weary|general\s+tightness|irregular\s+sleep)\b",
        r"\b(?:handle\s+things\s+independently|supportive|just\s+a\s+bit|manageable)\b"
    ]

    def analyze_diff(self, original: str, edited: str) -> Dict[str, Any]:
        """
        Computes detailed token diff, similarity ratio, and sanitization detection.
        """
        if not original or not edited:
            return {
                "similarity_ratio": 1.0,
                "sanitization_detected": False,
                "removed_vulnerability_terms": [],
                "added_sanitized_terms": [],
                "html_diff": edited
            }

        # Calculate Levenshtein-based similarity
        matcher = difflib.SequenceMatcher(None, original, edited)
        similarity = round(matcher.ratio(), 2)

        # Check for removal of raw vulnerability
        removed_terms = []
        for pat in self.RAW_VULNERABILITY_TERMS:
            matches_orig = re.findall(pat, original, re.IGNORECASE)
            matches_edit = re.findall(pat, edited, re.IGNORECASE)
            if len(matches_orig) > len(matches_edit):
                removed_terms.extend(matches_orig)

        # Check for addition of sanitized language
        added_sanitized = []
        for pat in self.SANITIZED_SUBSTITUTES:
            matches_orig = re.findall(pat, original, re.IGNORECASE)
            matches_edit = re.findall(pat, edited, re.IGNORECASE)
            if len(matches_edit) > len(matches_orig):
                added_sanitized.extend(matches_edit)

        sanitization_detected = len(removed_terms) > 0

        # Construct visual inline HTML diff
        orig_words = original.split()
        edit_words = edited.split()
        word_matcher = difflib.SequenceMatcher(None, orig_words, edit_words)
        diff_fragments = []

        for tag, i1, i2, j1, j2 in word_matcher.get_opcodes():
            if tag == 'equal':
                diff_fragments.append(" ".join(orig_words[i1:i2]))
            elif tag == 'delete':
                diff_fragments.append(f'<del class="diff-del">{" ".join(orig_words[i1:i2])}</del>')
            elif tag == 'insert':
                diff_fragments.append(f'<ins class="diff-ins">{" ".join(edit_words[j1:j2])}</ins>')
            elif tag == 'replace':
                diff_fragments.append(f'<del class="diff-del">{" ".join(orig_words[i1:i2])}</del> <ins class="diff-ins">{" ".join(edit_words[j1:j2])}</ins>')

        html_diff = " ".join(diff_fragments)

        # Classify the nature of the edit (Cosmetic vs Semantic/POV shift)
        if original.strip().lower() == edited.strip().lower():
            edit_type = "COSMETIC_CASING"
            edit_type_label = "Punctuation/Casing Triviality"
        elif similarity >= 0.88 and not removed_terms and not added_sanitized:
            edit_type = "MINOR_TYPO"
            edit_type_label = "Minor Spelling/Grammar Correction"
        elif sanitization_detected:
            edit_type = "VULNERABILITY_RETRACTION"
            edit_type_label = "Emotional Sanitization & Vulnerability Retraction"
        else:
            edit_type = "CONTEXTUAL_REVISION"
            edit_type_label = "Contextual & Perspective Revision"

        return {
            "similarity_ratio": similarity,
            "edit_type": edit_type,
            "edit_type_label": edit_type_label,
            "sanitization_detected": sanitization_detected,
            "is_substantive": edit_type in ["VULNERABILITY_RETRACTION", "CONTEXTUAL_REVISION"],
            "removed_vulnerability_terms": list(set(removed_terms)),
            "added_sanitized_terms": list(set(added_sanitized)),
            "html_diff": html_diff
        }

    def analyze_transcript_edits(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes all edited answers across the intake session.
        """
        edited_records = []
        total_edits = 0
        total_sanitizations = 0

        for item in transcript:
            if item.get("isEdited") and item.get("originalAnswer"):
                total_edits += 1
                diff_res = self.analyze_diff(item["originalAnswer"], item["finalAnswer"])

                if diff_res["sanitization_detected"]:
                    total_sanitizations += 1

                edited_records.append({
                    "step": item.get("step"),
                    "stage": item.get("stage"),
                    "question": item.get("question"),
                    "original_answer": item["originalAnswer"],
                    "final_answer": item["finalAnswer"],
                    "edit_type": diff_res["edit_type"],
                    "edit_type_label": diff_res["edit_type_label"],
                    "is_substantive": diff_res["is_substantive"],
                    "similarity_ratio": diff_res["similarity_ratio"],
                    "sanitization_detected": diff_res["sanitization_detected"],
                    "removed_vulnerability_terms": diff_res["removed_vulnerability_terms"],
                    "added_sanitized_terms": diff_res["added_sanitized_terms"],
                    "html_diff": diff_res["html_diff"]
                })

        if total_sanitizations >= 2:
            clinical_takeaway = "Active emotional sanitization detected across multiple answers. The client initially typed vivid, distressing experiences, but subsequently backtracked and replaced them with neutralized, socially composed wording."
        elif total_edits > 0:
            clinical_takeaway = "Answer revisions observed. The client edited specific responses, showing conscious deliberation in how symptoms are framed."
        else:
            clinical_takeaway = "No edited responses. The client submitted initial responses without retrospective revision."

        return {
            "total_edits": total_edits,
            "total_sanitizations": total_sanitizations,
            "has_edits": total_edits > 0,
            "records": edited_records,
            "clinical_takeaway": clinical_takeaway
        }
