package com.antara.app;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

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
    private TextView tvEmpty;
    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_history);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        rvHistory = findViewById(R.id.rv_history);
        tvEmpty = findViewById(R.id.tv_history_empty);

        rvHistory.setLayoutManager(new LinearLayoutManager(this));

        long userId = sessionManager.getUserId();
        List<SessionRecord> records = dbHelper.getUserSessions(userId);

        if (records.isEmpty()) {
            tvEmpty.setVisibility(View.VISIBLE);
            rvHistory.setVisibility(View.GONE);
        } else {
            tvEmpty.setVisibility(View.GONE);
            rvHistory.setVisibility(View.VISIBLE);
            HistoryAdapter adapter = new HistoryAdapter(records);
            rvHistory.setAdapter(adapter);
        }
    }
}
