"""Modern cashier dashboard with a clean, responsive layout."""
from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QBoxLayout,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

try:
    from PyQt6.QtCharts import (
        QCategoryAxis,
        QChart,
        QChartView,
        QLineSeries,
        QPieSeries,
        QValueAxis,
    )

    CHARTS_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    CHARTS_AVAILABLE = False
    QCategoryAxis = QChart = QChartView = QLineSeries = QPieSeries = QValueAxis = None  # type: ignore

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from database_setup import CashSession, FlexiTransaction, SessionLocal, Transaction
from ui_helpers import (
    ChartPlaceholder,
    CloseSessionDialog,
    FlexiDialog,
    FlexiTable,
    ModernDashboardWindow,
    NotesPanel,
    OpenSessionDialog,
    RecordTable,
    SessionDetailCard,
    SessionTable,
    StatisticGrid,
    SummaryCard,
    TransactionTable,
    ExpenseDialog,
    create_shadow,
    format_currency,
    format_datetime,
    format_duration,
)


class DashboardRepository:
    """Collects and formats dashboard data for the authenticated user."""

    def __init__(self, user) -> None:
        self.user = user

    def fetch(self) -> Dict[str, object]:
        with SessionLocal() as db:
            sessions: List[CashSession] = (
                db.query(CashSession)
                .filter(CashSession.user_id == self.user.id)
                .order_by(CashSession.start_time.desc())
                .all()
            )

            session_rows: List[Dict] = []
            expense_rows: List[Dict] = []
            flexi_rows: List[Dict] = []
            trend_map: Dict = defaultdict(lambda: {"income": 0.0, "expense": 0.0})

            total_income = 0.0
            total_expense = 0.0
            open_sessions = 0

            for session in sessions:
                transactions: Sequence[Transaction] = list(session.transactions)
                flexi_ops: Sequence[FlexiTransaction] = list(session.flexi_transactions)

                income_sum = sum(t.amount for t in transactions if t.type == "income")
                expense_sum = sum(t.amount for t in transactions if t.type == "expense")
                profit = income_sum - expense_sum
                flexi_consumed = session.flexi_consumed or 0.0
                start_balance = session.start_balance or 0.0
                end_balance = session.end_balance

                if session.status == "open":
                    open_sessions += 1

                total_income += income_sum
                total_expense += expense_sum

                day_key = session.start_time.date() if session.start_time else None
                if day_key is not None:
                    trend_map[day_key]["income"] += income_sum
                    trend_map[day_key]["expense"] += expense_sum

                session_rows.append(
                    {
                        "id": session.id,
                        "status": session.status,
                        "start": session.start_time,
                        "end": session.end_time,
                        "owner": self.user.username,
                        "start_display": format_datetime(session.start_time),
                        "end_display": format_datetime(session.end_time),
                        "duration": format_duration(session.start_time, session.end_time),
                        "start_balance": start_balance,
                        "end_balance": end_balance,
                        "income": income_sum,
                        "expense": expense_sum,
                        "profit": profit,
                        "flexi_consumed": flexi_consumed,
                        "notes": session.notes or "",
                        "recent_display": format_datetime(session.end_time or session.start_time),
                    }
                )

                for txn in transactions:
                    if txn.type != "expense":
                        continue
                    expense_rows.append(
                        {
                            "description": txn.description or "—",
                            "amount": txn.amount,
                            "session_id": session.id,
                            "timestamp": txn.timestamp,
                        }
                    )

                for record in flexi_ops:
                    flexi_rows.append(
                        {
                            "description": record.description or "—",
                            "amount": record.amount,
                            "is_paid": bool(record.is_paid),
                            "timestamp": record.timestamp,
                        }
                    )

            expense_rows.sort(key=lambda row: row["timestamp"] or 0, reverse=True)
            flexi_rows.sort(key=lambda row: row["timestamp"] or 0, reverse=True)

            sorted_days = sorted(trend_map.keys())
            trend_labels = [day.strftime("%d/%m") for day in sorted_days]
            trend_income = [trend_map[day]["income"] for day in sorted_days]
            trend_expense = [trend_map[day]["expense"] for day in sorted_days]

            total_sessions = len(session_rows)
            net_profit = total_income - total_expense
            average_profit = net_profit / total_sessions if total_sessions else 0.0

            summary = {
                "profit": total_income,
                "expenses": total_expense,
                "balance": net_profit,
                "total_sessions": total_sessions,
                "open_sessions": open_sessions,
                "expense_count": len(expense_rows),
                "average_profit": average_profit,
            }

            return {
                "summary": summary,
                "sessions": session_rows,
                "recent_sessions": session_rows[:6],
                "expenses": expense_rows,
                "flexi": flexi_rows,
                "trend": {
                    "labels": trend_labels,
                    "income": trend_income,
                    "expense": trend_expense,
                },
                "pie": {
                    "profit": max(net_profit, 0.0),
                    "expense": total_expense,
                },
            }


class UserDashboard(ModernDashboardWindow):
    """Main dashboard window for cashiers with a curated, modern layout."""

    def __init__(self, user) -> None:
        super().__init__(
            window_title="لوحة المستخدم - النسخة الخرافية",
            brand_title="لوحة القيادة",
            brand_tagline="جميع الجلسات، المصاريف، والفليكسي في واجهة واحدة",
            user=user,
        )
        self.repository = DashboardRepository(user)
        self.summary_cards: Dict[str, SummaryCard] = {}
        self.db = SessionLocal()
        self.current_session: Optional[CashSession] = None
        self.current_session_id: Optional[int] = None
        self.active_session: Optional[CashSession] = None

        self._build_pages()
        self._configure_actions()
        self.refresh_dashboard()

    # ------------------------------------------------------------------
    # UI assembly
    # ------------------------------------------------------------------

    def _configure_actions(self) -> None:
        self.refresh_button.setToolTip("تحديث البيانات من قاعدة المعلومات")
        self.refresh_button.clicked.connect(self.refresh_dashboard)

        self.new_session_button = QPushButton("بدء جلسة جديدة")
        self.new_session_button.setProperty("variant", "secondary")
        self.add_header_button(self.new_session_button, before_refresh=True)
        self.new_session_button.clicked.connect(self.open_cash_session)

        self.set_sidebar_footer("مرحباً %s! حافظ على تدفق العمل من خلال لوحة النسخة الخرافية." % self.user.username)

    def _build_pages(self) -> None:
        self.add_nav_label("التصفح")

        overview_page = self._create_overview_page()
        self.add_page(
            "overview",
            title="نظرة عامة",
            subtitle="ملخص مالي ورسوم بيانية لحركة الصندوق",
            nav_label="🏠 نظرة عامة",
            widget=overview_page,
        )

        sessions_page = self._create_sessions_page()
        self.add_page(
            "sessions",
            title="سجل الجلسات",
            subtitle="استعرض كل جلساتك مع تفاصيل دقيقة",
            nav_label="🗂 الجلسات",
            widget=sessions_page,
        )

        expenses_page = self._create_expenses_page()
        self.add_page(
            "expenses",
            title="المصاريف",
            subtitle="تابع المصاريف اليومية ورتبها بسهولة",
            nav_label="💸 المصاريف",
            widget=expenses_page,
        )

        flexi_page = self._create_flexi_page()
        self.add_page(
            "flexi",
            title="عمليات الفليكسي",
            subtitle="الفليكسي في مكان واحد مع حالة الدفع",
            nav_label="➕ الفليكسي",
            widget=flexi_page,
        )

    def _create_overview_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.summary_grid = StatisticGrid()
        self.summary_cards = {
            "profit": SummaryCard("إجمالي الأرباح", role="positive"),
            "expenses": SummaryCard("إجمالي المصاريف", role="negative"),
            "balance": SummaryCard("صافي الرصيد", role="info"),
        }
        for card in self.summary_cards.values():
            self.summary_grid.add_card(card)
        layout.addWidget(self.summary_grid)

        charts_frame = QFrame()
        charts_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(18)
        charts_frame.setLayout(charts_layout)
        self.charts_layout = charts_layout

        # Trend chart (line)
        trend_container = QFrame()
        self.trend_stack = QStackedLayout(trend_container)
        if CHARTS_AVAILABLE:
            self.revenue_chart = QChart()
            self.revenue_chart.legend().setVisible(True)
            self.revenue_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            self.revenue_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

            self.revenue_chart_view = QChartView(self.revenue_chart)
            self.revenue_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.trend_stack.addWidget(self.revenue_chart_view)
        self.trend_placeholder = ChartPlaceholder("سيظهر الرسم البياني بعد تسجيل بعض الجلسات")
        self.trend_stack.addWidget(self.trend_placeholder)
        self.trend_stack.setCurrentWidget(self.trend_placeholder)
        charts_layout.addWidget(trend_container, 3)

        # Pie chart
        pie_container = QFrame()
        self.pie_stack = QStackedLayout(pie_container)
        if CHARTS_AVAILABLE:
            self.pie_chart = QChart()
            self.pie_chart.legend().setVisible(True)
            self.pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            self.pie_chart_view = QChartView(self.pie_chart)
            self.pie_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.pie_stack.addWidget(self.pie_chart_view)
        self.pie_placeholder = ChartPlaceholder("لم يتم رصد نسب الأرباح والمصاريف بعد")
        self.pie_stack.addWidget(self.pie_placeholder)
        self.pie_stack.setCurrentWidget(self.pie_placeholder)
        charts_layout.addWidget(pie_container, 2)

        layout.addWidget(charts_frame)

        recent_header = QLabel("أحدث الجلسات")
        recent_header.setObjectName("SectionTitle")
        layout.addWidget(recent_header)

        self.recent_table = RecordTable(
            ["الجلسة", "الحالة", "الربح", "آخر تحديث"],
            numeric_columns=[2],
        )
        layout.addWidget(self.recent_table)

        return page

    def _create_sessions_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        header = QLabel("سجل الجلسات الاحترافي")
        header.setObjectName("SectionTitle")
        layout.addWidget(header)

        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(12)

        self.open_session_btn = QPushButton("فتح جلسة")
        self.open_session_btn.setProperty("variant", "secondary")
        self.open_session_btn.clicked.connect(self.open_cash_session)
        actions_layout.addWidget(self.open_session_btn)

        self.add_expense_btn = QPushButton("إضافة مصروف")
        self.add_expense_btn.setProperty("variant", "secondary")
        self.add_expense_btn.clicked.connect(self.add_expense)
        actions_layout.addWidget(self.add_expense_btn)

        self.add_flexi_btn = QPushButton("إضافة فليكسي")
        self.add_flexi_btn.setProperty("variant", "secondary")
        self.add_flexi_btn.clicked.connect(self.add_flexi)
        actions_layout.addWidget(self.add_flexi_btn)

        self.close_session_btn = QPushButton("إغلاق الجلسة")
        self.close_session_btn.setProperty("variant", "primary")
        self.close_session_btn.clicked.connect(self.close_cash_session)
        actions_layout.addWidget(self.close_session_btn)

        actions_layout.addStretch(1)
        layout.addWidget(actions_frame)

        splitter = QSplitter()
        splitter.setObjectName("SessionsSplitter")

        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        sessions_label = QLabel("الجلسات")
        sessions_label.setObjectName("SectionSubtitle")
        left_layout.addWidget(sessions_label)

        self.sessions_table = SessionTable()
        self.sessions_table.itemSelectionChanged.connect(self.handle_session_selection)
        left_layout.addWidget(self.sessions_table)

        splitter.addWidget(left_panel)

        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(18)

        self.session_detail = SessionDetailCard()
        create_shadow(self.session_detail, blur=36, y_offset=18, alpha=70)
        right_layout.addWidget(self.session_detail)

        self.notes_panel = NotesPanel()
        create_shadow(self.notes_panel, blur=36, y_offset=18, alpha=70)
        self.notes_panel.save_button.clicked.connect(self.save_session_notes)
        right_layout.addWidget(self.notes_panel)

        transactions_frame = QFrame()
        transactions_frame.setObjectName("TransactionsFrame")
        transactions_layout = QVBoxLayout(transactions_frame)
        transactions_layout.setContentsMargins(22, 22, 22, 22)
        transactions_layout.setSpacing(12)
        transactions_label = QLabel("المصاريف")
        transactions_label.setObjectName("SectionSubtitle")
        transactions_layout.addWidget(transactions_label)
        self.transactions_table = TransactionTable()
        self.transactions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.transactions_table.customContextMenuRequested.connect(self._open_transaction_menu)
        transactions_layout.addWidget(self.transactions_table)
        create_shadow(transactions_frame, blur=32, y_offset=16, alpha=60)
        right_layout.addWidget(transactions_frame)

        flexi_frame = QFrame()
        flexi_frame.setObjectName("FlexiFrame")
        flexi_layout = QVBoxLayout(flexi_frame)
        flexi_layout.setContentsMargins(22, 22, 22, 22)
        flexi_layout.setSpacing(12)
        flexi_label = QLabel("عمليات الفليكسي")
        flexi_label.setObjectName("SectionSubtitle")
        flexi_layout.addWidget(flexi_label)
        self.flexi_table = FlexiTable()
        self.flexi_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.flexi_table.customContextMenuRequested.connect(self._open_flexi_menu)
        flexi_layout.addWidget(self.flexi_table)
        create_shadow(flexi_frame, blur=32, y_offset=16, alpha=60)
        right_layout.addWidget(flexi_frame)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter)
        return page

    def _create_expenses_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        header = QLabel("مصروفاتك بالتفصيل")
        header.setObjectName("SectionTitle")
        layout.addWidget(header)

        self.expenses_table = RecordTable(
            ["الوصف", "المبلغ", "رقم الجلسة", "التاريخ"],
            numeric_columns=[1],
        )
        layout.addWidget(self.expenses_table)
        return page

    def _create_flexi_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        header = QLabel("إدارات الفليكسي")
        header.setObjectName("SectionTitle")
        layout.addWidget(header)

        self.flexi_table = RecordTable(
            ["الوصف", "المبلغ", "الحالة", "التاريخ"],
            numeric_columns=[1],
        )
        layout.addWidget(self.flexi_table)
        return page
    # ------------------------------------------------------------------
    # Data binding
    # ------------------------------------------------------------------

    def refresh_dashboard(self) -> None:  # type: ignore[override]
        data = self.repository.fetch()
        summary = data["summary"]

        self.summary_cards["profit"].set_metric(
            format_currency(summary["profit"]),
            f"{summary['total_sessions']} جلسة مسجلة",
        )
        self.summary_cards["expenses"].set_metric(
            format_currency(summary["expenses"]),
            f"{summary['expense_count']} عملية مصروف",
        )
        average_caption = (
            f"متوسط {format_currency(summary['average_profit'])} لكل جلسة"
            if summary["total_sessions"]
            else "ابدأ أول جلسة لك للبدء بالتحليل"
        )
        self.summary_cards["balance"].set_metric(
            format_currency(summary["balance"]),
            average_caption,
        )

        self._refresh_active_session()

        sessions: Sequence[Dict] = data["sessions"]  # type: ignore[assignment]
        previous_id = self.current_session_id
        self.sessions_table.set_sessions(sessions)
        if sessions:
            target_row = 0
            if previous_id is not None:
                for index, item in enumerate(sessions):
                    if item["id"] == previous_id:
                        target_row = index
                        break
            elif self.active_session is not None:
                for index, item in enumerate(sessions):
                    if item["id"] == self.active_session.id:
                        target_row = index
                        break
            self.sessions_table.selectRow(target_row)
            self.handle_session_selection()
        else:
            self.current_session = None
            self.current_session_id = None
            self.session_detail.clear()
            self.notes_panel.set_text("")
            self.notes_panel.set_editable(False)
            self.transactions_table.clear_transactions()
            self.flexi_table.clear_records()
            self._update_action_states(None)

        self._update_recent_sessions(data["recent_sessions"])  # type: ignore[arg-type]
        self._update_expenses(data["expenses"])  # type: ignore[arg-type]
        self._update_flexi(data["flexi"])  # type: ignore[arg-type]
        self._update_trend_chart(data["trend"])  # type: ignore[arg-type]
        self._update_pie_chart(data["pie"])  # type: ignore[arg-type]

    def _update_recent_sessions(self, sessions: Sequence[Dict]) -> None:
        rows = []
        for session in sessions:
            rows.append(
                [
                    f"جلسة #{session['id']}",
                    "مفتوحة" if session["status"] == "open" else "مغلقة",
                    format_currency(session["profit"]),
                    session["recent_display"],
                ]
            )
        self.recent_table.set_records(rows)

    def _update_expenses(self, expenses: Sequence[Dict]) -> None:
        rows = []
        for expense in expenses:
            rows.append(
                [
                    expense["description"],
                    format_currency(expense["amount"]),
                    f"#{expense['session_id']}",
                    format_datetime(expense["timestamp"]),
                ]
            )
        self.expenses_table.set_records(rows)

    def _update_flexi(self, records: Sequence[Dict]) -> None:
        rows = []
        for record in records:
            rows.append(
                [
                    record["description"],
                    format_currency(record["amount"]),
                    "مدفوع" if record["is_paid"] else "قيد التحصيل",
                    format_datetime(record["timestamp"]),
                ]
            )
        self.flexi_table.set_records(rows)

    def _update_trend_chart(self, trend: Dict[str, Sequence[float]]) -> None:
        if not CHARTS_AVAILABLE:
            self.trend_placeholder.set_message("قم بتثبيت PyQt6.QtCharts لعرض الرسم البياني")
            self.trend_stack.setCurrentWidget(self.trend_placeholder)
            return

        labels = list(trend.get("labels", []))
        incomes = list(trend.get("income", []))
        expenses = list(trend.get("expense", []))

        if not labels:
            self.trend_stack.setCurrentWidget(self.trend_placeholder)
            return

        self.revenue_chart.removeAllSeries()
        for axis in list(self.revenue_chart.axes()):
            self.revenue_chart.removeAxis(axis)
        income_series = QLineSeries()
        income_series.setName("الإيرادات")
        expense_series = QLineSeries()
        expense_series.setName("المصاريف")

        for index, value in enumerate(incomes):
            income_series.append(float(index), float(value))
        for index, value in enumerate(expenses):
            expense_series.append(float(index), float(value))

        self.revenue_chart.addSeries(income_series)
        self.revenue_chart.addSeries(expense_series)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
        for index, label in enumerate(labels):
            axis_x.append(label, float(index))
        axis_x.setRange(0, max(len(labels) - 1, 0))

        max_value = max(incomes + expenses) if incomes or expenses else 0.0
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        axis_y.setRange(0, max(max_value * 1.1, 10.0))

        self.revenue_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.revenue_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        income_series.attachAxis(axis_x)
        income_series.attachAxis(axis_y)
        expense_series.attachAxis(axis_x)
        expense_series.attachAxis(axis_y)

        self.trend_stack.setCurrentWidget(self.revenue_chart_view)

    def _update_pie_chart(self, pie: Dict[str, float]) -> None:
        if not CHARTS_AVAILABLE:
            self.pie_placeholder.set_message("قم بتثبيت PyQt6.QtCharts لعرض الرسم البياني")
            self.pie_stack.setCurrentWidget(self.pie_placeholder)
            return

        profit = float(pie.get("profit", 0.0))
        expense = float(pie.get("expense", 0.0))
        total = profit + expense

        if total <= 0:
            self.pie_stack.setCurrentWidget(self.pie_placeholder)
            return

        self.pie_chart.removeAllSeries()
        series = QPieSeries()
        if profit > 0:
            series.append("الأرباح", profit)
        if expense > 0:
            series.append("المصاريف", expense)
        self.pie_chart.addSeries(series)
        self.pie_stack.setCurrentWidget(self.pie_chart_view)

    def _refresh_active_session(self) -> None:
        try:
            self.active_session = (
                self.db.query(CashSession)
                .options(joinedload(CashSession.transactions), joinedload(CashSession.flexi_transactions))
                .filter(CashSession.user_id == self.user.id, CashSession.status == "open")
                .first()
            )
        except Exception:
            self.active_session = None

    def _fetch_session(self, session_id: int) -> Optional[CashSession]:
        try:
            return (
                self.db.query(CashSession)
                .options(joinedload(CashSession.transactions), joinedload(CashSession.flexi_transactions))
                .filter(CashSession.id == session_id)
                .one_or_none()
            )
        except Exception:
            return None

    def _load_transactions(self) -> None:
        if not self.current_session:
            self.transactions_table.clear_transactions()
            return
        expenses = [
            txn
            for txn in getattr(self.current_session, "transactions", [])
            if getattr(txn, "type", "expense") == "expense"
        ]
        expenses.sort(
            key=lambda txn: getattr(txn, "timestamp", None) or datetime.datetime.min,
            reverse=True,
        )
        self.transactions_table.set_transactions(expenses)

    def _load_flexi_records(self) -> None:
        if not self.current_session:
            self.flexi_table.clear_records()
            return
        records = list(getattr(self.current_session, "flexi_transactions", []))
        records.sort(
            key=lambda record: getattr(record, "timestamp", None) or datetime.datetime.min,
            reverse=True,
        )
        self.flexi_table.set_records(records)

    def _update_action_states(self, status: Optional[str]) -> None:
        has_open = self.active_session is not None
        is_selected_open = status == "open"
        self.new_session_button.setEnabled(not has_open)
        self.open_session_btn.setEnabled(not has_open)
        for button in (self.add_expense_btn, self.add_flexi_btn, self.close_session_btn):
            button.setEnabled(is_selected_open)
        self.notes_panel.set_editable(bool(is_selected_open))

    # ------------------------------------------------------------------
    # Interactions
    # ------------------------------------------------------------------

    def handle_session_selection(self) -> None:
        row = self.sessions_table.currentRow()
        session = self.sessions_table.session_at(row)
        self._display_session(session)

    def _display_session(self, session: Optional[Dict]) -> None:
        if not session:
            self.session_detail.clear()
            self.notes_panel.set_text("")
            self.notes_panel.set_editable(False)
            self.transactions_table.clear_transactions()
            self.flexi_table.clear_records()
            self.current_session = None
            self.current_session_id = None
            self._update_action_states(None)
            return

        self.session_detail.update_session(session)
        self.current_session_id = session["id"]
        self.notes_panel.set_text(session.get("notes", ""))

        record = self._fetch_session(session["id"])
        self.current_session = record

        self._load_transactions()
        self._load_flexi_records()
        self._update_action_states(session.get("status"))

    def open_cash_session(self) -> None:
        if self.active_session is not None:
            QMessageBox.warning(self, "جلسة مفتوحة", "يوجد بالفعل جلسة قيد التنفيذ. يرجى إغلاقها أولاً.")
            return

        dialog = OpenSessionDialog(self)
        if dialog.exec() != int(QDialog.DialogCode.Accepted):
            return
        payload = dialog.data() or {}
        try:
            start_balance = float(payload.get("start_balance", 0.0))
            start_flexi = float(payload.get("start_flexi", 0.0))
        except (TypeError, ValueError):
            QMessageBox.warning(self, "بيانات غير صالحة", "تعذر قراءة قيم الرصيد المدخلة.")
            return

        new_session = CashSession(
            user_id=self.user.id,
            start_balance=start_balance,
            start_flexi=start_flexi,
            status="open",
            start_time=datetime.datetime.now(datetime.timezone.utc),
        )
        try:
            self.db.add(new_session)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "حدث خطأ أثناء فتح الجلسة. حاول مرة أخرى.")
            return

        QMessageBox.information(self, "نجاح", "تم فتح الجلسة بنجاح.")
        self.db.expire_all()
        self.current_session_id = new_session.id
        self.refresh_dashboard()

    def add_expense(self) -> None:
        session = self.current_session if self.current_session and self.current_session.status == "open" else self.active_session
        if not session or session.status != "open":
            QMessageBox.warning(self, "لا توجد جلسة", "افتح جلسة قبل تسجيل المصاريف.")
            return

        dialog = ExpenseDialog(self)
        if dialog.exec() != int(QDialog.DialogCode.Accepted):
            return
        payload = dialog.data() or {}
        amount = payload.get("amount")
        if amount is None:
            QMessageBox.warning(self, "بيانات غير صالحة", "يرجى إدخال مبلغ صحيح.")
            return
        transaction = Transaction(
            session_id=session.id,
            type="expense",
            amount=float(amount),
            description=str(payload.get("description", "")),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        try:
            self.db.add(transaction)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر حفظ المصروف. حاول مجدداً.")
            return

        QMessageBox.information(self, "تم", "تم تسجيل المصروف بنجاح.")
        self.db.expire_all()
        self.current_session_id = session.id
        self.refresh_dashboard()

    def add_flexi(self) -> None:
        session = self.current_session if self.current_session and self.current_session.status == "open" else self.active_session
        if not session or session.status != "open":
            QMessageBox.warning(self, "لا توجد جلسة", "افتح جلسة قبل إضافة الفليكسي.")
            return

        dialog = FlexiDialog(self)
        if dialog.exec() != int(QDialog.DialogCode.Accepted):
            return
        payload = dialog.data() or {}
        amount = payload.get("amount")
        if amount is None:
            QMessageBox.warning(self, "بيانات غير صالحة", "يرجى إدخال مبلغ صحيح.")
            return
        record = FlexiTransaction(
            session_id=session.id,
            user_id=self.user.id,
            amount=float(amount),
            description=str(payload.get("description", "")),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            is_paid=bool(payload.get("is_paid", False)),
        )
        try:
            self.db.add(record)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر تسجيل عملية الفليكسي.")
            return

        QMessageBox.information(self, "تم", "تمت إضافة عملية الفليكسي.")
        self.db.expire_all()
        self.current_session_id = session.id
        self.refresh_dashboard()

    def close_cash_session(self) -> None:
        session = self.current_session if self.current_session and self.current_session.status == "open" else self.active_session
        if not session or session.status != "open":
            QMessageBox.warning(self, "لا توجد جلسة", "لا توجد جلسة مفتوحة لإغلاقها.")
            return

        summary = {
            "start_balance": session.start_balance or 0.0,
            "total_expense": session.total_expense if hasattr(session, "total_expense") else 0.0,
            "flexi_added": session.total_flexi_additions if hasattr(session, "total_flexi_additions") else 0.0,
        }
        dialog = CloseSessionDialog(summary, self)
        if dialog.exec() != int(QDialog.DialogCode.Accepted):
            return
        payload = dialog.data() or {}
        end_balance = payload.get("end_balance")
        end_flexi = payload.get("end_flexi")
        if end_balance is None or end_flexi is None:
            QMessageBox.warning(self, "بيانات غير صالحة", "يرجى إدخال أرصدة الإغلاق بشكل صحيح.")
            return

        session.end_balance = float(end_balance)
        session.end_flexi = float(end_flexi)
        session.status = "closed"
        session.end_time = datetime.datetime.now(datetime.timezone.utc)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر إغلاق الجلسة. حاول مرة أخرى.")
            return

        QMessageBox.information(self, "تم", "تم إغلاق الجلسة بنجاح.")
        self.db.expire_all()
        self.current_session_id = session.id
        self.refresh_dashboard()

    def save_session_notes(self) -> None:
        if not self.current_session or self.current_session.status != "open":
            QMessageBox.warning(self, "تعذر الحفظ", "يمكن تعديل الملاحظات للجلسات المفتوحة فقط.")
            return

        self.current_session.notes = self.notes_panel.text()
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر حفظ الملاحظات. حاول مرة أخرى.")
            return

        QMessageBox.information(self, "تم", "تم حفظ الملاحظات بنجاح.")
        self.db.expire_all()
        self.refresh_dashboard()

    def _open_transaction_menu(self, position) -> None:
        if not self.current_session or self.current_session.status != "open":
            return
        row = self.transactions_table.rowAt(position.y())
        if row < 0:
            return
        transaction = self.transactions_table.transaction_at(row)
        if transaction is None:
            return

        menu = QMenu(self)
        edit_action = menu.addAction("تعديل المصروف")
        delete_action = menu.addAction("حذف المصروف")
        action = menu.exec(self.transactions_table.mapToGlobal(position))
        if action == edit_action:
            self._edit_transaction(transaction)
        elif action == delete_action:
            self._delete_transaction(transaction)

    def _edit_transaction(self, transaction: Transaction) -> None:
        dialog = ExpenseDialog(
            self,
            description=transaction.description or "",
            amount=transaction.amount,
        )
        if dialog.exec() != int(QDialog.DialogCode.Accepted):
            return
        payload = dialog.data() or {}
        amount = payload.get("amount")
        if amount is None:
            return
        transaction.amount = float(amount)
        transaction.description = str(payload.get("description", ""))
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر تحديث المصروف.")
            return

        self.db.expire_all()
        self.refresh_dashboard()

    def _delete_transaction(self, transaction: Transaction) -> None:
        confirmation = QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف المصروف المحدد؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        try:
            self.db.delete(transaction)
            self.db.commit()
        except Exception:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر حذف المصروف.")
            return

        self.db.expire_all()
        self.refresh_dashboard()

    def _open_flexi_menu(self, position) -> None:
        if not self.current_session or self.current_session.status != "open":
            return
        row = self.flexi_table.rowAt(position.y())
        if row < 0:
            return
        record = self.flexi_table.record_at(row)
        if record is None:
            return

        menu = QMenu(self)
        edit_action = menu.addAction("تعديل العملية")
        toggle_action = menu.addAction("تبديل حالة الدفع")
        delete_action = menu.addAction("حذف العملية")
        action = menu.exec(self.flexi_table.mapToGlobal(position))
        if action == edit_action:
            self._edit_flexi_record(record)
        elif action == toggle_action:
            self._toggle_flexi_status(record)
        elif action == delete_action:
            self._delete_flexi_record(record)

    def _edit_flexi_record(self, record: FlexiTransaction) -> None:
        dialog = FlexiDialog(
            self,
            description=record.description or "",
            amount=record.amount,
            is_paid=bool(record.is_paid),
        )
        if dialog.exec() != int(QDialog.DialogCode.Accepted):
            return
        payload = dialog.data() or {}
        amount = payload.get("amount")
        if amount is None:
            return
        record.amount = float(amount)
        record.description = str(payload.get("description", ""))
        record.is_paid = bool(payload.get("is_paid", False))
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر تحديث عملية الفليكسي.")
            return

        self.db.expire_all()
        self.refresh_dashboard()

    def _delete_flexi_record(self, record: FlexiTransaction) -> None:
        confirmation = QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل ترغب بحذف عملية الفليكسي؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        try:
            self.db.delete(record)
            self.db.commit()
        except Exception:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر حذف العملية.")
            return

        self.db.expire_all()
        self.refresh_dashboard()

    def _toggle_flexi_status(self, record: FlexiTransaction) -> None:
        record.is_paid = not bool(record.is_paid)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            QMessageBox.critical(self, "خطأ", "تعذر تحديث حالة الدفع.")
            record.is_paid = not record.is_paid
            return

        status_text = "تم وضع الحالة على مدفوع" if record.is_paid else "تم وضع الحالة على قيد التحصيل"
        QMessageBox.information(self, "تم", status_text)
        self.db.expire_all()
        self.refresh_dashboard()

    # ------------------------------------------------------------------
    # Responsiveness
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # type: ignore[override]
        try:
            self.db.close()
        except Exception:
            pass
        super().closeEvent(event)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        width = event.size().width()
        self.summary_grid.update_layout(width)
        self._update_chart_layout(width)

    def _update_chart_layout(self, width: int) -> None:
        if width < 1280:
            self.charts_layout.setDirection(QBoxLayout.Direction.TopToBottom)
        else:
            self.charts_layout.setDirection(QBoxLayout.Direction.LeftToRight)
