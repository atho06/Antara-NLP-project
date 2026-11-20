package com.antara.app;

import android.app.Application;

import com.antara.app.utils.ThemeHelper;

public class AntaraApp extends Application {

    @Override
    public void onCreate() {
        super.onCreate();
        ThemeHelper.applyTheme(this);
    }
}
