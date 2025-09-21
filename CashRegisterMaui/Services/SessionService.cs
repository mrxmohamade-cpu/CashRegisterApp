using CashRegisterMaui.Data;
using CashRegisterMaui.Models;
using Microsoft.EntityFrameworkCore;

namespace CashRegisterMaui.Services;

public class SessionService : ISessionService
{
    private readonly IDbContextFactory<AppDbContext> _contextFactory;

    public SessionService(IDbContextFactory<AppDbContext> contextFactory)
    {
        _contextFactory = contextFactory;
    }

    public async Task<CashSession?> GetActiveSessionAsync(int userId, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        return await context.CashSessions
            .Include(cs => cs.Transactions)
            .Include(cs => cs.FlexiTransactions)
            .Where(cs => cs.UserId == userId && cs.ClosedAt == null)
            .OrderByDescending(cs => cs.OpenedAt)
            .FirstOrDefaultAsync(cancellationToken);
    }

    public async Task<CashSession> OpenSessionAsync(int userId, decimal openingCash, decimal openingFlexi, string? notes = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var existing = await context.CashSessions.AnyAsync(cs => cs.UserId == userId && cs.ClosedAt == null, cancellationToken);
        if (existing)
        {
            throw new InvalidOperationException("There is already an open session for this user.");
        }

        var session = new CashSession
        {
            UserId = userId,
            OpeningCash = openingCash,
            ClosingCash = openingCash,
            OpeningFlexi = openingFlexi,
            ClosingFlexi = openingFlexi,
            Notes = notes,
            OpenedAt = DateTime.UtcNow
        };

        await context.CashSessions.AddAsync(session, cancellationToken);
        await context.SaveChangesAsync(cancellationToken);
        return session;
    }

    public async Task CloseSessionAsync(int sessionId, decimal closingCash, decimal closingFlexi, string? notes = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var session = await context.CashSessions.FirstOrDefaultAsync(cs => cs.Id == sessionId, cancellationToken);
        if (session is null)
        {
            throw new InvalidOperationException("Session not found.");
        }

        session.ClosingCash = closingCash;
        session.ClosingFlexi = closingFlexi;
        session.Notes = notes ?? session.Notes;
        session.ClosedAt = DateTime.UtcNow;
        await context.SaveChangesAsync(cancellationToken);
    }

    public async Task<Transaction> AddExpenseAsync(int sessionId, decimal amount, string? description, CancellationToken cancellationToken = default)
    {
        if (amount < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(amount));
        }

        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var transaction = new Transaction
        {
            CashSessionId = sessionId,
            Amount = amount,
            Description = description,
            CreatedAt = DateTime.UtcNow
        };

        await context.Transactions.AddAsync(transaction, cancellationToken);
        await context.SaveChangesAsync(cancellationToken);
        return transaction;
    }

    public async Task<FlexiTransaction> AddFlexiAsync(int sessionId, decimal amount, bool isPaid, string? notes, CancellationToken cancellationToken = default)
    {
        if (amount < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(amount));
        }

        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var flexi = new FlexiTransaction
        {
            CashSessionId = sessionId,
            Amount = amount,
            IsPaid = isPaid,
            Notes = notes,
            CreatedAt = DateTime.UtcNow
        };

        await context.FlexiTransactions.AddAsync(flexi, cancellationToken);
        await context.SaveChangesAsync(cancellationToken);
        return flexi;
    }

    public async Task<IReadOnlyList<CashSession>> GetSessionsAsync(int? userId = null, DateTime? from = null, DateTime? to = null, CancellationToken cancellationToken = default)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(cancellationToken);
        var query = context.CashSessions
            .Include(cs => cs.User)
            .Include(cs => cs.Transactions)
            .Include(cs => cs.FlexiTransactions)
            .AsQueryable();

        if (userId.HasValue)
        {
            query = query.Where(cs => cs.UserId == userId.Value);
        }

        if (from.HasValue)
        {
            query = query.Where(cs => cs.OpenedAt >= from.Value);
        }

        if (to.HasValue)
        {
            query = query.Where(cs => cs.OpenedAt <= to.Value);
        }

        return await query.OrderByDescending(cs => cs.OpenedAt).ToListAsync(cancellationToken);
    }
}
