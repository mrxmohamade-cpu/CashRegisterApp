using CashRegisterMaui.Helpers;
using CashRegisterMaui.ViewModels;
using Microsoft.Maui.Controls;

namespace CashRegisterMaui.Views;

public partial class AdminDashboardPage : ContentPage
{
    private readonly AdminDashboardViewModel _viewModel;

    public AdminDashboardPage()
    {
        InitializeComponent();
        _viewModel = ServiceHelper.GetRequiredService<AdminDashboardViewModel>();
        BindingContext = _viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await _viewModel.LoadAsync();
    }
}
