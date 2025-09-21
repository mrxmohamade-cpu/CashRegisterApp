using CashRegisterMaui.Data;
using CashRegisterMaui.Models;
using Microsoft.EntityFrameworkCore;

namespace CashRegisterMaui.Services;

public class AuthenticationService : IAuthenticationService
{
    private readonly IDbContextFactory<AppDbContext> _contextFactory;

    public AuthenticationService(IDbContextFactory<AppDbContext> contextFactory)
    {
        _contextFactory = contextFactory;
    }

    public async Task<User?> AuthenticateAsync(string username, string password, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var passwordHash = AppDbContext.HashPassword(password);
        return await context.Users.FirstOrDefaultAsync(
            user => user.Username == username && user.PasswordHash == passwordHash && user.IsActive,
            cancellationToken);
    }
}
