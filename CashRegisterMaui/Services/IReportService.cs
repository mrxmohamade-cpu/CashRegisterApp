using CashRegisterMaui.Models;

namespace CashRegisterMaui.Services;

public interface IReportService
{
    Task<DashboardSummary> GetUserSummaryAsync(int userId, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default);
    Task<DashboardSummary> GetAdminSummaryAsync(DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<SessionReport>> GetSessionReportsAsync(int? userId = null, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<FlexiTransaction>> GetFlexiTransactionsAsync(bool? isPaid = null, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default);
    Task<IDictionary<string, decimal>> GetFlexiConsumptionByUserAsync(DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default);
}
