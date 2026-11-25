package com.antara.app;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
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

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.content.res.ResourcesCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.adapters.ChatAdapter;
import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.DraftSessionManager;
import com.antara.app.data.SessionManager;
import com.antara.app.models.ChatMessage;
import com.antara.app.nlp.ConversationalEngine;
import com.antara.app.nlp.CrisisClassifier;
import com.antara.app.nlp.NLPEmotionAnalyzer;
import com.antara.app.nlp.QuestionBank;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ChatActivity extends AppCompatActivity {

    private TextView tvTimer, tvCategory, tvOptionsLabel;
    private Button btnFinish, btnSend;
    private ProgressBar pbTimer;
    private RecyclerView rvChat;
    private EditText etInput;
    private View layoutOptionsContainer;
    private HorizontalScrollView scrollOptions;
    private LinearLayout layoutOptions;

    private List<ChatMessage> messageList;
    private ChatAdapter chatAdapter;
    private Set<String> askedQuestions;
    private List<String> emotionsLog;
    private int turnCount = 0;
    private Set<String> previousTopics;

    // Safe Space De-Escalation State Machine
    private boolean inSafetyHoldMode = false;
    private int safetySupportStep = 0;

    // Interruption / Abrupt Exit Resumption State
    private boolean isResumingInterruptionCheckIn = false;
    private boolean isSessionFinished = false;

    private int durationMinutes;
    private String category;
    private boolean isProcessingMessage = false;
    private int targetSeconds;
    private int secondsElapsed = 0;
    private boolean isTimeUpPrompted = false;

    private final Handler timerHandler = new Handler(Looper.getMainLooper());
    private Runnable timerRunnable;

    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        tvTimer = findViewById(R.id.tv_chat_timer);
        tvCategory = findViewById(R.id.tv_chat_category);
        tvOptionsLabel = findViewById(R.id.tv_options_label);
        btnFinish = findViewById(R.id.btn_chat_finish);
        btnSend = findViewById(R.id.btn_chat_send);
        pbTimer = findViewById(R.id.pb_chat_time);
        rvChat = findViewById(R.id.rv_chat);
        etInput = findViewById(R.id.et_chat_input);
        layoutOptionsContainer = findViewById(R.id.layout_options_container);
        scrollOptions = findViewById(R.id.scroll_options);
        layoutOptions = findViewById(R.id.layout_options);

        messageList = new ArrayList<>();
        askedQuestions = new HashSet<>();
        emotionsLog = new ArrayList<>();
        previousTopics = new HashSet<>();
        turnCount = 0;

        chatAdapter = new ChatAdapter(messageList);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        rvChat.setLayoutManager(layoutManager);
        rvChat.setAdapter(chatAdapter);

        boolean isResume = getIntent().getBooleanExtra("is_resume", false);
        DraftSessionManager.DraftSession draft = isResume ? DraftSessionManager.getDraft(this, sessionManager.getUserId()) : null;

        if (isResume && draft != null) {
            category = draft.category;
            durationMinutes = draft.durationMinutes;
            secondsElapsed = draft.secondsElapsed;
            targetSeconds = durationMinutes * 60;
            messageList.addAll(draft.messages);
            turnCount = messageList.size() / 2;

            cancelInactivityAlarm();
            isResumingInterruptionCheckIn = true;

            messageList.add(new ChatMessage(
                    "Welcome back. I noticed you stepped away earlier. Was everything okay, or did the conversation start to feel a little heavy?",
                    false
            ));
            chatAdapter.notifyDataSetChanged();
            rvChat.scrollToPosition(chatAdapter.getLastAdapterPosition());

            displayOptionButtons(Arrays.asList(
                    "I got interrupted",
                    "It felt a bit overwhelming",
                    "I lost my train of thought",
                    "I just needed a breather",
                    "I'm ready to continue"
            ));
        } else {
            durationMinutes = getIntent().getIntExtra("duration_minutes", 5);
            category = getIntent().getStringExtra("category");
            if (category == null) category = "daily_routine";
            targetSeconds = durationMinutes * 60;

            messageList.add(new ChatMessage(
                    "Hello, I'm Antara. I'm here to listen with care, without judgment. We can begin whenever you're ready.",
                    false
            ));

            QuestionBank.QuestionItem firstQ = QuestionBank.getNextQuestion(category, askedQuestions);
            messageList.add(new ChatMessage(firstQ.text, false));
            chatAdapter.notifyDataSetChanged();

            displayOptionButtons(firstQ.options);
        }

        if (tvCategory != null) {
            tvCategory.setText(formatCategoryLabel(category));
        }
        updateTimerUI();

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

        btnFinish.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finishSession();
            }
        });

        startTimer();
    }

    private String formatCategoryLabel(String cat) {
        if (cat == null) return "Daily routine";
        switch (cat) {
            case "stress":
                return "Stress & overwhelm";
            case "sadness":
                return "Low energy";
            case "relationships":
                return "Relationships";
            case "general":
                return "General reflection";
            case "daily_routine":
            default:
                return "Daily routine";
        }
    }

    private void displayOptionButtons(List<String> options) {
        layoutOptions.removeAllViews();
        if (options == null || options.isEmpty()) {
            layoutOptionsContainer.setVisibility(View.GONE);
            return;
        }

        layoutOptionsContainer.setVisibility(View.VISIBLE);
        if (tvOptionsLabel != null) {
            tvOptionsLabel.setText(turnCount == 0 ? "A place to start" : "Suggested replies");
        }

        int padH = dpToPx(16);
        int padV = dpToPx(10);
        int marginEnd = dpToPx(8);

        for (final String option : options) {
            TextView btn = new TextView(this);
            btn.setText(option);
            btn.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
            btn.setTypeface(ResourcesCompat.getFont(this, R.font.nunito_semibold));
            btn.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
            btn.setBackgroundResource(R.drawable.bg_option_button);
            btn.setGravity(Gravity.CENTER);
            btn.setPadding(padH, padV, padH, padV);

            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(0, dpToPx(2), marginEnd, dpToPx(2));
            btn.setLayoutParams(params);

            btn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    handleOptionClick(option);
                }
            });

            layoutOptions.addView(btn);
        }

        scrollOptions.post(new Runnable() {
            @Override
            public void run() {
                scrollOptions.fullScroll(HorizontalScrollView.FOCUS_LEFT);
            }
        });
    }

    private int dpToPx(int dp) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, dp, getResources().getDisplayMetrics());
    }

    private void handleOptionClick(String option) {
        if (isProcessingMessage) return;
        isProcessingMessage = true;

        layoutOptions.removeAllViews();
        layoutOptionsContainer.setVisibility(View.GONE);

        String lower = option.toLowerCase(Locale.ROOT).trim();

        if ("add emergency contact".equals(lower)) {
            isProcessingMessage = false;
            showAddEmergencyContactDialog();
            return;
        }

        if (lower.contains("open music app") || lower.contains("listen to music") || lower.contains("music player")) {
            isProcessingMessage = false;
            openMusicApp();
            return;
        }

        if (lower.startsWith("send check-in")) {
            long userId = sessionManager.getUserId();
            AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
            if (profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty()) {
                String contactName = profile.trustedContactName.isEmpty() ? "Trusted Contact" : profile.trustedContactName;
                String userName = profile.fullName.isEmpty() ? "Your friend" : profile.fullName;
                String smsText = "Hello " + contactName + ", this is a gentle note from Antara. "
                        + userName + " is going through a heavy moment today. Please reach out for a friendly check-in when you can.";
                sendSmsViaIntent(profile.trustedContactPhone.trim(), smsText);
                isProcessingMessage = false;
                return;
            }
        }

        if (lower.startsWith("call ")) {
            if (option.contains("14416")) {
                isProcessingMessage = false;
                dialPhoneNumber("14416");
                return;
            } else if (option.contains("1800-599-0019") || lower.contains("kiran")) {
                isProcessingMessage = false;
                dialPhoneNumber("18005990019");
                return;
            } else if (option.contains("9999 666 555") || lower.contains("vandrevala")) {
                isProcessingMessage = false;
                dialPhoneNumber("9999666555");
                return;
            }
            long userId = sessionManager.getUserId();
            AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
            if (profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty()) {
                isProcessingMessage = false;
                dialPhoneNumber(profile.trustedContactPhone.trim());
                return;
            }
        }

        if (lower.contains("ready to finish") || lower.contains("finish session") || lower.contains("finish reflection")) {
            isProcessingMessage = false;
            finishSession();
            return;
        }

        processUserMessage(option);
        isProcessingMessage = false;
    }

    private void openMusicApp() {
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.addCategory(Intent.CATEGORY_APP_MUSIC);
        try {
            startActivity(intent);
        } catch (Exception e) {
            try {
                Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse("https://open.spotify.com/genre/wellness-page"));
                startActivity(web);
            } catch (Exception ex) {
                Toast.makeText(this, "Could not open a music app", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void sendSmsViaIntent(String phone, String text) {
        Intent intent = new Intent(Intent.ACTION_SENDTO);
        intent.setData(Uri.parse("smsto:" + Uri.encode(phone)));
        intent.putExtra("sms_body", text);
        try {
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(this, "Could not open messaging app", Toast.LENGTH_SHORT).show();
        }
    }

    private void dialPhoneNumber(String phone) {
        Intent intent = new Intent(Intent.ACTION_DIAL);
        intent.setData(Uri.parse("tel:" + phone));
        try {
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(this, "Could not open phone dialer", Toast.LENGTH_SHORT).show();
        }
    }

    private boolean hasSavedEmergencyContact() {
        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
        return profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty();
    }

    private void processUserMessage(String userText) {
        if (userText == null || userText.trim().isEmpty()) return;

        if ("add emergency contact".equalsIgnoreCase(userText.trim())) {
            showAddEmergencyContactDialog();
            return;
        }

        // 1. Add User Message
        messageList.add(new ChatMessage(userText, true));
        chatAdapter.notifyLastMessageInserted();
        rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

        // 2. If already in Safe Space Hold Mode, handle de-escalation
        if (inSafetyHoldMode) {
            handleSafetySupportModeUserReply(userText);
            return;
        }

        // Check if user requested to talk to a real person / human helpline
        String lower = userText.toLowerCase(Locale.ROOT);
        if (lower.contains("talk to a real person") || lower.contains("real person")
                || lower.contains("talk to a human") || lower.contains("speak to a human")
                || lower.contains("counselor") || lower.contains("therapist")
                || lower.contains("talk to someone real") || lower.contains("call someone")
                || lower.contains("real counselor") || lower.contains("human support")
                || lower.contains("speak to someone")) {
            handleTalkToRealPersonRequest();
            return;
        }

        // 3. On-Device NLP Crisis & Extreme Emotion Check
        if (CrisisClassifier.checkCrisis(userText)) {
            triggerSafetySupportMode();
            return;
        }

        // 4. Interruption / Resumption Check-in Handler
        if (isResumingInterruptionCheckIn) {
            handleResumeCheckInReply(userText);
            return;
        }

        // 5. On-Device NLP Emotion Analysis
        NLPEmotionAnalyzer.EmotionResult analysis = NLPEmotionAnalyzer.analyze(userText);
        emotionsLog.add(analysis.primaryEmotion);

        // 6. Generate Connected, Contextual Dialogue using ConversationalEngine
        turnCount++;
        ConversationalEngine.DialogueResponse dialogResponse =
                ConversationalEngine.generateContextualResponse(userText, turnCount, category, askedQuestions, previousTopics);

        int addedCount = 0;
        if (dialogResponse.acknowledgement != null && !dialogResponse.acknowledgement.isEmpty()) {
            messageList.add(new ChatMessage(dialogResponse.acknowledgement, false));
            addedCount++;
        }
        messageList.add(new ChatMessage(dialogResponse.followUpQuestion, false));
        addedCount++;

        chatAdapter.notifyMessagesAppended(addedCount);
        rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

        displayOptionButtons(dialogResponse.options);
    }

    private void handleResumeCheckInReply(String userText) {
        isResumingInterruptionCheckIn = false;
        String lower = userText.toLowerCase(Locale.ROOT);

        String acknowledgement;
        if (lower.contains("overwhelm") || lower.contains("heavy") || lower.contains("too much") || lower.contains("stress") || lower.contains("hard")) {
            acknowledgement = "Thank you for being honest. Stepping away when things feel heavy is a kind way to look after yourself. There's no pressure here—we can take things slowly.";
        } else if (lower.contains("interrupt") || lower.contains("busy") || lower.contains("call") || lower.contains("work") || lower.contains("distract")) {
            acknowledgement = "Interruptions happen all the time. I'm glad you could take a quiet moment to come back.";
        } else if (lower.contains("breather") || lower.contains("break") || lower.contains("pause") || lower.contains("rest") || lower.contains("train of thought")) {
            acknowledgement = "Taking a breather is always welcome here. You're in control of the pace.";
        } else {
            acknowledgement = "Thank you for letting me know. I'm here whenever you're ready, with no rush.";
        }

        QuestionBank.QuestionItem nextQ = QuestionBank.getNextQuestion(category, askedQuestions);
        messageList.add(new ChatMessage(acknowledgement, false));
        messageList.add(new ChatMessage(nextQ.text, false));
        chatAdapter.notifyMessagesAppended(2);
        rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

        displayOptionButtons(nextQ.options);
    }

    // --- Safety Support Mode & Emergency Contact Flow ---

    private void triggerSafetySupportMode() {
        inSafetyHoldMode = true;
        safetySupportStep = 1;

        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);

        boolean hasContact = (profile != null
                && profile.trustedContactPhone != null
                && !profile.trustedContactPhone.trim().isEmpty());

        if (hasContact) {
            String crisisMsg = CrisisClassifier.buildCrisisMessageWithContact(
                    profile.trustedContactName,
                    profile.trustedContactPhone,
                    profile.trustedContactEmail);
            messageList.add(new ChatMessage(crisisMsg, false, "crisis", true));
            dispatchEmergencyContactAlert();
        } else {
            String crisisMsg = CrisisClassifier.buildCrisisMessageWithoutContact();
            messageList.add(new ChatMessage(crisisMsg, false, "crisis", true));
        }

        messageList.add(new ChatMessage(
                "I'm staying right here with you. Take all the time you need—there is no rush.\n\n"
                        + "How are you feeling in this moment? Are you somewhere safe right now?",
                false
        ));

        chatAdapter.notifyDataSetChanged();
        rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

        List<String> options = new ArrayList<>();
        if (!hasContact) {
            options.add("Add emergency contact");
            options.add("Call Tele-MANAS (14416)");
            options.add("I'm reaching out to someone I trust");
        } else {
            String callBtn = "Call " + (profile.trustedContactName.isEmpty() ? "contact" : profile.trustedContactName);
            options.add(callBtn);
            options.add("Send check-in SMS");
            options.add("Call Tele-MANAS (14416)");
        }
        options.add("I'm in a safe space");
        options.add("Can we do a breathing exercise?");
        options.add("Still feeling overwhelmed");
        options.add("Feeling a little calmer now");

        displayOptionButtons(options);
    }

    private void showAddEmergencyContactDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Add emergency contact");
        builder.setMessage("Add someone you trust so you can reach out to them quickly during heavy moments.");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int pad = dpToPx(20);
        layout.setPadding(pad, pad / 2, pad, pad / 2);

        final EditText etName = new EditText(this);
        etName.setHint("Name (e.g. Mom, Best friend)");
        etName.setBackgroundResource(R.drawable.bg_input);
        etName.setPadding(dpToPx(14), dpToPx(12), dpToPx(14), dpToPx(12));
        etName.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
        layout.addView(etName);

        final EditText etPhone = new EditText(this);
        etPhone.setHint("Phone number");
        etPhone.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
        etPhone.setBackgroundResource(R.drawable.bg_input);
        etPhone.setPadding(dpToPx(14), dpToPx(12), dpToPx(14), dpToPx(12));
        etPhone.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dpToPx(12);
        etPhone.setLayoutParams(lp);
        layout.addView(etPhone);

        final EditText etEmail = new EditText(this);
        etEmail.setHint("Email address (optional)");
        etEmail.setInputType(android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        etEmail.setBackgroundResource(R.drawable.bg_input);
        etEmail.setPadding(dpToPx(14), dpToPx(12), dpToPx(14), dpToPx(12));
        etEmail.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
        LinearLayout.LayoutParams lpEmail = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lpEmail.topMargin = dpToPx(12);
        etEmail.setLayoutParams(lpEmail);
        layout.addView(etEmail);

        builder.setView(layout);

        builder.setPositiveButton("Save contact", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String name = etName.getText().toString().trim();
                String phone = etPhone.getText().toString().trim();
                String email = etEmail.getText().toString().trim();
                if (phone.isEmpty()) {
                    Toast.makeText(ChatActivity.this, "Please enter a phone number", Toast.LENGTH_SHORT).show();
                    return;
                }
                if (name.isEmpty()) name = "Trusted Contact";
                saveEmergencyContactAndNotify(name, phone, email);
            }
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void saveEmergencyContactAndNotify(String name, String phone, String email) {
        long userId = sessionManager.getUserId();
        dbHelper.updateEmergencyContact(userId, name, phone, email);

        StringBuilder sb = new StringBuilder();
        sb.append("Emergency contact saved on this device:\n");
        sb.append("• Name: ").append(name).append("\n");
        sb.append("• Phone: ").append(phone).append("\n");
        if (email != null && !email.trim().isEmpty()) {
            sb.append("• Email: ").append(email.trim()).append("\n");
        }
        sb.append("\nYou can call or open a check-in text for them below.");

        messageList.add(new ChatMessage(sb.toString(), false));
        chatAdapter.notifyLastMessageInserted();
        rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

        dispatchEmergencyContactAlert();

        displayOptionButtons(Arrays.asList(
                "Call " + name,
                "Send check-in SMS",
                "Call Tele-MANAS (14416)",
                "I'm in a safe space",
                "Can we do a breathing exercise?",
                "Feeling a little calmer now"
        ));
    }

    private void dispatchEmergencyContactAlert() {
        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);

        if (profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty()) {
            String contactName = profile.trustedContactName.isEmpty() ? "Trusted Contact" : profile.trustedContactName;
            messageList.add(new ChatMessage(
                    "A check-in message is ready for " + contactName + ". Tap 'Send check-in SMS' below to open your messaging app with it.",
                    false
            ));
        }
    }

    private void handleSafetySupportModeUserReply(String userText) {
        String lower = userText.toLowerCase(Locale.ROOT);

        if (lower.contains("add emergency contact") || lower.contains("add contact") || lower.contains("set contact")) {
            showAddEmergencyContactDialog();
            return;
        }

        Pattern phonePat = Pattern.compile("(\\+?\\d{1,3}[- ]?)?(\\d{10})");
        Matcher m = phonePat.matcher(userText);
        if (m.find() && (!hasSavedEmergencyContact() || lower.contains("contact") || lower.contains("phone") || lower.contains("mom") || lower.contains("dad") || lower.contains("friend") || lower.contains("number") || userText.length() < 30)) {
            String extractedPhone = m.group();
            String extractedName = userText.replace(extractedPhone, "").replaceAll("(?i)(my|emergency|contact|is|name|phone|number|save|add|:|trusted)", "").trim();
            if (extractedName.isEmpty()) extractedName = "Trusted Contact";
            saveEmergencyContactAndNotify(extractedName, extractedPhone, "");
            return;
        }

        if (lower.contains("reaching out") || lower.contains("someone i trust") || lower.contains("called a friend") || lower.contains("talking to family")) {
            messageList.add(new ChatMessage(
                    "I'm really glad you're reaching out to someone you trust. Connecting with a real person can help a lot right now.\n\n"
                            + "I'll stay right here. Whenever you're ready, we can take a few slow breaths together or wrap up so you can rest.",
                    false
            ));
            chatAdapter.notifyLastMessageInserted();
            rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

            displayOptionButtons(Arrays.asList(
                    "Can we do a breathing exercise?",
                    "Feeling a little calmer now",
                    "Let's wrap up and rest today"
            ));
            return;
        }

        if (safetySupportStep == 99) {
            if (lower.contains("wrap up") || lower.contains("rest today") || lower.contains("finish")) {
                finishSession();
                return;
            } else if (lower.contains("continue") || lower.contains("ready") || lower.contains("gently")) {
                inSafetyHoldMode = false;
                safetySupportStep = 0;
                QuestionBank.QuestionItem nextQ = QuestionBank.getNextQuestion("general", askedQuestions);
                messageList.add(new ChatMessage("I'm glad we took that pause together. Whenever you're ready:", false));
                messageList.add(new ChatMessage(nextQ.text, false));
                chatAdapter.notifyMessagesAppended(2);
                rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());
                displayOptionButtons(nextQ.options);
                return;
            }
        }

        boolean feelingCalmer = (lower.contains("calm") || lower.contains("better") || lower.contains("safe space") || lower.contains("okay now") || lower.contains("lighter") || lower.contains("grounded"))
                && !lower.contains("not safe") && !lower.contains("still") && !lower.contains("worse");

        boolean wantsBreathing = lower.contains("breath") || lower.contains("breathing");

        if (feelingCalmer) {
            messageList.add(new ChatMessage(
                    "I'm glad you're feeling a little steadier now. We can take things slowly from here.\n\n"
                            + "Would you like to gently continue reflecting, or wrap up and rest for today?",
                    false
            ));
            chatAdapter.notifyLastMessageInserted();
            rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

            displayOptionButtons(Arrays.asList(
                    "Let's wrap up and rest today",
                    "I feel ready to gently continue",
                    "I want to sit quietly for a bit"
            ));

            safetySupportStep = 99;
            return;
        }

        if (wantsBreathing || safetySupportStep == 1) {
            safetySupportStep = 2;
            messageList.add(new ChatMessage(
                    "Let's slow down for a moment. You don't have to carry everything at once.\n\n"
                            + "Notice your feet resting on the floor, or place a hand gently over your chest. Breathe in slowly for 4 seconds, pause for 2, and breathe out for 4.\n\n"
                            + "How does your body feel right now?",
                    false
            ));
            chatAdapter.notifyLastMessageInserted();
            rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

            List<String> opts = new ArrayList<>();
            opts.add("Breathing slowly with you");
            opts.add("Feeling a little calmer now");
            opts.add("Still feeling very shaky");
            if (!hasSavedEmergencyContact()) {
                opts.add("Add emergency contact");
            }
            opts.add("Can you stay with me?");
            displayOptionButtons(opts);
            return;
        }

        if (safetySupportStep == 2) {
            safetySupportStep = 3;
            messageList.add(new ChatMessage(
                    "There is no pressure to fix anything right now. Whatever heavy feelings are here, you're allowed to let them be.\n\n"
                            + "If you can, take a sip of cool water or get comfortable somewhere warm.",
                    false
            ));
            chatAdapter.notifyLastMessageInserted();
            rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

            List<String> opts = new ArrayList<>();
            opts.add("Took a sip of water");
            opts.add("Feeling a little calmer now");
            opts.add("Still feeling very heavy");
            if (!hasSavedEmergencyContact()) {
                opts.add("Add emergency contact");
            }
            opts.add("I just needed someone to listen");
            displayOptionButtons(opts);
            return;
        }

        messageList.add(new ChatMessage(
                "I'm right here with you. You can also call Tele-MANAS toll-free at 14416 anytime to speak with a trained person who will listen without judgment.\n\n"
                        + "Take it one breath at a time. What would feel gentlest right now?",
                false
        ));
        chatAdapter.notifyLastMessageInserted();
        rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

        List<String> fallbackOpts = new ArrayList<>();
        fallbackOpts.add("Feeling a little calmer now");
        fallbackOpts.add("I'm going to lie down and rest");
        fallbackOpts.add("Call Tele-MANAS (14416)");
        if (!hasSavedEmergencyContact()) {
            fallbackOpts.add("Add emergency contact");
        }
        fallbackOpts.add("Still feeling overwhelmed");
        displayOptionButtons(fallbackOpts);
    }

    @Override
    protected void onPause() {
        super.onPause();
        saveDraftAndScheduleAlarm();
    }

    private void saveDraftAndScheduleAlarm() {
        if (!isSessionFinished && messageList != null && messageList.size() >= 2) {
            long userId = sessionManager.getUserId();
            DraftSessionManager.saveDraft(this, userId, category, durationMinutes, secondsElapsed, messageList);

            AlarmManager alarmManager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
            if (alarmManager != null) {
                Intent notifyIntent = new Intent(this, NotificationReceiver.class);
                PendingIntent pi = PendingIntent.getBroadcast(
                        this,
                        NotificationReceiver.NOTIFICATION_ID,
                        notifyIntent,
                        PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0)
                );
                long triggerAt = System.currentTimeMillis() + (60 * 60 * 1000L);
                alarmManager.set(AlarmManager.RTC_WAKEUP, triggerAt, pi);
            }
        }
    }

    private void cancelInactivityAlarm() {
        AlarmManager alarmManager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        if (alarmManager != null) {
            Intent notifyIntent = new Intent(this, NotificationReceiver.class);
            PendingIntent pi = PendingIntent.getBroadcast(
                    this,
                    NotificationReceiver.NOTIFICATION_ID,
                    notifyIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0)
            );
            alarmManager.cancel(pi);
        }
    }

    private void startTimer() {
        timerRunnable = new Runnable() {
            @Override
            public void run() {
                secondsElapsed++;
                updateTimerUI();

                if (targetSeconds > 0 && secondsElapsed >= targetSeconds && !isTimeUpPrompted && !inSafetyHoldMode) {
                    isTimeUpPrompted = true;
                    showContinuationDialog("We've reached your " + durationMinutes + "-minute mark. Would you like to wrap up or take a little more time?");
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
            tvTimer.setText(String.format(Locale.getDefault(), "%02d:%02d · Open", m, s));
            pbTimer.setProgress(0);
        } else {
            int remaining = Math.max(0, targetSeconds - secondsElapsed);
            int m = remaining / 60;
            int s = remaining % 60;
            tvTimer.setText(String.format(Locale.getDefault(), "%d:%02d left", m, s));
            int percent = (int) (((float) secondsElapsed / targetSeconds) * 100);
            pbTimer.setProgress(Math.min(100, percent));
        }
    }

    private void handleTalkToRealPersonRequest() {
        String botMsg = "I completely understand. While I'm here as a reflection companion, speaking with a real person can make a big difference.\n\n"
                + "These external helplines are free and available 24/7:\n"
                + "• Tele-MANAS (Govt. of India): 14416 (toll-free)\n"
                + "• KIRAN Mental Health: 1800-599-0019 (toll-free)\n"
                + "• Vandrevala Foundation: +91 9999 666 555";

        messageList.add(new ChatMessage(botMsg, false));
        chatAdapter.notifyLastMessageInserted();
        rvChat.smoothScrollToPosition(chatAdapter.getLastAdapterPosition());

        List<String> options = new ArrayList<>();
        options.add("Call Tele-MANAS (14416)");
        options.add("Call KIRAN (1800-599-0019)");
        options.add("Call Vandrevala (+91 9999 666 555)");

        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
        if (profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty()) {
            options.add("Call " + (profile.trustedContactName.isEmpty() ? "emergency contact" : profile.trustedContactName));
        }

        options.add("I'd like to continue reflecting here");
        options.add("I'm going to call now");
        displayOptionButtons(options);
    }

    private void showContinuationDialog(String message) {
        final String[] choices = new String[]{
                "+2 minutes (brief pause)",
                "+5 minutes (gentle reflection)",
                "+10 minutes (unhurried space)",
                "Open reflection (no timer)",
                "Wrap up and view summary"
        };

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Time check-in");
        builder.setMessage(message);
        builder.setItems(choices, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                switch (which) {
                    case 0:
                        targetSeconds += 120;
                        durationMinutes += 2;
                        isTimeUpPrompted = false;
                        Toast.makeText(ChatActivity.this, "Added 2 minutes. Take your time.", Toast.LENGTH_SHORT).show();
                        break;
                    case 1:
                        targetSeconds += 300;
                        durationMinutes += 5;
                        isTimeUpPrompted = false;
                        Toast.makeText(ChatActivity.this, "Added 5 minutes. Take your time.", Toast.LENGTH_SHORT).show();
                        break;
                    case 2:
                        targetSeconds += 600;
                        durationMinutes += 10;
                        isTimeUpPrompted = false;
                        Toast.makeText(ChatActivity.this, "Added 10 minutes. Take your time.", Toast.LENGTH_SHORT).show();
                        break;
                    case 3:
                        targetSeconds = 0;
                        isTimeUpPrompted = false;
                        Toast.makeText(ChatActivity.this, "Switched to open reflection.", Toast.LENGTH_SHORT).show();
                        break;
                    case 4:
                        finishSession();
                        break;
                }
            }
        });
        builder.setCancelable(false);
        builder.show();
    }

    private void finishSession() {
        isSessionFinished = true;
        cancelInactivityAlarm();
        DraftSessionManager.clearDraft(this, sessionManager.getUserId());

        timerHandler.removeCallbacks(timerRunnable);

        String dominant = "calm_grounded";
        if (!emotionsLog.isEmpty()) {
            dominant = emotionsLog.get(0);
        }

        int reflectionsCount = messageList.size() / 2;
        String durationPhrase = durationMinutes > 0
                ? durationMinutes + "-minute reflection"
                : "open reflection";
        String summary = "In today's " + durationPhrase + ", you shared "
                + reflectionsCount + (reflectionsCount == 1 ? " reflection" : " reflections")
                + ". Your tone leaned toward " + dominant.replace('_', ' ')
                + ". Thank you for taking a quiet moment for yourself.";

        long userId = sessionManager.getUserId();
        String emotionsJoined = android.text.TextUtils.join(",", emotionsLog);
        dbHelper.saveSession(userId, durationMinutes, category, dominant, summary, reflectionsCount, emotionsJoined);
        dbHelper.updateUserStreak(userId);

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
