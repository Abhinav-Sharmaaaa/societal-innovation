import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';

class UserProfile {
  UserProfile({
    required this.id,
    required this.email,
    required this.points,
    required this.isAnonymousDefault,
  });

  final String id;
  final String email;
  final int points;
  final bool isAnonymousDefault;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'].toString(),
      email: json['email'] as String? ?? '',
      points: (json['points'] as num?)?.toInt() ?? 0,
      isAnonymousDefault: json['is_anonymous_default'] as bool? ?? false,
    );
  }
}

/// ASSUMPTION: GET /users/me returns
///   { id, email, points, is_anonymous_default, created_at }
final userMeProvider = FutureProvider<UserProfile>((ref) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/users/me');
  return UserProfile.fromJson(response.data as Map<String, dynamic>);
});
