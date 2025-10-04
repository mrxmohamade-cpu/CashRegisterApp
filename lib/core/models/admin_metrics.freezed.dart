// coverage:ignore-file
// MANUAL FREEZED CODE.
// ignore_for_file: type=lint

part of 'admin_metrics.dart';

T _$identity<T>(T value) => value;

AdminDashboardMetrics _$AdminDashboardMetricsFromJson(
    Map<String, dynamic> json) {
  return _AdminDashboardMetrics.fromJson(json);
}

mixin _$AdminDashboardMetrics {
  int get sessionCount => throw UnimplementedError();
  double get totalExpenses => throw UnimplementedError();
  double get totalFlexiAdditions => throw UnimplementedError();
  double get netCashDifference => throw UnimplementedError();
  double get flexiConsumed => throw UnimplementedError();

  Map<String, dynamic> toJson() => throw UnimplementedError();
  @JsonKey(ignore: true)
  $AdminDashboardMetricsCopyWith<AdminDashboardMetrics> get copyWith =>
      throw UnimplementedError();
}

abstract class $AdminDashboardMetricsCopyWith<$Res> {
  factory $AdminDashboardMetricsCopyWith(AdminDashboardMetrics value,
          $Res Function(AdminDashboardMetrics) then) =
      _$AdminDashboardMetricsCopyWithImpl<$Res, AdminDashboardMetrics>;
  $Res call({
    int sessionCount,
    double totalExpenses,
    double totalFlexiAdditions,
    double netCashDifference,
    double flexiConsumed,
  });
}

class _$AdminDashboardMetricsCopyWithImpl<$Res,
        $Val extends AdminDashboardMetrics>
    implements $AdminDashboardMetricsCopyWith<$Res> {
  _$AdminDashboardMetricsCopyWithImpl(this._value, this._then);

  final $Val _value;
  final $Res Function($Val) _then;

  @override
  $Res call({
    Object? sessionCount = null,
    Object? totalExpenses = null,
    Object? totalFlexiAdditions = null,
    Object? netCashDifference = null,
    Object? flexiConsumed = null,
  }) {
    return _then(_value.copyWith(
      sessionCount:
          sessionCount == null ? _value.sessionCount : sessionCount as int,
      totalExpenses:
          totalExpenses == null ? _value.totalExpenses : totalExpenses as double,
      totalFlexiAdditions: totalFlexiAdditions == null
          ? _value.totalFlexiAdditions
          : totalFlexiAdditions as double,
      netCashDifference: netCashDifference == null
          ? _value.netCashDifference
          : netCashDifference as double,
      flexiConsumed:
          flexiConsumed == null ? _value.flexiConsumed : flexiConsumed as double,
    ) as $Val);
  }
}

abstract class _$$_AdminDashboardMetricsCopyWith<$Res>
    implements $AdminDashboardMetricsCopyWith<$Res> {
  factory _$$_AdminDashboardMetricsCopyWith(_$_AdminDashboardMetrics value,
          $Res Function(_$_AdminDashboardMetrics) then) =
      __$$_AdminDashboardMetricsCopyWithImpl<$Res>;
  @override
  $Res call({
    int sessionCount,
    double totalExpenses,
    double totalFlexiAdditions,
    double netCashDifference,
    double flexiConsumed,
  });
}

class __$$_AdminDashboardMetricsCopyWithImpl<$Res>
    extends _$AdminDashboardMetricsCopyWithImpl<$Res, _$_AdminDashboardMetrics>
    implements _$$_AdminDashboardMetricsCopyWith<$Res> {
  __$$_AdminDashboardMetricsCopyWithImpl(
      _$_AdminDashboardMetrics _value,
      $Res Function(_$_AdminDashboardMetrics) _then)
      : super(_value, _then);
}

@JsonSerializable()
class _$_AdminDashboardMetrics implements _AdminDashboardMetrics {
  const _$_AdminDashboardMetrics({
    this.sessionCount = 0,
    this.totalExpenses = 0.0,
    this.totalFlexiAdditions = 0.0,
    this.netCashDifference = 0.0,
    this.flexiConsumed = 0.0,
  });

  factory _$_AdminDashboardMetrics.fromJson(Map<String, dynamic> json) =>
      _$$_AdminDashboardMetricsFromJson(json);

  @override
  @JsonKey()
  final int sessionCount;
  @override
  @JsonKey()
  final double totalExpenses;
  @override
  @JsonKey()
  final double totalFlexiAdditions;
  @override
  @JsonKey()
  final double netCashDifference;
  @override
  @JsonKey()
  final double flexiConsumed;

  @override
  String toString() {
    return 'AdminDashboardMetrics(sessionCount: $sessionCount, totalExpenses: $totalExpenses)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$_AdminDashboardMetrics &&
            other.sessionCount == sessionCount &&
            other.totalExpenses == totalExpenses &&
            other.totalFlexiAdditions == totalFlexiAdditions &&
            other.netCashDifference == netCashDifference &&
            other.flexiConsumed == flexiConsumed);
  }

  @override
  int get hashCode => Object.hash(runtimeType, sessionCount, totalExpenses,
      totalFlexiAdditions, netCashDifference, flexiConsumed);

  @override
  @JsonKey(ignore: true)
  _$$_AdminDashboardMetricsCopyWith<_$_AdminDashboardMetrics> get copyWith =>
      __$$_AdminDashboardMetricsCopyWithImpl<_$_AdminDashboardMetrics>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_AdminDashboardMetricsToJson(this);
  }
}

abstract class _AdminDashboardMetrics implements AdminDashboardMetrics {
  const factory _AdminDashboardMetrics({
    final int sessionCount,
    final double totalExpenses,
    final double totalFlexiAdditions,
    final double netCashDifference,
    final double flexiConsumed,
  }) = _$_AdminDashboardMetrics;

  factory _AdminDashboardMetrics.fromJson(Map<String, dynamic> json) =
      _$_AdminDashboardMetrics.fromJson;

  @override
  int get sessionCount;
  @override
  double get totalExpenses;
  @override
  double get totalFlexiAdditions;
  @override
  double get netCashDifference;
  @override
  double get flexiConsumed;
  @override
  @JsonKey(ignore: true)
  _$$_AdminDashboardMetricsCopyWith<_$_AdminDashboardMetrics> get copyWith;
}
