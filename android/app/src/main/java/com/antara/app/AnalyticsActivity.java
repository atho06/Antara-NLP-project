package com.antara.app;

import android.os.Bundle;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;
import com.antara.app.models.SessionRecord;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class AnalyticsActivity extends AppCompatActivity {

    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;
    private List<SessionRecord> allRecords;

    private TextView btnFilterAll, btnFilterWeek, btnFilterToday;
    private ImageButton btnBack;
    private TextView tvMinutes, tvStreak;
    private TextView tvPctCalm, tvPctJoy, tvPctSad, tvPctStress;
    private ProgressBar pbCalm, pbJoy, pbSad, pbStress;
    private TextView tvCycleInsightText, tvEmptyNote;

    private int currentFilter = 0; // 0 = all, 1 = week, 2 = today

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_analytics);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        btnFilterAll = findViewById(R.id.btn_filter_all);
        btnFilterWeek = findViewById(R.id.btn_filter_week);
        btnFilterToday = findViewById(R.id.btn_filter_today);
        btnBack = findViewById(R.id.btn_analytics_back);

        tvMinutes = findViewById(R.id.tv_stat_minutes);
        tvStreak = findViewById(R.id.tv_stat_streak);

        tvPctCalm = findViewById(R.id.tv_pct_calm);
        tvPctJoy = findViewById(R.id.tv_pct_joy);
        tvPctSad = findViewById(R.id.tv_pct_sad);
        tvPctStress = findViewById(R.id.tv_pct_stress);

        pbCalm = findViewById(R.id.pb_calm);
        pbJoy = findViewById(R.id.pb_joy);
        pbSad = findViewById(R.id.pb_sad);
        pbStress = findViewById(R.id.pb_stress);

        tvCycleInsightText = findViewById(R.id.tv_cycle_insight_text);
        tvEmptyNote = findViewById(R.id.tv_analytics_empty_note);

        long userId = sessionManager.getUserId();
        allRecords = dbHelper.getUserSessions(userId);

        int streak = dbHelper.getUserStreak(userId);
        tvStreak.setText(streak + (streak == 1 ? " day" : " days"));

        // Menstrual cycle context
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
        if (profile != null && profile.menstrualPhase != null && !profile.menstrualPhase.equals("not_tracking")) {
            String rawPhase = profile.menstrualPhase.replace('_', ' ').trim();
            String formattedPhase = rawPhase.isEmpty()
                    ? rawPhase
                    : rawPhase.substring(0, 1).toUpperCase(Locale.ROOT) + rawPhase.substring(1).toLowerCase(Locale.ROOT);
            tvCycleInsightText.setText("Currently noted: " + formattedPhase
                    + ".\nEnergy and mood can naturally ebb and flow through different phases. Give yourself room for rest and a gentler pace when you need it.");
        } else {
            tvCycleInsightText.setText("If you'd like, you can optionally note your cycle phase in Settings to tailor your reflection context.");
        }

        btnFilterAll.setOnClickListener(v -> setFilter(0));
        btnFilterWeek.setOnClickListener(v -> setFilter(1));
        btnFilterToday.setOnClickListener(v -> setFilter(2));

        btnBack.setOnClickListener(v -> finish());

        setFilter(0);
    }

    private void setFilter(int filter) {
        currentFilter = filter;

        styleFilterChip(btnFilterAll, filter == 0);
        styleFilterChip(btnFilterWeek, filter == 1);
        styleFilterChip(btnFilterToday, filter == 2);

        List<SessionRecord> filtered = new ArrayList<>();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
        String todayStr = sdf.format(new Date());

        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_YEAR, -7);
        Date weekAgo = cal.getTime();

        for (SessionRecord r : allRecords) {
            if (filter == 0) {
                filtered.add(r);
            } else if (filter == 1) { // 7 days
                try {
                    Date rDate = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).parse(r.getCompletedAt().substring(0, 10));
                    if (rDate != null && !rDate.before(weekAgo)) {
                        filtered.add(r);
                    }
                } catch (Exception e) {
                    filtered.add(r);
                }
            } else if (filter == 2) { // today
                if (r.getCompletedAt() != null && r.getCompletedAt().startsWith(todayStr)) {
                    filtered.add(r);
                }
            }
        }

        updateAnalyticsUI(filtered);
    }

    private void styleFilterChip(TextView chip, boolean selected) {
        chip.setBackgroundResource(selected ? R.drawable.bg_option_selected : R.drawable.bg_option_button);
        chip.setTextColor(ContextCompat.getColor(this, selected ? R.color.primary_dark : R.color.text_secondary));
    }

    private void updateAnalyticsUI(List<SessionRecord> list) {
        int totalMinutes = 0;
        int countCalm = 0, countJoy = 0, countSad = 0, countStress = 0;
        int totalEmotions = 0;

        for (SessionRecord r : list) {
            totalMinutes += r.getDurationMinutes();

            String em = r.getDominantEmotion() != null ? r.getDominantEmotion().toLowerCase(Locale.ROOT) : "";
            String log = r.getEmotionsLog() != null ? r.getEmotionsLog().toLowerCase(Locale.ROOT) : "";
            String combined = em + " " + log;

            if (combined.contains("calm")) { countCalm++; totalEmotions++; }
            if (combined.contains("joy") || combined.contains("humor") || combined.contains("laugh")) { countJoy++; totalEmotions++; }
            if (combined.contains("sad") || combined.contains("low") || combined.contains("exhaust")) { countSad++; totalEmotions++; }
            if (combined.contains("stress") || combined.contains("anxi") || combined.contains("anger")) { countStress++; totalEmotions++; }
        }

        tvMinutes.setText(totalMinutes + " min");

        if (totalEmotions == 0) {
            tvEmptyNote.setVisibility(View.VISIBLE);
            tvPctCalm.setText("0%");
            tvPctJoy.setText("0%");
            tvPctSad.setText("0%");
            tvPctStress.setText("0%");

            pbCalm.setProgress(0);
            pbJoy.setProgress(0);
            pbSad.setProgress(0);
            pbStress.setProgress(0);
            return;
        }

        tvEmptyNote.setVisibility(View.GONE);

        int pctCalm = (countCalm * 100) / totalEmotions;
        int pctJoy = (countJoy * 100) / totalEmotions;
        int pctSad = (countSad * 100) / totalEmotions;
        int pctStress = (countStress * 100) / totalEmotions;

        tvPctCalm.setText(pctCalm + "%");
        tvPctJoy.setText(pctJoy + "%");
        tvPctSad.setText(pctSad + "%");
        tvPctStress.setText(pctStress + "%");

        pbCalm.setProgress(pctCalm);
        pbJoy.setProgress(pctJoy);
        pbSad.setProgress(pctSad);
        pbStress.setProgress(pctStress);
    }
}
