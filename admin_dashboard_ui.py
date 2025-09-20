import sys
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QTableWidget, QHeaderView, 
                             QTableWidgetItem, QDialog, QLineEdit, QMessageBox, 
                             QDialogButtonBox, QHBoxLayout, QFrame,
                             QFormLayout, QListWidget, QListWidgetItem, QStackedWidget,
                             QComboBox, QSizePolicy, QStyle, QSplitter, QTextEdit,
                             QCheckBox, QMenu, QDateEdit)
from PyQt6.QtGui import (QColor, QMouseEvent, QDoubleValidator, QIcon, QFont, 
                         QPainter, QPen, QBrush, QAction)
from PyQt6.QtCore import Qt, QPoint, QSize, QDate, QRect

# استيراد النماذج وقاعدة البيانات
from database_setup import User, SessionLocal, CashSession, Transaction, FlexiTransaction, init_db
from sqlalchemy import extract, func

# --- Custom Bar Chart Widget ---
class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {} # expected format: {day: value}
        self.setMinimumHeight(200)
        self.toolTipLabel = QLabel(self)
        self.toolTipLabel.setObjectName("ChartToolTip")
        self.toolTipLabel.hide()
        self.setMouseTracking(True)

    def set_data(self, data_dict):
        self.data = data_dict
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Light Theme Colors
        bg_color, text_color_main = QColor("#ffffff"), QColor("#6c757d")
        painter.fillRect(self.rect(), bg_color)

        if not self.data:
            painter.setPen(text_color_main)
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "لا توجد بيانات لعرضها في هذا الشهر")
            return

        axis_color, bar_color, grid_color, text_color_labels = QColor("#adb5bd"), QColor("#0d6efd"), QColor("#e9ecef"), QColor("#495057")
        
        max_val = max(self.data.values()) if self.data else 1
        painter.setPen(grid_color)
        num_grid_lines = 5
        for i in range(1, num_grid_lines + 1):
            y = self.height() - 40 - i * (self.height() - 60) / num_grid_lines
            painter.drawLine(40, int(y), self.width() - 20, int(y))
        
        painter.setPen(axis_color)
        painter.drawLine(40, self.height() - 40, self.width() - 20, self.height() - 40)
        painter.drawLine(40, 20, 40, self.height() - 40)
        
        painter.setPen(text_color_labels)
        painter.setFont(QFont("Segoe UI", 8))
        for i in range(num_grid_lines + 1):
            val = (max_val / num_grid_lines) * i
            y = self.height() - 40 - i * (self.height() - 60) / num_grid_lines
            painter.drawText(5, int(y) + 5, f"{val:,.0f}")
        
        days = sorted(self.data.keys())
        bar_width = (self.width() - 70) / (len(days) * 1.5) if days else 10
        for i, day in enumerate(days):
            val = self.data[day]
            bar_height = (val / max_val) * (self.height() - 60) if max_val > 0 else 0
            x, y = 50 + i * (bar_width * 1.5), self.height() - 40 - bar_height
            painter.setBrush(bar_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
            painter.setPen(text_color_labels)
            painter.drawText(int(x), self.height() - 22, int(bar_width), 20, Qt.AlignmentFlag.AlignCenter, str(day))
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.data: return
        days = sorted(self.data.keys())
        bar_width = (self.width() - 70) / (len(days) * 1.5) if days else 10
        found_bar = False
        for i, day in enumerate(days):
            val = self.data[day]
            bar_height = (val / max(self.data.values(), default=1)) * (self.height() - 60)
            x, y = 50 + i * (bar_width * 1.5), self.height() - 40 - bar_height
            bar_rect = QRect(int(x), int(y), int(bar_width), int(bar_height))
            if bar_rect.contains(event.pos()):
                self.toolTipLabel.setText(f"<b>اليوم {day}:</b> {val:,.2f}")
                self.toolTipLabel.adjustSize()
                pos = event.globalPosition().toPoint()
                self.toolTipLabel.move(self.mapFromGlobal(pos) + QPoint(10, -30))
                self.toolTipLabel.show()
                found_bar = True
                break
        if not found_bar: self.toolTipLabel.hide()

# --- Custom Stat Card Widget ---
class StatCard(QFrame):
    def __init__(self, title, icon: QIcon, accent: str = "primary", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setProperty("accentColor", accent)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("StatCardTitle")
        self.title_label.setWordWrap(True)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon.pixmap(24, 24))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setObjectName("StatCardIcon")

        header_layout.addWidget(self.title_label, 1)
        header_layout.addWidget(self.icon_label)

        self.value_label = QLabel("0.00")
        self.value_label.setObjectName("StatCardValue")
        self.value_label.setWordWrap(True)

        self.caption_label = QLabel("")
        self.caption_label.setObjectName("StatCardCaption")
        self.caption_label.setWordWrap(True)
        self.caption_label.setVisible(False)

        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addWidget(self.caption_label)
        layout.addStretch(1)

    def set_value(self, value_text):
        self.value_label.setText(value_text)

    def set_caption(self, caption_text: str):
        self.caption_label.setText(caption_text)
        self.caption_label.setVisible(bool(caption_text))
        
# --- Dialogs ---
class CustomDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self.old_pos = None
        self.bg_frame = QFrame(self); self.bg_frame.setObjectName("CustomDialogFrame")
        frame_layout = QVBoxLayout(self.bg_frame)
        frame_layout.setContentsMargins(1, 1, 1, 1); frame_layout.setSpacing(0)
        self.title_bar = QWidget(); self.title_bar.setObjectName("CustomTitleBar"); self.title_bar.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(self.title_bar); title_bar_layout.setContentsMargins(15, 0, 5, 0)
        self.title_label = QLabel(title); self.title_label.setObjectName("CustomTitleLabel")
        self.close_button = QPushButton("✕"); self.close_button.setObjectName("CustomCloseButton"); self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.reject)
        title_bar_layout.addWidget(self.title_label); title_bar_layout.addStretch(); title_bar_layout.addWidget(self.close_button)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 15, 20, 20); self.content_layout.setSpacing(15) # Increased spacing
        frame_layout.addWidget(self.title_bar); frame_layout.addWidget(self.content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0); main_layout.addWidget(self.bg_frame)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.underMouse(): self.old_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos: delta = QPoint(event.globalPosition().toPoint() - self.old_pos); self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event: QMouseEvent): self.old_pos = None

class UserDialog(CustomDialog):
    def __init__(self, parent=None, user: User = None):
        self.is_edit_mode = user is not None
        title = "تعديل بيانات العامل" if self.is_edit_mode else "إضافة عامل جديد"
        super().__init__(title, parent)
        self.setMinimumWidth(420)
        layout = self.content_layout
        layout.addWidget(QLabel("اسم المستخدم:"))
        self.username_input = QLineEdit(); self.username_input.setPlaceholderText("ادخل اسم المستخدم")
        layout.addWidget(self.username_input)
        password_label_text = "كلمة المرور الجديدة (اتركه فارغاً لعدم التغيير):" if self.is_edit_mode else "كلمة المرور:"
        layout.addWidget(QLabel(password_label_text))
        self.password_input = QLineEdit(); self.password_input.setPlaceholderText("ادخل كلمة المرور"); self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        if self.is_edit_mode: self.username_input.setText(user.username)
    def get_data(self):
        username = self.username_input.text().strip(); password = self.password_input.text()
        if not self.is_edit_mode and not (username and password): return None
        if self.is_edit_mode and not username: return None
        return {"username": username, "password": password}

class PasswordConfirmDialog(CustomDialog):
    def __init__(self, parent=None):
        super().__init__("تأكيد كلمة المرور", parent)
        self.setMinimumWidth(400)
        layout = self.content_layout
        layout.addWidget(QLabel("الرجاء إدخال كلمة مرور المشرف للمتابعة:"))
        self.password_input = QLineEdit(); self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
    def get_password(self): return self.password_input.text()

class EditSessionDialog(CustomDialog):
    def __init__(self, session: CashSession, parent=None):
        super().__init__(f"تعديل جلسة العامل: {session.user.username if session.user else 'محذوف'}", parent)
        self.setMinimumWidth(450); self.session = session
        layout = self.content_layout; form_layout = QFormLayout()
        
        # New: Flexi fields
        start_balance_flexi_val = str(session.start_flexi) if session.start_flexi is not None else ""
        end_balance_flexi_val = str(session.end_flexi) if session.end_flexi is not None else ""
        self.start_flexi_input = QLineEdit(start_balance_flexi_val); self.start_flexi_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        self.end_flexi_input = QLineEdit(end_balance_flexi_val); self.end_flexi_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        
        start_balance_val = str(session.start_balance) if session.start_balance is not None else ""
        end_balance_val = str(session.end_balance) if session.end_balance is not None else ""
        self.start_balance_input = QLineEdit(start_balance_val); self.start_balance_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))
        self.end_balance_input = QLineEdit(end_balance_val); self.end_balance_input.setValidator(QDoubleValidator(0.0, 99999999.99, 2))

        form_layout.addRow("رصيد النقد (البداية):", self.start_balance_input)
        form_layout.addRow("رصيد النقد (النهاية):", self.end_balance_input)
        form_layout.addRow("رصيد الفليكسي (البداية):", self.start_flexi_input)
        form_layout.addRow("رصيد الفليكسي (النهاية):", self.end_flexi_input)
        
        layout.addLayout(form_layout)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
    def get_data(self):
        try:
            start_balance = float(self.start_balance_input.text()) if self.start_balance_input.text() else 0.0
            end_balance = float(self.end_balance_input.text()) if self.end_balance_input.text() else None
            start_flexi = float(self.start_flexi_input.text()) if self.start_flexi_input.text() else None
            end_flexi = float(self.end_flexi_input.text()) if self.end_flexi_input.text() else None
            return {"start_balance": start_balance, "end_balance": end_balance, "start_flexi": start_flexi, "end_flexi": end_flexi}
        except ValueError: return None

# --- Session Details Dialog ---
class SessionDetailsDialog(CustomDialog):
    def __init__(self, session_id, parent=None):
        self.db_session = SessionLocal()
        self.session = self.db_session.query(CashSession).get(session_id)
        super().__init__(f"تفاصيل الجلسة - {self.session.user.username if self.session.user else 'محذوف'}", parent)
        self.setMinimumSize(800, 600)
        self.setup_details_ui()
        self.load_session_data()

    def setup_details_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Expenses section
        expenses_widget = QWidget()
        expenses_layout = QVBoxLayout(expenses_widget)
        expenses_title = QLabel("المصروفات")
        expenses_title.setObjectName("SectionTitle")
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(3) # Removed empty column
        self.expenses_table.setHorizontalHeaderLabels(["المبلغ", "الملاحظة", "الوقت"])
        self.expenses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.expenses_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.expenses_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.expenses_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.expenses_table.customContextMenuRequested.connect(self.open_expense_menu)
        expenses_layout.addWidget(expenses_title)
        expenses_layout.addWidget(self.expenses_table)
        
        # Notes section
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_title = QLabel("ملاحظات الجلسة")
        notes_title.setObjectName("SectionTitle")
        self.notes_editor = QTextEdit()
        self.save_notes_btn = QPushButton("حفظ الملاحظات")
        self.save_notes_btn.clicked.connect(self.save_notes)
        notes_layout.addWidget(notes_title)
        notes_layout.addWidget(self.notes_editor)
        notes_layout.addWidget(self.save_notes_btn)

        splitter.addWidget(expenses_widget)
        splitter.addWidget(notes_widget)
        splitter.setSizes([500, 300])
        self.content_layout.addWidget(splitter)

    def load_session_data(self):
        self.db_session.refresh(self.session)
        self.notes_editor.setText(self.session.notes or "")
        self.expenses_table.setRowCount(0)
        transactions = sorted(self.session.transactions, key=lambda t: t.timestamp, reverse=True)
        for t in transactions:
            row = self.expenses_table.rowCount()
            self.expenses_table.insertRow(row)
            amount_item = QTableWidgetItem(f"{t.amount:,.2f}")
            amount_item.setData(Qt.ItemDataRole.UserRole, t.id)
            desc_item = QTableWidgetItem(t.description)
            time_item = QTableWidgetItem(t.timestamp.strftime("%H:%M"))
            self.expenses_table.setItem(row, 0, amount_item)
            self.expenses_table.setItem(row, 1, desc_item)
            self.expenses_table.setItem(row, 2, time_item)

    def open_expense_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("تعديل المصروف")
        delete_action = menu.addAction("حذف المصروف")
        action = menu.exec(self.expenses_table.mapToGlobal(position))
        
        if action == edit_action: self.edit_expense()
        elif action == delete_action: self.delete_expense()

    def get_selected_transaction(self):
        selected_items = self.expenses_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "خطأ", "الرجاء تحديد مصروف أولاً.")
            return None
        transaction_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        return self.db_session.query(Transaction).get(transaction_id)
        
    def edit_expense(self):
        # Implementation similar to AddTransactionDialog would be needed here
        # For brevity, let's assume a simplified modification logic
        QMessageBox.information(self, "ميزة", "سيتم تنفيذ ميزة تعديل المصروف هنا.")

    def delete_expense(self):
        transaction = self.get_selected_transaction()
        if transaction:
            reply = QMessageBox.question(self, 'تأكيد الحذف', f"هل أنت متأكد من حذف هذا المصروف؟",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db_session.delete(transaction)
                self.db_session.commit()
                self.load_session_data()

    def save_notes(self):
        self.session.notes = self.notes_editor.toPlainText()
        self.db_session.commit()
        QMessageBox.information(self, "نجاح", "تم حفظ الملاحظات.")
        
    def closeEvent(self, event):
        self.db_session.close()
        super().closeEvent(event)

# --- Main Admin Dashboard ---
class AdminDashboard(QMainWindow):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.db_session = SessionLocal()
        self.show_timestamps = False # Default setting
        self.setWindowTitle(f"لوحة تحكم المشرف - مرحباً {self.user.username}")
        self.setGeometry(100, 100, 1400, 850)
        self.setMinimumSize(1280, 800)
        
        self.icon_user = self.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon) 
        self.icon_report = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self.icon_users = self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon)
        self.icon_dashboard = self.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
        self.icon_settings = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)

        self.setup_ui()
        self.apply_styles()
        self.populate_user_list()
        self.pages.setCurrentIndex(0) 
        self.load_dashboard_data()

    def setup_ui(self):
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        nav_widget = QWidget(); nav_widget.setObjectName("NavWidget"); nav_widget.setFixedWidth(240)
        nav_layout = QVBoxLayout(nav_widget); nav_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- NEW: Header with title and settings button ---
        header_layout = QHBoxLayout()
        nav_title = QLabel("لوحة التحكم"); nav_title.setObjectName("NavTitle")
        self.settings_btn = QPushButton(); self.settings_btn.setIcon(self.icon_settings)
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.clicked.connect(self.show_settings_page)
        header_layout.addWidget(nav_title)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_btn)
        nav_layout.addLayout(header_layout)
        
        self.nav_list = QListWidget(); self.nav_list.setObjectName("NavList")
        QListWidgetItem(self.icon_dashboard, "لوحة المعلومات", self.nav_list)
        QListWidgetItem(self.icon_users, "إدارة العمال", self.nav_list)
        QListWidgetItem(self.icon_report, "تقرير الجلسات", self.nav_list)
        
        separator = QFrame(); separator.setFrameShape(QFrame.Shape.HLine); separator.setObjectName("NavSeparator")
        users_title = QLabel("العمال"); users_title.setObjectName("NavGroupTitle")
        self.user_search_input = QLineEdit(); self.user_search_input.setPlaceholderText("ابحث عن عامل...")
        self.user_search_input.setObjectName("UserSearch")
        self.user_search_input.textChanged.connect(self.filter_user_list)
        self.user_nav_list = QListWidget(); self.user_nav_list.setObjectName("UserNavList")

        nav_layout.addWidget(self.nav_list); nav_layout.addWidget(separator); nav_layout.addWidget(users_title)
        nav_layout.addWidget(self.user_search_input); nav_layout.addWidget(self.user_nav_list)
        
        self.pages = QStackedWidget()
        main_layout.addWidget(nav_widget); main_layout.addWidget(self.pages)
        self.nav_list.currentRowChanged.connect(self.change_main_page)
        self.user_nav_list.itemClicked.connect(self.select_user_profile)

        # Page creation order matters for setCurrentIndex
        self.create_dashboard_page()          # Index 0
        self.create_user_management_page()    # Index 1
        self.create_sessions_report_page()    # Index 2
        self.create_settings_page()           # Index 3
        self.create_user_profile_page()       # Index 4

    def create_dashboard_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        title = QLabel("ملخص الأداء العام"); title.setObjectName("PageTitle")
        
        self.dash_date_filter = QComboBox()
        self.dash_date_filter.addItems(["الشهر الحالي", "الشهر الماضي", "آخر 7 أيام", "آخر 30 يومًا"])
        self.dash_date_filter.currentIndexChanged.connect(self.load_dashboard_data)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("عرض:"))
        header_layout.addWidget(self.dash_date_filter)
        layout.addLayout(header_layout)
        
        stats_layout = QHBoxLayout(); stats_layout.setSpacing(20)
        self.dash_card_sessions = StatCard("مجموع الجلسات", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogListView), accent="cyan")
        self.dash_card_expenses = StatCard("مجموع المصاريف", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown), accent="rose")
        
        # NEW: Flexi Additions Card
        self.dash_card_flexi_additions = StatCard("مجموع إضافات الفليكسي", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp), accent="violet")
        
        # -- تعديل --: بطاقة جديدة لصافي الفرق النقدي
        self.dash_card_net_cash = StatCard("صافي الفرق (نقد)", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp), accent="emerald")
        
        # -- إضافة --: بطاقة جديدة للفليكسي المستهلك
        self.dash_card_flexi_consumed = StatCard("الفليكسي المستهلك", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown), accent="orange")

        stats_layout.addWidget(self.dash_card_sessions); stats_layout.addWidget(self.dash_card_expenses); stats_layout.addWidget(self.dash_card_flexi_additions); stats_layout.addWidget(self.dash_card_net_cash); stats_layout.addWidget(self.dash_card_flexi_consumed)

        layout.addLayout(stats_layout); layout.addStretch(); self.pages.addWidget(page)

    def create_user_management_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)
        title = QLabel("إدارة العمال"); title.setObjectName("PageTitle")
        self.add_user_btn = QPushButton("إضافة عامل جديد"); self.add_user_btn.setFixedWidth(180); self.add_user_btn.clicked.connect(self.add_new_user)
        self.users_table = QTableWidget(); self.users_table.setColumnCount(4); self.users_table.setHorizontalHeaderLabels(["ID", "اسم المستخدم", "الدور", "إجراءات"])
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(title); layout.addWidget(self.add_user_btn, alignment=Qt.AlignmentFlag.AlignLeft); layout.addWidget(self.users_table)
        self.pages.addWidget(page)

    def create_sessions_report_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        title = QLabel("تقرير جميع الجلسات"); title.setObjectName("PageTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.report_user_filter = QComboBox()
        self.report_date_start = QDateEdit(QDate.currentDate().addMonths(-1))
        self.report_date_end = QDateEdit(QDate.currentDate())
        self.report_date_start.setCalendarPopup(True)
        self.report_date_end.setCalendarPopup(True)
        self.report_user_filter.currentIndexChanged.connect(self.load_sessions_report)
        self.report_date_start.dateChanged.connect(self.load_sessions_report)
        self.report_date_end.dateChanged.connect(self.load_sessions_report)

        header_layout.addWidget(QLabel("العامل:"))
        header_layout.addWidget(self.report_user_filter)
        header_layout.addWidget(QLabel("من:"))
        header_layout.addWidget(self.report_date_start)
        header_layout.addWidget(QLabel("إلى:"))
        header_layout.addWidget(self.report_date_end)
        
        layout.addLayout(header_layout)

        self.reports_table = QTableWidget()
        self.reports_table.setSortingEnabled(True)
        # New columns for Flexi
        self.reports_table.setColumnCount(11)
        self.reports_table.setHorizontalHeaderLabels([
            "العامل", "وقت الفتح", "وقت الإغلاق", 
            "رصيد النقد (البداية)", "رصيد النقد (النهاية)", "الفرق (النقد)", 
            "رصيد الفليكسي (البداية)", "مجموع الإضافات", "رصيد الفليكسي (النهاية)",
            "الحالة", "إجراءات"
        ])
        header = self.reports_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 11): header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.reports_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.reports_table); self.pages.addWidget(page)
    
    def create_user_profile_page(self):
        page = QWidget()
        profile_page_layout = QVBoxLayout(page)
        self.user_profile_placeholder = QLabel("الرجاء اختيار عامل من القائمة لعرض ملفه الشخصي"); self.user_profile_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter); self.user_profile_placeholder.setObjectName("PlaceholderLabel")
        profile_page_layout.addWidget(self.user_profile_placeholder)
        self.user_profile_widget = QWidget()
        self.user_profile_layout = QVBoxLayout(self.user_profile_widget); self.user_profile_layout.setContentsMargins(25, 25, 25, 25); self.user_profile_layout.setSpacing(20)
        profile_page_layout.addWidget(self.user_profile_widget)
        header_layout = QHBoxLayout()
        self.profile_title = QLabel("ملف العامل"); self.profile_title.setObjectName("PageTitle")
        current_date = QDate.currentDate()
        self.year_filter = QComboBox()
        for year in range(current_date.year() - 5, current_date.year() + 1): self.year_filter.addItem(str(year))
        self.year_filter.setCurrentText(str(current_date.year()))
        self.month_filter = QComboBox()
        for month in range(1, 13): self.month_filter.addItem(QDate(2000, month, 1).toString("MMMM"), month)
        self.month_filter.setCurrentIndex(current_date.month() - 1)
        self.year_filter.currentIndexChanged.connect(self.update_profile_view); self.month_filter.currentIndexChanged.connect(self.update_profile_view)
        header_layout.addWidget(self.profile_title); header_layout.addStretch()
        header_layout.addWidget(QLabel("الشهر:")); header_layout.addWidget(self.month_filter)
        header_layout.addWidget(QLabel("السنة:")); header_layout.addWidget(self.year_filter)
        self.user_profile_layout.addLayout(header_layout)
        stats_layout = QHBoxLayout(); stats_layout.setSpacing(20)
        self.profile_card_sessions = StatCard("عدد الجلسات", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogListView), accent="cyan")
        self.profile_card_expenses = StatCard("مجموع المصاريف", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown), accent="rose")
        
        # NEW: Flexi Additions for user profile
        self.profile_card_flexi_additions = StatCard("مجموع إضافات الفليكسي", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp), accent="violet")
        
        # -- تعديل --: بطاقات جديدة لصافي الفرق النقدي والفليكسي المستهلك
        self.profile_card_net_cash = StatCard("صافي الفرق (نقد)", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp), accent="emerald")
        self.profile_card_flexi_consumed = StatCard("الفليكسي المستهلك", self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown), accent="orange")

        stats_layout.addWidget(self.profile_card_sessions); stats_layout.addWidget(self.profile_card_expenses); stats_layout.addWidget(self.profile_card_flexi_additions); stats_layout.addWidget(self.profile_card_net_cash); stats_layout.addWidget(self.profile_card_flexi_consumed)

        self.user_profile_layout.addLayout(stats_layout)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_title = QLabel("المصاريف اليومية للشهر المحدد"); chart_title.setObjectName("SectionTitle")
        self.expenses_chart = BarChartWidget()
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.expenses_chart)
        
        sessions_widget = QWidget()
        sessions_layout = QVBoxLayout(sessions_widget)
        sessions_title = QLabel("جلسات العامل للشهر المحدد"); sessions_title.setObjectName("SectionTitle")
        self.user_sessions_table = QTableWidget(); 
        self.user_sessions_table.setColumnCount(10)
        self.user_sessions_table.setHorizontalHeaderLabels([
            "وقت الفتح", "وقت الإغلاق", 
            "رصيد النقد (البداية)", "رصيد النقد (النهاية)", "الفرق (النقد)", 
            "رصيد الفليكسي (البداية)", "مجموع الإضافات", "رصيد الفليكسي (النهاية)",
            "الحالة", "إجراءات"
        ])
        header = self.user_sessions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in range(2, 10): header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        sessions_layout.addWidget(sessions_title)
        sessions_layout.addWidget(self.user_sessions_table)

        splitter.addWidget(chart_widget)
        splitter.addWidget(sessions_widget)
        splitter.setSizes([250, 400])
        self.user_profile_layout.addWidget(splitter)
        
        self.pages.addWidget(page)
        self.user_profile_widget.hide()
        
    def create_settings_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)
        title = QLabel("الإعدادات"); title.setObjectName("PageTitle")
        self.timestamps_checkbox = QCheckBox("إظهار وقت الفتح والإغلاق في الجداول")
        self.timestamps_checkbox.setChecked(self.show_timestamps)
        self.timestamps_checkbox.stateChanged.connect(self.toggle_timestamp_visibility)
        layout.addWidget(title); layout.addWidget(self.timestamps_checkbox); layout.addStretch()
        self.pages.addWidget(page)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #e8ecf7; font-family: 'Segoe UI', 'Cairo', sans-serif; }
            QWidget#NavWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f2937, stop:1 #0f172a);
                border-right: none;
                color: #e2e8f0;
                padding-top: 12px;
            }
            QLabel#NavTitle { font-size: 18pt; font-weight: 800; color: #f8fafc; padding: 8px 4px; }
            QLabel#NavGroupTitle {
                font-size: 10.5pt;
                font-weight: 600;
                color: rgba(226, 232, 240, 0.7);
                padding: 18px 6px 10px;
                border-top: 1px solid rgba(148, 163, 184, 0.25);
                margin-top: 12px;
            }
            QFrame#NavSeparator { background-color: rgba(148, 163, 184, 0.25); height: 1px; }
            QListWidget#NavList, QListWidget#UserNavList {
                border: none;
                background: transparent;
                color: #e2e8f0;
            }
            QListWidget#NavList::item, QListWidget#UserNavList::item {
                color: #e2e8f0;
                padding: 12px 18px;
                border-radius: 12px;
                margin: 2px 0;
            }
            QListWidget#NavList::item:hover, QListWidget#UserNavList::item:hover {
                background-color: rgba(59, 130, 246, 0.28);
            }
            QListWidget#NavList::item:selected, QListWidget#UserNavList::item:selected {
                background-color: rgba(37, 99, 235, 0.7);
                color: #ffffff;
            }

            /* Main Window Inputs */
            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 11pt;
                background-color: #ffffff;
                color: #0f172a;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #2563eb;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
            }
            QLineEdit#UserSearch {
                background-color: rgba(15, 23, 42, 0.35);
                color: #f8fafc;
                border: 1px solid rgba(148, 163, 184, 0.4);
                margin: 6px 0;
            }
            QLineEdit#UserSearch::placeholder { color: rgba(226, 232, 240, 0.65); }
            QCheckBox { color: #475569; font-size: 10.5pt; }
            QComboBox::drop-down { border: none; }

            QLabel#PageTitle { font-size: 20pt; font-weight: 800; color: #0f172a; margin-bottom: 18px; }
            QLabel#SectionTitle { font-size: 12.5pt; font-weight: 700; color: #1f2937; margin: 18px 0 8px; }
            QLabel#PlaceholderLabel { font-size: 14pt; color: #94a3b8; }

            QTableWidget {
                font-size: 11pt;
                border: none;
                background-color: #ffffff;
                gridline-color: #e2e8f0;
                color: #0f172a;
                border-radius: 16px;
            }
            QTableWidget::item { padding: 12px 10px; }
            QTableWidget::item:selected { background-color: #dbeafe; color: #1e3a8a; }
            QHeaderView::section {
                background-color: #f1f5f9;
                color: #475569;
                padding: 14px 12px;
                font-size: 10.5pt;
                font-weight: 700;
                border-bottom: 1px solid rgba(148, 163, 184, 0.3);
                border-right: none;
            }

            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                color: #ffffff;
                font-size: 10.5pt;
                font-weight: 700;
                padding: 12px 22px;
                border-radius: 14px;
                border: none;
            }
            QPushButton:hover { background: #1e3a8a; }

            QPushButton#SettingsButton {
                background-color: rgba(255,255,255,0.08);
                border-radius: 12px;
                padding: 6px;
                max-width: 36px;
            }
            QPushButton#SettingsButton:hover { background-color: rgba(59, 130, 246, 0.25); }

            .ActionButton {
                font-size: 9.5pt;
                padding: 6px 10px;
                color: white;
                border-radius: 10px;
            }
            .DetailsButton { background-color: #22c55e; }
            .DetailsButton:hover { background-color: #16a34a; }
            .EditButton { background-color: #2563eb; }
            .EditButton:hover { background-color: #1d4ed8; }
            .DeleteButton { background-color: #ef4444; }
            .DeleteButton:hover { background-color: #dc2626; }
            .ActionButton:disabled, QPushButton:disabled { background-color: rgba(148, 163, 184, 0.4); color: #94a3b8; }

            QFrame#StatCard {
                background-color: #ffffff;
                border-radius: 24px;
                border: 1px solid rgba(148, 163, 184, 0.25);
                box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
            }
            QLabel#StatCardIcon {
                background-color: rgba(37, 99, 235, 0.12);
                border-radius: 16px;
                color: #1d4ed8;
                padding: 8px;
            }
            QLabel#StatCardTitle { font-size: 12pt; font-weight: 700; color: #64748b; }
            QLabel#StatCardValue { font-size: 28pt; font-weight: 800; color: #0f172a; }
            QLabel#StatCardCaption { font-size: 10pt; color: #64748b; }

            QFrame#StatCard[accentColor="cyan"] QLabel#StatCardIcon { background-color: rgba(14,165,233,0.2); color: #0e7490; }
            QFrame#StatCard[accentColor="cyan"] QLabel#StatCardValue { color: #0e7490; }
            QFrame#StatCard[accentColor="rose"] QLabel#StatCardIcon { background-color: rgba(244,114,182,0.2); color: #be123c; }
            QFrame#StatCard[accentColor="rose"] QLabel#StatCardValue { color: #be123c; }
            QFrame#StatCard[accentColor="violet"] QLabel#StatCardIcon { background-color: rgba(139,92,246,0.18); color: #7c3aed; }
            QFrame#StatCard[accentColor="violet"] QLabel#StatCardValue { color: #7c3aed; }
            QFrame#StatCard[accentColor="emerald"] QLabel#StatCardIcon { background-color: rgba(34,197,94,0.18); color: #047857; }
            QFrame#StatCard[accentColor="emerald"] QLabel#StatCardValue { color: #047857; }
            QFrame#StatCard[accentColor="orange"] QLabel#StatCardIcon { background-color: rgba(249,115,22,0.2); color: #c2410c; }
            QFrame#StatCard[accentColor="orange"] QLabel#StatCardValue { color: #c2410c; }

            #ChartToolTip { background-color: rgba(15, 23, 42, 0.9); color: white; border: none; padding: 6px 10px; border-radius: 6px; }

            /* Dialog Styles */
            QDialog QLineEdit, QDialog QTextEdit, QDialog QComboBox {
                background-color: #ffffff; color: #0f172a; border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 10px; padding: 10px; font-size: 11pt;
            }
            QDialog QLineEdit:focus, QDialog QTextEdit:focus { border-color: #2563eb; }
            QDialog QLabel { color: #475569; font-size: 11pt; }

            #CustomDialogFrame { background-color: #ffffff; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 16px; }
            #CustomTitleBar { background-color: #f1f5f9; border-top-left-radius: 15px; border-top-right-radius: 15px; border-bottom: 1px solid rgba(148, 163, 184, 0.25); }
            #CustomTitleLabel { font-size: 11pt; font-weight: bold; color: #0f172a; }
            #CustomCloseButton { background-color: transparent; color: #64748b; border: none; font-size: 14pt; font-weight: bold; border-radius: 6px; }
            #CustomCloseButton:hover { background-color: #ef4444; color: white; }
        """)

    def toggle_timestamp_visibility(self, state):
        self.show_timestamps = bool(state)
        # Main report table
        self.reports_table.setColumnHidden(1, not self.show_timestamps)
        self.reports_table.setColumnHidden(2, not self.show_timestamps)
        # User profile sessions table
        self.user_sessions_table.setColumnHidden(0, not self.show_timestamps)
        self.user_sessions_table.setColumnHidden(1, not self.show_timestamps)

    def load_dashboard_data(self):
        today = datetime.date.today()
        period = self.dash_date_filter.currentText()

        if period == "الشهر الحالي":
            start_date = today.replace(day=1)
            end_date = today
        elif period == "الشهر الماضي":
            first_day_of_current_month = today.replace(day=1)
            end_date = first_day_of_current_month - datetime.timedelta(days=1)
            start_date = end_date.replace(day=1)
        elif period == "آخر 7 أيام":
            start_date = today - datetime.timedelta(days=6)
            end_date = today
        elif period == "آخر 30 يومًا":
            start_date = today - datetime.timedelta(days=29)
            end_date = today
        else:
            return

        sessions = self.db_session.query(CashSession).filter(
            func.date(CashSession.start_time) >= start_date,
            func.date(CashSession.start_time) <= end_date
        ).all()
        
        total_sessions = len(sessions)
        total_expenses = sum(s.total_expense for s in sessions)
        total_flexi_additions = sum(s.total_flexi_additions for s in sessions)
        # -- تعديل --: حساب صافي الفرق النقدي الإجمالي والفليكسي المستهلك
        net_cash_difference = sum(s.net_cash_difference for s in sessions if s.end_balance is not None)
        flexi_consumed_total = sum(s.flexi_consumed for s in sessions if s.end_flexi is not None)

        self.dash_card_sessions.set_value(str(total_sessions))
        self.dash_card_expenses.set_value(f"{total_expenses:,.2f}")
        self.dash_card_flexi_additions.set_value(f"{total_flexi_additions:,.2f}")
        self.dash_card_net_cash.set_value(f"{net_cash_difference:+,.2f}")
        self.dash_card_flexi_consumed.set_value(f"{flexi_consumed_total:,.2f}")

        self.dash_card_sessions.set_caption(f"خلال {period}")
        if total_sessions:
            avg_expense = total_expenses / total_sessions
            self.dash_card_expenses.set_caption(f"متوسط {avg_expense:,.2f} لكل جلسة")
        else:
            self.dash_card_expenses.set_caption("لا توجد جلسات في هذه الفترة")
        self.dash_card_flexi_additions.set_caption("إجمالي عمليات الفليكسي المسجلة")
        self.dash_card_net_cash.set_caption("يشمل الجلسات المغلقة فقط")
        self.dash_card_flexi_consumed.set_caption("يُحتسب عند إغلاق الجلسة")


    def load_user_profile_data(self, user, year, month):
        self.profile_title.setText(f"ملف العامل: {user.username}")
        sessions = self.db_session.query(CashSession).filter(CashSession.user_id == user.id, extract('year', CashSession.start_time) == year, extract('month', CashSession.start_time) == month).order_by(CashSession.start_time.desc()).all()
        session_count, total_expenses, total_flexi_additions = len(sessions), sum(s.total_expense for s in sessions), sum(s.total_flexi_additions for s in sessions)
        # -- تعديل --: حساب صافي الفرق النقدي والفليكسي المستهلك
        net_cash_difference = sum(s.net_cash_difference for s in sessions if s.end_balance is not None)
        flexi_consumed_total = sum(s.flexi_consumed for s in sessions if s.end_flexi is not None)
        
        self.profile_card_sessions.set_value(f"{session_count}")
        self.profile_card_expenses.set_value(f"{total_expenses:,.2f}")
        self.profile_card_flexi_additions.set_value(f"{total_flexi_additions:,.2f}")
        self.profile_card_net_cash.set_value(f"{net_cash_difference:+,.2f}")
        self.profile_card_flexi_consumed.set_value(f"{flexi_consumed_total:,.2f}")

        if session_count:
            avg_expense = total_expenses / session_count
            self.profile_card_expenses.set_caption(f"متوسط {avg_expense:,.2f} لكل جلسة")
        else:
            self.profile_card_expenses.set_caption("لا توجد جلسات")
        self.profile_card_sessions.set_caption(f"الفترة: {month}/{year}")
        self.profile_card_flexi_additions.set_caption("قيمة الفليكسي المضافة")
        self.profile_card_net_cash.set_caption("يشمل الجلسات المغلقة")
        self.profile_card_flexi_consumed.set_caption("يظهر عند الإغلاق")
        
        expense_by_day = {day: 0 for day in range(1, 32)}
        for session in sessions: expense_by_day[session.start_time.day] += session.total_expense
        self.expenses_chart.set_data({k: v for k, v in expense_by_day.items() if v > 0})
        
        self.user_sessions_table.setRowCount(0)
        for row, session in enumerate(sessions):
            self.user_sessions_table.insertRow(row)
            self.user_sessions_table.setItem(row, 0, QTableWidgetItem(session.start_time.strftime("%Y-%m-%d %H:%M")))
            self.user_sessions_table.setItem(row, 1, QTableWidgetItem(session.end_time.strftime("%Y-%m-%d %H:%M") if session.end_time else "N/A"))
            self.user_sessions_table.setItem(row, 2, QTableWidgetItem(f"{session.start_balance:,.2f}"))
            self.user_sessions_table.setItem(row, 3, QTableWidgetItem(f"{session.end_balance:,.2f}" if session.end_balance is not None else "N/A"))
            # -- تعديل --: استخدام الخاصية net_cash_difference
            diff_cash = session.net_cash_difference
            diff_cash_item = QTableWidgetItem(f"{diff_cash:+,.2f}"); 
            if diff_cash < 0: diff_cash_item.setForeground(QColor("#dc3545"))
            elif diff_cash > 0: diff_cash_item.setForeground(QColor("#198754"))
            self.user_sessions_table.setItem(row, 4, diff_cash_item)
            
            self.user_sessions_table.setItem(row, 5, QTableWidgetItem(f"{session.start_flexi:,.2f}"))
            self.user_sessions_table.setItem(row, 6, QTableWidgetItem(f"{session.total_flexi_additions:,.2f}"))
            self.user_sessions_table.setItem(row, 7, QTableWidgetItem(f"{session.end_flexi:,.2f}" if session.end_flexi is not None else "N/A"))
            
            self.user_sessions_table.setItem(row, 8, QTableWidgetItem("مغلقة" if session.status == 'closed' else "مفتوحة"))
            self.add_user_session_actions(row, session)
        self.toggle_timestamp_visibility(self.show_timestamps)

    def populate_user_list(self):
        self.user_nav_list.clear()
        self.report_user_filter.clear()
        self.report_user_filter.addItem("جميع العمال", 0)

        users = self.db_session.query(User).filter(User.role == 'user').order_by(User.username).all()
        for user in users:
            item = QListWidgetItem(self.icon_user, user.username)
            item.setData(Qt.ItemDataRole.UserRole, user.id); self.user_nav_list.addItem(item)
            self.report_user_filter.addItem(user.username, user.id)

    
    def filter_user_list(self):
        filter_text = self.user_search_input.text().lower()
        for i in range(self.user_nav_list.count()):
            item = self.user_nav_list.item(i); item.setHidden(filter_text not in item.text().lower())

    def change_main_page(self, index):
        self.user_nav_list.clearSelection()
        if index < 3: # Corresponds to: Dashboard, User Mgmt, Reports
            self.pages.setCurrentIndex(index)
            if index == 0: self.load_dashboard_data()
            elif index == 1: self.load_users()
            elif index == 2: self.load_sessions_report()
            
            # Ensure profile page is hidden
            if self.pages.widget(4) is self.user_profile_widget.parent():
                 self.user_profile_placeholder.show(); self.user_profile_widget.hide()


    def show_settings_page(self):
        self.nav_list.clearSelection()
        self.user_nav_list.clearSelection()
        self.pages.setCurrentIndex(3) # Index of settings page is now 3
        self.user_profile_placeholder.show(); self.user_profile_widget.hide()


    def select_user_profile(self, item):
        self.nav_list.clearSelection()
        user_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_selected_user = self.db_session.query(User).get(user_id)
        if self.current_selected_user:
            self.pages.setCurrentIndex(4) # The profile page is index 4
            self.update_profile_view()
            self.user_profile_placeholder.hide(); self.user_profile_widget.show()

    def update_profile_view(self):
        if hasattr(self, 'current_selected_user') and self.current_selected_user:
            year = int(self.year_filter.currentText()); month = self.month_filter.currentData()
            self.load_user_profile_data(self.current_selected_user, year, month)

    def confirm_admin_password(self):
        dialog = PasswordConfirmDialog(self)
        if dialog.exec():
            password = dialog.get_password()
            if self.user.check_password(password): return True
            else: QMessageBox.warning(self, "خطأ", "كلمة المرور غير صحيحة.")
        return False
    
    def load_users(self):
        self.users_table.setRowCount(0)
        users = self.db_session.query(User).all()
        for row, user in enumerate(users):
            self.users_table.insertRow(row)
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.username))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.role))
            self.add_user_action_buttons(row, user)

    def add_user_action_buttons(self, row, user):
        buttons_widget = QWidget(); layout = QHBoxLayout(buttons_widget)
        layout.setContentsMargins(5, 0, 5, 0); layout.setSpacing(5)
        edit_btn = QPushButton("تعديل"); edit_btn.setProperty("class", "ActionButton EditButton"); edit_btn.clicked.connect(lambda _, u=user: self.handle_edit_user(u))
        delete_btn = QPushButton("حذف"); delete_btn.setProperty("class", "ActionButton DeleteButton"); delete_btn.clicked.connect(lambda _, u=user: self.handle_delete_user(u))
        if user.role == 'admin': edit_btn.setEnabled(False); delete_btn.setEnabled(False)
        layout.addWidget(edit_btn); layout.addWidget(delete_btn); self.users_table.setCellWidget(row, 3, buttons_widget)

    def handle_edit_user(self, user_to_edit: User):
        dialog = UserDialog(self, user=user_to_edit)
        if dialog.exec():
            data = dialog.get_data()
            if data and self.db_session.query(User).filter(User.username == data["username"], User.id != user_to_edit.id).first():
                QMessageBox.warning(self, "خطأ", "اسم المستخدم هذا موجود بالفعل."); return
            try:
                user_to_edit.username = data["username"]
                if data["password"]: user_to_edit.set_password(data["password"])
                self.db_session.commit(); QMessageBox.information(self, "نجاح", f"تم تعديل بيانات {data['username']} بنجاح.")
                self.load_users(); self.populate_user_list()
            except Exception as e: self.db_session.rollback(); QMessageBox.critical(self, "خطأ", f"فشل تعديل المستخدم: {e}")

    def handle_delete_user(self, user_to_delete: User):
        reply = QMessageBox.question(self, 'تأكيد الحذف', f"هل أنت متأكد من حذف '{user_to_delete.username}'؟\nسيتم حذف جميع جلساته.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_session.delete(user_to_delete); self.db_session.commit(); QMessageBox.information(self, "نجاح", "تم حذف العامل بنجاح.")
                self.load_users(); self.populate_user_list()
            except Exception as e: self.db_session.rollback(); QMessageBox.critical(self, "خطأ", f"فشل حذف المستخدم: {e}")

    def add_new_user(self):
        dialog = UserDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data and self.db_session.query(User).filter_by(username=data["username"]).first():
                QMessageBox.warning(self, "خطأ", "اسم المستخدم هذا موجود بالفعل."); return
            try:
                new_user = User(username=data["username"], role='user'); new_user.set_password(data["password"])
                self.db_session.add(new_user); self.db_session.commit(); QMessageBox.information(self, "نجاح", f"تمت إضافة {data['username']} بنجاح.")
                self.load_users(); self.populate_user_list()
            except Exception as e: self.db_session.rollback(); QMessageBox.critical(self, "خطأ", f"فشل في إضافة المستخدم: {e}")
            if not data: QMessageBox.warning(self, "خطأ", "الرجاء إدخال اسم مستخدم وكلمة مرور.")
    
    def load_sessions_report(self):
        query = self.db_session.query(CashSession)
        
        selected_user_id = self.report_user_filter.currentData()
        if selected_user_id and selected_user_id > 0:
            query = query.filter(CashSession.user_id == selected_user_id)

        start_date = self.report_date_start.date().toPyDate()
        end_date = self.report_date_end.date().toPyDate()
        query = query.filter(
            func.date(CashSession.start_time) >= start_date,
            func.date(CashSession.start_time) <= end_date
        )

        sessions = query.order_by(CashSession.start_time.desc()).all()
        
        self.reports_table.setRowCount(0)
        for row, session in enumerate(sessions):
            self.reports_table.insertRow(row)
            username = session.user.username if session.user else "(مستخدم محذوف)"
            username_item = QTableWidgetItem(username);
            if not session.user: username_item.setForeground(QColor("#6c757d"))
            
            # -- تعديل --: حساب الفرق النقدي والفليكسي المستهلك
            diff_cash = session.net_cash_difference
            diff_cash_item = QTableWidgetItem(f"{diff_cash:+,.2f}")
            if diff_cash < 0: diff_cash_item.setForeground(QColor("#dc3545"))
            elif diff_cash > 0: diff_cash_item.setForeground(QColor("#198754"))
            
            flexi_consumed_value = session.flexi_consumed
            flexi_consumed_item = QTableWidgetItem(f"{flexi_consumed_value:,.2f}")
            
            self.reports_table.setItem(row, 0, username_item)
            self.reports_table.setItem(row, 1, QTableWidgetItem(session.start_time.strftime("%Y-%m-%d %H:%M")))
            self.reports_table.setItem(row, 2, QTableWidgetItem(session.end_time.strftime("%Y-%m-%d %H:%M") if session.end_time else "N/A"))
            self.reports_table.setItem(row, 3, QTableWidgetItem(f"{session.start_balance:,.2f}"))
            self.reports_table.setItem(row, 4, QTableWidgetItem(f"{session.end_balance:,.2f}" if session.end_balance is not None else "N/A"))
            self.reports_table.setItem(row, 5, diff_cash_item)
            self.reports_table.setItem(row, 6, QTableWidgetItem(f"{session.start_flexi:,.2f}" if session.start_flexi is not None else "N/A"))
            self.reports_table.setItem(row, 7, QTableWidgetItem(f"{session.total_flexi_additions:,.2f}"))
            self.reports_table.setItem(row, 8, QTableWidgetItem(f"{session.end_flexi:,.2f}" if session.end_flexi is not None else "N/A"))
            self.reports_table.setItem(row, 9, QTableWidgetItem("مغلقة" if session.status == 'closed' else "مفتوحة"))
            self.add_session_action_buttons(row, session, self.reports_table)
        self.toggle_timestamp_visibility(self.show_timestamps)

    def add_user_session_actions(self, row, session):
        self.add_session_action_buttons(row, session, self.user_sessions_table, has_details=True)

    def add_session_action_buttons(self, row, session, table_widget, has_details=False):
        buttons_widget = QWidget(); layout = QHBoxLayout(buttons_widget)
        layout.setContentsMargins(5, 0, 5, 0); layout.setSpacing(5)
        if has_details:
            details_btn = QPushButton("تفاصيل"); details_btn.setProperty("class", "ActionButton DetailsButton"); details_btn.clicked.connect(lambda _, s=session.id: self.show_session_details(s))
            layout.addWidget(details_btn)
        edit_btn = QPushButton("تعديل"); edit_btn.setProperty("class", "ActionButton EditButton"); edit_btn.clicked.connect(lambda _, s=session: self.handle_edit_session(s))
        delete_btn = QPushButton("حذف"); delete_btn.setProperty("class", "ActionButton DeleteButton"); delete_btn.clicked.connect(lambda _, s=session: self.handle_delete_session(s))
        if not session.user: edit_btn.setEnabled(False); delete_btn.setEnabled(False)
        layout.addWidget(edit_btn); layout.addWidget(delete_btn)
        table_widget.setCellWidget(row, table_widget.columnCount() - 1, buttons_widget)

    def show_session_details(self, session_id):
        dialog = SessionDetailsDialog(session_id, self)
        dialog.exec()
        self.update_profile_view() # Refresh data after dialog closes

    def handle_edit_session(self, session_to_edit: CashSession):
        if self.confirm_admin_password():
            dialog = EditSessionDialog(session_to_edit, self)
            if dialog.exec():
                data = dialog.get_data()
                if data is not None:
                    session_to_edit.start_balance = data['start_balance']
                    session_to_edit.end_balance = data['end_balance']
                    session_to_edit.start_flexi = data['start_flexi']
                    session_to_edit.end_flexi = data['end_flexi']
                    self.db_session.commit(); QMessageBox.information(self, "نجاح", "تم تعديل الجلسة بنجاح.")
                    self.load_sessions_report(); self.update_profile_view()
                else: QMessageBox.warning(self, "خطأ", "الرجاء إدخال قيم صحيحة.")

    def handle_delete_session(self, session_to_delete: CashSession):
        if self.confirm_admin_password():
            reply = QMessageBox.question(self, 'تأكيد الحذف', "هل أنت متأكد من حذف هذه الجلسة؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db_session.delete(session_to_delete); self.db_session.commit(); QMessageBox.information(self, "نجاح", "تم حذف الجلسة بنجاح.")
                self.load_sessions_report(); self.update_profile_view()

    def closeEvent(self, event):
        self.db_session.close(); event.accept()

if __name__ == '__main__':
    init_db()
    app = QApplication(sys.argv)
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == 'admin').first()
    db.close()
    if admin_user:
        admin_win = AdminDashboard(user=admin_user)
        admin_win.show()
        sys.exit(app.exec())
    else:
        print("Could not find admin user to run the test.")
