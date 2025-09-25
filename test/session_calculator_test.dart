import 'package:flutter_test/flutter_test.dart';

import 'package:cash_register_app/core/models/cash_session_model.dart';
import 'package:cash_register_app/core/models/session_status.dart';
import 'package:cash_register_app/core/utils/session_calculator.dart';

void main() {
  group('SessionCalculator', () {
    test('calculates net values correctly when session is closed', () {
      final session = CashSessionModel(
        id: 1,
        userId: 2,
        startTime: DateTime(2024, 1, 1, 8),
        endTime: DateTime(2024, 1, 1, 18),
        startBalance: 1000,
        endBalance: 1500,
        status: SessionStatus.closed,
        startFlexi: 200,
        endFlexi: 150,
      );

      final summary = SessionCalculator.compute(
        session: session,
        totalExpense: 200,
        totalFlexiAdditions: 100,
        totalFlexiPaid: 50,
      );

      expect(summary.netCashDifference, closeTo(1500 - (1000 - 200 + 50), 0.0001));
      expect(summary.flexiConsumed, closeTo((200 + 100) - 150, 0.0001));
      expect(
        summary.totalNetProfit,
        closeTo((1500 - 1000 - 200) + (100 - summary.flexiConsumed), 0.0001),
      );
    });

    test('uses start balances when session still open', () {
      final session = CashSessionModel(
        id: 2,
        userId: 1,
        startTime: DateTime(2024, 2, 2, 8),
        status: SessionStatus.open,
        startBalance: 500,
        startFlexi: 100,
      );

      final summary = SessionCalculator.compute(
        session: session,
        totalExpense: 50,
        totalFlexiAdditions: 20,
        totalFlexiPaid: 0,
      );

      expect(summary.currentFlexi, 100);
      expect(summary.netCashDifference, closeTo(500 - (500 - 50 + 0), 0.0001));
      expect(summary.flexiConsumed, closeTo((100 + 20) - 100, 0.0001));
    });
  });
}
