import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt6.QtGui import QFont, QIcon
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
        self.setMinimumSize(450, 400)
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
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # إطار لتجميع محتويات تسجيل الدخول
        login_frame = QFrame()
        login_frame.setObjectName("LoginFrame")
        login_frame.setFixedWidth(380)
        frame_layout = QVBoxLayout(login_frame)
        frame_layout.setContentsMargins(35, 35, 35, 35)
        frame_layout.setSpacing(18)
        
        title_label = QLabel("تسجيل الدخول")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_button = QPushButton("دخول")
        self.login_button.setObjectName("LoginButton")
        
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(self.username_input)
        frame_layout.addWidget(self.password_input)
        frame_layout.addSpacing(10)
        frame_layout.addWidget(self.login_button)
        
        main_layout.addWidget(login_frame)
        
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            #LoginFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
            #TitleLabel {
                font-size: 20pt;
                font-weight: bold;
                color: #f0f6fc;
                margin-bottom: 10px;
            }
            QLineEdit {
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 12px;
                font-size: 11pt;
                background-color: #0d1117;
                color: #f0f6fc;
            }
            QLineEdit::placeholder {
                color: #8b949e;
            }
            QLineEdit:focus {
                border: 2px solid #58a6ff;
            }
            #LoginButton {
                background-color: #2f81f7;
                color: white;
                border: none;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 8px;
            }
            #LoginButton:hover {
                background-color: #1f6feb;
            }
            
            /* Style for QMessageBox */
            QMessageBox {
                background-color: #161b22;
            }
            QMessageBox QLabel {
                color: #f0f6fc;
                font-size: 11pt;
            }
            QMessageBox QPushButton {
                background-color: #2f81f7;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1f6feb;
            }
        """)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        db = SessionLocal()
        user = db.query(User).filter_by(username=username).first()
        db.close()
        
        if user and user.check_password(password):
            self.open_dashboard(user)
        else:
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
