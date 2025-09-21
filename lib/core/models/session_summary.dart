import 'package:freezed_annotation/freezed_annotation.dart';

part 'session_summary.freezed.dart';
part 'session_summary.g.dart';

@freezed
class SessionSummary with _$SessionSummary {
  const factory SessionSummary({
    @Default(0.0) double startBalance,
    @Default(0.0) double totalExpense,
    @Default(0.0) double currentFlexi,
    @Default(0.0) double netCashDifference,
    @Default(0.0) double flexiConsumed,
    @Default(0.0) double totalNetProfit,
    @Default(0.0) double totalFlexiAdditions,
    @Default(0.0) double totalFlexiPaid,
  }) = _SessionSummary;

  factory SessionSummary.fromJson(Map<String, dynamic> json) => _$SessionSummaryFromJson(json);
}
