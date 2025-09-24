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
    return _insertAndReturnId(
      'INSERT INTO cash_sessions(user_id, start_time, start_balance, status, start_flexi) VALUES(?, ?, ?, ?, ?)',
      [
        userId,
        DateTime.now().toIso8601String(),
        startBalance,
        SessionStatus.open.name,
        startFlexi,
      ],
    );
  }

  Future<void> updateSessionNotes(int sessionId, String notes) async {
    await _db.customStatement(
      'UPDATE cash_sessions SET notes = ? WHERE id = ?',
      [notes, sessionId],
    );
  }

  Future<void> closeSession({
    required int sessionId,
    required double endBalance,
    required double endFlexi,
  }) async {
    await _db.customStatement(
      'UPDATE cash_sessions SET end_time = ?, end_balance = ?, end_flexi = ?, status = ? WHERE id = ?',
      [
        DateTime.now().toIso8601String(),
        endBalance,
        endFlexi,
        SessionStatus.closed.name,
        sessionId,
      ],
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
    return _insertAndReturnId(
      'INSERT INTO transactions(session_id, type, amount, description, timestamp) VALUES(?, ?, ?, ?, ?)',
      [
        transaction.sessionId,
        transaction.type.name,
        transaction.amount,
        transaction.description,
        transaction.timestamp.toIso8601String(),
      ],
    );
  }

  Future<void> updateTransaction(CashTransactionModel transaction) async {
    final id = transaction.id;
    if (id == null) {
      throw ArgumentError('Transaction must have an id before it can be updated.');
    }
    await _db.customStatement(
      'UPDATE transactions SET type = ?, amount = ?, description = ?, timestamp = ? WHERE id = ?',
      [
        transaction.type.name,
        transaction.amount,
        transaction.description,
        transaction.timestamp.toIso8601String(),
        id,
      ],
    );
  }

  Future<void> deleteTransaction(int id) async {
    await _db.customStatement(
      'DELETE FROM transactions WHERE id = ?',
      [id],
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
    return _insertAndReturnId(
      'INSERT INTO flexi_transactions(session_id, user_id, amount, description, timestamp, is_paid) VALUES(?, ?, ?, ?, ?, ?)',
      [
        transaction.sessionId,
        transaction.userId,
        transaction.amount,
        transaction.description,
        transaction.timestamp.toIso8601String(),
        transaction.isPaid ? 1 : 0,
      ],
    );
  }

  Future<void> markFlexiPaid(int id, bool isPaid) async {
    await _db.customStatement(
      'UPDATE flexi_transactions SET is_paid = ? WHERE id = ?',
      [isPaid ? 1 : 0, id],
    );
  }

  Future<void> deleteFlexiTransaction(int id) async {
    await _db.customStatement(
      'DELETE FROM flexi_transactions WHERE id = ?',
      [id],
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

  Future<int> _insertAndReturnId(String sql, List<Object?> args) async {
    await _db.customStatement(sql, args);
    final row = await _db
        .customSelect('SELECT last_insert_rowid() AS id')
        .getSingle();
    return row.data['id'] as int;
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
