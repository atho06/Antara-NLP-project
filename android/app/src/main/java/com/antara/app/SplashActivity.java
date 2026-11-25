package com.antara.app;

import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.animation.AccelerateDecelerateInterpolator;

import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.SessionManager;

public class SplashActivity extends AppCompatActivity {

    private final Handler handler = new Handler(Looper.getMainLooper());
    private Runnable navigateRunnable;
    private AnimatorSet breathAnimator;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        View motif = findViewById(R.id.splash_motif);
        if (motif != null) {
            ObjectAnimator scaleX = ObjectAnimator.ofFloat(motif, View.SCALE_X, 0.94f, 1.05f);
            scaleX.setDuration(1400);
            scaleX.setRepeatMode(ValueAnimator.REVERSE);
            scaleX.setRepeatCount(ValueAnimator.INFINITE);

            ObjectAnimator scaleY = ObjectAnimator.ofFloat(motif, View.SCALE_Y, 0.94f, 1.05f);
            scaleY.setDuration(1400);
            scaleY.setRepeatMode(ValueAnimator.REVERSE);
            scaleY.setRepeatCount(ValueAnimator.INFINITE);

            breathAnimator = new AnimatorSet();
            breathAnimator.setInterpolator(new AccelerateDecelerateInterpolator());
            breathAnimator.playTogether(scaleX, scaleY);
            breathAnimator.start();
        }

        navigateRunnable = new Runnable() {
            @Override
            public void run() {
                SessionManager sm = new SessionManager(SplashActivity.this);
                Intent intent;
                if (sm.isLoggedIn()) {
                    intent = new Intent(SplashActivity.this, MainActivity.class);
                } else {
                    intent = new Intent(SplashActivity.this, LoginActivity.class);
                }
                startActivity(intent);
                finish();
            }
        };
        handler.postDelayed(navigateRunnable, 1500);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (navigateRunnable != null) {
            handler.removeCallbacks(navigateRunnable);
        }
        if (breathAnimator != null) {
            breathAnimator.cancel();
        }
    }
}
