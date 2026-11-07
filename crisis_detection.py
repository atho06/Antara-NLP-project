import re


# ==========================================================
# 1. CRISIS PATTERNS
# ==========================================================

CRISIS_PATTERNS = [

    # Self-harm
    r"\bself[- ]harm\b",
    r"\bhurt(?:ing)? myself\b",
    r"\bcut myself\b",
    r"\bwant to harm myself\b",
    r"\bwant to hurt myself\b",
    r"\bthinking about (?:hurting|harming) myself\b",
    r"\bthoughts? of (?:self[- ]harm|suicide)\b",
    r"\bi (?:might|may|could) hurt myself\b",
    r"\bi feel like (?:hurting|harming) myself\b",

    # Suicide
    r"\bwant to die\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bsuicidal\b",
    r"\bno reason to live\b",
    r"\bbetter off dead\b",
    r"\bend my own life\b",
    r"\btake my own life\b",
    r"\bi feel like killing myself\b",
    r"\bi want to end it\b",
    r"\bi don't want to live\b",
    r"\bi do not want to live\b",
    r"\bi don't want to be alive\b",
    r"\bi wish i was dead\b",
    r"\bi wish i were dead\b",

    # Threats towards others
    r"\bwant to kill someone\b",
    r"\bwanna kill someone\b",
    r"\bthinking about killing someone\b",
    r"\bthinking about killing people\b",
    r"\bi might kill someone\b",
    r"\bi may kill someone\b",
    r"\bi want to kill\b",
    r"\bi wanna kill\b",
    r"\bgoing to kill someone\b",
    r"\bgoing to kill people\b",
    r"\bwant to hurt someone\b",
    r"\bi might hurt someone\b",
    r"\bi may hurt someone\b",
    r"\bgoing to hurt someone\b",

    # Immediate danger
    r"\bin immediate danger\b",
    r"\bsomeone is threatening me\b",
    r"\bi am being threatened\b",
    r"\bi am not safe\b",
    r"\bi don't feel safe\b",

    # Other concerning expressions
    r"\bi can't go on\b",
    r"\bi cannot go on\b",
]


COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in CRISIS_PATTERNS
]


# ==========================================================
# 2. NEGATION HANDLING
# ==========================================================

NEGATION_PATTERNS = [
    r"\bi don't want to\b",
    r"\bi do not want to\b",
    r"\bi never want to\b",
    r"\bi would never\b",
    r"\bi am not going to\b",
    r"\bi'm not going to\b",
    r"\bi will not\b",
    r"\bi won't\b",
]


def is_negated(text, match_start):

    preceding_text = text[max(0, match_start - 60):match_start]

    for pattern in NEGATION_PATTERNS:

        if re.search(pattern, preceding_text, re.IGNORECASE):
            return True

    return False


# ==========================================================
# 3. CRISIS DETECTION
# ==========================================================

def detect_crisis(message):

    if not isinstance(message, str):
        return False

    text = message.strip().lower()

    if not text:
        return False

    text = text.replace("’", "'")

    # Check each sentence separately.
    sentences = re.split(r"[.!?\n]+", text)

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        for pattern in COMPILED_PATTERNS:

            match = pattern.search(sentence)

            if match:

                if is_negated(sentence, match.start()):
                    continue

                return True

    return False