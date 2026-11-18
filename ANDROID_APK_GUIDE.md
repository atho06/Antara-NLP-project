# 📱 Antara Android APK Build & Setup Guide

This guide explains how to build and test the **Antara Mobile App (APK)** from this repository.

---

## 🏗️ Architecture Overview
Antara is built with a **Python Streamlit/FastAPI backend** wrapped in a native **Android WebView container** (`android/app/src/main/java/com/antara/app/MainActivity.java`).

---

## ⚡ Step 1: Set Your Server URL

Before building the APK, specify where the Android app should connect. Open `android/app/src/main/java/com/antara/app/MainActivity.java` and edit line 36:

```java
String serverUrl = "https://YOUR-ANTARA-APP-URL";
```

### Options for the URL:
1. **Free Cloud Deployment (Recommended)**:
   - Deploy this GitHub repo to [Streamlit Community Cloud](https://share.streamlit.io/) (100% free, 2-minute setup).
   - Enter your URL: `https://your-app-name.streamlit.app`
2. **Free Tunnel (Instant Testing without Cloud Deployment)**:
   - Run Streamlit on your laptop: `streamlit run app.py`
   - In another terminal, run `npx localtunnel --port 8501` or `ngrok http 8501`.
   - Use the HTTPS URL generated (e.g., `https://antara-demo.loca.lt`).
3. **Local Wi-Fi Testing (Phone & Laptop on same Wi-Fi)**:
   - Find your laptop's local IP (e.g. `192.168.1.15`).
   - Run: `streamlit run app.py --server.address 0.0.0.0 --server.port 8501`
   - Set URL: `http://192.168.1.15:8501` (Cleartext traffic is enabled in `AndroidManifest.xml`).
4. **Android Studio Emulator**:
   - Set URL: `http://10.0.2.2:8501` (Points to host laptop localhost).

---

## 🛠️ Step 2: Build the APK

### Option A: Using GitHub Actions (No Android Studio Required! 🎉)
1. Push your changes with the updated server URL to GitHub.
2. In your GitHub repository, click on the **Actions** tab.
3. Click on the **Build Antara APK** workflow on the left.
4. Click **Run workflow** -> **Run workflow**.
5. Once completed (~2 minutes), click the finished run and download the `Antara-APK` artifact (`app-debug.apk`) directly to your phone!

### Option B: Using Android Studio
1. Open **Android Studio**.
2. Click **File > Open** and select the `android/` folder of this project.
3. Wait for Gradle sync to complete.
4. Click **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
5. The generated APK will be located at:
   `android/app/build/outputs/apk/debug/app-debug.apk`

### Option C: Using Command Line (Terminal)
```bash
cd android
./gradlew assembleDebug
```
(On Windows: `gradlew.bat assembleDebug`)

---

## 📲 Step 3: Install & Run on Phone
1. Transfer `app-debug.apk` to your Android phone via WhatsApp, Google Drive, or USB.
2. Tap the APK to install (enable *"Install from Unknown Sources"* if prompted).
3. Open **Antara** 🌷 and enjoy your personal wellness companion!
