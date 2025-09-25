import 'package:freezed_annotation/freezed_annotation.dart';

import 'user_role.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@freezed
class UserModel with _$UserModel {
  const factory UserModel({
    int? id,
    required String username,
    required String hashedPassword,
    @Default(UserRole.user) UserRole role,
  }) = _UserModel;

  const UserModel._();

  factory UserModel.fromJson(Map<String, dynamic> json) => _$UserModelFromJson(json);

  bool get isAdmin => role == UserRole.admin;
}
