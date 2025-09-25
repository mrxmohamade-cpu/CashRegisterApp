import '../models/cash_session_model.dart';
import '../models/session_summary.dart';

class SessionCalculator {
  const SessionCalculator._();

  static SessionSummary compute({
    required CashSessionModel session,
    required double totalExpense,
    required double totalFlexiAdditions,
    required double totalFlexiPaid,
  }) {
    final endBalance = session.endBalance ?? session.startBalance;
    final endFlexi = session.endFlexi ?? session.startFlexi;
    final netCashDifference = endBalance -
        (session.startBalance - totalExpense + totalFlexiPaid);
    final flexiConsumed = (session.startFlexi + totalFlexiAdditions) - endFlexi;
    final totalNetProfit = (endBalance - session.startBalance - totalExpense) +
        (totalFlexiAdditions - flexiConsumed);

    return SessionSummary(
      startBalance: session.startBalance,
      totalExpense: totalExpense,
      currentFlexi: endFlexi,
      netCashDifference: netCashDifference,
      flexiConsumed: flexiConsumed,
      totalNetProfit: totalNetProfit,
      totalFlexiAdditions: totalFlexiAdditions,
      totalFlexiPaid: totalFlexiPaid,
    );
  }
}
