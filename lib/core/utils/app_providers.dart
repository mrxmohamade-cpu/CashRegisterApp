import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../db/app_database.dart';
import '../repo/admin_repository.dart';
import '../repo/auth_repository.dart';
import '../repo/session_repository.dart';
import '../repo/user_repository.dart';

final databaseProvider = Provider<AppDatabase>((ref) {
  final db = AppDatabase();
  ref.onDispose(db.close);
  return db;
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final db = ref.watch(databaseProvider);
  return AuthRepository(db);
});

final userRepositoryProvider = Provider<UserRepository>((ref) {
  final db = ref.watch(databaseProvider);
  return UserRepository(db);
});

final sessionRepositoryProvider = Provider<SessionRepository>((ref) {
  final db = ref.watch(databaseProvider);
  return SessionRepository(db);
});

final adminRepositoryProvider = Provider<AdminRepository>((ref) {
  final db = ref.watch(databaseProvider);
  final sessionRepository = ref.watch(sessionRepositoryProvider);
  return AdminRepository(db, sessionRepository);
});
