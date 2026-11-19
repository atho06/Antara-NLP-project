import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/user_model.dart';

class ApiService {
  // Login
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.loginUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'user': UserModel.fromJson(data['user'])};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Login failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Could not connect to server. Check connection.'};
    }
  }

  // Register
  static Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
    String? phone,
    String? trustedContactName,
    String? trustedContactPhone,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.registerUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'full_name': fullName,
          'phone': phone ?? '',
          'trusted_contact_name': trustedContactName ?? '',
          'trusted_contact_phone': trustedContactPhone ?? '',
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'user': UserModel.fromJson(data['user'])};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Registration failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Could not connect to server. Check connection.'};
    }
  }

  // Send OTP
  static Future<Map<String, dynamic>> sendOtp({
    required String patientId,
    required String targetType,
    required String contactValue,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.sendOtpUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'patient_id': patientId,
          'target_type': targetType,
          'contact_value': contactValue,
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'otp': data['otp_code'], 'message': data['message']};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to send OTP'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Verify OTP
  static Future<Map<String, dynamic>> verifyOtp({
    required String patientId,
    required String targetType,
    required String otpCode,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.verifyOtpUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'patient_id': patientId,
          'target_type': targetType,
          'otp_code': otpCode,
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {
          'success': true,
          'user': data['user'] != null ? UserModel.fromJson(data['user']) : null,
          'message': data['message'],
        };
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Invalid code'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Update Profile
  static Future<Map<String, dynamic>> updateProfile({
    required String patientId,
    required String fullName,
    String? phone,
    String? trustedContactName,
    String? trustedContactPhone,
  }) async {
    try {
      final response = await http.put(
        Uri.parse(ApiConfig.profileUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'patient_id': patientId,
          'full_name': fullName,
          'phone': phone ?? '',
          'trusted_contact_name': trustedContactName ?? '',
          'trusted_contact_phone': trustedContactPhone ?? '',
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'user': UserModel.fromJson(data['user'])};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Update failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Change Password
  static Future<Map<String, dynamic>> changePassword({
    required String patientId,
    required String currentPassword,
    required String newPassword,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.changePasswordUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'patient_id': patientId,
          'current_password': currentPassword,
          'new_password': newPassword,
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message']};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to change password'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Start Session
  static Future<Map<String, dynamic>> startSession({
    required String patientId,
    required int durationMinutes,
    String category = 'daily_routine',
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.startSessionUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'patient_id': patientId,
          'duration_minutes': durationMinutes,
          'category': category,
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {
          'success': true,
          'session_id': data['session_id'],
          'initial_message': data['initial_message'],
          'first_question': data['first_question'],
          'target_seconds': data['target_seconds'],
        };
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to start session'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Send Message
  static Future<Map<String, dynamic>> sendMessage({
    required String sessionId,
    required String patientId,
    required String message,
    int elapsedSeconds = 0,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.sendMessageUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'patient_id': patientId,
          'message': message,
          'elapsed_seconds': elapsedSeconds,
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {
          'success': true,
          'status': data['status'],
          'reply': data['reply'],
          'next_question': data['next_question'],
          'is_crisis': data['is_crisis'] ?? false,
          'is_time_up': data['is_time_up'] ?? false,
          'allow_continuation': data['allow_continuation'] ?? false,
          'remaining_seconds': data['remaining_seconds'] ?? 0,
        };
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to send message'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // End Session
  static Future<Map<String, dynamic>> endSession({
    required String sessionId,
    required String patientId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.endSessionUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'patient_id': patientId,
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'summary': data['session_summary']};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to end session'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Get Session History
  static Future<Map<String, dynamic>> getHistory(String patientId) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.historyUrl}?patient_id=$patientId'),
        headers: {'Content-Type': 'application/json'},
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'sessions': data['sessions'] ?? []};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to load history'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Trigger Emergency SOS
  static Future<Map<String, dynamic>> triggerSos(String patientId, {String? note}) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.sosUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'patient_id': patientId,
          'current_message': note ?? 'Manual SOS from Antara mobile app',
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to trigger SOS'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error'};
    }
  }
}
