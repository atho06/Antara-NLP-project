package com.antara.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {

    private WebView webView;
    private SharedPreferences prefs;
    private static final String PREF_NAME = "antara_prefs";
    private static final String KEY_SERVER_URL = "server_url";
    
    // Default server URL pointing to your local Wi-Fi IP
    private static final String DEFAULT_URL = "http://172.29.9.185:8501";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        prefs = getSharedPreferences(PREF_NAME, MODE_PRIVATE);
        String currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL);

        // Root container
        FrameLayout rootLayout = new FrameLayout(this);
        rootLayout.setLayoutParams(new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        ));

        // WebView setup
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                if (request.isForMainFrame()) {
                    showServerConfigDialog("Could not connect to server.\nPlease check if the server is running on your laptop and verify the URL:");
                }
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                super.onReceivedError(view, errorCode, description, failingUrl);
                showServerConfigDialog("Could not connect to server (" + description + ").\nPlease verify your server URL:");
            }
        });

        webView.setLayoutParams(new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        ));
        rootLayout.addView(webView);

        // Small floating "⚙️ Server" button in the corner to change IP anytime
        Button settingsBtn = new Button(this);
        settingsBtn.setText("⚙️");
        settingsBtn.setTextSize(14);
        settingsBtn.setTextColor(Color.WHITE);
        settingsBtn.setBackgroundColor(Color.parseColor("#806C5CE7"));
        FrameLayout.LayoutParams btnParams = new FrameLayout.LayoutParams(
            110, 110, Gravity.BOTTOM | Gravity.END
        );
        btnParams.setMargins(0, 0, 30, 40);
        settingsBtn.setLayoutParams(btnParams);
        settingsBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showServerConfigDialog("Set Antara Server URL:");
            }
        });
        rootLayout.addView(settingsBtn);

        setContentView(rootLayout);

        // Load the configured URL
        loadServerUrl(currentUrl);
    }

    private void loadServerUrl(String url) {
        if (url == null || url.trim().isEmpty() || url.contains("YOUR-ANTARA-APP-URL")) {
            showServerConfigDialog("Please enter your Antara server URL to begin:");
            return;
        }
        webView.loadUrl(url.trim());
    }

    private void showServerConfigDialog(String promptMessage) {
        String currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL);

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Antara Server Connection 🌷");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(40, 20, 40, 10);

        TextView promptText = new TextView(this);
        promptText.setText(promptMessage);
        promptText.setPadding(0, 0, 0, 20);
        layout.addView(promptText);

        final EditText input = new EditText(this);
        input.setHint("http://192.168.x.x:8501 or https://...");
        input.setText(currentUrl);
        input.setSingleLine(true);
        layout.addView(input);

        TextView hintText = new TextView(this);
        hintText.setText("• Laptop Wi-Fi IP: http://172.29.9.185:8501\n• Free Tunnel (ngrok): https://xxx.ngrok.app\n• Cloud: https://xxx.streamlit.app");
        hintText.setTextSize(12);
        hintText.setTextColor(Color.GRAY);
        hintText.setPadding(0, 15, 0, 0);
        layout.addView(hintText);

        builder.setView(layout);

        builder.setPositiveButton("Connect", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String newUrl = input.getText().toString().trim();
                if (!newUrl.isEmpty()) {
                    prefs.edit().putString(KEY_SERVER_URL, newUrl).apply();
                    Toast.makeText(MainActivity.this, "Connecting to: " + newUrl, Toast.LENGTH_SHORT).show();
                    webView.loadUrl(newUrl);
                }
            }
        });

        builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.cancel();
            }
        });

        builder.show();
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
