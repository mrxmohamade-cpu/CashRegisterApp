import 'package:freezed_annotation/freezed_annotation.dart';

part 'flexi_transaction_model.freezed.dart';
part 'flexi_transaction_model.g.dart';

@freezed
class FlexiTransactionModel with _$FlexiTransactionModel {
  const factory FlexiTransactionModel({
    int? id,
    required int sessionId,
    required int userId,
    @Default(0.0) double amount,
    String? description,
    required DateTime timestamp,
    @Default(false) bool isPaid,
  }) = _FlexiTransactionModel;

  const FlexiTransactionModel._();

  factory FlexiTransactionModel.fromJson(Map<String, dynamic> json) => _$FlexiTransactionModelFromJson(json);
}
