import 'package:drift/drift.dart';

import '../db/app_database.dart';
import '../repo/session_repository.dart';
import '../models/admin_metrics.dart';
import '../models/cash_session_model.dart';
import '../models/session_status.dart';
import '../models/session_summary.dart';

class AdminRepository {
  AdminRepository(this._db, this._sessionRepository);

  final AppDatabase _db;
  final SessionRepository _sessionRepository;

  Future<AdminDashboardMetrics> loadMetrics({DateTime? from, DateTime? to}) async {
    final sessions = await fetchSessions(from: from, to: to);
    double totalExpenses = 0;
    double totalFlexiAdditions = 0;
    double netCashDiff = 0;
    double flexiConsumed = 0;

    for (final session in sessions) {
      final summary = await _sessionRepository.buildSummary(session);
      totalExpenses += summary.totalExpense;
      totalFlexiAdditions += summary.totalFlexiAdditions;
      netCashDiff += summary.netCashDifference;
      flexiConsumed += summary.flexiConsumed;
    }

    return AdminDashboardMetrics(
      sessionCount: sessions.length,
      totalExpenses: totalExpenses,
      totalFlexiAdditions: totalFlexiAdditions,
      netCashDifference: netCashDiff,
      flexiConsumed: flexiConsumed,
    );
  }

  Future<List<CashSessionModel>> fetchSessions({
    int? userId,
    DateTime? from,
    DateTime? to,
  }) {
    return _sessionRepository.filterSessions(userId: userId, from: from, to: to);
  }

  Future<Map<DateTime, double>> loadDailyExpenses({
    required int userId,
    required DateTime month,
  }) async {
    final firstDay = DateTime(month.year, month.month, 1);
    final lastDay = DateTime(month.year, month.month + 1, 0, 23, 59, 59);
    final rows = await _db.customSelect(
      'SELECT DATE(timestamp) as day, IFNULL(SUM(amount),0) as total '
      'FROM transactions t INNER JOIN cash_sessions cs ON cs.id = t.session_id '
      'WHERE cs.user_id = ? AND t.type = "expense" AND timestamp BETWEEN ? AND ? '
      'GROUP BY DATE(timestamp) ORDER BY DATE(timestamp)',
      variables: [
        Variable<int>(userId),
        Variable<String>(firstDay.toIso8601String()),
        Variable<String>(lastDay.toIso8601String()),
      ],
      readsFrom: const {},
    ).get();

    return Map.fromEntries(rows.map((row) {
      final day = DateTime.parse(row.data['day'] as String);
      final total = (row.data['total'] as num).toDouble();
      return MapEntry(day, total);
    }));
  }

  Future<SessionSummary> sessionSummary(int sessionId) async {
    final row = await _db.customSelect(
      'SELECT * FROM cash_sessions WHERE id = ? LIMIT 1',
      variables: [Variable<int>(sessionId)],
      readsFrom: const {},
    ).getSingle();
    final model = CashSessionModel(
      id: row.data['id'] as int,
      userId: row.data['user_id'] as int,
      startTime: DateTime.parse(row.data['start_time'] as String),
      endTime: row.data['end_time'] == null
          ? null
          : DateTime.tryParse(row.data['end_time'] as String),
      startBalance: (row.data['start_balance'] as num).toDouble(),
      endBalance: (row.data['end_balance'] as num?)?.toDouble(),
      status: (row.data['status'] as String) == 'open'
          ? SessionStatus.open
          : SessionStatus.closed,
      notes: row.data['notes'] as String?,
      startFlexi: (row.data['start_flexi'] as num?)?.toDouble() ?? 0.0,
      endFlexi: (row.data['end_flexi'] as num?)?.toDouble(),
    );
    return _sessionRepository.buildSummary(model);
  }
}
