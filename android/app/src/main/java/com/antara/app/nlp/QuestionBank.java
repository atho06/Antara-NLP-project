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
        // 1. Daily Routine & Energy
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
                ),
                new QuestionItem(
                        "When your schedule gets chaotic, what is usually the first thing you let go of?",
                        Arrays.asList("Nutritious food & water", "Sleep & quiet downtime", "Exercise or movement", "Connecting with loved ones", "Time alone with my thoughts")
                ),
                new QuestionItem(
                        "What is one small boundary or habit that could protect your energy tomorrow?",
                        Arrays.asList("Going to bed 30 min earlier", "Leaving work/study at a set time", "Less social media scrolling", "Saying 'no' to extra tasks", "Taking regular 5-minute pauses")
                ),
                new QuestionItem(
                        "If you could design an unhurried morning purely for yourself, how would you begin it?",
                        Arrays.asList("Sit quietly with a warm drink", "Sleep in without an alarm", "Go for a peaceful walk", "Listen to calm music", "Have a slow breakfast")
                ),
                new QuestionItem(
                        "What is one responsibility or chore that you can safely postpone until next week?",
                        Arrays.asList("A non-urgent project", "Cleaning or organizing chores", "Replying to non-vital messages", "An optional errand", "I can let go of several things")
                )
        ));

        // 2. Stress & Overwhelm
        CATEGORIES.put("stress", Arrays.asList(
                new QuestionItem(
                        "When work or daily pressure builds up, what does that feel like in your mind and body?",
                        Arrays.asList("Racing heartbeat & panic", "Mental fog & paralysis", "Irritable & short-tempered", "Physical tension in shoulders/chest", "I shut down & isolate")
                ),
                new QuestionItem(
                        "What is one burden or expectation you might be holding that isn't entirely yours?",
                        Arrays.asList("Family expectations", "Trying to please everyone", "Work or study perfection", "Carrying others' emotions", "Unsure, but feels heavy")
                ),
                new QuestionItem(
                        "When you notice that your mind is racing, what worry seems to loop most frequently?",
                        Arrays.asList("What if I make a mistake?", "I don't have enough time", "I'm going to let someone down", "Everything is on my shoulders", "I just can't keep up")
                ),
                new QuestionItem(
                        "What is a gentle boundary you might need to set for yourself right now?",
                        Arrays.asList("Saying 'no' to extra tasks", "Taking screen breaks", "Sleeping earlier", "Less time on social media", "Allowing myself to rest")
                ),
                new QuestionItem(
                        "What is one thing that is truly within your control right now in this exact hour?",
                        Arrays.asList("My next breath", "Taking a sip of water", "Stepping away for 5 minutes", "How gently I speak to myself", "Choosing to rest")
                ),
                new QuestionItem(
                        "Is there an activity or pause that helps you feel even slightly more grounded?",
                        Arrays.asList("Calm music", "Deep breathing exercises", "A warm shower", "A gentle walk", "Talking to a trusted friend")
                ),
                new QuestionItem(
                        "If your stress could speak to you like an exhausted friend, what would it ask for?",
                        Arrays.asList("I need you to slow down", "I need you to sleep", "I need to be reminded I'm safe", "Stop worrying about outcomes", "I need quiet comfort")
                )
        ));

        // 3. Low Energy & Sadness
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
                        "When sadness or low energy visits you, how does it physically feel?",
                        Arrays.asList("A heavy, exhausting weight", "An empty, hollow quiet", "A sudden wave of tears", "Feeling totally numb", "A mix of everything")
                ),
                new QuestionItem(
                        "If a dear friend were feeling this exact same way, what kind words would you give them?",
                        Arrays.asList("'You are doing your best'", "'It is okay to rest'", "'You don't have to carry this alone'", "'Be gentle with yourself'", "'I am here for you'")
                ),
                new QuestionItem(
                        "What is one forgiving thing you can allow yourself today without guilt?",
                        Arrays.asList("Leave chores for tomorrow", "Order comfort food", "Take a long nap", "Turn off notifications", "Cry if I need to")
                ),
                new QuestionItem(
                        "What is one small comfort that has helped soothe you in the past when feeling down?",
                        Arrays.asList("A warm blanket or hoodie", "A favorite comfort meal or tea", "Re-watching a comforting show", "Listening to soft rain or music", "Curling up in bed")
                ),
                new QuestionItem(
                        "What is a gentle truth you need to hear about yourself today?",
                        Arrays.asList("My worth isn't tied to productivity", "It's okay to have down days", "I am allowed to take up space", "This feeling will pass", "I am doing better than I think")
                )
        ));

        // 4. Relationships & Connection
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
                ),
                new QuestionItem(
                        "When tension or conflict happens with someone close, what is your initial instinct?",
                        Arrays.asList("I apologize even if not my fault", "I pull away and go silent", "I get defensive and angry", "I replay words endlessly in head", "I try to fix it immediately")
                ),
                new QuestionItem(
                        "What is one boundary you wish you could express without feeling guilty?",
                        Arrays.asList("Needing more time to myself", "Not wanting unsolicited advice", "Saying no to social plans", "Asking for emotional honesty", "Setting limits on expectations")
                )
        ));

        // 5. General Reflection
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
                ),
                new QuestionItem(
                        "If you could send a gentle message to your younger self right now, what would you say?",
                        Arrays.asList("You're stronger than you think", "Don't worry what others think", "It's okay to make mistakes", "Take time to enjoy life", "You will get through this")
                ),
                new QuestionItem(
                        "What is one quality about yourself that you are quietly proud of, even on hard days?",
                        Arrays.asList("My resilience and tenacity", "My empathy for other people", "My sense of humor", "My curiosity and creativity", "That I keep trying")
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
                    Arrays.asList("Go to sleep early", "Stop checking emails", "Treat myself gently", "Forgive today's mistakes", "Ask for a hug or help")
            ),
            new QuestionItem(
                    "If you could pause the world for an hour and do anything purely for rest, what would it be?",
                    Arrays.asList("Sleep deeply with no alarm", "Sit quietly in nature", "Listen to music in the dark", "Take a long bath/shower", "Do absolutely nothing")
            ),
            new QuestionItem(
                    "What is one small wish or hope you hold quietly for tomorrow?",
                    Arrays.asList("More peace of mind", "A little more energy", "A good laugh or smile", "Less stress at work/college", "Feeling lighter")
            ),
            new QuestionItem(
                    "What is one expectation you've been placing on yourself that you could soften a little?",
                    Arrays.asList("Having to be perfect", "Solving everything today", "Pleasing everybody", "Hiding my vulnerability", "Always staying strong")
            ),
            new QuestionItem(
                    "When was the last time you felt truly comfortable being yourself?",
                    Arrays.asList("Around close friends", "When I'm alone in my room", "In nature or outdoors", "A long time ago", "Right here in this reflection")
            ),
            new QuestionItem(
                    "What does your mind need most right now: rest, clarity, or reassurance?",
                    Arrays.asList("Deep physical rest", "Mental clarity & focus", "Gentle reassurance", "A complete distraction", "Just space to be")
            ),
            new QuestionItem(
                    "What is one thing you can do tonight that feels purely loving toward yourself?",
                    Arrays.asList("Eat my favorite meal", "Put my phone in another room", "Write down my feelings", "Sleep early with a clean sheet", "Take a warm shower and unwind")
            )
    );

    public static QuestionItem getNextQuestion(String category, Set<String> askedQuestions) {
        if (category == null || category.trim().isEmpty()) {
            category = "daily_routine";
        }

        // 1. Try selected category
        List<QuestionItem> list = CATEGORIES.get(category);
        if (list != null) {
            for (QuestionItem item : list) {
                if (askedQuestions == null || !askedQuestions.contains(item.text)) {
                    if (askedQuestions != null) askedQuestions.add(item.text);
                    return item;
                }
            }
        }

        // 2. Try other categories
        for (Map.Entry<String, List<QuestionItem>> entry : CATEGORIES.entrySet()) {
            for (QuestionItem item : entry.getValue()) {
                if (askedQuestions == null || !askedQuestions.contains(item.text)) {
                    if (askedQuestions != null) askedQuestions.add(item.text);
                    return item;
                }
            }
        }

        // 3. Try dynamic fallbacks
        for (QuestionItem item : DYNAMIC_FALLBACKS) {
            if (askedQuestions == null || !askedQuestions.contains(item.text)) {
                if (askedQuestions != null) askedQuestions.add(item.text);
                return item;
            }
        }

        // 4. Ultimate closing question (will only be reached after dozens of questions)
        String closingText = "What is one gentle intention you would like to carry into the rest of your day?";
        if (askedQuestions != null) askedQuestions.add(closingText);
        return new QuestionItem(
                closingText,
                Arrays.asList("Be kind to myself", "Take breaks without guilt", "Stay hydrated and rest", "One breath at a time", "Protect my inner peace")
        );
    }
}
