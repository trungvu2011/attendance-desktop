from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTabWidget, QStackedWidget,
                               QFrame, QSplitter, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

from app.views.user_management import UserManagementPanel
from app.views.exam_management import ExamManagementPanel
from app.views.attendance_panel import AttendancePanel
from app.views.monitoring_panel import MonitoringPanel
from app.views.candidate_exam_panel import CandidateExamPanel
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
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header-frame")
        self.header_frame.setStyleSheet("""
            #header-frame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        header_layout = self.create_header()
        self.header_frame.setLayout(header_layout)
        main_layout.addWidget(self.header_frame)
        
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
        
        role_label = QLabel(f"Vai trò: Thí sinh | Ngày: {today}")
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
        
        # Kiểm tra vai trò người dùng để chỉ gọi API cần thiết
        is_admin = self.auth_controller.is_admin()
        
        # Lấy số liệu API dựa trên vai trò
        if is_admin:
            # Admin có quyền xem tất cả dữ liệu
            users_count = len(self.user_controller.get_all_users())
            exams_count = len(self.exam_controller.get_all_exams())
            
            try:
                attendances_count = len(self.attendance_controller.get_all_attendance())
            except:
                attendances_count = 0
        else:
            # Candidate chỉ cần API liên quan đến kỳ thi của họ
            users_count = 1  # Chỉ họ
            exams_count = len(self.exam_controller.get_my_exams())
            
            # Candidate không cần thống kê điểm danh tổng thể
            attendances_count = 0
        
        # Users stat
        users_box = QFrame()
        users_box.setObjectName("users-box")
        users_box.setProperty("class", "stat-box")
        users_layout = QVBoxLayout(users_box)
        
        if is_admin:
            users_value = QLabel(str(users_count))
            users_label = QLabel("Người dùng")
        else:
            # Đối với candidate, hiển thị thông tin cá nhân
            users_value = QLabel("1")
            users_label = QLabel("Tài khoản")
        
        users_value.setProperty("class", "stat-value")
        users_value.setAlignment(Qt.AlignCenter)
        users_label.setProperty("class", "stat-label")
        users_label.setAlignment(Qt.AlignCenter)
        
        users_layout.addWidget(users_value)
        users_layout.addWidget(users_label)
        
        # Exams stat
        exams_box = QFrame()
        exams_box.setObjectName("exams-box")
        exams_box.setProperty("class", "stat-box")
        exams_layout = QVBoxLayout(exams_box)
        
        exams_value = QLabel(str(exams_count))
        exams_value.setProperty("class", "stat-value")
        exams_value.setAlignment(Qt.AlignCenter)
        
        if is_admin:
            exams_label = QLabel("Kỳ thi")
        else:
            exams_label = QLabel("Kỳ thi của tôi")
        
        exams_label.setProperty("class", "stat-label")
        exams_label.setAlignment(Qt.AlignCenter)
        
        exams_layout.addWidget(exams_value)
        exams_layout.addWidget(exams_label)
        
        # Attendance stat
        attendance_box = QFrame()
        attendance_box.setObjectName("attendance-box")
        attendance_box.setProperty("class", "stat-box")
        attendance_layout = QVBoxLayout(attendance_box)
        
        if is_admin:
            attendance_value = QLabel(str(attendances_count))
            attendance_label = QLabel("Điểm danh")
        else:
            # Chưa có API để lấy số lượng điểm danh của candidate
            attendance_value = QLabel("--")
            attendance_label = QLabel("Điểm danh của tôi")
        
        attendance_value.setProperty("class", "stat-value")
        attendance_value.setAlignment(Qt.AlignCenter)
        attendance_label.setProperty("class", "stat-label")
        attendance_label.setAlignment(Qt.AlignCenter)
        
        attendance_layout.addWidget(attendance_value)
        attendance_layout.addWidget(attendance_label)
        
        # Monitoring stat - chỉ hiển thị cho admin
        monitoring_box = QFrame()
        monitoring_box.setObjectName("monitoring-box")
        monitoring_box.setProperty("class", "stat-box")
        monitoring_layout = QVBoxLayout(monitoring_box)
        
        monitoring_value = QLabel("--")
        monitoring_value.setProperty("class", "stat-value")
        monitoring_value.setAlignment(Qt.AlignCenter)
        
        if is_admin:
            monitoring_label = QLabel("Sự kiện")
        else:
            monitoring_label = QLabel("Thông báo")
        
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
        user = self.auth_controller.get_current_user()
        
        if is_admin:
            # Admin panels với đầy đủ quyền quản trị
            # User Management
            user_panel = UserManagementPanel(self.user_controller, is_admin=True)
            self.tab_widget.addTab(user_panel, "Quản lý người dùng")
            
            # Exam Management
            exam_panel = ExamManagementPanel(self.exam_controller)
            self.tab_widget.addTab(exam_panel, "Quản lý kỳ thi")
            
            # Attendance Management
            attendance_panel = AttendancePanel(
                self.attendance_controller, 
                self.user_controller,
                self.exam_controller,
                is_admin=True
            )
            self.tab_widget.addTab(attendance_panel, "Quản lý điểm danh")
            
            # Monitoring - Chỉ admin mới được quyền giám sát
            monitoring_panel = MonitoringPanel()
            self.tab_widget.addTab(monitoring_panel, "Giám sát hệ thống")
            
            # Thêm tab thông tin cá nhân cho admin
            profile_panel = UserManagementPanel(
                self.user_controller, 
                is_admin=False, 
                user_id=user.user_id,
                is_personal_profile=True  # Thêm tham số này để panel biết gọi API profile cho admin
            )
            self.tab_widget.addTab(profile_panel, "Hồ sơ của tôi")
        else:
            # Candidate panels - Giới hạn quyền
            # My Exams - Sử dụng CandidateExamPanel mới để chỉ gọi API my-exams
            my_exams_panel = CandidateExamPanel(self.exam_controller)
            self.tab_widget.addTab(my_exams_panel, "Kỳ thi của tôi")
            
            # Attendance Panel - Vẫn giữ để candidate có thể xem thông tin điểm danh
            # Truyền tham số is_candidate=True để panel biết chỉ gọi API liên quan đến candidate
            attendance_panel = AttendancePanel(
                self.attendance_controller, 
                self.user_controller,
                self.exam_controller,
                is_admin=False,
                is_candidate=True  # Thêm tham số này để panel biết chỉ gọi API cho candidate
            )
            self.tab_widget.addTab(attendance_panel, "Điểm danh của tôi")
            
            # My Profile - Chỉ cần xem thông tin cá nhân
            profile_panel = UserManagementPanel(
                self.user_controller, 
                is_admin=False, 
                user_id=user.user_id,
                is_personal_profile=True  # Thêm tham số này để panel biết chỉ gọi API cho profile cá nhân
            )
            self.tab_widget.addTab(profile_panel, "Hồ sơ của tôi")
    
    def load_data(self):
        # Refresh the header with current user info
        self.refresh_header()
        
        # Update data in all tabs
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'load_data'):
                widget.load_data()
    
    def refresh_header(self):
        # Remove the old header
        if hasattr(self, 'header_frame'):
            old_layout = self.layout()
            old_layout.removeWidget(self.header_frame)
            self.header_frame.deleteLater()
        
        # Create a new header with updated user info
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header-frame")
        self.header_frame.setStyleSheet("""
            #header-frame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        header_layout = self.create_header()
        self.header_frame.setLayout(header_layout)
        
        # Add it back to the main layout at the top
        main_layout = self.layout()
        main_layout.insertWidget(0, self.header_frame)