package com.antara.app.utils;

import android.app.Activity;
import android.content.Context;
import android.content.DialogInterface;
import android.graphics.Typeface;
import android.util.TypedValue;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.core.content.ContextCompat;
import androidx.core.content.res.ResourcesCompat;

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
            Toast.makeText(activity, "2 more taps to open evaluator dashboard", Toast.LENGTH_SHORT).show();
        } else if (easterEggTapCount == 4) {
            Toast.makeText(activity, "1 more tap to open evaluator dashboard", Toast.LENGTH_SHORT).show();
        } else if (easterEggTapCount >= 5) {
            easterEggTapCount = 0;
            Toast.makeText(activity, "Evaluator dashboard unlocked", Toast.LENGTH_SHORT).show();
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

        Typeface nunitoRegular = ResourcesCompat.getFont(activity, R.font.nunito_regular);
        Typeface nunitoSemiBold = ResourcesCompat.getFont(activity, R.font.nunito_semibold);
        Typeface nunitoBold = ResourcesCompat.getFont(activity, R.font.nunito_bold);

        int pad20 = dp(activity, 20);
        int pad16 = dp(activity, 16);
        int pad12 = dp(activity, 12);
        int pad8 = dp(activity, 8);
        int pad6 = dp(activity, 6);

        AlertDialog.Builder builder = new AlertDialog.Builder(activity);
        builder.setTitle("Evaluator dashboard");

        ScrollView scrollView = new ScrollView(activity);
        scrollView.setVerticalScrollBarEnabled(false);

        LinearLayout container = new LinearLayout(activity);
        container.setOrientation(LinearLayout.VERTICAL);
        container.setPadding(pad20, pad8, pad20, pad12);

        // Header Description
        TextView tvSub = new TextView(activity);
        tvSub.setText("Project summary and local multi-user verification. Accounts and reflections are stored on this device.");
        tvSub.setTypeface(nunitoRegular);
        tvSub.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
        tvSub.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
        container.addView(tvSub);

        // Summary Row (Users + Sessions)
        LinearLayout summaryRow = new LinearLayout(activity);
        summaryRow.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams lpSummaryRow = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lpSummaryRow.topMargin = pad16;
        summaryRow.setLayoutParams(lpSummaryRow);

        // Box 1: Users
        LinearLayout boxUsers = new LinearLayout(activity);
        boxUsers.setOrientation(LinearLayout.VERTICAL);
        boxUsers.setBackgroundResource(R.drawable.bg_panel_sage);
        boxUsers.setPadding(pad16, pad12, pad16, pad12);
        LinearLayout.LayoutParams lpBox1 = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lpBox1.setMarginEnd(pad6);
        boxUsers.setLayoutParams(lpBox1);

        TextView tvUsersLabel = new TextView(activity);
        tvUsersLabel.setText("Registered users");
        tvUsersLabel.setTypeface(nunitoRegular);
        tvUsersLabel.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
        tvUsersLabel.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);

        TextView tvUsersVal = new TextView(activity);
        tvUsersVal.setText(String.valueOf(totalUsers));
        tvUsersVal.setTypeface(nunitoBold);
        tvUsersVal.setTextColor(ContextCompat.getColor(activity, R.color.primary));
        tvUsersVal.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20);
        tvUsersVal.setPadding(0, dp(activity, 2), 0, 0);

        boxUsers.addView(tvUsersLabel);
        boxUsers.addView(tvUsersVal);
        summaryRow.addView(boxUsers);

        // Box 2: Sessions
        LinearLayout boxSessions = new LinearLayout(activity);
        boxSessions.setOrientation(LinearLayout.VERTICAL);
        boxSessions.setBackgroundResource(R.drawable.bg_panel_sage);
        boxSessions.setPadding(pad16, pad12, pad16, pad12);
        LinearLayout.LayoutParams lpBox2 = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lpBox2.setMarginStart(pad6);
        boxSessions.setLayoutParams(lpBox2);

        TextView tvSessLabel = new TextView(activity);
        tvSessLabel.setText("Saved reflections");
        tvSessLabel.setTypeface(nunitoRegular);
        tvSessLabel.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
        tvSessLabel.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);

        TextView tvSessVal = new TextView(activity);
        tvSessVal.setText(String.valueOf(totalSessions));
        tvSessVal.setTypeface(nunitoBold);
        tvSessVal.setTextColor(ContextCompat.getColor(activity, R.color.primary));
        tvSessVal.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20);
        tvSessVal.setPadding(0, dp(activity, 2), 0, 0);

        boxSessions.addView(tvSessLabel);
        boxSessions.addView(tvSessVal);
        summaryRow.addView(boxSessions);

        container.addView(summaryRow);

        // User Directory Header
        TextView tvDirHeader = new TextView(activity);
        tvDirHeader.setText("User directory");
        tvDirHeader.setTypeface(nunitoBold);
        tvDirHeader.setTextColor(ContextCompat.getColor(activity, R.color.text_primary));
        tvDirHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
        LinearLayout.LayoutParams lpDirHeader = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lpDirHeader.topMargin = pad20;
        lpDirHeader.bottomMargin = pad8;
        tvDirHeader.setLayoutParams(lpDirHeader);
        container.addView(tvDirHeader);

        // User Directory List
        if (users.isEmpty()) {
            TextView tvEmpty = new TextView(activity);
            tvEmpty.setText("No users registered yet.");
            tvEmpty.setTypeface(nunitoRegular);
            tvEmpty.setTextColor(ContextCompat.getColor(activity, R.color.text_muted));
            tvEmpty.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
            container.addView(tvEmpty);
        } else {
            for (int i = 0; i < users.size(); i++) {
                AntaraDatabaseHelper.AdminUserSummary u = users.get(i);
                LinearLayout uCard = new LinearLayout(activity);
                uCard.setOrientation(LinearLayout.VERTICAL);
                uCard.setBackgroundResource(R.drawable.bg_card);
                uCard.setPadding(pad16, pad12, pad16, pad12);
                LinearLayout.LayoutParams lpCard = new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
                lpCard.bottomMargin = pad8;
                uCard.setLayoutParams(lpCard);

                TextView tvName = new TextView(activity);
                tvName.setText((i + 1) + ". " + u.name + " (" + u.email + ")");
                tvName.setTypeface(nunitoSemiBold);
                tvName.setTextColor(ContextCompat.getColor(activity, R.color.text_primary));
                tvName.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
                uCard.addView(tvName);

                TextView tvStats = new TextView(activity);
                tvStats.setText(u.sessionCount + " reflections  •  " + u.streak + "-day streak  •  Joined " + u.createdAt);
                tvStats.setTypeface(nunitoRegular);
                tvStats.setTextColor(ContextCompat.getColor(activity, R.color.text_secondary));
                tvStats.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
                tvStats.setPadding(0, dp(activity, 4), 0, 0);
                uCard.addView(tvStats);

                container.addView(uCard);
            }
        }

        scrollView.addView(container);
        builder.setView(scrollView);

        // Add Demo User button for live viva demonstration
        builder.setPositiveButton("Add demo user", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                int nextNum = dbHelper.getTotalUserCount() + 1;
                String demoName = "Student Peer " + nextNum;
                String demoEmail = "peer" + nextNum + "@college.edu";
                dbHelper.createDemoUser(demoName, demoEmail);
                Toast.makeText(activity, "Added " + demoName, Toast.LENGTH_SHORT).show();
                // Re-open updated dialog
                showDashboardDialog(activity, dbHelper);
            }
        });

        builder.setNegativeButton("Close", null);
        builder.show();
    }

    private static int dp(Context context, int value) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, value, context.getResources().getDisplayMetrics());
    }
}
