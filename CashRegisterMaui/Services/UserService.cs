using System.Linq;
using CashRegisterMaui.Data;
using CashRegisterMaui.Models;
using Microsoft.EntityFrameworkCore;

namespace CashRegisterMaui.Services;

public class UserService : IUserService
{
    private readonly IDbContextFactory<AppDbContext> _contextFactory;

    public UserService(IDbContextFactory<AppDbContext> contextFactory)
    {
        _contextFactory = contextFactory;
    }

    public async Task<IReadOnlyList<User>> GetUsersAsync(CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        return await context.Users.OrderBy(user => user.Username).ToListAsync(cancellationToken);
    }

    public async Task<User> AddUserAsync(string username, string password, UserRole role, string? fullName = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var user = new User
        {
            Username = username,
            PasswordHash = AppDbContext.HashPassword(password),
            Role = role,
            FullName = fullName,
            IsActive = true
        };
        await context.Users.AddAsync(user, cancellationToken);
        await context.SaveChangesAsync(cancellationToken);
        return user;
    }

    public async Task UpdateUserAsync(int userId, string? password = null, UserRole? role = null, string? fullName = null, bool? isActive = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var user = await context.Users.FirstOrDefaultAsync(u => u.Id == userId, cancellationToken);
        if (user is null)
        {
            throw new InvalidOperationException("User not found");
        }

        if (!string.IsNullOrWhiteSpace(password))
        {
            user.PasswordHash = AppDbContext.HashPassword(password);
        }

        if (role.HasValue)
        {
            user.Role = role.Value;
        }

        if (fullName is not null)
        {
            user.FullName = fullName;
        }

        if (isActive.HasValue)
        {
            user.IsActive = isActive.Value;
        }

        await context.SaveChangesAsync(cancellationToken);
    }

    public async Task DeleteUserAsync(int userId, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var user = await context.Users.FirstOrDefaultAsync(u => u.Id == userId, cancellationToken);
        if (user is null)
        {
            return;
        }

        context.Users.Remove(user);
        await context.SaveChangesAsync(cancellationToken);
    }
}
