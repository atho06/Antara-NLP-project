package com.antara.app;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.util.Locale;

public class SessionSummaryActivity extends AppCompatActivity {

    private TextView tvDuration, tvAnswers, tvEmotion, tvSummaryText;
    private Button btnHome;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_summary);

        tvDuration = findViewById(R.id.tv_sum_duration);
        tvAnswers = findViewById(R.id.tv_sum_answers);
        tvEmotion = findViewById(R.id.tv_sum_emotion);
        tvSummaryText = findViewById(R.id.tv_sum_text);
        btnHome = findViewById(R.id.btn_sum_home);

        int duration = getIntent().getIntExtra("duration_minutes", 5);
        int answers = getIntent().getIntExtra("reflections_count", 3);
        String emotion = getIntent().getStringExtra("dominant_emotion");
        if (emotion == null) emotion = "calm_grounded";
        String summary = getIntent().getStringExtra("summary_text");
        if (summary == null) summary = "Thank you for taking this quiet moment for yourself.";

        tvDuration.setText(duration + " min");
        tvAnswers.setText(answers == 1 ? "1 reflection" : answers + " reflections");
        String rawEmotion = emotion.toLowerCase(Locale.ROOT);
        String displayEmotion;
        if (rawEmotion.contains("joy") || rawEmotion.contains("humor") || rawEmotion.contains("laugh")) {
            displayEmotion = "Joyful and uplifted";
        } else if (rawEmotion.contains("sad") || rawEmotion.contains("low")) {
            displayEmotion = "Gently reflective";
        } else if (rawEmotion.contains("stress") || rawEmotion.contains("anxi")) {
            displayEmotion = "Working through stress";
        } else if (rawEmotion.contains("anger") || rawEmotion.contains("frustrat")) {
            displayEmotion = "Releasing tension";
        } else {
            displayEmotion = "Calm and grounded";
        }
        tvEmotion.setText(displayEmotion);
        tvSummaryText.setText(summary);

        btnHome.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(SessionSummaryActivity.this, MainActivity.class);
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                startActivity(intent);
                finish();
            }
        });
    }
}
