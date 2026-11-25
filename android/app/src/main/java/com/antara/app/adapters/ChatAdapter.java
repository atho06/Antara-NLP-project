package com.antara.app.adapters;

import android.content.Context;
import android.graphics.Typeface;
import android.text.method.LinkMovementMethod;
import android.text.util.Linkify;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.core.content.res.ResourcesCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.R;
import com.antara.app.models.ChatMessage;

import java.util.List;

public class ChatAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private static final int TYPE_HEADER = 0;
    private static final int TYPE_BOT = 1;
    private static final int TYPE_USER = 2;

    private final List<ChatMessage> messages;

    public ChatAdapter(List<ChatMessage> messages) {
        this.messages = messages;
    }

    @Override
    public int getItemViewType(int position) {
        if (position == 0) return TYPE_HEADER;
        return messages.get(position - 1).isUser() ? TYPE_USER : TYPE_BOT;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        if (viewType == TYPE_HEADER) {
            View view = inflater.inflate(R.layout.item_chat_header, parent, false);
            return new HeaderViewHolder(view);
        } else if (viewType == TYPE_USER) {
            View view = inflater.inflate(R.layout.item_chat_user, parent, false);
            return new UserViewHolder(view);
        } else {
            View view = inflater.inflate(R.layout.item_chat_bot, parent, false);
            return new BotViewHolder(view);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        if (holder instanceof HeaderViewHolder) {
            return;
        }
        ChatMessage message = messages.get(position - 1);
        Context ctx = holder.itemView.getContext();

        if (holder instanceof UserViewHolder) {
            ((UserViewHolder) holder).tvMessage.setText(message.getText());
        } else if (holder instanceof BotViewHolder) {
            BotViewHolder bvh = (BotViewHolder) holder;
            String text = message.getText() != null ? message.getText() : "";
            bvh.tvMessage.setText(text);

            Typeface regular = ResourcesCompat.getFont(ctx, R.font.nunito_regular);
            Typeface bold = ResourcesCompat.getFont(ctx, R.font.nunito_bold);

            if (message.isCrisis()) {
                bvh.tvMessage.setTextColor(ContextCompat.getColor(ctx, R.color.crisis_text));
                bvh.tvMessage.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15.5f);
                bvh.tvMessage.setTypeface(regular);
                bvh.tvMessage.setBackgroundResource(R.drawable.bg_crisis_card);
                bvh.tvMessage.setLineSpacing(6f, 1.0f);
                Linkify.addLinks(bvh.tvMessage, Linkify.PHONE_NUMBERS);
                bvh.tvMessage.setMovementMethod(LinkMovementMethod.getInstance());
            } else if (isStandaloneQuestion(text)) {
                // Highlighted sage prompt card, matching the Reflection reference
                bvh.tvMessage.setTextColor(ContextCompat.getColor(ctx, R.color.text_primary));
                bvh.tvMessage.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18f);
                bvh.tvMessage.setTypeface(bold);
                bvh.tvMessage.setBackgroundResource(R.drawable.bg_bot_question);
                bvh.tvMessage.setLineSpacing(4f, 1.0f);
                bvh.tvMessage.setMovementMethod(null);
            } else {
                bvh.tvMessage.setTextColor(ContextCompat.getColor(ctx, R.color.bot_bubble_text));
                bvh.tvMessage.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15f);
                bvh.tvMessage.setTypeface(regular);
                bvh.tvMessage.setBackgroundResource(R.drawable.bg_bot_bubble);
                bvh.tvMessage.setLineSpacing(4f, 1.0f);
                bvh.tvMessage.setMovementMethod(null);
            }
        }
    }

    private boolean isStandaloneQuestion(String text) {
        String trimmed = text.trim();
        return trimmed.endsWith("?") && trimmed.length() <= 140 && !trimmed.contains("\n");
    }

    @Override
    public int getItemCount() {
        return messages.size() + 1;
    }

    public int getLastAdapterPosition() {
        return messages.size();
    }

    public void notifyLastMessageInserted() {
        notifyItemInserted(messages.size());
    }

    public void notifyMessagesAppended(int count) {
        if (count <= 0) return;
        int startPos = (messages.size() - count) + 1;
        notifyItemRangeInserted(startPos, count);
    }

    static class HeaderViewHolder extends RecyclerView.ViewHolder {
        HeaderViewHolder(@NonNull View itemView) {
            super(itemView);
        }
    }

    static class UserViewHolder extends RecyclerView.ViewHolder {
        TextView tvMessage;
        UserViewHolder(@NonNull View itemView) {
            super(itemView);
            tvMessage = itemView.findViewById(R.id.tv_user_message);
        }
    }

    static class BotViewHolder extends RecyclerView.ViewHolder {
        TextView tvMessage;
        BotViewHolder(@NonNull View itemView) {
            super(itemView);
            tvMessage = itemView.findViewById(R.id.tv_bot_message);
        }
    }
}
