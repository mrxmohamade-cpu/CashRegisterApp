import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/cash_session_model.dart';
import '../../../core/models/session_summary.dart';
import '../../../core/models/user_model.dart';
import '../../../core/repo/session_repository.dart';
import '../../../core/utils/app_providers.dart';
import '../../../core/models/cash_transaction_model.dart';
import '../../../core/models/flexi_transaction_model.dart';

final userSessionsProvider = StreamProvider.family<List<CashSessionModel>, int>((ref, userId) {
  final repository = ref.watch(sessionRepositoryProvider);
  return repository.watchSessions(userId);
});

final activeSessionProvider = Provider.family<CashSessionModel?, int>((ref, userId) {
  final sessions = ref
      .watch(userSessionsProvider(userId))
      .maybeWhen(orElse: () => <CashSessionModel>[], data: (data) => data);
  for (final session in sessions) {
    if (session.isOpen) {
      return session;
    }
  }
  return null;
});

final sessionSummaryProvider = FutureProvider.family<SessionSummary, CashSessionModel>((ref, session) async {
  final repository = ref.watch(sessionRepositoryProvider);
  return repository.buildSummary(session);
});

final sessionTransactionsProvider = StreamProvider.family<List<CashTransactionModel>, int>((ref, sessionId) {
  final repository = ref.watch(sessionRepositoryProvider);
  return repository.watchTransactions(sessionId);
});

final sessionFlexiProvider = StreamProvider.family<List<FlexiTransactionModel>, int>((ref, sessionId) {
  final repository = ref.watch(sessionRepositoryProvider);
  return repository.watchFlexiTransactions(sessionId);
});

class SessionController {
  SessionController(this.ref);

  final Ref ref;

  SessionRepository get _repository => ref.read(sessionRepositoryProvider);

  Future<void> openSession({
    required UserModel user,
    required double startBalance,
    required double startFlexi,
  }) async {
    await _repository.openSession(userId: user.id!, startBalance: startBalance, startFlexi: startFlexi);
  }

  Future<void> closeSession({
    required CashSessionModel session,
    required double endBalance,
    required double endFlexi,
  }) async {
    await _repository.closeSession(sessionId: session.id!, endBalance: endBalance, endFlexi: endFlexi);
  }

  Future<void> addExpense({
    required CashSessionModel session,
    required double amount,
    String? description,
  }) async {
    await _repository.addExpense(sessionId: session.id!, amount: amount, description: description);
  }

  Future<void> addFlexi({
    required CashSessionModel session,
    required UserModel user,
    required double amount,
    String? description,
    bool isPaid = false,
  }) async {
    await _repository.addFlexi(
      sessionId: session.id!,
      userId: user.id!,
      amount: amount,
      description: description,
      isPaid: isPaid,
    );
  }

  Future<void> updateTransaction({required CashTransactionModel transaction}) async {
    await _repository.updateTransaction(transaction);
  }

  Future<void> deleteTransaction(int id) async {
    await _repository.deleteTransaction(id);
  }

  Future<void> markFlexiPaid(int id, bool isPaid) async {
    await _repository.markFlexiPaid(id, isPaid);
  }

  Future<void> deleteFlexi(int id) async {
    await _repository.deleteFlexi(id);
  }

  Future<void> updateNotes({
    required CashSessionModel session,
    required String notes,
  }) async {
    await _repository.updateNotes(session.id!, notes);
  }
}

final sessionControllerProvider = Provider<SessionController>((ref) {
  return SessionController(ref);
});
