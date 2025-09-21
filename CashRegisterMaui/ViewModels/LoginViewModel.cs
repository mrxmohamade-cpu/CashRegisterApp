using CashRegisterMaui.Models;
using CashRegisterMaui.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Maui.ApplicationModel;

namespace CashRegisterMaui.ViewModels;

public partial class LoginViewModel : ViewModelBase
{
    private readonly IAuthenticationService _authenticationService;
    private readonly AppState _appState;

    public LoginViewModel(IAuthenticationService authenticationService, AppState appState)
    {
        _authenticationService = authenticationService;
        _appState = appState;
        Title = "تسجيل الدخول";
    }

    [ObservableProperty]
    private string username = string.Empty;

    [ObservableProperty]
    private string password = string.Empty;

    [ObservableProperty]
    private string errorMessage = string.Empty;

    [RelayCommand]
    private async Task LoginAsync()
    {
        if (IsBusy)
        {
            return;
        }

        try
        {
            IsBusy = true;
            ErrorMessage = string.Empty;
            var user = await _authenticationService.AuthenticateAsync(Username.Trim(), Password);
            if (user is null)
            {
                ErrorMessage = "بيانات الدخول غير صحيحة";
                return;
            }

            _appState.CurrentUser = user;
            var route = user.Role == UserRole.Admin ? "//AdminDashboardPage" : "//UserDashboardPage";
            await MainThread.InvokeOnMainThreadAsync(() => Shell.Current.GoToAsync(route));
        }
        catch (Exception ex)
        {
            ErrorMessage = ex.Message;
        }
        finally
        {
            IsBusy = false;
            Password = string.Empty;
        }
    }
}
