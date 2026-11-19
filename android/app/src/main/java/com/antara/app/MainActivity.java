package com.antara.app;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.SessionManager;

import java.util.Calendar;

public class MainActivity extends AppCompatActivity {

    private TextView tvGreetingTime, tvUserName;
    private Button btnSos, btnStartSession;
    private Spinner spnDuration, spnCategory;
    private LinearLayout navHome, navHistory, navSettings;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        sessionManager = new SessionManager(this);

        tvGreetingTime = findViewById(R.id.tv_greeting_time);
        tvUserName = findViewById(R.id.tv_user_name);
        btnSos = findViewById(R.id.btn_sos_header);
        btnStartSession = findViewById(R.id.btn_start_session);
        spnDuration = findViewById(R.id.spn_duration);
        spnCategory = findViewById(R.id.spn_category);
        navHome = findViewById(R.id.nav_home);
        navHistory = findViewById(R.id.nav_history);
        navSettings = findViewById(R.id.nav_settings);

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

        // Emergency SOS
        btnSos.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showSosDialog();
            }
        });

        // Bottom Navigation
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
                        + "• Vandrevala Foundation: +91 9999 666 555\n"
                        + "• Emergency Medical: 112")
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
