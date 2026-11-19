import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class HistoryScreen extends StatefulWidget {
  final String patientId;
  const HistoryScreen({Key? key, required this.patientId}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _isLoading = true;
  List<dynamic> _sessions = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final res = await ApiService.getHistory(widget.patientId);
    if (!mounted) return;

    setState(() {
      _isLoading = false;
      if (res['success'] && res['sessions'] != null) {
        _sessions = res['sessions'];
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: AppColors.primary));
    }

    if (_sessions.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Center(child: Text('📖', style: TextStyle(fontSize: 34))),
              ),
              const SizedBox(height: 16),
              const Text(
                'No Past Reflections Yet',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),
              const Text(
                'Whenever you complete a reflection session with Antara, your key takeaways and emotional insights will appear here.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadHistory,
      color: AppColors.primary,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _sessions.length,
        itemBuilder: (ctx, idx) {
          final s = _sessions[idx];
          final completedAt = s['completed_at'] ?? s['created_at'] ?? 'Recent Session';
          final dominantEmotion = (s['dominant_emotion'] ?? 'calm').toString().replaceAll('_', ' ');

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Session #${idx + 1}',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          dominantEmotion.toUpperCase(),
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    completedAt.toString(),
                    style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                  ),
                  if (s['summary'] != null && s['summary'].toString().isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(
                      s['summary'].toString(),
                      style: const TextStyle(fontSize: 14, height: 1.35, color: AppColors.textPrimary),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
