import 'dart:convert';

import 'package:crypto/crypto.dart';

class HashUtils {
  const HashUtils._();

  static String hashPassword(String password) {
    final bytes = utf8.encode(password);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  static bool verifyPassword(String password, String hashed) {
    return hashPassword(password) == hashed;
  }
}
