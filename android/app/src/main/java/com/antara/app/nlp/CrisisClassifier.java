package com.antara.app.nlp;

import java.util.regex.Pattern;

public class CrisisClassifier {

    private static final Pattern[] CRISIS_PATTERNS = new Pattern[]{
            Pattern.compile("\\b(kill|end)\\s+(my|this)\\s+(life|self)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bwant\\s+to\\s+(die|disappear|sleep forever)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bsuicid(e|al)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bbetter\\s+off\\s+dead\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bcan'?t\\s+take\\s+this\\s+anymore\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bno\\s+reason\\s+to\\s+live\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bhurt\\s+myself\\b", Pattern.CASE_INSENSITIVE)
    };

    public static final String SAFETY_MESSAGE = 
            "I hear how much pain you are carrying right now, and I want to make sure you are safe. "
            + "Because I am an automated self-help tool and not a human counselor, I cannot provide crisis care.\n\n"
            + "Please reach out immediately to confidential support:\n"
            + "• Tele-MANAS: 14416 or 1800-891-4416 (24/7, Toll-Free)\n"
            + "• KIRAN Mental Health: 1800-599-0019 (24/7)\n"
            + "• Vandrevala Foundation: +91 9999 666 555 (24/7 Free)\n"
            + "• Emergency: 112\n\n"
            + "Your life and safety are the absolute priority. Please reach out to someone who can help right now.";

    public static boolean checkCrisis(String text) {
        if (text == null || text.trim().isEmpty()) return false;
        for (Pattern p : CRISIS_PATTERNS) {
            if (p.matcher(text).find()) {
                return true;
            }
        }
        return false;
    }
}
