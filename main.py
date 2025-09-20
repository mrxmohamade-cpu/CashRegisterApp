import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QCheckBox,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import Qt

# استيراد النماذج والمكونات الضرورية
from dashboard_ui import UserDashboard
from admin_dashboard_ui import AdminDashboard
from database_setup import (User, SessionLocal, engine, init_db, 
                              get_db_version, run_migrations, CURRENT_DB_VERSION, DB_FILENAME)

# --- نافذة تسجيل الدخول ---
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - نظام إدارة الصندوق")
        self.setMinimumSize(960, 580)
        self.setup_ui()
        self.apply_styles()
        self.set_app_icon()

    def set_app_icon(self):
        """
        تعيين أيقونة للتطبيق.
        """
        # مسار الأيقونة (يفترض وجودها في نفس مجلد main.py)
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if not os.path.exists(icon_path):
            # fallback to .png if .ico doesn't exist
            icon_path = os.path.join(os.path.dirname(__file__), "app_icon.png")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("Warning: Icon file not found.")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.main_layout = main_layout

        # --- لوحة التعريف ---
        brand_frame = QFrame()
        brand_frame.setObjectName("BrandFrame")
        brand_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.brand_frame = brand_frame

        brand_layout = QVBoxLayout(brand_frame)
        brand_layout.setContentsMargins(60, 80, 60, 60)
        brand_layout.setSpacing(24)
        self.brand_layout = brand_layout

        brand_badge = QLabel("نسخة خرافية")
        brand_badge.setObjectName("BrandBadge")
        brand_badge.setAlignment(Qt.AlignmentFlag.AlignLeft)

        brand_title = QLabel("إدارة الصندوق بواجهة مستقبلية")
        brand_title.setObjectName("BrandTitle")
        brand_title.setWordWrap(True)

        brand_subtitle = QLabel(
            "راقب جلساتك، المصاريف، والفليكسي بلمسة واحدة.\n"
            "لوحة القيادة الذكية تمنحك الوضوح في كل لحظة."
        )
        brand_subtitle.setObjectName("BrandSubtitle")
        brand_subtitle.setWordWrap(True)

        brand_points = QLabel(
            "• إحصائيات لحظية بتصميم أنيق\n"
            "• إدارة الجلسات و الفليكسي بسهولة\n"
            "• تجربة سلسة تدعم العمل الليلي والنهاري"
        )
        brand_points.setObjectName("BrandPoints")
        brand_points.setWordWrap(True)

        brand_footer = QLabel("حقوق النشر © 2024 - فريق التطوير")
        brand_footer.setObjectName("BrandFooter")
        brand_footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        brand_layout.addWidget(brand_badge)
        brand_layout.addStretch(1)
        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_subtitle)
        brand_layout.addSpacing(12)
        brand_layout.addWidget(brand_points)
        brand_layout.addStretch(2)
        brand_layout.addWidget(brand_footer)

        # --- بطاقة تسجيل الدخول ---
        login_side = QWidget()
        login_side_layout = QVBoxLayout(login_side)
        login_side_layout.setContentsMargins(0, 0, 0, 0)
        login_side_layout.setSpacing(0)
        login_side_layout.addStretch()
        self.login_side_layout = login_side_layout

        login_frame = QFrame()
        login_frame.setObjectName("LoginFrame")
        login_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._login_frame_min_width = 360
        self._login_frame_max_width = 520
        login_frame.setMinimumWidth(self._login_frame_min_width)
        login_frame.setMaximumWidth(self._login_frame_max_width)
        self.login_frame = login_frame

        card_layout = QVBoxLayout(login_frame)
        card_layout.setContentsMargins(40, 45, 40, 45)
        card_layout.setSpacing(20)

        card_header = QLabel("مرحباً بعودتك")
        card_header.setObjectName("CardTitle")
        card_header.setAlignment(Qt.AlignmentFlag.AlignLeft)

        card_subtitle = QLabel("سجل الدخول لمتابعة صندوقك الذكي")
        card_subtitle.setObjectName("CardSubtitle")
        card_subtitle.setWordWrap(True)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.setObjectName("LoginField")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("LoginField")

        self.remember_checkbox = QCheckBox("تذكرني لسبعة أيام")
        self.remember_checkbox.setObjectName("RememberCheck")

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setVisible(False)

        self.login_button = QPushButton("دخول")
        self.login_button.setObjectName("LoginButton")

        self.secondary_button = QPushButton("هل نسيت كلمة المرور؟")
        self.secondary_button.setObjectName("LinkButton")
        self.secondary_button.setFlat(True)
        self.secondary_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.version_badge = QLabel("واجهة النسخة الخرافية 2024")
        self.version_badge.setObjectName("VersionBadge")
        self.version_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(card_header)
        card_layout.addWidget(card_subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.remember_checkbox)
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.login_button)
        card_layout.addWidget(self.secondary_button, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addStretch()
        card_layout.addWidget(self.version_badge, alignment=Qt.AlignmentFlag.AlignCenter)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 20)
        shadow.setColor(QColor(15, 23, 42, 80))
        login_frame.setGraphicsEffect(shadow)

        login_side_layout.addWidget(login_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        login_side_layout.addStretch()

        main_layout.addWidget(brand_frame, 7)
        main_layout.addWidget(login_side, 5)

        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)

        # Ensure layout adapts to the initial size
        self.update_login_layout(self.size())

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            #BrandFrame {
                background-color: #0f172a;
                background-image: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #172554, stop:0.5 #1d4ed8, stop:1 #1e1b4b);
                color: #e2e8f0;
            }
            #BrandBadge {
                padding: 6px 14px;
                border-radius: 16px;
                background-color: rgba(226, 232, 240, 0.2);
                color: #f8fafc;
                font-size: 10.5pt;
                font-weight: bold;
                letter-spacing: 1px;
            }
            #BrandTitle {
                font-size: 28pt;
                font-weight: 800;
                line-height: 1.2;
                color: #f8fafc;
            }
            #BrandSubtitle {
                font-size: 13pt;
                color: rgba(248, 250, 252, 0.94);
            }
            #BrandPoints {
                font-size: 11.5pt;
                color: rgba(241, 245, 249, 0.95);
            }
            #BrandFooter {
                font-size: 9pt;
                color: rgba(226, 232, 240, 0.8);
            }
            #LoginFrame {
                background-color: #ffffff;
                border-radius: 24px;
            }
            #CardTitle {
                font-size: 20pt;
                font-weight: 700;
                color: #0f172a;
            }
            #CardSubtitle {
                font-size: 11.5pt;
                color: #64748b;
            }
            QLineEdit#LoginField {
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 14px 16px;
                font-size: 11.5pt;
                background-color: #f8fafc;
                color: #0f172a;
            }
            QLineEdit#LoginField:focus {
                border: 2px solid #2563eb;
                padding: 13px 15px;
                background-color: #ffffff;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
            #RememberCheck {
                color: #475569;
                font-size: 10.5pt;
            }
            #RememberCheck::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #cbd5f5;
                border-radius: 6px;
                background: #f8fafc;
            }
            #RememberCheck::indicator:checked {
                border: 2px solid #2563eb;
                background-color: #2563eb;
            }
            #StatusLabel {
                color: #ef4444;
                font-size: 10pt;
                min-height: 18px;
            }
            #LoginButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1d4ed8, stop:1 #2563eb);
                color: #ffffff;
                border: none;
                padding: 14px;
                font-size: 12pt;
                font-weight: 700;
                border-radius: 16px;
                min-height: 50px;
                letter-spacing: 0.4px;
            }
            #LoginButton:hover {
                background-color: #1e3a8a;
            }
            #LoginButton:pressed {
                background-color: #1d4ed8;
            }
            #LoginButton:disabled {
                background-color: rgba(148, 163, 184, 0.6);
                color: rgba(248, 250, 252, 0.7);
            }
            #LinkButton {
                color: #2563eb;
                font-weight: 600;
                border: none;
                font-size: 10.5pt;
            }
            #LinkButton:hover {
                color: #1d4ed8;
                text-decoration: underline;
            }
            #VersionBadge {
                background-color: rgba(37, 99, 235, 0.08);
                color: #1d4ed8;
                padding: 8px 18px;
                border-radius: 18px;
                font-size: 10pt;
                font-weight: 600;
            }

            /* Style for QMessageBox */
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #0f172a;
                font-size: 11pt;
            }
            QMessageBox QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                border-radius: 10px;
                min-width: 90px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_login_layout(event.size())

    def update_login_layout(self, size):
        available_width = size.width()
        if available_width <= 0:
            available_width = self.width()

        if available_width < 920:
            self.main_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self.main_layout.setSpacing(24)
            self.brand_layout.setContentsMargins(28, 32, 28, 24)
            self.brand_layout.setSpacing(18)
            self.brand_layout.setStretch(1, 0)
            self.brand_layout.setStretch(6, 0)
            self.login_side_layout.setContentsMargins(0, 0, 0, 32)
            max_width = max(
                self._login_frame_min_width,
                min(self._login_frame_max_width, available_width - 80)
            )
            self.login_frame.setMaximumWidth(max_width)
            self.login_frame.setMinimumWidth(self._login_frame_min_width)
        else:
            self.main_layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.main_layout.setSpacing(0)
            self.brand_layout.setContentsMargins(60, 80, 60, 60)
            self.brand_layout.setSpacing(24)
            self.brand_layout.setStretch(1, 1)
            self.brand_layout.setStretch(6, 2)
            self.login_side_layout.setContentsMargins(0, 0, 0, 0)
            self.login_frame.setMinimumWidth(self._login_frame_min_width)
            self.login_frame.setMaximumWidth(self._login_frame_max_width)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        self.status_label.setVisible(False)
        self.status_label.setText("")

        db = SessionLocal()
        user = db.query(User).filter_by(username=username).first()
        db.close()

        if user and user.check_password(password):
            self.open_dashboard(user)
        else:
            self.status_label.setText("اسم المستخدم أو كلمة المرور غير صحيحة.")
            self.status_label.setVisible(True)
            QMessageBox.warning(self, "خطأ في الدخول", "اسم المستخدم أو كلمة المرور غير صحيحة.")

    def open_dashboard(self, user):
        if user.role == 'admin':
            self.dashboard_window = AdminDashboard(user=user)
        else:
            self.dashboard_window = UserDashboard(user=user)
        self.dashboard_window.show()
        self.close()

def check_database_migration():
    """
    يفحص ويعالج ترقية قاعدة البيانات قبل تشغيل أي واجهة.
    """
    current_version = get_db_version(engine)
    if current_version < CURRENT_DB_VERSION:
        success, message = run_migrations(engine)
        if not success:
            QMessageBox.critical(None, "فشل التحديث", f"فشل تحديث قاعدة البيانات.\nالخطأ: {message}")
            return False
        else:
            QMessageBox.information(None, "نجاح", message)
            return True
    return True

def main():
    # التحقق من وجود ملف قاعدة البيانات قبل الترحيل
    db_exists = os.path.exists(DB_FILENAME)

    if not db_exists:
        init_db()
        QMessageBox.information(None, "نجاح", "تم إنشاء قاعدة البيانات بنجاح!")

    if not check_database_migration():
        sys.exit()
        
    login_window = LoginWindow()
    login_window.show()
    
    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Closing application.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()
