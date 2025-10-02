import 'dart:ui' as ui show TextDirection;

import 'package:data_table_2/data_table_2.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/admin_metrics.dart';
import '../../../core/models/cash_session_model.dart';
import '../../../core/models/user_model.dart';
import '../../../core/models/user_role.dart';
import '../../../core/utils/formatters.dart';
import '../../auth/providers/auth_controller.dart';
import '../../../core/utils/app_providers.dart';
import '../providers/admin_providers.dart';

class AdminDashboardScreen extends ConsumerWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(adminDashboardControllerProvider);
    final metricsAsync = ref.watch(adminMetricsProvider);
    final sessionsAsync = ref.watch(adminSessionsProvider);
    final usersAsync = ref.watch(adminUsersProvider);
    final showTimes = ref.watch(showTimesProvider);

    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 1000) {
          return DefaultTabController(
            length: 4,
            child: Scaffold(
              appBar: AppBar(
                title: const Text('لوحة المشرف'),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.logout),
                    onPressed: () => ref.read(authControllerProvider.notifier).logout(),
                    tooltip: 'تسجيل الخروج',
                  ),
                ],
                bottom: const TabBar(
                  isScrollable: true,
                  tabs: [
                    Tab(icon: Icon(Icons.dashboard_customize), text: 'نظرة عامة'),
                    Tab(icon: Icon(Icons.table_chart), text: 'الجلسات'),
                    Tab(icon: Icon(Icons.people_alt), text: 'العمال'),
                    Tab(icon: Icon(Icons.settings), text: 'إعدادات'),
                  ],
                ),
              ),
              body: TabBarView(
                children: [
                  _buildOverviewTab(ref, state, metricsAsync),
                  _buildSessionsTab(ref, sessionsAsync, showTimes),
                  _buildWorkersTab(ref, usersAsync),
                  _buildSettingsTab(ref, showTimes),
                ],
              ),
            ),
          );
        }

        return Scaffold(
          appBar: AppBar(
            title: const Text('لوحة المشرف'),
            actions: [
              TextButton.icon(
                onPressed: () => ref.read(authControllerProvider.notifier).logout(),
                icon: const Icon(Icons.logout),
                label: const Text('خروج'),
              ),
            ],
          ),
          body: _buildDesktopBody(ref, state, metricsAsync, usersAsync, sessionsAsync, showTimes),
        );
      },
    );
  }

  Widget _buildDesktopBody(
    WidgetRef ref,
    AdminDashboardState state,
    AsyncValue<AdminDashboardMetrics> metricsAsync,
    AsyncValue<List<UserModel>> usersAsync,
    AsyncValue<List<CashSessionModel>> sessionsAsync,
    bool showTimes,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _FilterBar(state: state),
          const SizedBox(height: 16),
          metricsAsync.when(
            data: (metrics) => _MetricsGrid(metrics: metrics),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => Text('تعذر تحميل الإحصائيات: $error'),
          ),
          const SizedBox(height: 16),
          _UserManagementSection(usersAsync: usersAsync),
          const SizedBox(height: 16),
          _SessionsReportSection(sessionsAsync: sessionsAsync, showTimes: showTimes),
          const SizedBox(height: 16),
          _WorkerProfileSection(usersAsync: usersAsync),
          const SizedBox(height: 16),
          Card(
            child: SwitchListTile(
              title: const Text('عرض أوقات الفتح والغلق في التقرير'),
              value: showTimes,
              onChanged: (value) => ref.read(adminDashboardControllerProvider.notifier).toggleShowTimes(value),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewTab(
    WidgetRef ref,
    AdminDashboardState state,
    AsyncValue<AdminDashboardMetrics> metricsAsync,
  ) {
    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(adminMetricsProvider);
        ref.invalidate(adminSessionsProvider);
        await ref.read(adminMetricsProvider.future);
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          _FilterBar(state: state),
          const SizedBox(height: 16),
          metricsAsync.when(
            data: (metrics) => _MetricsGrid(metrics: metrics),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => Text('تعذر تحميل الإحصائيات: $error'),
          ),
        ],
      ),
    );
  }

  Widget _buildSessionsTab(
    WidgetRef ref,
    AsyncValue<List<CashSessionModel>> sessionsAsync,
    bool showTimes,
  ) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _SessionsReportSection(sessionsAsync: sessionsAsync, showTimes: showTimes),
      ],
    );
  }

  Widget _buildWorkersTab(
    WidgetRef ref,
    AsyncValue<List<UserModel>> usersAsync,
  ) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _UserManagementSection(usersAsync: usersAsync),
        const SizedBox(height: 16),
        _WorkerProfileSection(usersAsync: usersAsync),
      ],
    );
  }

  Widget _buildSettingsTab(
    WidgetRef ref,
    bool showTimes,
  ) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: SwitchListTile(
            title: const Text('عرض أوقات الفتح والغلق في التقرير'),
            value: showTimes,
            onChanged: (value) => ref.read(adminDashboardControllerProvider.notifier).toggleShowTimes(value),
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('حول لوحة التحكم'),
            subtitle: const Text('واجهة متجاوبة محسّنة للهواتف لإدارة الصندوق بسهولة.'),
          ),
        ),
      ],
    );
  }
}

class _FilterBar extends ConsumerWidget {
  const _FilterBar({required this.state});

  final AdminDashboardState state;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(adminUsersProvider);

    return Wrap(
      spacing: 12,
      runSpacing: 12,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        DropdownButton<AdminFilter>(
          value: state.filter,
          items: AdminFilter.values
              .map(
                (filter) => DropdownMenuItem(
                  value: filter,
                  child: Text(_filterLabel(filter)),
                ),
              )
              .toList(),
          onChanged: (filter) {
            if (filter != null) {
              ref.read(adminDashboardControllerProvider.notifier).changeFilter(filter);
            }
          },
        ),
        usersAsync.when(
          data: (users) {
            final workers = users.where((user) => user.role == UserRole.user).toList();
            return SizedBox(
              width: 220,
              child: DropdownButton<int?>(
                isExpanded: true,
                hint: const Text('اختيار عامل'),
                value: state.selectedUserId,
                items: [
                  const DropdownMenuItem(value: null, child: Text('الكل')),
                  ...workers.map(
                    (user) => DropdownMenuItem(value: user.id, child: Text(user.username)),
                  ),
                ],
                onChanged: (value) =>
                    ref.read(adminDashboardControllerProvider.notifier).selectUser(value),
              ),
            );
          },
          loading: () => const CircularProgressIndicator(),
          error: (error, _) => Text('خطأ في تحميل المستخدمين: $error'),
        ),
        OutlinedButton.icon(
          onPressed: () async {
            final picked = await showDateRangePicker(
              context: context,
              firstDate: DateTime(2022),
              lastDate: DateTime.now().add(const Duration(days: 365)),
              initialDateRange: state.range,
              builder: (context, child) => Directionality(
                textDirection: ui.TextDirection.rtl,
                child: child ?? const SizedBox.shrink(),
              ),
            );
            if (picked != null) {
              ref.read(adminDashboardControllerProvider.notifier).setCustomRange(picked);
            }
          },
          icon: const Icon(Icons.date_range),
          label: const Text('تحديد فترة مخصصة'),
        ),
      ],
    );
  }

  String _filterLabel(AdminFilter filter) {
    switch (filter) {
      case AdminFilter.currentMonth:
        return 'الشهر الحالي';
      case AdminFilter.previousMonth:
        return 'الشهر الماضي';
      case AdminFilter.last7Days:
        return 'آخر 7 أيام';
      case AdminFilter.last30Days:
        return 'آخر 30 يومًا';
    }
  }
}

class _MetricsGrid extends StatelessWidget {
  const _MetricsGrid({required this.metrics});

  final AdminDashboardMetrics metrics;

  @override
  Widget build(BuildContext context) {
    final items = [
      _MetricTile('عدد الجلسات', metrics.sessionCount.toDouble()),
      _MetricTile('مجموع المصاريف', metrics.totalExpenses),
      _MetricTile('مجموع إضافات الفليكسي', metrics.totalFlexiAdditions),
      _MetricTile('صافي الفرق النقدي', metrics.netCashDifference),
      _MetricTile('الفليكسي المستهلك', metrics.flexiConsumed),
    ];
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: items
          .map(
            (item) => SizedBox(
              width: 220,
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(item.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Text(
                        item.isCount
                            ? Formatters.formatNumber(item.value)
                            : Formatters.formatCurrency(item.value),
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          )
          .toList(),
    );
  }
}

class _MetricTile {
  const _MetricTile(this.title, this.value, {bool isCountValue = false})
      : isCount = isCountValue;

  final String title;
  final double value;
  final bool isCount;
}

class _UserManagementSection extends ConsumerWidget {
  const _UserManagementSection({required this.usersAsync});

  final AsyncValue<List<UserModel>> usersAsync;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formKey = GlobalKey<FormState>();
    final usernameController = TextEditingController();
    final passwordController = TextEditingController();
    UserRole role = UserRole.user;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('إدارة العمال', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            usersAsync.when(
              data: (users) {
                return Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Form(
                            key: formKey,
                            child: Wrap(
                              spacing: 12,
                              runSpacing: 12,
                              children: [
                                SizedBox(
                                  width: 200,
                                  child: TextFormField(
                                    controller: usernameController,
                                    decoration: const InputDecoration(labelText: 'اسم المستخدم'),
                                    validator: (value) =>
                                        value == null || value.isEmpty ? 'إلزامي' : null,
                                  ),
                                ),
                                SizedBox(
                                  width: 200,
                                  child: TextFormField(
                                    controller: passwordController,
                                    decoration: const InputDecoration(labelText: 'كلمة المرور'),
                                    validator: (value) =>
                                        value == null || value.isEmpty ? 'إلزامي' : null,
                                  ),
                                ),
                                DropdownButton<UserRole>(
                                  value: role,
                                  items: UserRole.values
                                      .map(
                                        (item) => DropdownMenuItem(
                                          value: item,
                                          child: Text(item.displayName),
                                        ),
                                      )
                                      .toList(),
                                  onChanged: (value) {
                                    if (value != null) {
                                      role = value;
                                    }
                                  },
                                ),
                                FilledButton(
                                  onPressed: () async {
                                    if (formKey.currentState!.validate()) {
                                      await ref.read(userRepositoryProvider).createUser(
                                            username: usernameController.text,
                                            password: passwordController.text,
                                            role: role,
                                          );
                                      usernameController.clear();
                                      passwordController.clear();
                                    }
                                  },
                                  child: const Text('إضافة مستخدم'),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    DataTable2(
                      columnSpacing: 12,
                      columns: const [
                        DataColumn(label: Text('المعرف')),
                        DataColumn(label: Text('الاسم')),
                        DataColumn(label: Text('الدور')),
                        DataColumn(label: Text('إجراءات')),
                      ],
                      rows: users
                          .map(
                            (user) => DataRow(
                              cells: [
                                DataCell(Text('${user.id}')),
                                DataCell(Text(user.username)),
                                DataCell(Text(user.role.displayName)),
                                DataCell(Row(
                                  children: [
                                    IconButton(
                                      icon: const Icon(Icons.password),
                                      tooltip: 'إعادة تعيين كلمة المرور',
                                      onPressed: () => _resetPassword(context, ref, user),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.delete_outline),
                                      tooltip: 'حذف المستخدم',
                                      onPressed: () => _deleteUser(context, ref, user),
                                    ),
                                  ],
                                )),
                              ],
                            ),
                          )
                          .toList(),
                    ),
                  ],
                );
              },
              loading: () => const CircularProgressIndicator(),
              error: (error, _) => Text('تعذر تحميل المستخدمين: $error'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _resetPassword(BuildContext context, WidgetRef ref, UserModel user) async {
    final formKey = GlobalKey<FormState>();
    final newPasswordController = TextEditingController();
    final adminPasswordController = TextEditingController();
    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('إعادة تعيين كلمة المرور لـ ${user.username}'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: newPasswordController,
                  decoration: const InputDecoration(labelText: 'كلمة المرور الجديدة'),
                  validator: (value) =>
                      value == null || value.isEmpty ? 'أدخل كلمة المرور الجديدة' : null,
                ),
                TextFormField(
                  controller: adminPasswordController,
                  decoration: const InputDecoration(labelText: 'كلمة مرور المشرف للتأكيد'),
                  validator: (value) => value == null || value.isEmpty ? 'إلزامي' : null,
                  obscureText: true,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('إلغاء')),
            FilledButton(
              onPressed: () {
                if (formKey.currentState!.validate()) {
                  Navigator.pop(context, true);
                }
              },
              child: const Text('تأكيد'),
            ),
          ],
        );
      },
    );
    if (!context.mounted) {
      return;
    }
    if (result == true) {
      final authUser = ref.read(currentUserProvider);
      final isValid = await ref.read(userRepositoryProvider).confirmAdminPassword(
            authUser!.username,
            adminPasswordController.text,
          );
      if (!context.mounted) {
        return;
      }
      if (!isValid) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('كلمة مرور المشرف غير صحيحة')),
        );
        return;
      }
      await ref.read(userRepositoryProvider).updateUser(user, newPassword: newPasswordController.text);
      if (!context.mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('تم تحديث كلمة مرور ${user.username}')),
      );
    }
  }

  Future<void> _deleteUser(BuildContext context, WidgetRef ref, UserModel user) async {
    final adminPasswordController = TextEditingController();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('حذف المستخدم ${user.username}'),
          content: TextField(
            controller: adminPasswordController,
            decoration: const InputDecoration(labelText: 'أدخل كلمة مرور المشرف للتأكيد'),
            obscureText: true,
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('إلغاء')),
            FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('حذف')),
          ],
        );
      },
    );
    if (!context.mounted) {
      return;
    }
    if (confirmed == true) {
      final authUser = ref.read(currentUserProvider);
      final isValid = await ref.read(userRepositoryProvider).confirmAdminPassword(
            authUser!.username,
            adminPasswordController.text,
          );
      if (!context.mounted) {
        return;
      }
      if (!isValid) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('كلمة مرور المشرف غير صحيحة')),
        );
        return;
      }
      await ref.read(userRepositoryProvider).deleteUser(user.id!);
      if (!context.mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('تم حذف ${user.username}')),
      );
    }
  }
}

class _SessionsReportSection extends ConsumerWidget {
  const _SessionsReportSection({required this.sessionsAsync, required this.showTimes});

  final AsyncValue<List<CashSessionModel>> sessionsAsync;
  final bool showTimes;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('تقرير الجلسات', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            sessionsAsync.when(
              data: (sessions) {
                return DataTable2(
                  columnSpacing: 12,
                  columns: [
                    const DataColumn(label: Text('العامل')),
                    if (showTimes) const DataColumn(label: Text('وقت الفتح')),
                    if (showTimes) const DataColumn(label: Text('وقت الغلق')),
                    const DataColumn(label: Text('رصيد البداية')),
                    const DataColumn(label: Text('رصيد النهاية')),
                    const DataColumn(label: Text('الفرق')),
                    const DataColumn(label: Text('الفليكسي')),
                  ],
                  rows: sessions
                      .map(
                        (session) => DataRow(
                          cells: [
                            DataCell(Text('${session.userId}')),
                            if (showTimes)
                              DataCell(Text(Formatters.formatDate(session.startTime))),
                            if (showTimes)
                              DataCell(Text(
                                session.endTime == null
                                    ? '---'
                                    : Formatters.formatDate(session.endTime!),
                              )),
                            DataCell(Text(Formatters.formatCurrency(session.startBalance))),
                            DataCell(Text(Formatters.formatCurrency(session.endBalance ?? session.startBalance))),
                            DataCell(Text(
                              Formatters.formatCurrency(
                                (session.endBalance ?? session.startBalance) - session.startBalance,
                              ),
                            )),
                            DataCell(Text(
                              '${Formatters.formatCurrency(session.startFlexi)} → ${Formatters.formatCurrency(session.endFlexi ?? session.startFlexi)}',
                            )),
                          ],
                        ),
                      )
                      .toList(),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Text('تعذر تحميل الجلسات: $error'),
            ),
          ],
        ),
      ),
    );
  }
}

class _WorkerProfileSection extends ConsumerWidget {
  const _WorkerProfileSection({required this.usersAsync});

  final AsyncValue<List<UserModel>> usersAsync;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(adminDashboardControllerProvider);
    final expensesAsync = ref.watch(adminMonthlyExpensesProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('ملف العامل', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: usersAsync.when(
                    data: (users) {
                      final workers = users.where((user) => user.role == UserRole.user).toList();
                      return DropdownButton<int?>(
                        isExpanded: true,
                        hint: const Text('اختر العامل'),
                        value: state.selectedUserId,
                        items: [
                          const DropdownMenuItem(value: null, child: Text('الكل')),
                          ...workers.map(
                            (user) => DropdownMenuItem(value: user.id, child: Text(user.username)),
                          ),
                        ],
                        onChanged: (value) =>
                            ref.read(adminDashboardControllerProvider.notifier).selectUser(value),
                      );
                    },
                    loading: () => const CircularProgressIndicator(),
                    error: (error, _) => Text('خطأ: $error'),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton(
                  onPressed: () async {
                    final picked = await showMonthPicker(
                      context: context,
                      initialDate: state.selectedMonth,
                    );
                    if (picked != null) {
                      ref.read(adminDashboardControllerProvider.notifier).changeMonth(picked);
                    }
                  },
                  child: Text('الشهر: ${state.selectedMonth.month}/${state.selectedMonth.year}'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            expensesAsync.when(
              data: (data) {
                if (data.isEmpty) {
                  return const Text('اختر عاملًا لعرض بياناته.');
                }
                return SizedBox(
                  height: 200,
                  child: BarChart(
                    BarChartData(
                      alignment: BarChartAlignment.spaceAround,
                      titlesData: FlTitlesData(
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            getTitlesWidget: (value, meta) {
                              final index = value.toInt();
                              if (index < 0 || index >= data.length) {
                                return const SizedBox.shrink();
                              }
                              final date = data.keys.elementAt(index);
                              return Text('${date.day}');
                            },
                          ),
                        ),
                      ),
                      barGroups: [
                        for (int i = 0; i < data.length; i++)
                          BarChartGroupData(
                            x: i,
                            barRods: [
                              BarChartRodData(toY: data.values.elementAt(i), color: Colors.teal),
                            ],
                          ),
                      ],
                    ),
                  ),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Text('خطأ في تحميل بيانات المصاريف: $error'),
            ),
          ],
        ),
      ),
    );
  }
}

Future<DateTime?> showMonthPicker({required BuildContext context, required DateTime initialDate}) async {
  DateTime tempDate = initialDate;
  final result = await showDialog<DateTime>(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: const Text('اختر الشهر'),
        content: SizedBox(
          height: 250,
          width: 300,
          child: CalendarDatePicker(
            initialDate: tempDate,
            firstDate: DateTime(2020),
            lastDate: DateTime(DateTime.now().year + 1),
            onDateChanged: (value) => tempDate = DateTime(value.year, value.month),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('إلغاء')),
          FilledButton(onPressed: () => Navigator.pop(context, tempDate), child: const Text('اختيار')),
        ],
      );
    },
  );
  return result;
}
