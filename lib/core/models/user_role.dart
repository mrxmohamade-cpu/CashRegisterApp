import 'package:freezed_annotation/freezed_annotation.dart';

@JsonEnum(fieldRename: FieldRename.snake)
enum UserRole {
  admin,
  user,
}

extension UserRoleX on UserRole {
  String get displayName {
    switch (this) {
      case UserRole.admin:
        return 'مشرف';
      case UserRole.user:
        return 'عامل';
    }
  }
}
