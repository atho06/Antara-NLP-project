package com.antara.app.data;

import android.content.Context;
import android.content.SharedPreferences;

import com.antara.app.models.ChatMessage;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class DraftSessionManager {

    private static final String PREF_NAME = "antara_draft_sessions";
    private static final String KEY_ACTIVE = "draft_is_active_";
    private static final String KEY_CATEGORY = "draft_category_";
    private static final String KEY_DURATION = "draft_duration_";
    private static final String KEY_ELAPSED = "draft_elapsed_";
    private static final String KEY_TIMESTAMP = "draft_left_timestamp_";
    private static final String KEY_MESSAGES = "draft_messages_";

    public static class DraftSession {
        public final String category;
        public final int durationMinutes;
        public final int secondsElapsed;
        public final long leftAtTimestamp;
        public final List<ChatMessage> messages;

        public DraftSession(String category, int durationMinutes, int secondsElapsed, long leftAtTimestamp, List<ChatMessage> messages) {
            this.category = category;
            this.durationMinutes = durationMinutes;
            this.secondsElapsed = secondsElapsed;
            this.leftAtTimestamp = leftAtTimestamp;
            this.messages = messages;
        }
    }

    public static void saveDraft(Context context, long userId, String category, int durationMinutes, int secondsElapsed, List<ChatMessage> messages) {
        if (userId <= 0 || messages == null || messages.size() < 2) return;

        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit();

        JSONArray arr = new JSONArray();
        for (ChatMessage m : messages) {
            JSONObject obj = new JSONObject();
            try {
                obj.put("text", m.getText());
                obj.put("isUser", m.isUser());
                obj.put("emotion", m.getEmotion());
                obj.put("isCrisis", m.isCrisis());
                arr.put(obj);
            } catch (Exception ignored) {}
        }

        editor.putBoolean(KEY_ACTIVE + userId, true);
        editor.putString(KEY_CATEGORY + userId, category);
        editor.putInt(KEY_DURATION + userId, durationMinutes);
        editor.putInt(KEY_ELAPSED + userId, secondsElapsed);
        editor.putLong(KEY_TIMESTAMP + userId, System.currentTimeMillis());
        editor.putString(KEY_MESSAGES + userId, arr.toString());
        editor.apply();
    }

    public static boolean hasActiveDraft(Context context, long userId) {
        if (userId <= 0) return false;
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return prefs.getBoolean(KEY_ACTIVE + userId, false);
    }

    public static long getDraftLeftTimestamp(Context context, long userId) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return prefs.getLong(KEY_TIMESTAMP + userId, 0);
    }

    public static DraftSession getDraft(Context context, long userId) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        if (!prefs.getBoolean(KEY_ACTIVE + userId, false)) return null;

        String category = prefs.getString(KEY_CATEGORY + userId, "daily_routine");
        int duration = prefs.getInt(KEY_DURATION + userId, 5);
        int elapsed = prefs.getInt(KEY_ELAPSED + userId, 0);
        long timestamp = prefs.getLong(KEY_TIMESTAMP + userId, 0);
        String jsonStr = prefs.getString(KEY_MESSAGES + userId, "[]");

        List<ChatMessage> list = new ArrayList<>();
        try {
            JSONArray arr = new JSONArray(jsonStr);
            for (int i = 0; i < arr.length(); i++) {
                JSONObject obj = arr.getJSONObject(i);
                String text = obj.getString("text");
                boolean isUser = obj.getBoolean("isUser");
                String emotion = obj.optString("emotion", null);
                boolean isCrisis = obj.optBoolean("isCrisis", false);
                list.add(new ChatMessage(text, isUser, emotion, isCrisis));
            }
        } catch (Exception ignored) {}

        return new DraftSession(category, duration, elapsed, timestamp, list);
    }

    public static void clearDraft(Context context, long userId) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit();
        editor.remove(KEY_ACTIVE + userId);
        editor.remove(KEY_CATEGORY + userId);
        editor.remove(KEY_DURATION + userId);
        editor.remove(KEY_ELAPSED + userId);
        editor.remove(KEY_TIMESTAMP + userId);
        editor.remove(KEY_MESSAGES + userId);
        editor.apply();
    }
}
