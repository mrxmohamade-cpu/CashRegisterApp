using CashRegisterMaui.Views;

namespace CashRegisterMaui;

public partial class App : Application
{
    public App(AppShell shell)
    {
        InitializeComponent();
        MainPage = shell;
    }
}
