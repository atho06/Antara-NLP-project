package com.antara.app;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.adapters.ChatAdapter;
import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;
import com.antara.app.models.ChatMessage;
import com.antara.app.nlp.CrisisClassifier;
import com.antara.app.nlp.NLPEmotionAnalyzer;
import com.antara.app.nlp.QuestionBank;
import com.antara.app.nlp.ConversationalEngine;

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
    private HorizontalScrollView scrollOptions;
    private LinearLayout layoutOptions;

    private List<ChatMessage> messageList;
    private ChatAdapter chatAdapter;
    private Set<String> askedQuestions;
    private List<String> emotionsLog;
    private int turnCount = 0;
    private Set<String> previousTopics;

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
        scrollOptions = findViewById(R.id.scroll_options);
        layoutOptions = findViewById(R.id.layout_options);

        messageList = new ArrayList<>();
        askedQuestions = new HashSet<>();
        emotionsLog = new ArrayList<>();
        previousTopics = new HashSet<>();
        turnCount = 0;

        chatAdapter = new ChatAdapter(messageList);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvChat.setLayoutManager(layoutManager);
        rvChat.setAdapter(chatAdapter);

        // Initial welcome message
        messageList.add(new ChatMessage("Hello, I am Antara 🌷. I am here to listen with full care, without any judgment. Let's begin whenever you are ready.", false));
        
        // Fetch first question with options
        QuestionBank.QuestionItem firstQ = QuestionBank.getNextQuestion(category, askedQuestions);
        messageList.add(new ChatMessage(firstQ.text, false));
        chatAdapter.notifyDataSetChanged();

        // Display choice buttons for first question
        displayOptionButtons(firstQ.options);

        // Send Button for custom typed input
        btnSend.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String typedText = etInput.getText().toString().trim();
                if (!typedText.isEmpty()) {
                    etInput.setText("");
                    processUserMessage(typedText);
                }
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

    private void displayOptionButtons(List<String> options) {
        layoutOptions.removeAllViews();
        if (options == null || options.isEmpty()) {
            scrollOptions.setVisibility(View.GONE);
            return;
        }

        scrollOptions.setVisibility(View.VISIBLE);

        for (final String option : options) {
            TextView btn = new TextView(this);
            btn.setText(option);
            btn.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
            btn.setTextColor(ContextCompat.getColor(this, R.color.primary));
            btn.setBackgroundResource(R.drawable.bg_option_button);
            btn.setGravity(Gravity.CENTER);

            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(8, 4, 8, 4);
            btn.setLayoutParams(params);

            btn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    processUserMessage(option);
                }
            });

            layoutOptions.addView(btn);
        }

        // Scroll back to start
        scrollOptions.post(new Runnable() {
            @Override
            public void run() {
                scrollOptions.fullScroll(HorizontalScrollView.FOCUS_LEFT);
            }
        });
    }

    private void processUserMessage(String userText) {
        if (userText == null || userText.trim().isEmpty()) return;

        // 1. Add User Message
        messageList.add(new ChatMessage(userText, true));
        chatAdapter.notifyItemInserted(messageList.size() - 1);
        rvChat.smoothScrollToPosition(messageList.size() - 1);

        // 2. On-Device NLP Crisis Check
        if (CrisisClassifier.checkCrisis(userText)) {
            layoutOptions.removeAllViews();
            scrollOptions.setVisibility(View.GONE);
            messageList.add(new ChatMessage(CrisisClassifier.SAFETY_MESSAGE, false, "crisis", true));
            chatAdapter.notifyItemInserted(messageList.size() - 1);
            rvChat.smoothScrollToPosition(messageList.size() - 1);
            return;
        }

        // 3. On-Device NLP Emotion Analysis
        NLPEmotionAnalyzer.EmotionResult analysis = NLPEmotionAnalyzer.analyze(userText);
        emotionsLog.add(analysis.primaryEmotion);

        // 4. Overwhelm / Fatigue Detection
        if (analysis.userFatigued && !isTimeUpPrompted) {
            isTimeUpPrompted = true;
            showContinuationDialog("I notice this might be feeling a bit heavy or tiring. There is zero pressure here. Would you like to take a break and finish, or keep talking?");
            return;
        }

        // 5. Generate Connected, Contextual Dialogue using ConversationalEngine
        turnCount++;
        ConversationalEngine.DialogueResponse dialogResponse = 
                ConversationalEngine.generateContextualResponse(userText, turnCount, previousTopics);

        int addedCount = 0;
        if (dialogResponse.acknowledgement != null && !dialogResponse.acknowledgement.isEmpty()) {
            messageList.add(new ChatMessage(dialogResponse.acknowledgement, false));
            addedCount++;
        }
        messageList.add(new ChatMessage(dialogResponse.followUpQuestion, false));
        addedCount++;

        chatAdapter.notifyItemRangeInserted(messageList.size() - addedCount, addedCount);
        rvChat.smoothScrollToPosition(messageList.size() - 1);

        // Update option buttons for the new contextual question
        displayOptionButtons(dialogResponse.options);
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
