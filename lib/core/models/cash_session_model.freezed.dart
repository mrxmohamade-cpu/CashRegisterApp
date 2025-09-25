// coverage:ignore-file
// MANUALLY AUTHORED FREEZED-LIKE CODE.
// ignore_for_file: type=lint

part of 'cash_session_model.dart';

T _$identity<T>(T value) => value;

CashSessionModel _$CashSessionModelFromJson(Map<String, dynamic> json) {
  return _CashSessionModel.fromJson(json);
}

mixin _$CashSessionModel {
  int? get id => throw UnimplementedError();
  int get userId => throw UnimplementedError();
  DateTime get startTime => throw UnimplementedError();
  DateTime? get endTime => throw UnimplementedError();
  double get startBalance => throw UnimplementedError();
  double? get endBalance => throw UnimplementedError();
  SessionStatus get status => throw UnimplementedError();
  String? get notes => throw UnimplementedError();
  double get startFlexi => throw UnimplementedError();
  double? get endFlexi => throw UnimplementedError();

  Map<String, dynamic> toJson() => throw UnimplementedError();
  @JsonKey(ignore: true)
  $CashSessionModelCopyWith<CashSessionModel> get copyWith => throw UnimplementedError();
}

abstract class $CashSessionModelCopyWith<$Res> {
  factory $CashSessionModelCopyWith(
          CashSessionModel value, $Res Function(CashSessionModel) then) =
      _$CashSessionModelCopyWithImpl<$Res, CashSessionModel>;
  $Res call({
    int? id,
    int userId,
    DateTime startTime,
    DateTime? endTime,
    double startBalance,
    double? endBalance,
    SessionStatus status,
    String? notes,
    double startFlexi,
    double? endFlexi,
  });
}

class _$CashSessionModelCopyWithImpl<$Res, $Val extends CashSessionModel>
    implements $CashSessionModelCopyWith<$Res> {
  _$CashSessionModelCopyWithImpl(this._value, this._then);

  final $Val _value;
  final $Res Function($Val) _then;

  @override
  $Res call({
    Object? id = freezed,
    Object? userId = null,
    Object? startTime = null,
    Object? endTime = freezed,
    Object? startBalance = null,
    Object? endBalance = freezed,
    Object? status = null,
    Object? notes = freezed,
    Object? startFlexi = null,
    Object? endFlexi = freezed,
  }) {
    return _then(_value.copyWith(
      id: id == freezed ? _value.id : id as int?,
      userId: userId == null ? _value.userId : userId as int,
      startTime: startTime == null ? _value.startTime : startTime as DateTime,
      endTime: endTime == freezed ? _value.endTime : endTime as DateTime?,
      startBalance:
          startBalance == null ? _value.startBalance : startBalance as double,
      endBalance: endBalance == freezed ? _value.endBalance : endBalance as double?,
      status: status == null ? _value.status : status as SessionStatus,
      notes: notes == freezed ? _value.notes : notes as String?,
      startFlexi: startFlexi == null ? _value.startFlexi : startFlexi as double,
      endFlexi: endFlexi == freezed ? _value.endFlexi : endFlexi as double?,
    ) as $Val);
  }
}

abstract class _$$_CashSessionModelCopyWith<$Res>
    implements $CashSessionModelCopyWith<$Res> {
  factory _$$_CashSessionModelCopyWith(
          _$_CashSessionModel value, $Res Function(_$_CashSessionModel) then) =
      __$$_CashSessionModelCopyWithImpl<$Res>;
  @override
  $Res call({
    int? id,
    int userId,
    DateTime startTime,
    DateTime? endTime,
    double startBalance,
    double? endBalance,
    SessionStatus status,
    String? notes,
    double startFlexi,
    double? endFlexi,
  });
}

class __$$_CashSessionModelCopyWithImpl<$Res>
    extends _$CashSessionModelCopyWithImpl<$Res, _$_CashSessionModel>
    implements _$$_CashSessionModelCopyWith<$Res> {
  __$$_CashSessionModelCopyWithImpl(
      _$_CashSessionModel _value, $Res Function(_$_CashSessionModel) _then)
      : super(_value, _then);
}

@JsonSerializable()
class _$_CashSessionModel extends _CashSessionModel {
  const _$_CashSessionModel({
    this.id,
    required this.userId,
    required this.startTime,
    this.endTime,
    this.startBalance = 0.0,
    this.endBalance,
    this.status = SessionStatus.open,
    this.notes,
    this.startFlexi = 0.0,
    this.endFlexi,
  }) : super._();

  factory _$_CashSessionModel.fromJson(Map<String, dynamic> json) =>
      _$$_CashSessionModelFromJson(json);

  @override
  final int? id;
  @override
  final int userId;
  @override
  final DateTime startTime;
  @override
  final DateTime? endTime;
  @override
  @JsonKey()
  final double startBalance;
  @override
  final double? endBalance;
  @override
  @JsonKey()
  final SessionStatus status;
  @override
  final String? notes;
  @override
  @JsonKey()
  final double startFlexi;
  @override
  final double? endFlexi;

  @override
  String toString() {
    return 'CashSessionModel(id: $id, userId: $userId, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$_CashSessionModel &&
            other.id == id &&
            other.userId == userId &&
            other.startTime == startTime &&
            other.endTime == endTime &&
            other.startBalance == startBalance &&
            other.endBalance == endBalance &&
            other.status == status &&
            other.notes == notes &&
            other.startFlexi == startFlexi &&
            other.endFlexi == endFlexi);
  }

  @override
  int get hashCode => Object.hash(runtimeType, id, userId, startTime, endTime,
      startBalance, endBalance, status, notes, startFlexi, endFlexi);

  @override
  @JsonKey(ignore: true)
  _$$_CashSessionModelCopyWith<_$_CashSessionModel> get copyWith =>
      __$$_CashSessionModelCopyWithImpl<_$_CashSessionModel>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_CashSessionModelToJson(this);
  }
}

abstract class _CashSessionModel extends CashSessionModel {
  const factory _CashSessionModel({
    final int? id,
    required final int userId,
    required final DateTime startTime,
    final DateTime? endTime,
    final double startBalance,
    final double? endBalance,
    final SessionStatus status,
    final String? notes,
    final double startFlexi,
    final double? endFlexi,
  }) = _$_CashSessionModel;
  const _CashSessionModel._() : super._();

  factory _CashSessionModel.fromJson(Map<String, dynamic> json) =
      _$_CashSessionModel.fromJson;

  @override
  int? get id;
  @override
  int get userId;
  @override
  DateTime get startTime;
  @override
  DateTime? get endTime;
  @override
  double get startBalance;
  @override
  double? get endBalance;
  @override
  SessionStatus get status;
  @override
  String? get notes;
  @override
  double get startFlexi;
  @override
  double? get endFlexi;
  @override
  @JsonKey(ignore: true)
  _$$_CashSessionModelCopyWith<_$_CashSessionModel> get copyWith;
}
