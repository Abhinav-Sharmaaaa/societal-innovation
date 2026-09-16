import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/providers/core_providers.dart';
import '../../../core/router/app_router.dart';
import '../../../core/storage/app_database.dart';
import '../../../core/widgets/notifications_button.dart';
import '../../../core/widgets/state_views.dart';
import '../../../core/widgets/status_chip.dart';
import '../data/reports_providers.dart';

/// Shows the user's own submissions, merged from two sources:
///  - the local Drift queue, for anything not yet confirmed synced
///    (so "pending sync" / "uploading" / "failed, will retry" is
///    always accurate even fully offline), and
///  - GET /users/me/reports, for reports the server has confirmed --
///    once a local row is marked synced it drops out of the Drift
///    query automatically, so there's no risk of the same report
///    showing twice.
class MyReportsScreen extends ConsumerWidget {
  const MyReportsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final db = ref.watch(appDatabaseProvider);
    final remoteAsync = ref.watch(myRemoteReportsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('My Reports'), actions: const [NotificationsButton()]),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(myRemoteReportsProvider),
        child: StreamBuilder<List<PendingReport>>(
          stream: db.watchMyPendingReports(),
          builder: (context, snapshot) {
            final pending = snapshot.data ?? [];

            return remoteAsync.when(
              data: (remote) {
                if (pending.isEmpty && remote.isEmpty) {
                  return LayoutBuilder(
                    builder: (context, constraints) => SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      child: SizedBox(
                        height: constraints.maxHeight,
                        child: const EmptyStateView(
                          icon: Icons.assignment_outlined,
                          message: 'No reports yet.\nTap "Report issue" on Home to get started.',
                        ),
                      ),
                    ),
                  );
                }
                return ListView(
                  padding: const EdgeInsets.all(12),
                  children: [
                    for (final r in pending) ...[
                      Card(
                        child: ListTile(
                          leading: _statusIcon(r.status),
                          title: Text(r.description, maxLines: 2, overflow: TextOverflow.ellipsis),
                          subtitle: Text(_statusLabel(r.status, r.lastError)),
                        ),
                      ),
                      const SizedBox(height: 8),
                    ],
                    for (final r in remote) ...[
                      Card(
                        child: ListTile(
                          leading: const Icon(Icons.check_circle, color: Colors.green),
                          title: Text(r.description, maxLines: 2, overflow: TextOverflow.ellipsis),
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 4),
                            child: StatusChip(status: r.status),
                          ),
                          trailing: Text('${r.upvotes} \u25B2'),
                          onTap: () => context.push(AppRoutes.reportDetailPath(r.id)),
                        ),
                      ),
                      const SizedBox(height: 8),
                    ],
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, __) => ErrorRetryView(
                message: '$error',
                onRetry: () => ref.invalidate(myRemoteReportsProvider),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _statusIcon(QueueStatus status) {
    switch (status) {
      case QueueStatus.synced:
        return const Icon(Icons.check_circle, color: Colors.green);
      case QueueStatus.failed:
        return const Icon(Icons.error, color: Colors.red);
      case QueueStatus.uploadingMedia:
      case QueueStatus.uploadingReport:
        return const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2));
      case QueueStatus.pending:
        return const Icon(Icons.cloud_upload_outlined, color: Colors.orange);
    }
  }

  String _statusLabel(QueueStatus status, String? error) {
    switch (status) {
      case QueueStatus.pending:
        return 'Pending sync -- will upload when online';
      case QueueStatus.uploadingMedia:
        return 'Uploading photos...';
      case QueueStatus.uploadingReport:
        return 'Submitting report...';
      case QueueStatus.synced:
        return 'Synced';
      case QueueStatus.failed:
        return 'Failed: ${error ?? "unknown error"} -- will retry';
    }
  }
}
