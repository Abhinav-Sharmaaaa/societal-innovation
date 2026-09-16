import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/widgets/notifications_button.dart';
import '../../../core/widgets/state_views.dart';
import '../../profile/data/user_provider.dart';
import '../data/rewards_provider.dart';

class RewardsScreen extends ConsumerWidget {
  const RewardsScreen({super.key});

  Future<void> _redeem(BuildContext context, WidgetRef ref, Reward reward) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Redeem reward?'),
        content: Text('Spend ${reward.pointsCost} points on "${reward.title}" at ${reward.business}?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Redeem')),
        ],
      ),
    );
    if (confirmed != true) return;

    try {
      await ref.read(rewardsRepositoryProvider).redeem(reward.id);
      ref.invalidate(userMeProvider);
      if (!context.mounted) return;
      HapticFeedback.mediumImpact();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Redeemed "${reward.title}"!')),
      );
    } on DioException catch (e) {
      if (!context.mounted) return;
      final message = e.response?.data is Map ? e.response?.data['error'] as String? : null;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message ?? 'Could not redeem this reward.')),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalogAsync = ref.watch(rewardsCatalogProvider);
    final userAsync = ref.watch(userMeProvider);
    final points = userAsync.maybeWhen(data: (u) => u.points, orElse: () => 0);

    return Scaffold(
      appBar: AppBar(title: const Text('Rewards'), actions: const [NotificationsButton()]),
      body: catalogAsync.when(
        data: (rewards) {
          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(rewardsCatalogProvider);
              ref.invalidate(userMeProvider);
            },
            child: ListView(
              padding: const EdgeInsets.all(12),
              children: [
                Card(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Row(
                      children: [
                        Icon(Icons.stars_rounded, size: 32, color: Theme.of(context).colorScheme.onPrimaryContainer),
                        const SizedBox(width: 16),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '$points points',
                              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            Text(
                              'Earned from confirmed reports',
                              style: TextStyle(color: Theme.of(context).colorScheme.onPrimaryContainer),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                if (rewards.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 24),
                    child: EmptyStateView(
                      icon: Icons.card_giftcard_outlined,
                      message: 'No rewards available right now.\nCheck back soon.',
                    ),
                  )
                else
                  ...rewards.map((reward) {
                    final affordable = points >= reward.pointsCost;
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Card(
                        child: ListTile(
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          leading: CircleAvatar(
                            backgroundColor: affordable
                                ? Theme.of(context).colorScheme.primaryContainer
                                : Theme.of(context).colorScheme.surfaceContainerHighest,
                            child: Icon(
                              Icons.card_giftcard,
                              color: affordable
                                  ? Theme.of(context).colorScheme.onPrimaryContainer
                                  : Theme.of(context).colorScheme.outline,
                            ),
                          ),
                          title: Text(reward.title),
                          subtitle: Text('${reward.business} \u00b7 ${reward.pointsCost} pts'),
                          trailing: FilledButton(
                            onPressed: affordable ? () => _redeem(context, ref, reward) : null,
                            child: const Text('Redeem'),
                          ),
                        ),
                      ),
                    );
                  }),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, __) => ErrorRetryView(
          message: '$error',
          onRetry: () => ref.invalidate(rewardsCatalogProvider),
        ),
      ),
    );
  }
}
