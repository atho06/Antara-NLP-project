import ollama
import json

MODEL_NAME = "llama3.2:3b"


def format_conversation_history(conversation_history):
    """
    Convert conversation history into the format
    expected by Ollama.

    Every message must contain:
    {
        "role": "user" or "assistant",
        "content": "message"
    }
    """

    formatted_messages = []

    if not isinstance(conversation_history, list):
        return formatted_messages

    for item in conversation_history[-12:]:

        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        # Already in Ollama message format
        if role in ["user", "assistant"] and content:
            formatted_messages.append({
                "role": role,
                "content": str(content)
            })
            continue

        # Convert question-answer history if available
        question = item.get("question")
        answer = item.get("answer")

        if question:
            formatted_messages.append({
                "role": "assistant",
                "content": str(question)
            })

        if answer:
            formatted_messages.append({
                "role": "user",
                "content": str(answer)
            })

    return formatted_messages


def generate_followup(question, answer, conversation_history=None):

    if conversation_history is None:
        conversation_history = []

    system_prompt = """
You are Lia, the supportive conversational assistant
for Antara, a pre-therapy intake application.

Your role is to help users express their feelings
before meeting a qualified therapist.

YOUR TASK:
Decide whether the user's latest answer needs
ONE short follow-up question.

FOLLOW-UP GUIDELINES:

1. Ask a follow-up when the answer is vague,
   incomplete, or needs important clarification.

2. Do not ask a follow-up when the answer is already
   clear and sufficiently detailed.

3. Short answers such as yes, no, okay, and good
   may need clarification depending on the question
   and conversation context.

4. Consider the user's previous answers before
   generating a follow-up.

5. Never repeat a question that has already been asked.

6. Ask only ONE question at a time.

7. Keep questions simple, gentle and conversational.

8. Use warm, supportive and non-judgmental language.

9. Never assume what the user is feeling.

10. Never diagnose mental-health conditions.

11. Never prescribe medication, treatment or therapy.

12. Never pressure users to share information.

13. Do not provide long explanations or advice.

14. If the answer is clear, do not generate an
    unnecessary follow-up.

15. If the user says they do not want to elaborate,
    respect that decision.

IMPORTANT:
You are an intake assistant, not a therapist.
Your purpose is to understand the user's experience,
not to interpret or judge it.

Return ONLY valid JSON in this format:

{
    "follow_up_needed": true,
    "message": "One short follow-up question"
}

If no follow-up is needed, return:

{
    "follow_up_needed": false,
    "message": "NONE"
}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Safely format previous conversation
    formatted_history = format_conversation_history(
        conversation_history
    )

    messages.extend(formatted_history)

    # Add the current question and answer
    messages.append({
        "role": "user",
        "content": (
            f"Current question: {question}\n"
            f"User's answer: {answer}\n\n"
            "Based on the current answer and conversation "
            "history, decide whether one follow-up "
            "question is necessary."
        )
    })

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            format="json",
            options={
                "temperature": 0.3
            }
        )

        response_content = response["message"]["content"]

        result = json.loads(response_content)

        # Validate AI response
        if not isinstance(result, dict):
            raise ValueError("Invalid AI response format")

        follow_up_needed = result.get("follow_up_needed")
        message = result.get("message")

        if not isinstance(follow_up_needed, bool):
            raise ValueError("Invalid follow-up decision")

        if not isinstance(message, str):
            raise ValueError("Invalid follow-up message")

        message = message.strip()

        if follow_up_needed:

            if not message or message.upper() == "NONE":
                raise ValueError("Missing follow-up question")

            # Ensure only one question is returned
            if message.count("?") > 1:
                message = message.split("?")[0].strip() + "?"

            return {
                "follow_up_needed": True,
                "message": message
            }

        return {
            "follow_up_needed": False,
            "message": "NONE"
        }

    except Exception as error:

        print("Ollama error:", error)

        # Continue safely if the model is unavailable
        return {
            "follow_up_needed": False,
            "message": "NONE"
        }