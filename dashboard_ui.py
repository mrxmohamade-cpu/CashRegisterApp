import sys
import datetime
from datetime import timezone
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QLineEdit, QDialogButtonBox, QListWidget,
                             QListWidgetItem, QTextEdit, QSplitter, QHeaderView,
                             QStyle, QFrame, QSizePolicy, QMenu, QFormLayout, QCheckBox,
                             QGridLayout, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QColor, QDoubleValidator, QMouseEvent, QFont, QAction
from PyQt6.QtCore import Qt, QSize, QPoint, QEvent

from ui_helpers import FlowLayout


# Safe stub for AddTransactionDialog to satisfy linters (replace with real dialog in project)
if "AddTransactionDialog" not in globals():
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QDoubleSpinBox, QHBoxLayout
    from PyQt6.QtGui import QFont

    class AddTransactionDialog(QDialog):
        """Modern, larger Add / Edit expense dialog used when a real implementation
        isn't available. Returns `self.transaction_data = {amount, description}` when
        accepted.
        """
        def __init__(self, parent=None, transaction=None):
            super().__init__(parent)
            self.setWindowTitle("إضافة / تعديل مصروف")
            self.transaction_data = None

            self.setModal(True)
            self.setFixedWidth(480)

            title_font = QFont()
            title_font.setPointSize(12)
            title_font.setBold(True)

            label_font = QFont()
            label_font.setPointSize(11)

            self.main_layout = QVBoxLayout()
            self.main_layout.setSpacing(12)
            
            # -- تعديل --: إضافة تخطيط لتعبئة المساحة
            content_frame = QFrame()
            content_frame.setObjectName("CustomDialogFrame")
            content_layout = QVBoxLayout(content_frame)
            
            # -- تعديل --: إضافة شريط العنوان
            self.title_bar = QWidget()
            self.title_bar.setObjectName("CustomTitleBar")
            self.title_bar.setFixedHeight(40)
            title_bar_layout = QHBoxLayout(self.title_bar)
            title_bar_layout.setContentsMargins(15, 0, 5, 0)
            title_label = QLabel("إضافة / تعديل مصروف")
            title_label.setObjectName("CustomTitleLabel")
            close_button = QPushButton("✕")
            close_button.setObjectName("CustomCloseButton")
            close_button.setFixedSize(30, 30)
            close_button.clicked.connect(self.reject)
            title_bar_layout.addWidget(title_label)
            title_bar_layout.addStretch()
            title_bar_layout.addWidget(close_button)
            
            self.content_widget = QWidget()
            self.content_layout = QVBoxLayout(self.content_widget)
            self.content_layout.setContentsMargins(20, 15, 20, 20)
            self.content_layout.setSpacing(10)
            
            content_layout.addWidget(self.title_bar)
            content_layout.addWidget(self.content_widget)
            self.main_layout.addWidget(content_frame)

            self.setLayout(self.main_layout)

            # -- تعديل: استبدال QDoubleSpinBox بـ QLineEdit مع مدقق (validator)
            amount_label = QLabel("المبلغ:")
            amount_label.setFont(label_font)
            self.amount_input = QLineEdit()
            self.amount_input.setValidator(QDoubleValidator(0.00, 9999999999.99, 2))
            self.amount_input.setPlaceholderText("0.00")
            self.amount_input.setFixedHeight(36)
            self.amount_input.setStyleSheet("font-size:12pt; padding:4px;")
            self.content_layout.addWidget(amount_label)
            self.content_layout.addWidget(self.amount_input)
            
            desc_label = QLabel("الملاحظة:")
            desc_label.setFont(label_font)
            self.desc_input = QLineEdit()
            self.desc_input.setPlaceholderText("وصف المصروف، مثلاً: أدوات مكتبية")
            self.desc_input.setFixedHeight(36)
            self.desc_input.setStyleSheet("font-size:11.5pt; padding:6px;")
            self.content_layout.addWidget(desc_label)
            self.content_layout.addWidget(self.desc_input)

            btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            btns.accepted.connect(self.accept)
            btns.rejected.connect(self.reject)
            self.content_layout.addWidget(btns)

            # pre-fill when editing
            if transaction is not None:
                try:
                    if getattr(transaction, 'amount', None) is not None:
                        # -- تعديل: استخدام setText بدلاً من setValue
                        self.amount_input.setText(f"{transaction.amount:.2f}")
                    self.desc_input.setText(transaction.description or "")
                except Exception:
                    pass

        def accept(self):
            amt = None
            try:
                # -- تعديل: الحصول على النص من QLineEdit
                amt = float(self.amount_input.text().strip())
            except Exception:
                amt = None
            self.transaction_data = {"amount": amt, "description": self.desc_input.text().strip()}
            super().accept()

# استيراد معالجة الاستثناءات من SQLAlchemy (إن كانت موجودة في المشروع)
try:
    from sqlalchemy.exc import IntegrityError
except Exception:
    class IntegrityError(Exception):
        pass

# حاول استيراد نماذج قاعدة البيانات الحقيقية، وإن لم تتوفر استعمل بيانات وهمية للاختبار
try:
    from database_setup import User, CashSession, Transaction, SessionLocal, FlexiTransaction
    # If using SQLAlchemy, we may want to eager-load relationships
    try:
        from sqlalchemy.orm import joinedload
    except Exception:
        joinedload = None
except Exception:
    from dataclasses import dataclass, field
    @dataclass
    class Transaction:
        id: int
        session_id: int
        type: str
        amount: float
        description: str
        timestamp: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    @dataclass
    class FlexiTransaction:
        id: int
        session_id: int
        amount: float
        description: str
        timestamp: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
        user_id: int = 1
    
    @dataclass
    class User:
        id: int = 1
        username: str = "testuser"
        role: str = "user"
        password_hash: str = ""
        def set_password(self, p): self.password_hash = p
        
    @dataclass
    class CashSession:
        id: int
        user_id: int
        start_time: datetime.datetime
        start_balance: float = 0.0
        start_flexi: float = 0.0
        total_expense: float = 0.0
        total_flexi_additions: float = 0.0
        status: str = "closed"
        end_time: datetime.datetime | None = None
        end_balance: float | None = None
        end_flexi: float | None = None
        notes: str | None = ""
        transactions: list = field(default_factory=list)
        flexi_transactions: list = field(default_factory=list)

        @property
        def net_profit(self):
            # If an actual end balance exists, net profit is end_balance - start_balance
            if self.end_balance is not None:
                return self.end_balance - self.start_balance
            # otherwise derive from transactions / totals
            return self.start_balance - self.total_expense
        
        # -- إضافة --: خصائص جديدة لحساب الفروقات بشكل منفصل
        @property
        def net_cash_difference(self):
            if self.end_balance is None:
                return 0.0
            # -- تعديل --: تم إضافة خصم الفليكسي المستهلك
            theoretical_cash_balance = (self.start_balance - self.total_expense)
            return self.end_balance - theoretical_cash_balance
            
        @property
        def flexi_consumed(self):
            if self.end_flexi is None:
                return 0.0
            theoretical_flexi_balance = (self.start_flexi or 0.0) + (self.total_flexi_additions or 0.0)
            return theoretical_flexi_balance - self.end_flexi


        @property
        def gross_income(self):
            return self.start_balance - self.total_expense

    class SessionLocal:
        def __init__(self):
            self._sessions = []
            now = datetime.datetime.now(datetime.timezone.utc)
            for i in range(4):
                st = now - datetime.timedelta(hours=i*3)
                s = CashSession(id=i+1, user_id=1, start_time=st, start_balance=1600.0,
                                start_flexi=1000.0,
                                total_expense=1100.0 if i==0 else (200.0*(i)), status='closed' if i!=1 else 'open')
                if i==0:
                    s.total_expense = 123456789.99
                    s.transactions = [Transaction(id=1, session_id=s.id, type='expense', amount=123456789.99, description="فاتورة ضخمة جداً لعرض المشكلة", timestamp=st)]
                    s.flexi_transactions = [FlexiTransaction(id=1, session_id=s.id, amount=500.0, description="إضافة يومية", timestamp=st)]
                self._sessions.append(s)
        def query(self, model):
            class Q:
                def __init__(self, sessions): self.sessions = sessions
                def filter_by(self, **kwargs):
                    user_id = kwargs.get('user_id', None)
                    status = kwargs.get('status', None)
                    res = self.sessions
                    if user_id is not None:
                        res = [x for x in res if x.user_id == user_id]
                    if status is not None:
                        res = [x for x in res if x.status == status]
                    class R:
                        def __init__(self, items): self.items = items
                        def order_by(self, *args): return self
                        def all(self): return self.items
                        def first(self): return self.items[0] if self.items else None
                        def one(self): return self.items[0] if self.items else None
                        def get(self, id):
                            for it in self.items:
                                if it.id == id: return it
                            return None
                    return R(res)
            return Q(self._sessions)
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass
        def rollback(self): pass
        def close(self): pass

# --- Custom Dialog Base Class ---
class CustomDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(parent.styleSheet() if parent else "")

        self.old_pos = None

        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("CustomDialogFrame")
        self.bg_frame.setFrameShape(QFrame.Shape.NoFrame)

        frame_layout = QVBoxLayout(self.bg_frame)
        frame_layout.setContentsMargins(1, 1, 1, 1)
        frame_layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(15, 0, 5, 0)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("CustomTitleLabel")
        
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("CustomCloseButton")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.reject)

        title_bar_layout.addWidget(self.title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(self.close_button)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 15, 20, 20)
        self.content_layout.setSpacing(10)

        frame_layout.addWidget(self.title_bar)
        frame_layout.addWidget(self.content_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.bg_frame)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.underMouse():
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None

# --- Custom Message Box ---
class CustomMessageBox(CustomDialog):
    def __init__(self, parent, title, text, icon_pixmap):
        super().__init__(title, parent)
        self.setMinimumWidth(400)
        
        # Use the existing content_layout from the parent class
        self.content_layout.setSpacing(20)

        content_h_layout = QHBoxLayout()
        content_h_layout.setSpacing(15)
        
        icon_label = QLabel()
        icon_label.setPixmap(icon_pixmap.pixmap(48, 48))
        
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        content_h_layout.addWidget(icon_label)
        content_h_layout.addWidget(text_label, 1)

        self.buttons = QDialogButtonBox()
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.content_layout.addLayout(content_h_layout)
        self.content_layout.addWidget(self.buttons, 0, Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def show_message(parent, title, text, icon, buttons):
        style = parent.style()
        icon_pixmap = getattr(style, "standardIcon")(icon)
        msg_box = CustomMessageBox(parent, title, text, icon_pixmap)
        msg_box.buttons.setStandardButtons(buttons)
        return msg_box.exec()

    @staticmethod
    def show_warning(parent, title, text):
        return CustomMessageBox.show_message(parent, title, text, QStyle.StandardPixmap.SP_MessageBoxWarning, QDialogButtonBox.StandardButton.Ok)

    @staticmethod
    def show_information(parent, title, text):
        return CustomMessageBox.show_message(parent, title, text, QStyle.StandardPixmap.SP_MessageBoxInformation, QDialogButtonBox.StandardButton.Ok)
        
    @staticmethod
    def show_critical(parent, title, text):
        return CustomMessageBox.show_message(parent, title, text, QStyle.StandardPixmap.SP_MessageBoxCritical, QDialogButtonBox.StandardButton.Ok)

    @staticmethod
    def show_question(parent, title, text):
        reply = CustomMessageBox.show_message(parent, title, text, QStyle.StandardPixmap.SP_MessageBoxQuestion, QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        return reply == QDialog.DialogCode.Accepted


# --- Summary card ---
class SummaryCard(QFrame):
    def __init__(self, title, icon: QStyle.StandardPixmap, accent: str = "primary"):
        super().__init__()
        self.setObjectName("SummaryCard")
        self.setProperty("accentColor", accent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(200)
        self.setMinimumHeight(140)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("SummaryCardIcon")
        self.icon_label.setFixedSize(QSize(44, 44))
        pixmap = self.style().standardIcon(icon).pixmap(QSize(26, 26))
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("SummaryCardTitle")
        self.title_label.setWordWrap(True)

        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label, 1)

        self.value_label = QLabel("0.00")
        self.value_label.setObjectName("SummaryCardValue")
        self.value_label.setWordWrap(True)

        self.caption_label = QLabel("")
        self.caption_label.setObjectName("SummaryCardCaption")
        self.caption_label.setWordWrap(True)
        self.caption_label.setVisible(False)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.value_label)
        main_layout.addWidget(self.caption_label)
        main_layout.addStretch(1)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 14)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(15, 23, 42, 40))
        self.setGraphicsEffect(shadow)

    def set_value(self, value_text):
        self.value_label.setText(value_text)

    def set_caption(self, caption_text: str):
        self.caption_label.setText(caption_text)
        self.caption_label.setVisible(bool(caption_text))

# --- SessionHistoryItem (FIXED) ---


class SessionHistoryItem(QWidget):
    def __init__(self, session: CashSession):
        super().__init__()
        self.setObjectName("HistoryItem")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self.session = session

        # Make the widget expand horizontally inside the list
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Tooltip for notes
        self.setToolTip(session.notes or "")

        # Root layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # Card container (gives border + rounded corners)
        self.card = QFrame()
        self.card.setObjectName("HistoryCard")
        self.card.setFrameShape(QFrame.Shape.NoFrame)
        self.card_layout = QHBoxLayout(self.card)
        self.card_layout.setContentsMargins(8, 8, 8, 8)
        self.card_layout.setSpacing(12)

        self.card_shadow = QGraphicsDropShadowEffect(self.card)
        self.card_shadow.setOffset(0, 10)
        self.card_shadow.setBlurRadius(20)
        self.card_shadow.setColor(QColor(15, 23, 42, 60))
        self.card.setGraphicsEffect(self.card_shadow)

        # Left: date/time column
        date_time_layout = QVBoxLayout()
        date_time_layout.setSpacing(2)
        self.date_label = QLabel(session.start_time.strftime('%d/%m/%Y') if session.start_time else "غير متوفر")
        self.date_label.setObjectName("HistoryItemDate")
        self.date_label.setStyleSheet("font-weight:600;")
        self.time_label = QLabel(session.start_time.strftime('%H:%M') if session.start_time else "")
        self.time_label.setObjectName("HistoryItemTime")
        self.time_label.setStyleSheet("color: rgba(0,0,0,0.55); font-size:12px;")
        date_time_layout.addWidget(self.date_label)
        date_time_layout.addWidget(self.time_label)
        self.card_layout.addLayout(date_time_layout)

        # Middle: notes (stretch)
        middle_layout = QVBoxLayout()
        middle_layout.setSpacing(4)
        middle_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        note_text = (session.notes or "").strip()
        if not note_text:
            note_text = "لا توجد ملاحظات لهذه الجلسة"

        self.note_label = QLabel(note_text)
        self.note_label.setObjectName("HistoryItemNote")
        self.note_label.setStyleSheet("color: #343a40; font-size:14px; font-weight: 500;")
        self.note_label.setWordWrap(True)
        self.note_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.note_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.note_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        middle_layout.addWidget(self.note_label)
        middle_layout.addStretch(1)

        self.card_layout.addLayout(middle_layout, stretch=1)


        # Right: profit and status badges
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        # Profit value
        # -- تعديل --: عرض صافي الفرق النقدي فقط في قائمة السجل
        try:
            # -- تعديل --: استخدام الخاصية net_cash_difference
            profit_value = float(getattr(session, 'net_cash_difference', 0.0))
        except Exception:
            profit_value = 0.0
        self.profit_label = QLabel(f"{profit_value:+.2f}")
        self.profit_label.setObjectName("HistoryItemProfit")
        self.profit_label.setStyleSheet("font-weight:700; font-size:13px;")
        if profit_value >= 0:
            self.profit_label.setStyleSheet(self.profit_label.styleSheet() + "color: #198754;")
        else:
            self.profit_label.setStyleSheet(self.profit_label.styleSheet() + "color: #dc3545;")

        # status badge (open/closed)
        status_text = "مفتوحة" if session.status == 'open' else "مغلقة"
        self.status_badge = QLabel(status_text)
        self.status_badge.setObjectName("StatusBadge")
        # style depending on status
        if session.status == 'open':
            self.status_badge.setStyleSheet("padding:6px 10px; border-radius:12px; background-color: rgba(25,135,84,0.12); color:#198754; font-weight:600;")
        else:
            self.status_badge.setStyleSheet("padding:6px 10px; border-radius:12px; background-color: rgba(220,53,69,0.08); color:#dc3545; font-weight:600;")

        right_layout.addWidget(self.profit_label, alignment=Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(self.status_badge, alignment=Qt.AlignmentFlag.AlignRight)

        # -- إضافة --: عرض الربح الصافي الكلي
        if session.status == 'closed':
            try:
                # حساب الربح الصافي الكلي
                total_net_profit = (session.end_balance - session.start_balance - session.total_expense) + (session.total_flexi_additions - session.flexi_consumed)
                total_profit_label = QLabel(f"<b>الربح الصافي:</b> {total_net_profit:,.2f}")
                total_profit_label.setStyleSheet("font-size: 10px; color: #495057;")
                right_layout.addWidget(total_profit_label, alignment=Qt.AlignmentFlag.AlignRight)
            except Exception:
                pass
        
        self.card_layout.addLayout(right_layout)

        main_layout.addWidget(self.card)

        # enable hover tracking for nicer effect
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # default unselected style
        self.set_selected_state(False)

    def sizeHint(self):
        card_hint = self.card.sizeHint()
        note_hint = self.note_label.sizeHint()
        height = max(card_hint.height(), note_hint.height() + 32)
        return QSize(card_hint.width() + 16, height + 16)

    def _update_shadow(self, blur_radius: float, alpha: int):
        self.card_shadow.setBlurRadius(blur_radius)
        self.card_shadow.setColor(QColor(15, 23, 42, max(0, min(alpha, 255))))

    def set_selected_state(self, selected: bool):
        """Apply selected/unselected visual style to the card frame."""
        if selected:
            self.card.setStyleSheet("""
                QFrame#HistoryCard {
                    border: 2px solid rgba(37, 99, 235, 0.35);
                    border-radius: 18px;
                    background-color: rgba(37, 99, 235, 0.12);
                }
            """)
            self._update_shadow(26, 110)
        else:
            self.card.setStyleSheet("""
                QFrame#HistoryCard {
                    border: 1px solid rgba(148, 163, 184, 0.22);
                    border-radius: 18px;
                    background-color: rgba(255,255,255,0.96);
                }
            """)
            self._update_shadow(18, 80)

    def enterEvent(self, event):
        # subtle hover highlight
        hover_style = """
            QFrame#HistoryCard {
                border: 1px solid rgba(37, 99, 235, 0.3);
                border-radius: 18px;
                background-color: rgba(37, 99, 235, 0.1);
            }
        """
        self.card.setStyleSheet(hover_style)
        self._update_shadow(22, 100)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # restore based on selection state
        # find if parent list has this as current
        parent = self.parent()
        is_selected = False
        while parent is not None and not isinstance(parent, QListWidget):
            parent = parent.parent()
        if isinstance(parent, QListWidget):
            for i in range(parent.count()):
                it = parent.item(i)
                if parent.itemWidget(it) is self and parent.currentItem() is it:
                    is_selected = True
                    break
        self.set_selected_state(is_selected)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # when clicked, select the matching QListWidgetItem
        parent = self.parent()
        while parent is not None and not isinstance(parent, QListWidget):
            parent = parent.parent()
        if isinstance(parent, QListWidget):
            for i in range(parent.count()):
                it = parent.item(i)
                if parent.itemWidget(it) is self:
                    parent.setCurrentItem(it)
                    break

class AddFlexiDialog(CustomDialog):
    def __init__(self, parent=None):
        super().__init__("إضافة فليكسي", parent)
        self.setMinimumWidth(480)
        self.flexi_data = None
        
        layout = self.content_layout
        
        label = QLabel("الرجاء إدخال المبلغ المضاف للفليكسي:")
        self.amount_input = QLineEdit()
        self.amount_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        self.amount_input.setPlaceholderText("0.00")
        
        desc_label = QLabel("ملاحظة (اختياري):")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("مثلاً: شحن فليكسي من حساب خاص")
        
        # -- تعديل --: تغيير الحالة الافتراضية إلى غير محددة
        self.is_paid_checkbox = QCheckBox("تم الدفع نقدًا من الصندوق")
        self.is_paid_checkbox.setChecked(False)
        
        layout.addWidget(label)
        layout.addWidget(self.amount_input)
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_input)
        layout.addWidget(self.is_paid_checkbox)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
    def accept(self):
        amount = self.amount_input.text()
        if not amount:
            CustomMessageBox.show_warning(self, "خطأ", "الرجاء إدخال مبلغ صحيح.")
            return
        
        try:
            self.flexi_data = {
                "amount": float(amount),
                "description": self.desc_input.text().strip(),
                "is_paid": self.is_paid_checkbox.isChecked() # -- تعديل --: إضافة حالة الدفع
            }
            super().accept()
        except ValueError:
            CustomMessageBox.show_warning(self, "خطأ", "الرجاء إدخال قيمة رقمية صحيحة.")

class OpenCashDialog(CustomDialog):
    def __init__(self, parent=None):
        super().__init__("فتح صندوق جديد", parent)
        self.setMinimumWidth(400)

        layout = self.content_layout
        
        label_cash = QLabel("الرجاء إدخال رصيد بداية الصندوق:")
        self.balance_input = QLineEdit()
        self.balance_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        self.balance_input.setPlaceholderText("0.00")
        
        label_flexi = QLabel("الرجاء إدخال رصيد الفليكسي الحالي:")
        self.flexi_input = QLineEdit()
        self.flexi_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        self.flexi_input.setPlaceholderText("0.00")
        
        layout.addWidget(label_cash)
        layout.addWidget(self.balance_input)
        layout.addWidget(label_flexi)
        layout.addWidget(self.flexi_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
    def get_data(self):
        try:
            balance = float(self.balance_input.text()) if self.balance_input.text() else 0.0
            flexi_balance = float(self.flexi_input.text()) if self.flexi_input.text() else 0.0
            return {"start_balance": balance, "start_flexi": flexi_balance}
        except ValueError:
            return None

class CloseCashDialog(CustomDialog):
    def __init__(self, session_summary, parent=None):
        super().__init__("إغلاق الصندوق", parent)
        self.setMinimumWidth(440)

        layout = self.content_layout
        summary_label = QLabel("<b>ملخص الجلسة الحالية:</b>")
        layout.addWidget(summary_label)
        
        summary_frame = QFrame()
        summary_frame.setObjectName("SummaryFrame")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.addWidget(QLabel(f"رصيد النقد البداية: {session_summary['start_balance']:.2f}"))
        summary_layout.addWidget(QLabel(f"مجموع المصاريف: {session_summary['total_expense']:.2f}"))
        summary_layout.addWidget(QLabel(f"رصيد الفليكسي البداية: {session_summary['start_flexi']:.2f}"))
        summary_layout.addWidget(QLabel(f"مجموع إضافات الفليكسي: {session_summary['total_flexi_additions']:.2f}"))
        
        layout.addWidget(summary_frame)
        
        # Grid layout for better alignment
        form_layout = QFormLayout()
        
        end_balance_label = QLabel("<b>الرجاء إدخال رصيد النقد الفعلي:</b>")
        self.end_balance_input = QLineEdit()
        self.end_balance_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        self.end_balance_input.setPlaceholderText("المبلغ الذي تم عَدّه في الصندوق")
        form_layout.addRow(end_balance_label, self.end_balance_input)
        
        end_flexi_label = QLabel("<b>الرجاء إدخال رصيد الفليكسي الفعلي:</b>")
        self.end_flexi_input = QLineEdit()
        self.end_flexi_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        self.end_flexi_input.setPlaceholderText("المبلغ في حساب الفليكسي")
        form_layout.addRow(end_flexi_label, self.end_flexi_input)
        
        layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
    def get_data(self):
        try:
            end_balance = float(self.end_balance_input.text()) if self.end_balance_input.text() else None
            end_flexi = float(self.end_flexi_input.text()) if self.end_flexi_input.text() else None
            return {"end_balance": end_balance, "end_flexi": end_flexi}
        except ValueError:
            return None


class ClosingReportDialog(CustomDialog):
    def __init__(self, session, parent=None):
        super().__init__("تقرير إغلاق الجلسة", parent)
        self.setMinimumWidth(480)
        
        layout = self.content_layout
        layout.setSpacing(12)
        
        title_label = QLabel("تم إغلاق الجلسة بنجاح")
        title_label.setObjectName("ReportTitle")
        
        # Grid layout for better alignment
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Cash section
        cash_title = QLabel("<b>ملخص النقد:</b>")
        cash_title.setStyleSheet("font-size: 12pt; margin-top: 10px;")
        form_layout.addRow(cash_title)
        
        start_balance = f"{session.start_balance:,.2f}"
        total_expense = f"{session.total_expense:,.2f}"
        end_balance = f"{session.end_balance:,.2f}" if session.end_balance is not None else "N/A"
        
        # -- تعديل --: حساب الرصيد النظري النقدي بشكل صحيح
        theoretical_cash_balance = session.start_balance - session.total_expense + session.total_flexi_paid
        theoretical_balance_str = f"{theoretical_cash_balance:,.2f}"
        
        difference = session.net_cash_difference
        difference_str = f"{difference:+,.2f}"
        
        form_layout.addRow(QLabel("<b>رصيد البداية:</b>"), QLabel(start_balance))
        form_layout.addRow(QLabel("<b>مجموع المصاريف:</b>"), QLabel(total_expense))
        form_layout.addRow(QLabel("<b>الرصيد النظري:</b>"), QLabel(theoretical_balance_str))
        
        separator_cash = QFrame()
        separator_cash.setFrameShape(QFrame.Shape.HLine)
        separator_cash.setObjectName("Separator")
        form_layout.addRow(separator_cash)
        
        form_layout.addRow(QLabel("<b>الرصيد الفعلي (النهاية):</b>"), QLabel(end_balance))
        
        diff_label_cash = QLabel(difference_str)
        if difference < 0: diff_label_cash.setObjectName("NegativeValue")
        elif difference > 0: diff_label_cash.setObjectName("PositiveValue")
        form_layout.addRow(QLabel("<b>الفرق (عجز/زيادة):</b>"), diff_label_cash)

        # Flexi section
        flexi_title = QLabel("<b>ملخص الفليكسي:</b>")
        flexi_title.setStyleSheet("font-size: 12pt; margin-top: 15px;")
        form_layout.addRow(flexi_title)
        
        start_flexi = f"{session.start_flexi:,.2f}" if session.start_flexi is not None else "N/A"
        total_flexi_additions = f"{session.total_flexi_additions:,.2f}"
        end_flexi = f"{session.end_flexi:,.2f}" if session.end_flexi is not None else "N/A"
        
        flexi_theoretical_balance = (session.start_flexi or 0.0) + (session.total_flexi_additions or 0.0)
        flexi_theoretical_balance_str = f"{flexi_theoretical_balance:,.2f}"
        
        # -- تعديل --: حساب الفليكسي المستهلك
        flexi_consumed = session.flexi_consumed if session.end_flexi is not None else 0
        flexi_consumed_str = f"{flexi_consumed:,.2f}"
        
        form_layout.addRow(QLabel("<b>رصيد البداية:</b>"), QLabel(start_flexi))
        form_layout.addRow(QLabel("<b>مجموع الإضافات:</b>"), QLabel(total_flexi_additions))
        form_layout.addRow(QLabel("<b>الرصيد النظري:</b>"), QLabel(flexi_theoretical_balance_str))
        
        separator_flexi = QFrame()
        separator_flexi.setFrameShape(QFrame.Shape.HLine)
        separator_flexi.setObjectName("Separator")
        form_layout.addRow(separator_flexi)
        
        form_layout.addRow(QLabel("<b>الرصيد الفعلي (النهاية):</b>"), QLabel(end_flexi))

        diff_label_flexi = QLabel(flexi_consumed_str)
        diff_label_flexi.setObjectName("PositiveValue") # المستهلك يعتبر قيمة إيجابية
        form_layout.addRow(QLabel("<b>الفليكسي المستهلك:</b>"), diff_label_flexi)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)

        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(button_box)


# --- Main window ---
class UserDashboard(QMainWindow):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.db_session = SessionLocal()
        self.current_session = None
        self.all_sessions = []
        self.selected_session_id = None
        self._summary_column_count = None
        self._current_button_min_width = None
        self._current_detail_metrics = None
        self._current_summary_padding = None
        self._current_action_spacing = None
        self.setWindowTitle(f"نظام إدارة الصندوق - {self.user.username}")
        self.setGeometry(80, 80, 1300, 760)
        self.setMinimumSize(1024, 640)
        self.setup_ui()
        self.apply_styles()
        self.load_user_sessions_history()
        self.check_for_open_session()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.main_splitter = splitter

        history_widget = QWidget()
        history_widget.setObjectName("HistoryWidget")
        history_widget.setMinimumWidth(220)
        history_widget.setMaximumWidth(420)
        history_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.history_widget = history_widget
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.setSpacing(0)
        self.history_layout = history_layout

        history_label = QLabel("سجل الجلسات")
        history_label.setObjectName("HistoryTitle")

        self.history_search_input = QLineEdit()
        self.history_search_input.setObjectName("HistorySearch")
        self.history_search_input.setPlaceholderText("ابحث باسم العامل أو تاريخ الجلسة أو الحالة...")
        self.history_search_input.setClearButtonEnabled(True)
        self.history_search_input.textChanged.connect(self.filter_sessions_history)

        self.sessions_history_list = QListWidget()
        self.sessions_history_list.setObjectName("SessionsList")
        self.sessions_history_list.setSpacing(0)
        self.sessions_history_list.setUniformItemSizes(False)
        self.sessions_history_list.currentItemChanged.connect(self.select_session_from_history)

        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_search_input)
        history_layout.addWidget(self.sessions_history_list)
        splitter.addWidget(history_widget)

        details_widget = QWidget()
        details_widget.setObjectName("DetailsWidget")
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(30, 20, 30, 20)
        details_layout.setSpacing(20)
        self.details_layout = details_layout

        top_bar_container = QWidget()
        top_bar_container.setObjectName("TopBar")
        top_bar_layout = QVBoxLayout(top_bar_container)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(10)
        header_row.addStretch()
        welcome_label = QLabel(f"<b>أهلاً بك، {self.user.username}</b>")
        welcome_label.setObjectName("WelcomeLabel")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        welcome_label.setWordWrap(True)
        header_row.addWidget(welcome_label)
        top_bar_layout.addLayout(header_row)

        self.open_cash_btn = QPushButton(" فتح الصندوق")
        self.add_expense_btn = QPushButton(" إضافة مصروف")

        # NEW: Flexi button
        self.add_flexi_btn = QPushButton(" إضافة فليكسي")
        
        self.close_cash_btn = QPushButton(" غلق الصندوق")
        self.open_cash_btn.setObjectName("SuccessButton")
        self.close_cash_btn.setObjectName("DangerButton")
        self.add_expense_btn.setObjectName("PrimaryButton")
        self.add_flexi_btn.setObjectName("SecondaryButton")

        self.open_cash_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
        self.add_expense_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.add_flexi_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.close_cash_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogNoButton))

        actions_flow = FlowLayout(spacing=12, alignment=Qt.AlignmentFlag.AlignRight)
        actions_flow.setContentsMargins(0, 0, 0, 0)
        self.actions_flow = actions_flow
        self.action_buttons = [
            self.open_cash_btn,
            self.add_expense_btn,
            self.add_flexi_btn,
            self.close_cash_btn,
        ]
        for btn in self.action_buttons:
            btn.setIconSize(QSize(16, 16))
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            actions_flow.addWidget(btn)

        top_bar_layout.addLayout(actions_flow)
        details_layout.addWidget(top_bar_container)
        self.top_bar_container = top_bar_container

        self.session_context_label = QLabel("اختر جلسة من السجل لعرض تفاصيلها")
        self.session_context_label.setObjectName("SessionContextLabel")
        self.session_context_label.setWordWrap(True)
        self.session_context_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.session_context_label.setTextFormat(Qt.TextFormat.RichText)
        details_layout.addWidget(self.session_context_label)

        summary_container = QFrame()
        summary_container.setObjectName("SummaryContainer")
        summary_container.installEventFilter(self)
        summary_grid = QGridLayout(summary_container)
        summary_grid.setContentsMargins(20, 20, 20, 20)
        summary_grid.setHorizontalSpacing(22)
        summary_grid.setVerticalSpacing(22)
        summary_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.start_balance_card = SummaryCard("رصيد البداية", QStyle.StandardPixmap.SP_FileDialogStart, accent="emerald")
        self.total_expense_card = SummaryCard("مجموع المصاريف", QStyle.StandardPixmap.SP_ArrowDown, accent="orange")
        self.current_flexi_card = SummaryCard("رصيد الفليكسي", QStyle.StandardPixmap.SP_DirOpenIcon, accent="indigo")
        self.net_profit_card = SummaryCard("الفرق في النقد", QStyle.StandardPixmap.SP_ArrowUp, accent="cyan")
        self.flexi_consumed_card = SummaryCard("الفليكسي المستهلك", QStyle.StandardPixmap.SP_ArrowDown, accent="rose")
        self.total_net_profit_card = SummaryCard("الربح الصافي الكلي", QStyle.StandardPixmap.SP_DialogApplyButton, accent="violet")

        summary_cards = [
            self.start_balance_card,
            self.total_expense_card,
            self.current_flexi_card,
            self.net_profit_card,
            self.flexi_consumed_card,
            self.total_net_profit_card,
        ]

        self.summary_container = summary_container
        self.summary_grid = summary_grid
        self.summary_cards = summary_cards
        self.update_summary_grid_layout(force=True)

        details_layout.addWidget(summary_container)

        bottom_splitter = QSplitter(Qt.Orientation.Vertical)
        bottom_splitter.setChildrenCollapsible(False)

        tables_container = QWidget()
        tables_container.setObjectName("Container")
        tables_shadow = QGraphicsDropShadowEffect(tables_container)
        tables_shadow.setOffset(0, 12)
        tables_shadow.setBlurRadius(24)
        tables_shadow.setColor(QColor(15, 23, 42, 45))
        tables_container.setGraphicsEffect(tables_shadow)
        tables_layout = QVBoxLayout(tables_container)
        
        # Expenses table
        table_label = QLabel("سجل المصاريف")
        table_label.setObjectName("SectionTitle")
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(4)
        self.transactions_table.setHorizontalHeaderLabels(["#", "المبلغ", "الملاحظة", "الوقت"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.transactions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.transactions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.transactions_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transactions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.transactions_table.customContextMenuRequested.connect(self.open_transaction_menu)

        # Flexi transactions table
        flexi_table_label = QLabel("سجل إضافات الفليكسي")
        flexi_table_label.setObjectName("SectionTitle")
        self.flexi_transactions_table = QTableWidget()
        self.flexi_transactions_table.setColumnCount(4)
        self.flexi_transactions_table.setHorizontalHeaderLabels(["#", "المبلغ", "الملاحظة", "الوقت"])
        self.flexi_transactions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.flexi_transactions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.flexi_transactions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.flexi_transactions_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.flexi_transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.flexi_transactions_table.verticalHeader().setVisible(False)
        self.flexi_transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        tables_layout.addWidget(table_label)
        tables_layout.addWidget(self.transactions_table)
        tables_layout.addWidget(flexi_table_label)
        tables_layout.addWidget(self.flexi_transactions_table)

        notes_container = QWidget()
        notes_container.setObjectName("Container")
        notes_shadow = QGraphicsDropShadowEffect(notes_container)
        notes_shadow.setOffset(0, 12)
        notes_shadow.setBlurRadius(24)
        notes_shadow.setColor(QColor(15, 23, 42, 45))
        notes_container.setGraphicsEffect(notes_shadow)
        notes_layout = QVBoxLayout(notes_container)
        notes_label = QLabel("ملاحظات الجلسة")
        notes_label.setObjectName("SectionTitle")

        self.notes_editor = QTextEdit()
        self.notes_editor.setPlaceholderText("أضف ملاحظاتك هنا...")
        self.save_notes_btn = QPushButton("حفظ الملاحظات")
        self.save_notes_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.save_notes_btn.setObjectName("PrimaryButton")
        self.save_notes_btn.setFixedHeight(40)

        button_bar_layout = QHBoxLayout()
        button_bar_layout.addStretch()
        button_bar_layout.addWidget(self.save_notes_btn)

        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_editor)
        notes_layout.addLayout(button_bar_layout)
        
        bottom_splitter.addWidget(tables_container)
        bottom_splitter.addWidget(notes_container)
        bottom_splitter.setSizes([420, 220])

        details_layout.addWidget(bottom_splitter)
        splitter.addWidget(details_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([360, 940])
        self.bottom_splitter = bottom_splitter

        main_layout.addWidget(splitter)

        # Events
        self.open_cash_btn.clicked.connect(self.open_cash_session)
        self.add_expense_btn.clicked.connect(self.add_expense)
        self.add_flexi_btn.clicked.connect(self.add_flexi)
        self.close_cash_btn.clicked.connect(self.close_cash_session)
        self.save_notes_btn.clicked.connect(self.save_session_notes)

        self.update_responsive_layouts()

    def apply_styles(self):
        stylesheet = """
            QMainWindow {
                background-color: #e8ecf7;
                font-family: 'Segoe UI', 'Cairo', sans-serif;
            }
            #HistoryWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #eef2ff);
                border-right: 1px solid rgba(148, 163, 184, 0.25);
            }
            #DetailsWidget { background-color: #eef2ff; }
            #TopBar {
                background: transparent;
            }
            #HistoryTitle {
                font-size: 16pt;
                font-weight: 800;
                color: #0f172a;
                padding: 20px 18px 10px;
                background: transparent;
            }
            #HistorySearch {
                margin: 0 18px 18px;
                padding: 12px 18px;
                border-radius: 16px;
                border: 1px solid rgba(148, 163, 184, 0.35);
                background: rgba(255, 255, 255, 0.85);
                color: #0f172a;
                font-size: 11pt;
            }
            #HistorySearch:focus {
                border: 2px solid #2563eb;
                padding: 11px 17px;
                background: rgba(255, 255, 255, 0.95);
            }
            #HistorySearch::placeholder {
                color: rgba(100, 116, 139, 0.75);
            }
            #WelcomeLabel { font-size: 18pt; font-weight: 800; color: #0f172a; margin-bottom: 10px; }
            #SessionContextLabel {
                background: rgba(255, 255, 255, 0.86);
                border-radius: 20px;
                padding: 16px 22px;
                font-size: 11.5pt;
                color: #1e293b;
                border: 1px solid rgba(148, 163, 184, 0.25);
                margin-bottom: 8px;
            }
            #SessionContextLabel b { color: #0f172a; }
            #SessionContextLabel span { font-weight: 600; }

            /* --- Custom Dialog Styles --- */
            QDialog { background-color: transparent; }
            #CustomDialogFrame {
                background-color: #ffffff;
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 12px;
            }
            #CustomTitleBar { 
                background-color: #f8f9fa;
                border-top-left-radius: 11px;
                border-top-right-radius: 11px;
                border-bottom: 1px solid #e9ecef;
            }
            #CustomTitleLabel { font-size: 11pt; font-weight: bold; color: #212529; }
            #CustomCloseButton {
                background-color: transparent; color: #6c757d;
                border: none; font-size: 14pt; font-weight: bold;
                border-radius: 4px;
            }
            #CustomCloseButton:hover { background-color: #dc3545; color: white; }
            
            QDialog QLabel { font-size: 11pt; color: #495057; }
            QDialog QLabel b { color: #212529; }
            QDialog QLineEdit, QDialog QTextEdit {
                background-color: #ffffff; color: #212529; border: 1px solid #ced4da;
                border-radius: 6px; padding: 10px; font-size: 11pt;
            }
            QDialog QLineEdit:focus, QDialog QTextEdit:focus { border-color: #86b7fe; }

            QListWidget#SessionsList {
                border: none;
                font-size: 13pt;
                padding: 0 16px 16px;
                background: transparent;
            }
            QListWidget#SessionsList::item { border: none; padding: 6px 0; }
            QListWidget#SessionsList::item:selected { background-color: transparent; color: black; border: none; }

            QWidget#HistoryItem { background-color: transparent; }
            #HistoryItemDate { font-size: 11.5pt; font-weight: 700; color: #1e293b; }
            #HistoryItemTime { font-size: 9pt; color: #64748b; }
            #HistoryItemNote { color: #334155; font-size: 13px; }
            #HistoryItemProfit { font-size: 12pt; font-weight: 800; }

            QPushButton {
                border: none;
                padding: 12px 22px;
                font-size: 10.5pt;
                font-weight: 700;
                border-radius: 14px;
                background: #cbd5f5;
                color: #1e293b;
            }
            QPushButton:disabled { background-color: rgba(148, 163, 184, 0.4); color: #94a3b8; }
            #PrimaryButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                color: white;
            }
            #PrimaryButton:hover { background: #1e3a8a; }
            #SuccessButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #22c55e, stop:1 #16a34a);
                color: white;
            }
            #SuccessButton:hover { background: #15803d; }
            #DangerButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f97316, stop:1 #dc2626);
                color: white;
            }
            #DangerButton:hover { background: #b91c1c; }
            #SecondaryButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6366f1, stop:1 #4338ca);
                color: white;
            }
            #SecondaryButton:hover { background: #3730a3; }

            QDialogButtonBox QPushButton { background-color: #0d6efd; color: white; }
            QDialogButtonBox QPushButton:hover { background-color: #0b5ed7; }

            #SummaryContainer {
                background: transparent;
                border: none;
            }
            QFrame#SummaryCard {
                background-color: #ffffff;
                border-radius: 24px;
                border: 1px solid rgba(148, 163, 184, 0.25);
            }
            QLabel#SummaryCardIcon {
                background-color: rgba(37, 99, 235, 0.12);
                border-radius: 18px;
                color: #1d4ed8;
            }
            QLabel#SummaryCardTitle { font-size: 12pt; font-weight: 700; color: #64748b; }
            QLabel#SummaryCardValue { font-size: 26pt; font-weight: 800; color: #0f172a; }
            QLabel#SummaryCardCaption { font-size: 10pt; color: #64748b; }

            QFrame#SummaryCard[accentColor="emerald"] QLabel#SummaryCardIcon { background-color: rgba(34, 197, 94, 0.18); color: #047857; }
            QFrame#SummaryCard[accentColor="emerald"] QLabel#SummaryCardValue { color: #047857; }
            QFrame#SummaryCard[accentColor="orange"] QLabel#SummaryCardIcon { background-color: rgba(249, 115, 22, 0.18); color: #c2410c; }
            QFrame#SummaryCard[accentColor="orange"] QLabel#SummaryCardValue { color: #c2410c; }
            QFrame#SummaryCard[accentColor="indigo"] QLabel#SummaryCardIcon { background-color: rgba(99, 102, 241, 0.16); color: #4338ca; }
            QFrame#SummaryCard[accentColor="indigo"] QLabel#SummaryCardValue { color: #3730a3; }
            QFrame#SummaryCard[accentColor="cyan"] QLabel#SummaryCardIcon { background-color: rgba(14, 165, 233, 0.2); color: #0e7490; }
            QFrame#SummaryCard[accentColor="cyan"] QLabel#SummaryCardValue { color: #0e7490; }
            QFrame#SummaryCard[accentColor="rose"] QLabel#SummaryCardIcon { background-color: rgba(244, 114, 182, 0.2); color: #be123c; }
            QFrame#SummaryCard[accentColor="rose"] QLabel#SummaryCardValue { color: #be123c; }
            QFrame#SummaryCard[accentColor="violet"] QLabel#SummaryCardIcon { background-color: rgba(139, 92, 246, 0.18); color: #6d28d9; }
            QFrame#SummaryCard[accentColor="violet"] QLabel#SummaryCardValue { color: #6d28d9; }

            #Container {
                background-color: #ffffff;
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 20px;
                padding: 24px;
            }
            #SectionTitle {
                font-size: 15.5pt;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 18px;
            }
            QTableWidget {
                border: none; font-size: 11pt; background-color: #ffffff;
                gridline-color: #e9ecef; alternate-background-color: #f8f9fa;
                color: #212529;
                selection-background-color: #cfe2ff;
                selection-color: #000;
            }
            QHeaderView::section {
                background-color: #f8f9fa; padding: 14px 10px; border: none;
                border-bottom: 2px solid #dee2e6; font-weight: 700; font-size: 10pt;
                color: #495057;
            }
            QTableWidget::item { 
                padding: 12px 10px; 
                border-bottom: 1px solid #f0f1f3;
            }
             QTableWidget::item:selected {
                background-color: #cfe2ff;
                color: #212529;
            }
            QTextEdit {
                border: 1px solid #ced4da; border-radius: 8px; padding: 12px;
                font-size: 11pt; background-color: #f8f9fa; color: #212529;
            }
            QTextEdit::placeholder { color: #6c757d; }
            QTextEdit:focus { 
                border: 1px solid #86b7fe; 
                background-color: #ffffff;
            }
            QSplitter::handle { background: #dee2e6; }
            QSplitter::handle:vertical { height: 1px; }
            QSplitter::handle:horizontal { width: 1px; }

            /* Report Dialog Specifics */
            #ReportTitle { font-size: 14pt; font-weight: bold; color: #198754; }
            #NegativeValue { color: #dc3545; font-weight: bold; }
            #PositiveValue { color: #198754; font-weight: bold; }
            #Separator { background-color: #e9ecef; height: 1px; border: none; }
        """
        self.setStyleSheet(stylesheet)
        self.transactions_table.setAlternatingRowColors(True)
        self.flexi_transactions_table.setAlternatingRowColors(True)

    def load_user_sessions_history(self):
        # Fix #6: Sessions Ordering - This was already correct.
        # Try to eager-load transactions if SQLAlchemy is available; fallback to simple query for mock session
        try:
            if joinedload:
                sessions = (
                    self.db_session.query(CashSession)
                    .options(joinedload(CashSession.transactions))
                    .filter_by(user_id=self.user.id)
                    .order_by(CashSession.start_time.desc())
                    .all()
                )
            else:
                sessions = (
                    self.db_session.query(CashSession)
                    .filter_by(user_id=self.user.id)
                    .order_by(CashSession.start_time.desc())
                    .all()
                )
        except Exception:
            sessions = (
                self.db_session.query(CashSession)
                .filter_by(user_id=self.user.id)
                .order_by(CashSession.start_time.desc())
                .all()
            )

        self.all_sessions = sessions
        preferred_id = self.selected_session_id or (self.current_session.id if self.current_session else None)
        self.populate_sessions_list(sessions, preferred_id=preferred_id)

    def populate_sessions_list(self, sessions, preferred_id=None):
        self.sessions_history_list.blockSignals(True)
        self.sessions_history_list.clear()

        for session in sessions:
            list_item = QListWidgetItem(self.sessions_history_list)
            list_item.setData(Qt.ItemDataRole.UserRole, session.id)
            item_widget = SessionHistoryItem(session)
            item_widget.adjustSize()
            list_item.setSizeHint(item_widget.sizeHint())
            self.sessions_history_list.setItemWidget(list_item, item_widget)

        self.sessions_history_list.blockSignals(False)

        if not sessions:
            self.selected_session_id = None
            self.display_session_details(None)
            return

        target_id = preferred_id if preferred_id and any(s.id == preferred_id for s in sessions) else sessions[0].id
        for index in range(self.sessions_history_list.count()):
            item = self.sessions_history_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == target_id:
                self.sessions_history_list.setCurrentRow(index)
                break

    def filter_sessions_history(self, text: str):
        if not self.all_sessions:
            return

        query = (text or "").strip().lower()
        if not query:
            filtered = self.all_sessions
        else:
            filtered = []
            for session in self.all_sessions:
                note = (session.notes or "").lower()
                status = (session.status or "").lower()
                session_id_str = str(session.id)
                start_time_str = session.start_time.strftime('%d/%m/%Y %H:%M') if session.start_time else ""
                user_name = getattr(session.user, 'username', '')
                user_name_lower = user_name.lower() if user_name else ""

                if any(
                    query in field
                    for field in [note, status, session_id_str, start_time_str.lower(), user_name_lower]
                ):
                    filtered.append(session)

        preferred_id = self.selected_session_id or (self.current_session.id if self.current_session else None)
        self.populate_sessions_list(filtered, preferred_id=preferred_id)

    def update_responsive_layouts(self):
        if not getattr(self, "details_layout", None):
            return

        width = max(self.width(), 1)

        if width < 900:
            detail_margins = (18, 16, 18, 16)
            detail_spacing = 16
            summary_padding = 14
            summary_spacing = 14
            action_spacing = 6
            button_width = 132
            history_widths = (200, 320)
        elif width < 1300:
            detail_margins = (26, 20, 26, 20)
            detail_spacing = 18
            summary_padding = 20
            summary_spacing = 18
            action_spacing = 10
            button_width = 146
            history_widths = (220, 360)
        elif width < 1650:
            detail_margins = (34, 22, 34, 22)
            detail_spacing = 20
            summary_padding = 24
            summary_spacing = 22
            action_spacing = 12
            button_width = 156
            history_widths = (230, 400)
        else:
            detail_margins = (40, 24, 40, 24)
            detail_spacing = 22
            summary_padding = 28
            summary_spacing = 26
            action_spacing = 14
            button_width = 168
            history_widths = (250, 440)

        if self._current_detail_metrics != (detail_margins, detail_spacing):
            self.details_layout.setContentsMargins(*detail_margins)
            self.details_layout.setSpacing(detail_spacing)
            self._current_detail_metrics = (detail_margins, detail_spacing)

        if self._current_summary_padding != (summary_padding, summary_spacing):
            self.summary_grid.setContentsMargins(summary_padding, summary_padding, summary_padding, summary_padding)
            self.summary_grid.setHorizontalSpacing(summary_spacing)
            self.summary_grid.setVerticalSpacing(summary_spacing)
            self._current_summary_padding = (summary_padding, summary_spacing)

        if self._current_action_spacing != action_spacing:
            self.actions_flow.setSpacing(action_spacing)
            self._current_action_spacing = action_spacing

        if self._current_button_min_width != button_width:
            for btn in self.action_buttons:
                btn.setMinimumWidth(button_width)
            self._current_button_min_width = button_width

        min_width, max_width = history_widths
        self.history_widget.setMinimumWidth(min_width)
        self.history_widget.setMaximumWidth(max_width)

    def update_summary_grid_layout(self, force=False):
        if not hasattr(self, "summary_grid") or not self.summary_grid:
            return
        if not getattr(self, "summary_cards", None):
            return

        container_width = self.summary_container.width() or self.width()
        if container_width < 560:
            columns = 1
        elif container_width < 920:
            columns = 2
        elif container_width < 1320:
            columns = 3
        else:
            columns = 4

        if not force and self._summary_column_count == columns:
            return

        self._summary_column_count = columns

        while self.summary_grid.count():
            item = self.summary_grid.takeAt(0)
            widget = item.widget()
            if widget and widget not in self.summary_cards:
                widget.setParent(None)

        for index, card in enumerate(self.summary_cards):
            row = index // columns
            column = index % columns
            self.summary_grid.addWidget(card, row, column)

        for column in range(6):
            self.summary_grid.setColumnStretch(column, 1 if column < columns else 0)

    def update_summary_display(self, session):
        if session:
            # Recalculate total_expense from transactions (only expense type)
            transactions = getattr(session, 'transactions', None)
            if not transactions:
                try:
                    transactions = self.db_session.query(Transaction).filter_by(session_id=session.id).all()
                except Exception:
                    transactions = []

            expense_transactions = [t for t in transactions if getattr(t, 'type', 'expense') == 'expense']
            total_expense = sum(getattr(t, 'amount', 0.0) for t in expense_transactions)
            operations_count = len(expense_transactions)

            self.start_balance_card.set_value(f"<b>{session.start_balance:,.2f}</b>")
            opened_at = session.start_time.strftime('%d/%m/%Y %H:%M') if session.start_time else ""
            self.start_balance_card.set_caption(f"تم فتح الجلسة: {opened_at}" if opened_at else "جارٍ المتابعة")

            self.total_expense_card.set_value(f"<b>{total_expense:,.2f}</b>")
            self.total_expense_card.set_caption(f"{operations_count} عملية مصروف مسجلة")

            # Flexi summary
            flexi_additions = getattr(session, 'flexi_transactions', [])
            if not flexi_additions:
                try:
                    flexi_additions = self.db_session.query(FlexiTransaction).filter_by(session_id=session.id).all()
                except Exception:
                    flexi_additions = []

            total_flexi_additions = sum(t.amount for t in flexi_additions)
            flexi_operations = len(flexi_additions)

            # Use end_flexi if closed, otherwise calculate from start + additions
            if session.status == 'closed' and session.end_flexi is not None:
                current_flexi = session.end_flexi
            else:
                current_flexi = (session.start_flexi or 0.0) + total_flexi_additions

            self.current_flexi_card.set_value(f"<b>{current_flexi:,.2f}</b>")
            self.current_flexi_card.set_caption(f"{flexi_operations} حركة فليكسي")

            # -- تعديل --: حساب الفرق النقدي بشكل منفصل
            # هنا يتم حساب الربح الصافي بعد خصم الفليكسي المستهلك
            if session.end_balance is not None and session.end_flexi is not None:
                cash_difference = session.net_cash_difference
            else:
                cash_difference = (session.start_balance or 0.0) - total_expense
            self.net_profit_card.set_value(f"<b>{cash_difference:+.2f}</b>")
            self.net_profit_card.set_caption("الجلسة مغلقة" if session.status == 'closed' else "قيد العمل")

            # -- تعديل --: حساب الفليكسي المستهلك
            flexi_consumed = session.flexi_consumed if session.end_flexi is not None else 0
            self.flexi_consumed_card.set_value(f"<b>{flexi_consumed:,.2f}</b>")
            self.flexi_consumed_card.set_caption(
                "يظهر بالكامل بعد الإغلاق" if session.end_flexi is None else "إجمالي الفليكسي المستهلك"
            )

            # -- إضافة --: حساب الربح الصافي الكلي
            # (الرصيد الفعلي - رصيد البداية - المصاريف) + (إضافات الفليكسي - الفليكسي المستهلك)
            recorded_flexi_additions = getattr(session, 'total_flexi_additions', total_flexi_additions)
            if session.end_balance is not None:
                total_net_profit = (
                    (session.end_balance - (session.start_balance or 0.0) - total_expense)
                    + (recorded_flexi_additions - flexi_consumed)
                )
            else:
                total_net_profit = (
                    (session.start_balance or 0.0) - total_expense
                    + (recorded_flexi_additions - flexi_consumed)
                )

            self.total_net_profit_card.set_value(f"<b>{total_net_profit:,.2f}</b>")
            closed_at = session.end_time.strftime('%d/%m/%Y %H:%M') if getattr(session, 'end_time', None) else ""
            self.total_net_profit_card.set_caption(
                f"أغلقت في {closed_at}" if closed_at else "يتم التحديث مع إقفال الجلسة"
            )

        else:
            self.start_balance_card.set_value("<b>--</b>")
            self.start_balance_card.set_caption("")
            self.total_expense_card.set_value("<b>--</b>")
            self.total_expense_card.set_caption("")
            self.current_flexi_card.set_value("<b>--</b>")
            self.current_flexi_card.set_caption("")
            self.net_profit_card.set_value("<b>--</b>")
            self.net_profit_card.set_caption("")
            self.flexi_consumed_card.set_value("<b>--</b>")
            self.flexi_consumed_card.set_caption("")
            self.total_net_profit_card.set_value("<b>--</b>")
            self.total_net_profit_card.set_caption("")

    def select_session_from_history(self, current_item, previous_item):
        # Fix #3: Selection Indicator - This logic was already correct.
        if previous_item:
            prev_widget = self.sessions_history_list.itemWidget(previous_item)
            if isinstance(prev_widget, SessionHistoryItem):
                prev_widget.set_selected_state(False)
        if current_item:
            current_widget = self.sessions_history_list.itemWidget(current_item)
            if isinstance(current_widget, SessionHistoryItem):
                current_widget.set_selected_state(True)
            session_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.selected_session_id = session_id
            # Try to eager-load transactions if SQLAlchemy is available; fallback to simple query for mock session
            try:
                if joinedload:
                    selected_session = self.db_session.query(CashSession).options(joinedload(CashSession.transactions), joinedload(CashSession.flexi_transactions)).filter_by(id=session_id).one()
                else:
                    selected_session = self.db_session.query(CashSession).filter_by(id=session_id).one()
            except Exception:
                selected_session = self.db_session.query(CashSession).filter_by(id=session_id).one()
            self.display_session_details(selected_session)
        else:
            self.selected_session_id = None
            self.display_session_details(None)

    def check_for_open_session(self):
        open_session = self.db_session.query(CashSession).filter_by(user_id=self.user.id, status='open').first()
        if open_session:
            self.current_session = open_session
            self.selected_session_id = open_session.id
            for i in range(self.sessions_history_list.count()):
                item = self.sessions_history_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == open_session.id:
                    self.sessions_history_list.setCurrentRow(i)
                    break
        else:
            self.current_session = None
        self.update_ui_for_session_status()

    def display_session_details(self, session):
        if session is None:
            self.load_transactions(None)
            self.load_flexi_transactions(None)
            self.update_summary_display(None)
            self.notes_editor.clear()
            self.notes_editor.setReadOnly(True)
            self.save_notes_btn.setEnabled(False)
            if hasattr(self, "session_context_label"):
                self.session_context_label.setText("اختر جلسة من السجل لعرض تفاصيلها.")
            return

        self.load_transactions(session)
        self.load_flexi_transactions(session)
        self.update_summary_display(session)
        self.notes_editor.setText(session.notes or "")

        status_text = "مفتوحة" if session.status == 'open' else "مغلقة"
        start_text = session.start_time.strftime('%d/%m/%Y %H:%M') if session.start_time else "غير محدد"
        end_text = session.end_time.strftime('%d/%m/%Y %H:%M') if getattr(session, 'end_time', None) else ""
        owner_name = getattr(session.user, 'username', None) or self.user.username

        context_lines = [
            f"<b>جلسة رقم {session.id}</b> — الحالة: {status_text}",
            f"بدأت في {start_text}" + (f" • أغلقت في {end_text}" if end_text else ""),
            f"المسؤول: {owner_name}",
        ]

        if self.current_session and self.current_session.status == 'open' and session.id != self.current_session.id:
            context_lines.append(
                f"<span style='color:#dc2626;'>ملاحظة: الأوامر (إضافة مصروف/فليكسي) ستطبق على الجلسة المفتوحة رقم {self.current_session.id}.</span>"
            )

        if hasattr(self, "session_context_label"):
            self.session_context_label.setText("<br/>".join(context_lines))

        is_current_open = (
            self.current_session
            and session.id == self.current_session.id
            and self.current_session.status == 'open'
        )
        self.notes_editor.setReadOnly(not is_current_open)
        self.save_notes_btn.setEnabled(is_current_open)

    def open_cash_session(self):
        dialog = OpenCashDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data is None:
                CustomMessageBox.show_warning(self, "خطأ", "الرجاء إدخال قيم صحيحة.")
                return
            new_session = CashSession(user_id=self.user.id, start_balance=data["start_balance"], start_flexi=data["start_flexi"], start_time=datetime.datetime.now(datetime.timezone.utc))
            try:
                self.db_session.add(new_session)
                self.db_session.commit()
            except IntegrityError as e:
                self.db_session.rollback()
                CustomMessageBox.show_critical(self, "خطأ في فتح الصندوق", "حدث خطأ عند إنشاء الجلسة. الرجاء إعادة المحاولة.")
                print("IntegrityError عند فتح جلسة:", e)
                return

            self.db_session.refresh(new_session)
            self.current_session = new_session
            self.load_user_sessions_history()
            self.check_for_open_session()

    def add_expense(self):
        if not self.current_session or self.current_session.status != 'open':
            CustomMessageBox.show_warning(self, "تنبيه", "يجب فتح جلسة أولاً لإضافة مصروف.")
            return
        dialog = AddTransactionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.transaction_data
            new_transaction = Transaction(session_id=self.current_session.id, type='expense', amount=data['amount'], description=data['description'], timestamp=datetime.datetime.now(datetime.timezone.utc))
            try:
                self.db_session.add(new_transaction)
                self.db_session.commit()
            except IntegrityError as e:
                self.db_session.rollback()
                CustomMessageBox.show_critical(self, "خطأ", "حدث خطأ عند إضافة المصروف. حاول مرة أخرى.")
                print("IntegrityError عند إضافة مصروف:", e)
                return

            self.db_session.refresh(self.current_session)
            self.load_transactions(self.current_session)
            self.update_summary_display(self.current_session)
            
    def add_flexi(self):
        if not self.current_session or self.current_session.status != 'open':
            CustomMessageBox.show_warning(self, "تنبيه", "يجب فتح جلسة أولاً لإضافة فليكسي.")
            return
        dialog = AddFlexiDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.flexi_data
            if data:
                # -- تعديل --: إضافة خاصية is_paid
                new_flexi_transaction = FlexiTransaction(session_id=self.current_session.id, amount=data['amount'], description=data['description'], user_id=self.user.id, timestamp=datetime.datetime.now(datetime.timezone.utc), is_paid=data['is_paid'])
                try:
                    self.db_session.add(new_flexi_transaction)
                    self.db_session.commit()
                except IntegrityError as e:
                    self.db_session.rollback()
                    CustomMessageBox.show_critical(self, "خطأ", "حدث خطأ عند إضافة الفليكسي. حاول مرة أخرى.")
                    print("IntegrityError عند إضافة فليكسي:", e)
                    return
                
                self.db_session.refresh(self.current_session)
            self.load_flexi_transactions(self.current_session)
            self.update_summary_display(self.current_session)

    def open_transaction_menu(self, position):
        if not self.current_session or self.current_session.status == 'closed':
            return
        
        menu = QMenu()
        edit_action = menu.addAction("تعديل")
        delete_action = menu.addAction("حذف")
        
        # Determine the row that was right-clicked to avoid relying on selection
        row = self.transactions_table.rowAt(position.y())
        if row < 0:
            return
        id_item = self.transactions_table.item(row, 0)
        if not id_item:
            return
        transaction_id = id_item.data(Qt.ItemDataRole.UserRole)
        action = menu.exec(self.transactions_table.mapToGlobal(position))
        try:
            transaction = self.db_session.get(Transaction, transaction_id)
        except Exception:
            transaction = None
        
        if not transaction: return

        if action == edit_action:
            self.edit_transaction(transaction)
        elif action == delete_action:
            self.delete_transaction(transaction)

    def edit_transaction(self, transaction_to_edit):
        dialog = AddTransactionDialog(self, transaction=transaction_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.transaction_data
            transaction_to_edit.amount = data['amount']
            transaction_to_edit.description = data['description']
            try:
                self.db_session.commit()
            except Exception:
                if hasattr(self.db_session, 'rollback'):
                    self.db_session.rollback()
            # reload current session from DB if possible
            try:
                if hasattr(self.db_session, 'get'):
                    self.current_session = self.db_session.get(CashSession, self.current_session.id)
                elif hasattr(self.db_session, 'get_session_by_id'):
                    self.current_session = self.db_session.get_session_by_id(self.current_session.id)
            except Exception:
                pass
            self.load_transactions(self.current_session)
            self.update_summary_display(self.current_session)
            
    def delete_transaction(self, transaction_to_delete):
        if CustomMessageBox.show_question(self, 'تأكيد الحذف', f"هل أنت متأكد من حذف هذا المصروف؟"):
            self.db_session.delete(transaction_to_delete)
            try:
                self.db_session.commit()
            except Exception:
                if hasattr(self.db_session, 'rollback'):
                    self.db_session.rollback()
            # reload current session from DB if possible
            try:
                if hasattr(self.db_session, 'get'):
                    self.current_session = self.db_session.get(CashSession, self.current_session.id)
                elif hasattr(self.db_session, 'get_session_by_id'):
                    self.current_session = self.db_session.get_session_by_id(self.current_session.id)
            except Exception:
                pass
            self.load_transactions(self.current_session)
            self.update_summary_display(self.current_session)

    def close_cash_session(self):
        if not self.current_session: return
        summary = {
            'start_balance': self.current_session.start_balance, 
            'total_expense': self.current_session.total_expense,
            'start_flexi': self.current_session.start_flexi,
            'total_flexi_additions': self.current_session.total_flexi_additions
        }
        dialog = CloseCashDialog(summary, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data is None:
                CustomMessageBox.show_warning(self, "خطأ", "الرجاء إدخال قيم صحيحة.")
                return
            
            session_to_close = self.current_session
            session_to_close.end_balance = data["end_balance"]
            session_to_close.end_flexi = data["end_flexi"]
            session_to_close.status = 'closed'
            session_to_close.end_time = datetime.datetime.now(datetime.timezone.utc)
            try:
                self.db_session.commit()
            except Exception:
                if hasattr(self.db_session, 'rollback'):
                    self.db_session.rollback()
            try:
                if hasattr(self.db_session, 'get'):
                    session_to_close = self.db_session.get(CashSession, session_to_close.id)
                elif hasattr(self.db_session, 'get_session_by_id'):
                    self.current_session = self.db_session.get_session_by_id(session_to_close.id)
            except Exception:
                pass

            report_dialog = ClosingReportDialog(session_to_close, self)
            report_dialog.exec()
            
            self.current_session = None
            self.load_user_sessions_history()
            self.update_ui_for_session_status()

    def save_session_notes(self):
        if not self.sessions_history_list.currentItem(): return
        session_id_in_list = self.sessions_history_list.currentItem().data(Qt.ItemDataRole.UserRole)
        session_to_update = self.db_session.get(CashSession, session_id_in_list)
        if session_to_update and session_to_update.status == 'open':
            session_to_update.notes = self.notes_editor.toPlainText()
            self.db_session.commit()
            CustomMessageBox.show_information(self, "نجاح", "تم حفظ الملاحظات بنجاح.")
            self.load_user_sessions_history()
            # Reselect the same row after reloading
            for i in range(self.sessions_history_list.count()):
                item = self.sessions_history_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == session_id_in_list:
                    self.sessions_history_list.setCurrentRow(i)
                    break

    def load_transactions(self, session):
        self.transactions_table.setRowCount(0)
        if not session: return
        transactions = getattr(session, 'transactions', None)
        if not transactions:
            try:
                transactions = self.db_session.query(Transaction).filter_by(session_id=session.id).all()
            except Exception:
                transactions = []
        transactions = [t for t in transactions if getattr(t, 'type', 'expense') == 'expense']
        transactions.sort(key=lambda x: x.timestamp, reverse=True)
        for idx, transaction in enumerate(transactions, start=1):
            row_position = self.transactions_table.rowCount()
            self.transactions_table.insertRow(row_position)
            index_item = QTableWidgetItem(str(idx))
            # Format amount with thousands separator for readability
            try:
                amount_text = f"{transaction.amount:,.2f}"
            except Exception:
                amount_text = f"{getattr(transaction, 'amount', 0.0):.2f}"
            amount_item = QTableWidgetItem(amount_text)
            desc_item = QTableWidgetItem(transaction.description or "")
            time_item = QTableWidgetItem(transaction.timestamp.strftime("%H:%M:%S"))
            
            # Store ID in the first item of the row for easy retrieval
            index_item.setData(Qt.ItemDataRole.UserRole, transaction.id)
            
            # Align and set fonts for a cleaner, modern look
            index_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            amount_font = QFont()
            amount_font.setBold(True)
            amount_item.setFont(amount_font)

            self.transactions_table.setItem(row_position, 0, index_item)
            self.transactions_table.setItem(row_position, 1, amount_item)
            self.transactions_table.setItem(row_position, 2, desc_item)
            self.transactions_table.setItem(row_position, 3, time_item)

            # Increase row height for accessibility
            self.transactions_table.setRowHeight(row_position, 48)
            # color by transaction type
            if getattr(transaction, 'type', 'expense') == 'expense':
                amount_item.setForeground(QColor("#dc3545"))
            else:
                amount_item.setForeground(QColor("#198754"))
                
    def load_flexi_transactions(self, session):
        self.flexi_transactions_table.setRowCount(0)
        if not session: return
        transactions = getattr(session, 'flexi_transactions', [])
        transactions.sort(key=lambda x: x.timestamp, reverse=True)
        for idx, transaction in enumerate(transactions, start=1):
            row_position = self.flexi_transactions_table.rowCount()
            self.flexi_transactions_table.insertRow(row_position)
            index_item = QTableWidgetItem(str(idx))
            
            amount_text = f"{transaction.amount:,.2f}"
            amount_item = QTableWidgetItem(amount_text)
            desc_item = QTableWidgetItem(transaction.description or "")
            time_item = QTableWidgetItem(transaction.timestamp.strftime("%H:%M:%S"))
            
            index_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            amount_font = QFont()
            amount_font.setBold(True)
            amount_item.setFont(amount_font)
            amount_item.setForeground(QColor("#198754")) # Positive color for flexi additions

            self.flexi_transactions_table.setItem(row_position, 0, index_item)
            self.flexi_transactions_table.setItem(row_position, 1, amount_item)
            self.flexi_transactions_table.setItem(row_position, 2, desc_item)
            self.flexi_transactions_table.setItem(row_position, 3, time_item)
            self.flexi_transactions_table.setRowHeight(row_position, 48)


    def update_ui_for_session_status(self):
        has_open_session = self.current_session is not None
        self.open_cash_btn.setEnabled(not has_open_session)
        self.add_expense_btn.setEnabled(has_open_session)
        self.add_flexi_btn.setEnabled(has_open_session)
        self.close_cash_btn.setEnabled(has_open_session)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_summary_grid_layout()
        self.update_responsive_layouts()

    def eventFilter(self, obj, event):
        if obj is getattr(self, "summary_container", None) and event.type() == QEvent.Type.Resize:
            self.update_summary_grid_layout()
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        try:
            self.db_session.close()
        except Exception:
            pass
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = SessionLocal()
    # create or get user test (works with real DB or mock)
    try:
        test_user = db.query(User).filter_by(username='testuser').one()
    except Exception:
        try:
            test_user = db.query(User).filter_by(username='testuser').first()
        except Exception:
            test_user = None
    if not test_user:
        try:
            test_user = User(username='testuser', role='user')
            test_user.set_password('123')
            db.add(test_user)
            try:
                db.commit()
            except Exception:
                try:
                    db.rollback()
                except Exception:
                    pass
        except Exception:
            test_user = User()
    main_window = UserDashboard(user=test_user)
    main_window.show()
    try:
        db.close()
    except Exception:
        pass
    sys.exit(app.exec())
