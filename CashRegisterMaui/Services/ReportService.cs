using System.Collections.Generic;
using System.Linq;
using CashRegisterMaui.Data;
using CashRegisterMaui.Models;
using Microsoft.EntityFrameworkCore;

namespace CashRegisterMaui.Services;

public class ReportService : IReportService
{
    private readonly IDbContextFactory<AppDbContext> _contextFactory;

    public ReportService(IDbContextFactory<AppDbContext> contextFactory)
    {
        _contextFactory = contextFactory;
    }

    public async Task<DashboardSummary> GetUserSummaryAsync(int userId, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var sessions = await BuildSessionQuery(context, from, to)
            .Where(session => session.UserId == userId)
            .ToListAsync(cancellationToken);
        return BuildSummary(sessions);
    }

    public async Task<DashboardSummary> GetAdminSummaryAsync(DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var sessions = await BuildSessionQuery(context, from, to).ToListAsync(cancellationToken);
        return BuildSummary(sessions);
    }

    public async Task<IReadOnlyList<SessionReport>> GetSessionReportsAsync(int? userId = null, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var query = BuildSessionQuery(context, from, to);

        if (userId.HasValue)
        {
            query = query.Where(session => session.UserId == userId.Value);
        }

        var sessions = await query.ToListAsync(cancellationToken);
        return sessions.Select(session => new SessionReport
        {
            SessionId = session.Id,
            UserName = session.User?.DisplayName ?? session.User?.Username ?? "",
            OpenedAt = session.OpenedAt,
            ClosedAt = session.ClosedAt,
            OpeningCash = session.OpeningCash,
            ClosingCash = session.ClosingCash,
            OpeningFlexi = session.OpeningFlexi,
            ClosingFlexi = session.ClosingFlexi,
            TotalExpenses = session.TotalExpense,
            TotalFlexiAdditions = session.TotalFlexiAdditions,
            TotalFlexiPaid = session.TotalFlexiPaid,
            NetCashDifference = session.NetCashDifference,
            FlexiConsumed = session.FlexiConsumed
        }).ToList();
    }

    public async Task<IReadOnlyList<FlexiTransaction>> GetFlexiTransactionsAsync(bool? isPaid = null, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var query = context.FlexiTransactions.AsQueryable();

        if (isPaid.HasValue)
        {
            query = query.Where(f => f.IsPaid == isPaid.Value);
        }

        if (from.HasValue)
        {
            query = query.Where(f => f.CreatedAt >= from.Value);
        }

        if (to.HasValue)
        {
            query = query.Where(f => f.CreatedAt <= to.Value);
        }

        return await query.OrderByDescending(f => f.CreatedAt).ToListAsync(cancellationToken);
    }

    public async Task<IDictionary<string, decimal>> GetFlexiConsumptionByUserAsync(DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var sessions = await BuildSessionQuery(context, from, to).ToListAsync(cancellationToken);

        return sessions
            .GroupBy(session => session.User?.DisplayName ?? session.User?.Username ?? "Unknown")
            .ToDictionary(group => group.Key, group => group.Sum(session => session.FlexiConsumed));
    }

    private static IQueryable<CashSession> BuildSessionQuery(AppDbContext context, DateTime? from, DateTime? to)
    {
        var query = context.CashSessions
            .Include(session => session.User)
            .Include(session => session.Transactions)
            .Include(session => session.FlexiTransactions)
            .AsQueryable();

        if (from.HasValue)
        {
            query = query.Where(session => session.OpenedAt >= from.Value);
        }

        if (to.HasValue)
        {
            query = query.Where(session => session.OpenedAt <= to.Value);
        }

        return query;
    }

    private static DashboardSummary BuildSummary(IEnumerable<CashSession> sessions)
    {
        var totalExpenses = sessions.Sum(session => session.TotalExpense);
        var totalFlexiAdditions = sessions.Sum(session => session.TotalFlexiAdditions);
        var totalFlexiPaid = sessions.Sum(session => session.TotalFlexiPaid);
        var netCashDifference = sessions.Sum(session => session.NetCashDifference);
        var flexiConsumed = sessions.Sum(session => session.FlexiConsumed);
        return new DashboardSummary
        {
            TotalExpenses = totalExpenses,
            TotalFlexiAdditions = totalFlexiAdditions,
            TotalFlexiPaid = totalFlexiPaid,
            NetCashDifference = netCashDifference,
            FlexiConsumed = flexiConsumed,
            Profit = netCashDifference + totalFlexiPaid - totalExpenses
        };
    }
}
