import 'package:cash_register_app/main.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('renders login screen initially', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: CashRegisterApp()));
    expect(find.text('تسجيل الدخول'), findsOneWidget);
  });
}
