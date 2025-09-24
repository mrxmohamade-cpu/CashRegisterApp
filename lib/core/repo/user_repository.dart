import '../db/app_database.dart';
import '../db/dao/user_dao.dart';
import '../models/user_model.dart';
import '../models/user_role.dart';
import '../utils/hash_utils.dart';

class UserRepository {
  UserRepository(AppDatabase db) : _userDao = UserDao(db);

  final UserDao _userDao;

  Stream<List<UserModel>> watchUsers() => _userDao.watchUsers();

  Future<List<UserModel>> getUsers() => _userDao.getUsers();

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

  Future<void> updateUser(UserModel user, {String? newPassword}) async {
    final updated = user.copyWith(
      hashedPassword:
          newPassword != null ? HashUtils.hashPassword(newPassword) : user.hashedPassword,
    );
    await _userDao.updateUser(updated);
  }

  Future<void> deleteUser(int id) => _userDao.deleteUser(id);

  Future<bool> confirmAdminPassword(String username, String password) async {
    final user = await _userDao.findByUsername(username);
    if (user == null || !user.isAdmin) {
      return false;
    }
    return HashUtils.verifyPassword(password, user.hashedPassword);
  }
}
