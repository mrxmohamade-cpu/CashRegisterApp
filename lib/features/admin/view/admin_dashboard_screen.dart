import 'dart:ui' as ui show TextDirection;

import 'package:data_table_2/data_table_2.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/admin_metrics.dart';
import '../../../core/models/cash_session_model.dart';
import '../../../core/models/user_model.dart';
import '../../../core/models/user_role.dart';
import '../../../core/models/session_status.dart';
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
            child: SwitchListTile.adaptive(
              title: const Text('عرض أوقات الفتح والغلق في التقرير'),
              value: showTimes,
              onChanged: (value) => ref
                  .read(adminDashboardControllerProvider.notifier)
                  .toggleShowTimes(value),
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
          child: SwitchListTile.adaptive(
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

class _SessionReportTile extends StatelessWidget {
  const _SessionReportTile({
    required this.session,
    required this.user,
    required this.showTimes,
    this.onDetails,
  });

  final CashSessionModel session;
  final UserModel? user;
  final bool showTimes;
  final VoidCallback? onDetails;

  @override
  Widget build(BuildContext context) {
    final endBalance = session.endBalance ?? session.startBalance;
    final cashDifference = endBalance - session.startBalance;
    final endFlexi = session.endFlexi ?? session.startFlexi;
    final flexiMovement = endFlexi - session.startFlexi;
    final userName = user?.username ?? 'مستخدم #${session.userId}';

    return Card(
      margin: EdgeInsets.zero,
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        userName,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.w600),
                      ),
                      if (showTimes) ...[
                        const SizedBox(height: 6),
                        Text(
                          'الفتح: ${Formatters.formatDate(session.startTime)}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        Text(
                          'الإغلاق: ${session.endTime == null ? '---' : Formatters.formatDate(session.endTime!)}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ],
                  ),
                ),
                _StatusChip(status: session.status),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _InfoBadge(
                  icon: Icons.account_balance_wallet_outlined,
                  label: 'رصيد البداية',
                  value: Formatters.formatCurrency(session.startBalance),
                ),
                _InfoBadge(
                  icon: Icons.savings_outlined,
                  label: 'رصيد النهاية',
                  value: Formatters.formatCurrency(endBalance),
                ),
                _InfoBadge(
                  icon: Icons.trending_up,
                  label: 'الفرق النقدي',
                  value: Formatters.formatCurrency(cashDifference),
                ),
                _InfoBadge(
                  icon: Icons.swap_horiz,
                  label: 'الفليكسي',
                  value:
                      '${Formatters.formatCurrency(session.startFlexi)} → ${Formatters.formatCurrency(endFlexi)} (${Formatters.formatCurrency(flexiMovement)})',
                  maxLines: 2,
                ),
              ],
            ),
            if (session.notes?.isNotEmpty == true) ...[
              const SizedBox(height: 12),
              Text(
                'ملاحظات: ${session.notes!}',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
            if (onDetails != null) ...[
              const SizedBox(height: 12),
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: TextButton.icon(
                  onPressed: onDetails,
                  icon: const Icon(Icons.info_outline),
                  label: const Text('عرض التفاصيل'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _InfoBadge extends StatelessWidget {
  const _InfoBadge({
    required this.icon,
    required this.label,
    required this.value,
    this.maxLines = 1,
  });

  final IconData icon;
  final String label;
  final String value;
  final int maxLines;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ConstrainedBox(
      constraints: const BoxConstraints(minWidth: 120, maxWidth: 220),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: theme.colorScheme.primaryContainer.withValues(alpha: 0.14),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(icon, size: 18, color: theme.colorScheme.primary),
                  const SizedBox(width: 6),
                  Flexible(
                    child: Text(
                      label,
                      style: theme.textTheme.labelMedium
                          ?.copyWith(color: theme.colorScheme.primary),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                value,
                maxLines: maxLines,
                overflow: TextOverflow.ellipsis,
                style:
                    theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ),
      ),
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

class _AdminSectionCard extends StatelessWidget {
  const _AdminSectionCard({
    this.title,
    this.actions,
    required this.child,
    this.padding,
  });

  final String? title;
  final List<Widget>? actions;
  final Widget child;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final headerActions = actions?.whereType<Widget>().toList() ?? const [];
    final hasHeader = title != null || headerActions.isNotEmpty;

    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: padding ?? const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (hasHeader) ...[
              Row(
                children: [
                  if (title != null)
                    Expanded(
                      child: Text(
                        title!,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    )
                  else
                    const Spacer(),
                  ...headerActions,
                ],
              ),
              const SizedBox(height: 12),
            ],
            child,
          ],
        ),
      ),
    );
  }
}

class _MetricsGrid extends StatelessWidget {
  const _MetricsGrid({required this.metrics});

  final AdminDashboardMetrics metrics;

  @override
  Widget build(BuildContext context) {
    final tiles = <_MetricTileData>[
      _MetricTileData('عدد الجلسات', metrics.sessionCount.toDouble(), isCount: true),
      _MetricTileData('مجموع المصاريف', metrics.totalExpenses),
      _MetricTileData('مجموع إضافات الفليكسي', metrics.totalFlexiAdditions),
      _MetricTileData('صافي الفرق النقدي', metrics.netCashDifference),
      _MetricTileData('الفليكسي المستهلك', metrics.flexiConsumed),
    ];

    return LayoutBuilder(
      builder: (context, constraints) {
        final maxWidth = constraints.maxWidth;
        final columnCount = maxWidth < 420
            ? 1
            : maxWidth < 760
                ? 2
                : maxWidth < 1080
                    ? 3
                    : 4;
        final cardHeight = columnCount == 1 ? 132.0 : 120.0;

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: tiles.length,
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columnCount,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: columnCount == 1 ? 2.6 : 2.2,
          ),
          itemBuilder: (context, index) {
            final tile = tiles[index];
            return Card(
              elevation: 1,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: SizedBox(
                  height: cardHeight,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        tile.title,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        tile.isCount
                            ? Formatters.formatNumber(tile.value)
                            : Formatters.formatCurrency(tile.value),
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}

class _MetricTileData {
  const _MetricTileData(this.title, this.value, {this.isCount = false});

  final String title;
  final double value;
  final bool isCount;
}

class _UserManagementSection extends ConsumerStatefulWidget {
  const _UserManagementSection({required this.usersAsync});

  final AsyncValue<List<UserModel>> usersAsync;

  @override
  ConsumerState<_UserManagementSection> createState() => _UserManagementSectionState();
}

class _UserManagementSectionState extends ConsumerState<_UserManagementSection> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _usernameController;
  late final TextEditingController _passwordController;
  UserRole _role = UserRole.user;

  @override
  void initState() {
    super.initState();
    _usernameController = TextEditingController();
    _passwordController = TextEditingController();
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 720;
        final formFields = _buildFormFields(!isCompact);

        return _AdminSectionCard(
          title: 'إدارة العمال',
          actions: [
            IconButton(
              tooltip: 'تحديث القائمة',
              onPressed: () => ref.invalidate(adminUsersProvider),
              icon: const Icon(Icons.refresh),
            ),
          ],
          child: widget.usersAsync.when(
            data: (users) {
              final formChild = isCompact
                  ? Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: formFields
                          .map(
                            (child) => Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: child,
                            ),
                          )
                          .toList(),
                    )
                  : Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: formFields,
                    );

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Form(
                    key: _formKey,
                    child: formChild,
                  ),
                  const SizedBox(height: 16),
                  if (users.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 24),
                      child: Text(
                        'لم يتم إضافة أي عامل بعد.',
                        textAlign: TextAlign.center,
                      ),
                    )
                  else if (isCompact)
                    ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemBuilder: (context, index) {
                        final user = users[index];
                        return _WorkerListTile(
                          user: user,
                          onEdit: () => _editUser(context, user),
                          onDelete: () => _deleteUser(context, user),
                        );
                      },
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemCount: users.length,
                    )
                  else
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: DataTable2(
                        columnSpacing: 16,
                        horizontalMargin: 16,
                        minWidth: 720,
                        dataRowHeight: 56,
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
                                  DataCell(Text('${user.id ?? '-'}')),
                                  DataCell(Text(user.username)),
                                  DataCell(Text(user.role.displayName)),
                                  DataCell(
                                    Wrap(
                                      spacing: 8,
                                      runSpacing: 8,
                                      children: [
                                        OutlinedButton.icon(
                                          onPressed: () => _editUser(context, user),
                                          icon: const Icon(Icons.edit),
                                          label: const Text('تعديل كلمة المرور'),
                                        ),
                                        TextButton.icon(
                                          onPressed: () => _deleteUser(context, user),
                                          icon: const Icon(Icons.delete_outline),
                                          label: const Text('حذف'),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            )
                            .toList(),
                      ),
                    ),
                ],
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => Text('تعذر تحميل المستخدمين: $error'),
          ),
        );
      },
    );
  }

  List<Widget> _buildFormFields(bool isWide) {
    return [
      SizedBox(
        width: isWide ? 220 : double.infinity,
        child: TextFormField(
          controller: _usernameController,
          decoration: const InputDecoration(labelText: 'اسم المستخدم'),
          validator: (value) => value == null || value.isEmpty ? 'إلزامي' : null,
        ),
      ),
      SizedBox(
        width: isWide ? 220 : double.infinity,
        child: TextFormField(
          controller: _passwordController,
          decoration: const InputDecoration(labelText: 'كلمة المرور'),
          obscureText: true,
          validator: (value) => value == null || value.isEmpty ? 'إلزامي' : null,
        ),
      ),
      SizedBox(
        width: isWide ? 200 : double.infinity,
        child: DropdownButtonFormField<UserRole>(
          key: ValueKey(_role),
          initialValue: _role,
          decoration: const InputDecoration(labelText: 'الدور'),
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
              setState(() {
                _role = value;
              });
            }
          },
        ),
      ),
      SizedBox(
        width: isWide ? 180 : double.infinity,
        child: FilledButton.icon(
          onPressed: _submit,
          icon: const Icon(Icons.person_add_alt_1),
          label: const Text('إضافة مستخدم'),
        ),
      ),
    ];
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    await ref.read(userRepositoryProvider).createUser(
          username: _usernameController.text,
          password: _passwordController.text,
          role: _role,
        );
    if (!context.mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('تمت إضافة ${_usernameController.text} بنجاح')),
    );
    setState(() {
      _role = UserRole.user;
    });
    _usernameController.clear();
    _passwordController.clear();
  }

  Future<void> _editUser(BuildContext context, UserModel user) async {
    final adminPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('إعادة تعيين كلمة المرور لـ ${user.username}'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: newPasswordController,
                decoration: const InputDecoration(labelText: 'كلمة المرور الجديدة'),
                obscureText: true,
              ),
              const SizedBox(height: 12),
              TextField(
                controller: adminPasswordController,
                decoration: const InputDecoration(labelText: 'كلمة مرور المشرف للتأكيد'),
                obscureText: true,
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('إلغاء')),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
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

  Future<void> _deleteUser(BuildContext context, UserModel user) async {
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

class _WorkerListTile extends StatelessWidget {
  const _WorkerListTile({
    required this.user,
    required this.onEdit,
    required this.onDelete,
  });

  final UserModel user;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    final initials = user.username.isNotEmpty ? user.username[0].toUpperCase() : '?';

    return Card(
      margin: EdgeInsets.zero,
      elevation: 0,
      clipBehavior: Clip.antiAlias,
      child: ListTile(
        leading: CircleAvatar(
          child: Text(initials),
        ),
        title: Text(
          user.username,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        subtitle: Text('الدور: ${user.role.displayName}'),
        trailing: Wrap(
          spacing: 8,
          children: [
            IconButton(
              tooltip: 'تعديل كلمة المرور',
              onPressed: onEdit,
              icon: const Icon(Icons.edit_outlined),
            ),
            IconButton(
              tooltip: 'حذف المستخدم',
              onPressed: onDelete,
              icon: const Icon(Icons.delete_outline),
            ),
          ],
        ),
      ),
    );
  }
}

class _SessionsReportSection extends ConsumerWidget {
  const _SessionsReportSection({required this.sessionsAsync, required this.showTimes});

  final AsyncValue<List<CashSessionModel>> sessionsAsync;
  final bool showTimes;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersMap = ref.watch(adminUsersProvider).maybeWhen(
          data: (users) => {
            for (final user in users)
              if (user.id != null) user.id!: user
          },
          orElse: () => <int, UserModel>{},
        );

    return _AdminSectionCard(
      title: 'تقرير الجلسات',
      child: sessionsAsync.when(
        data: (sessions) {
          if (sessions.isEmpty) {
            return const Padding(
              padding: EdgeInsets.symmetric(vertical: 32),
              child: Text(
                'لا توجد جلسات في الفترة المحددة.',
                textAlign: TextAlign.center,
              ),
            );
          }

          final totals = _SessionTableTotals.fromSessions(sessions);

          return LayoutBuilder(
            builder: (context, constraints) {
              final isCompact = constraints.maxWidth < 900;

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      _SummaryChip(
                        icon: Icons.event_available,
                        label: 'عدد الجلسات',
                        value: Formatters.formatNumber(totals.count.toDouble()),
                      ),
                      _SummaryChip(
                        icon: Icons.lock_open,
                        label: 'جلسات مفتوحة',
                        value: Formatters.formatNumber(totals.openCount.toDouble()),
                        color: Colors.orange,
                      ),
                      _SummaryChip(
                        icon: Icons.lock,
                        label: 'جلسات مغلقة',
                        value: Formatters.formatNumber(totals.closedCount.toDouble()),
                        color: Colors.green,
                      ),
                      _SummaryChip(
                        icon: Icons.savings,
                        label: 'صافي الفرق النقدي',
                        value: Formatters.formatCurrency(totals.totalCashDifference),
                      ),
                      _SummaryChip(
                        icon: Icons.account_balance_wallet,
                        label: 'تغير الفليكسي',
                        value: Formatters.formatCurrency(totals.totalFlexiMovement),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (isCompact)
                    ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemBuilder: (context, index) {
                        final session = sessions[index];
                        return _SessionReportTile(
                          session: session,
                          user: usersMap[session.userId],
                          showTimes: showTimes,
                          onDetails: session.id == null
                              ? null
                              : () => _showSessionDetails(context, ref, session),
                        );
                      },
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemCount: sessions.length,
                    )
                  else
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: DataTable2(
                        columnSpacing: 16,
                        horizontalMargin: 16,
                        minWidth: showTimes ? 1040 : 900,
                        columns: [
                          const DataColumn(label: Text('العامل')),
                          if (showTimes) const DataColumn(label: Text('وقت الفتح')),
                          if (showTimes) const DataColumn(label: Text('وقت الغلق')),
                          const DataColumn(label: Text('رصيد البداية')),
                          const DataColumn(label: Text('رصيد النهاية')),
                          const DataColumn(label: Text('الفرق النقدي')),
                          const DataColumn(label: Text('الفليكسي')),
                          const DataColumn(label: Text('الحالة')),
                          const DataColumn(label: Text('ملاحظات')),
                          const DataColumn(label: Text('إجراءات')),
                        ],
                        rows: sessions
                            .map(
                              (session) {
                                final username =
                                    usersMap[session.userId]?.username ?? 'مستخدم #${session.userId}';
                                final endBalance = session.endBalance ?? session.startBalance;
                                final cashDifference = endBalance - session.startBalance;
                                final endFlexi = session.endFlexi ?? session.startFlexi;
                                final flexiMovement = endFlexi - session.startFlexi;

                                return DataRow(
                                  cells: [
                                    DataCell(Text(username)),
                                    if (showTimes)
                                      DataCell(Text(Formatters.formatDate(session.startTime))),
                                    if (showTimes)
                                      DataCell(Text(
                                        session.endTime == null
                                            ? '---'
                                            : Formatters.formatDate(session.endTime!),
                                      )),
                                    DataCell(Text(Formatters.formatCurrency(session.startBalance))),
                                    DataCell(Text(Formatters.formatCurrency(endBalance))),
                                    DataCell(Text(Formatters.formatCurrency(cashDifference))),
                                    DataCell(Text(
                                        '${Formatters.formatCurrency(session.startFlexi)} → ${Formatters.formatCurrency(endFlexi)} (${Formatters.formatCurrency(flexiMovement)})')),
                                    DataCell(_StatusChip(status: session.status)),
                                    DataCell(SizedBox(
                                      width: 200,
                                      child: Text(
                                        session.notes?.isNotEmpty == true ? session.notes! : '---',
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    )),
                                    DataCell(
                                      IconButton(
                                        tooltip: 'عرض التفاصيل',
                                        onPressed: session.id == null
                                            ? null
                                            : () => _showSessionDetails(context, ref, session),
                                        icon: const Icon(Icons.info_outline),
                                      ),
                                    ),
                                  ],
                                );
                              },
                            )
                            .toList(),
                      ),
                    ),
                ],
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Text('تعذر تحميل الجلسات: $error'),
      ),
    );
  }

  Future<void> _showSessionDetails(
    BuildContext context,
    WidgetRef ref,
    CashSessionModel session,
  ) async {
    if (session.id == null) {
      return;
    }
    final summary = await ref.read(adminSessionSummaryProvider(session.id!).future);
    final navigator = Navigator.of(context);
    if (!navigator.mounted) {
      return;
    }

    await showModalBottomSheet<void>(
      context: navigator.context,
      isScrollControlled: true,
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom + 24,
            left: 24,
            right: 24,
            top: 24,
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'تفاصيل الجلسة #${session.id}',
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _SummaryChip(
                      icon: Icons.play_circle_outline,
                      label: 'البداية',
                      value: Formatters.formatCurrency(summary.startBalance),
                    ),
                    _SummaryChip(
                      icon: Icons.receipt_long,
                      label: 'إجمالي المصاريف',
                      value: Formatters.formatCurrency(summary.totalExpense),
                    ),
                    _SummaryChip(
                      icon: Icons.trending_up,
                      label: 'الفرق النقدي',
                      value: Formatters.formatCurrency(summary.netCashDifference),
                    ),
                    _SummaryChip(
                      icon: Icons.account_balance_wallet,
                      label: 'الفليكسي الحالي',
                      value: Formatters.formatCurrency(summary.currentFlexi),
                    ),
                    _SummaryChip(
                      icon: Icons.call_made,
                      label: 'الفليكسي المستهلك',
                      value: Formatters.formatCurrency(summary.flexiConsumed),
                    ),
                    _SummaryChip(
                      icon: Icons.monetization_on_outlined,
                      label: 'صافي الربح',
                      value: Formatters.formatCurrency(summary.totalNetProfit),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Text(
                  'ملاحظات الجلسة',
                  style: Theme.of(context)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(session.notes?.isNotEmpty == true ? session.notes! : 'لا توجد ملاحظات.'),
                const SizedBox(height: 24),
                Align(
                  alignment: AlignmentDirectional.centerEnd,
                  child: FilledButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('إغلاق'),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _SessionTableTotals {
  const _SessionTableTotals({
    required this.count,
    required this.openCount,
    required this.closedCount,
    required this.totalCashDifference,
    required this.totalFlexiMovement,
  });

  factory _SessionTableTotals.fromSessions(List<CashSessionModel> sessions) {
    var openCount = 0;
    var closedCount = 0;
    var totalCashDifference = 0.0;
    var totalFlexiMovement = 0.0;

    for (final session in sessions) {
      if (session.status == SessionStatus.open) {
        openCount++;
      } else {
        closedCount++;
      }
      final endBalance = session.endBalance ?? session.startBalance;
      totalCashDifference += endBalance - session.startBalance;
      final endFlexi = session.endFlexi ?? session.startFlexi;
      totalFlexiMovement += endFlexi - session.startFlexi;
    }

    return _SessionTableTotals(
      count: sessions.length,
      openCount: openCount,
      closedCount: closedCount,
      totalCashDifference: totalCashDifference,
      totalFlexiMovement: totalFlexiMovement,
    );
  }

  final int count;
  final int openCount;
  final int closedCount;
  final double totalCashDifference;
  final double totalFlexiMovement;
}

class _SummaryChip extends StatelessWidget {
  const _SummaryChip({
    required this.icon,
    required this.label,
    required this.value,
    this.color,
  });

  final IconData icon;
  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final resolvedColor = color ?? theme.colorScheme.primary;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: resolvedColor.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: resolvedColor),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(label, style: theme.textTheme.bodySmall),
              Text(
                value,
                style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: resolvedColor,
                    ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final SessionStatus status;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    late final String label;
    late final Color color;
    if (status == SessionStatus.open) {
      label = 'مفتوحة';
      color = colorScheme.tertiary;
    } else {
      label = 'مغلقة';
      color = colorScheme.secondary;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
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

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 640;

        final selector = usersAsync.when(
          data: (users) {
            final workers = users.where((user) => user.role == UserRole.user).toList();
            return DropdownButtonFormField<int?>(
              key: ValueKey(state.selectedUserId),
              decoration: const InputDecoration(labelText: 'اختر العامل'),
              initialValue: state.selectedUserId,
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
        );

        final monthButton = OutlinedButton.icon(
          onPressed: () async {
            final picked = await showMonthPicker(
              context: context,
              initialDate: state.selectedMonth,
            );
            if (picked != null) {
              ref.read(adminDashboardControllerProvider.notifier).changeMonth(picked);
            }
          },
          icon: const Icon(Icons.calendar_month),
          label: Text('الشهر: ${state.selectedMonth.month}/${state.selectedMonth.year}'),
        );

        final selectorRow = isWide
            ? Row(
                children: [
                  Expanded(child: selector),
                  const SizedBox(width: 12),
                  monthButton,
                ],
              )
            : Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  selector,
                  const SizedBox(height: 12),
                  monthButton,
                ],
              );

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ملف العامل',
                  style: Theme.of(context)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                selectorRow,
                const SizedBox(height: 16),
                expensesAsync.when(
                  data: (data) {
                    if (data.isEmpty) {
                      return const Text('اختر عاملًا لعرض بياناته.');
                    }
                    final maxValue = data.values.reduce((a, b) => a > b ? a : b);
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'المصاريف اليومية',
                          style: Theme.of(context)
                              .textTheme
                              .titleSmall
                              ?.copyWith(fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          height: isWide ? 220 : 200,
                          child: BarChart(
                            BarChartData(
                              alignment: BarChartAlignment.spaceAround,
                              gridData: FlGridData(show: false),
                              borderData: FlBorderData(show: false),
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
                                leftTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                    showTitles: false,
                                  ),
                                ),
                              ),
                              maxY: maxValue == 0 ? 100 : maxValue * 1.2,
                              barGroups: [
                                for (int i = 0; i < data.length; i++)
                                  BarChartGroupData(
                                    x: i,
                                    barRods: [
                                      BarChartRodData(
                                        toY: data.values.elementAt(i),
                                        color: Theme.of(context).colorScheme.primary,
                                        width: isWide ? 18 : 14,
                                        borderRadius: BorderRadius.circular(6),
                                      ),
                                    ],
                                  ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    );
                  },
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (error, _) => Text('خطأ في تحميل بيانات المصاريف: $error'),
                ),
              ],
            ),
          ),
        );
      },
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
