package com.antara.app;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;

public class LoginActivity extends AppCompatActivity {

    private EditText etEmail, etPassword;
    private Button btnSubmit;
    private Button tvRegister;
    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        etEmail = findViewById(R.id.et_login_email);
        etPassword = findViewById(R.id.et_login_password);
        btnSubmit = findViewById(R.id.btn_login_submit);
        tvRegister = findViewById(R.id.tv_login_register);

        btnSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                handleLogin();
            }
        });

        tvRegister.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LoginActivity.this, RegisterActivity.class));
            }
        });
    }

    private void handleLogin() {
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        if (email.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Please enter your email and password.", Toast.LENGTH_SHORT).show();
            return;
        }

        long userId = dbHelper.authenticateUser(email, password);
        if (userId != -1) {
            AntaraDatabaseHelper.UserProfile profile = dbHelper.getUserProfile(userId);
            String userName = (profile != null && profile.fullName != null && !profile.fullName.trim().isEmpty())
                    ? profile.fullName.trim()
                    : "Friend";
            sessionManager.setLogin(userId, userName, email);
            Toast.makeText(this, "Welcome back, " + userName + ".", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(LoginActivity.this, MainActivity.class);
            startActivity(intent);
            finish();
        } else {
            Toast.makeText(this, "Email or password did not match.", Toast.LENGTH_SHORT).show();
        }
    }
}
