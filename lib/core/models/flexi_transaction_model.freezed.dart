// coverage:ignore-file
// MANUAL FREEZED STUB.
// ignore_for_file: type=lint

part of 'flexi_transaction_model.dart';

T _$identity<T>(T value) => value;

FlexiTransactionModel _$FlexiTransactionModelFromJson(
    Map<String, dynamic> json) {
  return _FlexiTransactionModel.fromJson(json);
}

mixin _$FlexiTransactionModel {
  int? get id => throw UnimplementedError();
  int get sessionId => throw UnimplementedError();
  int get userId => throw UnimplementedError();
  double get amount => throw UnimplementedError();
  String? get description => throw UnimplementedError();
  DateTime get timestamp => throw UnimplementedError();
  bool get isPaid => throw UnimplementedError();

  Map<String, dynamic> toJson() => throw UnimplementedError();
  @JsonKey(ignore: true)
  $FlexiTransactionModelCopyWith<FlexiTransactionModel> get copyWith =>
      throw UnimplementedError();
}

abstract class $FlexiTransactionModelCopyWith<$Res> {
  factory $FlexiTransactionModelCopyWith(FlexiTransactionModel value,
          $Res Function(FlexiTransactionModel) then) =
      _$FlexiTransactionModelCopyWithImpl<$Res, FlexiTransactionModel>;
  $Res call({
    int? id,
    int sessionId,
    int userId,
    double amount,
    String? description,
    DateTime timestamp,
    bool isPaid,
  });
}

class _$FlexiTransactionModelCopyWithImpl<$Res, $Val extends FlexiTransactionModel>
    implements $FlexiTransactionModelCopyWith<$Res> {
  _$FlexiTransactionModelCopyWithImpl(this._value, this._then);

  final $Val _value;
  final $Res Function($Val) _then;

  @override
  $Res call({
    Object? id = freezed,
    Object? sessionId = null,
    Object? userId = null,
    Object? amount = null,
    Object? description = freezed,
    Object? timestamp = null,
    Object? isPaid = null,
  }) {
    return _then(_value.copyWith(
      id: id == freezed ? _value.id : id as int?,
      sessionId: sessionId == null ? _value.sessionId : sessionId as int,
      userId: userId == null ? _value.userId : userId as int,
      amount: amount == null ? _value.amount : amount as double,
      description:
          description == freezed ? _value.description : description as String?,
      timestamp: timestamp == null ? _value.timestamp : timestamp as DateTime,
      isPaid: isPaid == null ? _value.isPaid : isPaid as bool,
    ) as $Val);
  }
}

abstract class _$$_FlexiTransactionModelCopyWith<$Res>
    implements $FlexiTransactionModelCopyWith<$Res> {
  factory _$$_FlexiTransactionModelCopyWith(_$_FlexiTransactionModel value,
          $Res Function(_$_FlexiTransactionModel) then) =
      __$$_FlexiTransactionModelCopyWithImpl<$Res>;
  @override
  $Res call({
    int? id,
    int sessionId,
    int userId,
    double amount,
    String? description,
    DateTime timestamp,
    bool isPaid,
  });
}

class __$$_FlexiTransactionModelCopyWithImpl<$Res>
    extends _$FlexiTransactionModelCopyWithImpl<$Res, _$_FlexiTransactionModel>
    implements _$$_FlexiTransactionModelCopyWith<$Res> {
  __$$_FlexiTransactionModelCopyWithImpl(_$_FlexiTransactionModel _value,
      $Res Function(_$_FlexiTransactionModel) _then)
      : super(_value, _then);
}

@JsonSerializable()
class _$_FlexiTransactionModel extends _FlexiTransactionModel {
  const _$_FlexiTransactionModel({
    this.id,
    required this.sessionId,
    required this.userId,
    this.amount = 0.0,
    this.description,
    required this.timestamp,
    this.isPaid = false,
  }) : super._();

  factory _$_FlexiTransactionModel.fromJson(Map<String, dynamic> json) =>
      _$$_FlexiTransactionModelFromJson(json);

  @override
  final int? id;
  @override
  final int sessionId;
  @override
  final int userId;
  @override
  @JsonKey()
  final double amount;
  @override
  final String? description;
  @override
  final DateTime timestamp;
  @override
  @JsonKey()
  final bool isPaid;

  @override
  String toString() {
    return 'FlexiTransactionModel(id: $id, amount: $amount, isPaid: $isPaid)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$_FlexiTransactionModel &&
            other.id == id &&
            other.sessionId == sessionId &&
            other.userId == userId &&
            other.amount == amount &&
            other.description == description &&
            other.timestamp == timestamp &&
            other.isPaid == isPaid);
  }

  @override
  int get hashCode => Object.hash(runtimeType, id, sessionId, userId, amount,
      description, timestamp, isPaid);

  @override
  @JsonKey(ignore: true)
  _$$_FlexiTransactionModelCopyWith<_$_FlexiTransactionModel> get copyWith =>
      __$$_FlexiTransactionModelCopyWithImpl<_$_FlexiTransactionModel>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_FlexiTransactionModelToJson(this);
  }
}

abstract class _FlexiTransactionModel extends FlexiTransactionModel {
  const factory _FlexiTransactionModel({
    final int? id,
    required final int sessionId,
    required final int userId,
    final double amount,
    final String? description,
    required final DateTime timestamp,
    final bool isPaid,
  }) = _$_FlexiTransactionModel;
  const _FlexiTransactionModel._() : super._();

  factory _FlexiTransactionModel.fromJson(Map<String, dynamic> json) =
      _$_FlexiTransactionModel.fromJson;

  @override
  int? get id;
  @override
  int get sessionId;
  @override
  int get userId;
  @override
  double get amount;
  @override
  String? get description;
  @override
  DateTime get timestamp;
  @override
  bool get isPaid;
  @override
  @JsonKey(ignore: true)
  _$$_FlexiTransactionModelCopyWith<_$_FlexiTransactionModel> get copyWith;
}
