import 'package:freezed_annotation/freezed_annotation.dart';

@JsonEnum(fieldRename: FieldRename.snake)
enum SessionStatus {
  open,
  closed,
}

extension SessionStatusX on SessionStatus {
  String get displayName {
    switch (this) {
      case SessionStatus.open:
        return 'مفتوحة';
      case SessionStatus.closed:
        return 'مغلقة';
    }
  }
}
