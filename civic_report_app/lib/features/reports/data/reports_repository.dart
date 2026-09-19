import 'dart:io';

import 'package:dio/dio.dart';
import 'package:uuid/uuid.dart';

import '../domain/report.dart';

/// ASSUMPTION: POST /media/upload accepts multipart/form-data with field
/// name "file" and returns { "media_id": "..." }. If the backend instead
/// uses a presigned-URL flow (request a URL, PUT the file, then confirm),
/// swap the body of [uploadMedia] for that two-step exchange — the rest
/// of the queue/retry logic is unaffected either way.
///
/// ASSUMPTION: POST /reports accepts:
///   {
///     "description": "...",
///     "category_id": "..." | null,
///     "latitude": 0.0, "longitude": 0.0,
///     "is_anonymous": bool,
///     "media_ids": ["...", "..."],
///     "idempotency_key": "uuid-string"
///   }
/// and returns the created report, which — per a later addition to the
/// test backend — also includes a resolved "media_urls" array (absolute
/// or root-relative URLs for each photo), since media_ids alone aren't
/// renderable without knowing where to fetch each photo from.
class ReportsRepository {
  ReportsRepository(this._dio);

  final Dio _dio;
  static const _uuid = Uuid();

  Future<String> uploadMedia(File file) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(file.path, filename: file.uri.pathSegments.last),
    });
    final response = await _dio.post('/media/upload', data: formData);
    final mediaId = response.data['media_id'] as String?;
    if (mediaId == null) {
      throw const FormatException('media_id missing from /media/upload response');
    }
    return mediaId;
  }

  Future<Report> submitReport({
    required String description,
    String? categoryId,
    required double latitude,
    required double longitude,
    required bool isAnonymous,
    required List<String> mediaIds,
  }) async {
    // Generate a short title from description for the backend.
    var title = description.length > 50 ? '${description.substring(0, 47)}...' : description;
    if (title.length < 5) {
      title = title.padRight(5, '.');
    }
    
    final category = categoryId != null ? categoryId.toUpperCase() : 'OTHER';
    
    // Generate a unique idempotency key to prevent duplicate submissions
    // if the request is retried (network timeout, etc.)
    final idempotencyKey = _uuid.v4();
    
    final response = await _dio.post('/challenges', data: {
      'title': title,
      'description': description,
      'category': category,
      'latitude': latitude,
      'longitude': longitude,
      'is_anonymous': isAnonymous,
      'media_ids': mediaIds,
      'idempotency_key': idempotencyKey,  // Backend uses this to deduplicate
    });
    return Report.fromJson(response.data as Map<String, dynamic>);
  }

  /// ASSUMPTION: GET /reports accepts optional query params
  /// lat, lng, radius (km), category, status — matches the filters
  /// named in the original spec.
  Future<List<Report>> listReports({
    double? lat,
    double? lng,
    double radiusKm = 10,
    String? category,
    String? status,
  }) async {
    final response = await _dio.get('/challenges', queryParameters: {
      if (lat != null) 'lat': lat,
      if (lng != null) 'lng': lng,
      if (lat != null && lng != null) 'radius': radiusKm,
      if (category != null) 'category': category,
      if (status != null) 'status': status,
    });
    final list = (response.data as List).cast<Map<String, dynamic>>();
    return list.map(Report.fromJson).toList();
  }

  Future<Report> getReport(String id) async {
    final response = await _dio.get('/challenges/$id');
    return Report.fromJson(response.data as Map<String, dynamic>);
  }

  Future<int> upvote(String id) async {
    final response = await _dio.post('/challenges/$id/upvote');
    return (response.data['upvotes'] as num).toInt();
  }

  Future<List<Report>> myReports() async {
    final response = await _dio.get('/challenges/me');
    final list = (response.data as List).cast<Map<String, dynamic>>();
    return list.map(Report.fromJson).toList();
  }
}