using System;
using Microsoft.Extensions.DependencyInjection;

namespace CashRegisterMaui.Helpers;

public static class ServiceHelper
{
    private static IServiceProvider? _provider;

    public static void Configure(IServiceProvider provider)
    {
        _provider = provider;
    }

    public static T GetRequiredService<T>() where T : notnull
    {
        if (_provider is null)
        {
            throw new InvalidOperationException("Service provider is not configured. Call ServiceHelper.Configure during app startup.");
        }

        return _provider.GetRequiredService<T>();
    }

    public static T? GetService<T>()
    {
        return _provider?.GetService<T>();
    }
}
