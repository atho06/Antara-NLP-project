package com.antara.app;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.antara.app.data.AntaraDatabaseHelper;
import com.antara.app.data.SessionManager;

public class RegisterActivity extends AppCompatActivity {

    private EditText etName, etEmail, etPassword, etPhone, etContactName, etContactPhone, etContactEmail;
    private Button btnSubmit;
    private TextView tvLogin;
    private AntaraDatabaseHelper dbHelper;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        dbHelper = new AntaraDatabaseHelper(this);
        sessionManager = new SessionManager(this);

        etName = findViewById(R.id.et_reg_name);
        etEmail = findViewById(R.id.et_reg_email);
        etPassword = findViewById(R.id.et_reg_password);
        etPhone = findViewById(R.id.et_reg_phone);
        etContactName = findViewById(R.id.et_reg_contact_name);
        etContactPhone = findViewById(R.id.et_reg_contact_phone);
        etContactEmail = findViewById(R.id.et_reg_contact_email);
        btnSubmit = findViewById(R.id.btn_reg_submit);
        tvLogin = findViewById(R.id.tv_reg_login);

        btnSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                handleRegister();
            }
        });

        tvLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    private void handleRegister() {
        String name = etName.getText().toString().trim();
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString().trim();
        String phone = etPhone.getText().toString().trim();
        String contactName = etContactName.getText().toString().trim();
        String contactPhone = etContactPhone.getText().toString().trim();
        String contactEmail = etContactEmail.getText().toString().trim();

        if (name.isEmpty() || email.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Please fill in your name, email, and password", Toast.LENGTH_SHORT).show();
            return;
        }

        if (password.length() < 6) {
            Toast.makeText(this, "Password must be at least 6 characters", Toast.LENGTH_SHORT).show();
            return;
        }

        long userId = dbHelper.registerUser(name, email, password, phone, contactName, contactPhone, contactEmail);
        if (userId != -1) {
            sessionManager.setLogin(userId, name, email);
            Toast.makeText(this, "Account created successfully! 🌸", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(RegisterActivity.this, MainActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        } else {
            Toast.makeText(this, "An account with this email already exists", Toast.LENGTH_SHORT).show();
        }
    }
}
