package com.antara.app.adapters;

import android.content.Context;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.R;
import com.antara.app.models.SessionRecord;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

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
        Context ctx = holder.itemView.getContext();

        holder.tvCategory.setText(s.getDurationMinutes() + " Min Reflection (" + s.getCategory().replace('_', ' ') + ")");
        holder.tvDate.setText(s.getCompletedAt());
        holder.tvSummary.setText(s.getSummary());

        // Populate Emotion Bubbles
        holder.layoutBubbles.removeAllViews();
        Set<String> uniqueEmotions = new LinkedHashSet<>();

        // Add dominant emotion first
        if (s.getDominantEmotion() != null && !s.getDominantEmotion().trim().isEmpty()) {
            uniqueEmotions.add(s.getDominantEmotion().trim().toLowerCase(Locale.ROOT));
        }

        // Add all logged emotions from session
        String log = s.getEmotionsLog();
        if (log != null && !log.trim().isEmpty()) {
            String[] parts = log.split(",");
            for (String p : parts) {
                String clean = p.trim().toLowerCase(Locale.ROOT);
                if (!clean.isEmpty()) uniqueEmotions.add(clean);
            }
        }

        if (uniqueEmotions.isEmpty()) {
            uniqueEmotions.add("calm_grounded");
        }

        for (String em : uniqueEmotions) {
            TextView bubble = new TextView(ctx);
            bubble.setText(formatEmotionBubbleText(em));
            bubble.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
            bubble.setTextColor(ContextCompat.getColor(ctx, R.color.text_primary));
            bubble.setBackgroundResource(R.drawable.bg_emotion_bubble);
            bubble.setPadding(24, 10, 24, 10);

            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
            );
            lp.setMargins(0, 0, 16, 0);
            bubble.setLayoutParams(lp);

            holder.layoutBubbles.addView(bubble);
        }
    }

    private String formatEmotionBubbleText(String emotion) {
        if (emotion.contains("joy") || emotion.contains("humor") || emotion.contains("laugh")) {
            return "✨ Joyful / Light";
        } else if (emotion.contains("sad") || emotion.contains("low") || emotion.contains("exhaust")) {
            return "🌧️ Tender / Sadness";
        } else if (emotion.contains("stress") || emotion.contains("anxi")) {
            return "⚡ Stress & Overwhelm";
        } else if (emotion.contains("anger") || emotion.contains("frustrat")) {
            return "🔥 Frustration";
        } else if (emotion.contains("reflective")) {
            return "💜 Reflective";
        } else {
            return "🌿 Calm Grounded";
        }
    }

    @Override
    public int getItemCount() {
        return records.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvCategory, tvDate, tvSummary;
        LinearLayout layoutBubbles;

        ViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCategory = itemView.findViewById(R.id.tv_history_category);
            tvDate = itemView.findViewById(R.id.tv_history_date);
            tvSummary = itemView.findViewById(R.id.tv_history_summary);
            layoutBubbles = itemView.findViewById(R.id.layout_history_bubbles);
        }
    }
}
