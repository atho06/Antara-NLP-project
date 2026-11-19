package com.antara.app.models;

public class ChatMessage {
    private String text;
    private boolean isUser;
    private long timestamp;
    private String emotion;
    private boolean isCrisis;

    public ChatMessage(String text, boolean isUser) {
        this.text = text;
        this.isUser = isUser;
        this.timestamp = System.currentTimeMillis();
        this.emotion = null;
        this.isCrisis = false;
    }

    public ChatMessage(String text, boolean isUser, String emotion, boolean isCrisis) {
        this.text = text;
        this.isUser = isUser;
        this.timestamp = System.currentTimeMillis();
        this.emotion = emotion;
        this.isCrisis = isCrisis;
    }

    public String getText() { return text; }
    public boolean isUser() { return isUser; }
    public long getTimestamp() { return timestamp; }
    public String getEmotion() { return emotion; }
    public boolean isCrisis() { return isCrisis; }
}
