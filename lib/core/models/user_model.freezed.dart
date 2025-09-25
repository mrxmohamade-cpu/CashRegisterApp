// coverage:ignore-file
// GENERATED CODE - MANUALLY WRITTEN TO MIMIC FREEZED OUTPUT.
// ignore_for_file: type=lint

part of 'user_model.dart';

T _$identity<T>(T value) => value;

UserModel _$UserModelFromJson(Map<String, dynamic> json) {
  return _UserModel.fromJson(json);
}

mixin _$UserModel {
  int? get id => throw UnimplementedError();
  String get username => throw UnimplementedError();
  String get hashedPassword => throw UnimplementedError();
  UserRole get role => throw UnimplementedError();

  Map<String, dynamic> toJson() => throw UnimplementedError();
  @JsonKey(ignore: true)
  $UserModelCopyWith<UserModel> get copyWith => throw UnimplementedError();
}

abstract class $UserModelCopyWith<$Res> {
  factory $UserModelCopyWith(UserModel value, $Res Function(UserModel) then) =
      _$UserModelCopyWithImpl<$Res, UserModel>;
  $Res call({int? id, String username, String hashedPassword, UserRole role});
}

class _$UserModelCopyWithImpl<$Res, $Val extends UserModel>
    implements $UserModelCopyWith<$Res> {
  _$UserModelCopyWithImpl(this._value, this._then);

  final $Val _value;
  final $Res Function($Val) _then;

  @override
  $Res call({
    Object? id = freezed,
    Object? username = null,
    Object? hashedPassword = null,
    Object? role = null,
  }) {
    return _then(_value.copyWith(
      id: id == freezed ? _value.id : id as int?,
      username: username == null ? _value.username : username as String,
      hashedPassword: hashedPassword == null
          ? _value.hashedPassword
          : hashedPassword as String,
      role: role == null ? _value.role : role as UserRole,
    ) as $Val);
  }
}

abstract class _$$_UserModelCopyWith<$Res> implements $UserModelCopyWith<$Res> {
  factory _$$_UserModelCopyWith(
          _$_UserModel value, $Res Function(_$_UserModel) then) =
      __$$_UserModelCopyWithImpl<$Res>;
  @override
  $Res call({int? id, String username, String hashedPassword, UserRole role});
}

class __$$_UserModelCopyWithImpl<$Res>
    extends _$UserModelCopyWithImpl<$Res, _$_UserModel>
    implements _$$_UserModelCopyWith<$Res> {
  __$$_UserModelCopyWithImpl(
      _$_UserModel _value, $Res Function(_$_UserModel) _then)
      : super(_value, _then);
}

@JsonSerializable()
class _$_UserModel extends _UserModel {
  const _$_UserModel({
    this.id,
    required this.username,
    required this.hashedPassword,
    this.role = UserRole.user,
  }) : super._();

  factory _$_UserModel.fromJson(Map<String, dynamic> json) =>
      _$$_UserModelFromJson(json);

  @override
  final int? id;
  @override
  final String username;
  @override
  final String hashedPassword;
  @override
  @JsonKey()
  final UserRole role;

  @override
  String toString() {
    return 'UserModel(id: $id, username: $username, role: $role)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$_UserModel &&
            other.id == id &&
            other.username == username &&
            other.hashedPassword == hashedPassword &&
            other.role == role);
  }

  @override
  int get hashCode => Object.hash(runtimeType, id, username, hashedPassword, role);

  @override
  @JsonKey(ignore: true)
  _$$_UserModelCopyWith<_$_UserModel> get copyWith =>
      __$$_UserModelCopyWithImpl<_$_UserModel>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_UserModelToJson(this);
  }
}

abstract class _UserModel extends UserModel {
  const factory _UserModel({
    final int? id,
    required final String username,
    required final String hashedPassword,
    final UserRole role,
  }) = _$_UserModel;
  const _UserModel._() : super._();

  factory _UserModel.fromJson(Map<String, dynamic> json) = _$_UserModel.fromJson;

  @override
  int? get id;
  @override
  String get username;
  @override
  String get hashedPassword;
  @override
  UserRole get role;
  @override
  @JsonKey(ignore: true)
  _$$_UserModelCopyWith<_$_UserModel> get copyWith;
}
