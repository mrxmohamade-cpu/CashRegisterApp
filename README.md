# Cash Register App

تطبيق Flutter لإدارة صندوق متجر مع دعم العربية والاتجاه من اليمين إلى اليسار. يعتمد المشروع على Riverpod لإدارة الحالة، و go_router للتوجيه، و Drift للتعامل مع قاعدة بيانات SQLite المحلية، مع استخدام Freezed و json_serializable للنماذج.

## المتطلبات الرئيسية
- إدارة جلسات الصندوق مع المصاريف والفليكسي.
- لوحات منفصلة للعامل والمشرف.
- دعم RTL واللغة العربية والتنسيقات المحلية.

## البنية
```
lib/
├── core/
│   ├── db/
│   ├── models/
│   ├── repo/
│   └── utils/
├── features/
│   ├── admin/
│   ├── auth/
│   ├── session/
│   └── user/
└── routes/
```

## المتطلبات المسبقة
- Flutter 3.22.0 أو أحدث (يتضمن حزمة `flutter_localizations` التي تعتمد على `intl 0.20.2`).
- Dart SDK الموافق لإصدار Flutter.
- أدوات المنصات المستهدفة (Android SDK أو أدوات سطح المكتب لـ Windows).

تحقق من صحة البيئة عبر:

```bash
flutter doctor
```

## تشغيل المشروع
1. **استنساخ المستودع**
   ```bash
   git clone https://github.com/<your-org>/CashRegisterApp.git
   cd CashRegisterApp
   ```
2. **تثبيت الحزم**
   ```bash
   flutter pub get
   ```
   > إذا ظهر خطأ يخص مكتبة `intl` فذلك يعني أن Flutter يحجز الإصدار ‎0.20.2‎. تم ضبط `pubspec.yaml` بالفعل على هذا الإصدار، لكن في حال عدلت الملف قم بتشغيل:
   > ```bash
   > flutter pub upgrade intl
   > ```
3. **توليد الملفات المبنية على build_runner** (نماذج Freezed و Drift)
   ```bash
   dart run build_runner build --delete-conflicting-outputs
   ```
4. **تشغيل التطبيق**
   - Android: وصل جهازًا حقيقيًا أو شغّل محاكيًا ثم نفّذ `flutter run`.
   - Windows: فعّل دعم سطح المكتب ثم نفّذ `flutter run -d windows`.

سيتم إنشاء قاعدة بيانات SQLite في مجلد التطبيق المحلي مع بيانات seed تشمل مستخدم المشرف `admin/admin` في أول تشغيل.

## الاختبارات
تم توفير اختبار وحدة لحسابات الجلسات:
```
flutter test
```

## استكشاف الأخطاء الشائعة
- **فشل `flutter pub get` بسبب `intl`:** تأكد من أن قيد الحزمة في `pubspec.yaml` هو `intl: ^0.20.2` أو استخدم `flutter pub upgrade intl`. السبب يعود لاعتماد Flutter على هذا الإصدار مع `flutter_localizations`.
- **تعارض ملفات build_runner:** استخدم `dart run build_runner build --delete-conflicting-outputs` لإعادة توليد الملفات.

يتم تلقائياً إنشاء مستخدم مشرف افتراضي (admin/admin) عند أول تشغيل لقاعدة البيانات.
