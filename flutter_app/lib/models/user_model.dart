class UserModel {
  final String patientId;
  final String email;
  final String fullName;
  final String phone;
  final String trustedContactName;
  final String trustedContactPhone;
  final bool emailVerified;
  final bool phoneVerified;
  final bool trustedContactVerified;
  final String preferredTheme;

  UserModel({
    required this.patientId,
    required this.email,
    required this.fullName,
    required this.phone,
    required this.trustedContactName,
    required this.trustedContactPhone,
    this.emailVerified = false,
    this.phoneVerified = false,
    this.trustedContactVerified = false,
    this.preferredTheme = 'lavender_peace',
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      patientId: json['patient_id'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? 'Antara User',
      phone: json['contact_number'] ?? json['phone'] ?? '',
      trustedContactName: json['trusted_contact_name'] ?? '',
      trustedContactPhone: json['trusted_contact_number'] ?? json['trusted_contact_phone'] ?? '',
      emailVerified: (json['email_verified'] == 1 || json['email_verified'] == true),
      phoneVerified: (json['phone_verified'] == 1 || json['phone_verified'] == true),
      trustedContactVerified: (json['trusted_contact_verified'] == 1 || json['trusted_contact_verified'] == true),
      preferredTheme: json['preferred_theme'] ?? 'lavender_peace',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'patient_id': patientId,
      'email': email,
      'full_name': fullName,
      'contact_number': phone,
      'trusted_contact_name': trustedContactName,
      'trusted_contact_number': trustedContactPhone,
      'email_verified': emailVerified ? 1 : 0,
      'phone_verified': phoneVerified ? 1 : 0,
      'trusted_contact_verified': trustedContactVerified ? 1 : 0,
      'preferred_theme': preferredTheme,
    };
  }
}
