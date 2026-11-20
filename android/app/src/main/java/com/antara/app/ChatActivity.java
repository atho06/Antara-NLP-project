package com.antara.app;

import android.Manifest;
import android.app.AlarmManager;
import android.app.AlertDialog;
import android.app.PendingIntent;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.telephony.SmsManager;
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

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.adapters.ChatAdapter;
import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.DraftSessionManager;
import com.antara.app.data.SessionManager;
import com.antara.app.models.ChatMessage;
import com.antara.app.nlp.CrisisClassifier;
import com.antara.app.nlp.NLPEmotionAnalyzer;
import com.antara.app.nlp.QuestionBank;
import com.antara.app.nlp.ConversationalEngine;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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

    // Safe Space De-Escalation State Machine
    private boolean inSafetyHoldMode = false;
    private int safetySupportStep = 0;

    // Interruption / Abrupt Exit Resumption State
    private boolean isResumingInterruptionCheckIn = false;
    private boolean isSessionFinished = false;

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

        boolean isResume = getIntent().getBooleanExtra("is_resume", false);
        DraftSessionManager.DraftSession draft = isResume ? DraftSessionManager.getDraft(this, sessionManager.getUserId()) : null;

        if (isResume && draft != null) {
            // Restore previous conversation state
            category = draft.category;
            durationMinutes = draft.durationMinutes;
            secondsElapsed = draft.secondsElapsed;
            targetSeconds = durationMinutes * 60;
            messageList.addAll(draft.messages);
            turnCount = messageList.size() / 2;

            // Cancel any pending 1-hour alarm notification
            cancelInactivityAlarm();

            // Set resumption check-in flag
            isResumingInterruptionCheckIn = true;

            // Antara asks why they left abruptly & if anything was wrong
            messageList.add(new ChatMessage(
                    "Welcome back 🌷. I noticed you had to step away from our conversation earlier. Was everything okay, or did the conversation feel overwhelming or heavy?",
                    false
            ));
            chatAdapter.notifyDataSetChanged();

            // Options for resumption
            displayOptionButtons(Arrays.asList(
                    "I got interrupted / busy",
                    "It felt a bit overwhelming",
                    "I lost my train of thought",
                    "I just needed a breather",
                    "I'm ready to continue now"
            ));
        } else {
            // New conversation session
            durationMinutes = getIntent().getIntExtra("duration_minutes", 5);
            category = getIntent().getStringExtra("category");
            if (category == null) category = "daily_routine";
            targetSeconds = durationMinutes * 60;

            // Initial welcome message
            messageList.add(new ChatMessage("Hello, I am Antara 🌷. I am here to listen with full care, without any judgment. Let's begin whenever you are ready.", false));

            // Fetch first question with options
            QuestionBank.QuestionItem firstQ = QuestionBank.getNextQuestion(category, askedQuestions);
            messageList.add(new ChatMessage(firstQ.text, false));
            chatAdapter.notifyDataSetChanged();

            // Display choice buttons for first question
            displayOptionButtons(firstQ.options);
        }

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
            btn.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
            btn.setBackgroundResource(R.drawable.bg_option_button);
            btn.setGravity(Gravity.CENTER);
            btn.setPadding(32, 18, 32, 18);

            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(8, 4, 8, 4);
            btn.setLayoutParams(params);

            btn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    handleOptionClick(option);
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

    private void handleOptionClick(String option) {
        if ("➕ Add Emergency Contact".equals(option)) {
            showAddEmergencyContactDialog();
            return;
        }

        if (option.startsWith("💬 Send Check-in")) {
            long userId = sessionManager.getUserId();
            AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
            if (profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty()) {
                String contactName = profile.trustedContactName.isEmpty() ? "Trusted Contact" : profile.trustedContactName;
                String userName = profile.fullName.isEmpty() ? "Your friend" : profile.fullName;
                String smsText = "Hello " + contactName + ", this is a gentle note from Antara. " 
                        + userName + " is going through a very heavy moment today. Please reach out to have a friendly check-in with them.";
                sendSmsViaIntent(profile.trustedContactPhone.trim(), smsText);
                return;
            }
        }

        if (option.startsWith("📞 Call ")) {
            if (option.contains("14416")) {
                dialPhoneNumber("14416");
                return;
            }
            long userId = sessionManager.getUserId();
            AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
            if (profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty()) {
                dialPhoneNumber(profile.trustedContactPhone.trim());
                return;
            }
        }

        processUserMessage(option);
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

        // Check if user clicked or typed add emergency contact command
        if ("➕ Add Emergency Contact".equals(userText.trim())) {
            showAddEmergencyContactDialog();
            return;
        }

        // 1. Add User Message
        messageList.add(new ChatMessage(userText, true));
        chatAdapter.notifyItemInserted(messageList.size() - 1);
        rvChat.smoothScrollToPosition(messageList.size() - 1);

        // 2. If already in Safe Space Hold Mode, handle de-escalation
        if (inSafetyHoldMode) {
            handleSafetySupportModeUserReply(userText);
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

        // 6. Overwhelm / Fatigue Detection
        if (analysis.userFatigued && !isTimeUpPrompted) {
            isTimeUpPrompted = true;
            showContinuationDialog("I notice this might be feeling a bit heavy or tiring. There is zero pressure here. Would you like to take a break and finish, or keep talking?");
            return;
        }

        // 7. Generate Connected, Contextual Dialogue using ConversationalEngine
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

    private void handleResumeCheckInReply(String userText) {
        isResumingInterruptionCheckIn = false;
        String lower = userText.toLowerCase(Locale.ROOT);

        String acknowledgement;
        if (lower.contains("overwhelm") || lower.contains("heavy") || lower.contains("too much") || lower.contains("stress") || lower.contains("hard")) {
            acknowledgement = "Thank you so much for being honest with me. Stepping away when things feel heavy or overwhelming is actually a very healthy and kind act of self-care. There is zero pressure here—we can take everything as gently and slowly as you like.";
        } else if (lower.contains("interrupt") || lower.contains("busy") || lower.contains("call") || lower.contains("work") || lower.contains("distract")) {
            acknowledgement = "Life and interruptions happen all the time! I'm really glad you were able to carve out a moment to come back to this space for yourself.";
        } else if (lower.contains("breather") || lower.contains("break") || lower.contains("pause") || lower.contains("rest") || lower.contains("train of thought")) {
            acknowledgement = "Taking a breather or pausing to gather your thoughts is always completely welcome here. You are in full control of this conversation.";
        } else {
            acknowledgement = "Thank you for letting me know. I'm right here with you, and there is never any rush.";
        }

        QuestionBank.QuestionItem nextQ = QuestionBank.getNextQuestion(category, askedQuestions);
        String continuationPrompt = acknowledgement + "\n\nWhenever you feel ready to continue: " + nextQ.text;

        messageList.add(new ChatMessage(continuationPrompt, false));
        chatAdapter.notifyItemInserted(messageList.size() - 1);
        rvChat.smoothScrollToPosition(messageList.size() - 1);

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

        // 1. Post Crisis / Safety Message (Emergency contact FIRST, bigger)
        if (hasContact) {
            String crisisMsg = CrisisClassifier.buildCrisisMessageWithContact(
                    profile.trustedContactName, 
                    profile.trustedContactPhone, 
                    profile.trustedContactEmail);
            messageList.add(new ChatMessage(crisisMsg, false, "crisis", true));

            // Dispatch Friendly Check-in Reminder SMS to Trusted Contact
            dispatchEmergencyContactAlert();
        } else {
            String crisisMsg = CrisisClassifier.buildCrisisMessageWithoutContact();
            messageList.add(new ChatMessage(crisisMsg, false, "crisis", true));
        }

        // 2. Post Immediate Holding Check-in
        messageList.add(new ChatMessage(
                "I am staying right here with you. Take all the time you need—there is no rush at all.\n\n"
                + "How are you feeling in this exact moment? Are you somewhere safe right now?",
                false
        ));

        chatAdapter.notifyDataSetChanged();
        rvChat.smoothScrollToPosition(messageList.size() - 1);

        // 3. Dynamic options based on contact availability
        List<String> options = new ArrayList<>();
        if (!hasContact) {
            options.add("➕ Add Emergency Contact");
            options.add("📞 Call Tele-MANAS (14416)");
            options.add("I am reaching out to someone I trust");
        } else {
            String callBtn = "📞 Call " + (profile.trustedContactName.isEmpty() ? "Contact" : profile.trustedContactName);
            options.add(callBtn);
            options.add("💬 Send Check-in SMS");
            options.add("📞 Call Tele-MANAS (14416)");
        }
        options.add("I am in a safe space");
        options.add("Can we do a breathing exercise?");
        options.add("Still feeling overwhelmed");
        options.add("Feeling a little calmer now");

        displayOptionButtons(options);
    }

    private void showAddEmergencyContactDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("➕ Add Emergency Contact");
        builder.setMessage("Please provide someone you trust who Antara can contact during heavy or overwhelming moments:");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int pad = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 20, getResources().getDisplayMetrics());
        layout.setPadding(pad, pad / 2, pad, pad / 2);

        final EditText etName = new EditText(this);
        etName.setHint("Contact Name (e.g. Mom, Best Friend, Partner)");
        etName.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
        layout.addView(etName);

        final EditText etPhone = new EditText(this);
        etPhone.setHint("Phone Number (e.g. +91 9876543210)");
        etPhone.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
        etPhone.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.topMargin = pad / 2;
        etPhone.setLayoutParams(lp);
        layout.addView(etPhone);

        final EditText etEmail = new EditText(this);
        etEmail.setHint("Contact Email Address (Optional)");
        etEmail.setInputType(android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        etEmail.setTextColor(ContextCompat.getColor(this, R.color.text_primary));
        LinearLayout.LayoutParams lpEmail = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lpEmail.topMargin = pad / 2;
        etEmail.setLayoutParams(lpEmail);
        layout.addView(etEmail);

        builder.setView(layout);

        builder.setPositiveButton("Save Contact", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String name = etName.getText().toString().trim();
                String phone = etPhone.getText().toString().trim();
                String email = etEmail.getText().toString().trim();
                if (phone.isEmpty()) {
                    Toast.makeText(ChatActivity.this, "Please enter a valid phone number", Toast.LENGTH_SHORT).show();
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
        sb.append("✅ Emergency contact successfully saved:\n");
        sb.append("👤 ").append(name).append("\n");
        sb.append("📞 ").append(phone).append("\n");
        if (email != null && !email.trim().isEmpty()) {
            sb.append("✉️ ").append(email.trim()).append("\n");
        }
        sb.append("\nA gentle check-in reminder is ready for them. Thank you for taking this important step for your safety.");

        // Notify in chat
        messageList.add(new ChatMessage(sb.toString(), false));
        chatAdapter.notifyItemInserted(messageList.size() - 1);
        rvChat.smoothScrollToPosition(messageList.size() - 1);

        // Dispatch SMS
        dispatchEmergencyContactAlert();

        // Update option buttons
        displayOptionButtons(Arrays.asList(
                "📞 Call " + name,
                "💬 Send Check-in SMS",
                "📞 Call Tele-MANAS (14416)",
                "I am in a safe space",
                "Can we do a breathing exercise?",
                "Feeling a little calmer now"
        ));
    }

    private void dispatchEmergencyContactAlert() {
        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);

        if (profile != null && profile.trustedContactPhone != null && !profile.trustedContactPhone.trim().isEmpty()) {
            String contactName = profile.trustedContactName.isEmpty() ? "Trusted Contact" : profile.trustedContactName;
            String contactEmail = profile.trustedContactEmail != null ? profile.trustedContactEmail.trim() : "";

            String emailSuffix = !contactEmail.isEmpty() ? " (and email alert prepared for " + contactEmail + ")" : "";
            messageList.add(new ChatMessage("✉️ A friendly check-in reminder is ready for your trusted contact (" + contactName + ")" + emailSuffix + ". Tap '💬 Send Check-in SMS' below to dispatch it.", false));
        }
    }

    private void handleSafetySupportModeUserReply(String userText) {
        String lower = userText.toLowerCase(Locale.ROOT);

        // Check if user is asking to add emergency contact via text
        if (lower.contains("add emergency contact") || lower.contains("add contact") || lower.contains("set contact")) {
            showAddEmergencyContactDialog();
            return;
        }

        // Check if user typed phone number in safety mode to save as contact
        Pattern phonePat = Pattern.compile("(\\+?\\d{1,3}[- ]?)?(\\d{10})");
        Matcher m = phonePat.matcher(userText);
        if (m.find() && (!hasSavedEmergencyContact() || lower.contains("contact") || lower.contains("phone") || lower.contains("mom") || lower.contains("dad") || lower.contains("friend") || lower.contains("number") || userText.length() < 30)) {
            String extractedPhone = m.group();
            String extractedName = userText.replace(extractedPhone, "").replaceAll("(?i)(my|emergency|contact|is|name|phone|number|save|add|:|trusted)", "").trim();
            if (extractedName.isEmpty()) extractedName = "Trusted Contact";
            saveEmergencyContactAndNotify(extractedName, extractedPhone, "");
            return;
        }

        // Check if user said they reached out to someone they trust
        if (lower.contains("reaching out") || lower.contains("someone i trust") || lower.contains("called a friend") || lower.contains("talking to family")) {
            messageList.add(new ChatMessage(
                    "I am so proud of you for reaching out to someone you trust. Having human connection right now makes all the difference.\n\n"
                    + "I will stay right here quietly with you. Whenever you feel ready, would you like to take a few slow breaths together or rest?",
                    false
            ));
            chatAdapter.notifyItemInserted(messageList.size() - 1);
            rvChat.smoothScrollToPosition(messageList.size() - 1);

            displayOptionButtons(Arrays.asList(
                    "Can we do a breathing exercise?",
                    "Feeling a little calmer now",
                    "Let's wrap up and rest today"
            ));
            return;
        }

        // Check if user confirmed they want to wrap up or resume after calming down
        if (safetySupportStep == 99) {
            if (lower.contains("wrap up") || lower.contains("rest today") || lower.contains("finish")) {
                finishSession();
                return;
            } else if (lower.contains("continue") || lower.contains("ready") || lower.contains("gently")) {
                inSafetyHoldMode = false;
                safetySupportStep = 0;
                // Resume with a warm, gentle reflection
                QuestionBank.QuestionItem nextQ = QuestionBank.getNextQuestion("general", askedQuestions);
                messageList.add(new ChatMessage(
                        "I am so glad we took that gentle pause together. Whenever you feel comfortable, we can gently explore: " + nextQ.text,
                        false
                ));
                chatAdapter.notifyItemInserted(messageList.size() - 1);
                rvChat.smoothScrollToPosition(messageList.size() - 1);
                displayOptionButtons(nextQ.options);
                return;
            }
        }

        // Check if user is feeling calmer / distress is subsiding
        boolean feelingCalmer = (lower.contains("calm") || lower.contains("better") || lower.contains("safe space") || lower.contains("okay now") || lower.contains("lighter") || lower.contains("grounded"))
                && !lower.contains("not safe") && !lower.contains("still") && !lower.contains("worse");

        boolean wantsBreathing = lower.contains("breath") || lower.contains("breathing");

        if (feelingCalmer) {
            messageList.add(new ChatMessage(
                    "I am so deeply glad you are feeling a little calmer and grounded now. That took so much courage to breathe through.\n\n"
                    + "We can take everything very slowly from here. Would you like to gently resume a light reflection, or would you prefer to wrap up and rest for today?",
                    false
            ));
            chatAdapter.notifyItemInserted(messageList.size() - 1);
            rvChat.smoothScrollToPosition(messageList.size() - 1);

            displayOptionButtons(Arrays.asList(
                    "Let's wrap up and rest today",
                    "I feel ready to gently continue",
                    "I want to sit quietly for a bit"
            ));

            safetySupportStep = 99; // ready for decision
            return;
        }

        // If distress still retains: Step 2 Breathing & Somatic Anchor
        if (wantsBreathing || safetySupportStep == 1) {
            safetySupportStep = 2;
            messageList.add(new ChatMessage(
                    "Let's anchor your body right now. You do not have to carry everything in this moment.\n\n"
                    + "Can you feel your feet resting on the floor, or place one hand gently over your chest?\n\n"
                    + "Let's breathe in slowly for 4 seconds... gently hold for 2... and let it out for 4.\n\n"
                    + "How does your chest and heart feel right now?",
                    false
            ));
            chatAdapter.notifyItemInserted(messageList.size() - 1);
            rvChat.smoothScrollToPosition(messageList.size() - 1);

            List<String> opts = new ArrayList<>();
            opts.add("Breathing slowly with you");
            opts.add("Feeling a little calmer now");
            opts.add("Still feeling very shaky");
            if (!hasSavedEmergencyContact()) {
                opts.add("➕ Add Emergency Contact");
            }
            opts.add("Can you stay with me?");
            displayOptionButtons(opts);
            return;
        }

        // If distress still retains: Step 3 Permission to Rest & Self-Compassion
        if (safetySupportStep == 2) {
            safetySupportStep = 3;
            messageList.add(new ChatMessage(
                    "There is zero pressure to 'fix' this right now. Whatever tears or heavy emotions are here, you are allowed to just let them exist.\n\n"
                    + "You are not a burden, and this pain will pass. Can you take a sip of cool water, or wrap yourself in a warm blanket right now?",
                    false
            ));
            chatAdapter.notifyItemInserted(messageList.size() - 1);
            rvChat.smoothScrollToPosition(messageList.size() - 1);

            List<String> opts = new ArrayList<>();
            opts.add("Took a sip of water");
            opts.add("Feeling a little calmer now");
            opts.add("Still feeling very heavy");
            if (!hasSavedEmergencyContact()) {
                opts.add("➕ Add Emergency Contact");
            }
            opts.add("I just needed someone to listen");
            displayOptionButtons(opts);
            return;
        }

        // Fallback Holding Space & Helpline Reassurance
        messageList.add(new ChatMessage(
                "I am right here with you, and remember you never have to be alone in this pain. You can also call Tele-MANAS toll-free at 14416 anytime—they are kind, trained people who will listen without judgment.\n\n"
                + "Take it one breath at a time. What would feel most gentle for you right now?",
                false
        ));
        chatAdapter.notifyItemInserted(messageList.size() - 1);
        rvChat.smoothScrollToPosition(messageList.size() - 1);

        List<String> fallbackOpts = new ArrayList<>();
        fallbackOpts.add("Feeling a little calmer now");
        fallbackOpts.add("I am going to lie down and rest");
        fallbackOpts.add("📞 Call Tele-MANAS (14416)");
        if (!hasSavedEmergencyContact()) {
            fallbackOpts.add("➕ Add Emergency Contact");
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

            // Schedule notification if away for > 1 hour (3,600,000 ms)
            AlarmManager alarmManager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
            if (alarmManager != null) {
                Intent notifyIntent = new Intent(this, NotificationReceiver.class);
                PendingIntent pi = PendingIntent.getBroadcast(
                        this,
                        NotificationReceiver.NOTIFICATION_ID,
                        notifyIntent,
                        PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0)
                );
                long triggerAt = System.currentTimeMillis() + (60 * 60 * 1000L); // 1 hour
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

                // If clock-time duration reached
                if (targetSeconds > 0 && secondsElapsed >= targetSeconds && !isTimeUpPrompted && !inSafetyHoldMode) {
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
        isSessionFinished = true;
        cancelInactivityAlarm();
        DraftSessionManager.clearDraft(this, sessionManager.getUserId());

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
