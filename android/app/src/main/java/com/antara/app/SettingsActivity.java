package com.antara.app;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;

import java.util.Random;

public class SettingsActivity extends AppCompatActivity {

    private TextView tvAvatar, tvName, tvEmail;
    private TextView btnVerifyEmail, btnVerifyPhone, btnVerifyContact;
    private Button btnLogout;

    private SessionManager sessionManager;
    private AntaraDatabaseHelper dbHelper;

    private boolean isEmailVerified = false;
    private boolean isPhoneVerified = false;
    private boolean isContactVerified = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        sessionManager = new SessionManager(this);
        dbHelper = new AntaraDatabaseHelper(this);

        tvAvatar = findViewById(R.id.tv_settings_avatar);
        tvName = findViewById(R.id.tv_settings_name);
        tvEmail = findViewById(R.id.tv_settings_email);

        btnVerifyEmail = findViewById(R.id.btn_verify_email);
        btnVerifyPhone = findViewById(R.id.btn_verify_phone);
        btnVerifyContact = findViewById(R.id.btn_verify_contact);
        btnLogout = findViewById(R.id.btn_settings_logout);

        String name = sessionManager.getUserName();
        String email = sessionManager.getUserEmail();

        tvName.setText(name);
        tvEmail.setText(email);
        if (!name.isEmpty()) {
            tvAvatar.setText(String.valueOf(name.charAt(0)).toUpperCase());
        }

        btnVerifyEmail.setOnClickListener(v -> showOtpDialog("Email", AntaraDatabaseHelper.COL_USER_EMAIL_VERIFIED, btnVerifyEmail));
        btnVerifyPhone.setOnClickListener(v -> showOtpDialog("Phone", AntaraDatabaseHelper.COL_USER_PHONE_VERIFIED, btnVerifyPhone));
        btnVerifyContact.setOnClickListener(v -> showOtpDialog("Emergency Contact", AntaraDatabaseHelper.COL_USER_CONTACT_VERIFIED, btnVerifyContact));

        btnLogout.setOnClickListener(v -> {
            sessionManager.logout();
            Intent intent = new Intent(SettingsActivity.this, LoginActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        });
    }

    private void showOtpDialog(String target, String dbField, TextView badgeView) {
        String generatedOtp = String.valueOf(100000 + new Random().nextInt(900000));

        final EditText input = new EditText(this);
        input.setHint("Enter 6-digit code");
        input.setSingleLine(true);

        new AlertDialog.Builder(this)
                .setTitle("🔐 Verify " + target)
                .setMessage("A verification code was generated for your " + target + ":\n\nDemo OTP Code: " + generatedOtp)
                .setView(input)
                .setPositiveButton("Verify", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String entered = input.getText().toString().trim();
                        if (entered.equals(generatedOtp)) {
                            dbHelper.setVerification(sessionManager.getUserId(), dbField, true);
                            badgeView.setText("Verified ✅");
                            badgeView.setTextColor(Color.parseColor("#00B894"));
                            badgeView.setEnabled(false);
                            Toast.makeText(SettingsActivity.this, target + " verified successfully! ✅", Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(SettingsActivity.this, "Invalid verification code", Toast.LENGTH_SHORT).show();
                        }
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }
}
