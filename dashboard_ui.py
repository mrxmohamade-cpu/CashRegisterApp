"""Modern cashier dashboard with a clean, responsive layout."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
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

from database_setup import CashSession, FlexiTransaction, SessionLocal, Transaction
from ui_helpers import (
    ChartPlaceholder,
    ModernDashboardWindow,
    RecordTable,
    SessionDetailCard,
    SessionTable,
    StatisticGrid,
    SummaryCard,
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
        self.new_session_button.clicked.connect(self._show_new_session_placeholder)

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

        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(18)

        self.sessions_table = SessionTable()
        self.sessions_table.itemSelectionChanged.connect(self.handle_session_selection)
        content_layout.addWidget(self.sessions_table, 3)

        self.session_detail = SessionDetailCard()
        content_layout.addWidget(self.session_detail, 2)

        layout.addWidget(content_frame)
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

        sessions: Sequence[Dict] = data["sessions"]  # type: ignore[assignment]
        self.sessions_table.set_sessions(sessions)
        if sessions:
            self.sessions_table.selectRow(0)
            self.session_detail.update_session(sessions[0])
        else:
            self.session_detail.clear()

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

    # ------------------------------------------------------------------
    # Interactions
    # ------------------------------------------------------------------

    def handle_session_selection(self) -> None:
        row = self.sessions_table.currentRow()
        session = self.sessions_table.session_at(row)
        self.session_detail.update_session(session)

    def _show_new_session_placeholder(self) -> None:
        QMessageBox.information(
            self,
            "قريباً",
            "إدارة الجلسات من الواجهة الجديدة قيد التطوير. يمكنك حالياً مواصلة استخدام الأدوات التقليدية.",
        )

    # ------------------------------------------------------------------
    # Responsiveness
    # ------------------------------------------------------------------

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
