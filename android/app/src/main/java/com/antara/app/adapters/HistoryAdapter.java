package com.antara.app.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.R;
import com.antara.app.models.SessionRecord;

import java.util.List;
import java.util.Locale;

public class HistoryAdapter extends RecyclerView.Adapter<HistoryAdapter.ViewHolder> {

    private List<SessionRecord> records;

    public HistoryAdapter(List<SessionRecord> records) {
        this.records = records;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_history_card, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        SessionRecord s = records.get(position);
        holder.tvCategory.setText(s.getDurationMinutes() + " Min Reflection (" + s.getCategory().replace('_', ' ') + ")");
        holder.tvEmotion.setText(s.getDominantEmotion().replace('_', ' ').toUpperCase(Locale.ROOT));
        holder.tvDate.setText(s.getCompletedAt());
        holder.tvSummary.setText(s.getSummary());
    }

    @Override
    public int getItemCount() {
        return records.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvCategory, tvEmotion, tvDate, tvSummary;
        ViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCategory = itemView.findViewById(R.id.tv_history_category);
            tvEmotion = itemView.findViewById(R.id.tv_history_emotion);
            tvDate = itemView.findViewById(R.id.tv_history_date);
            tvSummary = itemView.findViewById(R.id.tv_history_summary);
        }
    }
}
