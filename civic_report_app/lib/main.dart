import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/background/sync_worker.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ASSUMPTION: Firebase is initialized here once firebase_options.dart
  // exists (via `flutterfire configure`). Left out for now since it
  // requires a real Firebase project — push notifications are wired up
  // to a no-op until then. Uncomment once configured:
  // await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  await BackgroundSync.initialize();
  await BackgroundSync.schedulePeriodic();

  runApp(const ProviderScope(child: CivicReportApp()));
}

class CivicReportApp extends ConsumerWidget {
  const CivicReportApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Civic Report',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.system,
      routerConfig: router,
    );
  }
}
