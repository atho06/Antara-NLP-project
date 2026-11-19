import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../models/user_model.dart';
import 'dashboard_screen.dart';

class SessionSummaryScreen extends StatelessWidget {
  final Map<String, dynamic> summaryData;
  final UserModel user;

  const SessionSummaryScreen({
    Key? key,
    required this.summaryData,
    required this.user,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final dominantEmotion = (summaryData['dominant_emotion'] ?? 'calm_grounded').toString().replaceAll('_', ' ');
    final summaryText = summaryData['summary'] ?? 'Thank you for taking this time for self-reflection.';
    final affirmation = summaryData['affirmation'] ?? 'Be gentle with yourself today. Every reflection matters. 🌸';
    final exchangesCount = summaryData['exchanges_count'] ?? 0;
    final duration = summaryData['duration_minutes'] ?? 5;

    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('Reflection Summary 🌸'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.12),
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: Text('🌿', style: TextStyle(fontSize: 40)),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Well Done!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'You showed up for yourself today',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 15, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 32),
              // Session Stats Card
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
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildStat('⏱️ Time', '$duration min'),
                        Container(width: 1, height: 36, color: Colors.grey.shade200),
                        _buildStat('💬 Reflections', '$exchangesCount answers'),
                        Container(width: 1, height: 36, color: Colors.grey.shade200),
                        _buildStat('✨ Tone', dominantEmotion.toUpperCase()),
                      ],
                    ),
                    const SizedBox(height: 20),
                    const Divider(),
                    const SizedBox(height: 16),
                    Text(
                      summaryText,
                      style: const TextStyle(fontSize: 15, height: 1.4, color: AppColors.textPrimary),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              // Affirmation Card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: AppColors.primary.withOpacity(0.2)),
                ),
                child: Row(
                  children: [
                    const Text('🌸', style: TextStyle(fontSize: 24)),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        affirmation,
                        style: const TextStyle(
                          fontSize: 14,
                          fontStyle: FontStyle.italic,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 36),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(builder: (_) => DashboardScreen(user: user)),
                    (route) => false,
                  );
                },
                child: const Text('Back to Home'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStat(String label, String value) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.primary),
        ),
      ],
    );
  }
}
