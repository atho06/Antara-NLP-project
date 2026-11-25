package com.antara.app;

import android.content.DialogInterface;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.RatingBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;

public class FeedbackActivity extends AppCompatActivity {

    private ImageButton btnBack;
    private TextView tvRatingDescription;
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
                "General experience",
                "Reflection prompts and flow",
                "Feature suggestion",
                "Safety and support options",
                "Bug or technical issue"
        };
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, R.layout.item_spinner_selected, categories);
        adapter.setDropDownViewResource(R.layout.item_spinner_dropdown);
        spnCategory.setAdapter(adapter);

        // Rating change updates description
        rbRating.setOnRatingBarChangeListener(new RatingBar.OnRatingBarChangeListener() {
            @Override
            public void onRatingChanged(RatingBar ratingBar, float rating, boolean fromUser) {
                int r = (int) rating;
                switch (r) {
                    case 1:
                        tvRatingDescription.setText("1 of 5 • Needs improvement");
                        break;
                    case 2:
                        tvRatingDescription.setText("2 of 5 • Somewhat helpful");
                        break;
                    case 3:
                        tvRatingDescription.setText("3 of 5 • Steady and helpful");
                        break;
                    case 4:
                        tvRatingDescription.setText("4 of 5 • Very helpful");
                        break;
                    case 5:
                    default:
                        tvRatingDescription.setText("5 of 5 • Very supportive");
                        break;
                }
            }
        });

        // Save button
        btnSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String feedbackText = etContent.getText().toString().trim();
                if (feedbackText.isEmpty()) {
                    Toast.makeText(FeedbackActivity.this, "Please add a short note before saving.", Toast.LENGTH_SHORT).show();
                    return;
                }

                String category = spnCategory.getSelectedItem().toString();
                int rating = (int) rbRating.getRating();
                long userId = sessionManager.getUserId();

                dbHelper.saveFeedback(userId, category, rating, feedbackText);

                new AlertDialog.Builder(FeedbackActivity.this)
                        .setTitle("Feedback saved")
                        .setMessage("Your note has been saved to this device's local database. It is not sent over the internet.")
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
