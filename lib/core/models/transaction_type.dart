import 'package:freezed_annotation/freezed_annotation.dart';

@JsonEnum(fieldRename: FieldRename.snake)
enum TransactionType {
  expense,
  income,
}

extension TransactionTypeX on TransactionType {
  String get displayName {
    switch (this) {
      case TransactionType.expense:
        return 'مصروف';
      case TransactionType.income:
        return 'إيراد';
    }
  }
}
