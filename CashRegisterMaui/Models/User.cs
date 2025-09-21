using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CashRegisterMaui.Models;

public class User
{
    [Key]
    public int Id { get; set; }

    [Required]
    [MaxLength(64)]
    public string Username { get; set; } = string.Empty;

    [Required]
    public string PasswordHash { get; set; } = string.Empty;

    [Required]
    public UserRole Role { get; set; } = UserRole.User;

    [MaxLength(128)]
    public string? FullName { get; set; }

    public bool IsActive { get; set; } = true;

    public ICollection<CashSession> CashSessions { get; set; } = new HashSet<CashSession>();

    [NotMapped]
    public string DisplayName => string.IsNullOrWhiteSpace(FullName) ? Username : FullName;
}
