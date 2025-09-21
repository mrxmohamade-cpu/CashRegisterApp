using System.Collections.ObjectModel;
using System.Linq;
using CashRegisterMaui.Models;
using CashRegisterMaui.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace CashRegisterMaui.ViewModels;

public partial class UserDashboardViewModel : ViewModelBase
{
    private readonly AppState _appState;
    private readonly ISessionService _sessionService;
    private readonly IReportService _reportService;

    public UserDashboardViewModel(AppState appState, ISessionService sessionService, IReportService reportService)
    {
        _appState = appState;
        _sessionService = sessionService;
        _reportService = reportService;
        Title = "لوحة المستخدم";
    }

    [ObservableProperty]
    private CashSession? currentSession;

    [ObservableProperty]
    private DashboardSummary summary = new();

    [ObservableProperty]
    private decimal openingCash;

    [ObservableProperty]
    private decimal openingFlexi;

    [ObservableProperty]
    private decimal closingCash;

    [ObservableProperty]
    private decimal closingFlexi;

    [ObservableProperty]
    private string? sessionNotes;

    [ObservableProperty]
    private decimal newExpenseAmount;

    [ObservableProperty]
    private string? newExpenseDescription;

    [ObservableProperty]
    private decimal newFlexiAmount;

    [ObservableProperty]
    private bool newFlexiIsPaid;

    [ObservableProperty]
    private string? newFlexiNotes;

    public ObservableCollection<Transaction> RecentExpenses { get; } = new();

    public ObservableCollection<FlexiTransaction> RecentFlexi { get; } = new();

    public ObservableCollection<CashSession> SessionHistory { get; } = new();

    [RelayCommand]
    public async Task LoadAsync()
    {
        if (_appState.CurrentUser is null)
        {
            return;
        }

        try
        {
            IsBusy = true;
            await RefreshDataAsync(_appState.CurrentUser.Id);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task OpenSessionAsync()
    {
        if (_appState.CurrentUser is null)
        {
            return;
        }

        await _sessionService.OpenSessionAsync(_appState.CurrentUser.Id, OpeningCash, OpeningFlexi, sessionNotes: SessionNotes);
        await LoadAsync();
        OpeningCash = 0;
        OpeningFlexi = 0;
    }

    [RelayCommand]
    private async Task CloseSessionAsync()
    {
        if (CurrentSession is null)
        {
            return;
        }

        await _sessionService.CloseSessionAsync(CurrentSession.Id, ClosingCash, ClosingFlexi, SessionNotes);
        await LoadAsync();
        ClosingCash = 0;
        ClosingFlexi = 0;
        SessionNotes = string.Empty;
    }

    [RelayCommand]
    private async Task AddExpenseAsync()
    {
        if (CurrentSession is null || NewExpenseAmount <= 0)
        {
            return;
        }

        await _sessionService.AddExpenseAsync(CurrentSession.Id, NewExpenseAmount, NewExpenseDescription);
        NewExpenseAmount = 0;
        NewExpenseDescription = string.Empty;
        await LoadAsync();
    }

    [RelayCommand]
    private async Task AddFlexiAsync()
    {
        if (CurrentSession is null || NewFlexiAmount <= 0)
        {
            return;
        }

        await _sessionService.AddFlexiAsync(CurrentSession.Id, NewFlexiAmount, NewFlexiIsPaid, NewFlexiNotes);
        NewFlexiAmount = 0;
        NewFlexiNotes = string.Empty;
        NewFlexiIsPaid = false;
        await LoadAsync();
    }

    private async Task RefreshDataAsync(int userId)
    {
        CurrentSession = await _sessionService.GetActiveSessionAsync(userId);
        if (CurrentSession is not null)
        {
            ClosingCash = CurrentSession.ClosingCash;
            ClosingFlexi = CurrentSession.ClosingFlexi;
            SessionNotes = CurrentSession.Notes;
        }
        else
        {
            ClosingCash = 0;
            ClosingFlexi = 0;
            SessionNotes = string.Empty;
        }

        Summary = await _reportService.GetUserSummaryAsync(userId);

        var sessions = await _sessionService.GetSessionsAsync(userId: userId);
        SessionHistory.Clear();
        foreach (var session in sessions)
        {
            SessionHistory.Add(session);
        }

        RecentExpenses.Clear();
        foreach (var transaction in sessions.SelectMany(s => s.Transactions).OrderByDescending(t => t.CreatedAt).Take(10))
        {
            RecentExpenses.Add(transaction);
        }

        RecentFlexi.Clear();
        foreach (var flexi in sessions.SelectMany(s => s.FlexiTransactions).OrderByDescending(f => f.CreatedAt).Take(10))
        {
            RecentFlexi.Add(flexi);
        }

        OpeningCash = 0;
        OpeningFlexi = 0;
    }
}
