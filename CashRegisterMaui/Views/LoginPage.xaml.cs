using CashRegisterMaui.Helpers;
using CashRegisterMaui.ViewModels;
using Microsoft.Maui.Controls;

namespace CashRegisterMaui.Views;

public partial class LoginPage : ContentPage
{
    public LoginPage()
    {
        InitializeComponent();
        BindingContext = ServiceHelper.GetRequiredService<LoginViewModel>();
    }
}
