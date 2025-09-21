using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CashRegisterMaui.Models;

public class Transaction
{
    [Key]
    public int Id { get; set; }

    [Required]
    public int CashSessionId { get; set; }

    public CashSession? CashSession { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal Amount { get; set; }

    [MaxLength(256)]
    public string? Description { get; set; }

    [Required]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
