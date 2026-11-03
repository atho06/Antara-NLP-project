import re


# ==========================================
# CRISIS KEYWORD DETECTION
# ==========================================

CRISIS_PATTERNS = [

    # Self-harm
    r"\bself[- ]harm\b",
    r"\bhurt(?:ing)? myself\b",
    r"\bcut myself\b",
    r"\bwant to harm myself\b",
    r"\bthinking about (?:hurting|harming) myself\b",
    r"\bthoughts? of (?:self[- ]harm|suicide)\b",
    r"\bwant to (?:hurt|harm) myself\b",
    r"\bi (?:might|may|could) hurt myself\b",
    r"\bi feel like (?:hurting|harming) myself\b",
    # Threats towards other people
r"\bkill people\b",
r"\bwanna kill people\b",
r"\bwant to kill people\b",
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

    # Suicidal thoughts
    r"\bwant to die\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bsuicidal\b",
    r"\bno reason to live\b",
    r"\bbetter off dead\b",
    r"\b(?:end|take) my own life\b",
    r"\bi feel like killing myself\b",
    r"\bi want to end it\b",

    # Immediate danger
    r"\bin immediate danger\b",
    r"\bgoing to hurt someone\b",
    r"\bwant to hurt someone\b",
    r"\bi might hurt someone\b",
    r"\bi may hurt someone\b",

    # Additional concerning statements
    r"\bi can't go on\b",
    r"\bi cannot go on\b",
]


# Compile patterns for efficient matching
COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in CRISIS_PATTERNS
]


# ==========================================
# CRISIS DETECTION FUNCTION
# ==========================================

def detect_crisis(message):

    if not isinstance(message, str):
        return False

    text = message.strip().lower()

    if not text:
        return False

    # Normalize apostrophes
    text = text.replace("’", "'")

    for pattern in COMPILED_PATTERNS:

        if pattern.search(text):
            return True

    return False