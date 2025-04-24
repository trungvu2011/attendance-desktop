from PyQt5.QtWidgets import (QMainWindow, QStackedWidget, QMessageBox, QAction,
                               QStatusBar, QLabel, QToolBar, QStyle, QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont
from app.views.login_screen import LoginScreen
from app.views.dashboard_screen import DashboardScreen
from app.controllers.user_controller import UserController
from app.controllers.exam_controller import ExamController
from app.controllers.attendance_controller import AttendanceController
from app.assets.style import STYLE

class MainWindow(QMainWindow):
    def __init__(self, auth_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.user_controller = UserController()
        self.exam_controller = ExamController()
        self.attendance_controller = AttendanceController()
        
        # Áp dụng stylesheet hiện đại
        self.setStyleSheet(STYLE)
        
        self.init_ui()
        
        # Đã loại bỏ việc gọi phương thức attempt_auto_login() ở đây
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Hệ thống Quản lý Điểm danh")
        self.resize(1200, 800)
        
        # Create stacked widget to manage different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create login screen - truyền thêm user_controller để sử dụng chức năng đăng ký
        self.login_screen = LoginScreen(self.auth_controller, self.user_controller)
        self.login_screen.login_successful.connect(self.show_dashboard)
        self.stacked_widget.addWidget(self.login_screen)
        
        # Create dashboard screen (will be initialized when user logs in)
        self.dashboard_screen = None
        
        # Create menu bar and toolbar
        self.create_menu_bar()
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Sẵn sàng")
        self.status_bar.addWidget(self.status_label)
        
        # Start with login screen
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def attempt_auto_login(self):
        """Thử tự động đăng nhập nếu có token hợp lệ và thông tin người dùng đã lưu"""
        if self.auth_controller.is_logged_in():
            # Nếu đã có token hợp lệ và thông tin người dùng, tự động chuyển đến dashboard
            self.show_dashboard()
            self.status_label.setText("Đã đăng nhập tự động từ phiên làm việc trước")
    
    def create_menu_bar(self):
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&Tệp")
        
        # Logout action
        self.logout_action = QAction("Đăng xuất", self)
        self.logout_action.setShortcut("Ctrl+L")
        self.logout_action.triggered.connect(self.logout)
        self.logout_action.setEnabled(False)
        file_menu.addAction(self.logout_action)
        
        # Exit action
        exit_action = QAction("Thoát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&Xem")
        
        # Fullscreen action
        fullscreen_action = QAction("Toàn màn hình", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.toggled.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Trợ giúp")
        
        # About action
        about_action = QAction("Giới thiệu", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))  # Thay đổi từ Qt.QSize thành QSize
        self.addToolBar(toolbar)
        
        # User icon - shows current user status
        self.user_action = QAction(self.style().standardIcon(QStyle.SP_DialogApplyButton), "Đăng nhập", self)
        self.user_action.triggered.connect(self.show_user_info)
        toolbar.addAction(self.user_action)
        
        # Add spacer 
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # Refresh action
        refresh_action = QAction(self.style().standardIcon(QStyle.SP_BrowserReload), "Làm mới", self)
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
    
    def show_dashboard(self):
        # Always create a new dashboard screen when someone logs in
        # to ensure all components are updated with the new user's data
        if self.dashboard_screen:
            self.stacked_widget.removeWidget(self.dashboard_screen)
            self.dashboard_screen.deleteLater()
            
        # Create a fresh dashboard with the current controllers
        self.dashboard_screen = DashboardScreen(
            self.auth_controller,
            self.user_controller,
            self.exam_controller, 
            self.attendance_controller
        )
        self.stacked_widget.addWidget(self.dashboard_screen)
        
        # Switch to dashboard
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)
        
        # Update window title with user role
        user = self.auth_controller.get_current_user()
        role_display = "Quản trị viên" if user.role == "ADMIN" else "Thí sinh"
        self.setWindowTitle(f"Hệ thống Quản lý Điểm danh - {role_display}: {user.name}")
        
        # Enable logout button
        self.logout_action.setEnabled(True)
        
        # Update user action in toolbar
        self.user_action.setText(f"Người dùng: {user.name}")
        self.user_action.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        
        # Update status bar
        self.status_label.setText(f"Đã đăng nhập với tài khoản: {user.email}")
    
    def logout(self):
        if self.auth_controller.is_logged_in():
            reply = QMessageBox.question(
                self, 'Xác nhận đăng xuất', 
                'Bạn có chắc chắn muốn đăng xuất?',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Đăng xuất từ auth_controller
                self.auth_controller.logout()
                
                # Đảm bảo ApiService cũng được khởi tạo lại
                from app.utils.api_service import ApiService
                ApiService._instance = None
                
                # Tạo lại các controller để đảm bảo không còn dữ liệu cũ
                self.auth_controller = type(self.auth_controller)()  # Tạo lại instance từ class hiện tại
                self.user_controller = UserController()
                self.exam_controller = ExamController()
                self.attendance_controller = AttendanceController()
                
                # Tạo lại login_screen để sử dụng controller mới
                self.login_screen = LoginScreen(self.auth_controller, self.user_controller)
                self.login_screen.login_successful.connect(self.show_dashboard)
                
                # Xóa dashboard_screen hiện tại để tạo mới khi đăng nhập lại
                if self.dashboard_screen:
                    self.stacked_widget.removeWidget(self.dashboard_screen)
                    self.dashboard_screen.deleteLater()
                    self.dashboard_screen = None
                
                # Thêm login_screen mới vào stacked_widget
                self.stacked_widget.removeWidget(self.login_screen)
                self.stacked_widget.addWidget(self.login_screen)
                self.stacked_widget.setCurrentWidget(self.login_screen)
                
                # Cập nhật UI
                self.setWindowTitle("Hệ thống Quản lý Điểm danh")
                self.logout_action.setEnabled(False)
                self.user_action.setText("Đăng nhập")
                self.user_action.setIcon(self.style().standardIcon(QStyle.SP_DialogHelpButton))
                self.status_label.setText("Đã đăng xuất")
    
    def show_about(self):
        QMessageBox.about(
            self, 
            "Giới thiệu Hệ thống Quản lý Điểm danh",
            "Hệ thống Quản lý Điểm danh\n"
            "Phiên bản 1.0\n\n"
            "Phát triển để quản lý điểm danh cho các kỳ thi.\n"
            "© 2025 All Rights Reserved."
        )
    
    def show_user_info(self):
        if self.auth_controller.is_logged_in():
            # Thử lấy thông tin profile từ API trước
            user_profile = self.user_controller.get_current_user_profile()
            
            # Nếu API không trả về kết quả, sử dụng thông tin người dùng đã lưu
            if not user_profile:
                user_profile = self.auth_controller.get_current_user()
            
            if user_profile:
                QMessageBox.information(
                    self,
                    "Thông tin người dùng",
                    f"Tên: {user_profile.name}\n"
                    f"Email: {user_profile.email}\n"
                    f"Vai trò: {user_profile.role}\n"
                    f"CCCD: {user_profile.citizen_id}\n"
                    f"Ngày sinh: {user_profile.birth_date or 'Chưa cập nhật'}"
                )
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể lấy thông tin người dùng.")
    
    def refresh_data(self):
        if self.dashboard_screen and self.stacked_widget.currentWidget() == self.dashboard_screen:
            self.dashboard_screen.load_data()
            self.status_label.setText("Đã làm mới dữ liệu thành công")
    
    def toggle_fullscreen(self, checked):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Xác nhận thoát',
            'Bạn có chắc chắn muốn thoát khỏi ứng dụng?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()