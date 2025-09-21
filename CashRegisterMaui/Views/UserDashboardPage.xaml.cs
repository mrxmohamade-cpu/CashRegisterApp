using CashRegisterMaui.Helpers;
using CashRegisterMaui.ViewModels;
using Microsoft.Maui.Controls;

namespace CashRegisterMaui.Views;

public partial class UserDashboardPage : ContentPage
{
    private readonly UserDashboardViewModel _viewModel;

    public UserDashboardPage()
    {
        InitializeComponent();
        _viewModel = ServiceHelper.GetRequiredService<UserDashboardViewModel>();
        BindingContext = _viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await _viewModel.LoadAsync();
    }
}
