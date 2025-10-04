import 'package:freezed_annotation/freezed_annotation.dart';

part 'admin_metrics.freezed.dart';
part 'admin_metrics.g.dart';

@freezed
class AdminDashboardMetrics with _$AdminDashboardMetrics {
  const factory AdminDashboardMetrics({
    @Default(0) int sessionCount,
    @Default(0.0) double totalExpenses,
    @Default(0.0) double totalFlexiAdditions,
    @Default(0.0) double netCashDifference,
    @Default(0.0) double flexiConsumed,
  }) = _AdminDashboardMetrics;

  factory AdminDashboardMetrics.fromJson(Map<String, dynamic> json) => _$AdminDashboardMetricsFromJson(json);
}
