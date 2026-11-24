package com.antara.app.utils;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.graphics.Color;
import android.graphics.Typeface;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.core.content.ContextCompat;

import com.antara.app.R;
import com.antara.app.data.AntaraDatabaseHelper;

import java.util.List;

public class EvaluatorDashboardHelper {

    private static int easterEggTapCount = 0;
    private static long lastEasterEggTapTime = 0;

    /**
     * Handles the 5-tap developer easter egg logic.
     * Tapping 5 times within 2.5 seconds triggers the Evaluator Dashboard.
     */
    public static void onVersionTapped(Activity activity, AntaraDatabaseHelper dbHelper) {
        long currentTime = System.currentTimeMillis();
        if (currentTime - lastEasterEggTapTime > 2500) {
            easterEggTapCount = 1;
        } else {
            easterEggTapCount++;
        }
        lastEasterEggTapTime = currentTime;

        if (easterEggTapCount == 3) {
            Toast.makeText(activity, "2 more taps to open Evaluator Dashboard...", Toast.LENGTH_SHORT).show();
        } else if (easterEggTapCount == 4) {
            Toast.makeText(activity, "1 more tap to open Evaluator Dashboard...", Toast.LENGTH_SHORT).show();
        } else if (easterEggTapCount >= 5) {
            easterEggTapCount = 0;
            Toast.makeText(activity, "🔓 Evaluator Dashboard Unlocked!", Toast.LENGTH_SHORT).show();
            showDashboardDialog(activity, dbHelper);
        }
    }

    /**
     * Displays the Evaluator & Teacher Metrics Dialog.
     */
    public static void showDashboardDialog(final Activity activity, final AntaraDatabaseHelper dbHelper) {
        if (activity == null || activity.isFinishing()) return;

        int totalUsers = dbHelper.getTotalUserCount();
        int totalSessions = dbHelper.getTotalSessionsCount();
        List<AntaraDatabaseHelper.AdminUserSummary> users = dbHelper.getAllUsersSummary();

        AlertDialog.Builder builder = new AlertDialog.Builder(activity);
        builder.setTitle("🎓 Evaluator & Teacher Dashboard");

        ScrollView scrollView = new ScrollView(activity);
        LinearLayout container = new LinearLayout(activity);
        container.setOrientation(LinearLayout.VERTICAL);
        int pad = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 18, activity.getResources().getDisplayMetrics());
        container.setPadding(pad, pad / 2, pad, pad / 2);

        // Header Description
        TextView tvSub = new TextView(activity);
        tvSub.setText("Project Analytics & Multi-User Verification\n(Visible only to project developers)");
        tvSub.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
        tvSub.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
        container.addView(tvSub);

        // KPI Banner (Users + Sessions)
        LinearLayout kpiRow = new LinearLayout(activity);
        kpiRow.setOrientation(LinearLayout.HORIZONTAL);
        kpiRow.setPadding(0, pad / 2, 0, pad / 2);

        // Box 1: Users
        LinearLayout boxUsers = new LinearLayout(activity);
        boxUsers.setOrientation(LinearLayout.VERTICAL);
        boxUsers.setBackgroundResource(R.drawable.bg_option_button);
        boxUsers.setPadding(pad, pad / 2, pad, pad / 2);
        LinearLayout.LayoutParams lpBox1 = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lpBox1.setMargins(0, 0, pad / 3, 0);
        boxUsers.setLayoutParams(lpBox1);

        TextView tvUsersLabel = new TextView(activity);
        tvUsersLabel.setText("👥 Registered Users");
        tvUsersLabel.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
        tvUsersLabel.setTextSize(TypedValue.COMPLEX_UNIT_SP, 11);
        TextView tvUsersVal = new TextView(activity);
        tvUsersVal.setText(String.valueOf(totalUsers));
        tvUsersVal.setTextColor(ContextCompat.getColor(activity, R.color.primary));
        tvUsersVal.setTextSize(TypedValue.COMPLEX_UNIT_SP, 22);
        tvUsersVal.setTypeface(null, Typeface.BOLD);
        boxUsers.addView(tvUsersLabel);
        boxUsers.addView(tvUsersVal);
        kpiRow.addView(boxUsers);

        // Box 2: Sessions
        LinearLayout boxSessions = new LinearLayout(activity);
        boxSessions.setOrientation(LinearLayout.VERTICAL);
        boxSessions.setBackgroundResource(R.drawable.bg_option_button);
        boxSessions.setPadding(pad, pad / 2, pad, pad / 2);
        LinearLayout.LayoutParams lpBox2 = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lpBox2.setMargins(pad / 3, 0, 0, 0);
        boxSessions.setLayoutParams(lpBox2);

        TextView tvSessLabel = new TextView(activity);
        tvSessLabel.setText("🧘 Total Reflections");
        tvSessLabel.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
        tvSessLabel.setTextSize(TypedValue.COMPLEX_UNIT_SP, 11);
        TextView tvSessVal = new TextView(activity);
        tvSessVal.setText(String.valueOf(totalSessions));
        tvSessVal.setTextColor(Color.parseColor("#00B894"));
        tvSessVal.setTextSize(TypedValue.COMPLEX_UNIT_SP, 22);
        tvSessVal.setTypeface(null, Typeface.BOLD);
        boxSessions.addView(tvSessLabel);
        boxSessions.addView(tvSessVal);
        kpiRow.addView(boxSessions);

        container.addView(kpiRow);

        // User Directory Header
        TextView tvDirHeader = new TextView(activity);
        tvDirHeader.setText("📋 Registered User Directory:");
        tvDirHeader.setTextColor(ContextCompat.getColor(activity, R.color.text_primary));
        tvDirHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
        tvDirHeader.setTypeface(null, Typeface.BOLD);
        tvDirHeader.setPadding(0, pad / 2, 0, pad / 3);
        container.addView(tvDirHeader);

        // User Directory List
        if (users.isEmpty()) {
            TextView tvEmpty = new TextView(activity);
            tvEmpty.setText("No users registered yet.");
            tvEmpty.setTextColor(ContextCompat.getColor(activity, R.color.text_muted));
            container.addView(tvEmpty);
        } else {
            for (int i = 0; i < users.size(); i++) {
                AntaraDatabaseHelper.AdminUserSummary u = users.get(i);
                LinearLayout uCard = new LinearLayout(activity);
                uCard.setOrientation(LinearLayout.VERTICAL);
                uCard.setBackgroundResource(R.drawable.bg_option_button);
                uCard.setPadding(pad / 2, pad / 3, pad / 2, pad / 3);
                LinearLayout.LayoutParams lpCard = new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
                lpCard.setMargins(0, 0, 0, pad / 3);
                uCard.setLayoutParams(lpCard);

                TextView tvName = new TextView(activity);
                tvName.setText((i + 1) + ". " + u.name + " (" + u.email + ")");
                tvName.setTextColor(ContextCompat.getColor(activity, R.color.text_primary));
                tvName.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
                tvName.setTypeface(null, Typeface.BOLD);
                uCard.addView(tvName);

                TextView tvStats = new TextView(activity);
                tvStats.setText("   • " + u.sessionCount + " reflections logged  •  🔥 " + u.streak + "-day streak  •  Joined: " + u.createdAt);
                tvStats.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
                tvStats.setTextSize(TypedValue.COMPLEX_UNIT_SP, 11);
                uCard.addView(tvStats);

                container.addView(uCard);
            }
        }

        scrollView.addView(container);
        builder.setView(scrollView);

        // Add Demo User button for live viva demonstration
        builder.setPositiveButton("➕ Add Demo User", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                int nextNum = dbHelper.getTotalUserCount() + 1;
                String demoName = "Student Peer " + nextNum;
                String demoEmail = "peer" + nextNum + "@college.edu";
                dbHelper.createDemoUser(demoName, demoEmail);
                Toast.makeText(activity, "Added " + demoName + "! 👥", Toast.LENGTH_SHORT).show();
                // Re-open updated dialog
                showDashboardDialog(activity, dbHelper);
            }
        });

        builder.setNegativeButton("Close", null);
        builder.show();
    }
}
