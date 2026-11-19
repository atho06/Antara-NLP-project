import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import 'chat_screen.dart';
import 'history_screen.dart';
import 'settings_screen.dart';

class DashboardScreen extends StatefulWidget {
  final UserModel user;
  const DashboardScreen({Key? key, required this.user}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;
  late UserModel _currentUser;

  @override
  void initState() {
    super.initState();
    _currentUser = widget.user;
  }

  void _updateUser(UserModel updated) {
    setState(() => _currentUser = updated);
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }

  void _showStartSessionDialog() {
    int selectedDuration = 5;
    String selectedCategory = 'daily_routine';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Container(
              padding: const EdgeInsets.all(24),
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.grey.shade300,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  const Text(
                    'Begin Reflection 🌷',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'How much time would you like to take for yourself right now?',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: 20),
                  const Text('⏱️ Session Duration', style: TextStyle(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    children: [5, 10, 15, 20, 0].map((mins) {
                      final label = mins == 0 ? 'Unlimited' : '$mins min';
                      final isSelected = selectedDuration == mins;
                      return ChoiceChip(
                        label: Text(label),
                        selected: isSelected,
                        selectedColor: AppColors.primaryLight.withOpacity(0.3),
                        onSelected: (val) {
                          if (val) setModalState(() => selectedDuration = mins);
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 20),
                  const Text('🎯 Focus Topic', style: TextStyle(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      {'key': 'daily_routine', 'label': '☀️ Daily Routine'},
                      {'key': 'stress', 'label': '🌊 Stress & Overwhelm'},
                      {'key': 'sadness', 'label': '🌧️ Low Energy / Sadness'},
                      {'key': 'relationships', 'label': '🤝 Relationships'},
                      {'key': 'general', 'label': '🌿 Open Reflection'},
                    ].map((topic) {
                      final isSelected = selectedCategory == topic['key'];
                      return ChoiceChip(
                        label: Text(topic['label']!),
                        selected: isSelected,
                        selectedColor: AppColors.primaryLight.withOpacity(0.3),
                        onSelected: (val) {
                          if (val) setModalState(() => selectedCategory = topic['key']!);
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 28),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.pop(ctx);
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => ChatScreen(
                            user: _currentUser,
                            durationMinutes: selectedDuration,
                            category: selectedCategory,
                          ),
                        ),
                      );
                    },
                    child: const Text('Start Session'),
                  ),
                  const SizedBox(height: 12),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _showSosConfirmation() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Text('🆘 Emergency Support', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.sosRed)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'If you are feeling overwhelmed or unsafe, immediate help is available 24/7:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('• Tele-MANAS: 14416 (Toll-Free, 24/7)', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 4),
                  Text('• KIRAN Mental Health: 1800-599-0019', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 4),
                  Text('• Vandrevala Foundation: +91 9999 666 555', style: TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            if (_currentUser.trustedContactPhone.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                'Would you like to dispatch an alert SMS to your trusted contact (${_currentUser.trustedContactName})?',
                style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
          if (_currentUser.trustedContactPhone.isNotEmpty)
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.sosRed),
              onPressed: () async {
                Navigator.pop(ctx);
                final res = await ApiService.triggerSos(_currentUser.patientId);
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(res['success'] ? 'Alert dispatched to trusted contact.' : 'Could not dispatch alert.'),
                  ),
                );
              },
              child: const Text('Send SOS Alert'),
            ),
        ],
      ),
    );
  }

  Widget _buildHomeView() {
    final firstName = _currentUser.fullName.split(' ').first;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${_getGreeting()},',
                    style: const TextStyle(fontSize: 16, color: AppColors.textSecondary),
                  ),
                  Text(
                    firstName,
                    style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.emergency_outlined, color: AppColors.sosRed, size: 28),
                tooltip: 'Emergency SOS',
                onPressed: _showSosConfirmation,
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Daily Gentle Quote Card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.primary.withOpacity(0.12), AppColors.primaryLight.withOpacity(0.08)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              border: Border.Border.all(color: AppColors.primary.withOpacity(0.15)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text('🌸', style: TextStyle(fontSize: 20)),
                    SizedBox(width: 8),
                    Text(
                      'Daily Gentle Reminder',
                      style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary, fontSize: 14),
                    ),
                  ],
                ),
                SizedBox(height: 10),
                Text(
                  '"You do not have to have everything figured out right now. Just taking five quiet minutes to check in with yourself is enough."',
                  style: TextStyle(fontSize: 15, fontStyle: FontStyle.italic, color: AppColors.textPrimary, height: 1.4),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          // Primary Start Session Card
          Card(
            elevation: 3,
            shadowColor: AppColors.primary.withOpacity(0.2),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
            child: InkWell(
              borderRadius: BorderRadius.circular(24),
              onTap: _showStartSessionDialog,
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.15),
                        shape: BoxShape.circle,
                      ),
                      child: const Center(child: Text('💬', style: TextStyle(fontSize: 32))),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Start a Reflection Session',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'A private, thoughtful conversation with Antara. No pressure, no judgment—talk at your own pace.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.3),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton.icon(
                      onPressed: _showStartSessionDialog,
                      icon: const Icon(Icons.arrow_forward_rounded, size: 18),
                      label: const Text('Begin Today\'s Check-in'),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          // Trust & Confidentiality Banner
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.green.shade50,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.green.shade200),
            ),
            child: const Row(
              children: [
                Icon(Icons.shield_outlined, color: AppColors.success, size: 20),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Confidential & Local: Your reflections are stored securely on your device.',
                    style: TextStyle(fontSize: 12, color: AppColors.textPrimary),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final views = [
      _buildHomeView(),
      HistoryScreen(patientId: _currentUser.patientId),
      SettingsScreen(user: _currentUser, onUserUpdated: _updateUser),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(
          _currentIndex == 0 ? 'Antara 🌷' : _currentIndex == 1 ? 'Past Reflections 📖' : 'Settings ⚙️',
        ),
      ),
      body: views[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.history_outlined), selectedIcon: Icon(Icons.history), label: 'History'),
          NavigationDestination(icon: Icon(Icons.settings_outlined), selectedIcon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}
