using CashRegisterMaui.Models;

namespace CashRegisterMaui.Services;

public interface ISessionService
{
    Task<CashSession?> GetActiveSessionAsync(int userId, CancellationToken cancellationToken = default);
    Task<CashSession> OpenSessionAsync(int userId, decimal openingCash, decimal openingFlexi, string? notes = null, CancellationToken cancellationToken = default);
    Task CloseSessionAsync(int sessionId, decimal closingCash, decimal closingFlexi, string? notes = null, CancellationToken cancellationToken = default);
    Task<Transaction> AddExpenseAsync(int sessionId, decimal amount, string? description, CancellationToken cancellationToken = default);
    Task<FlexiTransaction> AddFlexiAsync(int sessionId, decimal amount, bool isPaid, string? notes, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<CashSession>> GetSessionsAsync(int? userId = null, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default);
}
