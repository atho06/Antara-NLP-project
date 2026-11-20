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
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class AntaraDatabaseHelper extends SQLiteOpenHelper {

    private static final String DATABASE_NAME = "antara_local.db";
    private static final int DATABASE_VERSION = 1;

    // Table: Users
    public static final String TABLE_USERS = "users";
    public static final String COL_USER_ID = "id";
    public static final String COL_USER_NAME = "full_name";
    public static final String COL_USER_EMAIL = "email";
    public static final String COL_USER_PASSWORD = "password_hash";
    public static final String COL_USER_PHONE = "phone";
    public static final String COL_USER_CONTACT_NAME = "trusted_contact_name";
    public static final String COL_USER_CONTACT_PHONE = "trusted_contact_phone";
    public static final String COL_USER_EMAIL_VERIFIED = "email_verified";
    public static final String COL_USER_PHONE_VERIFIED = "phone_verified";
    public static final String COL_USER_CONTACT_VERIFIED = "trusted_contact_verified";
    public static final String COL_USER_CREATED_AT = "created_at";

    // Table: Sessions
    public static final String TABLE_SESSIONS = "sessions";
    public static final String COL_SESS_ID = "id";
    public static final String COL_SESS_USER_ID = "user_id";
    public static final String COL_SESS_DURATION = "duration_minutes";
    public static final String COL_SESS_CATEGORY = "category";
    public static final String COL_SESS_EMOTION = "dominant_emotion";
    public static final String COL_SESS_SUMMARY = "summary";
    public static final String COL_SESS_EXCHANGES = "exchanges_count";
    public static final String COL_SESS_COMPLETED_AT = "completed_at";

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
                + COL_USER_EMAIL_VERIFIED + " INTEGER DEFAULT 0, "
                + COL_USER_PHONE_VERIFIED + " INTEGER DEFAULT 0, "
                + COL_USER_CONTACT_VERIFIED + " INTEGER DEFAULT 0, "
                + COL_USER_CREATED_AT + " TEXT)";

        String createSessionsTable = "CREATE TABLE " + TABLE_SESSIONS + " ("
                + COL_SESS_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, "
                + COL_SESS_USER_ID + " INTEGER, "
                + COL_SESS_DURATION + " INTEGER, "
                + COL_SESS_CATEGORY + " TEXT, "
                + COL_SESS_EMOTION + " TEXT, "
                + COL_SESS_SUMMARY + " TEXT, "
                + COL_SESS_EXCHANGES + " INTEGER, "
                + COL_SESS_COMPLETED_AT + " TEXT)";

        db.execSQL(createUsersTable);
        db.execSQL(createSessionsTable);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_SESSIONS);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_USERS);
        onCreate(db);
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
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COL_USER_NAME, name);
        values.put(COL_USER_EMAIL, email.trim().toLowerCase(Locale.ROOT));
        values.put(COL_USER_PASSWORD, hashPassword(password));
        values.put(COL_USER_PHONE, phone != null ? phone.trim() : "");
        values.put(COL_USER_CONTACT_NAME, contactName != null ? contactName.trim() : "");
        values.put(COL_USER_CONTACT_PHONE, contactPhone != null ? contactPhone.trim() : "");
        values.put(COL_USER_EMAIL_VERIFIED, 0);
        values.put(COL_USER_PHONE_VERIFIED, 0);
        values.put(COL_USER_CONTACT_VERIFIED, 0);
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

        public UserProfile(long id, String fullName, String email, String phone, String trustedContactName, String trustedContactPhone) {
            this.id = id;
            this.fullName = fullName != null ? fullName : "Antara Friend";
            this.email = email != null ? email : "";
            this.phone = phone != null ? phone : "";
            this.trustedContactName = trustedContactName != null ? trustedContactName : "";
            this.trustedContactPhone = trustedContactPhone != null ? trustedContactPhone : "";
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
            cursor.close();
            return new UserProfile(userId, name, email, phone, contactName, contactPhone);
        }
        if (cursor != null) cursor.close();
        return null;
    }

    // Update Emergency Contact
    public boolean updateEmergencyContact(long userId, String contactName, String contactPhone) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_USER_CONTACT_NAME, contactName != null ? contactName.trim() : "");
        cv.put(COL_USER_CONTACT_PHONE, contactPhone != null ? contactPhone.trim() : "");
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

    // Save Session Record
    public long saveSession(long userId, int durationMinutes, String category, 
                            String dominantEmotion, String summary, int exchangesCount) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_SESS_USER_ID, userId);
        cv.put(COL_SESS_DURATION, durationMinutes);
        cv.put(COL_SESS_CATEGORY, category);
        cv.put(COL_SESS_EMOTION, dominantEmotion);
        cv.put(COL_SESS_SUMMARY, summary);
        cv.put(COL_SESS_EXCHANGES, exchangesCount);
        cv.put(COL_SESS_COMPLETED_AT, new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(new Date()));

        return db.insert(TABLE_SESSIONS, null, cv);
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

                list.add(new SessionRecord(id, userId, duration, cat, emotion, summary, count, date));
            } while (cursor.moveToNext());
            cursor.close();
        }
        return list;
    }
}
