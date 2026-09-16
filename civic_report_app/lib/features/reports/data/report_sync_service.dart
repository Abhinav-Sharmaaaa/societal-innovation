import 'dart:io';

import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../core/network/token_storage.dart';
import '../../../core/storage/app_database.dart';
import 'reports_repository.dart';

const int kMaxUploadAttempts = 5;

class ReportSyncService {
  ReportSyncService({AppDatabase? db, Dio? dio})
      : _db = db ?? AppDatabase(),
        _ownsDb = db == null {
    final tokenStorage = TokenStorage();
    _dio = dio ?? DioClient(tokenStorage: tokenStorage).instance;
    _repo = ReportsRepository(_dio);
  }

  final AppDatabase _db;
  final bool _ownsDb;
  late final Dio _dio;
  late final ReportsRepository _repo;

  /// Returns true if every queued report is either synced or has hit the
  Future<bool> drainQueue() async {
    final queue = await _db.watchQueueOnce();
    var allSettled = true;

    for (final report in queue) {
      if (report.status == QueueStatus.synced) continue;
      if (report.attemptCount >= kMaxUploadAttempts) continue;

      final ok = await _syncOne(report);
      if (!ok) allSettled = false;
    }

    if (_ownsDb) await _db.close();
    return allSettled;
  }

  Future<bool> _syncOne(PendingReport report) async {
    try {
      await _db.updateStatus(report.uuid, QueueStatus.uploadingMedia);
      final mediaRows = await _db.mediaFor(report.uuid);
      final mediaIds = <String>[];

      for (final media in mediaRows) {
        if (media.remoteMediaId != null) {
          mediaIds.add(media.remoteMediaId!);
          continue;
        }
        final file = File(media.localFilePath);
        if (!await file.exists()) {
          // Local file vanished (e.g. storage cleared) — nothing to
          // retry for this photo; skip it rather than blocking forever.
          continue;
        }
        final remoteId = await _repo.uploadMedia(file);
        await _db.setMediaRemoteId(media.id, remoteId);
        mediaIds.add(remoteId);
      }

      await _db.updateStatus(report.uuid, QueueStatus.uploadingReport);
      await _repo.submitReport(
        description: report.description,
        categoryId: report.categoryId,
        latitude: report.latitude,
        longitude: report.longitude,
        isAnonymous: report.isAnonymous,
        mediaIds: mediaIds,
      );

      await _db.updateStatus(report.uuid, QueueStatus.synced);
      // Keep synced rows briefly for UI confirmation; a separate
      // periodic prune (or immediate delete) can remove them once the
      // "My Reports" screen has folded in the server copy.
      return true;
    } catch (e) {
      await _db.incrementAttempt(report.uuid);
      await _db.updateStatus(report.uuid, QueueStatus.failed, error: e.toString());
      return false;
    }
  }
}
