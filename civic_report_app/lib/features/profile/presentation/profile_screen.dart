import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/providers/core_providers.dart';
import '../../../core/router/app_router.dart';
import '../../../core/widgets/notifications_button.dart';
import '../data/user_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  Future<void> _signOut(BuildContext context, WidgetRef ref) async {
    final tokenStorage = ref.read(tokenStorageProvider);
    await tokenStorage.clear();
    if (!context.mounted) return;
    context.go(AppRoutes.login);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userMeProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Profile'), actions: const [NotificationsButton()]),
      body: userAsync.when(
        data: (user) => ListView(
          children: [
            const SizedBox(height: 16),
            CircleAvatar(
              radius: 32,
              child: Text(
                user.email.isNotEmpty ? user.email[0].toUpperCase() : '?',
                style: const TextStyle(fontSize: 28),
              ),
            ),
            const SizedBox(height: 8),
            Center(child: Text(user.email, style: Theme.of(context).textTheme.titleMedium)),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.stars_outlined),
              title: const Text('Points balance'),
              trailing: Text('${user.points}', style: Theme.of(context).textTheme.titleMedium),
            ),
            ListTile(
              leading: const Icon(Icons.upload_file_outlined),
              title: const Text('My submissions'),
              subtitle: const Text('Sync status for reports you\'ve created'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.push(AppRoutes.myReports),
            ),
            const ListTile(
              leading: Icon(Icons.military_tech_outlined),
              title: Text('Badges'),
              subtitle: Text('Coming soon'),
            ),
            SwitchListTile(
              secondary: const Icon(Icons.visibility_off_outlined),
              title: const Text('Default to anonymous reporting'),
              // Read-only for now -- persisting this requires a
              // PATCH /users/me endpoint not in the original spec.
              value: user.isAnonymousDefault,
              onChanged: null,
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Sign out'),
              onTap: () => _signOut(context, ref),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, __) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Could not load profile: $error'),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () => _signOut(context, ref),
                  child: const Text('Sign out'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
