// GENERATED CODE - MANUAL JSON SERIALIZABLE.
// ignore_for_file: type=lint

part of 'session_summary.dart';

_$_SessionSummary _$$_SessionSummaryFromJson(Map<String, dynamic> json) =>
    _$_SessionSummary(
      startBalance: (json['start_balance'] as num?)?.toDouble() ?? 0.0,
      totalExpense: (json['total_expense'] as num?)?.toDouble() ?? 0.0,
      currentFlexi: (json['current_flexi'] as num?)?.toDouble() ?? 0.0,
      netCashDifference:
          (json['net_cash_difference'] as num?)?.toDouble() ?? 0.0,
      flexiConsumed: (json['flexi_consumed'] as num?)?.toDouble() ?? 0.0,
      totalNetProfit: (json['total_net_profit'] as num?)?.toDouble() ?? 0.0,
      totalFlexiAdditions:
          (json['total_flexi_additions'] as num?)?.toDouble() ?? 0.0,
      totalFlexiPaid: (json['total_flexi_paid'] as num?)?.toDouble() ?? 0.0,
    );

Map<String, dynamic> _$$_SessionSummaryToJson(_$_SessionSummary instance) =>
    <String, dynamic>{
      'start_balance': instance.startBalance,
      'total_expense': instance.totalExpense,
      'current_flexi': instance.currentFlexi,
      'net_cash_difference': instance.netCashDifference,
      'flexi_consumed': instance.flexiConsumed,
      'total_net_profit': instance.totalNetProfit,
      'total_flexi_additions': instance.totalFlexiAdditions,
      'total_flexi_paid': instance.totalFlexiPaid,
    };
