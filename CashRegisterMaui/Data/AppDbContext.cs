using System.Security.Cryptography;
using System.Text;
using CashRegisterMaui.Models;
using Microsoft.EntityFrameworkCore;

namespace CashRegisterMaui.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }

    public DbSet<User> Users => Set<User>();
    public DbSet<CashSession> CashSessions => Set<CashSession>();
    public DbSet<Transaction> Transactions => Set<Transaction>();
    public DbSet<FlexiTransaction> FlexiTransactions => Set<FlexiTransaction>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<User>()
            .HasIndex(u => u.Username)
            .IsUnique();

        modelBuilder.Entity<User>().HasData(new User
        {
            Id = 1,
            Username = "admin",
            PasswordHash = HashPassword("admin"),
            Role = UserRole.Admin,
            FullName = "Administrator"
        });

        modelBuilder.Entity<CashSession>()
            .HasOne(cs => cs.User)
            .WithMany(u => u.CashSessions)
            .HasForeignKey(cs => cs.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Transaction>()
            .HasOne(t => t.CashSession)
            .WithMany(cs => cs.Transactions)
            .HasForeignKey(t => t.CashSessionId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<FlexiTransaction>()
            .HasOne(t => t.CashSession)
            .WithMany(cs => cs.FlexiTransactions)
            .HasForeignKey(t => t.CashSessionId)
            .OnDelete(DeleteBehavior.Cascade);
    }

    public static string HashPassword(string password)
    {
        using var sha = SHA256.Create();
        var bytes = Encoding.UTF8.GetBytes(password);
        var hash = sha.ComputeHash(bytes);
        return Convert.ToHexString(hash);
    }
}
