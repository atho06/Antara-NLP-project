package com.antara.app.utils;

import android.content.Context;
import android.content.SharedPreferences;

import androidx.appcompat.app.AppCompatDelegate;

public class ThemeHelper {

    private static final String PREF_NAME = "antara_theme_pref";
    private static final String KEY_THEME_MODE = "theme_mode";

    public static final int THEME_LIGHT = 0;
    public static final int THEME_DARK = 1;
    public static final int THEME_SYSTEM = 2;
    public static final int THEME_AMBER = 3; // Warm Sunrise
    public static final int THEME_MINT = 4;  // Serene Sage

    public static void applyTheme(Context context) {
        int mode = getSavedTheme(context);
        applyMode(mode);
    }

    public static void setTheme(Context context, int mode) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        prefs.edit().putInt(KEY_THEME_MODE, mode).apply();
        applyMode(mode);
    }

    public static int getSavedTheme(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return prefs.getInt(KEY_THEME_MODE, THEME_SYSTEM);
    }

    public static String getThemeName(int mode) {
        switch (mode) {
            case THEME_LIGHT:
                return "🌸 Light Mode (Blossom)";
            case THEME_DARK:
                return "🌙 Dark Mode (Midnight)";
            case THEME_AMBER:
                return "🌅 Amber Sunrise (Mood Uplift)";
            case THEME_MINT:
                return "🌿 Serene Sage (Stress Relief)";
            case THEME_SYSTEM:
            default:
                return "⚙️ Follow System Default";
        }
    }

    public static int recommendThemeForEmotion(String emotion) {
        if (emotion == null) return THEME_SYSTEM;
        String lower = emotion.toLowerCase();
        if (lower.contains("sad") || lower.contains("low") || lower.contains("exhaust")) {
            return THEME_AMBER; // Warm uplifting tones
        } else if (lower.contains("stress") || lower.contains("anxi") || lower.contains("anger") || lower.contains("frustrat")) {
            return THEME_MINT;  // Soothing grounding green
        } else if (lower.contains("joy") || lower.contains("humor")) {
            return THEME_LIGHT; // Bright blossom
        } else {
            return THEME_DARK;  // Night / Midnight calm
        }
    }

    private static void applyMode(int mode) {
        switch (mode) {
            case THEME_LIGHT:
            case THEME_AMBER:
            case THEME_MINT:
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO);
                break;
            case THEME_DARK:
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES);
                break;
            case THEME_SYSTEM:
            default:
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM);
                break;
        }
    }
}
