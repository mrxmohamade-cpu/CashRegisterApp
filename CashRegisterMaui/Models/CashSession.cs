using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;

namespace CashRegisterMaui.Models;

public class CashSession
{
    [Key]
    public int Id { get; set; }

    [Required]
    public int UserId { get; set; }

    public User? User { get; set; }

    [Required]
    public DateTime OpenedAt { get; set; } = DateTime.UtcNow;

    public DateTime? ClosedAt { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal OpeningCash { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal ClosingCash { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal OpeningFlexi { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal ClosingFlexi { get; set; }

    [MaxLength(256)]
    public string? Notes { get; set; }

    public ICollection<Transaction> Transactions { get; set; } = new HashSet<Transaction>();

    public ICollection<FlexiTransaction> FlexiTransactions { get; set; } = new HashSet<FlexiTransaction>();

    [NotMapped]
    public decimal TotalExpense => Transactions?.Sum(t => t.Amount) ?? 0m;

    [NotMapped]
    public decimal TotalFlexiAdditions => FlexiTransactions?.Sum(t => t.Amount) ?? 0m;

    [NotMapped]
    public decimal TotalFlexiPaid => FlexiTransactions?.Where(t => t.IsPaid).Sum(t => t.Amount) ?? 0m;

    [NotMapped]
    public decimal NetCashDifference => (ClosingCash - OpeningCash) - TotalExpense + TotalFlexiPaid;

    [NotMapped]
    public decimal FlexiConsumed => TotalFlexiAdditions - ClosingFlexi;

    [NotMapped]
    public bool IsClosed => ClosedAt.HasValue;
}
