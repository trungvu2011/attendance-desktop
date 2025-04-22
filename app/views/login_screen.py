from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QFrame, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFont

class LoginScreen(QWidget):
    # Signal emitted when login is successful
    login_successful = pyqtSignal()
    
    def __init__(self, auth_controller):
        super().__init__()
        self.auth_controller = auth_controller
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
        login_layout.addSpacing(20)
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
        
        if not email or not password:
            QMessageBox.warning(self, "Lỗi đăng nhập", "Vui lòng nhập đầy đủ email và mật khẩu.")
            return
        
        # For demo purposes, accept any login (comment out in production)
        # This allows testing the application without a backend server
        if self.auth_controller.login(email, password):
            self.login_successful.emit()
        else:
            # Use hardcoded admin credentials for testing
            if email == "admin@example.com" and password == "admin":
                from app.models.user import User
                # Create mock admin user
                user = User(
                    user_id=1,
                    name="Admin User",
                    email="admin@example.com",
                    birth_date="1990-01-01",
                    citizen_id="123456789012",
                    role="ADMIN"
                )
                self.auth_controller.current_user = user
                self.login_successful.emit()
            elif email == "user@example.com" and password == "user":
                from app.models.user import User
                # Create mock candidate user
                user = User(
                    user_id=2,
                    name="Test User",
                    email="user@example.com",
                    birth_date="1995-05-05",
                    citizen_id="987654321098",
                    role="CANDIDATE"
                )
                self.auth_controller.current_user = user
                self.login_successful.emit()
            else:
                QMessageBox.warning(self, "Lỗi đăng nhập", "Email hoặc mật khẩu không đúng.")
    
    def show_forgot_password(self):
        QMessageBox.information(self, "Quên mật khẩu", "Chức năng đặt lại mật khẩu chưa được triển khai trong phiên bản demo này.")