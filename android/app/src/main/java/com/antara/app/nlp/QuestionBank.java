package com.antara.app.nlp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class QuestionBank {

    private static final Map<String, List<String>> CATEGORIES = new HashMap<>();

    static {
        CATEGORIES.put("daily_routine", Arrays.asList(
                "How has your everyday routine been feeling lately?",
                "Are you finding enough time to rest and do things you quietly enjoy?",
                "What is one small part of your day that felt even slightly peaceful?",
                "How has your sleep and physical energy been over the past few days?"
        ));

        CATEGORIES.put("stress", Arrays.asList(
                "When work or daily pressure builds up, what does that feel like for you?",
                "What is one burden or expectation you might be holding that isn't entirely yours?",
                "What is a gentle boundary you might need to set for yourself right now?",
                "Is there an activity or pause that helps you feel even slightly more grounded?"
        ));

        CATEGORIES.put("sadness", Arrays.asList(
                "On days when your energy feels low, what tends to weigh on your mind the most?",
                "If you could say anything without fear of judgment, what would you express right now?",
                "If a dear friend were feeling this exact same way, what kind words would you give them?",
                "What is one forgiving thing you can allow yourself today?"
        ));

        CATEGORIES.put("relationships", Arrays.asList(
                "How are the connections with the people closest to you feeling lately?",
                "Is there someone in your life who truly makes you feel seen and heard?",
                "Is there a conversation or unspoken thought you have been keeping to yourself?",
                "What does feeling supported and safe look like for you right now?"
        ));

        CATEGORIES.put("general", Arrays.asList(
                "What is something on your mind right now that you haven't said out loud today?",
                "Looking back over this past week, what is one moment you are quietly glad happened?",
                "What is something small you're hoping for or looking forward to in the coming days?",
                "What does feeling truly at peace look or feel like for you?"
        ));
    }

    private static final List<String> DYNAMIC_FALLBACKS = Arrays.asList(
            "What is a favorite song, book, or warm drink that always brings you a sense of comfort?",
            "Even on heavy days, was there one tiny moment that felt okay or gentle?",
            "When you feel tension or worry, where in your body do you notice it the most?",
            "What is one kind, forgiving choice you can make for your peace of mind today?",
            "If you could pause the world for an hour and do anything purely for rest, what would it be?",
            "What is one small wish or hope you hold quietly for tomorrow?",
            "How has your self-talk been sounding lately—more critical, or gentle?"
    );

    public static String getNextQuestion(String category, Set<String> askedQuestions) {
        List<String> list = CATEGORIES.get(category);
        if (list != null) {
            for (String q : list) {
                if (!askedQuestions.contains(q)) {
                    askedQuestions.add(q);
                    return q;
                }
            }
        }

        // Try other categories
        for (List<String> otherList : CATEGORIES.values()) {
            for (String q : otherList) {
                if (!askedQuestions.contains(q)) {
                    askedQuestions.add(q);
                    return q;
                }
            }
        }

        // Use dynamic fallbacks
        for (String q : DYNAMIC_FALLBACKS) {
            if (!askedQuestions.contains(q)) {
                askedQuestions.add(q);
                return q;
            }
        }

        // Non-repeating infinite dynamic prompt
        String dyn = "What is one gentle thing you need right now at this point in your day?";
        return dyn;
    }
}
