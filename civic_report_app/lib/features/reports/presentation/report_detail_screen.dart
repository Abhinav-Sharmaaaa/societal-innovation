import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/app_config.dart';
import '../../../core/widgets/status_chip.dart';
import '../data/reports_providers.dart';
import '../domain/report.dart';

class ReportDetailScreen extends ConsumerWidget {
  const ReportDetailScreen({super.key, required this.reportId});

  final String reportId;

  Future<void> _upvote(BuildContext context, WidgetRef ref) async {
    final repo = ref.read(reportsRepositoryProvider);
    try {
      await repo.upvote(reportId);
      HapticFeedback.selectionClick();
      ref.invalidate(reportDetailProvider(reportId));
    } on DioException catch (e) {
      final message = e.response?.data is Map ? e.response?.data['error'] as String? : null;
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message ?? 'Could not upvote this report.')),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reportAsync = ref.watch(reportDetailProvider(reportId));

    return Scaffold(
      appBar: AppBar(title: const Text('Report Detail')),
      body: reportAsync.when(
        data: (report) => _DetailBody(report: report, onUpvote: () => _upvote(context, ref)),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, __) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Text('Could not load this report: $error'),
          ),
        ),
      ),
    );
  }
}

class _DetailBody extends StatelessWidget {
  const _DetailBody({required this.report, required this.onUpvote});

  final Report report;
  final VoidCallback onUpvote;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (report.mediaUrls.isNotEmpty) _PhotoCarousel(urls: report.mediaUrls),
        if (report.mediaUrls.isNotEmpty) const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: Text(report.description, style: Theme.of(context).textTheme.titleMedium),
            ),
            if (report.isAnonymous)
              const Padding(
                padding: EdgeInsets.only(left: 8),
                child: Chip(
                  label: Text('Anonymous', style: TextStyle(fontSize: 11)),
                  visualDensity: VisualDensity.compact,
                ),
              ),
          ],
        ),
        const SizedBox(height: 16),
        _StatusTimeline(report: report),
        const SizedBox(height: 16),
        Row(
          children: [
            OutlinedButton.icon(
              onPressed: report.canUpvote ? onUpvote : null,
              icon: Icon(report.upvotedByMe ? Icons.check : Icons.arrow_upward),
              label: Text(
                report.isOwn
                    ? 'Upvote (${report.upvotes})'
                    : report.upvotedByMe
                        ? 'Upvoted (${report.upvotes})'
                        : 'Upvote (${report.upvotes})',
              ),
            ),
            if (report.isOwn) ...[
              const SizedBox(width: 8),
              const Text('This is your report', style: TextStyle(fontSize: 12)),
            ],
          ],
        ),
        const SizedBox(height: 16),
        Card(
          child: ListTile(
            leading: const Icon(Icons.location_on_outlined),
            title: Text('${report.latitude.toStringAsFixed(5)}, ${report.longitude.toStringAsFixed(5)}'),
            subtitle: const Text('Reported location'),
          ),
        ),
      ],
    );
  }
}

class _PhotoCarousel extends StatelessWidget {
  const _PhotoCarousel({required this.urls});

  final List<String> urls;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 220,
      child: PageView.builder(
        itemCount: urls.length,
        itemBuilder: (context, index) {
          return ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: Image.network(
              AppConfig.resolveMediaUrl(urls[index]),
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => Container(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: const Center(child: Icon(Icons.image_not_supported_outlined, size: 48)),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _StatusTimeline extends StatelessWidget {
  const _StatusTimeline({required this.report});

  final Report report;

  @override
  Widget build(BuildContext context) {
    final isRejected = report.status == 'rejected';
    final steps = isRejected ? ['submitted', 'rejected'] : Report.statusOrder;
    final currentIndex = steps.indexOf(report.status);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Status', style: Theme.of(context).textTheme.titleSmall),
        const SizedBox(height: 8),
        Row(
          children: [
            for (var i = 0; i < steps.length; i++) ...[
              _StatusDot(
                label: Report.statusLabels[steps[i]] ?? steps[i],
                filled: i <= currentIndex,
                color: StatusChip.colorFor(steps[i]),
              ),
              if (i != steps.length - 1)
                Expanded(
                  child: Container(
                    height: 2,
                    color: i < currentIndex
                        ? StatusChip.colorFor(steps[i])
                        : Theme.of(context).colorScheme.outlineVariant,
                  ),
                ),
            ],
          ],
        ),
        if (report.statusReason != null) ...[
          const SizedBox(height: 12),
          Text(
            'Reason: ${report.statusReason}',
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
      ],
    );
  }
}

class _StatusDot extends StatelessWidget {
  const _StatusDot({required this.label, required this.filled, required this.color});

  final String label;
  final bool filled;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: filled ? color : Colors.transparent,
            border: Border.all(color: color, width: 2),
          ),
        ),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(fontSize: 10)),
      ],
    );
  }
}
