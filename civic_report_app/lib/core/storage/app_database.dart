import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

part 'app_database.g.dart';

/// Sync lifecycle for a locally-queued report.
/// pending      -> waiting for connectivity / first upload attempt
/// uploadingMedia -> media upload(s) in flight
/// uploadingReport -> POST /reports in flight
/// synced       -> server accepted it, safe to prune locally
/// failed       -> exhausted retries or got a non-retryable error
enum QueueStatus { pending, uploadingMedia, uploadingReport, synced, failed }

/// One row per media file attached to a not-yet-synced report. Kept
/// separate from PendingReports so a report can have N photos, and so
/// media upload progress can be tracked independently (each photo gets
/// its own media_id from POST /media/upload before the report is posted).
class PendingReportMedia extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get pendingReportUuid => text()(); // FK -> PendingReports.uuid
  TextColumn get localFilePath => text()(); // compressed file on disk
  TextColumn get remoteMediaId => text().nullable()(); // set once uploaded
  IntColumn get sortOrder => integer().withDefault(const Constant(0))();
}

class PendingReports extends Table {
  // Client-generated UUID is the stable identity used for de-duplication
  // and to correlate local rows with server rows once synced (submit it
  // as a client_request_id if the backend supports idempotency; otherwise
  // it's used purely for local tracking).
  TextColumn get uuid => text()();
  TextColumn get description => text()();
  TextColumn get categoryId => text().nullable()(); // optional per spec
  RealColumn get latitude => real()();
  RealColumn get longitude => real()();
  BoolColumn get manuallyAdjustedPin => boolean().withDefault(const Constant(false))();
  BoolColumn get isAnonymous => boolean().withDefault(const Constant(false))();
  IntColumn get status => intEnum<QueueStatus>().withDefault(const Constant(0))();
  IntColumn get attemptCount => integer().withDefault(const Constant(0))();
  TextColumn get lastError => text().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {uuid};
}

@DriftDatabase(tables: [PendingReports, PendingReportMedia])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  // --- Pending reports -----------------------------------------------

  Future<String> insertPendingReport({
    required String uuid,
    required String description,
    String? categoryId,
    required double latitude,
    required double longitude,
    bool manuallyAdjustedPin = false,
    bool isAnonymous = false,
  }) async {
    await into(pendingReports).insert(
      PendingReportsCompanion.insert(
        uuid: uuid,
        description: description,
        categoryId: Value(categoryId),
        latitude: latitude,
        longitude: longitude,
        manuallyAdjustedPin: Value(manuallyAdjustedPin),
        isAnonymous: Value(isAnonymous),
      ),
    );
    return uuid;
  }

  Future<void> addMediaToReport(String reportUuid, String localFilePath, int sortOrder) {
    return into(pendingReportMedia).insert(
      PendingReportMediaCompanion.insert(
        pendingReportUuid: reportUuid,
        localFilePath: localFilePath,
        sortOrder: Value(sortOrder),
      ),
    );
  }

  Future<void> setMediaRemoteId(int mediaRowId, String remoteMediaId) {
    return (update(pendingReportMedia)..where((t) => t.id.equals(mediaRowId)))
        .write(PendingReportMediaCompanion(remoteMediaId: Value(remoteMediaId)));
  }

  Future<List<PendingReport>> watchQueueOnce() => select(pendingReports).get();

  Stream<List<PendingReport>> watchMyPendingReports() {
    return (select(pendingReports)
          ..where((t) => t.status.equalsValue(QueueStatus.synced).not())
          ..orderBy([(t) => OrderingTerm.desc(t.createdAt)]))
        .watch();
  }

  Future<List<PendingReportMediaData>> mediaFor(String reportUuid) {
    return (select(pendingReportMedia)
          ..where((t) => t.pendingReportUuid.equals(reportUuid))
          ..orderBy([(t) => OrderingTerm.asc(t.sortOrder)]))
        .get();
  }

  Future<void> updateStatus(String uuid, QueueStatus status, {String? error}) {
    return (update(pendingReports)..where((t) => t.uuid.equals(uuid))).write(
      PendingReportsCompanion(
        status: Value(status),
        lastError: Value(error),
        updatedAt: Value(DateTime.now()),
      ),
    );
  }

  Future<void> incrementAttempt(String uuid) async {
    final row = await (select(pendingReports)..where((t) => t.uuid.equals(uuid))).getSingle();
    await (update(pendingReports)..where((t) => t.uuid.equals(uuid)))
        .write(PendingReportsCompanion(attemptCount: Value(row.attemptCount + 1)));
  }

  Future<void> deleteSynced(String uuid) async {
    await (delete(pendingReportMedia)..where((t) => t.pendingReportUuid.equals(uuid))).go();
    await (delete(pendingReports)..where((t) => t.uuid.equals(uuid))).go();
  }
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'civic_report_queue.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}
