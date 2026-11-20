package com.antara.app.nlp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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

    // --- Entity & Relational Keywords ---
    private static final String[] FAMILY_ENTITIES = {"mom", "mother", "dad", "father", "parents", "brother", "sister", "family"};
    private static final String[] SOCIAL_ENTITIES = {"friend", "friends", "best friend", "roommate", "colleague", "classmate", "partner", "boyfriend", "girlfriend"};
    private static final String[] ACADEMIC_ENTITIES = {"exam", "exams", "entrance exam", "test", "assignment", "college", "school", "project", "degree", "marks", "grades", "interview", "job", "career"};

    // --- Emotional & Somatic Distortions ---
    private static final String[] FAILURE_TERMS = {"failure", "disappointment", "disappointed", "let down", "ruined", "worthless", "not good enough", "loser", "useless"};
    private static final String[] CONFLICT_TERMS = {"fight", "fought", "argued", "arguing", "yelled", "shouted", "screaming", "angry with me", "blamed", "cut off", "ignore"};
    private static final String[] SOMATIC_CRYING_TERMS = {"crying", "cried", "tears", "shaking", "panic", "heart racing", "chest hurts", "can't breathe", "vomiting", "headache", "throwing up", "not eating", "haven't eaten"};
    private static final String[] NUMB_TERMS = {"numb", "empty", "staring at the wall", "staring at the ceiling", "spaced out", "detached", "autopilot", "feel nothing", "can't feel"};
    private static final String[] LONELINESS_TERMS = {"lonely", "alone", "isolated", "nobody", "no one", "no friends", "unseen", "unheard", "left out", "abandoned"};
    private static final String[] EXHAUSTION_TERMS = {"exhausted", "tired", "drained", "can't do this anymore", "burnout", "burned out", "no energy", "bed all day", "sleep"};
    private static final String[] POSITIVE_TERMS = {"happy", "peaceful", "peace", "calm", "grateful", "good", "great", "smile", "tea", "coffee", "walk", "nature", "sunlight", "relief", "better", "accomplished"};

    private static boolean containsAny(String text, String[] keywords) {
        String lower = text.toLowerCase(Locale.ROOT);
        for (String k : keywords) {
            if (lower.contains(k)) return true;
        }
        return false;
    }

    private static String findFirstMatch(String text, String[] keywords) {
        String lower = text.toLowerCase(Locale.ROOT);
        for (String k : keywords) {
            if (lower.contains(k)) return k;
        }
        return null;
    }

    /**
     * Inverts first-person statements to second-person reflective phrasing.
     * e.g., "i feel so overwhelmed by my studies" -> "feeling so overwhelmed by your studies"
     */
    private static String invertPerspective(String text) {
        if (text == null || text.trim().isEmpty()) return "";
        String clean = text.replaceAll("[.,!?;:]", "").trim();

        // Standard transformations
        clean = clean.replaceAll("(?i)\\bI am\\b", "you are");
        clean = clean.replaceAll("(?i)\\bI'm\\b", "you are");
        clean = clean.replaceAll("(?i)\\bI feel\\b", "you feel");
        clean = clean.replaceAll("(?i)\\bI have\\b", "you have");
        clean = clean.replaceAll("(?i)\\bI was\\b", "you were");
        clean = clean.replaceAll("(?i)\\bmy\\b", "your");
        clean = clean.replaceAll("(?i)\\bme\\b", "you");
        clean = clean.replaceAll("(?i)\\bmyself\\b", "yourself");
        clean = clean.replaceAll("(?i)\\bI\\b", "you");

        return clean;
    }

    public static DialogueResponse generateContextualResponse(String userText, int turnCount, Set<String> previousTopics) {
        if (userText == null) userText = "";
        String raw = userText.trim();
        String lower = raw.toLowerCase(Locale.ROOT);

        // --- 1. Specific High-Context Pattern Analysis ---

        // A. Conflict with Family/Parents + Feeling like a Failure/Disappointment
        if ((containsAny(lower, FAMILY_ENTITIES) || containsAny(lower, SOCIAL_ENTITIES)) 
                && (containsAny(lower, CONFLICT_TERMS) || containsAny(lower, FAILURE_TERMS))) {
            
            String entity = findFirstMatch(lower, FAMILY_ENTITIES);
            if (entity == null) entity = findFirstMatch(lower, SOCIAL_ENTITIES);
            if (entity == null) entity = "someone you care about";

            previousTopics.add("RELATIONAL_CONFLICT");
            return new DialogueResponse(
                    "Having a conflict with your " + entity + " and feeling that painful weight of being called or feeling like a disappointment hurts so deeply. That harsh judgment cuts right into your heart.",
                    "When parental or relational expectations clash with where your energy is right now, it can make home feel like the hardest place to breathe. Do you feel they truly understand how much you're already carrying inside?",
                    Arrays.asList(
                            "They don't understand at all",
                            "They want what's best, but it hurts",
                            "I feel guilty and angry at the same time",
                            "I feel completely alone in this",
                            "I'm terrified of letting them down"
                    ),
                    "RELATIONAL_CONFLICT"
            );
        }

        // B. Somatic Distress & Crying / Bodily Overwhelm
        if (containsAny(lower, SOMATIC_CRYING_TERMS)) {
            previousTopics.add("SOMATIC_OVERLOAD");
            return new DialogueResponse(
                    "I hear how intensely this is impacting your body right now. Crying and physical shaking are your nervous system's honest way of releasing pressure when everything has been held in for too long.",
                    "Right now, let's take things one quiet second at a time. What is one small, gentle comfort your body needs in this very moment?",
                    Arrays.asList(
                            "A glass of cool water",
                            "To lie down in a quiet, dark room",
                            "A slow, steady deep breath",
                            "A warm blanket or comfortable hoodie",
                            "Space to let the tears finish falling"
                    ),
                    "SOMATIC_OVERLOAD"
            );
        }

        // C. Academic & Career Overwhelm (Exams, Deadlines, Job, College)
        if (containsAny(lower, ACADEMIC_ENTITIES)) {
            String academicThing = findFirstMatch(lower, ACADEMIC_ENTITIES);
            if (academicThing == null) academicThing = "studies";

            previousTopics.add("ACADEMIC_PRESSURE");
            return new DialogueResponse(
                    "The relentless pressure around " + academicThing + " can make it feel like your entire future and self-worth are on trial every single day. That is an exhausting weight to carry.",
                    "When you look at this pressure right now, what is the loudest fear or worry running through your mind?",
                    Arrays.asList(
                            "Fear of failing and falling behind",
                            "Disappointing my parents or family",
                            "Feeling like I have no time or guidance",
                            "Feeling completely burned out & paralyzed",
                            "Worrying that my best isn't good enough"
                    ),
                    "ACADEMIC_PRESSURE"
            );
        }

        // D. Numbness, Apathy & Dissociation ("staring at wall", "feel numb", "empty")
        if (containsAny(lower, NUMB_TERMS)) {
            previousTopics.add("NUMBNESS_DISSOCIATION");
            return new DialogueResponse(
                    "Sitting in that numbness or finding yourself staring into space is often your mind's protective emergency brake when emotions have been running too high for too long. You are not broken for feeling this way.",
                    "When you are in that quiet, empty space, does it feel more like a heavy fog you can't push through, or like you are totally detached from the world around you?",
                    Arrays.asList(
                            "Like a heavy mental fog",
                            "Totally detached & on autopilot",
                            "Just zero motivation to do anything",
                            "Wanting to sleep and shut everything off",
                            "Feeling confused about why I feel this way"
                    ),
                    "NUMBNESS_DISSOCIATION"
            );
        }

        // E. Loneliness & Isolation ("no one understands", "nobody cares", "alone")
        if (containsAny(lower, LONELINESS_TERMS)) {
            previousTopics.add("LONELINESS");
            return new DialogueResponse(
                    "Feeling like you are carrying your thoughts all by yourself in a world where nobody truly hears you is such a quiet, aching loneliness to endure.",
                    "When that disconnection feels heaviest, what kind of presence would feel safest or most comforting to you?",
                    Arrays.asList(
                            "Someone just sitting with me in silence",
                            "Someone who listens without offering advice",
                            "A reassuring reminder that I matter",
                            "Space to be alone, but knowing someone cares",
                            "I'm not sure, just less distant"
                    ),
                    "LONELINESS"
            );
        }

        // F. Deep Exhaustion & Burnout ("can't do this anymore", "drained", "no energy")
        if (containsAny(lower, EXHAUSTION_TERMS)) {
            previousTopics.add("EXHAUSTION");
            return new DialogueResponse(
                    "When you reach this point of deep exhaustion, even making a simple decision or getting out of bed takes an enormous amount of willpower.",
                    "If you were to give yourself a full permission slip today without any guilt, what would you let yourself put down?",
                    Arrays.asList(
                            "Stop studying/working earlier tonight",
                            "Order food instead of worrying about chores",
                            "Turn off notifications & sleep early",
                            "Forgive myself for having low energy today",
                            "Take a full, uninterrupted rest"
                    ),
                    "EXHAUSTION"
            );
        }

        // G. Positive Moments / Glimmers of Relief
        if (containsAny(lower, POSITIVE_TERMS)) {
            previousTopics.add("POSITIVE");
            return new DialogueResponse(
                    "There is so much quiet beauty and relief in that. In the middle of everything, pausing to savor even a small gentle moment is a powerful form of self-care.",
                    "When you experienced that peaceful moment, what did it feel like in your chest or mind? Did it give you a little breathing room?",
                    Arrays.asList(
                            "Gave me real breathing room",
                            "Felt brief, but reminded me I can be okay",
                            "Made me want to protect moments like that",
                            "Helped reset my mind for a while",
                            "Felt warm and comforting"
                    ),
                    "POSITIVE"
            );
        }

        // --- 2. Dynamic Grammatical Rogerian Parsing (For ANY Custom Typed Answer) ---
        // If the user typed an arbitrary sentence that didn't trigger a hardcoded keyword,
        // we parse their exact clause and mirror it back!

        String inverted = invertPerspective(raw);
        if (inverted.length() > 60) {
            inverted = inverted.substring(0, 57) + "...";
        }

        // Check sentiment polarity of the custom text
        NLPEmotionAnalyzer.EmotionResult emotionAnalysis = NLPEmotionAnalyzer.analyze(raw);

        if (emotionAnalysis.valence < -0.1) {
            // Negative/Distressed custom input
            return new DialogueResponse(
                    "Thank you for expressing that. When you mention that " + inverted + ", it makes complete sense that you feel weighed down. It takes courage to say what you're truly carrying.",
                    "When that thought or feeling is sitting with you, what feels like the hardest part to bear right now?",
                    Arrays.asList(
                            "Feeling like I have no control over it",
                            "Feeling alone in dealing with it",
                            "Worrying about what will happen next",
                            "Feeling exhausted by how long it's lasted",
                            "Just needing someone to truly listen"
                    ),
                    "CUSTOM_DISTRESS"
            );
        } else if (emotionAnalysis.valence > 0.1) {
            // Positive custom input
            return new DialogueResponse(
                    "I really appreciate you sharing that. Noticing that " + inverted + " is such a gentle, hopeful reflection.",
                    "What is one small way you can invite a little more of that peaceful energy into the rest of your day?",
                    Arrays.asList(
                            "Take a quiet walk or step outside",
                            "Listen to some calming music",
                            "Share this feeling with someone close",
                            "Protect my evening for rest",
                            "Keep this gentle reminder in mind"
                    ),
                    "CUSTOM_POSITIVE"
            );
        } else {
            // Reflective / Ambiguous custom input
            return new DialogueResponse(
                    "I hear you, and I appreciate you putting that into words. Even when thoughts feel tangled or hard to explain, having a space to speak them matters.",
                    "If you could ask for one thing purely for your own peace of mind right now, what would feel most supportive?",
                    Arrays.asList(
                            "A little quiet time to myself",
                            "Someone who understands without judging",
                            "A clear plan to tackle my worries",
                            "Permission to take a complete break",
                            "Just taking it one breath at a time"
                    ),
                    "CUSTOM_REFLECTIVE"
            );
        }
    }
}
