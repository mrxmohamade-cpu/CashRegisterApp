import 'package:freezed_annotation/freezed_annotation.dart';

import 'session_status.dart';

part 'cash_session_model.freezed.dart';
part 'cash_session_model.g.dart';

@freezed
class CashSessionModel with _$CashSessionModel {
  const factory CashSessionModel({
    int? id,
    required int userId,
    required DateTime startTime,
    DateTime? endTime,
    @Default(0.0) double startBalance,
    double? endBalance,
    @Default(SessionStatus.open) SessionStatus status,
    String? notes,
    @JsonKey(defaultValue: 0.0) double startFlexi,
    double? endFlexi,
  }) = _CashSessionModel;

  const CashSessionModel._();

  factory CashSessionModel.fromJson(Map<String, dynamic> json) => _$CashSessionModelFromJson(json);

  bool get isOpen => status == SessionStatus.open;
}
