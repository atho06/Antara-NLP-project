from crisis_detection import detect_crisis


test_messages = [

    "I have been feeling stressed lately.",

    "I want to kill myself.",

    "I am happy today.",

    "Sometimes I think about hurting myself.",

    "I am worried about my exams.",
    "I want to kill.",
    "I feel like killing.",
    "I feel like hurting myself.",
    "I want to end it.",
    "I cannot go on."
]


for message in test_messages:

    result = detect_crisis(message)

    print("Message:", message)
    print("Crisis detected:", result)
    print("---------------------------")