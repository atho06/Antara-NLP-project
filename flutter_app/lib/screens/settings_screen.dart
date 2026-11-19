import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../theme/app_theme.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import 'login_screen.dart';

class SettingsScreen extends StatefulWidget {
  final UserModel user;
  final Function(UserModel) onUserUpdated;

  const SettingsScreen({
    Key? key,
    required this.user,
    required this.onUserUpdated,
  }) : super(key: key);

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late UserModel _user;

  @override
  void initState() {
    super.initState();
    _user = widget.user;
  }

  void _showOtpVerificationDialog(String targetType, String contactValue) async {
    // 1. Request OTP from API
    final sendRes = await ApiService.sendOtp(
      patientId: _user.patientId,
      targetType: targetType,
      contactValue: contactValue,
    );

    if (!mounted) return;

    if (!sendRes['success']) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(sendRes['error'] ?? 'Failed to send OTP')),
      );
      return;
    }

    final otpCode = sendRes['otp'];
    final otpController = TextEditingController();

    // 2. Show OTP input dialog with simulated code for convenience
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text('🔐 Verify ${targetType.replaceAll('_', ' ').capitalize()}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('A 6-digit code was sent to $contactValue:'),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'Demo OTP Code: $otpCode',
                style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: otpController,
              keyboardType: TextInputType.number,
              maxLength: 6,
              decoration: const InputDecoration(
                labelText: 'Enter 6-digit OTP',
                prefixIcon: Icon(Icons.pin),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final code = otpController.text.trim();
              if (code.length != 6) return;

              Navigator.pop(ctx);
              final verifyRes = await ApiService.verifyOtp(
                patientId: _user.patientId,
                targetType: targetType,
                otpCode: code,
              );

              if (!mounted) return;

              if (verifyRes['success'] && verifyRes['user'] != null) {
                final updated = verifyRes['user'] as UserModel;
                setState(() => _user = updated);
                widget.onUserUpdated(updated);

                final prefs = await SharedPreferences.getInstance();
                await prefs.setString('saved_user', jsonEncode(updated.toJson()));

                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('${targetType.replaceAll('_', ' ').capitalize()} verified successfully! ✅'),
                    backgroundColor: AppColors.success,
                  ),
                );
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(verifyRes['error'] ?? 'Verification failed'),
                    backgroundColor: AppColors.error,
                  ),
                );
              }
            },
            child: const Text('Verify'),
          ),
        ],
      ),
    );
  }

  void _showChangePasswordDialog() {
    final currPassController = TextEditingController();
    final newPassController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('🔑 Change Password'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: currPassController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Current Password'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: newPassController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'New Password (min 6 chars)'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              if (newPassController.text.length < 6) return;
              Navigator.pop(ctx);

              final res = await ApiService.changePassword(
                patientId: _user.patientId,
                currentPassword: currPassController.text,
                newPassword: newPassController.text,
              );

              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(res['success'] ? 'Password updated successfully! ✅' : res['error']),
                  backgroundColor: res['success'] ? AppColors.success : AppColors.error,
                ),
              );
            },
            child: const Text('Update'),
          ),
        ],
      ),
    );
  }

  Future<void> _handleLogout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('saved_user');

    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  Widget _buildVerificationBadge(bool isVerified, VoidCallback onVerify) {
    if (isVerified) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.green.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.green.shade300),
        ),
        child: const Text(
          'Verified ✅',
          style: TextStyle(color: AppColors.success, fontWeight: FontWeight.bold, fontSize: 12),
        ),
      );
    }
    return InkWell(
      onTap: onVerify,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.amber.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.amber.shade400),
        ),
        child: const Text(
          'Verify Now ⚠️',
          style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 12),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Profile Header Card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.04),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: AppColors.primary.withOpacity(0.15),
                  child: Text(
                    _user.fullName.isNotEmpty ? _user.fullName[0].toUpperCase() : 'A',
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.primary),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _user.fullName,
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        _user.email,
                        style: const TextStyle(fontSize: 14, color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Verification Status Section
          const Text('🔐 Verification Badges', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Column(
                children: [
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.email_outlined, color: AppColors.primary),
                    title: const Text('Email Address'),
                    subtitle: Text(_user.email),
                    trailing: _buildVerificationBadge(
                      _user.emailVerified,
                      () => _showOtpVerificationDialog('email', _user.email),
                    ),
                  ),
                  const Divider(),
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.phone_outlined, color: AppColors.primary),
                    title: const Text('Phone Number'),
                    subtitle: Text(_user.phone.isNotEmpty ? _user.phone : 'Not provided'),
                    trailing: _user.phone.isNotEmpty
                        ? _buildVerificationBadge(
                            _user.phoneVerified,
                            () => _showOtpVerificationDialog('phone', _user.phone),
                          )
                        : null,
                  ),
                  const Divider(),
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.favorite_outline, color: AppColors.primary),
                    title: const Text('Emergency Contact'),
                    subtitle: Text(
                      _user.trustedContactPhone.isNotEmpty
                          ? '${_user.trustedContactName} (${_user.trustedContactPhone})'
                          : 'Not configured',
                    ),
                    trailing: _user.trustedContactPhone.isNotEmpty
                        ? _buildVerificationBadge(
                            _user.trustedContactVerified,
                            () => _showOtpVerificationDialog('trusted_contact', _user.trustedContactPhone),
                          )
                        : null,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Security & Preferences Section
          const Text('⚙️ Account & Security', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.lock_reset, color: AppColors.primary),
                  title: const Text('Change Password'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _showChangePasswordDialog,
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.info_outline, color: AppColors.primary),
                  title: const Text('About Antara'),
                  subtitle: const Text('v2.0 • NLP Emotional Companion'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    showAboutDialog(
                      context: context,
                      applicationName: 'Antara',
                      applicationVersion: '2.0.0',
                      applicationIcon: const Text('🌷', style: TextStyle(fontSize: 32)),
                      children: const [
                        Text('Antara is a confidential self-help emotional reflection companion powered by NLP sentiment and emotion analysis.'),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),

          // Logout Button
          OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.error,
              side: const BorderSide(color: AppColors.error),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
            onPressed: _handleLogout,
            icon: const Icon(Icons.logout),
            label: const Text('Sign Out'),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}

extension StringExtension on String {
  String capitalize() {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
}
