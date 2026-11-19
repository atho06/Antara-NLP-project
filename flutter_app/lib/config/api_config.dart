class ApiConfig {
  // Set your FastAPI server URL here:
  // - For Android Emulator: 'http://10.0.2.2:8000'
  // - For Physical Phone over Wi-Fi: 'http://YOUR_LAPTOP_IP:8000' (e.g. 'http://192.168.1.15:8000')
  // - For Cloud Deployed / Ngrok: 'https://your-domain.com'
  static String baseUrl = "http://10.0.2.2:8000";

  // Auth endpoints
  static String get registerUrl => '$baseUrl/api/auth/register';
  static String get loginUrl => '$baseUrl/api/auth/login';
  static String get sendOtpUrl => '$baseUrl/api/auth/send-otp';
  static String get verifyOtpUrl => '$baseUrl/api/auth/verify-otp';

  // Profile endpoints
  static String get profileUrl => '$baseUrl/api/user/profile';
  static String get changePasswordUrl => '$baseUrl/api/user/change-password';

  // Session endpoints
  static String get startSessionUrl => '$baseUrl/api/session/start';
  static String get sendMessageUrl => '$baseUrl/api/session/message';
  static String get endSessionUrl => '$baseUrl/api/session/end';
  static String get historyUrl => '$baseUrl/api/session/history';

  // Emergency SOS
  static String get sosUrl => '$baseUrl/api/emergency/sos';
  static String get healthUrl => '$baseUrl/api/health';
}
