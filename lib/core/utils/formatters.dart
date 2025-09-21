import 'package:intl/intl.dart';

class Formatters {
  static final NumberFormat currencyFormatter = NumberFormat.currency(
    locale: 'ar',
    symbol: 'دج',
    decimalDigits: 2,
  );

  static final NumberFormat numberFormatter = NumberFormat('#,##0.00', 'ar');

  static String formatCurrency(num value) => currencyFormatter.format(value);

  static String formatNumber(num value) => numberFormatter.format(value);

  static String formatDate(DateTime value) => DateFormat.yMMMEd('ar').add_Hm().format(value);

  static void initialize() {
    NumberFormat.localeExists('ar');
  }
}
