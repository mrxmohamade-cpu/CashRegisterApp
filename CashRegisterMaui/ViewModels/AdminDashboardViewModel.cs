using System.Collections.ObjectModel;
using System.Linq;
using CashRegisterMaui.Models;
using CashRegisterMaui.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Painting;
using SkiaSharp;

namespace CashRegisterMaui.ViewModels;

public partial class AdminDashboardViewModel : ViewModelBase
{
    private readonly IReportService _reportService;
    private readonly IUserService _userService;

    public AdminDashboardViewModel(IReportService reportService, IUserService userService)
    {
        _reportService = reportService;
        _userService = userService;
        Title = "لوحة المشرف";
    }

    [ObservableProperty]
    private DashboardSummary summary = new();

    [ObservableProperty]
    private string? statusMessage;

    [ObservableProperty]
    private User? selectedUser;

    [ObservableProperty]
    private string newUsername = string.Empty;

    [ObservableProperty]
    private string newFullName = string.Empty;

    [ObservableProperty]
    private string newPassword = string.Empty;

    [ObservableProperty]
    private bool newIsAdmin;

    [ObservableProperty]
    private bool newIsActive = true;

    [ObservableProperty]
    private ISeries[] flexiSeries = Array.Empty<ISeries>();

    [ObservableProperty]
    private Axis[] flexiXAxis = Array.Empty<Axis>();

    public ObservableCollection<User> Users { get; } = new();

    public ObservableCollection<SessionReport> SessionReports { get; } = new();

    [RelayCommand]
    public async Task LoadAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = string.Empty;
            await RefreshAsync();
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task AddUserAsync()
    {
        if (string.IsNullOrWhiteSpace(NewUsername) || string.IsNullOrWhiteSpace(NewPassword))
        {
            StatusMessage = "الرجاء إدخال اسم مستخدم وكلمة مرور";
            return;
        }

        var role = NewIsAdmin ? UserRole.Admin : UserRole.User;
        await _userService.AddUserAsync(NewUsername.Trim(), NewPassword, role, NewFullName);
        StatusMessage = "تمت إضافة المستخدم";
        await RefreshUsersAsync();
        ClearForm();
    }

    [RelayCommand]
    private async Task UpdateUserAsync()
    {
        if (SelectedUser is null)
        {
            StatusMessage = "الرجاء اختيار مستخدم";
            return;
        }

        var role = NewIsAdmin ? UserRole.Admin : UserRole.User;
        await _userService.UpdateUserAsync(SelectedUser.Id, string.IsNullOrWhiteSpace(NewPassword) ? null : NewPassword, role, NewFullName, NewIsActive);
        StatusMessage = "تم تحديث بيانات المستخدم";
        await RefreshUsersAsync();
    }

    [RelayCommand]
    private async Task DeleteUserAsync()
    {
        if (SelectedUser is null)
        {
            StatusMessage = "الرجاء اختيار مستخدم";
            return;
        }

        await _userService.DeleteUserAsync(SelectedUser.Id);
        StatusMessage = "تم حذف المستخدم";
        await RefreshUsersAsync();
        ClearForm();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        Summary = await _reportService.GetAdminSummaryAsync();
        await RefreshUsersAsync();
        await RefreshSessionsAsync();
        await BuildFlexiChartAsync();
    }

    private async Task RefreshUsersAsync()
    {
        var users = await _userService.GetUsersAsync();
        Users.Clear();
        foreach (var user in users)
        {
            Users.Add(user);
        }
    }

    private async Task RefreshSessionsAsync()
    {
        var reports = await _reportService.GetSessionReportsAsync();
        SessionReports.Clear();
        foreach (var report in reports.Take(20))
        {
            SessionReports.Add(report);
        }
    }

    private async Task BuildFlexiChartAsync()
    {
        var chartData = await _reportService.GetFlexiConsumptionByUserAsync();
        var ordered = chartData.OrderByDescending(item => item.Value).ToList();
        var labels = ordered.Select(item => item.Key).ToArray();
        FlexiSeries = new ISeries[]
        {
            new ColumnSeries<decimal>
            {
                Values = ordered.Select(item => item.Value).ToArray(),
                Name = "الفليكسي المستهلك",
                Fill = new SolidColorPaint(SKColors.DeepSkyBlue)
            }
        };
        FlexiXAxis = new[]
        {
            new Axis
            {
                Labels = labels,
                LabelsRotation = -45,
                LabelsPaint = new SolidColorPaint(SKColors.Gray) { SKTypeface = SKTypeface.Default },
                TextSize = 14
            }
        };
    }

    partial void OnSelectedUserChanged(User? value)
    {
        if (value is null)
        {
            return;
        }

        NewUsername = value.Username;
        NewFullName = value.FullName ?? string.Empty;
        NewIsAdmin = value.Role == UserRole.Admin;
        NewIsActive = value.IsActive;
        NewPassword = string.Empty;
    }

    private void ClearForm()
    {
        NewUsername = string.Empty;
        NewFullName = string.Empty;
        NewPassword = string.Empty;
        NewIsAdmin = false;
        NewIsActive = true;
        SelectedUser = null;
    }
}
