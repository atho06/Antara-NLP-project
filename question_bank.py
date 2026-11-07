# ==========================================================
# ANTARA: LIA'S ADAPTIVE QUESTION BANK
# ==========================================================

QUESTION_BANK = {

    "introduction": {
        "id": "INTRO",
        "type": "opening",
        "message": (
            "Hi! I'm Lia, your companion here at Antara. 🌷\n\n"
            "I'm really glad you're here. This is a space where "
            "you can express yourself freely, without worrying "
            "about being judged.\n\n"
            "You don't have to have everything figured out. "
            "We can take things one step at a time. 💗"
        )
    },

    "time_preference": {
        "id": "TIME_01",
        "type": "choice",
        "question": "How much time would you like to spend with me today?",
        "options": [
            "5 minutes",
            "10 minutes",
            "15 minutes",
            "20 minutes",
            "I have plenty of time"
        ]
    },

    "emotional_checkin": {
        "id": "EMOTION_01",
        "type": "choice",
        "question": "How have you been feeling lately?",
        "options": [
            "Happy or peaceful",
            "A little stressed",
            "Anxious or worried",
            "Sad or low",
            "Lonely or disconnected",
            "Angry or frustrated",
            "Exhausted or overwhelmed",
            "I don't really know how I feel"
        ]
    },

    "general": {
        "name": "Understanding Your Feelings",
        "questions": [
            {
                "id": "GEN_01",
                "question": "What's been occupying your mind the most lately?",
                "tags": ["general", "thoughts"]
            },
            {
                "id": "GEN_02",
                "question": "Have these feelings been around for a few days, weeks or longer?",
                "tags": ["duration", "general"]
            },
            {
                "id": "GEN_03",
                "question": "Do you feel that you have someone who genuinely listens to you?",
                "tags": ["support", "general"]
            },
            {
                "id": "GEN_04",
                "question": "If you could change one thing about how you've been feeling, what would it be?",
                "tags": ["reflection", "general"]
            }
        ]
    },

    "stress": {
        "name": "Stress and Anxiety",
        "questions": [
            {
                "id": "STR_01",
                "question": "What situations tend to make you feel stressed or worried?",
                "tags": ["stress", "triggers"]
            },
            {
                "id": "STR_02",
                "question": "When you feel anxious, do you notice anything happening in your body, such as a racing heart, muscle tension or difficulty relaxing?",
                "tags": ["stress", "physical"]
            },
            {
                "id": "STR_03",
                "question": "Do you find yourself worrying about things even when you're trying to relax?",
                "tags": ["stress", "thoughts"]
            },
            {
                "id": "STR_04",
                "question": "What usually helps you feel a little calmer?",
                "tags": ["stress", "coping"]
            }
        ]
    },

    "sadness": {
        "name": "Sadness and Low Mood",
        "questions": [
            {
                "id": "SAD_01",
                "question": "Would you like to share what might be contributing to these feelings?",
                "tags": ["sadness", "triggers"]
            },
            {
                "id": "SAD_02",
                "question": "Have you noticed changes in the things you usually enjoy doing?",
                "tags": ["sadness", "daily_life"]
            },
            {
                "id": "SAD_03",
                "question": "Do you find it difficult to talk about your feelings with others?",
                "tags": ["sadness", "support"]
            },
            {
                "id": "SAD_04",
                "question": "What is one small thing that has brought you comfort recently?",
                "tags": ["sadness", "coping"]
            }
        ]
    },

    "loneliness": {
        "name": "Loneliness and Connection",
        "questions": [
            {
                "id": "LON_01",
                "question": "Do you sometimes feel lonely even when you're surrounded by people?",
                "tags": ["loneliness", "relationships"]
            },
            {
                "id": "LON_02",
                "question": "Is there someone with whom you feel comfortable being yourself?",
                "tags": ["loneliness", "support"]
            },
            {
                "id": "LON_03",
                "question": "What kind of connection or support do you wish you had right now?",
                "tags": ["loneliness", "support"]
            }
        ]
    },

    "relationships": {
        "name": "Relationships",
        "questions": [
            {
                "id": "REL_01",
                "question": "How have your relationships with family, friends or a partner been lately?",
                "tags": ["relationships"]
            },
            {
                "id": "REL_02",
                "question": "Do you feel respected and heard in your relationships?",
                "tags": ["relationships", "boundaries"]
            },
            {
                "id": "REL_03",
                "question": "Do you ever feel pressured to do things that you're uncomfortable with?",
                "tags": ["relationships", "boundaries", "safety"]
            },
            {
                "id": "REL_04",
                "question": "Do you feel safe in the relationships and environments around you?",
                "tags": ["relationships", "safety"]
            }
        ]
    },

    "physical_health": {
        "name": "Physical Well-being",
        "questions": [
            {
                "id": "PHY_01",
                "question": "Have you noticed any physical changes recently, such as headaches, body pain, fatigue or changes in appetite?",
                "tags": ["physical", "health"]
            },
            {
                "id": "PHY_02",
                "question": "How has your sleep been lately?",
                "tags": ["physical", "sleep"]
            },
            {
                "id": "PHY_03",
                "question": "Have you noticed any changes in your energy or concentration?",
                "tags": ["physical", "energy"]
            },
            {
                "id": "PHY_04",
                "question": "Have you discussed these physical concerns with a healthcare professional?",
                "tags": ["physical", "medical_support"]
            }
        ]
    },

    "daily_routine": {
        "name": "Daily Routine",
        "questions": [
            {
                "id": "DAY_01",
                "question": "How has your everyday routine been lately?",
                "tags": ["daily_life"]
            },
            {
                "id": "DAY_02",
                "question": "Are you getting enough time to rest and do things you enjoy?",
                "tags": ["daily_life", "self_care"]
            },
            {
                "id": "DAY_03",
                "question": "Have your feelings affected your studies, work or responsibilities?",
                "tags": ["daily_life", "functioning"]
            }
        ]
    },

    "safety": {
        "name": "Personal Safety",
        "questions": [
            {
                "id": "SAFE_01",
                "question": "Do you currently feel safe where you live and in the places you spend your time?",
                "tags": ["safety"]
            },
            {
                "id": "SAFE_02",
                "question": "Has anyone made you feel frightened, threatened or unsafe recently?",
                "tags": ["safety", "support"]
            },
            {
                "id": "SAFE_03",
                "question": "Is there someone you could contact if you needed help or felt unsafe?",
                "tags": ["safety", "support"]
            }
        ]
    },

    "therapy_goals": {
        "name": "Your Hopes for Therapy",
        "questions": [
            {
                "id": "THER_01",
                "question": "What would you most like to work on or understand during therapy?",
                "tags": ["therapy"]
            },
            {
                "id": "THER_02",
                "question": "What would you like your therapist to understand about you?",
                "tags": ["therapy"]
            },
            {
                "id": "THER_03",
                "question": "What kind of support would make you feel comfortable?",
                "tags": ["therapy", "support"]
            }
        ]
    },

    "closing": {
        "name": "Closing",
        "questions": [
            {
                "id": "CLOSE_01",
                "question": "Is there anything else you'd like to share before we finish?",
                "tags": ["closing"]
            },
            {
                "id": "CLOSE_02",
                "question": "How are you feeling after our conversation?",
                "tags": ["closing", "emotional_checkin"]
            }
        ]
    }
}


# ==========================================================
# QUESTION-SPECIFIC QUICK RESPONSE OPTIONS
# ==========================================================

QUESTION_OPTIONS = {

    "GEN_01": [
        "My relationships",
        "Family problems",
        "Studies or work",
        "My health",
        "Financial worries",
        "My future",
        "Something I cannot explain"
    ],

    "GEN_02": [
    "Just today",
    "A few days",
    "A few weeks",
    "Several months",
    "For a long time",
    "I'm not sure",
    "Something else"
],

    "GEN_03": [
        "Yes, I have someone",
        "Sometimes",
        "Not really",
        "I find it difficult to open up",
        "I prefer being alone"
    ],

    "GEN_04": [
        "I want to feel peaceful",
        "I want to stop overthinking",
        "I want to feel understood",
        "I want to improve my relationships",
        "I want to feel confident",
        "I'm not sure yet"
    ],

    "STR_01": [
        "Studies or work pressure",
        "Family expectations",
        "Relationship problems",
        "Financial concerns",
        "Uncertainty about my future",
        "Too many responsibilities",
        "Something else"
    ],

    "STR_02": [
        "Racing heartbeat",
        "Muscle tension",
        "Headaches",
        "Difficulty sleeping",
        "Restlessness",
        "I don't notice physical changes",
        "Something else"
    ],

    "STR_03": [
        "Almost always",
        "Often",
        "Sometimes",
        "Rarely",
        "Never"
    ],

    "STR_04": [
        "Listening to music",
        "Talking to someone",
        "Going for a walk",
        "Sleeping or resting",
        "Being alone for a while",
        "Nothing seems to help yet"
    ],

    "SAD_01": [
        "Something happened recently",
        "Relationship difficulties",
        "Family concerns",
        "Feeling lonely",
        "Academic or work pressure",
        "I don't know why"
    ],

    "SAD_02": [
        "Yes, I have lost interest",
        "A little",
        "I still enjoy my activities",
        "I haven't noticed"
    ],

    "SAD_03": [
        "Yes, it's difficult",
        "I can talk to one person",
        "I keep everything to myself",
        "I'm afraid of being judged",
        "I don't know how to explain it"
    ],

    "SAD_04": [
        "Music",
        "Talking to someone",
        "Spending time with family",
        "Being outdoors",
        "Resting",
        "Nothing recently"
    ],

    "LON_01": [
        "Yes, very often",
        "Sometimes",
        "Not usually",
        "I mostly prefer being alone"
    ],

    "LON_02": [
        "Yes, definitely",
        "I have one person",
        "Not at the moment",
        "I find it difficult to trust people"
    ],

    "LON_03": [
        "Someone to listen",
        "More meaningful friendships",
        "Emotional support",
        "Someone who understands me",
        "More time with loved ones",
        "I'm not sure"
    ],

    "REL_01": [
        "Things are going well",
        "There are occasional disagreements",
        "I feel misunderstood",
        "I feel distant from someone",
        "There is frequent conflict",
        "I'd rather explain in my own words"
    ],

    "REL_02": [
        "Yes, most of the time",
        "Sometimes",
        "Rarely",
        "No, I don't feel heard",
        "I'm not sure"
    ],

    "REL_03": [
        "Yes, sometimes",
        "Often",
        "Rarely",
        "No",
        "I'd rather not answer"
    ],

    "REL_04": [
        "Yes, I feel safe",
        "Sometimes",
        "No, I don't feel safe",
        "I'm not sure",
        "I'd rather not answer"
    ],

    "PHY_01": [
        "Headaches",
        "Body pain",
        "Fatigue",
        "Appetite changes",
        "Stomach discomfort",
        "No noticeable changes",
        "Something else"
    ],

    "PHY_02": [
        "I sleep well",
        "I struggle to fall asleep",
        "I wake up frequently",
        "I sleep too much",
        "My sleep schedule is irregular"
    ],

    "PHY_03": [
        "I feel energetic",
        "I feel tired frequently",
        "I struggle to concentrate",
        "Both energy and concentration are affected",
        "No noticeable changes"
    ],

    "PHY_04": [
        "Yes",
        "Not yet",
        "I am planning to",
        "I would prefer not to answer"
    ],

    "DAY_01": [
        "My routine is mostly fine",
        "My days feel very busy",
        "My routine is irregular",
        "I struggle to get things done",
        "I don't have a fixed routine"
    ],

    "DAY_02": [
        "Yes, I get enough rest",
        "Sometimes",
        "I rarely get time for myself",
        "I feel guilty when I rest",
        "I haven't been taking care of myself"
    ],

    "DAY_03": [
        "Yes, significantly",
        "A little",
        "Not really",
        "I'm not sure"
    ],

    "SAFE_01": [
        "Yes, I feel safe",
        "Sometimes",
        "No",
        "I'd rather not answer"
    ],

    "SAFE_02": [
        "Yes",
        "Sometimes",
        "No",
        "I'd rather not answer"
    ],

    "SAFE_03": [
        "Yes, I have someone",
        "I have a few people",
        "Not at the moment",
        "I'm not sure"
    ],

    "THER_01": [
        "Understand my emotions",
        "Manage stress and anxiety",
        "Improve my relationships",
        "Build confidence",
        "Understand recurring patterns",
        "I don't know yet"
    ],

    "THER_02": [
        "My personal experiences",
        "My family situation",
        "My relationships",
        "My fears and worries",
        "Things I find difficult to express",
        "Everything I have shared"
    ],

    "THER_03": [
        "Someone who listens patiently",
        "Practical coping strategies",
        "A non-judgmental environment",
        "Help understanding my feelings",
        "Taking things slowly"
    ],

    "CLOSE_01": [
        "I have shared everything for now",
        "There is something else",
        "I need more time",
        "I'd rather leave it here"
    ],

    "CLOSE_02": [
        "A little lighter",
        "The same as before",
        "Still overwhelmed",
        "Emotional",
        "Calmer",
        "I'm not sure"
    ]
}


# ==========================================================
# OPTIONAL WELLNESS ACTIVITIES
# ==========================================================

WELLNESS_ACTIVITIES = {

    "breathing": {
        "title": "🌬️ A Gentle Breathing Break",
        "description": (
            "Find a comfortable position. Breathe gently and "
            "naturally. If it feels comfortable, slowly breathe "
            "in and out for a minute. Stop if you feel dizzy "
            "or uncomfortable."
        ),
        "duration": "1 minute",
        "tags": ["stress", "anxiety", "overwhelmed"]
    },

    "nature": {
        "title": "🌳 Spend a Little Time in Nature",
        "description": (
            "If it's safe and accessible, spend a few minutes "
            "outside. Notice the trees, sky, sounds and fresh air. "
            "There's no need to achieve anything."
        ),
        "duration": "5 minutes",
        "tags": ["stress", "sadness", "overwhelmed"]
    },

    "walking": {
        "title": "🚶 Take a Gentle Walk",
        "description": (
            "If you feel physically comfortable, try a short "
            "walk at your own pace. You don't need to count "
            "steps or cover a particular distance."
        ),
        "duration": "5 to 10 minutes",
        "tags": ["stress", "low_energy", "overwhelmed"]
    },

    "grounding": {
        "title": "🌸 Try the 5-4-3-2-1 Exercise",
        "description": (
            "Notice 5 things you can see, 4 things you can feel, "
            "3 things you can hear, 2 things you can smell "
            "and 1 thing you can taste. Take your time."
        ),
        "duration": "3 minutes",
        "tags": ["anxiety", "stress", "overwhelmed"]
    },

    "visualization": {
        "title": "🌷 Imagine a Peaceful Place",
        "description": (
            "If closing your eyes feels comfortable, imagine "
            "a place where you feel peaceful. Picture the colours, "
            "sounds and surroundings. You can keep your eyes open "
            "if that feels better."
        ),
        "duration": "3 minutes",
        "tags": ["stress", "anxiety", "sadness"]
    },

    "journaling": {
        "title": "📖 Write Down Your Thoughts",
        "description": (
            "Take a moment to write whatever is on your mind. "
            "You don't need perfect sentences. This is just "
            "a space for your thoughts."
        ),
        "duration": "5 minutes",
        "tags": ["sadness", "stress", "thoughts"]
    },

    "meditation": {
        "title": "🧘 A Quiet Moment",
        "description": (
            "Sit somewhere comfortable. Notice your breathing "
            "and the sensations around you. When your mind wanders, "
            "gently bring your attention back. You don't need "
            "to force yourself to feel calm."
        ),
        "duration": "3 minutes",
        "tags": ["stress", "overwhelmed", "anxiety"]
    },

    "social_connection": {
        "title": "💗 Reach Out to Someone",
        "description": (
            "If there's someone you trust, consider sending them "
            "a message or spending a little time together. "
            "You don't have to explain everything."
        ),
        "duration": "Whenever you're comfortable",
        "tags": ["loneliness", "sadness", "support"]
    }
}