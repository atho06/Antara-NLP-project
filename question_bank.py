QUESTION_BANK = {

    # ==============================================
    # STAGE 1: WELCOME AND CONSENT
    # Handled separately in app.py
    # ==============================================

    1: {
        "name": "Welcome and Consent",
        "questions": [
            {
                "id": "S1_Q1",
                "text": "Would you like to begin sharing how you have been feeling?",
                "type": "opening"
            },
            {
                "id": "S1_Q2",
                "text": "Do you understand how your conversation will be used and shared?",
                "type": "consent"
            }
        ]
    },


    # ==============================================
    # STAGE 2: CURRENT FEELINGS
    # ==============================================

    2: {
        "name": "Current Feelings",
        "questions": [
            {
                "id": "S2_Q1",
                "text": "How have you been feeling lately?",
                "type": "open"
            },
            {
                "id": "S2_Q2",
                "text": "What has been on your mind the most recently?",
                "type": "open"
            },
            {
                "id": "S2_Q3",
                "text": "How long have you been experiencing these feelings?",
                "type": "follow_up"
            }
        ]
    },


    # ==============================================
    # STAGE 3: EMOTIONS AND BODY SENSATIONS
    # ==============================================

    3: {
        "name": "Emotions and Body Sensations",
        "questions": [
            {
                "id": "S3_Q1",
                "text": "How do these feelings affect you emotionally or physically?",
                "type": "open"
            },
            {
                "id": "S3_Q2",
                "text": "How intense do these feelings usually get?",
                "type": "follow_up"
            }
        ]
    },


    # ==============================================
    # STAGE 4: SITUATIONS AND TRIGGERS
    # ==============================================

    4: {
        "name": "Situations and Triggers",
        "questions": [
            {
                "id": "S4_Q1",
                "text": "Are there particular situations that make these feelings stronger?",
                "type": "open"
            },
            {
                "id": "S4_Q2",
                "text": "Is anything happening in your life that you think might be contributing to these feelings?",
                "type": "open"
            }
        ]
    },


    # ==============================================
    # STAGE 5: DAILY LIFE
    # ==============================================

    5: {
        "name": "Daily Life",
        "questions": [
            {
                "id": "S5_Q1",
                "text": "Have these feelings affected your sleep, studies, work or daily routine?",
                "type": "open"
            },
            {
                "id": "S5_Q2",
                "text": "Have you noticed any changes in your energy or motivation?",
                "type": "follow_up"
            }
        ]
    },


    # ==============================================
    # STAGE 6: RELATIONSHIPS AND SUPPORT
    # ==============================================

    6: {
        "name": "Relationships and Support",
        "questions": [
            {
                "id": "S6_Q1",
                "text": "Do you feel comfortable sharing your feelings with someone you trust?",
                "type": "open"
            },
            {
                "id": "S6_Q2",
                "text": "How supported do you feel by the people around you?",
                "type": "follow_up"
            }
        ]
    },


    # ==============================================
    # STAGE 7: HOPES FOR THERAPY
    # ==============================================

    7: {
        "name": "Hopes for Therapy",
        "questions": [
            {
                "id": "S7_Q1",
                "text": "What would you most like to talk about during therapy?",
                "type": "open"
            },
            {
                "id": "S7_Q2",
                "text": "What would you like your therapist to understand about your experience?",
                "type": "open"
            },
            {
                "id": "S7_Q3",
                "text": "What kind of support are you hoping to receive?",
                "type": "open"
            }
        ]
    },


    # ==============================================
    # STAGE 8: CLOSING
    # ==============================================

    8: {
        "name": "Closing",
        "questions": [
            {
                "id": "S8_Q1",
                "text": "Is there anything else you would like your therapist to know?",
                "type": "open"
            },
            {
                "id": "S8_Q2",
                "text": "How are you feeling about sharing your experiences today?",
                "type": "closing"
            }
        ]
    }

}