// GENERATED CODE - MANUAL JSON SERIALIZABLE.
// ignore_for_file: type=lint

part of 'flexi_transaction_model.dart';

_$_FlexiTransactionModel _$$_FlexiTransactionModelFromJson(
        Map<String, dynamic> json) =>
    _$_FlexiTransactionModel(
      id: json['id'] as int?,
      sessionId: json['session_id'] as int,
      userId: json['user_id'] as int,
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      description: json['description'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
      isPaid: json['is_paid'] as bool? ?? false,
    );

Map<String, dynamic> _$$_FlexiTransactionModelToJson(
        _$_FlexiTransactionModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'session_id': instance.sessionId,
      'user_id': instance.userId,
      'amount': instance.amount,
      'description': instance.description,
      'timestamp': instance.timestamp.toIso8601String(),
      'is_paid': instance.isPaid,
    };
