import 'dart:async';

import 'package:drift/drift.dart';

import '../../models/user_model.dart';
import '../../models/user_role.dart';
import '../app_database.dart';

class UserDao {
  UserDao(this._db);

  final AppDatabase _db;
  final _usersController = StreamController<List<UserModel>>.broadcast();

  Future<UserModel?> findByUsername(String username) async {
    final result = await _db.customSelect(
      'SELECT * FROM users WHERE username = ? LIMIT 1',
      variables: [Variable<String>(username)],
      readsFrom: const {},
    ).getSingleOrNull();
    if (result == null) {
      return null;
    }
    return _mapUser(result.data);
  }

  Future<UserModel?> findById(int id) async {
    final result = await _db.customSelect(
      'SELECT * FROM users WHERE id = ? LIMIT 1',
      variables: [Variable<int>(id)],
      readsFrom: const {},
    ).getSingleOrNull();
    if (result == null) {
      return null;
    }
    return _mapUser(result.data);
  }

  Stream<List<UserModel>> watchUsers() {
    _emitUsers();
    return _usersController.stream;
  }

  Future<List<UserModel>> getUsers() async {
    final rows = await _db.customSelect(
      'SELECT * FROM users ORDER BY username ASC',
      readsFrom: const {},
    ).get();
    return rows.map((row) => _mapUser(row.data)).toList();
  }

  Future<int> insertUser(UserModel user) async {
    final id = await _db.customInsert(
      'INSERT INTO users(username, hashed_password, role) VALUES (?, ?, ?)',
      variables: [
        Variable<String>(user.username),
        Variable<String>(user.hashedPassword),
        Variable<String>(user.role.name),
      ],
    );
    await _emitUsers();
    return id;
  }

  Future<void> updateUser(UserModel user) async {
    final id = user.id;
    if (id == null) {
      throw ArgumentError('User must have an id before it can be updated.');
    }
    await _db.customStatement(
      'UPDATE users SET username = ?, hashed_password = ?, role = ? WHERE id = ?',
      [
        user.username,
        user.hashedPassword,
        user.role.name,
        id,
      ],
    );
    await _emitUsers();
  }

  Future<void> deleteUser(int id) async {
    await _db.customStatement(
      'DELETE FROM users WHERE id = ?',
      [id],
    );
    await _emitUsers();
  }

  UserModel _mapUser(Map<String, Object?> data) {
    return UserModel(
      id: data['id'] as int?,
      username: data['username'] as String,
      hashedPassword: data['hashed_password'] as String,
      role: (data['role'] as String) == 'admin' ? UserRole.admin : UserRole.user,
    );
  }

  Future<void> _emitUsers() async {
    final rows = await _db.customSelect(
      'SELECT * FROM users ORDER BY username ASC',
      readsFrom: const {},
    ).get();
    if (!_usersController.isClosed) {
      _usersController.add(rows.map((row) => _mapUser(row.data)).toList());
    }
  }
}
