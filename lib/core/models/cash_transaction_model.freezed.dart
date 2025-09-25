// coverage:ignore-file
// MANUAL FREEZED-LIKE IMPLEMENTATION.
// ignore_for_file: type=lint

part of 'cash_transaction_model.dart';

T _$identity<T>(T value) => value;

CashTransactionModel _$CashTransactionModelFromJson(Map<String, dynamic> json) {
  return _CashTransactionModel.fromJson(json);
}

mixin _$CashTransactionModel {
  int? get id => throw UnimplementedError();
  int get sessionId => throw UnimplementedError();
  TransactionType get type => throw UnimplementedError();
  double get amount => throw UnimplementedError();
  String? get description => throw UnimplementedError();
  DateTime get timestamp => throw UnimplementedError();

  Map<String, dynamic> toJson() => throw UnimplementedError();
  @JsonKey(ignore: true)
  $CashTransactionModelCopyWith<CashTransactionModel> get copyWith =>
      throw UnimplementedError();
}

abstract class $CashTransactionModelCopyWith<$Res> {
  factory $CashTransactionModelCopyWith(CashTransactionModel value,
          $Res Function(CashTransactionModel) then) =
      _$CashTransactionModelCopyWithImpl<$Res, CashTransactionModel>;
  $Res call({
    int? id,
    int sessionId,
    TransactionType type,
    double amount,
    String? description,
    DateTime timestamp,
  });
}

class _$CashTransactionModelCopyWithImpl<$Res, $Val extends CashTransactionModel>
    implements $CashTransactionModelCopyWith<$Res> {
  _$CashTransactionModelCopyWithImpl(this._value, this._then);

  final $Val _value;
  final $Res Function($Val) _then;

  @override
  $Res call({
    Object? id = freezed,
    Object? sessionId = null,
    Object? type = null,
    Object? amount = null,
    Object? description = freezed,
    Object? timestamp = null,
  }) {
    return _then(_value.copyWith(
      id: id == freezed ? _value.id : id as int?,
      sessionId: sessionId == null ? _value.sessionId : sessionId as int,
      type: type == null ? _value.type : type as TransactionType,
      amount: amount == null ? _value.amount : amount as double,
      description:
          description == freezed ? _value.description : description as String?,
      timestamp: timestamp == null ? _value.timestamp : timestamp as DateTime,
    ) as $Val);
  }
}

abstract class _$$_CashTransactionModelCopyWith<$Res>
    implements $CashTransactionModelCopyWith<$Res> {
  factory _$$_CashTransactionModelCopyWith(_$_CashTransactionModel value,
          $Res Function(_$_CashTransactionModel) then) =
      __$$_CashTransactionModelCopyWithImpl<$Res>;
  @override
  $Res call({
    int? id,
    int sessionId,
    TransactionType type,
    double amount,
    String? description,
    DateTime timestamp,
  });
}

class __$$_CashTransactionModelCopyWithImpl<$Res>
    extends _$CashTransactionModelCopyWithImpl<$Res, _$_CashTransactionModel>
    implements _$$_CashTransactionModelCopyWith<$Res> {
  __$$_CashTransactionModelCopyWithImpl(_$_CashTransactionModel _value,
      $Res Function(_$_CashTransactionModel) _then)
      : super(_value, _then);
}

@JsonSerializable()
class _$_CashTransactionModel extends _CashTransactionModel {
  const _$_CashTransactionModel({
    this.id,
    required this.sessionId,
    this.type = TransactionType.expense,
    this.amount = 0.0,
    this.description,
    required this.timestamp,
  }) : super._();

  factory _$_CashTransactionModel.fromJson(Map<String, dynamic> json) =>
      _$$_CashTransactionModelFromJson(json);

  @override
  final int? id;
  @override
  final int sessionId;
  @override
  @JsonKey()
  final TransactionType type;
  @override
  @JsonKey()
  final double amount;
  @override
  final String? description;
  @override
  final DateTime timestamp;

  @override
  String toString() {
    return 'CashTransactionModel(id: $id, sessionId: $sessionId, amount: $amount)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$_CashTransactionModel &&
            other.id == id &&
            other.sessionId == sessionId &&
            other.type == type &&
            other.amount == amount &&
            other.description == description &&
            other.timestamp == timestamp);
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, id, sessionId, type, amount, description, timestamp);

  @override
  @JsonKey(ignore: true)
  _$$_CashTransactionModelCopyWith<_$_CashTransactionModel> get copyWith =>
      __$$_CashTransactionModelCopyWithImpl<_$_CashTransactionModel>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_CashTransactionModelToJson(this);
  }
}

abstract class _CashTransactionModel extends CashTransactionModel {
  const factory _CashTransactionModel({
    final int? id,
    required final int sessionId,
    final TransactionType type,
    final double amount,
    final String? description,
    required final DateTime timestamp,
  }) = _$_CashTransactionModel;
  const _CashTransactionModel._() : super._();

  factory _CashTransactionModel.fromJson(Map<String, dynamic> json) =
      _$_CashTransactionModel.fromJson;

  @override
  int? get id;
  @override
  int get sessionId;
  @override
  TransactionType get type;
  @override
  double get amount;
  @override
  String? get description;
  @override
  DateTime get timestamp;
  @override
  @JsonKey(ignore: true)
  _$$_CashTransactionModelCopyWith<_$_CashTransactionModel> get copyWith;
}
