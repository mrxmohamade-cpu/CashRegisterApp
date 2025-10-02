import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/cash_session_model.dart';
import '../../../core/models/cash_transaction_model.dart';
import '../../../core/models/session_status.dart';
import '../../../core/models/session_summary.dart';
import '../../../core/models/user_model.dart';
import '../../../core/utils/formatters.dart';
import '../../auth/providers/auth_controller.dart';
import '../../session/providers/session_providers.dart';

class UserDashboardScreen extends ConsumerStatefulWidget {
  const UserDashboardScreen({required this.user, super.key});

  final UserModel user;

  @override
  ConsumerState<UserDashboardScreen> createState() => _UserDashboardScreenState();
}

class _UserDashboardScreenState extends ConsumerState<UserDashboardScreen> {
  final _notesController = TextEditingController();

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final user = widget.user;
    if (user.id == null) {
      return const Scaffold(
        body: Center(child: Text('لم يتم تحميل بيانات المستخدم بعد.')),
      );
    }
    final sessionsAsync = ref.watch(userSessionsProvider(user.id!));
    final activeSession = ref.watch(activeSessionProvider(user.id!));
    final sessionController = ref.watch(sessionControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text('لوحة العامل - ${user.username}'),
        actions: [
          if (sessionsAsync.hasValue)
            Builder(
              builder: (context) {
                final sessions = sessionsAsync.value ?? const <CashSessionModel>[];
                final hasCompactHistory = MediaQuery.of(context).size.width < 900 && sessions.isNotEmpty;
                if (!hasCompactHistory) {
                  return const SizedBox.shrink();
                }
                return IconButton(
                  icon: const Icon(Icons.history),
                  tooltip: 'سجل الجلسات',
                  onPressed: () => _showHistorySheet(context, sessions, activeSession?.id),
                );
              },
            ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => ref.read(authControllerProvider.notifier).logout(),
            tooltip: 'تسجيل الخروج',
          ),
        ],
      ),
      body: sessionsAsync.when(
        data: (sessions) {
          final summaryAsync = activeSession != null
              ? ref.watch(sessionSummaryProvider(activeSession))
              : const AsyncValue.data(SessionSummary());
          if (activeSession != null && (activeSession.notes ?? '').isNotEmpty) {
            _notesController.text = activeSession.notes!;
          }
          return LayoutBuilder(
            builder: (context, constraints) {
              if (constraints.maxWidth >= 900) {
                return _buildWideLayout(
                  context,
                  sessionController,
                  user,
                  sessions,
                  activeSession,
                  summaryAsync,
                );
              }
              return _buildMobileLayout(
                context,
                sessionController,
                user,
                sessions,
                activeSession,
                summaryAsync,
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('فشل التحميل: $error')),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: sessionsAsync.maybeWhen(
        data: (_) {
          final width = MediaQuery.of(context).size.width;
          if (width >= 900) {
            return null;
          }
          return FloatingActionButton.extended(
            icon: const Icon(Icons.tune),
            label: const Text('إجراءات سريعة'),
            onPressed: () => _showQuickActions(
              context,
              sessionController,
              user,
              activeSession,
            ),
          );
        },
        orElse: () => null,
      ),
    );
  }

  Widget _buildWideLayout(
    BuildContext context,
    SessionController sessionController,
    UserModel user,
    List<CashSessionModel> sessions,
    CashSessionModel? activeSession,
    AsyncValue<SessionSummary> summaryAsync,
  ) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 3,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _buildActionBar(context, sessionController, user, activeSession),
              const SizedBox(height: 16),
              summaryAsync.when(
                data: (summary) => _SummaryCards(summary: summary),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, _) => Text('حدث خطأ: $error'),
              ),
              const SizedBox(height: 16),
              if (activeSession != null) ...[
                _NotesSection(
                  controller: _notesController,
                  enabled: activeSession.isOpen,
                  onSave: (value) => sessionController.updateNotes(
                    session: activeSession,
                    notes: value,
                  ),
                ),
                const SizedBox(height: 16),
                _TransactionsTable(session: activeSession),
                const SizedBox(height: 16),
                _FlexiTable(session: activeSession),
              ] else
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: const [
                        Text(
                          'لا توجد جلسة مفتوحة حاليا.',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                        ),
                        SizedBox(height: 8),
                        Text('قم بفتح الصندوق لبدء جلسة جديدة.'),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
        SizedBox(
          width: 320,
          child: _SessionHistoryList(
            sessions: sessions,
            activeSessionId: activeSession?.id,
          ),
        ),
      ],
    );
  }

  Widget _buildMobileLayout(
    BuildContext context,
    SessionController sessionController,
    UserModel user,
    List<CashSessionModel> sessions,
    CashSessionModel? activeSession,
    AsyncValue<SessionSummary> summaryAsync,
  ) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      children: [
        _buildActionBar(context, sessionController, user, activeSession),
        const SizedBox(height: 16),
        summaryAsync.when(
          data: (summary) => _SummaryCards(summary: summary, compact: true),
          loading: () => const Padding(
            padding: EdgeInsets.symmetric(vertical: 32),
            child: Center(child: CircularProgressIndicator()),
          ),
          error: (error, _) => Text('حدث خطأ: $error'),
        ),
        const SizedBox(height: 16),
        if (activeSession != null) ...[
          Card(
            child: ListTile(
              leading: Icon(activeSession.isOpen ? Icons.lightbulb : Icons.lock),
              title: Text(activeSession.isOpen ? 'جلسة مفتوحة' : 'جلسة مغلقة'),
              subtitle: Text(Formatters.formatDate(activeSession.startTime)),
              trailing: Text(activeSession.status.displayName),
            ),
          ),
          const SizedBox(height: 12),
          _NotesSection(
            controller: _notesController,
            enabled: activeSession.isOpen,
            onSave: (value) => sessionController.updateNotes(
              session: activeSession,
              notes: value,
            ),
          ),
          const SizedBox(height: 16),
          _MobileTransactionsList(session: activeSession),
          const SizedBox(height: 16),
          _MobileFlexiList(session: activeSession),
        ] else ...[
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'لا توجد جلسة مفتوحة حاليا.',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                  ),
                  SizedBox(height: 8),
                  Text('استخدم زر فتح الصندوق لبدء جلسة جديدة.'),
                ],
              ),
            ),
          ),
        ],
        const SizedBox(height: 16),
        ExpansionTile(
          leading: const Icon(Icons.history_toggle_off),
          title: const Text('سجل الجلسات'),
          children: [
            _SessionHistoryList(
              sessions: sessions,
              activeSessionId: activeSession?.id,
              compact: true,
            ),
          ],
        ),
      ],
    );
  }

  void _showQuickActions(
    BuildContext context,
    SessionController controller,
    UserModel user,
    CashSessionModel? activeSession,
  ) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: const Icon(Icons.lock_open),
                  title: const Text('فتح الصندوق'),
                  onTap: activeSession == null
                      ? () {
                          Navigator.of(context).pop();
                          _showOpenDialog(context, controller, user);
                        }
                      : null,
                ),
                ListTile(
                  leading: const Icon(Icons.money_off),
                  title: const Text('إضافة مصروف'),
                  onTap: activeSession == null
                      ? null
                      : () {
                          Navigator.of(context).pop();
                          _showExpenseDialog(context, controller, activeSession);
                        },
                ),
                ListTile(
                  leading: const Icon(Icons.phone_android),
                  title: const Text('إضافة فليكسي'),
                  onTap: activeSession == null
                      ? null
                      : () {
                          Navigator.of(context).pop();
                          _showFlexiDialog(context, controller, user, activeSession);
                        },
                ),
                ListTile(
                  leading: const Icon(Icons.lock),
                  title: const Text('غلق الصندوق'),
                  onTap: activeSession == null
                      ? null
                      : () {
                          Navigator.of(context).pop();
                          _showCloseDialog(context, controller, activeSession);
                        },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showHistorySheet(
    BuildContext context,
    List<CashSessionModel> sessions,
    int? activeSessionId,
  ) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: _SessionHistoryList(
              sessions: sessions,
              activeSessionId: activeSessionId,
              compact: true,
            ),
          ),
        );
      },
    );
  }

  Widget _buildActionBar(
    BuildContext context,
    SessionController controller,
    UserModel user,
    CashSessionModel? activeSession,
  ) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        ElevatedButton.icon(
          onPressed: activeSession == null
              ? () => _showOpenDialog(context, controller, user)
              : null,
          icon: const Icon(Icons.lock_open),
          label: const Text('فتح الصندوق'),
        ),
        ElevatedButton.icon(
          onPressed: activeSession == null
              ? null
              : () => _showExpenseDialog(context, controller, activeSession),
          icon: const Icon(Icons.money_off),
          label: const Text('إضافة مصروف'),
        ),
        ElevatedButton.icon(
          onPressed: activeSession == null
              ? null
              : () => _showFlexiDialog(context, controller, user, activeSession),
          icon: const Icon(Icons.phone_android),
          label: const Text('إضافة فليكسي'),
        ),
        ElevatedButton.icon(
          onPressed: activeSession == null
              ? null
              : () => _showCloseDialog(context, controller, activeSession),
          icon: const Icon(Icons.lock),
          label: const Text('غلق الصندوق'),
        ),
      ],
    );
  }

  Future<void> _showOpenDialog(
    BuildContext context,
    SessionController controller,
    UserModel user,
  ) async {
    final formKey = GlobalKey<FormState>();
    final startBalanceController = TextEditingController();
    final startFlexiController = TextEditingController(text: '0');
    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('فتح جلسة جديدة'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: startBalanceController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'رصيد البداية'),
                  validator: _validateNumber,
                ),
                TextFormField(
                  controller: startFlexiController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'رصيد الفليكسي'),
                  validator: _validateNumber,
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
              child: const Text('فتح'),
            ),
          ],
        );
      },
    );
    if (result == true) {
      await controller.openSession(
        user: user,
        startBalance: double.parse(startBalanceController.text),
        startFlexi: double.parse(startFlexiController.text),
      );
    }
  }

  Future<void> _showExpenseDialog(
    BuildContext context,
    SessionController controller,
    CashSessionModel session,
  ) async {
    final formKey = GlobalKey<FormState>();
    final amountController = TextEditingController();
    final descriptionController = TextEditingController();
    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('إضافة مصروف'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: amountController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'المبلغ'),
                  validator: _validateNumber,
                ),
                TextFormField(
                  controller: descriptionController,
                  decoration: const InputDecoration(labelText: 'الوصف (اختياري)'),
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
              child: const Text('حفظ'),
            ),
          ],
        );
      },
    );
    if (result == true) {
      await controller.addExpense(
        session: session,
        amount: double.parse(amountController.text),
        description: descriptionController.text.isEmpty ? null : descriptionController.text,
      );
    }
  }

  Future<void> _showFlexiDialog(
    BuildContext context,
    SessionController controller,
    UserModel user,
    CashSessionModel session,
  ) async {
    final formKey = GlobalKey<FormState>();
    final amountController = TextEditingController();
    final descriptionController = TextEditingController();
    bool isPaid = false;
    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return StatefulBuilder(builder: (context, setState) {
          return AlertDialog(
            title: const Text('إضافة فليكسي'),
            content: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: amountController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'المبلغ'),
                    validator: _validateNumber,
                  ),
                  TextFormField(
                    controller: descriptionController,
                    decoration: const InputDecoration(labelText: 'الوصف (اختياري)'),
                  ),
                  CheckboxListTile(
                    value: isPaid,
                    onChanged: (value) => setState(() => isPaid = value ?? false),
                    title: const Text('تم السداد فوراً'),
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
                child: const Text('حفظ'),
              ),
            ],
          );
        });
      },
    );
    if (result == true) {
      await controller.addFlexi(
        session: session,
        user: user,
        amount: double.parse(amountController.text),
        description: descriptionController.text.isEmpty ? null : descriptionController.text,
        isPaid: isPaid,
      );
    }
  }

  Future<void> _showCloseDialog(
    BuildContext context,
    SessionController controller,
    CashSessionModel session,
  ) async {
    final formKey = GlobalKey<FormState>();
    final endBalanceController = TextEditingController(text: session.startBalance.toString());
    final endFlexiController = TextEditingController(text: session.startFlexi.toString());
    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('غلق الجلسة'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: endBalanceController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'رصيد النهاية'),
                  validator: _validateNumber,
                ),
                TextFormField(
                  controller: endFlexiController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'رصيد الفليكسي النهائي'),
                  validator: _validateNumber,
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
              child: const Text('غلق'),
            ),
          ],
        );
      },
    );
    if (result == true) {
      await controller.closeSession(
        session: session,
        endBalance: double.parse(endBalanceController.text),
        endFlexi: double.parse(endFlexiController.text),
      );
    }
  }

  String? _validateNumber(String? value) {
    if (value == null || value.isEmpty) {
      return 'الحقل مطلوب';
    }
    final parsed = double.tryParse(value);
    if (parsed == null) {
      return 'أدخل رقماً صالحاً';
    }
    return null;
  }
}

class _SummaryCards extends StatelessWidget {
  const _SummaryCards({required this.summary, this.compact = false});

  final SessionSummary summary;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final items = <_SummaryItem>[
      _SummaryItem('رصيد البداية', summary.startBalance),
      _SummaryItem('إجمالي المصاريف', summary.totalExpense),
      _SummaryItem('الفليكسي الحالي', summary.currentFlexi),
      _SummaryItem('صافي الفرق', summary.netCashDifference),
      _SummaryItem('الفليكسي المستهلك', summary.flexiConsumed),
      _SummaryItem('صافي الربح', summary.totalNetProfit),
    ];
    final cards = items
        .map(
          (item) => SizedBox(
            width: 220,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item.title, style: const TextStyle(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Text(
                      Formatters.formatCurrency(item.value),
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ],
                ),
              ),
            ),
          ),
        )
        .toList();
    if (compact) {
      return SizedBox(
        height: 150,
        child: ListView.separated(
          scrollDirection: Axis.horizontal,
          itemCount: cards.length,
          separatorBuilder: (_, __) => const SizedBox(width: 12),
          itemBuilder: (context, index) => cards[index],
        ),
      );
    }
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: cards,
    );
  }
}

class _SummaryItem {
  const _SummaryItem(this.title, this.value);

  final String title;
  final double value;
}

class _TransactionsTable extends ConsumerWidget {
  const _TransactionsTable({required this.session});

  final CashSessionModel session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final transactionsAsync = ref.watch(sessionTransactionsProvider(session.id!));
    final controller = ref.watch(sessionControllerProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('جدول المصروفات', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            transactionsAsync.when(
              data: (transactions) {
                final expense = transactions.where((tx) => tx.isExpense).toList();
                return DataTable2(
                  columnSpacing: 12,
                  horizontalMargin: 12,
                  columns: const [
                    DataColumn(label: Text('#')),
                    DataColumn(label: Text('المبلغ')),
                    DataColumn(label: Text('الوصف')),
                    DataColumn(label: Text('الوقت')),
                    DataColumn(label: Text('إجراءات')),
                  ],
                  rows: [
                    for (int index = 0; index < expense.length; index++)
                      DataRow(cells: [
                        DataCell(Text('${index + 1}')),
                        DataCell(Text(Formatters.formatCurrency(expense[index].amount))),
                        DataCell(Text(expense[index].description ?? '-')),
                        DataCell(Text(Formatters.formatDate(expense[index].timestamp))),
                        DataCell(Row(
                          children: [
                            IconButton(
                              icon: const Icon(Icons.edit),
                              onPressed: () => _editTransaction(context, controller, expense[index]),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline),
                              onPressed: () => controller.deleteTransaction(expense[index].id!),
                            ),
                          ],
                        )),
                      ]),
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Text('خطأ في تحميل المصروفات: $error'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _editTransaction(
    BuildContext context,
    SessionController controller,
    CashTransactionModel transaction,
  ) async {
    final formKey = GlobalKey<FormState>();
    final amountController = TextEditingController(text: transaction.amount.toString());
    final descriptionController = TextEditingController(text: transaction.description ?? '');
    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('تعديل مصروف'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: amountController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'المبلغ'),
                  validator: (value) => value == null || value.isEmpty ? 'إلزامي' : null,
                ),
                TextFormField(
                  controller: descriptionController,
                  decoration: const InputDecoration(labelText: 'الوصف'),
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
              child: const Text('حفظ'),
            ),
          ],
        );
      },
    );
    if (result == true) {
      await controller.updateTransaction(
        transaction: transaction.copyWith(
          amount: double.parse(amountController.text),
          description: descriptionController.text,
          timestamp: DateTime.now(),
        ),
      );
    }
  }
}

class _MobileTransactionsList extends ConsumerWidget {
  const _MobileTransactionsList({required this.session});

  final CashSessionModel session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final transactionsAsync = ref.watch(sessionTransactionsProvider(session.id!));
    final controller = ref.watch(sessionControllerProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(Icons.money_off),
                SizedBox(width: 8),
                Text('المصاريف', style: TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 8),
            transactionsAsync.when(
              data: (transactions) {
                final expense = transactions.where((tx) => tx.isExpense).toList();
                if (expense.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text('لا توجد مصاريف مسجلة بعد.'),
                  );
                }
                return Column(
                  children: [
                    for (final tx in expense)
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text(Formatters.formatCurrency(tx.amount)),
                        subtitle: Text(tx.description?.isEmpty ?? true ? '-' : tx.description!),
                        trailing: Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(Formatters.formatDate(tx.timestamp)),
                            const SizedBox(height: 4),
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.edit, size: 18),
                                  tooltip: 'تعديل',
                                  onPressed: () => _editTransaction(context, controller, tx),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.delete_outline, size: 18),
                                  tooltip: 'حذف',
                                  onPressed: () => controller.deleteTransaction(tx.id!),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Text('خطأ في تحميل المصروفات: $error'),
            ),
          ],
        ),
      ),
    );
  }
}

class _FlexiTable extends ConsumerWidget {
  const _FlexiTable({required this.session});

  final CashSessionModel session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final flexiAsync = ref.watch(sessionFlexiProvider(session.id!));
    final controller = ref.watch(sessionControllerProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('جدول الفليكسي', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            flexiAsync.when(
              data: (items) {
                return DataTable2(
                  columnSpacing: 12,
                  columns: const [
                    DataColumn(label: Text('#')),
                    DataColumn(label: Text('المبلغ')),
                    DataColumn(label: Text('الوصف')),
                    DataColumn(label: Text('الوقت')),
                    DataColumn(label: Text('مدفوع؟')),
                    DataColumn(label: Text('إجراءات')),
                  ],
                  rows: [
                    for (int index = 0; index < items.length; index++)
                      DataRow(cells: [
                        DataCell(Text('${index + 1}')),
                        DataCell(Text(
                          Formatters.formatCurrency(items[index].amount),
                          style: const TextStyle(color: Colors.green),
                        )),
                        DataCell(Text(items[index].description ?? '-')),
                        DataCell(Text(Formatters.formatDate(items[index].timestamp))),
                        DataCell(Icon(
                          items[index].isPaid ? Icons.check_circle : Icons.hourglass_bottom,
                          color: items[index].isPaid ? Colors.teal : Colors.orange,
                        )),
                        DataCell(Row(
                          children: [
                            IconButton(
                              icon: Icon(items[index].isPaid ? Icons.visibility : Icons.check),
                              onPressed: () => controller.markFlexiPaid(items[index].id!, !items[index].isPaid),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline),
                              onPressed: () => controller.deleteFlexi(items[index].id!),
                            ),
                          ],
                        )),
                      ]),
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Text('خطأ في تحميل الفليكسي: $error'),
            ),
          ],
        ),
      ),
    );
  }
}

class _MobileFlexiList extends ConsumerWidget {
  const _MobileFlexiList({required this.session});

  final CashSessionModel session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final transactionsAsync = ref.watch(flexiTransactionsProvider(session.id!));
    final controller = ref.watch(sessionControllerProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(Icons.phone_android),
                SizedBox(width: 8),
                Text('حركات الفليكسي', style: TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 8),
            transactionsAsync.when(
              data: (transactions) {
                if (transactions.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text('لا توجد عمليات فليكسي مسجلة بعد.'),
                  );
                }
                return Column(
                  children: [
                    for (final tx in transactions)
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: CircleAvatar(
                          backgroundColor: Colors.teal.withValues(alpha: 0.1),
                          child: Text(
                            Formatters.formatCurrency(tx.amount),
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ),
                        title: Text(
                          Formatters.formatCurrency(tx.amount),
                          style: const TextStyle(color: Colors.teal, fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(tx.description?.isEmpty ?? true ? '-' : tx.description!),
                        trailing: Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(Formatters.formatDate(tx.timestamp)),
                            const SizedBox(height: 4),
                            Switch(
                              value: tx.isPaid,
                              onChanged: (value) => controller.toggleFlexiPaid(tx, value),
                              activeColor: Colors.teal,
                            ),
                          ],
                        ),
                      ),
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Text('خطأ في تحميل الفليكسي: $error'),
            ),
          ],
        ),
      ),
    );
  }
}

class _NotesSection extends StatefulWidget {
  const _NotesSection({
    required this.controller,
    required this.enabled,
    required this.onSave,
  });

  final TextEditingController controller;
  final bool enabled;
  final ValueChanged<String> onSave;

  @override
  State<_NotesSection> createState() => _NotesSectionState();
}

class _NotesSectionState extends State<_NotesSection> {
  bool _isDirty = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('ملاحظات الجلسة', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: widget.controller,
              maxLines: 4,
              enabled: widget.enabled,
              onChanged: (_) => setState(() => _isDirty = true),
              decoration: const InputDecoration(border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: FilledButton.icon(
                onPressed: !widget.enabled || !_isDirty
                    ? null
                    : () {
                        widget.onSave(widget.controller.text);
                        setState(() => _isDirty = false);
                      },
                icon: const Icon(Icons.save),
                label: const Text('حفظ الملاحظات'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SessionHistoryList extends StatelessWidget {
  const _SessionHistoryList({
    required this.sessions,
    required this.activeSessionId,
    this.compact = false,
  });

  final List<CashSessionModel> sessions;
  final int? activeSessionId;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final content = ListView.builder(
      shrinkWrap: compact,
      physics: compact ? const NeverScrollableScrollPhysics() : null,
      itemCount: sessions.length,
      itemBuilder: (context, index) {
        final session = sessions[index];
        final isActive = session.id == activeSessionId;
        final summaryText = session.endBalance == null
            ? 'قيد العمل'
            : Formatters.formatCurrency((session.endBalance ?? 0) - session.startBalance);
        return Card(
          margin: compact ? const EdgeInsets.symmetric(vertical: 4) : const EdgeInsets.symmetric(vertical: 6),
          color: isActive ? Colors.teal.withValues(alpha: 0.1) : null,
          child: ListTile(
            title: Text(Formatters.formatDate(session.startTime)),
            subtitle: Text(session.notes?.isEmpty ?? true ? 'بدون ملاحظات' : session.notes!),
            trailing: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(session.status.displayName),
                Text(summaryText),
              ],
            ),
          ),
        );
      },
    );

    if (compact) {
      return content;
    }

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('سجل الجلسات', style: TextStyle(fontWeight: FontWeight.bold)),
            const Divider(),
            Expanded(child: content),
          ],
        ),
      ),
    );
  }
}
