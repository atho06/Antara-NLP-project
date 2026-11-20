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
            Pattern.compile("\\b(don'?t|do not)\\s+want\\s+to\\s+(live|exist|be here)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bwant\\s+to\\s+(end\\s+it\\s+all|give\\s+up\\s+on\\s+life)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bcan'?t\\s+(go\\s+on|continue\\s+living|survive\\s+this)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bhurt\\s+myself\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(harming|harm|cut|cutting)\\s+myself\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(feel\\s+like|thinking\\s+about)\\s+(dying|suicide|ending\\s+my\\s+life)\\b", Pattern.CASE_INSENSITIVE)
    };

    public static String buildCrisisMessageWithContact(String contactName, String contactPhone) {
        return buildCrisisMessageWithContact(contactName, contactPhone, "");
    }

    public static String buildCrisisMessageWithContact(String contactName, String contactPhone, String contactEmail) {
        String name = (contactName != null && !contactName.trim().isEmpty()) ? contactName.trim() : "Emergency Contact";
        String phone = (contactPhone != null && !contactPhone.trim().isEmpty()) ? contactPhone.trim() : "";
        String email = (contactEmail != null && !contactEmail.trim().isEmpty()) ? contactEmail.trim() : "";

        StringBuilder sb = new StringBuilder();
        sb.append("🚨 PRIMARY EMERGENCY CONTACT (CALL FIRST):\n");
        sb.append("👤 ").append(name).append("\n");
        sb.append("📞 ").append(phone).append("\n");
        if (!email.isEmpty()) {
            sb.append("✉️ ").append(email).append("\n");
        }
        sb.append("\nI hear how much pain you are carrying right now. Your life and safety are the absolute priority.\n");
        sb.append("Please reach out to ").append(name).append(" immediately—they care about you deeply.\n\n");
        sb.append("🆘 24/7 Professional Helplines:\n");
        sb.append("• Tele-MANAS (Govt. of India): 14416 (Toll-Free)\n");
        sb.append("• KIRAN Mental Health: 1800-599-0019 (Toll-Free)\n");
        sb.append("• Vandrevala Foundation: +91 9999 666 555 (24/7 Free)\n");
        sb.append("• Emergency Medical: 112");
        return sb.toString();
    }

    public static String buildCrisisMessageWithoutContact() {
        return "⚠️ NO EMERGENCY CONTACT CONFIGURED\n\n"
                + "You haven't set up an emergency contact in Antara yet.\n\n"
                + "Please reach out right now to someone you trust in your life—a family member, close friend, or doctor.\n\n"
                + "Or call one of these free, confidential 24/7 crisis helplines immediately:\n"
                + "• Tele-MANAS (Govt. of India): 14416 (Toll-Free)\n"
                + "• KIRAN Mental Health: 1800-599-0019 (Toll-Free)\n"
                + "• Vandrevala Foundation: +91 9999 666 555 (24/7 Free)\n"
                + "• Emergency Medical: 112\n\n"
                + "👉 Please add an emergency contact now so Antara can alert them with a gentle check-in if you ever need support.";
    }

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
