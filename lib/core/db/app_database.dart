import 'dart:async';
import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import '../utils/hash_utils.dart';

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dir = await getApplicationDocumentsDirectory();
    final dbPath = p.join(dir.path, 'cash_register.sqlite');
    return NativeDatabase(File(dbPath));
  });
}

class AppDatabase extends GeneratedDatabase {
  AppDatabase() : super(_openConnection());

  static Future<AppDatabase> makeDefault() async {
    return AppDatabase();
  }

  @override
  Iterable<TableInfo<Table, Object?>> get allTables => const [];

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (Migrator m) async {
          await _createSchema();
          await _seedAdmin();
        },
        onUpgrade: (Migrator m, int from, int to) async {
          if (from < 1) {
            await _createSchema();
            await _seedAdmin();
          }
        },
      );

  Future<void> _createSchema() async {
    await customStatement('''
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','user'))
      );
    ''');

    await customStatement('''
      CREATE TABLE IF NOT EXISTS cash_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        start_balance REAL NOT NULL,
        end_balance REAL,
        status TEXT NOT NULL CHECK(status IN ('open','closed')),
        notes TEXT,
        start_flexi REAL NOT NULL DEFAULT 0.0,
        end_flexi REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      );
    ''');

    await customStatement('''
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('expense','income')),
        amount REAL NOT NULL,
        description TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(session_id) REFERENCES cash_sessions(id)
      );
    ''');

    await customStatement('''
      CREATE TABLE IF NOT EXISTS flexi_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        timestamp TEXT NOT NULL,
        is_paid INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(session_id) REFERENCES cash_sessions(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
      );
    ''');
  }

  Future<void> _seedAdmin() async {
    const username = 'admin';
    final password = HashUtils.hashPassword('admin');
    await customStatement(
      'INSERT OR IGNORE INTO users(username, hashed_password, role) VALUES(?, ?, ?)',
      [username, password, 'admin'],
    );
  }
}
