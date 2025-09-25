// GENERATED CODE - MANUAL JSON SERIALIZABLE.
// ignore_for_file: type=lint

part of 'cash_transaction_model.dart';

_$_CashTransactionModel _$$_CashTransactionModelFromJson(
        Map<String, dynamic> json) =>
    _$_CashTransactionModel(
      id: json['id'] as int?,
      sessionId: json['session_id'] as int,
      type: _$enumDecodeNullable(_$TransactionTypeEnumMap, json['type']) ??
          TransactionType.expense,
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      description: json['description'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );

Map<String, dynamic> _$$_CashTransactionModelToJson(
        _$_CashTransactionModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'session_id': instance.sessionId,
      'type': _$TransactionTypeEnumMap[instance.type],
      'amount': instance.amount,
      'description': instance.description,
      'timestamp': instance.timestamp.toIso8601String(),
    };

const _$TransactionTypeEnumMap = {
  TransactionType.expense: 'expense',
  TransactionType.income: 'income',
};

T? _$enumDecodeNullable<T>(Map<T, dynamic> enumValues, dynamic source,
    {T? unknownValue}) {
  if (source == null) {
    return null;
  }
  return _$enumDecode(enumValues, source, unknownValue: unknownValue);
}

T _$enumDecode<T>(Map<T, dynamic> enumValues, dynamic source,
    {T? unknownValue}) {
  if (source == null) {
    throw ArgumentError('A value must be provided.');
  }
  final entry = enumValues.entries.firstWhere(
    (element) => element.value == source,
    orElse: () {
      if (unknownValue == null) {
        throw ArgumentError('`$source` is not one of the supported values.');
      }
      return MapEntry(unknownValue, enumValues.values.first);
    },
  );
  return entry.key;
}
