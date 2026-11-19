class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? emotion;
  final bool isCrisis;
  final bool isContinuationPrompt;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.emotion,
    this.isCrisis = false,
    this.isContinuationPrompt = false,
  });
}
