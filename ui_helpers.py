"""Reusable UI helpers for the modern Cash Register dashboards."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
)


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def create_shadow(widget: QWidget, *, blur: int = 38, y_offset: int = 18, alpha: int = 80) -> None:
    """Apply a soft drop shadow to elevate a widget."""

    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(15, 23, 42, alpha))
    widget.setGraphicsEffect(shadow)


def format_currency(value: float) -> str:
    """Format numbers with thousands separators and دج suffix."""

    return f"{value:,.2f} دج".replace(",", " ")


def format_datetime(value) -> str:
    if value is None:
        return "—"
    try:
        return value.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(value)


def format_duration(start, end) -> str:
    if not start or not end:
        return "—"
    try:
        delta = end - start
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f"{hours} س {minutes} د"
    except Exception:
        return "—"


# ---------------------------------------------------------------------------
# Navigation sidebar button
# ---------------------------------------------------------------------------


class NavigationButton(QPushButton):
    """Styled navigation button used inside the sidebar."""

    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.setProperty("isNav", True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(46)


# ---------------------------------------------------------------------------
# Summary cards and responsive grid
# ---------------------------------------------------------------------------


class SummaryCard(QFrame):
    """A rounded statistic card that highlights a headline metric."""

    def __init__(self, title: str, *, role: str = "neutral", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("SummaryCard")
        self.setProperty("accentRole", role)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.value_label = QLabel("0")
        self.value_label.setObjectName("CardValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.caption_label = QLabel("—")
        self.caption_label.setObjectName("CardCaption")
        self.caption_label.setWordWrap(True)
        self.caption_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.caption_label)

    def set_metric(self, value: str, caption: str) -> None:
        self.value_label.setText(value)
        self.caption_label.setText(caption)


class StatisticGrid(QWidget):
    """Responsive grid that reflows summary cards by available width."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._cards: List[SummaryCard] = []
        self._columns = 3
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(18)
        self._grid.setVerticalSpacing(18)

    def add_card(self, card: SummaryCard) -> None:
        self._cards.append(card)
        self._grid.addWidget(card, 0, len(self._cards) - 1)
        self._relayout()

    def cards(self) -> Sequence[SummaryCard]:
        return tuple(self._cards)

    def _relayout(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        for index, card in enumerate(self._cards):
            row = index // self._columns
            col = index % self._columns
            self._grid.addWidget(card, row, col)

    def update_layout(self, width: Optional[int] = None) -> None:
        if width is None:
            width = max(1, self.width())
        if width < 640:
            columns = 1
        elif width < 1024:
            columns = 2
        else:
            columns = 3
        if columns != self._columns:
            self._columns = columns
            self._relayout()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self.update_layout(event.size().width())


# ---------------------------------------------------------------------------
# Session detail card and tables
# ---------------------------------------------------------------------------


class SessionDetailCard(QFrame):
    """Displays a detailed summary of the selected cash session."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("SessionDetailCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.title_label = QLabel("تفاصيل الجلسة")
        self.title_label.setObjectName("DetailTitle")

        self.status_badge = QLabel("—")
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_badge.setMinimumWidth(90)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.status_badge)

        self.stack = QStackedLayout()

        self.empty_state = QLabel("اختر جلسة من الجدول لعرض التفاصيل")
        self.empty_state.setObjectName("EmptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.detail_widget = QWidget()
        detail_layout = QGridLayout(self.detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setHorizontalSpacing(18)
        detail_layout.setVerticalSpacing(12)

        self.detail_labels: Dict[str, QLabel] = {}
        fields = [
            ("owner", "اسم المستخدم"),
            ("start", "وقت البدء"),
            ("end", "وقت الإغلاق"),
            ("duration", "المدة"),
            ("cash_open", "الرصيد الافتتاحي"),
            ("cash_close", "الرصيد الختامي"),
            ("income", "إجمالي الدخل"),
            ("expense", "إجمالي المصاريف"),
            ("profit", "الربح الصافي"),
            ("flexi", "الفليكسي المستهلك"),
            ("notes", "ملاحظات"),
        ]

        for row, (key, label_text) in enumerate(fields):
            label = QLabel(label_text)
            label.setObjectName("DetailLabel")
            value_label = QLabel("—")
            value_label.setObjectName("DetailValue")
            value_label.setWordWrap(True)
            detail_layout.addWidget(label, row, 0)
            detail_layout.addWidget(value_label, row, 1)
            self.detail_labels[key] = value_label

        self.stack.addWidget(self.empty_state)
        self.stack.addWidget(self.detail_widget)
        self.stack.setCurrentWidget(self.empty_state)

        layout.addLayout(header_layout)
        layout.addLayout(self.stack)
    def clear(self) -> None:
        self.stack.setCurrentWidget(self.empty_state)
        self.status_badge.setText("—")
        self.status_badge.setProperty("status", "")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

    def update_session(self, session: Optional[Dict]) -> None:
        if not session:
            self.clear()
            return

        self.title_label.setText(f"جلسة #{session['id']}")
        self.status_badge.setText("مفتوحة" if session["status"] == "open" else "مغلقة")
        self.status_badge.setProperty("status", session["status"])
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

        self.detail_labels["owner"].setText(session.get("owner", "—"))
        self.detail_labels["start"].setText(session["start_display"])
        self.detail_labels["end"].setText(session["end_display"])
        self.detail_labels["duration"].setText(session["duration"])
        self.detail_labels["cash_open"].setText(format_currency(session["start_balance"]))
        close_balance = format_currency(session["end_balance"]) if session["end_balance"] is not None else "—"
        self.detail_labels["cash_close"].setText(close_balance)
        self.detail_labels["income"].setText(format_currency(session["income"]))
        self.detail_labels["expense"].setText(format_currency(session["expense"]))
        self.detail_labels["profit"].setText(format_currency(session["profit"]))
        self.detail_labels["flexi"].setText(format_currency(session["flexi_consumed"]))
        notes = session.get("notes") or "—"
        self.detail_labels["notes"].setText(notes)

        self.stack.setCurrentWidget(self.detail_widget)


class SessionTable(QTableWidget):
    """Table specialised for listing sessions with professional styling."""

    HEADERS = [
        "التاريخ",
        "الحالة",
        "الدخل",
        "المصاريف",
        "الربح",
    ]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(0, len(self.HEADERS), parent)
        self._sessions: List[Dict] = []
        self.setObjectName("SessionTable")
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, len(self.HEADERS)):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)

    def set_sessions(self, sessions: Sequence[Dict]) -> None:
        self._sessions = list(sessions)
        self.setRowCount(len(self._sessions))
        for row, session in enumerate(self._sessions):
            self._set_item(row, 0, session["start_display"])
            status_text = "مفتوحة" if session["status"] == "open" else "مغلقة"
            self._set_item(row, 1, status_text)
            self._set_item(row, 2, format_currency(session["income"]), align_right=True)
            self._set_item(row, 3, format_currency(session["expense"]), align_right=True)
            self._set_item(row, 4, format_currency(session["profit"]), align_right=True)

    def _set_item(self, row: int, column: int, text: str, *, align_right: bool = False) -> None:
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        alignment = Qt.AlignmentFlag.AlignVCenter | (Qt.AlignmentFlag.AlignRight if align_right else Qt.AlignmentFlag.AlignLeft)
        item.setTextAlignment(int(alignment))
        self.setItem(row, column, item)

    def session_at(self, row: int) -> Optional[Dict]:
        if 0 <= row < len(self._sessions):
            return self._sessions[row]
        return None


class RecordTable(QTableWidget):
    """Generic table used for expenses, flexi transactions, and user listings."""

    def __init__(
        self,
        headers: Iterable[str],
        *,
        numeric_columns: Optional[Sequence[int]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        headers = list(headers)
        super().__init__(0, len(headers), parent)
        self.setObjectName("RecordTable")
        self._numeric_columns = set(numeric_columns or [])
        self.setHorizontalHeaderLabels(headers)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        for column in range(len(headers)):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)

    def set_records(self, rows: Sequence[Sequence[str]]) -> None:
        self.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                align = Qt.AlignmentFlag.AlignVCenter
                if column in self._numeric_columns:
                    align |= Qt.AlignmentFlag.AlignRight
                else:
                    align |= Qt.AlignmentFlag.AlignLeft
                item.setTextAlignment(int(align))
                self.setItem(row_index, column, item)


class ChartPlaceholder(QFrame):
    """Displayed when the QtCharts module is not available or data is missing."""

    def __init__(self, message: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("ChartPlaceholder")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)
        self.message_label = label

    def set_message(self, message: str) -> None:
        self.message_label.setText(message)


# ---------------------------------------------------------------------------
# Modern dashboard window shell
# ---------------------------------------------------------------------------


class ModernDashboardWindow(QMainWindow):
    """Base window that provides the sidebar, header, and stacked pages."""

    def __init__(
        self,
        *,
        window_title: str,
        brand_title: str,
        brand_tagline: str,
        user,
    ) -> None:
        super().__init__()
        self.user = user
        self.setWindowTitle(window_title)
        self.setMinimumSize(1180, 720)
        self.resize(1400, 840)

        self._pages: Dict[str, Dict[str, object]] = {}

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(32, 32, 32, 32)
        root_layout.setSpacing(24)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(24, 28, 24, 28)
        sidebar_layout.setSpacing(20)

        brand_container = QVBoxLayout()
        brand_container.setContentsMargins(0, 0, 0, 0)
        brand_container.setSpacing(6)
        self.brand_title_label = QLabel(brand_title)
        self.brand_title_label.setObjectName("BrandTitle")
        self.brand_tagline_label = QLabel(brand_tagline)
        self.brand_tagline_label.setObjectName("BrandTagline")
        self.brand_tagline_label.setWordWrap(True)
        brand_container.addWidget(self.brand_title_label)
        brand_container.addWidget(self.brand_tagline_label)
        sidebar_layout.addLayout(brand_container)

        self.nav_layout = QVBoxLayout()
        self.nav_layout.setContentsMargins(0, 8, 0, 0)
        self.nav_layout.setSpacing(8)
        sidebar_layout.addLayout(self.nav_layout)
        sidebar_layout.addStretch(1)

        self.sidebar_footer = QLabel("واجهة النسخة الخرافية 2024")
        self.sidebar_footer.setObjectName("SidebarFooter")
        self.sidebar_footer.setWordWrap(True)
        sidebar_layout.addWidget(self.sidebar_footer)

        root_layout.addWidget(self.sidebar, 0)

        # Main surface
        self.surface = QFrame()
        self.surface.setObjectName("DashboardSurface")
        create_shadow(self.surface, blur=42, y_offset=26, alpha=90)
        surface_layout = QVBoxLayout(self.surface)
        surface_layout.setContentsMargins(32, 32, 32, 32)
        surface_layout.setSpacing(24)

        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        header_text_layout = QVBoxLayout()
        header_text_layout.setContentsMargins(0, 0, 0, 0)
        header_text_layout.setSpacing(6)
        self.header_title = QLabel(window_title)
        self.header_title.setObjectName("HeaderTitle")
        self.header_subtitle = QLabel("—")
        self.header_subtitle.setObjectName("HeaderSubtitle")
        self.header_subtitle.setWordWrap(True)
        header_text_layout.addWidget(self.header_title)
        header_text_layout.addWidget(self.header_subtitle)

        header_layout.addLayout(header_text_layout)
        header_layout.addStretch(1)

        self.header_actions_layout = QHBoxLayout()
        self.header_actions_layout.setContentsMargins(0, 0, 0, 0)
        self.header_actions_layout.setSpacing(12)

        self.refresh_button = QPushButton("تحديث البيانات")
        self.refresh_button.setProperty("variant", "primary")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_actions_layout.addWidget(self.refresh_button)
        header_layout.addLayout(self.header_actions_layout)

        surface_layout.addWidget(header_frame)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(20)
        surface_layout.addLayout(self.body_layout)

        self.stack = QStackedWidget()
        self.body_layout.addWidget(self.stack)

        root_layout.addWidget(self.surface, 1)

        self.refresh_button.clicked.connect(self._handle_refresh_click)

        apply_dashboard_styles(self)

    # -- Sidebar helpers -------------------------------------------------

    def add_nav_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SidebarSectionLabel")
        self.nav_layout.addWidget(label)
        return label

    def add_page(self, key: str, *, title: str, subtitle: str, widget: QWidget, nav_label: Optional[str] = None) -> None:
        button = NavigationButton(nav_label or title)
        button.clicked.connect(lambda checked, k=key: self.show_page(k))
        self.nav_layout.addWidget(button)
        self.stack.addWidget(widget)
        self._pages[key] = {
            "widget": widget,
            "title": title,
            "subtitle": subtitle,
            "button": button,
        }
        if self.stack.count() == 1:
            self.show_page(key)

    def show_page(self, key: str) -> None:
        page = self._pages.get(key)
        if not page:
            return
        widget = page["widget"]
        self.stack.setCurrentWidget(widget)  # type: ignore[arg-type]
        self.header_title.setText(page["title"])
        self.header_subtitle.setText(page["subtitle"])
        for identifier, info in self._pages.items():
            button: NavigationButton = info["button"]  # type: ignore[assignment]
            button.setChecked(identifier == key)

    def set_sidebar_footer(self, text: str) -> None:
        self.sidebar_footer.setText(text)

    def add_header_button(self, button: QPushButton, *, before_refresh: bool = False) -> None:
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        if before_refresh:
            index = self.header_actions_layout.indexOf(self.refresh_button)
            if index == -1:
                self.header_actions_layout.addWidget(button)
            else:
                self.header_actions_layout.insertWidget(index, button)
        else:
            self.header_actions_layout.insertWidget(0, button)

    # -- Refresh ---------------------------------------------------------

    def _handle_refresh_click(self) -> None:
        try:
            self.refresh_dashboard()
        except NotImplementedError:
            pass

    def refresh_dashboard(self) -> None:  # pragma: no cover - meant to be overridden
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


DASHBOARD_STYLE = """
QMainWindow {
    background-color: #030712;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Cairo', 'Tajawal', sans-serif;
}
QFrame#Sidebar {
    background-color: #020617;
    border-radius: 26px;
}
#BrandTitle {
    font-size: 17pt;
    font-weight: 800;
    color: #f8fafc;
}
#BrandTagline {
    color: #94a3b8;
    font-size: 10.5pt;
}
#SidebarSectionLabel {
    color: #64748b;
    font-size: 10pt;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 18px;
    margin-bottom: 4px;
}
#SidebarFooter {
    color: #475569;
    font-size: 9.5pt;
}
QFrame#DashboardSurface {
    background-color: #0b1120;
    border-radius: 28px;
}
#HeaderTitle {
    font-size: 22pt;
    font-weight: 700;
    color: #e2e8f0;
}
#HeaderSubtitle {
    color: #94a3b8;
    font-size: 11pt;
}
QPushButton[variant="primary"] {
    background-color: #2563eb;
    color: white;
    border-radius: 14px;
    padding: 12px 24px;
    font-weight: 600;
    border: none;
}
QPushButton[variant="primary"]:hover {
    background-color: #1d4ed8;
}
QPushButton[variant="primary"]:pressed {
    background-color: #1e3a8a;
}
QPushButton[variant="secondary"] {
    background-color: rgba(59, 130, 246, 0.18);
    color: #bfdbfe;
    border-radius: 14px;
    padding: 10px 22px;
    font-weight: 600;
    border: none;
}
QPushButton[variant="secondary"]:hover {
    background-color: rgba(96, 165, 250, 0.24);
}
QPushButton[variant="secondary"]:pressed {
    background-color: rgba(37, 99, 235, 0.35);
}
QPushButton[isNav="true"] {
    background-color: transparent;
    border: none;
    border-radius: 14px;
    padding: 12px 18px;
    text-align: left;
    font-size: 11pt;
    color: #cbd5f5;
}
QPushButton[isNav="true"]:hover {
    background-color: rgba(148, 163, 184, 0.12);
}
QPushButton[isNav="true"]:checked {
    background-color: rgba(37, 99, 235, 0.22);
    color: #ffffff;
}
#SummaryCard {
    background-color: #111827;
    border-radius: 24px;
}
#SummaryCard QLabel {
    color: #cbd5f5;
}
#SummaryCard QLabel#CardTitle {
    font-size: 11pt;
    font-weight: 600;
    color: #94a3b8;
}
#SummaryCard QLabel#CardValue {
    font-size: 22pt;
    font-weight: 700;
    color: #f8fafc;
}
#SummaryCard[accentRole="positive"] QLabel#CardValue {
    color: #34d399;
}
#SummaryCard[accentRole="negative"] QLabel#CardValue {
    color: #f87171;
}
#SummaryCard[accentRole="info"] QLabel#CardValue {
    color: #60a5fa;
}
#SummaryCard QLabel#CardCaption {
    font-size: 10pt;
    color: #94a3b8;
}
#SessionDetailCard {
    background-color: #111827;
    border-radius: 24px;
}
#SessionDetailCard #DetailTitle {
    font-size: 13pt;
    font-weight: 700;
    color: #f8fafc;
}
#SessionDetailCard #DetailLabel {
    color: #94a3b8;
    font-size: 10.5pt;
}
#SessionDetailCard #DetailValue {
    color: #e2e8f0;
    font-size: 11pt;
}
#SessionDetailCard #EmptyState {
    color: #64748b;
    font-size: 11pt;
}
#StatusBadge {
    border-radius: 12px;
    padding: 6px 14px;
    font-weight: 600;
    background-color: rgba(148, 163, 184, 0.18);
    color: #e2e8f0;
}
#StatusBadge[status="open"] {
    background-color: rgba(34, 197, 94, 0.18);
    color: #4ade80;
}
#StatusBadge[status="closed"] {
    background-color: rgba(239, 68, 68, 0.18);
    color: #f87171;
}
QTableWidget {
    background-color: #0f172a;
    alternate-background-color: #111c2f;
    border: 1px solid #1e293b;
    border-radius: 22px;
    gridline-color: #1e293b;
    selection-background-color: rgba(37, 99, 235, 0.35);
    selection-color: #f8fafc;
    color: #e2e8f0;
}
QTableWidget::item {
    padding: 12px 8px;
}
QHeaderView::section {
    background-color: #111c2f;
    color: #94a3b8;
    border: none;
    padding: 12px 10px;
    font-weight: 600;
}
QTableCornerButton::section {
    background-color: #111c2f;
    border: none;
}
#ChartPlaceholder {
    background-color: rgba(15, 23, 42, 0.7);
    border-radius: 24px;
    border: 1px dashed rgba(148, 163, 184, 0.24);
}
#ChartPlaceholder QLabel {
    color: #94a3b8;
    font-size: 11pt;
}
"""


def apply_dashboard_styles(widget: QWidget) -> None:
    widget.setStyleSheet(DASHBOARD_STYLE)
