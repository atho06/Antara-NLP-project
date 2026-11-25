package com.antara.app;

import android.Manifest;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.DraftSessionManager;
import com.antara.app.data.SessionManager;
import com.antara.app.models.SessionRecord;

import java.util.Calendar;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private static final int NOTIF_PERMISSION_REQ = 102;

    private TextView tvGreetingTime, tvUserName;
    private Button btnSos, btnStartSession;
    private Spinner spnDuration, spnCategory;
    private LinearLayout navHome, navAnalytics, navHistory, navSettings;
    private SessionManager sessionManager;
    private AntaraDatabaseHelper dbHelper;

    // Resume session panel views
    private View cardResumeSession;
    private TextView tvResumeTimeAgo, tvResumeDetails;
    private Button btnResumeSession;

    // Weekly check-in views
    private View cardStreakDashboard;
    private TextView tvStreakTitle, tvStreakLevel, tvStreakSub;
    private TextView dotMon, dotTue, dotWed, dotThu, dotFri, dotSat, dotSun;

    // Cycle & music support views
    private View cardCycleSupport;
    private TextView tvCycleHomeTitle, tvCycleHomeTip;
    private View btnOpenMusicHome;

    // Small insight views
    private TextView tvFactTitle, tvFactText;

    // Peer perspective views
    private TextView tvTestimonialQuote, tvTestimonialAuthor;

    // Feedback / community card views
    private View cardSupporterPreview;
    private Button btnSupporterLearn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        sessionManager = new SessionManager(this);
        dbHelper = new AntaraDatabaseHelper(this);

        tvGreetingTime = findViewById(R.id.tv_greeting_time);
        tvUserName = findViewById(R.id.tv_user_name);
        btnSos = findViewById(R.id.btn_sos_header);
        btnStartSession = findViewById(R.id.btn_start_session);
        spnDuration = findViewById(R.id.spn_duration);
        spnCategory = findViewById(R.id.spn_category);
        navHome = findViewById(R.id.nav_home);
        navAnalytics = findViewById(R.id.nav_analytics);
        navHistory = findViewById(R.id.nav_history);
        navSettings = findViewById(R.id.nav_settings);

        cardResumeSession = findViewById(R.id.card_resume_session);
        tvResumeTimeAgo = findViewById(R.id.tv_resume_time_ago);
        tvResumeDetails = findViewById(R.id.tv_resume_details);
        btnResumeSession = findViewById(R.id.btn_resume_session);

        cardStreakDashboard = findViewById(R.id.card_streak_dashboard);
        tvStreakTitle = findViewById(R.id.tv_streak_title);
        tvStreakLevel = findViewById(R.id.tv_streak_level);
        tvStreakSub = findViewById(R.id.tv_streak_sub);
        dotMon = findViewById(R.id.dot_mon);
        dotTue = findViewById(R.id.dot_tue);
        dotWed = findViewById(R.id.dot_wed);
        dotThu = findViewById(R.id.dot_thu);
        dotFri = findViewById(R.id.dot_fri);
        dotSat = findViewById(R.id.dot_sat);
        dotSun = findViewById(R.id.dot_sun);

        cardCycleSupport = findViewById(R.id.card_cycle_support);
        tvCycleHomeTitle = findViewById(R.id.tv_cycle_home_title);
        tvCycleHomeTip = findViewById(R.id.tv_cycle_home_tip);
        btnOpenMusicHome = findViewById(R.id.btn_open_music_home);

        tvFactTitle = findViewById(R.id.tv_fact_title);
        tvFactText = findViewById(R.id.tv_fact_text);
        tvTestimonialQuote = findViewById(R.id.tv_testimonial_quote);
        tvTestimonialAuthor = findViewById(R.id.tv_testimonial_author);

        cardSupporterPreview = findViewById(R.id.card_supporter_preview);
        btnSupporterLearn = findViewById(R.id.btn_supporter_learn);

        // Populate greeting and user name
        tvGreetingTime.setText(getGreetingLabel());
        String rawName = sessionManager.getUserName();
        if (rawName != null && !rawName.trim().isEmpty() && !"Friend".equalsIgnoreCase(rawName.trim())) {
            String firstName = rawName.trim().split("\\s+")[0];
            tvUserName.setText("Hi, " + firstName + ".");
        } else {
            tvUserName.setText("Hi there.");
        }

        // Duration options
        String[] durations = new String[]{
                "5 minutes",
                "10 minutes",
                "15 minutes",
                "20 minutes",
                "Open reflection"
        };
        ArrayAdapter<String> durAdapter = new ArrayAdapter<>(this, R.layout.item_spinner_selected, durations);
        durAdapter.setDropDownViewResource(R.layout.item_spinner_dropdown);
        spnDuration.setAdapter(durAdapter);

        // Topic categories
        String[] categories = new String[]{
                "Daily routine",
                "Stress and overwhelm",
                "Low energy or sadness",
                "Relationships",
                "General reflection"
        };
        ArrayAdapter<String> catAdapter = new ArrayAdapter<>(this, R.layout.item_spinner_selected, categories);
        catAdapter.setDropDownViewResource(R.layout.item_spinner_dropdown);
        spnCategory.setAdapter(catAdapter);

        // Start Reflection Button
        btnStartSession.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                int durationMins = 5;
                int pos = spnDuration.getSelectedItemPosition();
                if (pos == 0) durationMins = 5;
                else if (pos == 1) durationMins = 10;
                else if (pos == 2) durationMins = 15;
                else if (pos == 3) durationMins = 20;
                else if (pos == 4) durationMins = 0; // open

                String categoryKey = "daily_routine";
                int catPos = spnCategory.getSelectedItemPosition();
                if (catPos == 0) categoryKey = "daily_routine";
                else if (catPos == 1) categoryKey = "stress";
                else if (catPos == 2) categoryKey = "sadness";
                else if (catPos == 3) categoryKey = "relationships";
                else if (catPos == 4) categoryKey = "general";

                Intent intent = new Intent(MainActivity.this, ChatActivity.class);
                intent.putExtra("duration_minutes", durationMins);
                intent.putExtra("category", categoryKey);
                startActivity(intent);
            }
        });

        // Resume Incomplete Session Button
        btnResumeSession.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, ChatActivity.class);
                intent.putExtra("is_resume", true);
                startActivity(intent);
            }
        });

        // Support / SOS Pill
        btnSos.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showSosDialog();
            }
        });

        // Bottom Navigation
        if (navAnalytics != null) {
            navAnalytics.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(new Intent(MainActivity.this, AnalyticsActivity.class));
                }
            });
        }

        navHistory.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(MainActivity.this, HistoryActivity.class));
            }
        });

        navSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(MainActivity.this, SettingsActivity.class));
            }
        });

        if (btnOpenMusicHome != null) {
            btnOpenMusicHome.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    openMusicApp();
                }
            });
        }

        if (btnSupporterLearn != null) {
            btnSupporterLearn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(new Intent(MainActivity.this, FeedbackActivity.class));
                }
            });
        }

        setupDashboardComponents();

        // Request POST_NOTIFICATIONS permission on Android 13+ if needed
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.POST_NOTIFICATIONS}, NOTIF_PERMISSION_REQ);
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        checkActiveDraft();
        setupDashboardComponents();
    }

    private void setupDashboardComponents() {
        long userId = sessionManager.getUserId();

        // 1. Gentle check-in rhythm (non-pressuring)
        int streak = dbHelper.getUserStreak(userId);
        if (tvStreakTitle != null) {
            if (streak <= 0) {
                tvStreakTitle.setText("One day at a time");
            } else if (streak == 1) {
                tvStreakTitle.setText("1 day of checking in");
            } else {
                tvStreakTitle.setText(streak + " days of checking in");
            }
        }
        if (tvStreakLevel != null) {
            if (streak >= 7) {
                tvStreakLevel.setText("Steady rhythm");
            } else if (streak >= 3) {
                tvStreakLevel.setText("Growing gently");
            } else {
                tvStreakLevel.setText("Sprout level");
            }
        }
        if (tvStreakSub != null) {
            if (streak <= 0) {
                tvStreakSub.setText("Your first reflection is a fresh beginning.");
            } else {
                tvStreakSub.setText("Showing up at your own pace is always enough.");
            }
        }

        // Highlight today's day of week
        Calendar cal = Calendar.getInstance();
        int dayOfWeek = cal.get(Calendar.DAY_OF_WEEK);
        highlightDot(dotSun, dayOfWeek == Calendar.SUNDAY);
        highlightDot(dotMon, dayOfWeek == Calendar.MONDAY);
        highlightDot(dotTue, dayOfWeek == Calendar.TUESDAY);
        highlightDot(dotWed, dayOfWeek == Calendar.WEDNESDAY);
        highlightDot(dotThu, dayOfWeek == Calendar.THURSDAY);
        highlightDot(dotFri, dayOfWeek == Calendar.FRIDAY);
        highlightDot(dotSat, dayOfWeek == Calendar.SATURDAY);

        // 2. Cycle rhythm & calming music
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
        if (profile != null && profile.menstrualPhase != null && !profile.menstrualPhase.equals("not_tracking")) {
            if (tvCycleHomeTitle != null) {
                tvCycleHomeTitle.setText("Moving with your cycle");
            }
            if (tvCycleHomeTip != null) {
                if (profile.menstrualPhase.contains("period")) {
                    tvCycleHomeTip.setText("Energy can feel lower right now. Give yourself room for stillness, something warm to drink, and quiet music.");
                } else if (profile.menstrualPhase.contains("luteal")) {
                    tvCycleHomeTip.setText("Things can feel a little heavier during the luteal phase. Go gently with yourself today.");
                } else {
                    tvCycleHomeTip.setText("Noticing your rhythm can help you choose a softer pace. You can update your cycle phase anytime in Settings.");
                }
            }
        } else {
            if (tvCycleHomeTitle != null) {
                tvCycleHomeTitle.setText("Find your softer rhythm");
            }
            if (tvCycleHomeTip != null) {
                tvCycleHomeTip.setText("Make room for rest with calming soundscapes and support that moves with your cycle.");
            }
        }

        // 3. Rotating quiet insights (non-clinical, no unsupported stats)
        String[][] insights = new String[][]{
                {"Rest is part of moving forward.", "Giving yourself permission to pause can ease stress and make space for what comes next."},
                {"Naming a feeling softens it.", "Putting swirling thoughts into a few plain words can make them feel less crowded."},
                {"One slow breath is a start.", "A longer exhale than inhale is a gentle way to remind your body that you can slow down."},
                {"You don't need all the answers.", "Writing something down isn't about solving it right away—it's just setting it down for a moment."},
                {"Come back to where your feet are.", "Noticing the chair beneath you or a sound in the room can help bring you back to the present."}
        };
        int dayOfYear = cal.get(Calendar.DAY_OF_YEAR);
        int insightIdx = Math.abs(dayOfYear) % insights.length;
        if (tvFactTitle != null) {
            tvFactTitle.setText(insights[insightIdx][0]);
        }
        if (tvFactText != null) {
            tvFactText.setText(insights[insightIdx][1]);
        }

        // 4. Rotating peer reflections ("You're not alone")
        String[][] testimonials = new String[][]{
                {"\"When panic felt like a tidal wave, taking it one breath at a time gave me my ground back.\"", "A fellow student, finding their way"},
                {"\"I used to feel guilty for taking time to rest. Pausing reminded me that resting isn't falling behind.\"", "A student navigating exam stress"},
                {"\"Admitting I was overwhelmed was the first step to feeling a little lighter.\"", "A college sophomore"},
                {"\"Having a quiet place where I didn't have to pretend everything was fine helped more than I expected.\"", "A fellow student"}
        };
        int testIdx = Math.abs(dayOfYear) % testimonials.length;
        if (tvTestimonialQuote != null) {
            tvTestimonialQuote.setText(testimonials[testIdx][0]);
        }
        if (tvTestimonialAuthor != null) {
            tvTestimonialAuthor.setText(testimonials[testIdx][1]);
        }

        // 5. Feedback card (shown after a couple of sessions)
        List<SessionRecord> userSessions = dbHelper.getUserSessions(userId);
        if (cardSupporterPreview != null) {
            if (userSessions.size() >= 2 || streak >= 2) {
                cardSupporterPreview.setVisibility(View.VISIBLE);
            } else {
                cardSupporterPreview.setVisibility(View.GONE);
            }
        }
    }

    private void highlightDot(TextView dot, boolean isToday) {
        if (dot == null) return;
        if (isToday) {
            dot.setBackgroundResource(R.drawable.bg_day_circle_today);
            dot.setTextColor(ContextCompat.getColor(this, R.color.on_primary));
        } else {
            dot.setBackgroundResource(R.drawable.bg_day_circle);
            dot.setTextColor(ContextCompat.getColor(this, R.color.text_secondary));
        }
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
                Toast.makeText(this, "Could not open a music app on this device", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void checkActiveDraft() {
        long userId = sessionManager.getUserId();
        if (DraftSessionManager.hasActiveDraft(this, userId)) {
            long leftTimestamp = DraftSessionManager.getDraftLeftTimestamp(this, userId);
            long diffMs = System.currentTimeMillis() - leftTimestamp;
            if (diffMs >= 2 * 60 * 1000) {
                DraftSessionManager.DraftSession draft = DraftSessionManager.getDraft(this, userId);
                if (draft != null) {
                    cardResumeSession.setVisibility(View.VISIBLE);
                    long minutesAgo = diffMs / (60 * 1000);
                    if (minutesAgo < 60) {
                        tvResumeTimeAgo.setText("Paused " + minutesAgo + "m ago");
                    } else {
                        long hoursAgo = minutesAgo / 60;
                        tvResumeTimeAgo.setText("Paused " + hoursAgo + "h ago");
                    }
                    tvResumeDetails.setText("You stepped away from your " + draft.category.replace('_', ' ')
                            + " reflection. You can pick up where you left off whenever you're ready.");
                    return;
                }
            }
        }
        cardResumeSession.setVisibility(View.GONE);
    }

    private String getGreetingLabel() {
        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        if (hour < 12) return "Your morning exhale";
        if (hour < 17) return "Your afternoon exhale";
        return "Your daily exhale";
    }

    private void showSosDialog() {
        new AlertDialog.Builder(this)
                .setTitle("Support helplines")
                .setMessage("If things feel overwhelming or you need to talk to someone right now, these external helplines are free and available 24/7:\n\n"
                        + "• Tele-MANAS (Govt. of India): 14416 (toll-free)\n"
                        + "• KIRAN Mental Health: 1800-599-0019 (toll-free)\n"
                        + "• Vandrevala Foundation: +91 9999 666 555\n\n"
                        + "Antara is a reflection companion, not an emergency service.")
                .setPositiveButton("Call Tele-MANAS", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        Intent callIntent = new Intent(Intent.ACTION_DIAL);
                        callIntent.setData(Uri.parse("tel:14416"));
                        startActivity(callIntent);
                    }
                })
                .setNegativeButton("Close", null)
                .show();
    }
}
