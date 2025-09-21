# Entity Framework Core Migrations

لتوليد الهجرات وتشغيلها استخدم أوامر EF Core المعتادة من داخل مجلد المشروع:

```bash
# إنشاء الهجرة الأولى
 dotnet ef migrations add InitialCreate

# تحديث قاعدة البيانات
 dotnet ef database update
```

الهجرات تُحفظ داخل هذا المجلد وسيتم تطبيقها تلقائياً عند تشغيل التطبيق بفضل `DatabaseInitializer`.
