using CashRegisterMaui.Models;

namespace CashRegisterMaui.Services;

public interface IUserService
{
    Task<IReadOnlyList<User>> GetUsersAsync(CancellationToken cancellationToken = default);
    Task<User> AddUserAsync(string username, string password, UserRole role, string? fullName = null, CancellationToken cancellationToken = default);
    Task UpdateUserAsync(int userId, string? password = null, UserRole? role = null, string? fullName = null, bool? isActive = null, CancellationToken cancellationToken = default);
    Task DeleteUserAsync(int userId, CancellationToken cancellationToken = default);
}
