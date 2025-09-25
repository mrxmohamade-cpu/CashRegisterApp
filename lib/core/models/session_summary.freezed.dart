// coverage:ignore-file
// MANUAL FREEZED OUTPUT.
// ignore_for_file: type=lint

part of 'session_summary.dart';

T _$identity<T>(T value) => value;

SessionSummary _$SessionSummaryFromJson(Map<String, dynamic> json) {
  return _SessionSummary.fromJson(json);
}

mixin _$SessionSummary {
  double get startBalance => throw UnimplementedError();
  double get totalExpense => throw UnimplementedError();
  double get currentFlexi => throw UnimplementedError();
  double get netCashDifference => throw UnimplementedError();
  double get flexiConsumed => throw UnimplementedError();
  double get totalNetProfit => throw UnimplementedError();
  double get totalFlexiAdditions => throw UnimplementedError();
  double get totalFlexiPaid => throw UnimplementedError();

  Map<String, dynamic> toJson() => throw UnimplementedError();
  @JsonKey(ignore: true)
  $SessionSummaryCopyWith<SessionSummary> get copyWith =>
      throw UnimplementedError();
}

abstract class $SessionSummaryCopyWith<$Res> {
  factory $SessionSummaryCopyWith(SessionSummary value,
          $Res Function(SessionSummary) then) =
      _$SessionSummaryCopyWithImpl<$Res, SessionSummary>;
  $Res call({
    double startBalance,
    double totalExpense,
    double currentFlexi,
    double netCashDifference,
    double flexiConsumed,
    double totalNetProfit,
    double totalFlexiAdditions,
    double totalFlexiPaid,
  });
}

class _$SessionSummaryCopyWithImpl<$Res, $Val extends SessionSummary>
    implements $SessionSummaryCopyWith<$Res> {
  _$SessionSummaryCopyWithImpl(this._value, this._then);

  final $Val _value;
  final $Res Function($Val) _then;

  @override
  $Res call({
    Object? startBalance = null,
    Object? totalExpense = null,
    Object? currentFlexi = null,
    Object? netCashDifference = null,
    Object? flexiConsumed = null,
    Object? totalNetProfit = null,
    Object? totalFlexiAdditions = null,
    Object? totalFlexiPaid = null,
  }) {
    return _then(_value.copyWith(
      startBalance:
          startBalance == null ? _value.startBalance : startBalance as double,
      totalExpense:
          totalExpense == null ? _value.totalExpense : totalExpense as double,
      currentFlexi:
          currentFlexi == null ? _value.currentFlexi : currentFlexi as double,
      netCashDifference: netCashDifference == null
          ? _value.netCashDifference
          : netCashDifference as double,
      flexiConsumed:
          flexiConsumed == null ? _value.flexiConsumed : flexiConsumed as double,
      totalNetProfit: totalNetProfit == null
          ? _value.totalNetProfit
          : totalNetProfit as double,
      totalFlexiAdditions: totalFlexiAdditions == null
          ? _value.totalFlexiAdditions
          : totalFlexiAdditions as double,
      totalFlexiPaid: totalFlexiPaid == null
          ? _value.totalFlexiPaid
          : totalFlexiPaid as double,
    ) as $Val);
  }
}

abstract class _$$_SessionSummaryCopyWith<$Res>
    implements $SessionSummaryCopyWith<$Res> {
  factory _$$_SessionSummaryCopyWith(
          _$_SessionSummary value, $Res Function(_$_SessionSummary) then) =
      __$$_SessionSummaryCopyWithImpl<$Res>;
  @override
  $Res call({
    double startBalance,
    double totalExpense,
    double currentFlexi,
    double netCashDifference,
    double flexiConsumed,
    double totalNetProfit,
    double totalFlexiAdditions,
    double totalFlexiPaid,
  });
}

class __$$_SessionSummaryCopyWithImpl<$Res>
    extends _$SessionSummaryCopyWithImpl<$Res, _$_SessionSummary>
    implements _$$_SessionSummaryCopyWith<$Res> {
  __$$_SessionSummaryCopyWithImpl(
      _$_SessionSummary _value, $Res Function(_$_SessionSummary) _then)
      : super(_value, _then);
}

@JsonSerializable()
class _$_SessionSummary implements _SessionSummary {
  const _$_SessionSummary({
    this.startBalance = 0.0,
    this.totalExpense = 0.0,
    this.currentFlexi = 0.0,
    this.netCashDifference = 0.0,
    this.flexiConsumed = 0.0,
    this.totalNetProfit = 0.0,
    this.totalFlexiAdditions = 0.0,
    this.totalFlexiPaid = 0.0,
  });

  factory _$_SessionSummary.fromJson(Map<String, dynamic> json) =>
      _$$_SessionSummaryFromJson(json);

  @override
  @JsonKey()
  final double startBalance;
  @override
  @JsonKey()
  final double totalExpense;
  @override
  @JsonKey()
  final double currentFlexi;
  @override
  @JsonKey()
  final double netCashDifference;
  @override
  @JsonKey()
  final double flexiConsumed;
  @override
  @JsonKey()
  final double totalNetProfit;
  @override
  @JsonKey()
  final double totalFlexiAdditions;
  @override
  @JsonKey()
  final double totalFlexiPaid;

  @override
  String toString() {
    return 'SessionSummary(startBalance: $startBalance, totalExpense: $totalExpense)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$_SessionSummary &&
            other.startBalance == startBalance &&
            other.totalExpense == totalExpense &&
            other.currentFlexi == currentFlexi &&
            other.netCashDifference == netCashDifference &&
            other.flexiConsumed == flexiConsumed &&
            other.totalNetProfit == totalNetProfit &&
            other.totalFlexiAdditions == totalFlexiAdditions &&
            other.totalFlexiPaid == totalFlexiPaid);
  }

  @override
  int get hashCode => Object.hash(runtimeType, startBalance, totalExpense,
      currentFlexi, netCashDifference, flexiConsumed, totalNetProfit,
      totalFlexiAdditions, totalFlexiPaid);

  @override
  @JsonKey(ignore: true)
  _$$_SessionSummaryCopyWith<_$_SessionSummary> get copyWith =>
      __$$_SessionSummaryCopyWithImpl<_$_SessionSummary>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_SessionSummaryToJson(this);
  }
}

abstract class _SessionSummary implements SessionSummary {
  const factory _SessionSummary({
    final double startBalance,
    final double totalExpense,
    final double currentFlexi,
    final double netCashDifference,
    final double flexiConsumed,
    final double totalNetProfit,
    final double totalFlexiAdditions,
    final double totalFlexiPaid,
  }) = _$_SessionSummary;

  factory _SessionSummary.fromJson(Map<String, dynamic> json) =
      _$_SessionSummary.fromJson;

  @override
  double get startBalance;
  @override
  double get totalExpense;
  @override
  double get currentFlexi;
  @override
  double get netCashDifference;
  @override
  double get flexiConsumed;
  @override
  double get totalNetProfit;
  @override
  double get totalFlexiAdditions;
  @override
  double get totalFlexiPaid;
  @override
  @JsonKey(ignore: true)
  _$$_SessionSummaryCopyWith<_$_SessionSummary> get copyWith;
}
