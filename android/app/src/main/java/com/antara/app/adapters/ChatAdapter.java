package com.antara.app.adapters;

import android.graphics.Color;
import android.text.method.LinkMovementMethod;
import android.text.util.Linkify;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.antara.app.R;
import com.antara.app.models.ChatMessage;

import java.util.List;

public class ChatAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private static final int TYPE_BOT = 1;
    private static final int TYPE_USER = 2;

    private List<ChatMessage> messages;

    public ChatAdapter(List<ChatMessage> messages) {
        this.messages = messages;
    }

    @Override
    public int getItemViewType(int position) {
        return messages.get(position).isUser() ? TYPE_USER : TYPE_BOT;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        if (viewType == TYPE_USER) {
            View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_chat_user, parent, false);
            return new UserViewHolder(view);
        } else {
            View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_chat_bot, parent, false);
            return new BotViewHolder(view);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        ChatMessage message = messages.get(position);
        if (holder instanceof UserViewHolder) {
            ((UserViewHolder) holder).tvMessage.setText(message.getText());
        } else if (holder instanceof BotViewHolder) {
            BotViewHolder bvh = (BotViewHolder) holder;
            bvh.tvMessage.setText(message.getText());
            if (message.isCrisis()) {
                bvh.tvMessage.setTextColor(Color.parseColor("#9B1C1C"));
                bvh.tvMessage.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16.5f);
                bvh.tvMessage.setBackgroundResource(R.drawable.bg_crisis_card);
                bvh.tvMessage.setLineSpacing(8f, 1.0f);
                Linkify.addLinks(bvh.tvMessage, Linkify.PHONE_NUMBERS);
                bvh.tvMessage.setMovementMethod(LinkMovementMethod.getInstance());
            } else {
                bvh.tvMessage.setTextColor(ContextCompat.getColor(holder.itemView.getContext(), R.color.bot_bubble_text));
                bvh.tvMessage.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15f);
                bvh.tvMessage.setBackgroundResource(R.drawable.bg_bot_bubble);
                bvh.tvMessage.setLineSpacing(3f, 1.0f);
            }
        }
    }

    @Override
    public int getItemCount() {
        return messages.size();
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
