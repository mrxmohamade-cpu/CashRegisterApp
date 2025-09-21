using CommunityToolkit.Mvvm.ComponentModel;

namespace CashRegisterMaui.ViewModels;

public partial class ViewModelBase : ObservableObject
{
    [ObservableProperty]
    private bool isBusy;

    [ObservableProperty]
    private string title = string.Empty;
}
