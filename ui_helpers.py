"""Reusable UI helpers for the modern Cash Register dashboards."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

from PyQt6.QtCore import QItemSelectionModel, Qt
from PyQt6.QtGui import QColor, QDoubleValidator
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QBoxLayout,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QListView,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedLayout,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
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
        detail_layout.setColumnStretch(0, 0)
        detail_layout.setColumnStretch(1, 1)

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

        detail_layout.setRowStretch(len(fields) - 1, 1)

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


class SessionCardWidget(QFrame):
    """Card used in the responsive session history list."""

    def __init__(self, session: Dict, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("SessionCard")
        self.setProperty("selected", False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        self.date_label = QLabel("—")
        self.date_label.setObjectName("SessionDate")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.status_chip = QLabel("—")
        self.status_chip.setObjectName("StatusChip")
        self.status_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_chip.setMinimumWidth(86)

        header_layout.addWidget(self.date_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.status_chip)

        layout.addLayout(header_layout)

        self.recent_label = QLabel("—")
        self.recent_label.setObjectName("RecentLabel")
        self.recent_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.recent_label)

        metrics_layout = QGridLayout()
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setHorizontalSpacing(18)
        metrics_layout.setVerticalSpacing(4)

        self.metric_labels: Dict[str, QLabel] = {}
        metrics = [
            ("income", "الدخل"),
            ("expense", "المصاريف"),
            ("profit", "الربح"),
        ]
        for column, (key, caption) in enumerate(metrics):
            value_label = QLabel("—")
            value_label.setObjectName("MetricValue")
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            caption_label = QLabel(caption)
            caption_label.setObjectName("MetricLabel")
            caption_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            metrics_layout.addWidget(value_label, 0, column)
            metrics_layout.addWidget(caption_label, 1, column)
            metrics_layout.setColumnStretch(column, 1)
            self.metric_labels[key] = value_label

        layout.addLayout(metrics_layout)

        self.notes_preview = QLabel("—")
        self.notes_preview.setObjectName("NotesPreview")
        self.notes_preview.setWordWrap(True)
        self.notes_preview.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.notes_preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.notes_preview)

        create_shadow(self, blur=32, y_offset=16, alpha=60)

        self.update_session(session)

    def update_session(self, session: Dict) -> None:
        self.date_label.setText(session.get("start_display", "—"))
        status = session.get("status", "closed")
        status_text = "مفتوحة" if status == "open" else "مغلقة"
        self.status_chip.setText(status_text)
        self.status_chip.setProperty("status", status)
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)
        self.setProperty("status", status)
        self.style().unpolish(self)
        self.style().polish(self)

        recent_display = session.get("recent_display") or session.get("end_display") or "—"
        self.recent_label.setText(f"آخر تحديث: {recent_display}")

        self.metric_labels["income"].setText(format_currency(session.get("income", 0.0)))
        self.metric_labels["expense"].setText(format_currency(session.get("expense", 0.0)))
        self.metric_labels["profit"].setText(format_currency(session.get("profit", 0.0)))

        notes = session.get("notes") or "لا توجد ملاحظات"
        self.notes_preview.setText(notes)
        self.notes_preview.setToolTip(notes)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)


class SessionHistoryList(QListWidget):
    """Responsive list that renders sessions as modern cards."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._sessions: List[Dict] = []
        self.setObjectName("SessionHistoryList")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSpacing(12)
        self.setUniformItemSizes(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def set_sessions(self, sessions: Sequence[Dict]) -> None:
        self._sessions = list(sessions)
        self.blockSignals(True)
        self.clear()
        for session in self._sessions:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, session.get("id"))
            card = SessionCardWidget(session)
            item.setSizeHint(card.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, card)
        self.blockSignals(False)
        self._refresh_selection_styles()

    def session_at(self, row: int) -> Optional[Dict]:
        if 0 <= row < len(self._sessions):
            return self._sessions[row]
        return None

    def clear_sessions(self) -> None:
        self._sessions = []
        self.clear()

    def selectRow(self, row: int) -> None:
        self.setCurrentRow(row)

    def setCurrentRow(
        self,
        row: int,
        mode: QItemSelectionModel.SelectionFlag = QItemSelectionModel.SelectionFlag.ClearAndSelect,
    ) -> None:
        super().setCurrentRow(row, mode)
        self._refresh_selection_styles()

    def selectionChanged(self, selected, deselected) -> None:  # type: ignore[override]
        super().selectionChanged(selected, deselected)
        self._refresh_selection_styles()

    def _refresh_selection_styles(self) -> None:
        for index in range(self.count()):
            item = self.item(index)
            widget = self.itemWidget(item)
            if isinstance(widget, SessionCardWidget):
                widget.set_selected(item.isSelected())


class ResponsiveSplitter(QSplitter):
    """Splitter that flips orientation when width is below a breakpoint."""

    def __init__(self, parent: Optional[QWidget] = None, *, breakpoint: int = 1160) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._breakpoint = breakpoint
        self.setChildrenCollapsible(False)
        self.setHandleWidth(14)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._apply_orientation(event.size().width())

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self._apply_orientation(self.width())

    def _apply_orientation(self, width: int) -> None:
        if width <= 0:
            return
        orientation = Qt.Orientation.Vertical if width < self._breakpoint else Qt.Orientation.Horizontal
        if orientation != self.orientation():
            self.setOrientation(orientation)


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
        self.setWordWrap(True)
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
        self.resizeRowsToContents()


class NotesPanel(QFrame):
    """Container that hosts the editable notes area for sessions."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("NotesPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        self.title_label = QLabel("ملاحظات الجلسة")
        self.title_label.setObjectName("NotesTitle")

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("دوّن ملاحظاتك هنا لتتبع التفاصيل الهامة...")
        self.text_edit.setObjectName("NotesEditor")
        self.text_edit.setMinimumHeight(120)

        self.save_button = QPushButton("حفظ الملاحظات")
        self.save_button.setProperty("variant", "secondary")

        layout.addWidget(self.title_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

    def text(self) -> str:
        return self.text_edit.toPlainText().strip()

    def set_text(self, text: str) -> None:
        self.text_edit.setPlainText(text or "")

    def set_editable(self, editable: bool) -> None:
        self.text_edit.setReadOnly(not editable)
        self.save_button.setEnabled(editable)


class TransactionTable(QTableWidget):
    """Specialised table for listing expenses with modern spacing."""

    HEADERS = ["#", "الوصف", "المبلغ", "الوقت"]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(0, len(self.HEADERS), parent)
        self._transactions: List[object] = []
        self.setObjectName("TransactionTable")
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

    def set_transactions(self, transactions: Sequence[object]) -> None:
        self._transactions = list(transactions)
        self.setRowCount(len(self._transactions))
        for row, transaction in enumerate(self._transactions, start=1):
            index_item = QTableWidgetItem(str(row))
            index_item.setData(Qt.ItemDataRole.UserRole, getattr(transaction, "id", row))
            index_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))

            description = getattr(transaction, "description", "") or "—"
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            desc_item.setTextAlignment(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

            amount_text = format_currency(getattr(transaction, "amount", 0.0))
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))

            timestamp = format_datetime(getattr(transaction, "timestamp", None))
            time_item = QTableWidgetItem(timestamp)
            time_item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))

            self.setItem(row - 1, 0, index_item)
            self.setItem(row - 1, 1, desc_item)
            self.setItem(row - 1, 2, amount_item)
            self.setItem(row - 1, 3, time_item)
        self.resizeRowsToContents()

    def transaction_at(self, row: int):
        if 0 <= row < len(self._transactions):
            return self._transactions[row]
        return None

    def clear_transactions(self) -> None:
        self._transactions = []
        self.setRowCount(0)


class FlexiTable(QTableWidget):
    """Table specialised for flexi transactions with payment status."""

    HEADERS = ["#", "الوصف", "المبلغ", "الحالة", "الوقت"]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(0, len(self.HEADERS), parent)
        self._records: List[object] = []
        self.setObjectName("FlexiTable")
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

    def set_records(self, records: Sequence[object]) -> None:
        self._records = list(records)
        self.setRowCount(len(self._records))
        for row, record in enumerate(self._records, start=1):
            index_item = QTableWidgetItem(str(row))
            index_item.setData(Qt.ItemDataRole.UserRole, getattr(record, "id", row))
            index_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))

            description = getattr(record, "description", "") or "—"
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            desc_item.setTextAlignment(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

            amount_text = format_currency(getattr(record, "amount", 0.0))
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))

            is_paid = bool(getattr(record, "is_paid", False))
            status_text = "مدفوع" if is_paid else "قيد التحصيل"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))

            timestamp = format_datetime(getattr(record, "timestamp", None))
            time_item = QTableWidgetItem(timestamp)
            time_item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))

            self.setItem(row - 1, 0, index_item)
            self.setItem(row - 1, 1, desc_item)
            self.setItem(row - 1, 2, amount_item)
            self.setItem(row - 1, 3, status_item)
            self.setItem(row - 1, 4, time_item)
        self.resizeRowsToContents()

    def record_at(self, row: int):
        if 0 <= row < len(self._records):
            return self._records[row]
        return None

    def clear_records(self) -> None:
        self._records = []
        self.setRowCount(0)


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
# Dialog helpers
# ---------------------------------------------------------------------------


class _BaseFinanceDialog(QDialog):
    """Shared styling and validation helpers for dashboard dialogs."""

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self._data: Optional[Dict[str, object]] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        layout.addLayout(self.content_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def data(self) -> Optional[Dict[str, object]]:
        return self._data

    # Sub-classes override to run validation and populate self._data
    def _collect(self) -> Optional[Dict[str, object]]:
        raise NotImplementedError

    def accept(self) -> None:  # type: ignore[override]
        payload = self._collect()
        if payload is None:
            QMessageBox.warning(self, "بيانات غير صالحة", "الرجاء التحقق من القيم المدخلة.")
            return
        self._data = payload
        super().accept()


class OpenSessionDialog(_BaseFinanceDialog):
    """Collects the opening balances for a new cash session."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("بدء جلسة جديدة", parent)
        form = QFormLayout()
        form.setSpacing(12)
        self.cash_input = QLineEdit()
        self.cash_input.setPlaceholderText("رصيد البداية النقدي")
        self.cash_input.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        self.flexi_input = QLineEdit()
        self.flexi_input.setPlaceholderText("رصيد الفليكسي")
        self.flexi_input.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        form.addRow("الرصيد النقدي:", self.cash_input)
        form.addRow("رصيد الفليكسي:", self.flexi_input)
        self.content_layout.addLayout(form)

    def _collect(self) -> Optional[Dict[str, object]]:
        try:
            start_balance = float(self.cash_input.text().strip() or 0.0)
            start_flexi = float(self.flexi_input.text().strip() or 0.0)
        except ValueError:
            return None
        if start_balance < 0 or start_flexi < 0:
            return None
        return {"start_balance": start_balance, "start_flexi": start_flexi}


class CloseSessionDialog(_BaseFinanceDialog):
    """Collects closing balances while presenting a quick summary."""

    def __init__(self, summary: Dict[str, float], parent: Optional[QWidget] = None) -> None:
        super().__init__("إغلاق الجلسة", parent)
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(6)

        summary_label = QLabel(
            "<b>ملخص سريع:</b>\n"
            f"• الرصيد الافتتاحي: {format_currency(summary.get('start_balance', 0.0))}\n"
            f"• المصاريف المسجلة: {format_currency(summary.get('total_expense', 0.0))}\n"
            f"• الفليكسي المضاف: {format_currency(summary.get('flexi_added', 0.0))}"
        )
        summary_label.setWordWrap(True)
        summary_layout.addWidget(summary_label)
        self.content_layout.addWidget(summary_frame)

        form = QFormLayout()
        form.setSpacing(12)
        self.end_cash_input = QLineEdit()
        self.end_cash_input.setPlaceholderText("الرصيد النقدي عند الإغلاق")
        self.end_cash_input.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        self.end_flexi_input = QLineEdit()
        self.end_flexi_input.setPlaceholderText("رصيد الفليكسي المتبقي")
        self.end_flexi_input.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        form.addRow("الرصيد النقدي الختامي:", self.end_cash_input)
        form.addRow("رصيد الفليكسي الختامي:", self.end_flexi_input)
        self.content_layout.addLayout(form)

    def _collect(self) -> Optional[Dict[str, object]]:
        try:
            end_balance = float(self.end_cash_input.text().strip())
            end_flexi_text = self.end_flexi_input.text().strip()
            end_flexi = float(end_flexi_text) if end_flexi_text else 0.0
        except ValueError:
            return None
        if end_balance < 0 or end_flexi < 0:
            return None
        return {"end_balance": end_balance, "end_flexi": end_flexi}


class ExpenseDialog(_BaseFinanceDialog):
    """Dialog used to add or edit an expense transaction."""

    def __init__(self, parent: Optional[QWidget] = None, *, description: str = "", amount: float = 0.0) -> None:
        super().__init__("تسجيل مصروف", parent)
        form = QFormLayout()
        form.setSpacing(12)
        self.amount_input = QLineEdit(f"{amount:.2f}" if amount else "")
        self.amount_input.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        self.amount_input.setPlaceholderText("0.00")
        self.desc_input = QLineEdit(description)
        self.desc_input.setPlaceholderText("وصف المصروف")
        form.addRow("المبلغ:", self.amount_input)
        form.addRow("الوصف:", self.desc_input)
        self.content_layout.addLayout(form)

    def _collect(self) -> Optional[Dict[str, object]]:
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            return None
        description = self.desc_input.text().strip()
        if amount <= 0:
            return None
        return {"amount": amount, "description": description}


class FlexiDialog(_BaseFinanceDialog):
    """Dialog used to add or edit flexi top-ups."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        description: str = "",
        amount: float = 0.0,
        is_paid: bool = False,
    ) -> None:
        super().__init__("تسجيل فليكسي", parent)
        form = QFormLayout()
        form.setSpacing(12)
        self.amount_input = QLineEdit(f"{amount:.2f}" if amount else "")
        self.amount_input.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        self.amount_input.setPlaceholderText("0.00")
        self.desc_input = QLineEdit(description)
        self.desc_input.setPlaceholderText("وصف العملية")
        self.paid_checkbox = QCheckBox("تم تحصيل المبلغ نقداً")
        self.paid_checkbox.setChecked(is_paid)
        form.addRow("المبلغ:", self.amount_input)
        form.addRow("الوصف:", self.desc_input)
        form.addRow("", self.paid_checkbox)
        self.content_layout.addLayout(form)

    def _collect(self) -> Optional[Dict[str, object]]:
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            return None
        if amount <= 0:
            return None
        description = self.desc_input.text().strip()
        return {
            "amount": amount,
            "description": description,
            "is_paid": self.paid_checkbox.isChecked(),
        }


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
        self._root_layout = root_layout

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(24, 28, 24, 28)
        sidebar_layout.setSpacing(20)
        self._sidebar_layout = sidebar_layout

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
        self.surface.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        surface_layout = QVBoxLayout(self.surface)
        surface_layout.setContentsMargins(32, 32, 32, 32)
        surface_layout.setSpacing(24)
        self._surface_layout = surface_layout

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
        self._apply_shell_mode(self.width())

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

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._apply_shell_mode(event.size().width())

    def _apply_shell_mode(self, width: int) -> None:
        if width <= 0:
            width = self.width()
        if width < 1250:
            self._root_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self._root_layout.setSpacing(20)
            self.sidebar.setMaximumHeight(320)
            self.sidebar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.surface.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.sidebar_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self._root_layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self._root_layout.setSpacing(24)
            self.sidebar.setMaximumHeight(16777215)
            self.sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.surface.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.sidebar_footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

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
#SectionSubtitle {
    color: #cbd5f5;
    font-size: 11.5pt;
    font-weight: 600;
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
#TransactionsFrame, #FlexiFrame {
    background-color: #111827;
    border-radius: 24px;
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
#NotesPanel {
    background-color: #111827;
    border-radius: 24px;
}
#NotesPanel #NotesTitle {
    font-size: 12pt;
    font-weight: 600;
    color: #f8fafc;
}
#NotesEditor {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 16px;
    color: #e2e8f0;
    font-size: 10.5pt;
    padding: 12px;
}
#NotesEditor:disabled {
    color: #64748b;
}
#SessionHistoryList {
    background-color: transparent;
    border: none;
}
#SessionHistoryList::item {
    margin: 0 0 12px 0;
}
#SessionHistoryList::item:selected,
#SessionHistoryList::item:hover {
    background: transparent;
}
#SessionCard {
    background-color: #111827;
    border-radius: 22px;
    border: 1px solid transparent;
}
#SessionCard[selected="true"] {
    border: 1px solid rgba(59, 130, 246, 0.45);
    background-color: #0b152b;
}
#SessionCard[status="open"] {
    border: 1px solid rgba(34, 197, 94, 0.28);
}
#SessionCard[status="closed"] {
    border: 1px solid rgba(148, 163, 184, 0.14);
}
#SessionCard[status="open"][selected="true"],
#SessionCard[status="closed"][selected="true"] {
    border: 1px solid rgba(59, 130, 246, 0.45);
}
#SessionCard QLabel {
    color: #cbd5f5;
}
#SessionCard QLabel#SessionDate {
    font-size: 11.5pt;
    font-weight: 600;
    color: #f8fafc;
}
#SessionCard QLabel#RecentLabel {
    font-size: 9.8pt;
    color: #64748b;
}
#SessionCard QLabel#MetricLabel {
    font-size: 9.6pt;
    color: #94a3b8;
}
#SessionCard QLabel#MetricValue {
    font-size: 12.2pt;
    font-weight: 700;
    color: #f8fafc;
}
#SessionCard QLabel#NotesPreview {
    font-size: 10pt;
    color: #94a3b8;
}
#StatusChip {
    border-radius: 14px;
    padding: 6px 16px;
    font-weight: 600;
    background-color: rgba(148, 163, 184, 0.18);
    color: #e2e8f0;
}
#StatusChip[status="open"] {
    background-color: rgba(34, 197, 94, 0.18);
    color: #4ade80;
}
#StatusChip[status="closed"] {
    background-color: rgba(239, 68, 68, 0.18);
    color: #f87171;
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
QScrollArea#SessionDetailScroll {
    background: transparent;
    border: none;
}
QScrollArea#SessionDetailScroll > QWidget > QWidget {
    background: transparent;
}
QSplitter#SessionsSplitter::handle {
    background-color: transparent;
    margin: 0 6px;
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
