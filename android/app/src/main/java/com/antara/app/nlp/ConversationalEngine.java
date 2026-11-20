package com.antara.app.nlp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class ConversationalEngine {

    public static class DialogueResponse {
        public final String acknowledgement;
        public final String followUpQuestion;
        public final List<String> options;
        public final String detectedTopic;

        public DialogueResponse(String acknowledgement, String followUpQuestion, List<String> options, String detectedTopic) {
            this.acknowledgement = acknowledgement;
            this.followUpQuestion = followUpQuestion;
            this.options = options != null ? options : new ArrayList<>();
            this.detectedTopic = detectedTopic;
        }

        public String getFullBotMessage() {
            if (acknowledgement != null && !acknowledgement.isEmpty()) {
                return acknowledgement + "\n\n" + followUpQuestion;
            }
            return followUpQuestion;
        }
    }

    // Keyword topic detectors
    private static final String[] WORK_KEYWORDS = new String[]{
            "work", "study", "studies", "exam", "exams", "test", "deadline", "assignment", 
            "college", "job", "career", "boss", "rushed", "hectic", "pressure", "behind in life",
            "fail", "failing", "marks", "grades"
    };

    private static final String[] SLEEP_TIRED_KEYWORDS = new String[]{
            "sleep", "tired", "exhausted", "exhausting", "energy", "body", "drained", 
            "headache", "insomnia", "bed", "restless", "fatigue", "nap", "waking up", "heavy"
    };

    private static final String[] LONELY_KEYWORDS = new String[]{
            "lonely", "alone", "isolated", "disconnect", "disconnected", "nobody", "no one", 
            "unseen", "unheard", "distance", "distant", "misunderstood", "left out"
    };

    private static final String[] ANXIETY_KEYWORDS = new String[]{
            "anxious", "anxiety", "panic", "worried", "worry", "overthinking", "racing", 
            "heartbeat", "paralysis", "scared", "fear", "nervous", "tension"
    };

    private static final String[] SADNESS_KEYWORDS = new String[]{
            "sad", "sadness", "crying", "cry", "tears", "low", "hopeless", "empty", 
            "grief", "hurting", "hurt", "depressed", "sorrow", "pain"
    };

    private static final String[] RELATIONSHIP_KEYWORDS = new String[]{
            "friend", "friends", "family", "mother", "father", "parents", "partner", 
            "relationship", "boyfriend", "girlfriend", "brother", "sister", "arguing", "conflict"
    };

    private static final String[] POSITIVE_KEYWORDS = new String[]{
            "happy", "peaceful", "peace", "calm", "grateful", "good", "great", "smile", 
            "tea", "coffee", "walk", "nature", "sunlight", "relief", "better", "accomplished"
    };

    private static boolean containsAny(String text, String[] keywords) {
        String lower = text.toLowerCase(Locale.ROOT);
        for (String k : keywords) {
            if (lower.contains(k)) return true;
        }
        return false;
    }

    public static DialogueResponse generateContextualResponse(String userText, int turnCount, Set<String> previousTopics) {
        if (userText == null) userText = "";
        String lower = userText.toLowerCase(Locale.ROOT);

        // 1. Detect Domain Topic from what user said
        String topic = "GENERAL";

        if (containsAny(lower, WORK_KEYWORDS)) {
            topic = "WORK_PRESSURE";
        } else if (containsAny(lower, SLEEP_TIRED_KEYWORDS)) {
            topic = "EXHAUSTION_SLEEP";
        } else if (containsAny(lower, LONELY_KEYWORDS)) {
            topic = "LONELINESS";
        } else if (containsAny(lower, ANXIETY_KEYWORDS)) {
            topic = "ANXIETY";
        } else if (containsAny(lower, SADNESS_KEYWORDS)) {
            topic = "SADNESS";
        } else if (containsAny(lower, RELATIONSHIP_KEYWORDS)) {
            topic = "RELATIONSHIPS";
        } else if (containsAny(lower, POSITIVE_KEYWORDS)) {
            topic = "POSITIVE";
        }

        previousTopics.add(topic);

        // 2. Progressive Dialogue Logic (Connected conversational flow)
        switch (topic) {

            case "WORK_PRESSURE":
                if (turnCount <= 2) {
                    return new DialogueResponse(
                            "Academic and work pressure can feel like a suffocating weight, especially when expectations keep piling up.",
                            "When that rush and pressure builds up, what is the loudest thought playing in your head?",
                            Arrays.asList(
                                    "Fear of disappointing others",
                                    "Feeling behind compared to everyone",
                                    "Pressure to make everything perfect",
                                    "Feeling paralyzed & unable to start",
                                    "Just wanting everything to pause"
                            ),
                            topic
                    );
                } else {
                    return new DialogueResponse(
                            "Carrying those high expectations for so long is deeply exhausting.",
                            "If you were to gently lower your expectations for yourself today by just 10%, what could you give yourself permission to postpone or let go of?",
                            Arrays.asList(
                                    "Stop studying/working earlier tonight",
                                    "Accept 'good enough' instead of perfect",
                                    "Take a full, guilt-free break",
                                    "Say no to non-essential demands",
                                    "Forgive myself for feeling behind"
                            ),
                            topic
                    );
                }

            case "EXHAUSTION_SLEEP":
                if (turnCount <= 2) {
                    return new DialogueResponse(
                            "When your body and mind are this drained, even small daily routines can take twice the energy.",
                            "Does this tiredness feel more like physical fatigue in your body, or is it your mind that won't stop running?",
                            Arrays.asList(
                                    "Mostly physical body exhaustion",
                                    "My mind is constantly racing",
                                    "Both mind and body feel empty",
                                    "Feeling numb and unmotivated",
                                    "Restless and unable to settle"
                            ),
                            topic
                    );
                } else {
                    return new DialogueResponse(
                            "It makes complete sense that your body is asking for deep rest right now.",
                            "What is one tiny, gentle comfort you can give your body before today ends?",
                            Arrays.asList(
                                    "An early night with no phone screens",
                                    "A warm drink or comforting meal",
                                    "Lying down in quiet darkness for 20 mins",
                                    "A slow, warm shower or bath",
                                    "Soft, comfortable clothes & cozy blanket"
                            ),
                            topic
                    );
                }

            case "LONELINESS":
                if (turnCount <= 2) {
                    return new DialogueResponse(
                            "Feeling lonely or disconnected is such a quiet, aching feeling to sit with.",
                            "Do you notice this distance mostly when you're by yourself, or does it happen even when you are surrounded by people?",
                            Arrays.asList(
                                    "Even when surrounded by people",
                                    "Mostly when I am alone in my room",
                                    "Feeling like no one truly understands me",
                                    "I find myself pulling away & isolating",
                                    "It comes in unexpected waves"
                            ),
                            topic
                    );
                } else {
                    return new DialogueResponse(
                            "Feeling unseen around others is often the loneliest place of all.",
                            "If there was one person who could sit with you right now without any expectations, who would you feel safest around?",
                            Arrays.asList(
                                    "A close friend who listens without advice",
                                    "A family member or partner",
                                    "A pet or just quiet nature",
                                    "Prefer to be alone, but feel heard here",
                                    "I haven't found that person yet"
                            ),
                            topic
                    );
                }

            case "ANXIETY":
                if (turnCount <= 2) {
                    return new DialogueResponse(
                            "Anxiety and that racing sensation in your chest can be so distressing to experience.",
                            "When your mind starts spiraling with worry, where in your body do you notice that tension holding on the most?",
                            Arrays.asList(
                                    "Tightness in my chest or throat",
                                    "Shoulders, neck and jaw clenching",
                                    "A churning feeling in my stomach",
                                    "Shallow breathing or trembling",
                                    "A foggy, racing headache"
                            ),
                            topic
                    );
                } else {
                    return new DialogueResponse(
                            "Let's soften your shoulders and take a slow, full breath right now together. You are safe in this moment.",
                            "Would it feel comforting to try a short grounding pause, or do you prefer to keep expressing what triggered this?",
                            Arrays.asList(
                                    "Let's take a 1-minute slow breathing pause",
                                    "I want to keep talking and express more",
                                    "Help me untangle what's worrying me",
                                    "I just need to know it's going to be okay",
                                    "I feel a tiny bit lighter having shared"
                            ),
                            topic
                    );
                }

            case "SADNESS":
                if (turnCount <= 2) {
                    return new DialogueResponse(
                            "I hear the heavy sorrow in what you're feeling, and it is completely okay to not be okay right now.",
                            "Have you been carrying this sadness quietly on your own, or has anyone around you noticed?",
                            Arrays.asList(
                                    "Hiding it completely from everyone",
                                    "A few people noticed I'm quiet",
                                    "Trying to act normal on the outside",
                                    "Too exhausted to even pretend today",
                                    "I've shared a little bit with someone"
                            ),
                            topic
                    );
                } else {
                    return new DialogueResponse(
                            "Putting on a brave face every day takes so much hidden strength. You don't have to pretend here.",
                            "If you could give yourself one kind, forgiving permission slip today, what would it say?",
                            Arrays.asList(
                                    "'It is okay to cry and feel sad'",
                                    "'You don't have to fix everything today'",
                                    "'You are worthy of care, even when low'",
                                    "'Rest is not something you have to earn'",
                                    "'Take it one breath at a time'"
                            ),
                            topic
                    );
                }

            case "RELATIONSHIPS":
                if (turnCount <= 2) {
                    return new DialogueResponse(
                            "Relationships are often our biggest source of joy, but also where we feel the most vulnerability and hurt.",
                            "In this dynamic, do you feel like your thoughts and feelings are being given enough space?",
                            Arrays.asList(
                                    "I feel silenced or dismissed",
                                    "I end up prioritizing their feelings first",
                                    "There is a lot of unspoken tension",
                                    "It feels warm, but we've drifted apart",
                                    "I find it hard to express my real needs"
                            ),
                            topic
                    );
                } else {
                    return new DialogueResponse(
                            "It takes so much emotional energy to constantly navigate other people's needs.",
                            "What is one small boundary or space you might need to preserve for yourself right now?",
                            Arrays.asList(
                                    "Not responding to messages immediately",
                                    "Taking some quiet time alone",
                                    "Saying an honest 'no' without guilt",
                                    "Speaking my mind gently but firmly",
                                    "Letting go of trying to fix their mood"
                            ),
                            topic
                    );
                }

            case "POSITIVE":
                return new DialogueResponse(
                        "There is so much quiet warmth in that. It's beautiful to pause and notice moments that bring relief.",
                        "When you experienced that calm or peaceful moment, how did it shift how you felt inside?",
                        Arrays.asList(
                                "My chest felt lighter and looser",
                                "Gave me breathing room for a while",
                                "Felt brief, but reminded me I can feel okay",
                                "Made me want to protect moments like that",
                                "Helped me reset my mind"
                        ),
                        topic
                );

            default: // GENERAL
                if (turnCount <= 2) {
                    return new DialogueResponse(
                            "Thank you for sharing that with me so honestly. It takes real courage to open up.",
                            "When you think about where you are right now, what is the biggest thing you wish someone understood about what you're going through?",
                            Arrays.asList(
                                    "How exhausted I truly am inside",
                                    "That I'm trying my best even when it's hard",
                                    "That I just need a listening ear, not advice",
                                    "That I feel uncertain about my future",
                                    "That a little gentleness would mean the world"
                            ),
                            topic
                    );
                } else {
                    return new DialogueResponse(
                            "I hear you completely, and your feelings are completely valid.",
                            "Looking ahead to the rest of your day, what is one kind thing you can do purely for your peace of mind?",
                            Arrays.asList(
                                    "Take an early, quiet rest tonight",
                                    "Do something simple that makes me smile",
                                    "Put down all work and just breathe",
                                    "Reach out to someone I trust",
                                    "Be patient and gentle with myself"
                            ),
                            topic
                    );
                }
        }
    }
}
