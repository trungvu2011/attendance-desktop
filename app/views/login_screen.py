from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QFrame, QCheckBox,
                              QDialog, QDateEdit, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QPixmap, QIcon, QFont
from app.models.user import User
from config.config import Config
import os

class LoginScreen(QWidget):
    # Signal emitted when login is successful
    login_successful = pyqtSignal()
    
    def __init__(self, auth_controller, user_controller=None):
        super().__init__()
        self.auth_controller = auth_controller
        self.user_controller = user_controller
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout()
        
        # Logo section (left side)
        logo_frame = QFrame()
        logo_frame.setObjectName("logo-frame")
        logo_frame.setStyleSheet("""
            #logo-frame {
                background-color: #1a73e8;
                border-radius: 10px;
                margin-right: 20px;
            }
        """)
        logo_layout = QVBoxLayout(logo_frame)
        
        # Title
        title_label = QLabel("HỆ THỐNG QUẢN LÝ ĐIỂM DANH")
        title_label.setProperty("title", "true")
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Đăng nhập để tiếp tục")
        subtitle_label.setProperty("subtitle", "true")
        subtitle_label.setStyleSheet("color: white;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        logo_layout.addStretch()
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        logo_layout.addStretch()
        
        # Login form section (right side)
        login_frame = QFrame()
        login_frame.setObjectName("login-frame")
        login_frame.setStyleSheet("""
            #login-frame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        login_layout = QVBoxLayout(login_frame)
        
        # Login header
        login_header = QLabel("Đăng nhập")
        login_header.setProperty("header", "true")
        login_header.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(login_header)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Email field
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email của bạn")
        self.email_input.setMinimumHeight(40)
        form_layout.addRow(email_label, self.email_input)
        
        # Password field
        password_label = QLabel("Mật khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu của bạn")
        self.password_input.setMinimumHeight(40)
        form_layout.addRow(password_label, self.password_input)
        
        # Remember me checkbox
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Ghi nhớ đăng nhập")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        # Forgot password link
        forgot_password_link = QLabel("<a href='#'>Quên mật khẩu?</a>")
        forgot_password_link.setTextFormat(Qt.RichText)
        forgot_password_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        forgot_password_link.linkActivated.connect(self.show_forgot_password)
        remember_layout.addWidget(forgot_password_link)
        
        # Login button
        self.login_btn = QPushButton("ĐĂNG NHẬP")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.clicked.connect(self.login)
        
        # Register section
        register_layout = QHBoxLayout()
        register_label = QLabel("Chưa có tài khoản?")
        register_layout.addWidget(register_label)
        register_layout.addStretch()
        
        # Register link
        register_link = QLabel("<a href='#'>Đăng ký ngay</a>")
        register_link.setTextFormat(Qt.RichText)
        register_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        register_link.linkActivated.connect(self.show_register_dialog)
        register_layout.addWidget(register_link)
        
        # Demo account info
        demo_label = QLabel("Tài khoản demo:")
        demo_label.setAlignment(Qt.AlignCenter)
        
        demo_admin = QLabel("Admin: admin@example.com / admin")
        demo_admin.setAlignment(Qt.AlignCenter)
        demo_admin.setStyleSheet("color: #666;")
        
        demo_user = QLabel("User: user@example.com / user")
        demo_user.setAlignment(Qt.AlignCenter)
        demo_user.setStyleSheet("color: #666;")
        
        # Add to login layout
        login_layout.addLayout(form_layout)
        login_layout.addLayout(remember_layout)
        login_layout.addWidget(self.login_btn)
        login_layout.addSpacing(10)
        login_layout.addLayout(register_layout)
        login_layout.addSpacing(10)
        login_layout.addWidget(demo_label)
        login_layout.addWidget(demo_admin)
        login_layout.addWidget(demo_user)
        login_layout.addStretch()
        
        # Add frames to main layout
        main_layout.addWidget(logo_frame, 1)
        main_layout.addWidget(login_frame, 1)
        
        # Set layout
        self.setLayout(main_layout)
        
        # Connect enter key to login
        self.email_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
    
    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        remember = self.remember_checkbox.isChecked()  # Lấy trạng thái checkbox ghi nhớ đăng nhập
        
        if not email or not password:
            QMessageBox.warning(self, "Lỗi đăng nhập", "Vui lòng nhập đầy đủ email và mật khẩu.")
            return
        
        # Bước 1: Làm sạch dữ liệu phiên đăng nhập hiện tại nếu cần
        # Chỉ xóa token nếu email đăng nhập khác với email đã lưu
        from app.utils.api_service import ApiService
        api_service = ApiService.get_instance()
        
        # Bước 2: Thực hiện đăng nhập với thông tin mới và tham số remember
        if self.auth_controller.login(email, password, remember):
            # Đăng nhập thành công, phát tín hiệu để MainWindow cập nhật giao diện
            self.login_successful.emit()
        else:
            # Sử dụng thông tin xác thực demo cho việc kiểm thử
            if email == "admin@example.com" and password == "admin":
                from app.models.user import User
                # Tạo người dùng admin mẫu
                user = User(
                    user_id=1,
                    name="Admin User",
                    email="admin@example.com",
                    birth_date="1990-01-01",
                    citizen_id="123456789012",
                    role="ADMIN"
                )
                # Đảm bảo không có dữ liệu người dùng cũ trước khi gán người dùng mới
                self.auth_controller.current_user = None
                # Gán người dùng mới
                self.auth_controller.current_user = user
                self.login_successful.emit()
            elif email == "user@example.com" and password == "user":
                from app.models.user import User
                # Tạo người dùng thí sinh mẫu
                user = User(
                    user_id=2,
                    name="Test User",
                    email="user@example.com",
                    birth_date="1995-05-05",
                    citizen_id="987654321098",
                    role="CANDIDATE"
                )
                # Đảm bảo không có dữ liệu người dùng cũ trước khi gán người dùng mới
                self.auth_controller.current_user = None
                # Gán người dùng mới
                self.auth_controller.current_user = user
                self.login_successful.emit()
            else:
                QMessageBox.warning(self, "Lỗi đăng nhập", "Email hoặc mật khẩu không đúng.")
    
    def show_forgot_password(self):
        QMessageBox.information(self, "Quên mật khẩu", "Chức năng đặt lại mật khẩu chưa được triển khai trong phiên bản demo này.")
    
    def show_register_dialog(self):
        if not self.user_controller:
            QMessageBox.warning(self, "Lỗi", "Không thể khởi tạo chức năng đăng ký.")
            return
            
        dialog = RegisterDialog(self, self.user_controller)
        dialog.exec_()


class RegisterDialog(QDialog):
    def __init__(self, parent, user_controller):
        super().__init__(parent)
        self.user_controller = user_controller
        self.setWindowTitle("Đăng ký tài khoản mới")
        self.setMinimumWidth(400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Full name
        name_label = QLabel("Họ và tên:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập họ và tên đầy đủ")
        form_layout.addRow(name_label, self.name_input)
        
        # Email
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email của bạn")
        form_layout.addRow(email_label, self.email_input)
        
        # Password
        password_label = QLabel("Mật khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        form_layout.addRow(password_label, self.password_input)
        
        # Confirm password
        confirm_label = QLabel("Xác nhận mật khẩu:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Nhập lại mật khẩu")
        form_layout.addRow(confirm_label, self.confirm_input)
        
        # Citizen ID
        citizen_label = QLabel("CCCD/CMND:")
        self.citizen_input = QLineEdit()
        self.citizen_input.setPlaceholderText("Nhập 12 số CCCD")
        form_layout.addRow(citizen_label, self.citizen_input)
        
        # Birth date
        birth_label = QLabel("Ngày sinh:")
        self.birth_input = QDateEdit()
        self.birth_input.setCalendarPopup(True)
        self.birth_input.setDate(QDate.currentDate().addYears(-20))  # Default to 20 years ago
        self.birth_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow(birth_label, self.birth_input)
        
        # Role selection
        role_label = QLabel("Vai trò:")
        self.role_combo = QComboBox()
        self.role_combo.addItem("Thí sinh", Config.ROLE_CANDIDATE)
        self.role_combo.addItem("Quản trị viên", Config.ROLE_ADMIN)
        form_layout.addRow(role_label, self.role_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.register_btn = QPushButton("Đăng ký")
        self.register_btn.clicked.connect(self.register)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.register_btn)
        
        # Add to main layout
        layout.addLayout(form_layout)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
    
    def register(self):
        # Get form data
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        citizen_id = self.citizen_input.text()
        birth_date = self.birth_input.date().toString("yyyy-MM-dd")
        role = self.role_combo.currentData()
        
        # Validate fields
        if not all([name, email, password, confirm, citizen_id]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đầy đủ tất cả các trường.")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu và xác nhận mật khẩu không khớp.")
            return
        
        if not citizen_id.isdigit() or len(citizen_id) != 12:
            QMessageBox.warning(self, "Lỗi", "CCCD/CMND phải là 12 chữ số.")
            return
        
        if '@' not in email:
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ.")
            return
        
        # Create user object
        user = User(
            name=name,
            email=email,
            password=password,
            birth_date=birth_date,
            citizen_id=citizen_id,
            role=role
        )
        
        # Call API to register user
        result = self.user_controller.register_user(user)
        if result:
            QMessageBox.information(self, "Thành công", "Đăng ký tài khoản thành công. Vui lòng đăng nhập bằng tài khoản mới.")
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể đăng ký tài khoản. Vui lòng thử lại sau hoặc liên hệ quản trị viên.")