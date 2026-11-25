package com.antara.app;

import android.os.Bundle;
import android.view.View;
import android.widget.ImageButton;
import android.widget.LinearLayout;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.adapters.HistoryAdapter;
import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;
import com.antara.app.models.SessionRecord;

import java.util.List;

public class HistoryActivity extends AppCompatActivity {

    private RecyclerView rvHistory;
    private LinearLayout layoutEmpty;
    private ImageButton btnBack;
    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_history);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        btnBack = findViewById(R.id.btn_history_back);
        rvHistory = findViewById(R.id.rv_history);
        layoutEmpty = findViewById(R.id.layout_history_empty);

        btnBack.setOnClickListener(v -> finish());

        rvHistory.setLayoutManager(new LinearLayoutManager(this));

        long userId = sessionManager.getUserId();
        List<SessionRecord> records = dbHelper.getUserSessions(userId);

        if (records.isEmpty()) {
            layoutEmpty.setVisibility(View.VISIBLE);
            rvHistory.setVisibility(View.GONE);
        } else {
            layoutEmpty.setVisibility(View.GONE);
            rvHistory.setVisibility(View.VISIBLE);
            HistoryAdapter adapter = new HistoryAdapter(records);
            rvHistory.setAdapter(adapter);
        }
    }
}
