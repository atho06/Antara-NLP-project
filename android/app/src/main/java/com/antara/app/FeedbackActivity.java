package com.antara.app;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RatingBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;

public class FeedbackActivity extends AppCompatActivity {

    private TextView btnBack, tvRatingDescription;
    private Spinner spnCategory;
    private RatingBar rbRating;
    private EditText etContent;
    private Button btnSubmit;

    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_feedback);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        btnBack = findViewById(R.id.btn_feedback_back);
        tvRatingDescription = findViewById(R.id.tv_rating_description);
        spnCategory = findViewById(R.id.spn_feedback_category);
        rbRating = findViewById(R.id.rb_feedback_rating);
        etContent = findViewById(R.id.et_feedback_content);
        btnSubmit = findViewById(R.id.btn_feedback_submit);

        // Back button
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        // Category dropdown
        String[] categories = new String[]{
                "General Experience & Thoughts",
                "Conversational Questions & Flow",
                "Feature Request / Suggestion",
                "Safety & Emergency Support",
                "Bug or Technical Glitch"
        };
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, categories);
        spnCategory.setAdapter(adapter);

        // Rating change updates description
        rbRating.setOnRatingBarChangeListener(new RatingBar.OnRatingBarChangeListener() {
            @Override
            public void onRatingChanged(RatingBar ratingBar, float rating, boolean fromUser) {
                int r = (int) rating;
                switch (r) {
                    case 1:
                        tvRatingDescription.setText("⭐ Needs Significant Improvement");
                        break;
                    case 2:
                        tvRatingDescription.setText("⭐⭐ Somewhat Helpful");
                        break;
                    case 3:
                        tvRatingDescription.setText("⭐⭐⭐ Good & Meaningful");
                        break;
                    case 4:
                        tvRatingDescription.setText("⭐⭐⭐⭐ Very Helpful");
                        break;
                    case 5:
                    default:
                        tvRatingDescription.setText("⭐⭐⭐⭐⭐ Extremely Supportive 🌸");
                        break;
                }
            }
        });

        // Submit Button
        btnSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String feedbackText = etContent.getText().toString().trim();
                if (feedbackText.isEmpty()) {
                    Toast.makeText(FeedbackActivity.this, "Please tell us your thoughts or suggestions", Toast.LENGTH_SHORT).show();
                    return;
                }

                String category = spnCategory.getSelectedItem().toString();
                int rating = (int) rbRating.getRating();
                long userId = sessionManager.getUserId();

                dbHelper.saveFeedback(userId, category, rating, feedbackText);

                new AlertDialog.Builder(FeedbackActivity.this)
                        .setTitle("Thank You 🌸")
                        .setMessage("Your thoughts and suggestions have been received with care. Every piece of feedback helps us make Antara a gentler, more supportive space for you.")
                        .setPositiveButton("Done", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                finish();
                            }
                        })
                        .setCancelable(false)
                        .show();
            }
        });
    }
}
