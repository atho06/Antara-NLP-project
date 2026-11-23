package com.antara.app.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import com.antara.app.models.SessionRecord;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class AntaraDatabaseHelper extends SQLiteOpenHelper {

    private static final String DATABASE_NAME = "antara_local.db";
    private static final int DATABASE_VERSION = 3;

    // Table: Users
    public static final String TABLE_USERS = "users";
    public static final String COL_USER_ID = "id";
    public static final String COL_USER_NAME = "full_name";
    public static final String COL_USER_EMAIL = "email";
    public static final String COL_USER_PASSWORD = "password_hash";
    public static final String COL_USER_PHONE = "phone";
    public static final String COL_USER_CONTACT_NAME = "trusted_contact_name";
    public static final String COL_USER_CONTACT_PHONE = "trusted_contact_phone";
    public static final String COL_USER_CONTACT_EMAIL = "trusted_contact_email";
    public static final String COL_USER_EMAIL_VERIFIED = "email_verified";
    public static final String COL_USER_PHONE_VERIFIED = "phone_verified";
    public static final String COL_USER_CONTACT_VERIFIED = "trusted_contact_verified";
    public static final String COL_USER_MENSTRUAL_PHASE = "menstrual_phase";
    public static final String COL_USER_STREAK_COUNT = "streak_count";
    public static final String COL_USER_LAST_STREAK_DATE = "last_streak_date";
    public static final String COL_USER_CREATED_AT = "created_at";

    // Table: Sessions
    public static final String TABLE_SESSIONS = "sessions";
    public static final String COL_SESS_ID = "id";
    public static final String COL_SESS_USER_ID = "user_id";
    public static final String COL_SESS_DURATION = "duration_minutes";
    public static final String COL_SESS_CATEGORY = "category";
    public static final String COL_SESS_EMOTION = "dominant_emotion";
    public static final String COL_SESS_EMOTIONS_LOG = "emotions_log";
    public static final String COL_SESS_SUMMARY = "summary";
    public static final String COL_SESS_EXCHANGES = "exchanges_count";
    public static final String COL_SESS_COMPLETED_AT = "completed_at";

    // Table: Feedback
    public static final String TABLE_FEEDBACK = "feedback";
    public static final String COL_FEEDBACK_ID = "id";
    public static final String COL_FEEDBACK_USER_ID = "user_id";
    public static final String COL_FEEDBACK_CATEGORY = "category";
    public static final String COL_FEEDBACK_RATING = "rating";
    public static final String COL_FEEDBACK_TEXT = "feedback_text";
    public static final String COL_FEEDBACK_CREATED_AT = "created_at";

    public AntaraDatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        String createUsersTable = "CREATE TABLE " + TABLE_USERS + " ("
                + COL_USER_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, "
                + COL_USER_NAME + " TEXT, "
                + COL_USER_EMAIL + " TEXT UNIQUE, "
                + COL_USER_PASSWORD + " TEXT, "
                + COL_USER_PHONE + " TEXT, "
                + COL_USER_CONTACT_NAME + " TEXT, "
                + COL_USER_CONTACT_PHONE + " TEXT, "
                + COL_USER_CONTACT_EMAIL + " TEXT, "
                + COL_USER_EMAIL_VERIFIED + " INTEGER DEFAULT 0, "
                + COL_USER_PHONE_VERIFIED + " INTEGER DEFAULT 0, "
                + COL_USER_CONTACT_VERIFIED + " INTEGER DEFAULT 0, "
                + COL_USER_MENSTRUAL_PHASE + " TEXT DEFAULT 'not_tracking', "
                + COL_USER_STREAK_COUNT + " INTEGER DEFAULT 0, "
                + COL_USER_LAST_STREAK_DATE + " TEXT DEFAULT '', "
                + COL_USER_CREATED_AT + " TEXT)";

        String createSessionsTable = "CREATE TABLE " + TABLE_SESSIONS + " ("
                + COL_SESS_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, "
                + COL_SESS_USER_ID + " INTEGER, "
                + COL_SESS_DURATION + " INTEGER, "
                + COL_SESS_CATEGORY + " TEXT, "
                + COL_SESS_EMOTION + " TEXT, "
                + COL_SESS_EMOTIONS_LOG + " TEXT DEFAULT '', "
                + COL_SESS_SUMMARY + " TEXT, "
                + COL_SESS_EXCHANGES + " INTEGER, "
                + COL_SESS_COMPLETED_AT + " TEXT)";

        String createFeedbackTable = "CREATE TABLE IF NOT EXISTS " + TABLE_FEEDBACK + " ("
                + COL_FEEDBACK_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, "
                + COL_FEEDBACK_USER_ID + " INTEGER, "
                + COL_FEEDBACK_CATEGORY + " TEXT, "
                + COL_FEEDBACK_RATING + " INTEGER, "
                + COL_FEEDBACK_TEXT + " TEXT, "
                + COL_FEEDBACK_CREATED_AT + " TEXT)";

        db.execSQL(createUsersTable);
        db.execSQL(createSessionsTable);
        db.execSQL(createFeedbackTable);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        if (oldVersion < 2) {
            try {
                db.execSQL("ALTER TABLE " + TABLE_USERS + " ADD COLUMN " + COL_USER_CONTACT_EMAIL + " TEXT DEFAULT ''");
            } catch (Exception ignored) {}
        }
        if (oldVersion < 3) {
            try {
                db.execSQL("ALTER TABLE " + TABLE_SESSIONS + " ADD COLUMN " + COL_SESS_EMOTIONS_LOG + " TEXT DEFAULT ''");
            } catch (Exception ignored) {}
            try {
                db.execSQL("ALTER TABLE " + TABLE_USERS + " ADD COLUMN " + COL_USER_MENSTRUAL_PHASE + " TEXT DEFAULT 'not_tracking'");
            } catch (Exception ignored) {}
            try {
                db.execSQL("ALTER TABLE " + TABLE_USERS + " ADD COLUMN " + COL_USER_STREAK_COUNT + " INTEGER DEFAULT 0");
            } catch (Exception ignored) {}
            try {
                db.execSQL("ALTER TABLE " + TABLE_USERS + " ADD COLUMN " + COL_USER_LAST_STREAK_DATE + " TEXT DEFAULT ''");
            } catch (Exception ignored) {}
        }
        db.execSQL("CREATE TABLE IF NOT EXISTS " + TABLE_FEEDBACK + " ("
                + COL_FEEDBACK_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, "
                + COL_FEEDBACK_USER_ID + " INTEGER, "
                + COL_FEEDBACK_CATEGORY + " TEXT, "
                + COL_FEEDBACK_RATING + " INTEGER, "
                + COL_FEEDBACK_TEXT + " TEXT, "
                + COL_FEEDBACK_CREATED_AT + " TEXT)");
    }

    // Password Hashing
    public static String hashPassword(String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(password.getBytes());
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            return String.valueOf(password.hashCode());
        }
    }

    // User Registration
    public long registerUser(String name, String email, String password, String phone, 
                             String contactName, String contactPhone) {
        return registerUser(name, email, password, phone, contactName, contactPhone, "");
    }

    public long registerUser(String name, String email, String password, String phone, 
                             String contactName, String contactPhone, String contactEmail) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COL_USER_NAME, name);
        values.put(COL_USER_EMAIL, email.trim().toLowerCase(Locale.ROOT));
        values.put(COL_USER_PASSWORD, hashPassword(password));
        values.put(COL_USER_PHONE, phone != null ? phone.trim() : "");
        values.put(COL_USER_CONTACT_NAME, contactName != null ? contactName.trim() : "");
        values.put(COL_USER_CONTACT_PHONE, contactPhone != null ? contactPhone.trim() : "");
        values.put(COL_USER_CONTACT_EMAIL, contactEmail != null ? contactEmail.trim().toLowerCase(Locale.ROOT) : "");
        values.put(COL_USER_EMAIL_VERIFIED, 0);
        values.put(COL_USER_PHONE_VERIFIED, 0);
        values.put(COL_USER_CONTACT_VERIFIED, 0);
        values.put(COL_USER_MENSTRUAL_PHASE, "not_tracking");
        values.put(COL_USER_STREAK_COUNT, 0);
        values.put(COL_USER_LAST_STREAK_DATE, "");
        values.put(COL_USER_CREATED_AT, new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date()));

        return db.insert(TABLE_USERS, null, values);
    }

    // User Login
    public long authenticateUser(String email, String password) {
        SQLiteDatabase db = this.getReadableDatabase();
        String hashedPassword = hashPassword(password);
        Cursor cursor = db.query(TABLE_USERS, new String[]{COL_USER_ID}, 
                COL_USER_EMAIL + "=? AND " + COL_USER_PASSWORD + "=?", 
                new String[]{email.trim().toLowerCase(Locale.ROOT), hashedPassword}, 
                null, null, null);

        long userId = -1;
        if (cursor != null && cursor.moveToFirst()) {
            userId = cursor.getLong(0);
            cursor.close();
        }
        return userId;
    }

    public static class UserProfile {
        public final long id;
        public final String fullName;
        public final String email;
        public final String phone;
        public final String trustedContactName;
        public final String trustedContactPhone;
        public final String trustedContactEmail;
        public final String menstrualPhase;
        public final int streakCount;

        public UserProfile(long id, String fullName, String email, String phone, 
                           String trustedContactName, String trustedContactPhone, String trustedContactEmail,
                           String menstrualPhase, int streakCount) {
            this.id = id;
            this.fullName = fullName != null ? fullName : "Antara Friend";
            this.email = email != null ? email : "";
            this.phone = phone != null ? phone : "";
            this.trustedContactName = trustedContactName != null ? trustedContactName : "";
            this.trustedContactPhone = trustedContactPhone != null ? trustedContactPhone : "";
            this.trustedContactEmail = trustedContactEmail != null ? trustedContactEmail : "";
            this.menstrualPhase = menstrualPhase != null ? menstrualPhase : "not_tracking";
            this.streakCount = streakCount;
        }
    }

    public UserProfile getUserProfile(long userId) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.query(TABLE_USERS, null, COL_USER_ID + "=?", 
                new String[]{String.valueOf(userId)}, null, null, null);
        if (cursor != null && cursor.moveToFirst()) {
            String name = cursor.getString(cursor.getColumnIndexOrThrow(COL_USER_NAME));
            String email = cursor.getString(cursor.getColumnIndexOrThrow(COL_USER_EMAIL));
            String phone = cursor.getString(cursor.getColumnIndexOrThrow(COL_USER_PHONE));
            String contactName = cursor.getString(cursor.getColumnIndexOrThrow(COL_USER_CONTACT_NAME));
            String contactPhone = cursor.getString(cursor.getColumnIndexOrThrow(COL_USER_CONTACT_PHONE));
            
            String contactEmail = "";
            int emailIdx = cursor.getColumnIndex(COL_USER_CONTACT_EMAIL);
            if (emailIdx != -1) contactEmail = cursor.getString(emailIdx);

            String phase = "not_tracking";
            int phaseIdx = cursor.getColumnIndex(COL_USER_MENSTRUAL_PHASE);
            if (phaseIdx != -1) {
                String p = cursor.getString(phaseIdx);
                if (p != null) phase = p;
            }

            int streak = 0;
            int streakIdx = cursor.getColumnIndex(COL_USER_STREAK_COUNT);
            if (streakIdx != -1) streak = cursor.getInt(streakIdx);

            cursor.close();
            return new UserProfile(userId, name, email, phone, contactName, contactPhone, contactEmail, phase, streak);
        }
        if (cursor != null) cursor.close();
        return null;
    }

    // Update Emergency Contact
    public boolean updateEmergencyContact(long userId, String contactName, String contactPhone) {
        return updateEmergencyContact(userId, contactName, contactPhone, "");
    }

    public boolean updateEmergencyContact(long userId, String contactName, String contactPhone, String contactEmail) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_USER_CONTACT_NAME, contactName != null ? contactName.trim() : "");
        cv.put(COL_USER_CONTACT_PHONE, contactPhone != null ? contactPhone.trim() : "");
        cv.put(COL_USER_CONTACT_EMAIL, contactEmail != null ? contactEmail.trim().toLowerCase(Locale.ROOT) : "");
        int rows = db.update(TABLE_USERS, cv, COL_USER_ID + "=?", new String[]{String.valueOf(userId)});
        return rows > 0;
    }

    // Update User Profile Details
    public boolean updateUserProfile(long userId, String fullName, String email, String phone) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_USER_NAME, fullName != null ? fullName.trim() : "");
        cv.put(COL_USER_EMAIL, email != null ? email.trim().toLowerCase(Locale.ROOT) : "");
        cv.put(COL_USER_PHONE, phone != null ? phone.trim() : "");
        int rows = db.update(TABLE_USERS, cv, COL_USER_ID + "=?", new String[]{String.valueOf(userId)});
        return rows > 0;
    }

    // Update Menstrual Phase
    public boolean updateMenstrualPhase(long userId, String phase) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_USER_MENSTRUAL_PHASE, phase != null ? phase : "not_tracking");
        int rows = db.update(TABLE_USERS, cv, COL_USER_ID + "=?", new String[]{String.valueOf(userId)});
        return rows > 0;
    }

    // Update Verification Status
    public boolean setVerification(long userId, String field, boolean verified) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(field, verified ? 1 : 0);
        int rows = db.update(TABLE_USERS, cv, COL_USER_ID + "=?", new String[]{String.valueOf(userId)});
        return rows > 0;
    }

    // Save Session Record (with optional emotionsLog)
    public long saveSession(long userId, int durationMinutes, String category, 
                            String dominantEmotion, String summary, int exchangesCount) {
        return saveSession(userId, durationMinutes, category, dominantEmotion, summary, exchangesCount, "");
    }

    public long saveSession(long userId, int durationMinutes, String category, 
                            String dominantEmotion, String summary, int exchangesCount, String emotionsLog) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_SESS_USER_ID, userId);
        cv.put(COL_SESS_DURATION, durationMinutes);
        cv.put(COL_SESS_CATEGORY, category);
        cv.put(COL_SESS_EMOTION, dominantEmotion);
        cv.put(COL_SESS_EMOTIONS_LOG, emotionsLog != null ? emotionsLog : "");
        cv.put(COL_SESS_SUMMARY, summary);
        cv.put(COL_SESS_EXCHANGES, exchangesCount);
        cv.put(COL_SESS_COMPLETED_AT, new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(new Date()));

        long sessId = db.insert(TABLE_SESSIONS, null, cv);
        updateUserStreak(userId);
        return sessId;
    }

    // Streak Calculation
    private void updateUserStreak(long userId) {
        try {
            SQLiteDatabase db = this.getWritableDatabase();
            Cursor cursor = db.query(TABLE_USERS, new String[]{COL_USER_STREAK_COUNT, COL_USER_LAST_STREAK_DATE}, 
                    COL_USER_ID + "=?", new String[]{String.valueOf(userId)}, null, null, null);
            
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
            String today = sdf.format(new Date());

            Calendar cal = Calendar.getInstance();
            cal.add(Calendar.DAY_OF_YEAR, -1);
            String yesterday = sdf.format(cal.getTime());

            int currentStreak = 0;
            String lastDate = "";

            if (cursor != null && cursor.moveToFirst()) {
                currentStreak = cursor.getInt(0);
                lastDate = cursor.getString(1);
                cursor.close();
            }

            int newStreak = currentStreak;
            if (lastDate == null || lastDate.isEmpty()) {
                newStreak = 1;
            } else if (lastDate.equals(today)) {
                // Already reflected today, streak stays intact
                return;
            } else if (lastDate.equals(yesterday)) {
                newStreak = currentStreak + 1;
            } else {
                newStreak = 1;
            }

            ContentValues cv = new ContentValues();
            cv.put(COL_USER_STREAK_COUNT, newStreak);
            cv.put(COL_USER_LAST_STREAK_DATE, today);
            db.update(TABLE_USERS, cv, COL_USER_ID + "=?", new String[]{String.valueOf(userId)});
        } catch (Exception ignored) {}
    }

    public int getUserStreak(long userId) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.query(TABLE_USERS, new String[]{COL_USER_STREAK_COUNT, COL_USER_LAST_STREAK_DATE}, 
                COL_USER_ID + "=?", new String[]{String.valueOf(userId)}, null, null, null);
        int streak = 0;
        if (cursor != null && cursor.moveToFirst()) {
            streak = cursor.getInt(0);
            cursor.close();
        }
        return Math.max(0, streak);
    }

    // Save Feedback
    public long saveFeedback(long userId, String category, int rating, String text) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_FEEDBACK_USER_ID, userId);
        cv.put(COL_FEEDBACK_CATEGORY, category != null ? category : "General");
        cv.put(COL_FEEDBACK_RATING, rating);
        cv.put(COL_FEEDBACK_TEXT, text != null ? text.trim() : "");
        cv.put(COL_FEEDBACK_CREATED_AT, new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date()));
        return db.insert(TABLE_FEEDBACK, null, cv);
    }

    // Get Sessions for User
    public List<SessionRecord> getUserSessions(long userId) {
        List<SessionRecord> list = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.query(TABLE_SESSIONS, null, COL_SESS_USER_ID + "=?", 
                new String[]{String.valueOf(userId)}, null, null, COL_SESS_ID + " DESC");

        if (cursor != null && cursor.moveToFirst()) {
            do {
                long id = cursor.getLong(cursor.getColumnIndexOrThrow(COL_SESS_ID));
                int duration = cursor.getInt(cursor.getColumnIndexOrThrow(COL_SESS_DURATION));
                String cat = cursor.getString(cursor.getColumnIndexOrThrow(COL_SESS_CATEGORY));
                String emotion = cursor.getString(cursor.getColumnIndexOrThrow(COL_SESS_EMOTION));
                String summary = cursor.getString(cursor.getColumnIndexOrThrow(COL_SESS_SUMMARY));
                int count = cursor.getInt(cursor.getColumnIndexOrThrow(COL_SESS_EXCHANGES));
                String date = cursor.getString(cursor.getColumnIndexOrThrow(COL_SESS_COMPLETED_AT));

                String emotionsLog = "";
                int logIdx = cursor.getColumnIndex(COL_SESS_EMOTIONS_LOG);
                if (logIdx != -1) emotionsLog = cursor.getString(logIdx);

                list.add(new SessionRecord(id, userId, duration, cat, emotion, summary, count, date, emotionsLog));
            } while (cursor.moveToNext());
            cursor.close();
        }
        return list;
    }
}
