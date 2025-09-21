using CashRegisterMaui.Models;

namespace CashRegisterMaui.Services;

public interface IAuthenticationService
{
    Task<User?> AuthenticateAsync(string username, string password, CancellationToken cancellationToken = default);
}
