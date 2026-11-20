package com.antara.app.nlp;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class NLPEmotionAnalyzer {

    // Emotion lexicons
    private static final Set<String> JOY_WORDS = new HashSet<>(Arrays.asList(
            "happy", "good", "great", "peace", "calm", "grateful", "smile", "love", 
            "joy", "hope", "energized", "relaxed", "glad", "wonderful", "better", "accomplished",
            "blessed", "cheerful", "content", "delighted", "laugh", "laughter", "laughing", 
            "hilarious", "joke", "funny", "haha", "lol", "fun", "celebrated", "cracked", "giggle"
    ));

    private static final Set<String> STRESS_WORDS = new HashSet<>(Arrays.asList(
            "stress", "stressed", "stressful", "anxious", "anxiety", "worried", "worry", "pressure", 
            "deadline", "panic", "hectic", "nervous", "scared", "restless", "burden", "overthinking",
            "overwhelmed", "rushed", "chaotic", "dread", "racing", "tension", "paralyzed"
    ));

    private static final Set<String> SADNESS_WORDS = new HashSet<>(Arrays.asList(
            "sad", "sadness", "crying", "cried", "tears", "down", "low", "hopeless", "lonely", "alone", 
            "empty", "exhausted", "exhausting", "tired", "depressed", "heavy", "grief", "hurting", 
            "lost", "heartbroken", "drained", "burnout", "unmotivated", "numb"
    ));

    private static final Set<String> ANGER_WORDS = new HashSet<>(Arrays.asList(
            "angry", "mad", "annoyed", "frustrated", "unfair", "hate", "irritated", "furious",
            "pissed", "resentful", "rage", "yelled", "screamed"
    ));

    private static final Set<String> FATIGUE_WORDS = new HashSet<>(Arrays.asList(
            "tired", "bored", "overwhelmed", "too much", "stop", "pause", "exhausted", 
            "don't want to answer", "can't focus", "done for today", "need to stop"
    ));

    public static class EmotionResult {
        public final String primaryEmotion;
        public final boolean userFatigued;
        public final double valence;

        public EmotionResult(String primaryEmotion, boolean userFatigued, double valence) {
            this.primaryEmotion = primaryEmotion;
            this.userFatigued = userFatigued;
            this.valence = valence;
        }
    }

    public static EmotionResult analyze(String text) {
        if (text == null || text.trim().isEmpty()) {
            return new EmotionResult("calm_grounded", false, 0.0);
        }

        String lower = text.toLowerCase(Locale.ROOT);

        // Immediate check for laughing / humor expressions
        if (lower.contains("dying of laughter") || lower.contains("dying laughing") || 
            lower.contains("died laughing") || lower.contains("laughed so hard") || 
            lower.contains("funny") || lower.contains("hilarious") || lower.contains("joke")) {
            return new EmotionResult("joy_humor", false, 0.8);
        }

        String[] tokens = lower.replaceAll("[^a-z ]", "").split("\\s+");

        int joyCount = 0, stressCount = 0, sadCount = 0, angerCount = 0;
        boolean isFatigued = false;

        for (String w : FATIGUE_WORDS) {
            if (lower.contains(w)) {
                isFatigued = true;
                break;
            }
        }

        for (String token : tokens) {
            if (JOY_WORDS.contains(token)) joyCount++;
            if (STRESS_WORDS.contains(token)) stressCount++;
            if (SADNESS_WORDS.contains(token)) sadCount++;
            if (ANGER_WORDS.contains(token)) angerCount++;
        }

        String primary = "calm_grounded";
        int maxCount = joyCount;

        if (stressCount > maxCount) {
            maxCount = stressCount;
            primary = "stress_anxiety";
        }
        if (sadCount > maxCount) {
            maxCount = sadCount;
            primary = "sadness_low_energy";
        }
        if (angerCount > maxCount) {
            maxCount = angerCount;
            primary = "anger_frustration";
        }
        if (maxCount == 0) {
            if (lower.contains("smooth") || lower.contains("manageable") || lower.contains("peace") || lower.contains("fine") || lower.contains("okay")) {
                primary = "calm_grounded";
            } else {
                primary = "reflective";
            }
        }

        double valence = (joyCount - (stressCount + sadCount + angerCount)) / Math.max(1.0, (double) tokens.length);

        return new EmotionResult(primary, isFatigued, valence);
    }
}
