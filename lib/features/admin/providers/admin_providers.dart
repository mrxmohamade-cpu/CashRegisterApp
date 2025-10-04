import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/admin_metrics.dart';
import '../../../core/models/cash_session_model.dart';
import '../../../core/models/user_model.dart';
import '../../../core/utils/app_providers.dart';

enum AdminFilter {
  currentMonth,
  previousMonth,
  last7Days,
  last30Days,
}

class AdminDashboardState {
  AdminDashboardState({
    this.filter = AdminFilter.currentMonth,
    DateTimeRange? range,
    DateTime? selectedMonth,
    this.selectedUserId,
    this.showTimes = true,
  })  : range = range ?? _calculateRange(filter),
        selectedMonth = selectedMonth ?? DateTime(DateTime.now().year, DateTime.now().month);

  final AdminFilter filter;
  final DateTimeRange range;
  final DateTime selectedMonth;
  final int? selectedUserId;
  final bool showTimes;

  AdminDashboardState copyWith({
    AdminFilter? filter,
    DateTimeRange? range,
    DateTime? selectedMonth,
    int? selectedUserId,
    bool? showTimes,
  }) {
    final newFilter = filter ?? this.filter;
    return AdminDashboardState(
      filter: newFilter,
      range: range ?? (filter != null ? _calculateRange(newFilter) : this.range),
      selectedMonth: selectedMonth ?? this.selectedMonth,
      selectedUserId: selectedUserId ?? this.selectedUserId,
      showTimes: showTimes ?? this.showTimes,
    );
  }

  static DateTimeRange _calculateRange(AdminFilter filter) {
    final now = DateTime.now();
    switch (filter) {
      case AdminFilter.currentMonth:
        final start = DateTime(now.year, now.month, 1);
        final end = DateTime(now.year, now.month + 1, 0, 23, 59, 59);
        return DateTimeRange(start: start, end: end);
      case AdminFilter.previousMonth:
        final prev = DateTime(now.year, now.month - 1, 1);
        final end = DateTime(now.year, now.month, 0, 23, 59, 59);
        return DateTimeRange(start: prev, end: end);
      case AdminFilter.last7Days:
        final start = now.subtract(const Duration(days: 7));
        return DateTimeRange(start: start, end: now);
      case AdminFilter.last30Days:
        final start = now.subtract(const Duration(days: 30));
        return DateTimeRange(start: start, end: now);
    }
  }
}

class AdminDashboardController extends StateNotifier<AdminDashboardState> {
  AdminDashboardController() : super(AdminDashboardState());

  void changeFilter(AdminFilter filter) {
    state = state.copyWith(filter: filter);
  }

  void selectUser(int? userId) {
    state = state.copyWith(selectedUserId: userId);
  }

  void changeMonth(DateTime month) {
    state = state.copyWith(selectedMonth: month);
  }

  void toggleShowTimes(bool value) {
    state = state.copyWith(showTimes: value);
  }

  void setCustomRange(DateTimeRange range) {
    state = state.copyWith(range: range);
  }
}

final adminDashboardControllerProvider =
    StateNotifierProvider<AdminDashboardController, AdminDashboardState>((ref) {
  return AdminDashboardController();
});

final adminMetricsProvider = FutureProvider<AdminDashboardMetrics>((ref) async {
  final state = ref.watch(adminDashboardControllerProvider);
  final repository = ref.watch(adminRepositoryProvider);
  return repository.loadMetrics(from: state.range.start, to: state.range.end);
});

final adminSessionsProvider = FutureProvider<List<CashSessionModel>>((ref) async {
  final state = ref.watch(adminDashboardControllerProvider);
  final repository = ref.watch(adminRepositoryProvider);
  return repository.fetchSessions(
    userId: state.selectedUserId,
    from: state.range.start,
    to: state.range.end,
  );
});

final adminUsersProvider = StreamProvider<List<UserModel>>((ref) {
  final repository = ref.watch(userRepositoryProvider);
  return repository.watchUsers();
});

final adminMonthlyExpensesProvider = FutureProvider<Map<DateTime, double>>((ref) async {
  final state = ref.watch(adminDashboardControllerProvider);
  final selectedUser = state.selectedUserId;
  if (selectedUser == null) {
    return {};
  }
  final repository = ref.watch(adminRepositoryProvider);
  return repository.loadDailyExpenses(userId: selectedUser, month: state.selectedMonth);
});

final adminSessionSummaryProvider = FutureProvider.family((ref, int sessionId) {
  final repository = ref.watch(adminRepositoryProvider);
  return repository.sessionSummary(sessionId);
});

final showTimesProvider = Provider<bool>((ref) {
  return ref.watch(adminDashboardControllerProvider).showTimes;
});

