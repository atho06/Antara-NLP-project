# 📱 Antara Flutter Mobile App & FastAPI Backend Guide

Welcome to the **Antara Native Mobile Application**! Antara has been upgraded from a web interface to a **100% Native Flutter Mobile Application** powered by a high-performance **Python FastAPI REST API**.

---

## 🏗️ Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │        📱 Antara Flutter Mobile        │
                      │               (Android APK)            │
                      └───────────────────┬────────────────────┘
                                          │  REST API (JSON)
                                          ▼
                      ┌────────────────────────────────────────┐
                      │       🧠 Python FastAPI Backend        │
                      │             (api_server.py)            │
                      └───────┬───────────────┬────────────────┘
                              │               │
                              ▼               ▼
                      ┌───────────────┐ ┌──────────────────────┐
                      │  NLP Engine   │ │   SQLite Database    │
                      │(VADER/RoBERTa)│ │     (antara.db)      │
                      └───────────────┘ └──────────────────────┘
```

1. **Frontend (`flutter_app/`)**:
   - Native Flutter screens: Splash, Login, Register, Dashboard, Bubble Chat with Countdown Timer, Summary, Settings, and Past Reflections.
   - Compiles into a real, standalone **Android APK (`app-debug.apk`)**.
2. **Backend (`api_server.py`)**:
   - Python FastAPI server hosting your NLP sentiment models, crisis detection, and SQLite database.

---

## ⚡ Step 1: Start the Python Backend

Run the FastAPI server on your laptop:

```bash
python api_server.py
```
*(Or `uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload`)*

- The API is live at `http://localhost:8000`
- Interactive API documentation (Swagger) is at: `http://localhost:8000/docs`

---

## 📲 Step 2: Build the Flutter APK

You and your teammate have **3 options** to build the APK:

### Option A: GitHub Cloud Build (Recommended — No Flutter or Android Studio needed!) 🎉
1. Push your changes to GitHub on `main`.
2. Open your GitHub repository in your browser: `https://github.com/atho06/Antara-NLP-project`
3. Click on the **Actions** tab at the top.
4. On the left sidebar, click **Build Antara Flutter APK**.
5. Click **Run workflow** -> **Run workflow**.
6. Wait ~2-3 minutes for the build to finish.
7. Click the completed run, and under **Artifacts**, download **`Antara-Flutter-APK`**.
8. Unzip to get **`app-debug.apk`**!

---

### Option B: Local Build via Flutter CLI (For your teammate)
If your teammate has Flutter installed on their computer:
```bash
cd flutter_app
flutter pub get
flutter build apk --debug
```
The APK will be generated at:
`flutter_app/build/app/outputs/flutter-apk/app-debug.apk`

---

### Option C: Run Directly on Phone / Emulator
To run and test the app with live reload:
```bash
cd flutter_app
flutter run
```

---

## 🌐 Step 3: Connecting the Phone to Your Backend

The Flutter app needs to reach your FastAPI backend. In `flutter_app/lib/config/api_config.dart` (or directly from the **⚙️ Settings icon** on the app's login screen):

- **Android Emulator**: Uses `http://10.0.2.2:8000` (works out of the box).
- **Physical Phone on same Wi-Fi**:
  1. Find your laptop IP: Run `ipconfig` on Windows (e.g. `192.168.1.15`).
  2. Set URL: `http://192.168.1.15:8000`
- **Cloud Hosted Backend**:
  1. Deploy `api_server.py` to Render, Railway, or Fly.io for free.
  2. Set URL: `https://your-backend.onrender.com`

---

## 📋 What Features are Included in the Flutter App?

- 🌸 **Splash & Welcome Screen**: Branded Antara lotus logo and automatic saved-login restore.
- 🔐 **Authentication & Registration**: Clean form validation, password hiding, and instant account creation.
- ⏱️ **Timer-Based Sessions**: 5, 10, 15, 20 min or Open Reflection with a real-time countdown progress bar.
- 💬 **Native Chat UI**: Smooth message bubbles, emotion analysis, and "Feeling Overwhelmed" check-ins.
- 📊 **Reflection Summary**: Takeaways, dominant emotional tone, and supportive affirmations.
- ⚙️ **Settings & Verification Suite**: Interactive OTP verification badges for Email, Phone, and Trusted Contact, plus password changing.
- 📖 **Reflection History**: List of all past sessions saved in the SQLite database.
- 🆘 **Emergency SOS**: Immediate mental health hotlines (Tele-MANAS, KIRAN, Vandrevala) and trusted contact alert dispatch.
