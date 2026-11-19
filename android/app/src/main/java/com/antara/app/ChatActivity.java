package com.antara.app;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.adapters.ChatAdapter;
import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;
import com.antara.app.models.ChatMessage;
import com.antara.app.nlp.CrisisClassifier;
import com.antara.app.nlp.NLPEmotionAnalyzer;
import com.antara.app.nlp.QuestionBank;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class ChatActivity extends AppCompatActivity {

    private TextView tvTimer;
    private Button btnFinish, btnSend;
    private ProgressBar pbTimer;
    private RecyclerView rvChat;
    private EditText etInput;

    private List<ChatMessage> messageList;
    private ChatAdapter chatAdapter;
    private Set<String> askedQuestions;
    private List<String> emotionsLog;

    private int durationMinutes;
    private String category;
    private int targetSeconds;
    private int secondsElapsed = 0;
    private boolean isTimeUpPrompted = false;

    private Handler timerHandler = new Handler(Looper.getMainLooper());
    private Runnable timerRunnable;

    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        durationMinutes = getIntent().getIntExtra("duration_minutes", 5);
        category = getIntent().getStringExtra("category");
        if (category == null) category = "daily_routine";

        targetSeconds = durationMinutes * 60;

        tvTimer = findViewById(R.id.tv_chat_timer);
        btnFinish = findViewById(R.id.btn_chat_finish);
        btnSend = findViewById(R.id.btn_chat_send);
        pbTimer = findViewById(R.id.pb_chat_time);
        rvChat = findViewById(R.id.rv_chat);
        etInput = findViewById(R.id.et_chat_input);

        messageList = new ArrayList<>();
        askedQuestions = new HashSet<>();
        emotionsLog = new ArrayList<>();

        chatAdapter = new ChatAdapter(messageList);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvChat.setLayoutManager(layoutManager);
        rvChat.setAdapter(chatAdapter);

        // Initial welcome messages
        messageList.add(new ChatMessage("Hello, I am Antara 🌷. I am here to listen with full care, without any judgment. Let's begin whenever you are ready.", false));
        String firstQ = QuestionBank.getNextQuestion(category, askedQuestions);
        messageList.add(new ChatMessage(firstQ, false));
        chatAdapter.notifyDataSetChanged();

        // Send Button
        btnSend.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                handleSendMessage();
            }
        });

        // Finish Button
        btnFinish.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finishSession();
            }
        });

        startTimer();
    }

    private void startTimer() {
        timerRunnable = new Runnable() {
            @Override
            public void run() {
                secondsElapsed++;
                updateTimerUI();

                // If clock-time duration reached
                if (targetSeconds > 0 && secondsElapsed >= targetSeconds && !isTimeUpPrompted) {
                    isTimeUpPrompted = true;
                    showContinuationDialog("We have reached your chosen " + durationMinutes + "-minute mark. You did great today. Would you like to wrap up or continue talking?");
                }

                timerHandler.postDelayed(this, 1000);
            }
        };
        timerHandler.postDelayed(timerRunnable, 1000);
    }

    private void updateTimerUI() {
        if (targetSeconds == 0) {
            int m = secondsElapsed / 60;
            int s = secondsElapsed % 60;
            tvTimer.setText(String.format(Locale.getDefault(), "⏱️ %02d:%02d (Open)", m, s));
            pbTimer.setProgress(0);
        } else {
            int remaining = Math.max(0, targetSeconds - secondsElapsed);
            int m = remaining / 60;
            int s = remaining % 60;
            tvTimer.setText(String.format(Locale.getDefault(), "⏱️ %02d:%02d remaining", m, s));
            int percent = (int) (((float) secondsElapsed / targetSeconds) * 100);
            pbTimer.setProgress(Math.min(100, percent));
        }
    }

    private void handleSendMessage() {
        String text = etInput.getText().toString().trim();
        if (text.isEmpty()) return;

        etInput.setText("");

        // 1. Add User Message
        messageList.add(new ChatMessage(text, true));
        chatAdapter.notifyItemInserted(messageList.size() - 1);
        rvChat.smoothScrollToPosition(messageList.size() - 1);

        // 2. On-Device NLP Crisis Check
        if (CrisisClassifier.checkCrisis(text)) {
            messageList.add(new ChatMessage(CrisisClassifier.SAFETY_MESSAGE, false, "crisis", true));
            chatAdapter.notifyItemInserted(messageList.size() - 1);
            rvChat.smoothScrollToPosition(messageList.size() - 1);
            return;
        }

        // 3. On-Device NLP Emotion Analysis
        NLPEmotionAnalyzer.EmotionResult analysis = NLPEmotionAnalyzer.analyze(text);
        emotionsLog.add(analysis.primaryEmotion);

        // 4. Overwhelm / Fatigue Detection
        if (analysis.userFatigued && !isTimeUpPrompted) {
            isTimeUpPrompted = true;
            showContinuationDialog("I notice this might be feeling a bit heavy or tiring. There is zero pressure here. Would you like to take a break and finish, or keep talking?");
            return;
        }

        // 5. Generate Next Gentle Acknowledgement and Question
        String[] acks = new String[]{
                "Thank you for sharing that with me.",
                "I hear you, and it makes complete sense that you feel this way.",
                "Thank you for opening up—it takes courage to reflect like this.",
                "I appreciate you expressing that so honestly."
        };
        String ack = acks[(int) (Math.random() * acks.length)];

        messageList.add(new ChatMessage(ack, false));
        String nextQ = QuestionBank.getNextQuestion(category, askedQuestions);
        messageList.add(new ChatMessage(nextQ, false));

        chatAdapter.notifyItemRangeInserted(messageList.size() - 2, 2);
        rvChat.smoothScrollToPosition(messageList.size() - 1);
    }

    private void showContinuationDialog(String message) {
        new AlertDialog.Builder(this)
                .setTitle("⏱️ Time Check-in")
                .setMessage(message)
                .setPositiveButton("Wrap Up & Finish", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        finishSession();
                    }
                })
                .setNegativeButton("Keep Talking", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        targetSeconds = 0; // extend indefinitely
                        dialog.dismiss();
                    }
                })
                .setCancelable(false)
                .show();
    }

    private void finishSession() {
        timerHandler.removeCallbacks(timerRunnable);

        // Calculate Dominant Emotion
        String dominant = "calm_grounded";
        if (!emotionsLog.isEmpty()) {
            dominant = emotionsLog.get(0);
        }

        int reflectionsCount = messageList.size() / 2;
        String summary = "In today's " + durationMinutes + "-minute session, you explored " 
                + reflectionsCount + " thoughtful reflections. Your emotional tone centered around " 
                + dominant.replace('_', ' ') + ". Thank you for showing up for yourself and taking this time to listen inward.";

        // Save into local SQLite
        long userId = sessionManager.getUserId();
        dbHelper.saveSession(userId, durationMinutes, category, dominant, summary, reflectionsCount);

        // Open Summary Activity
        Intent intent = new Intent(ChatActivity.this, SessionSummaryActivity.class);
        intent.putExtra("duration_minutes", durationMinutes);
        intent.putExtra("reflections_count", reflectionsCount);
        intent.putExtra("dominant_emotion", dominant);
        intent.putExtra("summary_text", summary);
        startActivity(intent);
        finish();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (timerHandler != null && timerRunnable != null) {
            timerHandler.removeCallbacks(timerRunnable);
        }
    }
}
