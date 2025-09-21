import '../db/app_database.dart';
import '../db/dao/session_dao.dart';
import '../models/cash_session_model.dart';
import '../models/cash_transaction_model.dart';
import '../models/flexi_transaction_model.dart';
import '../models/session_status.dart';
import '../models/session_summary.dart';
import '../utils/session_calculator.dart';
import '../models/transaction_type.dart';

class SessionRepository {
  SessionRepository(this._db) : _dao = SessionDao(_db);

  final AppDatabase _db;
  final SessionDao _dao;

  Stream<List<CashSessionModel>> watchSessions(int userId) => _dao.watchSessionsForUser(userId);

  Future<CashSessionModel?> currentOpenSession(int userId) => _dao.getOpenSessionForUser(userId);

  Future<int> openSession({
    required int userId,
    required double startBalance,
    required double startFlexi,
  }) async {
    return _dao.startSession(userId: userId, startBalance: startBalance, startFlexi: startFlexi);
  }

  Future<void> updateNotes(int sessionId, String notes) => _dao.updateSessionNotes(sessionId, notes);

  Future<void> closeSession({
    required int sessionId,
    required double endBalance,
    required double endFlexi,
  }) =>
      _dao.closeSession(sessionId: sessionId, endBalance: endBalance, endFlexi: endFlexi);

  Stream<List<CashTransactionModel>> watchTransactions(int sessionId) => _dao.watchTransactions(sessionId);

  Stream<List<FlexiTransactionModel>> watchFlexiTransactions(int sessionId) =>
      _dao.watchFlexiTransactions(sessionId);

  Future<int> addExpense({
    required int sessionId,
    required double amount,
    String? description,
  }) {
    return _dao.insertTransaction(
      CashTransactionModel(
        sessionId: sessionId,
        type: TransactionType.expense,
        amount: amount,
        description: description,
        timestamp: DateTime.now(),
      ),
    );
  }

  Future<int> addIncome({
    required int sessionId,
    required double amount,
    String? description,
  }) {
    return _dao.insertTransaction(
      CashTransactionModel(
        sessionId: sessionId,
        type: TransactionType.income,
        amount: amount,
        description: description,
        timestamp: DateTime.now(),
      ),
    );
  }

  Future<int> addFlexi({
    required int sessionId,
    required int userId,
    required double amount,
    String? description,
    bool isPaid = false,
  }) {
    return _dao.insertFlexiTransaction(
      FlexiTransactionModel(
        sessionId: sessionId,
        userId: userId,
        amount: amount,
        description: description,
        timestamp: DateTime.now(),
        isPaid: isPaid,
      ),
    );
  }

  Future<void> updateTransaction(CashTransactionModel transaction) =>
      _dao.updateTransaction(transaction);

  Future<void> deleteTransaction(int id) => _dao.deleteTransaction(id);

  Future<void> markFlexiPaid(int id, bool isPaid) => _dao.markFlexiPaid(id, isPaid);

  Future<void> deleteFlexi(int id) => _dao.deleteFlexiTransaction(id);

  Future<SessionSummary> buildSummary(CashSessionModel session) async {
    final totalExpense = await _dao.sumExpenses(session.id!);
    final totalFlexiAdditions = await _dao.sumFlexiAdditions(session.id!);
    final totalFlexiPaid = await _dao.sumFlexiPaid(session.id!);
    return SessionCalculator.compute(
      session: session,
      totalExpense: totalExpense,
      totalFlexiAdditions: totalFlexiAdditions,
      totalFlexiPaid: totalFlexiPaid,
    );
  }

  Future<List<CashSessionModel>> filterSessions({
    int? userId,
    DateTime? from,
    DateTime? to,
  }) async {
    final buffer = StringBuffer('SELECT * FROM cash_sessions WHERE 1=1');
    final variables = <Variable>[];
    if (userId != null) {
      buffer.write(' AND user_id = ?');
      variables.add(Variable<int>(userId));
    }
    if (from != null) {
      buffer.write(' AND start_time >= ?');
      variables.add(Variable<String>(from.toIso8601String()));
    }
    if (to != null) {
      buffer.write(' AND start_time <= ?');
      variables.add(Variable<String>(to.toIso8601String()));
    }
    buffer.write(' ORDER BY start_time DESC');
    final rows = await _db.customSelect(
      buffer.toString(),
      variables: variables,
      readsFrom: const {},
    ).get();
    return rows.map((row) => _mapSession(row.data)).toList();
  }

  CashSessionModel _mapSession(Map<String, Object?> data) {
    return CashSessionModel(
      id: data['id'] as int?,
      userId: data['user_id'] as int,
      startTime: DateTime.parse(data['start_time'] as String),
      endTime: data['end_time'] == null
          ? null
          : DateTime.tryParse(data['end_time'] as String),
      startBalance: (data['start_balance'] as num).toDouble(),
      endBalance: (data['end_balance'] as num?)?.toDouble(),
      status: (data['status'] as String) == 'open'
          ? SessionStatus.open
          : SessionStatus.closed,
      notes: data['notes'] as String?,
      startFlexi: (data['start_flexi'] as num?)?.toDouble() ?? 0.0,
      endFlexi: (data['end_flexi'] as num?)?.toDouble(),
    );
  }
}
