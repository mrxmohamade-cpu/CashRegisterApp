import 'package:drift/drift.dart';

import '../../models/cash_session_model.dart';
import '../../models/cash_transaction_model.dart';
import '../../models/flexi_transaction_model.dart';
import '../../models/session_status.dart';
import '../../models/transaction_type.dart';
import '../app_database.dart';

class SessionDao {
  SessionDao(this._db);

  final AppDatabase _db;

  Future<CashSessionModel?> getOpenSessionForUser(int userId) async {
    final row = await _db.customSelect(
      'SELECT * FROM cash_sessions WHERE user_id = ? AND status = "open" ORDER BY id DESC LIMIT 1',
      variables: [Variable<int>(userId)],
      readsFrom: const {},
    ).getSingleOrNull();
    return row == null ? null : _mapSession(row.data);
  }

  Stream<List<CashSessionModel>> watchSessionsForUser(int userId) {
    return _db
        .customSelect(
          'SELECT * FROM cash_sessions WHERE user_id = ? ORDER BY start_time DESC',
          variables: [Variable<int>(userId)],
          readsFrom: const {},
        )
        .watch()
        .map((rows) => rows.map((row) => _mapSession(row.data)).toList());
  }

  Future<List<CashSessionModel>> getSessionsForUser(int userId) async {
    final rows = await _db.customSelect(
      'SELECT * FROM cash_sessions WHERE user_id = ? ORDER BY start_time DESC',
      variables: [Variable<int>(userId)],
      readsFrom: const {},
    ).get();
    return rows.map((row) => _mapSession(row.data)).toList();
  }

  Future<int> startSession({
    required int userId,
    required double startBalance,
    required double startFlexi,
  }) async {
    return _db.customInsert(
      'INSERT INTO cash_sessions(user_id, start_time, start_balance, status, start_flexi) VALUES(?, ?, ?, ?, ?)',
      variables: [
        Variable<int>(userId),
        Variable<String>(DateTime.now().toIso8601String()),
        Variable<double>(startBalance),
        Variable<String>(SessionStatus.open.name),
        Variable<double>(startFlexi),
      ],
    );
  }

  Future<void> updateSessionNotes(int sessionId, String notes) async {
    await _db.customUpdate(
      'UPDATE cash_sessions SET notes = ? WHERE id = ?',
      variables: [Variable<String>(notes), Variable<int>(sessionId)],
      updates: const {},
      updateKind: UpdateKind.update,
    );
  }

  Future<void> closeSession({
    required int sessionId,
    required double endBalance,
    required double endFlexi,
  }) async {
    await _db.customUpdate(
      'UPDATE cash_sessions SET end_time = ?, end_balance = ?, end_flexi = ?, status = ? WHERE id = ?',
      variables: [
        Variable<String>(DateTime.now().toIso8601String()),
        Variable<double>(endBalance),
        Variable<double>(endFlexi),
        Variable<String>(SessionStatus.closed.name),
        Variable<int>(sessionId),
      ],
      updates: const {},
      updateKind: UpdateKind.update,
    );
  }

  Stream<List<CashTransactionModel>> watchTransactions(int sessionId) {
    return _db
        .customSelect(
          'SELECT * FROM transactions WHERE session_id = ? ORDER BY timestamp DESC',
          variables: [Variable<int>(sessionId)],
          readsFrom: const {},
        )
        .watch()
        .map((rows) => rows.map((row) => _mapTransaction(row.data)).toList());
  }

  Future<int> insertTransaction(CashTransactionModel transaction) {
    return _db.customInsert(
      'INSERT INTO transactions(session_id, type, amount, description, timestamp) VALUES(?, ?, ?, ?, ?)',
      variables: [
        Variable<int>(transaction.sessionId),
        Variable<String>(transaction.type.name),
        Variable<double>(transaction.amount),
        Variable<String?>(transaction.description),
        Variable<String>(transaction.timestamp.toIso8601String()),
      ],
    );
  }

  Future<void> updateTransaction(CashTransactionModel transaction) async {
    await _db.customUpdate(
      'UPDATE transactions SET type = ?, amount = ?, description = ?, timestamp = ? WHERE id = ?',
      variables: [
        Variable<String>(transaction.type.name),
        Variable<double>(transaction.amount),
        Variable<String?>(transaction.description),
        Variable<String>(transaction.timestamp.toIso8601String()),
        Variable<int?>(transaction.id),
      ],
      updates: const {},
      updateKind: UpdateKind.update,
    );
  }

  Future<void> deleteTransaction(int id) async {
    await _db.customUpdate(
      'DELETE FROM transactions WHERE id = ?',
      variables: [Variable<int>(id)],
      updates: const {},
      updateKind: UpdateKind.delete,
    );
  }

  Stream<List<FlexiTransactionModel>> watchFlexiTransactions(int sessionId) {
    return _db
        .customSelect(
          'SELECT * FROM flexi_transactions WHERE session_id = ? ORDER BY timestamp DESC',
          variables: [Variable<int>(sessionId)],
          readsFrom: const {},
        )
        .watch()
        .map((rows) => rows.map((row) => _mapFlexi(row.data)).toList());
  }

  Future<int> insertFlexiTransaction(FlexiTransactionModel transaction) {
    return _db.customInsert(
      'INSERT INTO flexi_transactions(session_id, user_id, amount, description, timestamp, is_paid) VALUES(?, ?, ?, ?, ?, ?)',
      variables: [
        Variable<int>(transaction.sessionId),
        Variable<int>(transaction.userId),
        Variable<double>(transaction.amount),
        Variable<String?>(transaction.description),
        Variable<String>(transaction.timestamp.toIso8601String()),
        Variable<int>(transaction.isPaid ? 1 : 0),
      ],
    );
  }

  Future<void> markFlexiPaid(int id, bool isPaid) async {
    await _db.customUpdate(
      'UPDATE flexi_transactions SET is_paid = ? WHERE id = ?',
      variables: [Variable<int>(isPaid ? 1 : 0), Variable<int>(id)],
      updates: const {},
      updateKind: UpdateKind.update,
    );
  }

  Future<void> deleteFlexiTransaction(int id) async {
    await _db.customUpdate(
      'DELETE FROM flexi_transactions WHERE id = ?',
      variables: [Variable<int>(id)],
      updates: const {},
      updateKind: UpdateKind.delete,
    );
  }

  Future<double> sumExpenses(int sessionId) async {
    final row = await _db.customSelect(
      'SELECT IFNULL(SUM(amount), 0) AS total FROM transactions WHERE session_id = ? AND type = "expense"',
      variables: [Variable<int>(sessionId)],
      readsFrom: const {},
    ).getSingle();
    return (row.data['total'] as num).toDouble();
  }

  Future<double> sumFlexiAdditions(int sessionId) async {
    final row = await _db.customSelect(
      'SELECT IFNULL(SUM(amount), 0) AS total FROM flexi_transactions WHERE session_id = ?',
      variables: [Variable<int>(sessionId)],
      readsFrom: const {},
    ).getSingle();
    return (row.data['total'] as num).toDouble();
  }

  Future<double> sumFlexiPaid(int sessionId) async {
    final row = await _db.customSelect(
      'SELECT IFNULL(SUM(amount), 0) AS total FROM flexi_transactions WHERE session_id = ? AND is_paid = 1',
      variables: [Variable<int>(sessionId)],
      readsFrom: const {},
    ).getSingle();
    return (row.data['total'] as num).toDouble();
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

  CashTransactionModel _mapTransaction(Map<String, Object?> data) {
    return CashTransactionModel(
      id: data['id'] as int?,
      sessionId: data['session_id'] as int,
      type: (data['type'] as String) == 'income'
          ? TransactionType.income
          : TransactionType.expense,
      amount: (data['amount'] as num).toDouble(),
      description: data['description'] as String?,
      timestamp: DateTime.parse(data['timestamp'] as String),
    );
  }

  FlexiTransactionModel _mapFlexi(Map<String, Object?> data) {
    return FlexiTransactionModel(
      id: data['id'] as int?,
      sessionId: data['session_id'] as int,
      userId: data['user_id'] as int,
      amount: (data['amount'] as num).toDouble(),
      description: data['description'] as String?,
      timestamp: DateTime.parse(data['timestamp'] as String),
      isPaid: (data['is_paid'] as int) == 1,
    );
  }
}
