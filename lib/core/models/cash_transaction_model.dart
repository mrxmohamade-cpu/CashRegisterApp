import 'package:freezed_annotation/freezed_annotation.dart';

import 'transaction_type.dart';

part 'cash_transaction_model.freezed.dart';
part 'cash_transaction_model.g.dart';

@freezed
class CashTransactionModel with _$CashTransactionModel {
  const factory CashTransactionModel({
    int? id,
    required int sessionId,
    @Default(TransactionType.expense) TransactionType type,
    @Default(0.0) double amount,
    String? description,
    required DateTime timestamp,
  }) = _CashTransactionModel;

  const CashTransactionModel._();

  factory CashTransactionModel.fromJson(Map<String, dynamic> json) => _$CashTransactionModelFromJson(json);

  bool get isExpense => type == TransactionType.expense;
}
