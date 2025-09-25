import '../../../core/models/user_model.dart';

class AuthState {
  const AuthState({this.user, this.errorMessage, this.isLoading = false});

  final UserModel? user;
  final String? errorMessage;
  final bool isLoading;

  bool get isAuthenticated => user != null;
  bool get isAdmin => user?.isAdmin ?? false;

  AuthState copyWith({
    UserModel? user,
    String? errorMessage,
    bool? isLoading,
  }) {
    return AuthState(
      user: user ?? this.user,
      errorMessage: errorMessage,
      isLoading: isLoading ?? this.isLoading,
    );
  }

  static AuthState unauthenticated() => const AuthState();
}
