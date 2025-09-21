using Microsoft.Maui.Controls;

namespace CashRegisterMaui.Views;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();
        Dispatcher.Dispatch(async () => await GoToAsync("//LoginPage"));
    }
}
