// GENERATED CODE - MANUALLY WRITTEN JSON SERIALIZABLE STUB.
// ignore_for_file: type=lint

part of 'user_model.dart';

_$_UserModel _$$_UserModelFromJson(Map<String, dynamic> json) => _$_UserModel(
      id: json['id'] as int?,
      username: json['username'] as String,
      hashedPassword: json['hashed_password'] as String,
      role: _$enumDecodeNullable(_$UserRoleEnumMap, json['role']) ?? UserRole.user,
    );

Map<String, dynamic> _$$_UserModelToJson(_$_UserModel instance) => <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'hashed_password': instance.hashedPassword,
      'role': _$UserRoleEnumMap[instance.role],
    };

const _$UserRoleEnumMap = {
  UserRole.admin: 'admin',
  UserRole.user: 'user',
};

T? _$enumDecodeNullable<T>(Map<T, dynamic> enumValues, dynamic source,
    {T? unknownValue}) {
  if (source == null) {
    return null;
  }
  return _$enumDecode(enumValues, source, unknownValue: unknownValue);
}

T _$enumDecode<T>(Map<T, dynamic> enumValues, dynamic source,
    {T? unknownValue}) {
  if (source == null) {
    throw ArgumentError('A value must be provided.');
  }
  final entry = enumValues.entries.firstWhere(
    (element) => element.value == source,
    orElse: () {
      if (unknownValue == null) {
        throw ArgumentError('`$source` is not one of the supported values.');
      }
      return MapEntry(unknownValue, enumValues.values.first);
    },
  );
  return entry.key;
}
