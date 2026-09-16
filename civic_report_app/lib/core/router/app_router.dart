import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/splash_screen.dart';
import '../../features/notifications/presentation/notifications_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/reports/presentation/create_report_screen.dart';
import '../../features/reports/presentation/home_feed_screen.dart';
import '../../features/reports/presentation/my_reports_screen.dart';
import '../../features/reports/presentation/report_detail_screen.dart';
import '../../features/rewards/presentation/rewards_screen.dart';
import 'app_shell.dart';

abstract class AppRoutes {
  static const splash = '/';
  static const login = '/login';
  static const home = '/home';
  static const createReport = '/home/create-report';
  static const reportDetail = '/report/:id';
  static const myReports = '/my-reports';
  static const profile = '/profile';
  static const rewards = '/rewards';
  static const notifications = '/notifications';

  static String reportDetailPath(String id) => '/report/$id';
}

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: AppRoutes.splash,
    routes: [
      GoRoute(path: AppRoutes.splash, builder: (context, state) => const SplashScreen()),
      GoRoute(path: AppRoutes.login, builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: AppRoutes.reportDetail,
        builder: (context, state) => ReportDetailScreen(reportId: state.pathParameters['id']!),
      ),
      GoRoute(path: AppRoutes.myReports, builder: (context, state) => const MyReportsScreen()),
      GoRoute(path: AppRoutes.notifications, builder: (context, state) => const NotificationsScreen()),
      // Bottom-nav tabs share a shell so the nav bar persists across them.
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(path: AppRoutes.home, builder: (context, state) => const HomeFeedScreen()),
          GoRoute(path: AppRoutes.rewards, builder: (context, state) => const RewardsScreen()),
          GoRoute(path: AppRoutes.profile, builder: (context, state) => const ProfileScreen()),
        ],
      ),
      GoRoute(
        path: AppRoutes.createReport,
        builder: (context, state) => const CreateReportScreen(),
      ),
    ],
  );
});
