namespace CashRegisterMaui.Models;

public class SessionReport
{
    public int SessionId { get; set; }
    public string UserName { get; set; } = string.Empty;
    public DateTime OpenedAt { get; set; }
    public DateTime? ClosedAt { get; set; }
    public decimal OpeningCash { get; set; }
    public decimal ClosingCash { get; set; }
    public decimal OpeningFlexi { get; set; }
    public decimal ClosingFlexi { get; set; }
    public decimal TotalExpenses { get; set; }
    public decimal TotalFlexiAdditions { get; set; }
    public decimal TotalFlexiPaid { get; set; }
    public decimal NetCashDifference { get; set; }
    public decimal FlexiConsumed { get; set; }
}
