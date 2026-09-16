import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Wraps flutter_secure_storage for auth tokens.
///
/// ASSUMPTION: backend issues a short-lived access token + longer-lived
/// refresh token pair from POST /auth/login and POST /auth/refresh, e.g.:
///   { "access_token": "...", "refresh_token": "...", "expires_in": 900 }
class TokenStorage {
  TokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  static const _accessKey = 'civic_access_token';
  static const _refreshKey = 'civic_refresh_token';
  static const _userIdKey = 'civic_user_id';

  Future<String?> get accessToken => _storage.read(key: _accessKey);
  Future<String?> get refreshToken => _storage.read(key: _refreshKey);
  Future<String?> get userId => _storage.read(key: _userIdKey);

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
    String? userId,
  }) async {
    await _storage.write(key: _accessKey, value: accessToken);
    await _storage.write(key: _refreshKey, value: refreshToken);
    if (userId != null) {
      await _storage.write(key: _userIdKey, value: userId);
    }
  }

  Future<void> clear() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
    await _storage.delete(key: _userIdKey);
  }

  Future<bool> get hasSession async => (await accessToken) != null;
}
