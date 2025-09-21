using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CashRegisterMaui.Models;

public class FlexiTransaction
{
    [Key]
    public int Id { get; set; }

    [Required]
    public int CashSessionId { get; set; }

    public CashSession? CashSession { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal Amount { get; set; }

    public bool IsPaid { get; set; }

    [MaxLength(256)]
    public string? Notes { get; set; }

    [Required]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
