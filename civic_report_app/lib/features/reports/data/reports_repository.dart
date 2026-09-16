import 'dart:io';

import 'package:dio/dio.dart';

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
///     "media_ids": ["...", "..."]
///   }
/// and returns the created report, which — per a later addition to the
/// test backend — also includes a resolved "media_urls" array (absolute
/// or root-relative URLs for each photo), since media_ids alone aren't
/// renderable without knowing where to fetch each photo from.
class ReportsRepository {
  ReportsRepository(this._dio);

  final Dio _dio;

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

  Future<String> submitReport({
    required String description,
    String? categoryId,
    required double latitude,
    required double longitude,
    required bool isAnonymous,
    required List<String> mediaIds,
  }) async {
    final response = await _dio.post('/reports', data: {
      'description': description,
      'category_id': categoryId,
      'latitude': latitude,
      'longitude': longitude,
      'is_anonymous': isAnonymous,
      'media_ids': mediaIds,
    });
    final id = response.data['id']?.toString();
    if (id == null) {
      throw const FormatException('id missing from /reports response');
    }
    return id;
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
    final response = await _dio.get('/reports', queryParameters: {
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
    final response = await _dio.get('/reports/$id');
    return Report.fromJson(response.data as Map<String, dynamic>);
  }

  Future<int> upvote(String id) async {
    final response = await _dio.post('/reports/$id/upvote');
    return (response.data['upvotes'] as num).toInt();
  }

  Future<List<Report>> myReports() async {
    final response = await _dio.get('/users/me/reports');
    final list = (response.data as List).cast<Map<String, dynamic>>();
    return list.map(Report.fromJson).toList();
  }
}
