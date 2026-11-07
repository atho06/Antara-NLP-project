import ollama
import json
import re

from difflib import SequenceMatcher


# 1. MODEL CONFIGURATION

MODEL_NAME = "llama3.2:3b"



# ============================================================
# 1. MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "llama3.2:3b"


# ============================================================
# 2. TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# 3. SKIP AND BOUNDARY DETECTION
# ============================================================

def user_wants_to_skip(answer):

    if not isinstance(answer, str):
        return False

    normalized = normalize_text(answer)

    skip_phrases = [
        "skip",
        "skip this",
        "skip question",
        "next question",
        "prefer not to say",
        "i dont want to answer",
        "i do not want to answer",
        "i dont want to talk about it",
        "i do not want to talk about it",
        "not comfortable answering",
        "not comfortable sharing",
        "rather not say",
        "leave it",
        "move on",
        "no comment"
    ]

    return any(
        normalized == phrase
        or normalized.startswith(phrase + " ")
        for phrase in skip_phrases
    )


# ============================================================
# 4. CONVERSATION HISTORY
# ============================================================

def format_conversation_history(conversation_history):

    if not isinstance(conversation_history, list):
        return []

    formatted = []

    for message in conversation_history[-16:]:

        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content", "")

        if role not in ["user", "assistant"]:
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()

        if not content:
            continue

        formatted.append({
            "role": role,
            "content": content[:1200]
        })

    return formatted


# ============================================================
# 5. CONVERSATION MEMORY
# ============================================================

def build_conversation_memory(conversation_history):
    """
    Extract relevant details from previous conversation messages.

    This is contextual memory for the current session.
    It does not create permanent patient memory.
    """

    history = format_conversation_history(
        conversation_history
    )

    memory = []

    for message in history:

        if message["role"] == "user":

            content = message["content"].strip()

            if content:
                memory.append(content)

    return memory[-8:]


# ============================================================
# 6. PREVIOUS QUESTION EXTRACTION
# ============================================================

def extract_previous_questions(conversation_history):

    questions = []

    if not isinstance(conversation_history, list):
        return questions

    for message in conversation_history:

        if not isinstance(message, dict):
            continue

        if message.get("role") != "assistant":
            continue

        content = message.get("content", "")

        if not isinstance(content, str):
            continue

        found = re.findall(
            r"[^?]*\?",
            content
        )

        for item in found:

            item = item.strip()

            if item:
                questions.append(item)

    return questions[-16:]


# ============================================================
# 7. SIMILAR QUESTION DETECTION
# ============================================================

def is_repeated_question(new_question, previous_questions):

    new_text = normalize_text(new_question)

    if not new_text:
        return False

    stop_words = {
        "what", "when", "where", "why", "how",
        "is", "are", "was", "were", "do", "does",
        "did", "you", "your", "the", "a", "an",
        "to", "of", "in", "on", "for", "and",
        "or", "about", "can", "could", "would",
        "have", "has", "had", "it", "this",
        "that", "tell", "me", "please"
    }

    new_words = {
        word for word in new_text.split()
        if word not in stop_words and len(word) > 2
    }

    for previous in previous_questions:

        old_text = normalize_text(previous)

        if not old_text:
            continue

        if new_text == old_text:
            return True

        similarity = SequenceMatcher(
            None,
            new_text,
            old_text
        ).ratio()

        if similarity >= 0.84:
            return True

        old_words = {
            word for word in old_text.split()
            if word not in stop_words and len(word) > 2
        }

        if new_words and old_words:

            overlap = len(new_words.intersection(old_words))

            smaller_set = min(
                len(new_words),
                len(old_words)
            )

            if smaller_set > 0:

                overlap_ratio = overlap / smaller_set

                if overlap_ratio >= 0.80:
                    return True

    return False


# ============================================================
# 8. JSON RESPONSE CLEANING
# ============================================================

def clean_json_response(response):

    if isinstance(response, dict):
        return response

    if not isinstance(response, str):
        return {}

    response = response.strip()

    response = re.sub(
        r"^```json\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"^```\s*",
        "",
        response
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    try:
        return json.loads(response)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL
        )

        if match:

            try:
                return json.loads(match.group())

            except json.JSONDecodeError:
                pass

    return {}


# ============================================================
# 9. LIA SYSTEM PROMPT
# ============================================================

def get_system_prompt():

    return """
You are Lia, the conversational companion inside Antara,
a patient intake application.

PERSONALITY:

- Warm and calm.
- Respectful and non-judgmental.
- Patient and understanding.
- Natural and conversational.
- Never overly dramatic.

You are not a doctor or therapist.
Never diagnose the patient.

----------------------------------------
A. UNDERSTAND THE LATEST ANSWER
----------------------------------------

Always focus on the latest patient answer.

Understand what the patient actually communicated.

Acknowledge the specific information shared.

Do not use generic acknowledgements unnecessarily.

Example:

Question:
How have your studies been recently?

Answer:
I cannot concentrate.

Good:
"It sounds like concentrating on your studies
has been difficult recently."

----------------------------------------
B. CONTEXTUAL MEMORY
----------------------------------------

Use previous conversation details when relevant.

Remember information shared during this session.

For example:

Earlier answer:
I have been sleeping very late.

Latest answer:
I feel tired during classes.

You may acknowledge the connection carefully.

Good:
"You mentioned that your sleep schedule has
been irregular. Do you think that might be
affecting how you feel during classes?"

Never invent connections.

Never assume earlier information is still true.

Do not unnecessarily repeat personal details.

----------------------------------------
C. EMOTIONAL UNDERSTANDING
----------------------------------------

Identify emotional themes only when supported
by the patient's actual words.

Possible themes include:

- Stress
- Sadness
- Loneliness
- Frustration
- Fear
- Confusion
- Exhaustion
- Relationship difficulties

Do not assume a diagnosis.

Do not label the patient.

For factual answers, acknowledge the facts.

----------------------------------------
D. FOLLOW-UP QUESTIONS
----------------------------------------

Ask at most ONE follow-up question.

Ask only when additional information would
meaningfully improve the intake.

Good reasons to ask:

- The answer is unclear.
- Important context is missing.
- The patient has shared something they may
  want to explain further.
- A gentle clarification would be useful.

Do not ask follow-ups unnecessarily.

If the answer is already clear, do not ask another question.

----------------------------------------
E. QUESTION REPETITION
----------------------------------------

Never repeat an earlier question.

Do not ask different versions of the same question.

Use the previous conversation to identify
topics already discussed.

Choose a genuinely different question if needed.

----------------------------------------
F. RESPECT BOUNDARIES
----------------------------------------

If the patient skips a question:

- Respect the decision.
- Do not ask why.
- Do not pressure them.
- Do not ask another version of the question.

----------------------------------------
G. ACKNOWLEDGEMENTS
----------------------------------------

Keep acknowledgements concise.

Usually one sentence is enough.

Avoid:

- Repeating the entire answer.
- Excessive sympathy.
- Dramatic statements.
- Robotic phrases.
- Unnecessary motivational advice.

Vary your wording naturally.

----------------------------------------
H. SAFETY
----------------------------------------

If the patient mentions self-harm,
suicidal thoughts or immediate danger:

- Respond calmly.
- Do not minimize the situation.
- Encourage immediate human support.
- Encourage contacting emergency services
  when there is immediate danger.
- Never provide harmful instructions.

The separate application crisis system
handles crisis detection.

----------------------------------------
I. OUTPUT FORMAT
----------------------------------------

Return ONLY valid JSON.

Use exactly this structure:

{
    "acknowledgement": "Natural acknowledgement",
    "follow_up_needed": false,
    "follow_up_question": "",
    "message": "Complete response"
}

Rules:

- acknowledgement must be a string.
- follow_up_needed must be boolean.
- follow_up_question must be a string.
- message must be a string.
- Ask at most one follow-up question.
- Do not include markdown.
- Do not include text outside JSON.
"""


# ============================================================
# 10. RESPONSE VALIDATION
# ============================================================

def validate_lia_response(result, history=None, answer=None):

    if not isinstance(result, dict):
        result = {}

    acknowledgement = result.get(
        "acknowledgement",
        ""
    )

    follow_up_question = result.get(
        "follow_up_question",
        ""
    )

    follow_up_needed = result.get(
        "follow_up_needed",
        False
    )

    if not isinstance(acknowledgement, str):
        acknowledgement = ""

    if not isinstance(follow_up_question, str):
        follow_up_question = ""

    acknowledgement = acknowledgement.strip()
    follow_up_question = follow_up_question.strip()

    if not acknowledgement:
        acknowledgement = "Thank you for sharing that with me."

    # Respect skipped answers.
    if user_wants_to_skip(answer):

        follow_up_needed = False
        follow_up_question = ""

    # Validate follow-up format.
    if follow_up_question.count("?") != 1:

        follow_up_needed = False
        follow_up_question = ""

    # Check previously asked questions.
    previous_questions = extract_previous_questions(history)

    if follow_up_question:

        if is_repeated_question(
            follow_up_question,
            previous_questions
        ):

            follow_up_needed = False
            follow_up_question = ""

    if not isinstance(follow_up_needed, bool):
        follow_up_needed = False

    if not follow_up_question:
        follow_up_needed = False

    if follow_up_needed:

        message = (
            acknowledgement + " " + follow_up_question
        )

    else:

        message = acknowledgement

    return {
        "acknowledgement": acknowledgement,
        "follow_up_needed": follow_up_needed,
        "follow_up_question": follow_up_question,
        "message": message
    }


# ============================================================
# 11. GENERATE FOLLOW-UP
# ============================================================

def generate_followup(
    question,
    answer,
    conversation_history=None
):

    if user_wants_to_skip(answer):

        message = "That's completely okay. We can move on."

        return {
            "acknowledgement": message,
            "follow_up_needed": False,
            "follow_up_question": "",
            "message": message
        }

    history = format_conversation_history(
        conversation_history
    )

    previous_questions = extract_previous_questions(
        history
    )

    previous_questions_text = "\n".join(
        previous_questions
    )

    memory = build_conversation_memory(history)

    memory_text = "\n".join(memory)

    user_prompt = f"""
CURRENT QUESTION:
{question}

LATEST PATIENT ANSWER:
{answer}

RELEVANT DETAILS FROM EARLIER ANSWERS:
{memory_text}

PREVIOUS QUESTIONS ASKED BY LIA:
{previous_questions_text}

INSTRUCTIONS:

1. Acknowledge the latest answer.
2. Consider relevant earlier information.
3. Do not invent emotions or experiences.
4. Ask a follow-up only when genuinely useful.
5. Never repeat previous questions.
6. Respect boundaries.
7. Return the required JSON only.
"""

    messages = [
        {
            "role": "system",
            "content": get_system_prompt()
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": user_prompt
    })

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            format="json",
            options={
                "temperature": 0.35,
                "num_predict": 250
            }
        )

        raw_response = response["message"]["content"]

        result = clean_json_response(raw_response)

        return validate_lia_response(
            result,
            history=history,
            answer=answer
        )

    except Exception as e:

        print("Lia follow-up error:", e)

        acknowledgement = (
            "Thank you for sharing that with me."
        )

        return {
            "acknowledgement": acknowledgement,
            "follow_up_needed": False,
            "follow_up_question": "",
            "message": acknowledgement
        }


# ============================================================
# 12. FOLLOW-UP ACKNOWLEDGEMENT
# ============================================================

def generate_followup_acknowledgement(
    original_question,
    original_answer,
    followup_question,
    followup_answer,
    conversation_history=None
):

    if user_wants_to_skip(followup_answer):

        return (
            "That's completely okay. Thank you for "
            "sharing what you feel comfortable with."
        )

    history = format_conversation_history(
        conversation_history
    )

    system_prompt = """
You are Lia, a warm and respectful patient intake companion.

Acknowledge the patient's latest follow-up answer.

Rules:

1. Focus on the latest answer.
2. Connect earlier information only when relevant.
3. Never invent emotions or circumstances.
4. Do not exaggerate the situation.
5. Do not repeat the answer word for word.
6. Use natural conversational language.
7. Keep it to one or two sentences.
8. Do not ask another question.
9. Do not diagnose or provide medical advice.
10. Return only the acknowledgement.
"""

    user_prompt = f"""
ORIGINAL QUESTION:
{original_question}

ORIGINAL ANSWER:
{original_answer}

FOLLOW-UP QUESTION:
{followup_question}

LATEST FOLLOW-UP ANSWER:
{followup_answer}

RECENT CONVERSATION:
{json.dumps(history, ensure_ascii=False)}

Write a short acknowledgement of the latest answer.
"""

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            options={
                "temperature": 0.35,
                "num_predict": 120
            }
        )

        acknowledgement = (
            response["message"]["content"].strip()
        )

        acknowledgement = acknowledgement.strip('"').strip("'")

        if not acknowledgement or "?" in acknowledgement:

            return "Thank you for sharing that with me."

        return acknowledgement

    except Exception as e:

        print("Lia acknowledgement error:", e)

        return "Thank you for sharing that with me."


# ============================================================
# 13. WELLNESS SUGGESTION
# ============================================================

def generate_wellness_suggestion(
    emotional_theme,
    conversation_history=None
):

    history = format_conversation_history(
        conversation_history
    )

    system_prompt = """
You are Lia, a supportive wellness companion.

Suggest ONE simple, safe and optional wellness activity.

Rules:

- Keep it gentle and practical.
- Do not diagnose.
- Do not promise results.
- Do not pressure the patient.
- Avoid medical claims.
- Use simple language.
- Keep the suggestion brief.
"""

    user_prompt = f"""
CURRENT EMOTIONAL THEME:
{emotional_theme}

RECENT CONVERSATION:
{json.dumps(history, ensure_ascii=False)}

Suggest one appropriate wellness activity.
"""

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            options={
                "temperature": 0.4,
                "num_predict": 120
            }
        )

        return response["message"]["content"].strip()

    except Exception as e:

        print("Lia wellness suggestion error:", e)

        return (
            "You could take a few quiet minutes for yourself "
            "and try some slow, comfortable breathing."
        )


# ============================================================
# 2. TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for comparison.
    """

    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# 3. USER BOUNDARY / SKIP DETECTION
# ============================================================

def user_wants_to_skip(answer):
    """
    Detect whether the user wants to skip or avoid a question.
    """

    if not isinstance(answer, str):
        return False

    normalized = normalize_text(answer)

    skip_phrases = [
        "skip",
        "skip this",
        "skip question",
        "next question",
        "prefer not to say",
        "i dont want to answer",
        "i do not want to answer",
        "i dont want to talk about it",
        "i do not want to talk about it",
        "not comfortable answering",
        "not comfortable sharing",
        "rather not say",
        "leave it",
        "move on",
        "no comment"
    ]

    return any(
        normalized == phrase
        or normalized.startswith(phrase + " ")
        for phrase in skip_phrases
    )


# ============================================================
# 4. CONVERSATION HISTORY
# ============================================================

def format_conversation_history(conversation_history):
    """
    Format recent conversation history for Ollama.
    """

    if not isinstance(conversation_history, list):
        return []

    formatted = []

    for message in conversation_history[-16:]:

        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content", "")

        if role not in ["user", "assistant"]:
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()

        if not content:
            continue

        formatted.append({
            "role": role,
            "content": content[:1200]
        })

    return formatted


# ============================================================
# 5. EXTRACT PREVIOUS QUESTIONS
# ============================================================

def extract_previous_questions(conversation_history):
    """
    Extract questions already asked by Lia.
    """

    questions = []

    if not isinstance(conversation_history, list):
        return questions

    for message in conversation_history:

        if not isinstance(message, dict):
            continue

        if message.get("role") != "assistant":
            continue

        content = message.get("content", "")

        if not isinstance(content, str):
            continue

        found = re.findall(
            r"[^?]*\?",
            content
        )

        for item in found:

            item = item.strip()

            if item:
                questions.append(item)

    return questions[-12:]


# ============================================================
# 6. SIMILAR QUESTION DETECTION
# ============================================================

def is_repeated_question(new_question, previous_questions):
    """
    Detect exact and similar questions.

    Uses:
    1. Exact normalized comparison.
    2. SequenceMatcher similarity.
    3. Meaningful word overlap.
    """

    new_text = normalize_text(new_question)

    if not new_text:
        return False

    stop_words = {
        "what", "when", "where", "why", "how",
        "is", "are", "was", "were", "do", "does",
        "did", "you", "your", "the", "a", "an",
        "to", "of", "in", "on", "for", "and",
        "or", "about", "can", "could", "would",
        "have", "has", "had", "it", "this",
        "that", "tell", "me", "please"
    }

    new_words = {
        word for word in new_text.split()
        if word not in stop_words and len(word) > 2
    }

    for previous in previous_questions:

        old_text = normalize_text(previous)

        if not old_text:
            continue

        # Exact match
        if new_text == old_text:
            return True

        # Similarity comparison
        similarity = SequenceMatcher(
            None,
            new_text,
            old_text
        ).ratio()

        if similarity >= 0.84:
            return True

        old_words = {
            word for word in old_text.split()
            if word not in stop_words and len(word) > 2
        }

        if new_words and old_words:

            overlap = len(new_words.intersection(old_words))

            smaller_set = min(
                len(new_words),
                len(old_words)
            )

            if smaller_set > 0:

                overlap_ratio = overlap / smaller_set

                if overlap_ratio >= 0.80:
                    return True

    return False


# ============================================================
# 7. CLEAN JSON RESPONSE
# ============================================================

def clean_json_response(response):
    """
    Clean and parse JSON returned by Ollama.
    """

    if isinstance(response, dict):
        return response

    if not isinstance(response, str):
        return {}

    response = response.strip()

    response = re.sub(
        r"^```json\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"^```\s*",
        "",
        response
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    try:
        return json.loads(response)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL
        )

        if match:

            try:
                return json.loads(match.group())

            except json.JSONDecodeError:
                pass

    return {}


# ============================================================
# 8. LIA SYSTEM PROMPT
# ============================================================

def get_system_prompt():

    return """
You are Lia, the conversational companion inside Antara,
a patient intake application.

YOUR PERSONALITY:

- Warm
- Calm
- Respectful
- Patient
- Non-judgmental
- Emotionally supportive
- Natural and conversational

You are not a doctor or therapist.
You must never diagnose a patient.

--------------------------------------------------
A. RESPOND TO THE LATEST ANSWER FIRST
--------------------------------------------------

Always prioritize the patient's latest answer.

Read the current question and answer carefully.

Your acknowledgement must directly relate to what
the patient actually said.

Do not respond using a generic acknowledgement
when a specific acknowledgement is possible.

Example:

Question:
How have your studies been recently?

Answer:
I am struggling to concentrate.

Good acknowledgement:
"It sounds like concentrating on your studies
has been difficult recently."

Bad acknowledgement:
"Sudden changes can be difficult to navigate."

--------------------------------------------------
B. NEVER ASSUME EMOTIONS OR EXPERIENCES
--------------------------------------------------

Only acknowledge feelings that the patient has
actually expressed.

Do not assume that the patient is:

- Depressed
- Anxious
- Distressed
- Lonely
- Afraid
- Overwhelmed
- Emotionally exhausted

unless their response supports that interpretation.

For short factual answers, acknowledge the fact.

Example:

Answer:
Several months.

Good:
"Thank you for sharing that it has been
happening for several months."

Bad:
"It sounds like you have been experiencing
significant emotional distress for months."

Another example:

Answer:
My family.

Good:
"Thank you for sharing that this is related
to your family."

Bad:
"It sounds like your family has been causing
you a lot of emotional pain."

--------------------------------------------------
C. USE PREVIOUS CONVERSATION CONTEXT
--------------------------------------------------

Consider earlier answers when they are relevant.

Do not ignore information the patient has already shared.

However:

- Do not repeat the same acknowledgement.
- Do not assume that earlier information is still true.
- Do not invent connections between unrelated answers.
- Do not unnecessarily repeat personal details.

--------------------------------------------------
D. FOLLOW-UP QUESTION RULES
--------------------------------------------------

You may ask ONE follow-up question when it would
help understand the patient's experience better.

Ask a follow-up only when:

- The answer needs clarification.
- An important detail is missing.
- More context would meaningfully improve intake.
- The patient has shared something that deserves
  a gentle opportunity to elaborate.

Do not ask a follow-up when:

- The answer is already sufficiently clear.
- The answer is purely factual and needs no clarification.
- A similar question has already been asked.
- The patient has skipped the question.
- The patient has expressed a boundary.

Avoid asking unnecessary questions just to continue
the conversation.

--------------------------------------------------
E. AVOID REPETITIVE QUESTIONS
--------------------------------------------------

Do not repeat questions already asked.

Avoid asking different versions of the same question.

For example, if you already asked:

"What has been difficult about your family situation?"

Do not ask:

"Can you tell me what is challenging about your family?"

Choose a different topic or do not ask another question.

--------------------------------------------------
F. RESPECT USER BOUNDARIES
--------------------------------------------------

If the patient does not want to answer:

- Respect their decision.
- Do not pressure them.
- Do not ask why they skipped.
- Do not ask another version of the same question.

--------------------------------------------------
G. ACKNOWLEDGEMENT STYLE
--------------------------------------------------

Keep acknowledgements natural and concise.

Usually one sentence is enough.

Avoid:

- Repeating the patient's entire answer.
- Overly dramatic emotional language.
- Excessive sympathy.
- Robotic phrases.
- Unnecessary motivational statements.

--------------------------------------------------
H. SAFETY
--------------------------------------------------

If the patient expresses self-harm, suicidal thoughts,
or immediate danger:

- Respond calmly and compassionately.
- Do not minimize the situation.
- Encourage immediate support from emergency services
  or a trusted person.
- Never provide harmful instructions.

The application's separate crisis detection system
handles crisis classification and safety escalation.

--------------------------------------------------
I. OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON.

Use this exact structure:

{
    "acknowledgement": "A natural acknowledgement",
    "follow_up_needed": false,
    "follow_up_question": "",
    "message": "The acknowledgement and follow-up question together"
}

Rules:

- acknowledgement must be a string.
- follow_up_needed must be true or false.
- follow_up_question must be a string.
- message must be a string.
- Ask at most one follow-up question.
- Do not include markdown.
- Do not include text outside JSON.
"""


# ============================================================
# 9. VALIDATE LIA RESPONSE
# ============================================================

def validate_lia_response(result, history=None, answer=None):
    """
    Validate the model response and enforce conversation rules.
    """

    if not isinstance(result, dict):
        result = {}

    acknowledgement = result.get(
        "acknowledgement",
        ""
    )

    follow_up_question = result.get(
        "follow_up_question",
        ""
    )

    follow_up_needed = result.get(
        "follow_up_needed",
        False
    )

    if not isinstance(acknowledgement, str):
        acknowledgement = ""

    if not isinstance(follow_up_question, str):
        follow_up_question = ""

    acknowledgement = acknowledgement.strip()
    follow_up_question = follow_up_question.strip()

    if not acknowledgement:
        acknowledgement = "Thank you for sharing that with me."

    # Respect skipped answers and boundaries.
    if user_wants_to_skip(answer):

        follow_up_needed = False
        follow_up_question = ""

    # Ensure only one question is asked.
    question_marks = follow_up_question.count("?")

    if question_marks != 1:

        follow_up_needed = False
        follow_up_question = ""

    # Prevent repeated or similar questions.
    previous_questions = extract_previous_questions(history)

    if follow_up_question:

        if is_repeated_question(
            follow_up_question,
            previous_questions
        ):

            follow_up_needed = False
            follow_up_question = ""

    if not isinstance(follow_up_needed, bool):
        follow_up_needed = False

    if not follow_up_question:
        follow_up_needed = False

    if follow_up_needed:

        message = (
            acknowledgement + " " + follow_up_question
        )

    else:

        message = acknowledgement

    return {
        "acknowledgement": acknowledgement,
        "follow_up_needed": follow_up_needed,
        "follow_up_question": follow_up_question,
        "message": message
    }


# ============================================================
# 10. GENERATE FOLLOW-UP
# ============================================================

def generate_followup(
    question,
    answer,
    conversation_history=None
):
    """
    Generate an acknowledgement and optional follow-up question.
    """

    if user_wants_to_skip(answer):

        return {
            "acknowledgement": "That's completely okay. We can move on.",
            "follow_up_needed": False,
            "follow_up_question": "",
            "message": "That's completely okay. We can move on."
        }

    history = format_conversation_history(
        conversation_history
    )

    previous_questions = extract_previous_questions(
        history
    )

    previous_questions_text = "\n".join(
        previous_questions
    )

    user_prompt = f"""
CURRENT QUESTION:
{question}

PATIENT'S LATEST ANSWER:
{answer}

PREVIOUS QUESTIONS ASKED BY LIA:
{previous_questions_text}

RECENT CONVERSATION:
{json.dumps(history, ensure_ascii=False)}

INSTRUCTIONS:

1. Focus on the latest answer.
2. Acknowledge only what the patient actually shared.
3. Do not invent emotions or experiences.
4. Use previous context only when relevant.
5. Decide whether one follow-up question is genuinely useful.
6. Do not repeat or rephrase previous questions.
7. Respect the patient's boundaries.
8. Return only the required JSON.
"""

    messages = [
        {
            "role": "system",
            "content": get_system_prompt()
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": user_prompt
    })

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            format="json",
            options={
                "temperature": 0.25,
                "num_predict": 250
            }
        )

        raw_response = response["message"]["content"]

        result = clean_json_response(raw_response)

        return validate_lia_response(
            result,
            history=history,
            answer=answer
        )

    except Exception as e:

        print("Lia follow-up error:", e)

        acknowledgement = (
            "Thank you for sharing that with me."
        )

        return {
            "acknowledgement": acknowledgement,
            "follow_up_needed": False,
            "follow_up_question": "",
            "message": acknowledgement
        }


# ============================================================
# 11. GENERATE FOLLOW-UP ACKNOWLEDGEMENT
# ============================================================

def generate_followup_acknowledgement(
    original_question,
    original_answer,
    followup_question,
    followup_answer,
    conversation_history=None
):
    """
    Generate a natural acknowledgement after the patient
    answers Lia's follow-up question.

    This function does not generate another question.
    """

    if user_wants_to_skip(followup_answer):

        return "That's completely okay. Thank you for sharing what you feel comfortable with."

    history = format_conversation_history(
        conversation_history
    )

    system_prompt = """
You are Lia, a warm and respectful patient intake companion.

Your task is to acknowledge the patient's latest answer
to a follow-up question.

IMPORTANT RULES:

1. Focus on the latest follow-up answer.
2. Connect it to the original answer only when relevant.
3. Never invent emotions, experiences, or circumstances.
4. Do not exaggerate the patient's situation.
5. Do not repeat the patient's answer word for word.
6. Use natural, conversational language.
7. Keep the acknowledgement to one or two sentences.
8. Do not ask another question.
9. Do not provide medical diagnoses or advice.
10. Return only the acknowledgement, without JSON.
"""

    user_prompt = f"""
ORIGINAL QUESTION:
{original_question}

ORIGINAL ANSWER:
{original_answer}

FOLLOW-UP QUESTION:
{followup_question}

LATEST FOLLOW-UP ANSWER:
{followup_answer}

RECENT CONVERSATION:
{json.dumps(history, ensure_ascii=False)}

Write a short, natural acknowledgement of the latest answer.
Do not make assumptions.
Do not ask another question.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            options={
                "temperature": 0.3,
                "num_predict": 120
            }
        )

        acknowledgement = (
            response["message"]["content"].strip()
        )

        # Remove accidental quotation marks.
        acknowledgement = acknowledgement.strip('"').strip("'")

        # Prevent accidental questions.
        if "?" in acknowledgement:

            acknowledgement = (
                "Thank you for sharing that with me."
            )

        if not acknowledgement:

            acknowledgement = (
                "Thank you for sharing that with me."
            )

        return acknowledgement

    except Exception as e:

        print("Lia acknowledgement error:", e)

        return "Thank you for sharing that with me."


# ============================================================
# 12. WELLNESS SUGGESTION
# ============================================================

def generate_wellness_suggestion(
    emotional_theme,
    conversation_history=None
):
    """
    Generate a gentle wellness activity suggestion.
    """

    history = format_conversation_history(
        conversation_history
    )

    system_prompt = """
You are Lia, a supportive wellness companion.

Suggest one simple, safe, practical wellness activity.

Rules:

- Keep it gentle and optional.
- Do not diagnose.
- Do not promise results.
- Do not pressure the patient.
- Use simple language.
- Keep the suggestion brief.
"""

    user_prompt = f"""
The patient's current theme is:
{emotional_theme}

Recent conversation:
{json.dumps(history, ensure_ascii=False)}

Suggest one simple wellness activity.
"""

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            options={
                "temperature": 0.4,
                "num_predict": 120
            }
        )

        return response["message"]["content"].strip()

    except Exception as e:

        print("Lia wellness suggestion error:", e)

        return (
            "You could take a few quiet minutes for yourself "
            "and try some slow, comfortable breathing."
        )