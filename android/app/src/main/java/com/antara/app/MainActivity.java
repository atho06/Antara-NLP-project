package com.antara.app;

import android.Manifest;
import android.app.AlertDialog;
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

import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.antara.app.data.DraftSessionManager;
import com.antara.app.data.SessionManager;

import java.util.Calendar;

public class MainActivity extends AppCompatActivity {

    private static final int NOTIF_PERMISSION_REQ = 102;

    private TextView tvGreetingTime, tvUserName;
    private Button btnSos, btnStartSession;
    private Spinner spnDuration, spnCategory;
    private LinearLayout navHome, navAnalytics, navHistory, navSettings;
    private SessionManager sessionManager;
    private com.antara.app.data.AntaraDatabaseHelper dbHelper;

    // Resume session card views
    private CardView cardResumeSession;
    private TextView tvResumeTimeAgo, tvResumeDetails;
    private Button btnResumeSession;

    // Streak Dashboard Views
    private CardView cardStreakDashboard;
    private TextView tvStreakTitle, tvStreakLevel, tvStreakSub;
    private TextView dotMon, dotTue, dotWed, dotThu, dotFri, dotSat, dotSun;

    // Cycle & Music Support Views
    private CardView cardCycleSupport;
    private TextView tvCycleHomeTitle, tvCycleHomeTip;
    private Button btnOpenMusicHome;

    // Facts & Figures Views
    private TextView tvFactText;

    // Testimonials Views
    private TextView tvTestimonialQuote, tvTestimonialAuthor;

    // Supporter Preview Views
    private CardView cardSupporterPreview;
    private Button btnSupporterLearn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        sessionManager = new SessionManager(this);
        dbHelper = new com.antara.app.data.AntaraDatabaseHelper(this);

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

        tvFactText = findViewById(R.id.tv_fact_text);
        tvTestimonialQuote = findViewById(R.id.tv_testimonial_quote);
        tvTestimonialAuthor = findViewById(R.id.tv_testimonial_author);

        cardSupporterPreview = findViewById(R.id.card_supporter_preview);
        btnSupporterLearn = findViewById(R.id.btn_supporter_learn);

        // Populate user name and greeting
        tvUserName.setText(sessionManager.getUserName());
        tvGreetingTime.setText(getGreetingTime() + ",");

        // Duration options
        String[] durations = new String[]{"5 Minutes", "10 Minutes", "15 Minutes", "20 Minutes", "Open Reflection"};
        ArrayAdapter<String> durAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, durations);
        spnDuration.setAdapter(durAdapter);

        // Topic categories
        String[] categories = new String[]{"Daily Routine", "Stress & Overwhelm", "Low Energy / Sadness", "Relationships", "General Reflection"};
        ArrayAdapter<String> catAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, categories);
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

        // Emergency SOS
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
                    showSupporterDialog();
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

        // 1. Streak & Weekly Progress Indicator
        int streak = dbHelper.getUserStreak(userId);
        if (tvStreakTitle != null) {
            tvStreakTitle.setText("🔥 " + streak + (streak == 1 ? "-Day Streak" : "-Day Streak"));
        }
        if (tvStreakLevel != null) {
            if (streak >= 7) {
                tvStreakLevel.setText("🌳 Grounded Tree");
            } else if (streak >= 3) {
                tvStreakLevel.setText("🌿 Blooming Level");
            } else {
                tvStreakLevel.setText("🌱 Sprout Level");
            }
        }

        // Highlight today's day of week in weekly dots
        Calendar cal = Calendar.getInstance();
        int dayOfWeek = cal.get(Calendar.DAY_OF_WEEK);
        highlightDot(dotSun, dayOfWeek == Calendar.SUNDAY);
        highlightDot(dotMon, dayOfWeek == Calendar.MONDAY);
        highlightDot(dotTue, dayOfWeek == Calendar.TUESDAY);
        highlightDot(dotWed, dayOfWeek == Calendar.WEDNESDAY);
        highlightDot(dotThu, dayOfWeek == Calendar.THURSDAY);
        highlightDot(dotFri, dayOfWeek == Calendar.FRIDAY);
        highlightDot(dotSat, dayOfWeek == Calendar.SATURDAY);

        // 2. Menstrual Cycle Support & Music Redirection
        com.antara.app.data.AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
        if (profile != null && profile.menstrualPhase != null && !profile.menstrualPhase.equals("not_tracking")) {
            String p = profile.menstrualPhase.replace('_', ' ');
            if (tvCycleHomeTitle != null) {
                tvCycleHomeTitle.setText("🌸 " + p.toUpperCase(java.util.Locale.ROOT) + " • Somatic Care");
            }
            if (tvCycleHomeTip != null) {
                if (profile.menstrualPhase.contains("period")) {
                    tvCycleHomeTip.setText("Your body is in a restorative cycle right now. Physical energy naturally lowers; allow yourself gentle stillness, warm tea, and calming soundscapes.");
                } else if (profile.menstrualPhase.contains("luteal")) {
                    tvCycleHomeTip.setText("During the luteal phase, sensitivity and vulnerability can peak. Practice extra self-compassion and listen to grounding music to soothe tension.");
                } else {
                    tvCycleHomeTip.setText("Honoring your hormonal rhythm helps maintain emotional equilibrium. Take 5 minutes to ground your mind.");
                }
            }
        } else {
            if (tvCycleHomeTitle != null) {
                tvCycleHomeTitle.setText("🌸 Cycle Rhythm & Music Regulation");
            }
            if (tvCycleHomeTip != null) {
                tvCycleHomeTip.setText("Listening to calming soundscapes activates the vagus nerve and downregulates cortisol. You can also sync your cycle in Settings for tailored somatic support.");
            }
        }

        // 3. Evidence-Based Psychology & Neuroscience Facts
        String[] facts = new String[]{
                "Putting feelings into words (affect labeling) reduces amygdala reactivity by up to 40% and activates prefrontal regions that restore emotional regulation.",
                "Practicing a 4-second inhale followed by a 6-second exhale activates the parasympathetic nervous system, lowering heart rate and signaling the brain that you are safe.",
                "Research in cognitive psychology shows that writing down swirling worries takes them out of working memory, freeing mental bandwidth and reducing rumination.",
                "Somatic grounding exercises like feeling feet on the floor stimulate mechanoreceptors that disrupt panic loops and return the mind to the present moment.",
                "Neuroimaging studies show that giving yourself compassionate permission to rest restores dopamine baseline and prevents burnout."
        };
        int dayOfYear = cal.get(Calendar.DAY_OF_YEAR);
        if (tvFactText != null) {
            tvFactText.setText(facts[Math.abs(dayOfYear) % facts.length]);
        }

        // 4. Rotating Peer Testimonials ("You Are Not Alone")
        String[][] testimonials = new String[][]{
                {"\"I used to feel so guilty for taking time to rest. Reflecting here reminded me that taking a pause isn't falling behind—it is survival.\"", "— A student peer navigating exam anxiety"},
                {"\"When panic felt like a tidal wave, breaking it down into one breath at a time gave me my ground back.\"", "— Second-year engineering student"},
                {"\"I realized that everyone around me seemed calm only because they were hiding their stress too. Admitting I was overwhelmed was the first step to feeling lighter.\"", "— College sophomore"},
                {"\"Antara gave me a safe space where I didn't have to pretend everything was fine. Sometimes just being heard is all you need.\"", "— Anonymous peer"}
        };
        int testIdx = Math.abs(dayOfYear) % testimonials.length;
        if (tvTestimonialQuote != null) {
            tvTestimonialQuote.setText(testimonials[testIdx][0]);
        }
        if (tvTestimonialAuthor != null) {
            tvTestimonialAuthor.setText(testimonials[testIdx][1]);
        }

        // 5. Supporter Preview (after 2-3 sessions or usage)
        java.util.List<com.antara.app.models.SessionRecord> userSessions = dbHelper.getUserSessions(userId);
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
            dot.setBackgroundColor(ContextCompat.getColor(this, R.color.primary));
            dot.setTextColor(android.graphics.Color.WHITE);
        } else {
            dot.setBackgroundResource(R.drawable.bg_option_button);
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
                android.widget.Toast.makeText(this, "Could not open music player", android.widget.Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void showSupporterDialog() {
        new AlertDialog.Builder(this)
                .setTitle("🌷 Antara Community Patron")
                .setMessage("Antara is built with love as a 100% private, on-device mental wellness companion for students.\n\n"
                        + "• Zero data tracking or ads\n"
                        + "• 100% offline & confidential\n"
                        + "• Free forever for students\n\n"
                        + "Optional Patron support helps us keep serverless mental health resources freely accessible to learners worldwide.")
                .setPositiveButton("I Love Antara 🌸", null)
                .show();
    }

    private void checkActiveDraft() {
        long userId = sessionManager.getUserId();
        if (DraftSessionManager.hasActiveDraft(this, userId)) {
            long leftTimestamp = DraftSessionManager.getDraftLeftTimestamp(this, userId);
            long diffMs = System.currentTimeMillis() - leftTimestamp;
            // Show option to continue if user left and hasn't returned within 2 minutes (120,000 ms)
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
                            + " reflection. Would you like to resume where you left off?");
                    return;
                }
            }
        }
        cardResumeSession.setVisibility(View.GONE);
    }

    private String getGreetingTime() {
        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        if (hour < 12) return "Good morning";
        if (hour < 17) return "Good afternoon";
        return "Good evening";
    }

    private void showSosDialog() {
        new AlertDialog.Builder(this)
                .setTitle("🆘 Immediate Emergency Helplines")
                .setMessage("If you are feeling overwhelmed or in crisis, immediate confidential support is available 24/7:\n\n"
                        + "• Tele-MANAS (Govt. of India): 14416 (Toll-Free)\n"
                        + "• KIRAN Mental Health: 1800-599-0019 (Toll-Free)\n"
                        + "• Vandrevala Foundation: +91 9999 666 555 (24/7 Free)")
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
