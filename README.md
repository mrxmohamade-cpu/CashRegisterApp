# Cash Register Applications

يحتوي هذا المستودع الآن على إصدارين من التطبيق:

- **CashRegisterApp/**: التطبيق الأصلي المكتوب بـ Python (PyQt + SQLAlchemy).
- **CashRegisterMaui/**: التطبيق الجديد المبني باستخدام .NET MAUI وEntity Framework Core وMVVM.

## بدء العمل مع مشروع .NET MAUI

1. تثبيت حزم .NET 8 SDK مع دعم MAUI وWorkload الخاصة بالمنصات التي ترغب بالعمل عليها.
2. من داخل مجلد `CashRegisterMaui` نفّذ أوامر الاستعادة والبناء:
   ```bash
   dotnet restore
   dotnet build
   ```
3. لإدارة قاعدة البيانات وتشغيل الهجرات:
   ```bash
   dotnet ef migrations add InitialCreate
   dotnet ef database update
   ```

### الحسابات المبدئية

- يتم تهيئة مستخدم مدير افتراضي ببيانات الدخول: **admin / admin**.

### البنية

- `Data/`: تعريف `AppDbContext` وتهيئة الكيانات والعلاقات مع دعم الهجرات.
- `Models/`: الكيانات وقيم الملخص المستخدمة في الواجهات.
- `Services/`: منطق الأعمال للتوثيق والجلسات والتقارير وإدارة المستخدمين.
- `ViewModels/`: طبقة MVVM المعتمدة على CommunityToolkit.
- `Views/`: صفحات XAML مع نماذج أولية لشاشة الدخول ولوحة المستخدم ولوحة المشرف.
- `Resources/`: الأصول والأنماط المستخدمة في الواجهات.

يمكن تشغيل التطبيق على المنصات المدعومة من MAUI (Android، iOS، MacCatalyst، Windows) بعد إعداد بيئة التطوير المناسبة.
