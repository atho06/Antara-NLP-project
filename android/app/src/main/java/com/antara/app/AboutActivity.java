package com.antara.app;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.utils.EvaluatorDashboardHelper;

public class AboutActivity extends AppCompatActivity {

    private AntaraDatabaseHelper dbHelper;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_about);

        dbHelper = new AntaraDatabaseHelper(this);

        TextView btnBack = findViewById(R.id.btn_about_back);
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        TextView tvAboutVersion = findViewById(R.id.tv_about_version);
        if (tvAboutVersion != null) {
            tvAboutVersion.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    EvaluatorDashboardHelper.onVersionTapped(AboutActivity.this, dbHelper);
                }
            });
        }
    }
}
