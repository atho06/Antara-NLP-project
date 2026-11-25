package com.antara.app;

import android.Manifest;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;

import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import com.antara.app.data.DraftSessionManager;
import com.antara.app.data.SessionManager;

public class NotificationReceiver extends BroadcastReceiver {

    public static final String CHANNEL_ID = "antara_checkin_channel";
    public static final int NOTIFICATION_ID = 1001;

    @Override
    public void onReceive(Context context, Intent intent) {
        // Only notify if there is an active draft that was never finished
        SessionManager sessionManager = new SessionManager(context);
        long userId = sessionManager.getUserId();
        if (!DraftSessionManager.hasActiveDraft(context, userId)) {
            return;
        }

        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Antara Reflection Reminders",
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("Gentle reminders when you pause a reflection");
            nm.createNotificationChannel(channel);
        }

        Intent openIntent = new Intent(context, MainActivity.class);
        openIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(
                context, 0, openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0)
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_launcher)
                .setContentTitle("Antara")
                .setContentText("Your reflection is waiting whenever you feel ready. No rush.")
                .setStyle(new NotificationCompat.BigTextStyle()
                        .bigText("You paused your reflection earlier. Whenever you have a quiet moment, you can pick up where you left off or leave it for another time."))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true)
                .setContentIntent(pi);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                return;
            }
        }

        nm.notify(NOTIFICATION_ID, builder.build());
    }
}
