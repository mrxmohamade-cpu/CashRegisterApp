import '../db/app_database.dart';
import '../db/dao/user_dao.dart';
import '../models/user_model.dart';
import '../models/user_role.dart';
import '../utils/hash_utils.dart';

class AuthRepository {
  AuthRepository(this._db) : _userDao = UserDao(_db);

  final AppDatabase _db;
  final UserDao _userDao;

  Future<UserModel?> authenticate(String username, String password) async {
    final user = await _userDao.findByUsername(username);
    if (user == null) {
      return null;
    }
    if (HashUtils.verifyPassword(password, user.hashedPassword)) {
      return user;
    }
    return null;
  }

  Future<UserModel> createUser({
    required String username,
    required String password,
    required UserRole role,
  }) async {
    final hashed = HashUtils.hashPassword(password);
    final id = await _userDao.insertUser(
      UserModel(username: username, hashedPassword: hashed, role: role),
    );
    return (await _userDao.findById(id))!;
  }
}
