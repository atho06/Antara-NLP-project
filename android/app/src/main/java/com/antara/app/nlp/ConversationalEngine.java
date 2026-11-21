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
            "degree", "marks", "grades", "interview", "job", "career", "studying", "study", "deadline", "deadlines"
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

    private static DialogueResponse makeResponse(String ack, String question, List<String> options, String topic, String category, Set<String> askedQuestions) {
        if (askedQuestions != null) {
            // Check if this follow-up was already asked in the session
            if (askedQuestions.contains(question)) {
                // Fetch a fresh, unique question from the QuestionBank instead of repeating
                QuestionBank.QuestionItem freshQ = QuestionBank.getNextQuestion(category, askedQuestions);
                question = freshQ.text;
                options = freshQ.options;
            } else {
                askedQuestions.add(question);
            }
        }
        return new DialogueResponse(ack, question, options, topic);
    }

    public static DialogueResponse generateContextualResponse(
            String userText, 
            int turnCount, 
            String category, 
            Set<String> askedQuestions, 
            Set<String> previousTopics
    ) {
        if (userText == null) userText = "";
        String raw = userText.trim();
        String lower = raw.toLowerCase(Locale.ROOT);

        // =========================================================================
        // 0. GENTLE SESSION WRAP-UP (When session has progressed for multiple turns)
        // =========================================================================
        if (turnCount >= 5 && !previousTopics.contains("WRAP_UP_ASKED")) {
            previousTopics.add("WRAP_UP_ASKED");
            return makeResponse(
                    "You've shared some really honest, meaningful reflections with me today. Giving yourself this quiet space to listen inward takes genuine courage.",
                    "As we come toward the close of our reflection, what is one kind reminder you want to carry with you for the rest of today?",
                    Arrays.asList(
                            "Be gentle with my energy today",
                            "Take breaks without feeling guilty",
                            "I don't have to carry everything alone",
                            "Celebrate my small efforts",
                            "Take things one step at a time"
                    ),
                    "WRAP_UP",
                    category,
                    askedQuestions
            );
        }

        if (previousTopics.contains("WRAP_UP_ASKED")) {
            return makeResponse(
                    "Hold that reminder close. You are doing so much better than you give yourself credit for.",
                    "Take a slow, deep breath and carry this peace with you. When you feel ready, tap 'Finish' in the top right to view your reflection summary.",
                    Arrays.asList(
                            "Ready to finish session 🌷",
                            "Feeling a lot calmer now",
                            "Thank you for listening, Antara"
                    ),
                    "SESSION_COMPLETE",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 1. SPECIFIC OPTION MATCHES: AFTERNOONS / RUSH BREAKDOWN
        // =========================================================================
        if (lower.contains("afternoon") || lower.contains("deadline") || lower.contains("deadlines & tasks")) {
            previousTopics.add("AFTERNOON_DEADLINES");
            return makeResponse(
                    "Afternoons when deadlines and task lists pile up can create that intense feeling of your chest tightening and time slipping away. In that rush, it's so easy to forget to take even a single deep breath.",
                    "When afternoon pressure is peaking, what usually helps keep you from feeling completely overwhelmed?",
                    Arrays.asList(
                            "Breaking tasks into tiny single steps",
                            "Stepping away for 5 minutes of fresh air",
                            "Focus music or noise cancellation",
                            "Reminding myself I can only do one thing at a time",
                            "Honestly, nothing helps - I just push through"
                    ),
                    "AFTERNOON_DEADLINES",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("morning start") || lower.contains("commuting") || lower.contains("mornings getting started")) {
            previousTopics.add("MORNING_RUSH");
            return makeResponse(
                    "Waking up already feeling behind or having to rush through a chaotic commute sets your nervous system on high alert before the day has even properly started.",
                    "What would make your morning feel even 10% more peaceful tomorrow?",
                    Arrays.asList(
                            "Prepping things the night before",
                            "Waking up 15 minutes earlier just to sit quietly",
                            "Not checking my phone right after waking",
                            "Listening to calming music during commute",
                            "An unhurried warm drink"
                    ),
                    "MORNING_RUSH",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("evenings trying to finish chores") || lower.contains("finish chores")) {
            previousTopics.add("EVENING_CHORES");
            return makeResponse(
                    "When your daytime energy is spent and the evening is swallowed by chores, it feels like there is zero time left that belongs purely to you.",
                    "What is one chore or expectation you could give yourself permission to leave untouched tonight?",
                    Arrays.asList(
                            "Leave the dishes / cleaning for tomorrow",
                            "Order dinner instead of cooking",
                            "Skip replying to non-urgent messages",
                            "Just lie down and let the evening be quiet",
                            "Everything feels urgent, but I'll try"
                    ),
                    "EVENING_CHORES",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("trying to please everyone") || lower.contains("please everyone around me")) {
            previousTopics.add("PEOPLE_PLEASING");
            return makeResponse(
                    "Trying to carry everyone else's expectations while ignoring your own needs is an exhausting, silent sacrifice. You deserve the same kindness you give to everyone else.",
                    "If you didn't have to worry about letting anyone down, what boundary would you set today?",
                    Arrays.asList(
                            "Saying 'no' without over-explaining",
                            "Taking time alone without apologizing",
                            "Asking someone else to take responsibility",
                            "Allowing myself to rest first",
                            "Speaking up about how tired I am"
                    ),
                    "PEOPLE_PLEASING",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("never feeling caught up") || lower.contains("falling behind")) {
            previousTopics.add("NEVER_CAUGHT_UP");
            return makeResponse(
                    "That feeling of being permanently behind is so loud, especially in a world that constantly glorifies hustle. But life is not a synchronized race, and you are allowed to move at your own humane pace.",
                    "What is one small win or effort you made recently that you haven't given yourself credit for?",
                    Arrays.asList(
                            "Just showing up today despite feeling tired",
                            "Handled a difficult task or conversation",
                            "Took time out for this reflection",
                            "Kept going when things felt heavy",
                            "It's hard to give myself credit, but I'm trying"
                    ),
                    "NEVER_CAUGHT_UP",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 2. SPECIFIC OPTION MATCHES: SUPPORT & REST PERMISSION
        // =========================================================================
        if (lower.contains("someone who understands without judging") || lower.contains("understands without judging")) {
            previousTopics.add("DESIRE_BEING_UNDERSTOOD");
            return makeResponse(
                    "Craving someone who simply listens without offering unsolicited advice or judging you is such a deeply human need. When everyone around seems focused on output, having just one person say 'I see how hard you're trying' can change everything.",
                    "Is there someone in your life you feel safe opening up to like that, or has that felt hard to find lately?",
                    Arrays.asList(
                            "I have someone, but haven't reached out",
                            "It's hard to find people who truly listen",
                            "I usually keep my thoughts to myself",
                            "I'm hoping to find that kind of connection",
                            "Talking here in Antara is helping right now"
                    ),
                    "DESIRE_BEING_UNDERSTOOD",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("permission to take a complete break") || lower.contains("complete break")) {
            previousTopics.add("PERMISSION_TO_REST");
            return makeResponse(
                    "Consider this your full, unconditional permission slip right now. You are a human being, not a productivity machine. Taking a complete break without feeling guilty is not quitting; it is how your mind and body heal.",
                    "If you truly let yourself take a complete break tonight, what is the first restful thing you would let yourself do?",
                    Arrays.asList(
                            "Turn off all alarms and sleep early",
                            "Watch a comforting movie or read quietly",
                            "Lie down in silence with no screens",
                            "Eat a warm comfort meal slowly",
                            "Do absolutely nothing and just breathe"
                    ),
                    "PERMISSION_TO_REST",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("a little quiet time to myself") || lower.contains("quiet time to myself")) {
            previousTopics.add("QUIET_TIME");
            return makeResponse(
                    "Carving out even fifteen quiet minutes purely for your own mind is like giving your nervous system a sanctuary. In a world full of notifications and demands, quiet alone time is deeply restorative.",
                    "What would your ideal quiet sanctuary moment look like today?",
                    Arrays.asList(
                            "A quiet walk with no phone",
                            "Sitting with a warm cup of tea in peace",
                            "Listening to soft, calming sounds",
                            "Resting in a dimly lit, cozy room",
                            "Just closing my eyes for a little while"
                    ),
                    "QUIET_TIME",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("a clear plan to tackle my worries") || lower.contains("plan to tackle my worries")) {
            previousTopics.add("WORRY_PLAN");
            return makeResponse(
                    "When worries swirl around in your head, they feel ten times bigger than they actually are. Seeing them clearly and breaking them down can bring immediate relief.",
                    "If we were to look at what's worrying you, what is one single next step that is completely within your control today?",
                    Arrays.asList(
                            "Focusing only on the very next hour",
                            "Writing down the top 3 priorities",
                            "Asking for clarification or help",
                            "Deciding what can wait until tomorrow",
                            "Letting go of things I cannot control"
                    ),
                    "WORRY_PLAN",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("just taking it one breath at a time") || lower.contains("one breath at a time")) {
            previousTopics.add("ONE_BREATH");
            return makeResponse(
                    "That is the most grounding anchor you have. Every breath is a fresh opportunity to reset your nervous system and release whatever tension you were holding.",
                    "Let's take a slow, calming breath together right now. Inhale gently for 4... exhale smoothly for 6. How is that feeling in your body?",
                    Arrays.asList(
                            "A little bit lighter",
                            "Chest feels more relaxed",
                            "Still carrying tension, but helping",
                            "Mind is quieter now",
                            "Thank you, that gave me space"
                    ),
                    "ONE_BREATH",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 3. JOY, HUMOR & LAUGHTER ("dying of laughter", jokes, funny, comedy)
        // =========================================================================
        if (containsAny(lower, LAUGHTER_TERMS)) {
            previousTopics.add("JOY_HUMOR");
            return makeResponse(
                    "I love hearing that! Sharing genuine laughter and cracking up is such a wonderful, uplifting breath of fresh air for your mind.",
                    "What was making you laugh so hard, or who was sharing that moment with you?",
                    Arrays.asList(
                            "A really funny friend",
                            "A hilarious video or show",
                            "Something silly that happened",
                            "Just felt unexpectedly light and happy",
                            "It completely lifted my mood today"
                    ),
                    "JOY_HUMOR",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 4. SPECIFIC ROUTINE INITIAL CHOICES
        // =========================================================================
        if (lower.contains("smooth & manageable") || lower.contains("smooth and manageable") || lower.equals("smooth")) {
            previousTopics.add("ROUTINE_SMOOTH");
            return makeResponse(
                    "That is wonderful to hear. Having a steady, manageable rhythm gives your mind and body a calm foundation to truly thrive.",
                    "What has been helping keep your everyday flow feeling so balanced lately?",
                    Arrays.asList(
                            "Getting better sleep & rest",
                            "Staying organized and taking it slow",
                            "Supportive people around me",
                            "Doing things I quietly enjoy",
                            "Just good fortune and steady energy"
                    ),
                    "ROUTINE_SMOOTH",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("a bit rushed") || lower.equals("rushed") || lower.contains("busy schedule")) {
            previousTopics.add("ROUTINE_RUSHED");
            return makeResponse(
                    "Rushing from one responsibility to the next can leave you feeling breathless before the day even ends. Your nervous system is working on high alert.",
                    "Where in your routine does that rush feel most intense or demanding?",
                    Arrays.asList(
                            "Mornings getting started & commuting",
                            "Afternoons with deadlines & tasks",
                            "Evenings trying to finish chores",
                            "Trying to please everyone around me",
                            "Never feeling caught up"
                    ),
                    "ROUTINE_RUSHED",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("exhausting & heavy") || lower.contains("exhausting and heavy") || lower.equals("exhausting")) {
            previousTopics.add("ROUTINE_HEAVY");
            return makeResponse(
                    "When everyday routines start feeling heavy and draining, even the smallest tasks like getting ready or replying to texts feel like climbing a mountain.",
                    "What feels like it is taking the biggest toll on your energy right now?",
                    Arrays.asList(
                            "Too much mental pressure & worries",
                            "Lack of genuine rest & poor sleep",
                            "Carrying emotional burdens alone",
                            "Feeling unmotivated & emotionally flat",
                            "Just physically worn down"
                    ),
                    "ROUTINE_HEAVY",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("repetitive & dull") || lower.contains("repetitive & boring") || lower.contains("repetitive and dull") || lower.contains("repetitive")) {
            previousTopics.add("ROUTINE_REPETITIVE");
            return makeResponse(
                    "When days blur together in repetition, it is very natural to feel restless, emotionally flat, or uninspired. Your soul is craving a little spark.",
                    "What is one tiny change or comforting novelty that might bring a little fresh air into your routine?",
                    Arrays.asList(
                            "Taking a different walk or stepping outside",
                            "Listening to a new playlist or audiobook",
                            "Treating myself to a favorite comfort snack",
                            "Catching up with someone I miss",
                            "Switching off my routine early tonight"
                    ),
                    "ROUTINE_REPETITIVE",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 5. SECOND-LEVEL OPTION RESPONSES (Continuing previous selections)
        // =========================================================================
        if (lower.contains("a really funny friend") || lower.contains("funny friend")) {
            return makeResponse(
                    "Having a friend who can make you laugh until your stomach hurts is truly one of the sweetest treasures in life. Those shared moments protect your mental wellbeing.",
                    "Did sharing that laughter give you a noticeable boost or a sense of relief?",
                    Arrays.asList(
                            "Yes, it completely made my day",
                            "Felt so much lighter afterwards",
                            "Reminded me to stay connected",
                            "I'm grateful for that friend",
                            "I needed that laugh so badly"
                    ),
                    "JOY_FRIEND",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("breaking tasks into tiny single steps") || lower.contains("single steps")) {
            return makeResponse(
                    "Shrinking a huge mountain down to one pebble at a time is the secret to surviving heavy days. When you only focus on the next 15 minutes, the overwhelm disappears.",
                    "What is the single next task you want to gently conquer today, leaving the rest for later?",
                    Arrays.asList(
                            "Finishing one important work/study task",
                            "Sending one important message",
                            "Organizing my immediate desk or space",
                            "Just taking a break before deciding",
                            "Focusing on resting tonight"
                    ),
                    "TASK_BREAKDOWN",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("too much mental pressure") || lower.contains("mental pressure")) {
            return makeResponse(
                    "When your mind is constantly holding a running list of worries, your nervous system never gets a true signal that it's safe to rest.",
                    "If you could put down just one expectation for the remainder of today, what would give your head the most room to breathe?",
                    Arrays.asList(
                            "Stop studying or working earlier tonight",
                            "Turn off notifications & put my phone away",
                            "Forgive myself for having low energy",
                            "Ask someone for help with a chore",
                            "Let tomorrow's problems wait for tomorrow"
                    ),
                    "UNBURDENING",
                    category,
                    askedQuestions
            );
        }

        if (lower.contains("deep breath") || lower.contains("slow, deep breath")) {
            return makeResponse(
                    "Let's do that together right now. Gently breathe in through your nose for 4 seconds... hold softly for 4... and exhale slowly through your mouth for 6. Let your shoulders drop down.",
                    "How does your chest and body feel after that gentle breath?",
                    Arrays.asList(
                            "A little bit lighter",
                            "Chest feels more relaxed",
                            "Still carrying tension, but helping",
                            "Mind is quieter now",
                            "Thank you, that gave me space"
                    ),
                    "BREATHING",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 6. ANGER & FRUSTRATION ("annoyed", "unfair", "mad", "irritated")
        // =========================================================================
        if (containsAny(lower, ANGER_TERMS)) {
            previousTopics.add("ANGER");
            return makeResponse(
                    "It is completely valid to feel angry or frustrated. Anger is often our mind's natural protector - it signals that a boundary was crossed or something felt deeply unfair.",
                    "Would it feel better right now to vent more of what happened, or would you like to explore ways to discharge that tense energy?",
                    Arrays.asList(
                            "I just need to vent it all out",
                            "I feel like nobody listened to me",
                            "I want to release the physical tension",
                            "Tired of dealing with unfair expectations",
                            "I just want some peace and distance"
                    ),
                    "ANGER",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 7. RELATIONAL CONFLICT (Family, Parents, Friends, Disappointment)
        // =========================================================================
        if ((containsAny(lower, FAMILY_ENTITIES) || containsAny(lower, SOCIAL_ENTITIES)) 
                && (containsAny(lower, CONFLICT_TERMS) || lower.contains("disappointed") || lower.contains("guilt"))) {
            
            String entity = findFirstMatch(lower, FAMILY_ENTITIES);
            if (entity == null) entity = findFirstMatch(lower, SOCIAL_ENTITIES);
            if (entity == null) entity = "someone you care about";

            previousTopics.add("RELATIONAL_CONFLICT");
            return makeResponse(
                    "Tension with your " + entity + " and that painful feeling of being judged or criticized cuts right to the bone. It can make home or relationships feel so heavy.",
                    "Do you feel they truly understand what you're already going through inside, or are you carrying that weight in silence?",
                    Arrays.asList(
                            "They don't understand at all",
                            "They want what's best, but their words hurt",
                            "I feel guilty and angry at the same time",
                            "I feel completely misunderstood",
                            "I just want to be accepted as I am"
                    ),
                    "RELATIONAL_CONFLICT",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 8. SOMATIC DISTRESS & TEARS ("crying", "shaking", "panic", "chest tight")
        // =========================================================================
        if (containsAny(lower, SOMATIC_CRYING_TERMS)) {
            previousTopics.add("SOMATIC_OVERLOAD");
            return makeResponse(
                    "I hear how intensely your body is reacting right now. Crying and physical shaking are your nervous system's honest way of releasing built-up pressure when you've held things in for too long.",
                    "Right now, let's take things one quiet second at a time. What is one small comfort your body needs in this very moment?",
                    Arrays.asList(
                            "A glass of cool water",
                            "To lie down in a quiet, dark room",
                            "A slow, steady deep breath",
                            "A soft blanket or comfortable hoodie",
                            "Space to let the tears finish falling"
                    ),
                    "SOMATIC_OVERLOAD",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 9. ACADEMIC & CAREER PRESSURE (Exams, Deadlines, College, Job)
        // =========================================================================
        if (containsAny(lower, ACADEMIC_ENTITIES)) {
            String academicThing = findFirstMatch(lower, ACADEMIC_ENTITIES);
            if (academicThing == null) academicThing = "studies";

            previousTopics.add("ACADEMIC_PRESSURE");
            return makeResponse(
                    "The relentless pressure around " + academicThing + " can make it feel like your entire worth is on trial every single day. That is an exhausting weight to carry.",
                    "When you look at this pressure right now, what is the loudest fear or worry running through your mind?",
                    Arrays.asList(
                            "Fear of failing and falling behind",
                            "Disappointing my parents or family",
                            "Feeling like I have no time or guidance",
                            "Feeling completely burned out & paralyzed",
                            "Worrying that my best isn't good enough"
                    ),
                    "ACADEMIC_PRESSURE",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 10. NUMBNESS & DISSOCIATION ("staring at wall", "feel numb", "empty")
        // =========================================================================
        if (containsAny(lower, NUMB_TERMS)) {
            previousTopics.add("NUMBNESS_DISSOCIATION");
            return makeResponse(
                    "Sitting in that numbness or finding yourself staring into space is often your mind's protective emergency brake when emotions have been running too high for too long. You are not broken for feeling this way.",
                    "When you are in that quiet, empty space, does it feel more like a heavy fog you can't push through, or like you are totally detached from the world around you?",
                    Arrays.asList(
                            "Like a heavy mental fog",
                            "Totally detached & on autopilot",
                            "Just zero motivation to do anything",
                            "Wanting to sleep and shut everything off",
                            "Feeling confused about why I feel this way"
                    ),
                    "NUMBNESS_DISSOCIATION",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 11. LONELINESS & ISOLATION ("no one understands", "nobody cares", "alone")
        // =========================================================================
        if (containsAny(lower, LONELINESS_TERMS)) {
            previousTopics.add("LONELINESS");
            return makeResponse(
                    "Feeling like you are carrying your thoughts all by yourself in a world where nobody truly hears you is such a quiet, aching loneliness to endure.",
                    "When that disconnection feels heaviest, what kind of presence would feel safest or most comforting to you?",
                    Arrays.asList(
                            "Someone just sitting with me in silence",
                            "Someone who listens without offering unsolicited advice",
                            "A reassuring reminder that I matter",
                            "Space to be alone, but knowing someone cares",
                            "I'm not sure, just less distant"
                    ),
                    "LONELINESS",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 12. EXHAUSTION & BURNOUT ("can't do this anymore", "drained", "no energy")
        // =========================================================================
        if (containsAny(lower, EXHAUSTION_TERMS)) {
            previousTopics.add("EXHAUSTION");
            return makeResponse(
                    "When you reach this point of deep exhaustion, even making a simple decision or getting out of bed takes an enormous amount of willpower.",
                    "If you were to give yourself a full permission slip today without any guilt, what would you let yourself put down?",
                    Arrays.asList(
                            "Stop studying/working earlier tonight",
                            "Order food instead of worrying about cooking",
                            "Turn off notifications & sleep early",
                            "Forgive myself for having low energy today",
                            "Take a full, uninterrupted rest"
                    ),
                    "EXHAUSTION",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 13. POSITIVE MOMENTS / GLIMMERS OF RELIEF
        // =========================================================================
        if (containsAny(lower, POSITIVE_TERMS)) {
            previousTopics.add("POSITIVE");
            return makeResponse(
                    "There is so much quiet beauty in that. In the middle of everything, pausing to savor even a small gentle moment is a powerful form of self-care.",
                    "When you experienced that peaceful moment, what did it feel like in your chest or mind? Did it give you a little breathing room?",
                    Arrays.asList(
                            "Gave me real breathing room",
                            "Felt brief, but reminded me I can be okay",
                            "Made me want to protect moments like that",
                            "Helped reset my mind for a while",
                            "Felt warm and comforting"
                    ),
                    "POSITIVE",
                    category,
                    askedQuestions
            );
        }

        // =========================================================================
        // 14. DYNAMIC ROGERIAN INTEGRATION WITH QUESTIONBANK (FOR ALL OTHER CUSTOM/OPTION INPUTS)
        // =========================================================================
        // When user enters custom text or an option not caught by specific branches:
        // 1. Invert perspective for honest reflection
        // 2. Form a warm, varied Rogerian validation (never the same canned phrase)
        // 3. Pull the NEXT UNIQUE question from QuestionBank so questions NEVER repeat!

        String inverted = invertPerspective(raw);
        if (inverted.length() > 60) {
            inverted = inverted.substring(0, 57) + "...";
        }

        NLPEmotionAnalyzer.EmotionResult emotionAnalysis = NLPEmotionAnalyzer.analyze(raw);

        // Rotating variety of empathy stems to avoid robotic repetition
        String[] empathyStems = new String[]{
                "Thank you for sharing that openly. Hearing that " + inverted + ", it makes complete sense that you feel this way.",
                "I hear you, and it takes real self-awareness to notice that " + inverted + ".",
                "That is such an honest reflection. When you say " + inverted + ", it shows how deeply you've been carrying things.",
                "I'm listening with care, and what you expressed about " + inverted + " is completely valid.",
                "Thank you for putting that into words. Reflecting that " + inverted + " is an important step in honoring your feelings."
        };
        int stemIdx = Math.abs(userText.hashCode()) % empathyStems.length;
        String acknowledgment = empathyStems[stemIdx];

        // Fetch the next fresh question from QuestionBank that has NEVER been asked before
        QuestionBank.QuestionItem nextQuestion = QuestionBank.getNextQuestion(category, askedQuestions);

        return new DialogueResponse(
                acknowledgment,
                nextQuestion.text,
                nextQuestion.options,
                "DYNAMIC_REFLECTION"
        );
    }
}
