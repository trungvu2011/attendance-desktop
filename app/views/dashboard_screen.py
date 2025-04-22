from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTabWidget, QStackedWidget,
                               QFrame, QSplitter, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

from app.views.user_management import UserManagementPanel
from app.views.exam_management import ExamManagementPanel
from app.views.attendance_panel import AttendancePanel
from app.views.monitoring_panel import MonitoringPanel
from config.config import Config

class DashboardScreen(QWidget):
    def __init__(self, auth_controller, user_controller, exam_controller, attendance_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.user_controller = user_controller
        self.exam_controller = exam_controller
        self.attendance_controller = attendance_controller
        
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("header-frame")
        header_frame.setStyleSheet("""
            #header-frame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        header_layout = self.create_header()
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)
        
        # Add dashboard summary for quick stats
        summary_frame = self.create_summary_dashboard()
        main_layout.addWidget(summary_frame)
        
        # Content section - use tab widget for different panels
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)  # Cleaner look
        
        # Create a container frame for the tab widget
        content_frame = QFrame()
        content_frame.setObjectName("content-frame")
        content_frame.setStyleSheet("""
            #content-frame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.tab_widget)
        
        # Initialize panels based on user role
        self.initialize_panels()
        
        main_layout.addWidget(content_frame)
        
        # Set layout
        self.setLayout(main_layout)
    
    def create_header(self):
        # Create header layout
        header_layout = QHBoxLayout()
        
        # User info section
        user = self.auth_controller.get_current_user()
        
        user_info_layout = QVBoxLayout()
        
        # Welcome message
        welcome_label = QLabel(f"Xin chào, {user.name}")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a73e8;")
        
        # Role and date
        import datetime
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        
        role_label = QLabel(f"Vai trò: {user.role} | Ngày: {today}")
        role_label.setStyleSheet("font-style: italic; color: #555;")
        
        user_info_layout.addWidget(welcome_label)
        user_info_layout.addWidget(role_label)
        
        # Actions section
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Làm mới dữ liệu")
        refresh_btn.setProperty("secondary", "true")
        refresh_btn.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
        refresh_btn.clicked.connect(self.load_data)
        
        actions_layout.addStretch()
        actions_layout.addWidget(refresh_btn)
        
        # Add to header layout
        header_layout.addLayout(user_info_layout)
        header_layout.addLayout(actions_layout)
        
        return header_layout
    
    def create_summary_dashboard(self):
        # Create a dashboard summary frame with quick stats
        summary_frame = QFrame()
        summary_frame.setObjectName("summary-frame")
        summary_frame.setMaximumHeight(120)
        summary_frame.setStyleSheet("""
            #summary-frame {
                background-color: white;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            
            .stat-box {
                border-radius: 6px;
                padding: 15px;
            }
            
            #users-box {
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
            }
            
            #exams-box {
                background-color: #e8f5e9;
                border: 1px solid #c8e6c9;
            }
            
            #attendance-box {
                background-color: #fff3e0;
                border: 1px solid #ffe0b2;
            }
            
            #monitoring-box {
                background-color: #f3e5f5;
                border: 1px solid #e1bee7;
            }
            
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
            
            .stat-label {
                color: #666;
            }
        """)
        
        # Grid layout for stats
        summary_layout = QGridLayout(summary_frame)
        
        # Users stat
        users_box = QFrame()
        users_box.setObjectName("users-box")
        users_box.setProperty("class", "stat-box")
        users_layout = QVBoxLayout(users_box)
        
        users_value = QLabel("12")
        users_value.setProperty("class", "stat-value")
        users_value.setAlignment(Qt.AlignCenter)
        
        users_label = QLabel("Người dùng")
        users_label.setProperty("class", "stat-label")
        users_label.setAlignment(Qt.AlignCenter)
        
        users_layout.addWidget(users_value)
        users_layout.addWidget(users_label)
        
        # Exams stat
        exams_box = QFrame()
        exams_box.setObjectName("exams-box")
        exams_box.setProperty("class", "stat-box")
        exams_layout = QVBoxLayout(exams_box)
        
        exams_value = QLabel("8")
        exams_value.setProperty("class", "stat-value")
        exams_value.setAlignment(Qt.AlignCenter)
        
        exams_label = QLabel("Kỳ thi")
        exams_label.setProperty("class", "stat-label")
        exams_label.setAlignment(Qt.AlignCenter)
        
        exams_layout.addWidget(exams_value)
        exams_layout.addWidget(exams_label)
        
        # Attendance stat
        attendance_box = QFrame()
        attendance_box.setObjectName("attendance-box")
        attendance_box.setProperty("class", "stat-box")
        attendance_layout = QVBoxLayout(attendance_box)
        
        attendance_value = QLabel("45")
        attendance_value.setProperty("class", "stat-value")
        attendance_value.setAlignment(Qt.AlignCenter)
        
        attendance_label = QLabel("Điểm danh")
        attendance_label.setProperty("class", "stat-label")
        attendance_label.setAlignment(Qt.AlignCenter)
        
        attendance_layout.addWidget(attendance_value)
        attendance_layout.addWidget(attendance_label)
        
        # Monitoring stat
        monitoring_box = QFrame()
        monitoring_box.setObjectName("monitoring-box")
        monitoring_box.setProperty("class", "stat-box")
        monitoring_layout = QVBoxLayout(monitoring_box)
        
        monitoring_value = QLabel("20")
        monitoring_value.setProperty("class", "stat-value")
        monitoring_value.setAlignment(Qt.AlignCenter)
        
        monitoring_label = QLabel("Sự kiện")
        monitoring_label.setProperty("class", "stat-label")
        monitoring_label.setAlignment(Qt.AlignCenter)
        
        monitoring_layout.addWidget(monitoring_value)
        monitoring_layout.addWidget(monitoring_label)
        
        # Add to grid layout
        summary_layout.addWidget(users_box, 0, 0)
        summary_layout.addWidget(exams_box, 0, 1)
        summary_layout.addWidget(attendance_box, 0, 2)
        summary_layout.addWidget(monitoring_box, 0, 3)
        
        return summary_frame
    
    def initialize_panels(self):
        # Check user role
        is_admin = self.auth_controller.is_admin()
        
        if is_admin:
            # Admin panels
            # User Management
            user_panel = UserManagementPanel(self.user_controller)
            self.tab_widget.addTab(user_panel, "Quản lý người dùng")
            
            # Exam Management
            exam_panel = ExamManagementPanel(self.exam_controller)
            self.tab_widget.addTab(exam_panel, "Quản lý kỳ thi")
            
            # Attendance Management
            attendance_panel = AttendancePanel(
                self.attendance_controller, 
                self.user_controller,
                self.exam_controller
            )
            self.tab_widget.addTab(attendance_panel, "Quản lý điểm danh")
            
            # Monitoring
            monitoring_panel = MonitoringPanel()
            self.tab_widget.addTab(monitoring_panel, "Giám sát hệ thống")
        else:
            # Candidate panels
            # My Exams
            attendance_panel = AttendancePanel(
                self.attendance_controller, 
                self.user_controller,
                self.exam_controller,
                is_admin=False
            )
            self.tab_widget.addTab(attendance_panel, "Kỳ thi của tôi")
            
            # My Profile
            user = self.auth_controller.get_current_user()
            profile_panel = UserManagementPanel(
                self.user_controller, 
                is_admin=False, 
                user_id=user.user_id
            )
            self.tab_widget.addTab(profile_panel, "Hồ sơ của tôi")
    
    def load_data(self):
        # Update data in all tabs
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'load_data'):
                widget.load_data()