import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

import '../config/app_config.dart';
import 'token_storage.dart';

/// Thin wrapper that owns a configured [Dio] instance plus an auth
/// interceptor that attaches the bearer token and transparently refreshes
/// it on a 401, retrying the original request once.
///
/// ASSUMPTION: refresh endpoint is POST /auth/refresh with body
///   { "refresh_token": "<token>" }
/// returning { "access_token": "...", "refresh_token": "..." }.
/// If the backend instead rotates refresh tokens differently or uses
/// cookie-based refresh, update `_refresh()` accordingly.
class DioClient {
  DioClient({required this.tokenStorage, Dio? dio})
      : _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: AppConfig.baseUrl,
                connectTimeout: AppConfig.connectTimeout,
                receiveTimeout: AppConfig.receiveTimeout,
                sendTimeout: AppConfig.sendTimeout,
                headers: {'Accept': 'application/json'},
              ),
            ) {
    _dio.interceptors.add(_authInterceptor());
    // Keep logging out of release builds.
    assert(() {
      _dio.interceptors.add(
        PrettyDioLogger(
          requestHeader: false,
          requestBody: true,
          responseBody: false,
          compact: true,
        ),
      );
      return true;
    }());
  }

  final Dio _dio;
  final TokenStorage tokenStorage;

  Dio get instance => _dio;

  // Serializes concurrent refresh attempts so parallel 401s don't each
  // fire their own refresh call.
  Future<String?>? _refreshing;

  InterceptorsWrapper _authInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Let auth endpoints go through unauthenticated.
        if (!_isAuthFreeRoute(options.path)) {
          final token = await tokenStorage.accessToken;
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
        }
        handler.next(options);
      },
      onError: (DioException error, handler) async {
        final isUnauthorized = error.response?.statusCode == 401;
        final alreadyRetried = error.requestOptions.extra['retried'] == true;

        if (isUnauthorized && !alreadyRetried && !_isAuthFreeRoute(error.requestOptions.path)) {
          final newToken = await _refresh();
          if (newToken != null) {
            final retryOptions = error.requestOptions;
            retryOptions.headers['Authorization'] = 'Bearer $newToken';
            retryOptions.extra['retried'] = true;
            try {
              final response = await _dio.fetch(retryOptions);
              return handler.resolve(response);
            } on DioException catch (retryError) {
              return handler.next(retryError);
            }
          } else {
            await tokenStorage.clear();
            // Downstream: an app-level listener on auth state should route
            // to the login screen when tokens are cleared.
          }
        }
        handler.next(error);
      },
    );
  }

  bool _isAuthFreeRoute(String path) {
    return path.contains('/auth/login') ||
        path.contains('/auth/register') ||
        path.contains('/auth/refresh');
  }

  Future<String?> _refresh() {
    _refreshing ??= _doRefresh();
    return _refreshing!.whenComplete(() => _refreshing = null);
  }

  Future<String?> _doRefresh() async {
    final refreshToken = await tokenStorage.refreshToken;
    if (refreshToken == null) return null;
    try {
      final response = await Dio(BaseOptions(baseUrl: AppConfig.baseUrl)).post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      final newAccess = response.data['access_token'] as String?;
      final newRefresh = response.data['refresh_token'] as String? ?? refreshToken;
      if (newAccess == null) return null;
      await tokenStorage.saveTokens(accessToken: newAccess, refreshToken: newRefresh);
      return newAccess;
    } catch (_) {
      return null;
    }
  }
}
