import 'package:flutter/material.dart';

/// Placeholder: status-change alerts, tap-through to report detail.
/// Populated by firebase_messaging foreground/background handlers
/// (see core/notifications setup, to be added alongside FCM token
/// registration against the backend).
class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Notifications')),
      body: const Center(child: Text('Notifications placeholder — FCM driven')),
    );
  }
}
