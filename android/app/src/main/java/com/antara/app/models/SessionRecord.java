package com.antara.app.models;

public class SessionRecord {
    private long id;
    private long userId;
    private int durationMinutes;
    private String category;
    private String dominantEmotion;
    private String summary;
    private int exchangesCount;
    private String completedAt;

    public SessionRecord(long id, long userId, int durationMinutes, String category, 
                         String dominantEmotion, String summary, int exchangesCount, String completedAt) {
        this.id = id;
        this.userId = userId;
        this.durationMinutes = durationMinutes;
        this.category = category;
        this.dominantEmotion = dominantEmotion;
        this.summary = summary;
        this.exchangesCount = exchangesCount;
        this.completedAt = completedAt;
    }

    public long getId() { return id; }
    public long getUserId() { return userId; }
    public int getDurationMinutes() { return durationMinutes; }
    public String getCategory() { return category; }
    public String getDominantEmotion() { return dominantEmotion; }
    public String getSummary() { return summary; }
    public int getExchangesCount() { return exchangesCount; }
    public String getCompletedAt() { return completedAt; }
}
