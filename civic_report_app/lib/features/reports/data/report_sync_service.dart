import 'dart:io';

import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../domain/report.dart';
import '../../../core/network/token_storage.dart';
import '../../../core/storage/app_database.dart';
import 'reports_repository.dart';

const int kMaxUploadAttempts = 5;

class ReportSyncService {
  ReportSyncService({AppDatabase? db, Dio? dio})
      : _db = db ?? AppDatabase() {
    final tokenStorage = TokenStorage();
    _dio = dio ?? DioClient(tokenStorage: tokenStorage).instance;
    _repo = ReportsRepository(_dio);
  }

  final AppDatabase _db;
  late final Dio _dio;
  late final ReportsRepository _repo;

  /// Returns true if every queued report is either synced or has hit the
  /// max attempt count.
  Future<bool> drainQueue() async {
    final queue = await _db.watchQueueOnce();
    var allSettled = true;

    for (final report in queue) {
      // Already synced — prune it from the local queue now rather than
      // waiting for a separate cleanup pass. This is what was causing
      // old/stale reports to be re-submitted after a backend/DB reset:
      // synced rows were kept around and picked up again on next drain.
      if (report.status == QueueStatus.synced) {
        await _db.deleteSynced(report.uuid);
        continue;
      }

      // Exhausted retries — stop trying and drop it rather than
      // resurrecting it on every app start.
      if (report.attemptCount >= kMaxUploadAttempts) {
        await _db.deleteSynced(report.uuid);
        continue;
      }

      final ok = await _syncOne(report);
      if (!ok) allSettled = false;
    }

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
      // Submit report and receive full Report object with AI analysis
      final submittedReport = await _repo.submitReport(
        description: report.description,
        categoryId: report.categoryId,
        latitude: report.latitude,
        longitude: report.longitude,
        isAnonymous: report.isAnonymous,
        mediaIds: mediaIds,
      );
      // Currently we don't persist AI fields locally; you may extend the local schema to store them.
      // Using submittedReport to avoid unused variable warnings.

      await _db.updateStatus(report.uuid, QueueStatus.synced);
      // Delete immediately rather than waiting for the next drainQueue
      // pass, so a synced row can never be picked up again.
      await _db.deleteSynced(report.uuid);
      return true;
    } catch (e) {
      await _db.incrementAttempt(report.uuid);
      await _db.updateStatus(report.uuid, QueueStatus.failed, error: e.toString());
      return false;
    }
  }
}