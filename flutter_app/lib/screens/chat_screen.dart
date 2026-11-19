import 'dart:async';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../models/user_model.dart';
import '../models/chat_message.dart';
import '../services/api_service.dart';
import 'session_summary_screen.dart';

class ChatScreen extends StatefulWidget {
  final UserModel user;
  final int durationMinutes;
  final String category;

  const ChatScreen({
    Key? key,
    required this.user,
    required this.durationMinutes,
    required this.category,
  }) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<ChatMessage> _messages = [];
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  String? _sessionId;
  bool _isLoading = true;
  bool _isSending = false;

  Timer? _countdownTimer;
  int _targetSeconds = 0;
  int _secondsElapsed = 0;
  bool _timeUpPromptShown = false;

  @override
  void initState() {
    super.initState();
    _targetSeconds = widget.durationMinutes * 60;
    _initSession();
  }

  Future<void> _initSession() async {
    final result = await ApiService.startSession(
      patientId: widget.user.patientId,
      durationMinutes: widget.durationMinutes,
      category: widget.category,
    );

    if (!mounted) return;

    if (result['success']) {
      setState(() {
        _sessionId = result['session_id'];
        _targetSeconds = result['target_seconds'] ?? _targetSeconds;
        _isLoading = false;

        // Add greeting message
        _messages.add(
          ChatMessage(
            text: result['initial_message'] ?? 'Hello, I am Antara. Let\'s begin when you are ready.',
            isUser: false,
            timestamp: DateTime.now(),
          ),
        );

        // Add first question
        final firstQ = result['first_question'];
        if (firstQ != null && firstQ['text'] != null) {
          _messages.add(
            ChatMessage(
              text: firstQ['text'],
              isUser: false,
              timestamp: DateTime.now(),
            ),
          );
        }
      });

      _startTimer();
    } else {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'] ?? 'Could not start session')),
      );
    }
  }

  void _startTimer() {
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) return;
      setState(() {
        _secondsElapsed++;
      });

      // If target reached and haven't prompted yet
      if (_targetSeconds > 0 && _secondsElapsed >= _targetSeconds && !_timeUpPromptShown) {
        _timeUpPromptShown = true;
        _showTimeCompletedPrompt();
      }
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    final text = _inputController.text.trim();
    if (text.isEmpty || _isSending || _sessionId == null) return;

    _inputController.clear();
    setState(() {
      _isSending = true;
      _messages.add(ChatMessage(text: text, isUser: true, timestamp: DateTime.now()));
    });
    _scrollToBottom();

    final result = await ApiService.sendMessage(
      sessionId: _sessionId!,
      patientId: widget.user.patientId,
      message: text,
      elapsedSeconds: _secondsElapsed,
    );

    if (!mounted) return;
    setState(() => _isSending = false);

    if (result['success']) {
      final reply = result['reply'];
      final nextQ = result['next_question'];
      final isCrisis = result['is_crisis'] ?? false;
      final allowContinuation = result['allow_continuation'] ?? false;

      setState(() {
        if (reply != null && reply.isNotEmpty) {
          _messages.add(
            ChatMessage(
              text: reply,
              isUser: false,
              timestamp: DateTime.now(),
              isCrisis: isCrisis,
              isContinuationPrompt: allowContinuation,
            ),
          );
        }
        if (nextQ != null && nextQ['text'] != null) {
          _messages.add(
            ChatMessage(
              text: nextQ['text'],
              isUser: false,
              timestamp: DateTime.now(),
            ),
          );
        }
      });
      _scrollToBottom();

      if (allowContinuation && !_timeUpPromptShown) {
        _timeUpPromptShown = true;
        _showTimeCompletedPrompt();
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'] ?? 'Failed to send message')),
      );
    }
  }

  void _showTimeCompletedPrompt() {
    showModalBottomSheet(
      context: context,
      isDismissible: false,
      enableDrag: false,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('⏱️ Time Check-in', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            Text(
              'We have reached your ${widget.durationMinutes}-minute mark. Would you like to wrap up and see your reflection summary, or keep talking?',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 15, color: AppColors.textSecondary, height: 1.4),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.pop(ctx);
                      _wrapUpSession();
                    },
                    child: const Text('Wrap Up & Finish'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(ctx);
                      // Continue session indefinitely
                      setState(() {
                        _targetSeconds = 0; // unlimited
                      });
                    },
                    child: const Text('Keep Talking'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  Future<void> _wrapUpSession() async {
    _countdownTimer?.cancel();
    if (_sessionId == null) {
      Navigator.pop(context);
      return;
    }

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      ),
    );

    final res = await ApiService.endSession(
      sessionId: _sessionId!,
      patientId: widget.user.patientId,
    );

    if (!mounted) return;
    Navigator.pop(context); // close spinner

    if (res['success'] && res['summary'] != null) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => SessionSummaryScreen(
            summaryData: res['summary'],
            user: widget.user,
          ),
        ),
      );
    } else {
      Navigator.pop(context);
    }
  }

  String _formatTimer() {
    if (_targetSeconds == 0) {
      final m = _secondsElapsed ~/ 60;
      final s = _secondsElapsed % 60;
      return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')} (Open)';
    }
    final remaining = (_targetSeconds - _secondsElapsed).clamp(0, _targetSeconds);
    final m = remaining ~/ 60;
    final s = remaining % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')} remaining';
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final progress = _targetSeconds > 0 ? (_secondsElapsed / _targetSeconds).clamp(0.0, 1.0) : 0.0;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          children: [
            const Text('Antara 🌷', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text(
              _formatTimer(),
              style: const TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w500),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: _wrapUpSession,
            child: const Text('Finish', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : Column(
              children: [
                if (_targetSeconds > 0)
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: Colors.grey.shade200,
                    valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                    minHeight: 3,
                  ),
                Expanded(
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    itemCount: _messages.length,
                    itemBuilder: (ctx, idx) {
                      final msg = _messages[idx];
                      return _buildMessageBubble(msg);
                    },
                  ),
                ),
                _buildInputBar(),
              ],
            ),
    );
  }

  Widget _buildMessageBubble(ChatMessage msg) {
    if (msg.isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12, left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
          decoration: BoxDecoration(
            color: AppColors.userBubble,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(20),
              topRight: Radius.circular(20),
              bottomLeft: Radius.circular(20),
              bottomRight: Radius.circular(4),
            ),
          ),
          child: Text(
            msg.text,
            style: const TextStyle(color: AppColors.userBubbleText, fontSize: 15, height: 1.3),
          ),
        ),
      );
    }

    // Bot message
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12, right: 48),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        decoration: BoxDecoration(
          color: msg.isCrisis ? Colors.red.shade50 : AppColors.botBubble,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
            bottomRight: Radius.circular(20),
            bottomLeft: Radius.circular(4),
          ),
          border: msg.isCrisis ? Border.all(color: AppColors.sosRed) : null,
        ),
        child: Text(
          msg.text,
          style: TextStyle(
            color: msg.isCrisis ? AppColors.sosRed : AppColors.botBubbleText,
            fontSize: 15,
            height: 1.35,
          ),
        ),
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, -3),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _inputController,
                textCapitalization: TextCapitalization.sentences,
                maxLines: null,
                decoration: InputDecoration(
                  hintText: 'Type your reflection here...',
                  hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 14),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  border: InputBorder.none,
                  enabledBorder: InputBorder.none,
                  focusedBorder: InputBorder.none,
                ),
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
            const SizedBox(width: 8),
            Container(
              decoration: const BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: IconButton(
                icon: _isSending
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.send_rounded, color: Colors.white, size: 20),
                onPressed: _isSending ? null : _sendMessage,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
