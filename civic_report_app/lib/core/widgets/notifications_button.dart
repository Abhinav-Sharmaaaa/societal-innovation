import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../router/app_router.dart';

/// Top-bar bell icon that takes the place of the old Notifications
/// bottom-nav tab. Drop this into the `actions` of any screen's AppBar.
class NotificationsButton extends StatelessWidget {
  const NotificationsButton({super.key});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.notifications_outlined),
      tooltip: 'Notifications',
      onPressed: () => context.push(AppRoutes.notifications),
    );
  }
}
