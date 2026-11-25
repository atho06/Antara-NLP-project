package com.antara.app;

import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.util.TypedValue;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;
import com.antara.app.utils.ThemeHelper;

import java.util.Random;

public class SettingsActivity extends AppCompatActivity {

    private TextView tvAvatar, tvName, tvEmail, tvPhone;
    private TextView tvContactName, tvContactPhone, tvContactEmail;
    private Button btnEditProfile, btnEditContact;
    private TextView tvCurrentTheme;
    private Button btnChangeTheme;
    private TextView tvCurrentCycle;
    private Button btnChangeCycle;
    private TextView btnVerifyEmail, btnVerifyPhone, btnVerifyContact;
    private Button btnLogout;

    private SessionManager sessionManager;
    private AntaraDatabaseHelper dbHelper;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        sessionManager = new SessionManager(this);
        dbHelper = new AntaraDatabaseHelper(this);

        ImageButton btnBack = findViewById(R.id.btn_settings_back);
        if (btnBack != null) {
            btnBack.setOnClickListener(v -> finish());
        }

        tvAvatar = findViewById(R.id.tv_settings_avatar);
        tvName = findViewById(R.id.tv_settings_name);
        tvEmail = findViewById(R.id.tv_settings_email);
        tvPhone = findViewById(R.id.tv_settings_phone);

        tvContactName = findViewById(R.id.tv_contact_name);
        tvContactPhone = findViewById(R.id.tv_contact_phone);
        tvContactEmail = findViewById(R.id.tv_contact_email);

        btnEditProfile = findViewById(R.id.btn_edit_profile);
        btnEditContact = findViewById(R.id.btn_edit_contact);

        tvCurrentTheme = findViewById(R.id.tv_current_theme);
        btnChangeTheme = findViewById(R.id.btn_change_theme);
        View rowTheme = findViewById(R.id.row_settings_theme);

        int currentMode = ThemeHelper.getSavedTheme(this);
        if (tvCurrentTheme != null) {
            tvCurrentTheme.setText(ThemeHelper.getThemeName(currentMode));
        }

        View.OnClickListener themeClickListener = new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showThemeSelectionDialog();
            }
        };

        if (btnChangeTheme != null) btnChangeTheme.setOnClickListener(themeClickListener);
        if (rowTheme != null) rowTheme.setOnClickListener(themeClickListener);

        tvCurrentCycle = findViewById(R.id.tv_current_cycle);
        btnChangeCycle = findViewById(R.id.btn_change_cycle);
        View rowCycle = findViewById(R.id.row_settings_cycle);

        View.OnClickListener cycleClickListener = new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showCycleSelectionDialog();
            }
        };

        if (btnChangeCycle != null) btnChangeCycle.setOnClickListener(cycleClickListener);
        if (rowCycle != null) rowCycle.setOnClickListener(cycleClickListener);

        btnVerifyEmail = findViewById(R.id.btn_verify_email);
        btnVerifyPhone = findViewById(R.id.btn_verify_phone);
        btnVerifyContact = findViewById(R.id.btn_verify_contact);
        btnLogout = findViewById(R.id.btn_settings_logout);

        TextView tvSettingsVersion = findViewById(R.id.tv_settings_version);
        if (tvSettingsVersion != null) {
            tvSettingsVersion.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    com.antara.app.utils.EvaluatorDashboardHelper.onVersionTapped(SettingsActivity.this, dbHelper);
                }
            });
        }

        loadProfileData();

        // 1. Edit personal details with local confirmation code
        btnEditProfile.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                promptEmailVerificationForAction("personal details", new Runnable() {
                    @Override
                    public void run() {
                        showEditProfileDialog();
                    }
                });
            }
        });

        // 2. Edit support contact with local confirmation code
        btnEditContact.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                promptEmailVerificationForAction("support contact", new Runnable() {
                    @Override
                    public void run() {
                        showEditEmergencyContactDialog();
                    }
                });
            }
        });

        // Local verification checks
        btnVerifyEmail.setOnClickListener(v -> showOtpDialog("Email", AntaraDatabaseHelper.COL_USER_EMAIL_VERIFIED, btnVerifyEmail));
        btnVerifyPhone.setOnClickListener(v -> showOtpDialog("Phone", AntaraDatabaseHelper.COL_USER_PHONE_VERIFIED, btnVerifyPhone));
        btnVerifyContact.setOnClickListener(v -> showOtpDialog("Support contact", AntaraDatabaseHelper.COL_USER_CONTACT_VERIFIED, btnVerifyContact));

        // 3. Navigation to Feedback and About
        View rowFeedback = findViewById(R.id.row_settings_feedback);
        View rowAbout = findViewById(R.id.row_settings_about);

        if (rowFeedback != null) {
            rowFeedback.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(new Intent(SettingsActivity.this, FeedbackActivity.class));
                }
            });
        }

        if (rowAbout != null) {
            rowAbout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(new Intent(SettingsActivity.this, AboutActivity.class));
                }
            });
        }

        // Sign out
        btnLogout.setOnClickListener(v -> {
            sessionManager.logout();
            Intent intent = new Intent(SettingsActivity.this, LoginActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        });
    }

    private void loadProfileData() {
        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);

        if (profile != null) {
            tvName.setText(profile.fullName);
            tvEmail.setText(profile.email);
            tvPhone.setText(!profile.phone.isEmpty() ? profile.phone : "No phone number added");

            if (!profile.fullName.isEmpty()) {
                tvAvatar.setText(String.valueOf(profile.fullName.charAt(0)).toUpperCase());
            }

            if (!profile.trustedContactName.isEmpty()) {
                tvContactName.setText("Name: " + profile.trustedContactName);
                tvContactPhone.setText(!profile.trustedContactPhone.isEmpty() ? "Phone: " + profile.trustedContactPhone : "Phone: Not specified");
                tvContactEmail.setText(!profile.trustedContactEmail.isEmpty() ? "Email: " + profile.trustedContactEmail : "Email: Not specified");
            } else {
                tvContactName.setText("Name: Not added yet");
                tvContactPhone.setText("Phone: Not added");
                tvContactEmail.setText("Email: Not added");
            }

            if (tvCurrentCycle != null) {
                tvCurrentCycle.setText(formatCyclePhase(profile.menstrualPhase));
            }
        }
    }

    private String formatCyclePhase(String phaseKey) {
        if (phaseKey == null || phaseKey.equals("not_tracking") || phaseKey.isEmpty()) {
            return "Not tracking";
        } else if (phaseKey.equals("menstrual_period")) {
            return "Menstrual phase (rest and care)";
        } else if (phaseKey.equals("follicular")) {
            return "Follicular phase (rising energy)";
        } else if (phaseKey.equals("ovulation")) {
            return "Ovulation phase (steady energy)";
        } else if (phaseKey.equals("luteal_pms")) {
            return "Luteal / PMS phase (extra gentleness)";
        }
        return phaseKey.replace('_', ' ');
    }

    private void promptEmailVerificationForAction(final String actionTarget, final Runnable onVerifiedSuccess) {
        final String userEmail = sessionManager.getUserEmail();
        final String generatedOtp = String.valueOf(100000 + new Random().nextInt(900000));

        LinearLayout container = new LinearLayout(this);
        container.setOrientation(LinearLayout.VERTICAL);
        int pad = dpToPx(20);
        container.setPadding(pad, dpToPx(8), pad, 0);

        final EditText input = new EditText(this);
        input.setHint("Enter 6-digit code");
        input.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        input.setSingleLine(true);
        container.addView(input);

        new AlertDialog.Builder(this)
                .setTitle("Confirm before editing")
                .setMessage("Enter the local confirmation code below to update your " + actionTarget
                        + ". This is an offline demo check (no email is sent to " + userEmail + ").\n\nCode: " + generatedOtp)
                .setView(container)
                .setPositiveButton("Continue", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String entered = input.getText().toString().trim();
                        if (entered.equals(generatedOtp)) {
                            Toast.makeText(SettingsActivity.this, "Code confirmed.", Toast.LENGTH_SHORT).show();
                            onVerifiedSuccess.run();
                        } else {
                            Toast.makeText(SettingsActivity.this, "That code didn't match. Please try again.", Toast.LENGTH_SHORT).show();
                        }
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showEditProfileDialog() {
        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
        if (profile == null) return;

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Edit personal details");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int pad = dpToPx(20);
        layout.setPadding(pad, pad / 2, pad, pad / 2);

        final EditText etName = new EditText(this);
        etName.setHint("Full name");
        etName.setText(profile.fullName);
        layout.addView(etName);

        final EditText etEmail = new EditText(this);
        etEmail.setHint("Email address");
        etEmail.setText(profile.email);
        etEmail.setInputType(android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        layout.addView(etEmail);

        final EditText etPhone = new EditText(this);
        etPhone.setHint("Phone number");
        etPhone.setText(profile.phone);
        etPhone.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
        layout.addView(etPhone);

        builder.setView(layout);

        builder.setPositiveButton("Save changes", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String newName = etName.getText().toString().trim();
                String newEmail = etEmail.getText().toString().trim();
                String newPhone = etPhone.getText().toString().trim();

                if (newName.isEmpty() || newEmail.isEmpty()) {
                    Toast.makeText(SettingsActivity.this, "Name and email are required.", Toast.LENGTH_SHORT).show();
                    return;
                }

                dbHelper.updateUserProfile(userId, newName, newEmail, newPhone);
                sessionManager.updateUserInfo(newName, newEmail);
                loadProfileData();
                Toast.makeText(SettingsActivity.this, "Personal details updated.", Toast.LENGTH_SHORT).show();
            }
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void showEditEmergencyContactDialog() {
        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Edit support contact");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int pad = dpToPx(20);
        layout.setPadding(pad, pad / 2, pad, pad / 2);

        final EditText etName = new EditText(this);
        etName.setHint("Contact name (e.g. Mom, partner, friend)");
        etName.setText(profile != null ? profile.trustedContactName : "");
        layout.addView(etName);

        final EditText etPhone = new EditText(this);
        etPhone.setHint("Phone number (e.g. +91 9876543210)");
        etPhone.setText(profile != null ? profile.trustedContactPhone : "");
        etPhone.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
        layout.addView(etPhone);

        final EditText etEmail = new EditText(this);
        etEmail.setHint("Contact email (e.g. contact@example.com)");
        etEmail.setText(profile != null ? profile.trustedContactEmail : "");
        etEmail.setInputType(android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        layout.addView(etEmail);

        builder.setView(layout);

        builder.setPositiveButton("Save contact", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String newName = etName.getText().toString().trim();
                String newPhone = etPhone.getText().toString().trim();
                String newEmail = etEmail.getText().toString().trim();

                if (newPhone.isEmpty() && newName.isEmpty()) {
                    Toast.makeText(SettingsActivity.this, "Please enter at least a name or phone number.", Toast.LENGTH_SHORT).show();
                    return;
                }

                if (newName.isEmpty()) newName = "Trusted contact";

                dbHelper.updateEmergencyContact(userId, newName, newPhone, newEmail);
                loadProfileData();
                Toast.makeText(SettingsActivity.this, "Support contact updated.", Toast.LENGTH_SHORT).show();
            }
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void showOtpDialog(String target, String dbField, TextView badgeView) {
        String generatedOtp = String.valueOf(100000 + new Random().nextInt(900000));

        LinearLayout container = new LinearLayout(this);
        container.setOrientation(LinearLayout.VERTICAL);
        int pad = dpToPx(20);
        container.setPadding(pad, dpToPx(8), pad, 0);

        final EditText input = new EditText(this);
        input.setHint("Enter 6-digit code");
        input.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        input.setSingleLine(true);
        container.addView(input);

        new AlertDialog.Builder(this)
                .setTitle("Verify " + target.toLowerCase())
                .setMessage("Enter this local demo code to mark your " + target.toLowerCase()
                        + " as verified on this device. No email or SMS is sent.\n\nCode: " + generatedOtp)
                .setView(container)
                .setPositiveButton("Verify", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String entered = input.getText().toString().trim();
                        if (entered.equals(generatedOtp)) {
                            dbHelper.setVerification(sessionManager.getUserId(), dbField, true);
                            badgeView.setText("Verified");
                            badgeView.setTextColor(ContextCompat.getColor(SettingsActivity.this, R.color.success));
                            badgeView.setEnabled(false);
                            Toast.makeText(SettingsActivity.this, target + " marked as verified.", Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(SettingsActivity.this, "That code didn't match.", Toast.LENGTH_SHORT).show();
                        }
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showThemeSelectionDialog() {
        final String[] themeOptions = new String[]{
                ThemeHelper.getThemeName(ThemeHelper.THEME_LIGHT),
                ThemeHelper.getThemeName(ThemeHelper.THEME_DARK),
                ThemeHelper.getThemeName(ThemeHelper.THEME_SYSTEM),
                ThemeHelper.getThemeName(ThemeHelper.THEME_AMBER),
                ThemeHelper.getThemeName(ThemeHelper.THEME_MINT)
        };

        int current = ThemeHelper.getSavedTheme(this);
        if (current < 0 || current >= themeOptions.length) current = ThemeHelper.THEME_SYSTEM;
        final int[] selected = new int[]{current};

        new AlertDialog.Builder(this)
                .setTitle("Choose app theme")
                .setSingleChoiceItems(themeOptions, current, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        selected[0] = which;
                    }
                })
                .setPositiveButton("Apply", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        ThemeHelper.setTheme(SettingsActivity.this, selected[0]);
                        if (tvCurrentTheme != null) {
                            tvCurrentTheme.setText(ThemeHelper.getThemeName(selected[0]));
                        }
                        Toast.makeText(SettingsActivity.this, "Theme updated.", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showCycleSelectionDialog() {
        final String[] cycleLabels = new String[]{
                "Not tracking",
                "Menstrual phase (days 1-5: rest and care)",
                "Follicular phase (days 6-13: rising energy)",
                "Ovulation phase (days 14-17: steady energy)",
                "Luteal / PMS phase (days 18-28: extra gentleness)"
        };

        final String[] cycleKeys = new String[]{
                "not_tracking",
                "menstrual_period",
                "follicular",
                "ovulation",
                "luteal_pms"
        };

        long userId = sessionManager.getUserId();
        AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
        int currentIdx = 0;
        if (profile != null && profile.menstrualPhase != null) {
            for (int i = 0; i < cycleKeys.length; i++) {
                if (cycleKeys[i].equalsIgnoreCase(profile.menstrualPhase)) {
                    currentIdx = i;
                    break;
                }
            }
        }

        final int[] selected = new int[]{currentIdx};

        new AlertDialog.Builder(this)
                .setTitle("Current cycle phase")
                .setSingleChoiceItems(cycleLabels, currentIdx, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        selected[0] = which;
                    }
                })
                .setPositiveButton("Save", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String chosenKey = cycleKeys[selected[0]];
                        dbHelper.updateMenstrualPhase(userId, chosenKey);
                        if (tvCurrentCycle != null) {
                            tvCurrentCycle.setText(formatCyclePhase(chosenKey));
                        }
                        Toast.makeText(SettingsActivity.this, "Cycle phase updated.", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private int dpToPx(int dp) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, dp, getResources().getDisplayMetrics());
    }
}
