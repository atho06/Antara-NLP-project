package com.antara.app.nlp;

import java.util.regex.Pattern;

public class CrisisClassifier {

    // Idiomatic and figurative expressions that contain "die", "kill", "dead" but are strictly NOT crises
    private static final Pattern[] FIGURATIVE_PATTERNS = new Pattern[]{
            Pattern.compile("\\b(dying|died|die)\\s+(of|from|with)\\s+laughter\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(dying|died|die)\\s+laughing\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(dying|died|die)\\s+(of|from)\\s+embarrassment\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(dying|died)\\s+to\\s+(see|know|hear|go|meet|watch|read|try)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bto\\s+die\\s+for\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(killing|kills)\\s+me\\s+(with|of)?\\s*(laughter|laughing|humor)?\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(feet|legs|back|head|shoes|joke)\\s+(is|are)\\s+killing\\s+me\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bkilling\\s+it\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bdead\\s+(tired|serious|bored|exhausted)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bdrop\\s+dead\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\blaugh(ing|ed)?\\s+(so\\s+hard|to\\s+death)\\b", Pattern.CASE_INSENSITIVE)
    };

    // Explicit negations
    private static final Pattern[] NEGATION_PATTERNS = new Pattern[]{
            Pattern.compile("\\b(don'?t|do\\s+not|never|would\\s+never|won'?t|will\\s+not|not\\s+going\\s+to)\\s+want\\s+to\\s+(die|end|kill|hurt)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bnot\\s+suicid(e|al)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(don'?t|do\\s+not)\\s+feel\\s+like\\s+dying\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bnot\\s+(trying|wanting)\\s+to\\s+hurt\\s+myself\\b", Pattern.CASE_INSENSITIVE)
    };

    // Genuine crisis patterns
    private static final Pattern[] CRISIS_PATTERNS = new Pattern[]{
            Pattern.compile("\\b(kill|end)\\s+(my|this)\\s+(life|self)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bwant\\s+to\\s+die\\b(?!\\s+(of|from|with)\\s+laughter)", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bwant\\s+to\\s+(disappear|sleep forever)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bsuicid(e|al)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bbetter\\s+off\\s+dead\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bcan'?t\\s+take\\s+this\\s+anymore\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bno\\s+reason\\s+to\\s+live\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(don'?t|do not)\\s+want\\s+to\\s+(live|exist|be alive)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bwant\\s+to\\s+(end\\s+it\\s+all|give\\s+up\\s+on\\s+life)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bcan'?t\\s+(go\\s+on|continue\\s+living|survive\\s+this)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(hurt|harm|harming|cut|cutting)\\s+myself\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(feel\\s+like|thinking\\s+about)\\s+(ending\\s+my\\s+life|suicide)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(feel\\s+like|thinking\\s+about)\\s+dying\\b(?!\\s+(of|from|with)\\s+laughter)", Pattern.CASE_INSENSITIVE)
    };

    public static String buildCrisisMessageWithContact(String contactName, String contactPhone) {
        return buildCrisisMessageWithContact(contactName, contactPhone, "");
    }

    public static String buildCrisisMessageWithContact(String contactName, String contactPhone, String contactEmail) {
        String name = (contactName != null && !contactName.trim().isEmpty()) ? contactName.trim() : "Emergency Contact";
        String phone = (contactPhone != null && !contactPhone.trim().isEmpty()) ? contactPhone.trim() : "";
        String email = (contactEmail != null && !contactEmail.trim().isEmpty()) ? contactEmail.trim() : "";

        StringBuilder sb = new StringBuilder();
        sb.append("PRIMARY EMERGENCY CONTACT (CALL FIRST):\n");
        sb.append("Name: ").append(name).append("\n");
        sb.append("Phone: ").append(phone).append("\n");
        if (!email.isEmpty()) {
            sb.append("Email: ").append(email).append("\n");
        }
        sb.append("\nI hear how much pain you are carrying right now. Your safety is the top priority.\n");
        sb.append("Please reach out to ").append(name).append(" right away—you don't have to face this alone.\n\n");
        sb.append("24/7 Professional Helplines:\n");
        sb.append("• Tele-MANAS (Govt. of India): 14416 (Toll-Free)\n");
        sb.append("• KIRAN Mental Health: 1800-599-0019 (Toll-Free)\n");
        sb.append("• Vandrevala Foundation: +91 9999 666 555 (24/7 Free)");
        return sb.toString();
    }

    public static String buildCrisisMessageWithoutContact() {
        return "NO EMERGENCY CONTACT CONFIGURED\n\n"
                + "You haven't set up an emergency contact in Antara yet.\n\n"
                + "Please reach out right now to someone you trust—a family member, close friend, or doctor.\n\n"
                + "Or call one of these free, confidential 24/7 crisis helplines immediately:\n"
                + "• Tele-MANAS (Govt. of India): 14416 (Toll-Free)\n"
                + "• KIRAN Mental Health: 1800-599-0019 (Toll-Free)\n"
                + "• Vandrevala Foundation: +91 9999 666 555 (24/7 Free)\n\n"
                + "Please add an emergency contact now so you can reach out to them quickly with a check-in if you ever need support.";
    }

    public static boolean checkCrisis(String text) {
        if (text == null || text.trim().isEmpty()) return false;
        String clean = text.trim();

        // 1. Exclude figurative expressions / idioms (e.g. dying of laughter)
        for (Pattern p : FIGURATIVE_PATTERNS) {
            if (p.matcher(clean).find()) {
                return false;
            }
        }

        // 2. Exclude negated statements
        for (Pattern p : NEGATION_PATTERNS) {
            if (p.matcher(clean).find()) {
                return false;
            }
        }

        // 3. Match genuine crisis
        for (Pattern p : CRISIS_PATTERNS) {
            if (p.matcher(clean).find()) {
                return true;
            }
        }
        return false;
    }
}
