import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/user_model.dart';
import '../../../core/models/user_role.dart';
import '../../../core/repo/auth_repository.dart';
import '../../../core/utils/app_providers.dart';
import 'auth_state.dart';

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return AuthController(authRepository);
});

final currentUserProvider = Provider<UserModel?>((ref) {
  return ref.watch(authControllerProvider).user;
});

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._authRepository) : super(AuthState.unauthenticated());

  final AuthRepository _authRepository;

  Future<bool> login(String username, String password) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    final user = await _authRepository.authenticate(username, password);
    if (user == null) {
      state = state.copyWith(isLoading: false, errorMessage: 'بيانات الدخول غير صحيحة');
      return false;
    }
    state = AuthState(user: user);
    return true;
  }

  void logout() {
    state = AuthState.unauthenticated();
  }

  Future<UserModel> createUser({
    required String username,
    required String password,
    UserRole role = UserRole.user,
  }) async {
    return _authRepository.createUser(username: username, password: password, role: role);
  }
}
