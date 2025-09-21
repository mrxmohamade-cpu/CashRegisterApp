// GENERATED CODE - MANUAL JSON SERIALIZABLE.
// ignore_for_file: type=lint

part of 'admin_metrics.dart';

_$_AdminDashboardMetrics _$$_AdminDashboardMetricsFromJson(
        Map<String, dynamic> json) =>
    _$_AdminDashboardMetrics(
      sessionCount: json['session_count'] as int? ?? 0,
      totalExpenses: (json['total_expenses'] as num?)?.toDouble() ?? 0.0,
      totalFlexiAdditions:
          (json['total_flexi_additions'] as num?)?.toDouble() ?? 0.0,
      netCashDifference:
          (json['net_cash_difference'] as num?)?.toDouble() ?? 0.0,
      flexiConsumed: (json['flexi_consumed'] as num?)?.toDouble() ?? 0.0,
    );

Map<String, dynamic> _$$_AdminDashboardMetricsToJson(
        _$_AdminDashboardMetrics instance) =>
    <String, dynamic>{
      'session_count': instance.sessionCount,
      'total_expenses': instance.totalExpenses,
      'total_flexi_additions': instance.totalFlexiAdditions,
      'net_cash_difference': instance.netCashDifference,
      'flexi_consumed': instance.flexiConsumed,
    };
