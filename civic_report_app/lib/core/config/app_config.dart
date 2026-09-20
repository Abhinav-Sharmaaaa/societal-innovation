/// Central place for environment-dependent configuration.
///
/// ASSUMPTION: base URL and any API keys are injected at build time via
/// --dart-define. Replace the default with your actual dev backend URL.
class AppConfig {
  AppConfig._();

  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://societal-innovation-ieeu.onrender.com/api/v1',
  );

  static const String mapsApiKey = String.fromEnvironment('MAPS_API_KEY');

  /// Uploaded photos are served from the backend's root (e.g.
  /// /uploads/xyz.jpg), not under the /api prefix that baseUrl includes
  /// for the JSON API. This strips a trailing "/api" so relative media
  /// URLs returned by the backend resolve correctly.
  static String get mediaOrigin =>
      baseUrl.endsWith('/api') ? baseUrl.substring(0, baseUrl.length - 4) : baseUrl;

  /// Turns a relative media URL like "/uploads/x.jpg" into an absolute
  /// one the app can load directly. Already-absolute URLs pass through.
  static String resolveMediaUrl(String url) {
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    return '$mediaOrigin$url';
  }

  static const Duration connectTimeout = Duration(seconds: 90);
  static const Duration receiveTimeout = Duration(seconds: 90);
  static const Duration sendTimeout = Duration(seconds: 60);

  // Image compression targets — tune against real backend storage costs.
  static const int imageMaxWidth = 1600;
  static const int imageMaxHeight = 1600;
  static const int imageQuality = 70;

  static const String pendingSyncTaskName = 'civic_report_pending_sync';
}
