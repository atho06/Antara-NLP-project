package com.antara.app.nlp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class QuestionBank {

    public static class QuestionItem {
        public final String text;
        public final List<String> options;

        public QuestionItem(String text, List<String> options) {
            this.text = text;
            this.options = options != null ? options : new ArrayList<>();
        }
    }

    private static final Map<String, List<QuestionItem>> CATEGORIES = new HashMap<>();

    static {
        // Daily Routine
        CATEGORIES.put("daily_routine", Arrays.asList(
                new QuestionItem(
                        "How has your everyday routine been feeling lately?",
                        Arrays.asList("Smooth & manageable", "A bit rushed", "Exhausting & heavy", "Repetitive & dull", "Taking it one day at a time")
                ),
                new QuestionItem(
                        "Are you finding enough time to rest and do things you quietly enjoy?",
                        Arrays.asList("Yes, plenty of time", "A little bit", "Hardly any time", "I feel guilty when I rest", "Not at all")
                ),
                new QuestionItem(
                        "What is one small part of your day that felt even slightly peaceful?",
                        Arrays.asList("Morning tea/coffee", "Quiet evening time", "A nice conversation", "Being in nature", "Nothing yet today")
                ),
                new QuestionItem(
                        "How has your sleep and physical energy been over the past few days?",
                        Arrays.asList("Sleeping well & energized", "Trouble falling asleep", "Waking up exhausted", "Restless & broken sleep", "Low energy throughout")
                )
        ));

        // Stress & Overwhelm
        CATEGORIES.put("stress", Arrays.asList(
                new QuestionItem(
                        "When work or daily pressure builds up, what does that feel like for you?",
                        Arrays.asList("Racing heartbeat & panic", "Mental fog & paralysis", "Irritable & short-tempered", "Physical body tension", "I shut down & isolate")
                ),
                new QuestionItem(
                        "What is one burden or expectation you might be holding that isn't entirely yours?",
                        Arrays.asList("Family expectations", "Trying to please everyone", "Work or study perfection", "Carrying others' emotions", "Unsure, but feels heavy")
                ),
                new QuestionItem(
                        "What is a gentle boundary you might need to set for yourself right now?",
                        Arrays.asList("Saying 'no' to extra tasks", "Taking screen breaks", "Sleeping earlier", "Less time on social media", "Allowing myself to rest")
                ),
                new QuestionItem(
                        "Is there an activity or pause that helps you feel even slightly more grounded?",
                        Arrays.asList("Calm music", "Deep breathing exercises", "A warm shower", "A gentle walk", "Talking to a trusted friend")
                )
        ));

        // Low Energy / Sadness
        CATEGORIES.put("sadness", Arrays.asList(
                new QuestionItem(
                        "On days when your energy feels low, what tends to weigh on your mind the most?",
                        Arrays.asList("Feeling behind in life", "Loneliness or disconnection", "Unfinished responsibilities", "Worrying about the future", "No specific reason")
                ),
                new QuestionItem(
                        "If you could say anything without fear of judgment, what would you express right now?",
                        Arrays.asList("I am really overwhelmed", "I feel lonely and unseen", "I wish someone would hold me", "I'm trying my best but it's hard", "I just want peace")
                ),
                new QuestionItem(
                        "If a dear friend were feeling this exact same way, what kind words would you give them?",
                        Arrays.asList("'You are doing your best'", "'It is okay to rest'", "'You don't have to carry this alone'", "'Be gentle with yourself'", "'I am here for you'")
                ),
                new QuestionItem(
                        "What is one forgiving thing you can allow yourself today?",
                        Arrays.asList("Leave chores for tomorrow", "Order comfort food", "Take a long nap", "Turn off notifications", "Cry if I need to")
                )
        ));

        // Relationships
        CATEGORIES.put("relationships", Arrays.asList(
                new QuestionItem(
                        "How are the connections with the people closest to you feeling lately?",
                        Arrays.asList("Warm & supportive", "A little distant", "Strained & stressful", "Isolated & lonely", "Mixed feelings")
                ),
                new QuestionItem(
                        "Is there someone in your life who truly makes you feel seen and heard?",
                        Arrays.asList("Yes, definitely", "Sometimes", "Not really right now", "I prefer keeping to myself", "I'm looking for connection")
                ),
                new QuestionItem(
                        "Is there a conversation or unspoken thought you have been keeping to yourself?",
                        Arrays.asList("Yes, keeping it inside", "I'm preparing to speak up", "No, feeling open", "It feels too complicated", "I'm not sure")
                ),
                new QuestionItem(
                        "What does feeling supported and safe look like for you right now?",
                        Arrays.asList("Quiet companionship", "A listening ear with no advice", "Encouragement & reassurance", "Practical help with tasks", "Space to be myself")
                )
        ));

        // General
        CATEGORIES.put("general", Arrays.asList(
                new QuestionItem(
                        "What is something on your mind right now that you haven't said out loud today?",
                        Arrays.asList("A secret fear or worry", "A hope I'm shy to admit", "How exhausted I truly am", "Gratitude for something small", "Too tangled to explain")
                ),
                new QuestionItem(
                        "Looking back over this past week, what is one moment you are quietly glad happened?",
                        Arrays.asList("A small achievement", "A warm conversation", "A peaceful moment of rest", "Overcoming a challenge", "Nothing comes to mind")
                ),
                new QuestionItem(
                        "What is something small you're hoping for or looking forward to in the coming days?",
                        Arrays.asList("A restful weekend", "Meeting someone dear", "Finishing a project", "Good food or a warm movie", "Just some quiet time")
                ),
                new QuestionItem(
                        "What does feeling truly at peace look or feel like for you?",
                        Arrays.asList("A quiet sunlit room", "No deadlines or alarms", "Deep, slow breathing", "Feeling accepted as I am", "Being near nature or water")
                )
        ));
    }

    private static final List<QuestionItem> DYNAMIC_FALLBACKS = Arrays.asList(
            new QuestionItem(
                    "What is a favorite song, book, or warm drink that always brings you a sense of comfort?",
                    Arrays.asList("A warm tea/coffee", "A comforting song or album", "A favorite movie or show", "Reading a quiet book", "Wrapping up in a blanket")
            ),
            new QuestionItem(
                    "Even on heavy days, was there one tiny moment that felt okay or gentle?",
                    Arrays.asList("Morning sunlight", "A kind smile or text", "A delicious meal", "A quiet breath", "Not really today")
            ),
            new QuestionItem(
                    "When you feel tension or worry, where in your body do you notice it the most?",
                    Arrays.asList("In my chest or heart", "In my shoulders & neck", "In my stomach or gut", "Headache or jaw clenching", "All over")
            ),
            new QuestionItem(
                    "What is one kind, forgiving choice you can make for your peace of mind today?",
                    Arrays.asList("Go to sleep early", "Stop checking emails", "Treat myself gently", "Forgive myself for today's mistakes", "Ask for a hug or help")
            ),
            new QuestionItem(
                    "If you could pause the world for an hour and do anything purely for rest, what would it be?",
                    Arrays.asList("Sleep deeply with no alarm", "Sit quietly in nature", "Listen to music in the dark", "Take a long bath/shower", "Do absolutely nothing")
            ),
            new QuestionItem(
                    "What is one small wish or hope you hold quietly for tomorrow?",
                    Arrays.asList("More peace of mind", "A little more energy", "A good laugh or smile", "Less stress at work/college", "Feeling lighter")
            )
    );

    public static QuestionItem getNextQuestion(String category, Set<String> askedQuestions) {
        List<QuestionItem> list = CATEGORIES.get(category);
        if (list != null) {
            for (QuestionItem item : list) {
                if (!askedQuestions.contains(item.text)) {
                    askedQuestions.add(item.text);
                    return item;
                }
            }
        }

        // Try other categories
        for (List<QuestionItem> otherList : CATEGORIES.values()) {
            for (QuestionItem item : otherList) {
                if (!askedQuestions.contains(item.text)) {
                    askedQuestions.add(item.text);
                    return item;
                }
            }
        }

        // Use dynamic fallbacks
        for (QuestionItem item : DYNAMIC_FALLBACKS) {
            if (!askedQuestions.contains(item.text)) {
                askedQuestions.add(item.text);
                return item;
            }
        }

        // Fallback
        return new QuestionItem(
                "What is one gentle thing you need right now at this point in your day?",
                Arrays.asList("A moment of silence", "A comforting word", "Some deep breaths", "Rest and sleep", "To be listened to")
        );
    }
}
