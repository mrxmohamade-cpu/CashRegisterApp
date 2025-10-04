import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/models/user_model.dart';
import '../core/models/user_role.dart';
import '../features/admin/view/admin_dashboard_screen.dart';
import '../features/auth/providers/auth_controller.dart';
import '../features/auth/view/login_screen.dart';
import '../features/user/view/user_dashboard_screen.dart';

enum AppRoute {
  login,
  userDashboard,
  adminDashboard,
}

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authControllerProvider);

  return GoRouter(
    initialLocation: '/login',
    refreshListenable: GoRouterRefreshStream(
      ref.watch(authControllerProvider.notifier).stream,
    ),
    redirect: (context, state) {
      final isLoggingIn = state.matchedLocation == '/login';
      final user = authState.user;
      if (user == null) {
        return isLoggingIn ? null : '/login';
      }
      if (isLoggingIn) {
        return user.isAdmin ? '/admin' : '/user';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        name: AppRoute.login.name,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/user',
        name: AppRoute.userDashboard.name,
        builder: (context, state) {
          final user = ref.read(currentUserProvider) ?? const UserModel(username: 'زائر', hashedPassword: '', role: UserRole.user);
          return UserDashboardScreen(user: user);
        },
      ),
      GoRoute(
        path: '/admin',
        name: AppRoute.adminDashboard.name,
        builder: (context, state) => const AdminDashboardScreen(),
      ),
    ],
  );
});

class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream(Stream<dynamic> stream) {
    notifyListeners();
    _subscription = stream.asBroadcastStream().listen((_) {
      notifyListeners();
    });
  }

  late final StreamSubscription<dynamic> _subscription;

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}
