namespace CashRegisterMaui.Models;

public class DashboardSummary
{
    public decimal TotalExpenses { get; set; }
    public decimal TotalFlexiAdditions { get; set; }
    public decimal TotalFlexiPaid { get; set; }
    public decimal NetCashDifference { get; set; }
    public decimal FlexiConsumed { get; set; }
    public decimal Profit { get; set; }
}
