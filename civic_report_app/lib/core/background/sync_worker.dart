import 'package:workmanager/workmanager.dart';

import '../../features/reports/data/report_sync_service.dart';
import '../config/app_config.dart';

/// Top-level callback dispatcher required by Workmanager — runs in its
/// own background isolate, so it cannot see the app's Riverpod state and
/// must build its own dependencies (handled inside ReportSyncService).
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    if (task == AppConfig.pendingSyncTaskName) {
      final service = ReportSyncService();
      final allSettled = await service.drainQueue();
      // Returning false tells Workmanager to reschedule/retry per its
      // backoff policy when items are still pending.
      return allSettled;
    }
    return true;
  });
}

class BackgroundSync {
  static Future<void> initialize() async {
    await Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
  }

  /// Schedules a one-off retry attempt as soon as network constraints
  /// are satisfied — call this right after queueing a report so the
  /// system doesn't wait for the next periodic window.
  static Future<void> scheduleOneOff() async {
    await Workmanager().registerOneOffTask(
      '${AppConfig.pendingSyncTaskName}_oneoff_${DateTime.now().millisecondsSinceEpoch}',
      AppConfig.pendingSyncTaskName,
      constraints: Constraints(networkType: NetworkType.connected),
      existingWorkPolicy: ExistingWorkPolicy.append,
      backoffPolicy: BackoffPolicy.exponential,
      backoffPolicyDelay: const Duration(seconds: 30),
    );
  }

  /// Periodic safety net in case a one-off task is missed (app killed
  /// before it fires, etc). 15 minutes is the Workmanager Android floor.
  static Future<void> schedulePeriodic() async {
    await Workmanager().registerPeriodicTask(
      AppConfig.pendingSyncTaskName,
      AppConfig.pendingSyncTaskName,
      frequency: const Duration(minutes: 15),
      constraints: Constraints(networkType: NetworkType.connected),
      backoffPolicy: BackoffPolicy.exponential,
      backoffPolicyDelay: const Duration(minutes: 1),
    );
  }
}
