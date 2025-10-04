// GENERATED CODE - MANUAL JSON SERIALIZABLE STUB.
// ignore_for_file: type=lint

part of 'cash_session_model.dart';

_$_CashSessionModel _$$_CashSessionModelFromJson(Map<String, dynamic> json) =>
    _$_CashSessionModel(
      id: json['id'] as int?,
      userId: json['user_id'] as int,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: json['end_time'] == null
          ? null
          : DateTime.parse(json['end_time'] as String),
      startBalance: (json['start_balance'] as num?)?.toDouble() ?? 0.0,
      endBalance: (json['end_balance'] as num?)?.toDouble(),
      status: _$enumDecodeNullable(_$SessionStatusEnumMap, json['status']) ??
          SessionStatus.open,
      notes: json['notes'] as String?,
      startFlexi: (json['start_flexi'] as num?)?.toDouble() ?? 0.0,
      endFlexi: (json['end_flexi'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$$_CashSessionModelToJson(_$_CashSessionModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'start_time': instance.startTime.toIso8601String(),
      'end_time': instance.endTime?.toIso8601String(),
      'start_balance': instance.startBalance,
      'end_balance': instance.endBalance,
      'status': _$SessionStatusEnumMap[instance.status],
      'notes': instance.notes,
      'start_flexi': instance.startFlexi,
      'end_flexi': instance.endFlexi,
    };

const _$SessionStatusEnumMap = {
  SessionStatus.open: 'open',
  SessionStatus.closed: 'closed',
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
