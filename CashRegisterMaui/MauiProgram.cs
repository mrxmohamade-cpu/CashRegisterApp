using System.IO;
using CashRegisterMaui.Data;
using CashRegisterMaui.Helpers;
using CashRegisterMaui.Services;
using CashRegisterMaui.ViewModels;
using CashRegisterMaui.Views;
using CommunityToolkit.Maui;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Maui.Storage;
using SQLitePCL;

namespace CashRegisterMaui;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit();

        SQLitePCL.Batteries_V2.Init();

        var dbPath = Path.Combine(FileSystem.AppDataDirectory, "cashregister.db");
        builder.Services.AddDbContextFactory<AppDbContext>(options =>
        {
            options.UseSqlite($"Data Source={dbPath}");
        });

        builder.Services.AddSingleton<IDatabaseInitializer, DatabaseInitializer>();
        builder.Services.AddSingleton<AppState>();
        builder.Services.AddScoped<IAuthenticationService, AuthenticationService>();
        builder.Services.AddScoped<ISessionService, SessionService>();
        builder.Services.AddScoped<IReportService, ReportService>();
        builder.Services.AddScoped<IUserService, UserService>();

        builder.Services.AddTransient<LoginViewModel>();
        builder.Services.AddTransient<UserDashboardViewModel>();
        builder.Services.AddTransient<AdminDashboardViewModel>();

        builder.Services.AddSingleton<AppShell>();
        builder.Services.AddTransient<LoginPage>();
        builder.Services.AddTransient<UserDashboardPage>();
        builder.Services.AddTransient<AdminDashboardPage>();

#if DEBUG
        builder.Logging.AddDebug();
#endif

        var app = builder.Build();
        ServiceHelper.Configure(app.Services);

        using var scope = app.Services.CreateScope();
        var initializer = scope.ServiceProvider.GetRequiredService<IDatabaseInitializer>();
        initializer.InitializeAsync().GetAwaiter().GetResult();

        return app;
    }
}
