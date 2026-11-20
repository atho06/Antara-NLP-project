package com.antara.app.nlp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
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

    // --- Entity & Keyword Taxonomies ---
    private static final String[] LAUGHTER_TERMS = {
            "dying of laughter", "dying laughing", "died laughing", "laughed so hard", 
            "laughter", "laughing", "laugh", "hilarious", "joke", "funny", "cracked up", 
            "giggle", "giggling", "comedy", "haha", "lol"
    };

    private static final String[] FAMILY_ENTITIES = {
            "mom", "mother", "dad", "father", "parents", "brother", "sister", "family"
    };

    private static final String[] SOCIAL_ENTITIES = {
            "friend", "friends", "best friend", "roommate", "colleague", "classmate", "partner", "boyfriend", "girlfriend"
    };

    private static final String[] ACADEMIC_ENTITIES = {
            "exam", "exams", "test", "assignment", "college", "school", "project", 
            "degree", "marks", "grades", "interview", "job", "career", "studying", "study"
    };

    private static final String[] CONFLICT_TERMS = {
            "fight", "fought", "argued", "arguing", "yelled", "shouted", "screaming", 
            "angry with me", "blamed", "cut off", "ignore", "criticized", "disappointment"
    };

    private static final String[] SOMATIC_CRYING_TERMS = {
            "crying", "cried", "tears", "shaking", "panic", "heart racing", "chest hurts", 
            "can't breathe", "vomiting", "headache", "throwing up", "not eating", "chest tight"
    };

    private static final String[] NUMB_TERMS = {
            "numb", "empty", "staring at the wall", "staring at the ceiling", "spaced out", 
            "detached", "autopilot", "feel nothing", "can't feel"
    };

    private static final String[] LONELINESS_TERMS = {
            "lonely", "alone", "isolated", "nobody", "no one", "no friends", "unseen", 
            "unheard", "left out", "abandoned"
    };

    private static final String[] EXHAUSTION_TERMS = {
            "exhausted", "exhausting", "tired", "drained", "can't do this anymore", "burnout", 
            "burned out", "no energy", "bed all day", "sleep", "worn out"
    };

    private static final String[] ANGER_TERMS = {
            "angry", "mad", "annoyed", "frustrated", "irritated", "furious", "pissed", 
            "unfair", "hate", "resentful"
    };

    private static final String[] POSITIVE_TERMS = {
            "happy", "peaceful", "peace", "calm", "grateful", "good", "great", "smile", 
            "tea", "coffee", "walk", "nature", "sunlight", "relief", "better", "accomplished", "content"
    };

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

    private static String invertPerspective(String text) {
        if (text == null || text.trim().isEmpty()) return "";
        String clean = text.replaceAll("[.,!?;:]", " ").trim();

        clean = clean.replaceAll("(?i)\\bI am\\b", "you are");
        clean = clean.replaceAll("(?i)\\bI'm\\b", "you are");
        clean = clean.replaceAll("(?i)\\bI feel\\b", "you feel");
        clean = clean.replaceAll("(?i)\\bI have\\b", "you have");
        clean = clean.replaceAll("(?i)\\bI was\\b", "you were");
        clean = clean.replaceAll("(?i)\\bmy\\b", "your");
        clean = clean.replaceAll("(?i)\\bme\\b", "you");
        clean = clean.replaceAll("(?i)\\bmyself\\b", "yourself");
        clean = clean.replaceAll("(?i)\\bI\\b", "you");

        return clean.replaceAll("\\s+", " ");
    }

    public static DialogueResponse generateContextualResponse(String userText, int turnCount, Set<String> previousTopics) {
        if (userText == null) userText = "";
        String raw = userText.trim();
        String lower = raw.toLowerCase(Locale.ROOT);

        // =========================================================================
        // 1. JOY, HUMOR & LAUGHTER ("dying of laughter", jokes, funny, comedy)
        // =========================================================================
        if (containsAny(lower, LAUGHTER_TERMS)) {
            previousTopics.add("JOY_HUMOR");
            return new DialogueResponse(
                    "I love hearing that! Sharing genuine laughter and cracking up is such a wonderful, uplifting breath of fresh air for your mind.",
                    "What was making you laugh so hard, or who was sharing that moment with you?",
                    Arrays.asList(
                            "A really funny friend",
                            "A hilarious video or show",
                            "Something silly that happened",
                            "Just felt unexpectedly light and happy",
                            "It completely lifted my mood today"
                    ),
                    "JOY_HUMOR"
            );
        }

        // =========================================================================
        // 2. SPECIFIC ROUTINE CHOICES (Direct matching for 1st turn options)
        // =========================================================================
        if (lower.contains("smooth & manageable") || lower.contains("smooth and manageable") || lower.equals("smooth")) {
            previousTopics.add("ROUTINE_SMOOTH");
            return new DialogueResponse(
                    "That is wonderful to hear. Having a steady, manageable rhythm gives your mind and body a calm foundation to truly thrive.",
                    "What has been helping keep your everyday flow feeling so balanced lately?",
                    Arrays.asList(
                            "Getting better sleep & rest",
                            "Staying organized and taking it slow",
                            "Supportive people around me",
                            "Doing things I quietly enjoy",
                            "Just good fortune and steady energy"
                    ),
                    "ROUTINE_SMOOTH"
            );
        }

        if (lower.contains("a bit rushed") || lower.equals("rushed") || lower.contains("busy schedule")) {
            previousTopics.add("ROUTINE_RUSHED");
            return new DialogueResponse(
                    "Rushing from one responsibility to the next can leave you feeling breathless before the day even ends. Your nervous system is working on high alert.",
                    "Where in your routine does that rush feel most intense or demanding?",
                    Arrays.asList(
                            "Mornings getting started & commuting",
                            "Afternoons with deadlines & tasks",
                            "Evenings trying to finish chores",
                            "Trying to please everyone around me",
                            "Never feeling caught up"
                    ),
                    "ROUTINE_RUSHED"
            );
        }

        if (lower.contains("exhausting & heavy") || lower.contains("exhausting and heavy") || lower.equals("exhausting")) {
            previousTopics.add("ROUTINE_HEAVY");
            return new DialogueResponse(
                    "When everyday routines start feeling heavy and draining, even the smallest tasks like getting ready or replying to texts feel like climbing a mountain.",
                    "What feels like it is taking the biggest toll on your energy right now?",
                    Arrays.asList(
                            "Too much mental pressure & worries",
                            "Lack of genuine rest & poor sleep",
                            "Carrying emotional burdens alone",
                            "Feeling unmotivated & emotionally flat",
                            "Just physically worn down"
                    ),
                    "ROUTINE_HEAVY"
            );
        }

        if (lower.contains("repetitive & dull") || lower.contains("repetitive & boring") || lower.contains("repetitive and dull") || lower.contains("repetitive")) {
            previousTopics.add("ROUTINE_REPETITIVE");
            return new DialogueResponse(
                    "When days blur together in repetition, it is very natural to feel restless, emotionally flat, or uninspired. Your soul is craving a little spark.",
                    "What is one tiny change or comforting novelty that might bring a little fresh air into your routine?",
                    Arrays.asList(
                            "Taking a different walk or stepping outside",
                            "Listening to a new playlist or audiobook",
                            "Treating myself to a favorite comfort snack",
                            "Catching up with someone I miss",
                            "Switching off my routine early tonight"
                    ),
                    "ROUTINE_REPETITIVE"
            );
        }

        if (lower.contains("taking it one day at a time") || lower.contains("one day at a time")) {
            previousTopics.add("ONE_DAY_AT_A_TIME");
            return new DialogueResponse(
                    "Taking things one day at a time is one of the wisest, gentlest approaches you can take. You don't have to figure out next month today.",
                    "Right here in this present moment, what is one small thing within your control that you can do for yourself?",
                    Arrays.asList(
                            "Drink a glass of water and breathe",
                            "Rest without feeling guilty",
                            "Take three slow, deep breaths",
                            "Speak kindly to myself today",
                            "Take a short walk or stretch"
                    ),
                    "ONE_DAY_AT_A_TIME"
            );
        }

        // =========================================================================
        // 3. SECOND-LEVEL OPTION RESPONSES (Continuing previous selections)
        // =========================================================================
        if (lower.contains("a really funny friend") || lower.contains("funny friend")) {
            return new DialogueResponse(
                    "Having a friend who can make you laugh until your stomach hurts is truly one of the sweetest treasures in life. Those shared moments protect your mental wellbeing.",
                    "Did sharing that laughter give you a noticeable boost or a sense of relief?",
                    Arrays.asList(
                            "Yes, it completely made my day",
                            "Felt so much lighter afterwards",
                            "Reminded me to stay connected",
                            "I'm grateful for that friend",
                            "I needed that laugh so badly"
                    ),
                    "JOY_FRIEND"
            );
        }

        if (lower.contains("fear of failing") || lower.contains("falling behind")) {
            return new DialogueResponse(
                    "That fear of falling behind is so loud, especially when everyone around seems to be moving ahead. But life is not a synchronized sprint, and you are allowed to move at your own humane pace.",
                    "What is one small win or effort you made recently that you haven't given yourself credit for?",
                    Arrays.asList(
                            "Just showing up today despite feeling tired",
                            "Handled a difficult task or conversation",
                            "Took time out for this reflection",
                            "Kept going when things felt heavy",
                            "It's hard to give myself credit, but I'm trying"
                    ),
                    "SELF_COMPASSION"
            );
        }

        if (lower.contains("too much mental pressure") || lower.contains("worries")) {
            return new DialogueResponse(
                    "When your mind is constantly holding a running list of worries, your nervous system never gets a true signal that it's safe to rest.",
                    "If you could put down just one expectation for the remainder of today, what would give your head the most room to breathe?",
                    Arrays.asList(
                            "Stop studying or working earlier tonight",
                            "Turn off notifications & put my phone away",
                            "Forgive myself for having low energy",
                            "Ask someone for help with a chore",
                            "Let tomorrow's problems wait for tomorrow"
                    ),
                    "UNBURDENING"
            );
        }

        if (lower.contains("deep breath") || lower.contains("slow, deep breath")) {
            return new DialogueResponse(
                    "Let's do that together right now. Gently breathe in through your nose for 4 seconds... hold softly for 4... and exhale slowly through your mouth for 6. Let your shoulders drop down.",
                    "How does your chest and body feel after that gentle breath?",
                    Arrays.asList(
                            "A little bit lighter",
                            "Chest feels more relaxed",
                            "Still carrying tension, but helping",
                            "Mind is quieter now",
                            "Thank you, that gave me space"
                    ),
                    "BREATHING"
            );
        }

        // =========================================================================
        // 4. ANGER & FRUSTRATION ("annoyed", "unfair", "mad", "irritated")
        // =========================================================================
        if (containsAny(lower, ANGER_TERMS)) {
            previousTopics.add("ANGER");
            return new DialogueResponse(
                    "It is completely valid to feel angry or frustrated. Anger is often our mind's natural protector—it signals that a boundary was crossed or something felt deeply unfair.",
                    "Would it feel better right now to vent more of what happened, or would you like to explore ways to discharge that tense energy?",
                    Arrays.asList(
                            "I just need to vent it all out",
                            "I feel like nobody listened to me",
                            "I want to release the physical tension",
                            "Tired of dealing with unfair expectations",
                            "I just want some peace and distance"
                    ),
                    "ANGER"
            );
        }

        // =========================================================================
        // 5. RELATIONAL CONFLICT (Family, Parents, Friends, Disappointment)
        // =========================================================================
        if ((containsAny(lower, FAMILY_ENTITIES) || containsAny(lower, SOCIAL_ENTITIES)) 
                && (containsAny(lower, CONFLICT_TERMS) || lower.contains("disappointed") || lower.contains("guilt"))) {
            
            String entity = findFirstMatch(lower, FAMILY_ENTITIES);
            if (entity == null) entity = findFirstMatch(lower, SOCIAL_ENTITIES);
            if (entity == null) entity = "someone you care about";

            previousTopics.add("RELATIONAL_CONFLICT");
            return new DialogueResponse(
                    "Tension with your " + entity + " and that painful feeling of being judged or criticized cuts right to the bone. It can make home or relationships feel so heavy.",
                    "Do you feel they truly understand what you're already going through inside, or are you carrying that weight in silence?",
                    Arrays.asList(
                            "They don't understand at all",
                            "They want what's best, but their words hurt",
                            "I feel guilty and angry at the same time",
                            "I feel completely misunderstood",
                            "I just want to be accepted as I am"
                    ),
                    "RELATIONAL_CONFLICT"
            );
        }

        // =========================================================================
        // 6. SOMATIC DISTRESS & TEARS ("crying", "shaking", "panic", "chest tight")
        // =========================================================================
        if (containsAny(lower, SOMATIC_CRYING_TERMS)) {
            previousTopics.add("SOMATIC_OVERLOAD");
            return new DialogueResponse(
                    "I hear how intensely your body is reacting right now. Crying and physical shaking are your nervous system's honest way of releasing built-up pressure when you've held things in for too long.",
                    "Right now, let's take things one quiet second at a time. What is one small comfort your body needs in this very moment?",
                    Arrays.asList(
                            "A glass of cool water",
                            "To lie down in a quiet, dark room",
                            "A slow, steady deep breath",
                            "A soft blanket or comfortable hoodie",
                            "Space to let the tears finish falling"
                    ),
                    "SOMATIC_OVERLOAD"
            );
        }

        // =========================================================================
        // 7. ACADEMIC & CAREER PRESSURE (Exams, Deadlines, College, Job)
        // =========================================================================
        if (containsAny(lower, ACADEMIC_ENTITIES)) {
            String academicThing = findFirstMatch(lower, ACADEMIC_ENTITIES);
            if (academicThing == null) academicThing = "studies";

            previousTopics.add("ACADEMIC_PRESSURE");
            return new DialogueResponse(
                    "The relentless pressure around " + academicThing + " can make it feel like your entire worth is on trial every single day. That is an exhausting weight to carry.",
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

        // =========================================================================
        // 8. NUMBNESS & DISSOCIATION ("staring at wall", "feel numb", "empty")
        // =========================================================================
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

        // =========================================================================
        // 9. LONELINESS & ISOLATION ("no one understands", "nobody cares", "alone")
        // =========================================================================
        if (containsAny(lower, LONELINESS_TERMS)) {
            previousTopics.add("LONELINESS");
            return new DialogueResponse(
                    "Feeling like you are carrying your thoughts all by yourself in a world where nobody truly hears you is such a quiet, aching loneliness to endure.",
                    "When that disconnection feels heaviest, what kind of presence would feel safest or most comforting to you?",
                    Arrays.asList(
                            "Someone just sitting with me in silence",
                            "Someone who listens without offering unsolicited advice",
                            "A reassuring reminder that I matter",
                            "Space to be alone, but knowing someone cares",
                            "I'm not sure, just less distant"
                    ),
                    "LONELINESS"
            );
        }

        // =========================================================================
        // 10. EXHAUSTION & BURNOUT ("can't do this anymore", "drained", "no energy")
        // =========================================================================
        if (containsAny(lower, EXHAUSTION_TERMS)) {
            previousTopics.add("EXHAUSTION");
            return new DialogueResponse(
                    "When you reach this point of deep exhaustion, even making a simple decision or getting out of bed takes an enormous amount of willpower.",
                    "If you were to give yourself a full permission slip today without any guilt, what would you let yourself put down?",
                    Arrays.asList(
                            "Stop studying/working earlier tonight",
                            "Order food instead of worrying about cooking",
                            "Turn off notifications & sleep early",
                            "Forgive myself for having low energy today",
                            "Take a full, uninterrupted rest"
                    ),
                    "EXHAUSTION"
            );
        }

        // =========================================================================
        // 11. POSITIVE MOMENTS / GLIMMERS OF RELIEF
        // =========================================================================
        if (containsAny(lower, POSITIVE_TERMS)) {
            previousTopics.add("POSITIVE");
            return new DialogueResponse(
                    "There is so much quiet beauty in that. In the middle of everything, pausing to savor even a small gentle moment is a powerful form of self-care.",
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

        // =========================================================================
        // 12. DYNAMIC ROGERIAN PARSING FOR CUSTOM TYPED STATEMENTS
        // =========================================================================
        String inverted = invertPerspective(raw);
        if (inverted.length() > 65) {
            inverted = inverted.substring(0, 62) + "...";
        }

        NLPEmotionAnalyzer.EmotionResult emotionAnalysis = NLPEmotionAnalyzer.analyze(raw);

        if (emotionAnalysis.valence < -0.1) {
            // Negative / Distressed custom reflection
            return new DialogueResponse(
                    "Thank you for sharing that openly. Hearing that " + inverted + ", it makes complete sense that you feel weighed down. It takes courage to put words to difficult feelings.",
                    "When that thought or feeling is sitting with you, what feels like the most supportive thing for your mind right now?",
                    Arrays.asList(
                            "Giving myself permission to feel this way",
                            "Talking it through step by step",
                            "Taking a gentle break from everything",
                            "Focusing only on what I can control today",
                            "Just knowing I was heard without judgment"
                    ),
                    "CUSTOM_DISTRESS"
            );
        } else if (emotionAnalysis.valence > 0.1) {
            // Positive custom reflection
            return new DialogueResponse(
                    "I really appreciate you expressing that. Noticing that " + inverted + " is such a gentle, uplifting reflection.",
                    "What is one small way you can invite a little more of that comforting energy into the rest of your day?",
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
            // Balanced / Observational custom reflection
            return new DialogueResponse(
                    "I hear you, and I appreciate you putting that into words. Even when thoughts feel tangled or hard to explain, having a quiet space to reflect matters.",
                    "If you could ask for one thing purely for your own peace of mind right now, what would feel most comforting?",
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
