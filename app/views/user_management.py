from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QLineEdit, QDateEdit,
                              QComboBox, QMessageBox, QFrame, QHeaderView,
                              QSplitter, QToolButton, QAction, QMenu)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon
from app.models.user import User
from config.config import Config

class UserManagementPanel(QWidget):
    def __init__(self, user_controller, is_admin=False, user_id=None, is_personal_profile=False):
        super().__init__()
        self.user_controller = user_controller
        self.is_admin = is_admin  # Kept for backward compatibility but always False
        self.user_id = user_id
        self.is_personal_profile = is_personal_profile  # Flag để xác định đây là profile cá nhân
        self.users = []
        
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        if self.is_admin:
            # Admin view - full user management
            # Title
            title_frame = QFrame()
            title_frame.setObjectName("title-frame")
            title_frame.setStyleSheet("""
                #title-frame {
                    background-color: white;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
            """)
            title_layout = QHBoxLayout(title_frame)
            
            title_label = QLabel("Quản lý người dùng")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a73e8;")
            title_layout.addWidget(title_label)
            
            # Button bar in title frame
            button_layout = QHBoxLayout()
            
            self.add_user_btn = QPushButton("Thêm người dùng")
            self.add_user_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
            self.add_user_btn.clicked.connect(self.show_add_user_dialog)
            
            self.refresh_btn = QPushButton("Làm mới")
            self.refresh_btn.setProperty("secondary", "true")
            self.refresh_btn.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
            self.refresh_btn.clicked.connect(self.load_users)
            
            button_layout.addWidget(self.add_user_btn)
            button_layout.addWidget(self.refresh_btn)
            button_layout.addStretch()
            
            title_layout.addLayout(button_layout)
            
            main_layout.addWidget(title_frame)
            
            # Search and filter area
            filter_frame = QFrame()
            filter_frame.setObjectName("filter-frame")
            filter_frame.setMaximumHeight(80)
            filter_frame.setMinimumHeight(35)
            filter_frame.setStyleSheet("""                #filter-frame {
                    background-color: white;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
            """)
            filter_layout = QHBoxLayout(filter_frame)
            self.search_label = QLabel("Tìm kiếm:")
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Nhập tên hoặc email...")
            self.search_input.setMinimumHeight(35)  # Increased height
            self.search_input.textChanged.connect(self.filter_users)
            
            filter_layout.addWidget(self.search_label)
            filter_layout.addWidget(self.search_input)
            filter_layout.addStretch()
            
            main_layout.addWidget(filter_frame)
            
            # User table in a frame
            table_frame = QFrame()
            table_frame.setObjectName("table-frame")
            table_frame.setStyleSheet("""
                #table-frame {
                    background-color: white;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            table_layout = QVBoxLayout(table_frame)
            
            self.user_table = QTableWidget()
            self.user_table.setColumnCount(7)
            self.user_table.setHorizontalHeaderLabels(
                ["ID", "Họ tên", "Email", "Ngày sinh", "CCCD", "Vai trò", "Thao tác"]
            )
            self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.user_table.horizontalHeader().setStretchLastSection(True)
            self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.user_table.setAlternatingRowColors(True)
            self.user_table.verticalHeader().setVisible(False)
            
            table_layout.addWidget(self.user_table)
            
            main_layout.addWidget(table_frame)
        else:
            # Candidate view - only profile view/edit
            # Profile card
            profile_frame = QFrame()
            profile_frame.setObjectName("profile-frame")
            profile_frame.setStyleSheet("""
                #profile-frame {
                    background-color: white;
                    border-radius: 8px;
                    padding: 20px;
                }
                
                QLabel[field="true"] {
                    font-weight: bold;
                    color: #555;
                }
                
                QLabel[value="true"] {
                    color: #333;
                    padding: 5px;
                    background-color: #f5f5f7;
                    border-radius: 4px;
                }
            """)
            profile_layout = QVBoxLayout(profile_frame)
            
            # Title
            title_label = QLabel("Thông tin cá nhân")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;")
            profile_layout.addWidget(title_label)
            
            # Info grid
            form_layout = QFormLayout()
            form_layout.setSpacing(15)
            form_layout.setContentsMargins(20, 20, 20, 20)
            
            # Name field
            name_label = QLabel("Họ tên:")
            name_label.setProperty("field", "true")
            self.name_value = QLabel()
            self.name_value.setProperty("value", "true")
            form_layout.addRow(name_label, self.name_value)
            
            # Email field
            email_label = QLabel("Email:")
            email_label.setProperty("field", "true")
            self.email_value = QLabel()
            self.email_value.setProperty("value", "true")
            form_layout.addRow(email_label, self.email_value)
            
            # Birth date field
            birth_date_label = QLabel("Ngày sinh:")
            birth_date_label.setProperty("field", "true")
            self.birth_date_value = QLabel()
            self.birth_date_value.setProperty("value", "true")
            form_layout.addRow(birth_date_label, self.birth_date_value)
            
            # Citizen ID field
            citizen_id_label = QLabel("CCCD:")
            citizen_id_label.setProperty("field", "true")
            self.citizen_id_value = QLabel()
            self.citizen_id_value.setProperty("value", "true")
            form_layout.addRow(citizen_id_label, self.citizen_id_value)
            
            # Role field
            role_label = QLabel("Vai trò:")
            role_label.setProperty("field", "true")
            self.role_value = QLabel()
            self.role_value.setProperty("value", "true")
            form_layout.addRow(role_label, self.role_value)
            
            profile_layout.addLayout(form_layout)
            
            # Button container
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.edit_profile_btn = QPushButton("Chỉnh sửa thông tin")
            self.edit_profile_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
            self.edit_profile_btn.clicked.connect(self.show_edit_profile_dialog)
            
            button_layout.addWidget(self.edit_profile_btn)
            
            profile_layout.addLayout(button_layout)
            profile_layout.addStretch()
            
            main_layout.addWidget(profile_frame)
            main_layout.addStretch()
        
        # Set layout
        self.setLayout(main_layout)
    
    def load_users(self):
        if self.is_admin:
            # Admin view - load all users
            self.users = self.user_controller.get_all_users()
            self.populate_user_table()
        else:
            # Candidate view hoặc profile cá nhân - chỉ tải thông tin người dùng hiện tại
            if self.user_id:
                print(f"==== Đang tải thông tin người dùng với ID: {self.user_id} ====")
                print(f"Is personal profile: {self.is_personal_profile}")
                
                if self.is_personal_profile:
                    # Nếu là profile cá nhân, thử lấy thông tin từ nhiều nguồn
                    # Ưu tiên 1: API profile
                    print("Đang thử lấy thông tin từ API profile...")
                    user_profile = self.user_controller.get_current_user_profile()
                    
                    if user_profile:
                        print(f"Đã lấy được thông tin profile từ API: {user_profile.name}, {user_profile.email}")
                    else:
                        print("Không lấy được thông tin từ API profile")
                    
                    # Ưu tiên 2: Lấy theo user_id
                    if not user_profile:
                        print(f"Đang thử lấy thông tin theo ID: {self.user_id}")
                        user_profile = self.user_controller.get_user_by_id(self.user_id)
                        if user_profile:
                            print(f"Đã lấy được thông tin theo ID: {user_profile.name}, {user_profile.email}")
                        else:
                            print("Không lấy được thông tin theo ID")
                    
                    # Ưu tiên 3: Lấy từ auth_controller
                    if not user_profile:
                        print("Đang thử lấy thông tin từ auth_controller")
                        from app.controllers.auth_controller import AuthController
                        auth_controller = AuthController()
                        user_profile = auth_controller.get_current_user()
                        if user_profile:
                            print(f"Đã lấy được thông tin từ auth_controller: {user_profile.name}, {user_profile.email}")
                        else:
                            print("Không lấy được thông tin từ auth_controller")
                    
                    if user_profile:
                        print("Cập nhật giao diện profile với dữ liệu đã lấy được")
                        self.update_profile_view(user_profile)
                    else:
                        print("KHÔNG THỂ LẤY THÔNG TIN NGƯỜI DÙNG TỪ BẤT KỲ NGUỒN NÀO")
                        self.add_offline_indicator("⚠️ Không thể tải thông tin người dùng")
                else:
                    # Trường hợp khác, lấy thông tin theo ID
                    user_profile = self.user_controller.get_user_by_id(self.user_id)
                    if user_profile:
                        self.update_profile_view(user_profile)
                    else:
                        self.add_offline_indicator("⚠️ Không thể tải thông tin người dùng theo ID")
    
    def filter_users(self):
        if not self.is_admin:
            return
            
        search_text = self.search_input.text().lower()
        
        for row in range(self.user_table.rowCount()):
            should_show = True
            
            # Check if name or email contains search text
            name = self.user_table.item(row, 1).text().lower()
            email = self.user_table.item(row, 2).text().lower()
            
            if search_text and search_text not in name and search_text not in email:
                should_show = False
            
            # Show/hide row
            self.user_table.setRowHidden(row, not should_show)
    
    def populate_user_table(self):
        self.user_table.setRowCount(0)
        
        for row, user in enumerate(self.users):
            self.user_table.insertRow(row)
            
            # Set user details
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user.user_id)))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.name))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.email))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.birth_date))
            self.user_table.setItem(row, 4, QTableWidgetItem(user.citizen_id))
            self.user_table.setItem(row, 5, QTableWidgetItem(user.role))
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)
            
            edit_btn = QToolButton()
            edit_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
            edit_btn.setIconSize(QSize(18, 18))
            edit_btn.setToolTip("Chỉnh sửa")
            edit_btn.clicked.connect(lambda checked, u=user: self.show_edit_user_dialog(u))
            
            delete_btn = QToolButton()
            delete_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
            delete_btn.setIconSize(QSize(18, 18))
            delete_btn.setToolTip("Xóa")
            delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u))
            
            # More options button
            more_btn = QToolButton()
            more_btn.setIcon(self.style().standardIcon(self.style().SP_ToolBarHorizontalExtensionButton))
            more_btn.setIconSize(QSize(18, 18))
            more_btn.setToolTip("Tùy chọn khác")
            
            # More options menu
            more_menu = QMenu(more_btn)
            
            view_action = QAction("Xem chi tiết", more_btn)
            view_action.triggered.connect(lambda checked, u=user: self.view_user_details(u))
            more_menu.addAction(view_action)
            
            reset_pwd_action = QAction("Đặt lại mật khẩu", more_btn)
            reset_pwd_action.triggered.connect(lambda checked, u=user: self.reset_password(u))
            more_menu.addAction(reset_pwd_action)
            more_btn.setMenu(more_menu)
            more_btn.setPopupMode(QToolButton.InstantPopup)
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(more_btn)
            
            action_widget.setLayout(action_layout)
            self.user_table.setCellWidget(row, 6, action_widget)
    
    def update_profile_view(self, user):
        self.name_value.setText(user.name)
        self.email_value.setText(user.email)
        self.birth_date_value.setText(user.birth_date)
        self.citizen_id_value.setText(user.citizen_id)
        self.role_value.setText("Thí sinh")
    
    def add_offline_indicator(self, message="⚠️ Đang xem dữ liệu ngoại tuyến"):
        """Thêm chỉ báo khi không thể kết nối đến API profile"""
        # Xóa indicator cũ nếu đã tồn tại
        if hasattr(self, 'offline_indicator'):
            try:
                self.offline_indicator.deleteLater()
            except:
                pass
        
        # Tạo indicator mới
        self.offline_indicator = QLabel(message)
        self.offline_indicator.setStyleSheet("""
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
            border-radius: 4px;
            padding: 8px;
            margin-top: 10px;
            font-weight: bold;
        """)
        
        # Thêm vào layout của profile frame
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item.widget(), QFrame) and item.widget().objectName() == "profile-frame":
                profile_frame = item.widget()
                profile_layout = profile_frame.layout()
                # Thêm vào vị trí trước nút Chỉnh sửa
                profile_layout.insertWidget(profile_layout.count() - 1, self.offline_indicator)
                break
    
    def show_add_user_dialog(self):
        dialog = UserDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            user = dialog.get_user()
            valid, message = self.user_controller.validate_user(user)
            
            if valid:
                # Sử dụng register_user thay vì create_user để gọi đúng API endpoint
                created_user = self.user_controller.register_user(user)
                if created_user:
                    QMessageBox.information(self, "Thành công", "Thêm người dùng thành công.")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể thêm người dùng. Vui lòng kiểm tra thông tin và thử lại.")
            else:
                QMessageBox.warning(self, "Lỗi xác thực", message)
    
    def show_edit_user_dialog(self, user):
        dialog = UserDialog(parent=self, user=user)
        if dialog.exec_() == QDialog.Accepted:
            updated_user = dialog.get_user()
            valid, message = self.user_controller.validate_user(updated_user)
            
            if valid:
                result = self.user_controller.update_user(updated_user)
                if result:
                    QMessageBox.information(self, "Thành công", "Cập nhật người dùng thành công.")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể cập nhật người dùng.")
            else:
                QMessageBox.warning(self, "Lỗi xác thực", message)
    
    def show_edit_profile_dialog(self):
        if self.user_id:
            user = self.user_controller.get_user_by_id(self.user_id)
            if user:
                dialog = UserDialog(parent=self, user=user, edit_profile=True)
                if dialog.exec_() == QDialog.Accepted:
                    updated_user = dialog.get_user()
                    valid, message = self.user_controller.validate_user(updated_user)
                    
                    if valid:
                        result = self.user_controller.update_user(updated_user)
                        if result:
                            QMessageBox.information(self, "Thành công", "Cập nhật thông tin thành công.")
                            self.update_profile_view(result)
                        else:
                            QMessageBox.warning(self, "Lỗi", "Không thể cập nhật thông tin.")
                    else:
                        QMessageBox.warning(self, "Lỗi xác thực", message)
    
    def delete_user(self, user):
        reply = QMessageBox.question(
            self, 'Xác nhận xóa', 
            f'Bạn có chắc chắn muốn xóa người dùng {user.name}?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.user_controller.delete_user(user.user_id)
            if result:
                QMessageBox.information(self, "Thành công", "Xóa người dùng thành công.")
                self.load_users()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa người dùng.")
    
    def view_user_details(self, user):
        QMessageBox.information(
            self,
            "Thông tin chi tiết",
            f"ID: {user.user_id}\n"
            f"Họ tên: {user.name}\n"
            f"Email: {user.email}\n"
            f"Ngày sinh: {user.birth_date}\n"
            f"CCCD: {user.citizen_id}\n"
            f"Vai trò: {user.role}"
        )
    
    def reset_password(self, user):
        QMessageBox.information(
            self,
            "Đặt lại mật khẩu",
            f"Chức năng đặt lại mật khẩu cho {user.name} sẽ được triển khai trong phiên bản tiếp theo."
        )


class UserDialog(QDialog):
    def __init__(self, parent=None, user=None, edit_profile=False):
        super().__init__(parent)
        self.user = user
        self.edit_profile = edit_profile
        
        self.setObjectName("user-dialog")
        self.setStyleSheet("""
            #user-dialog {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        self.init_ui()
        if user:
            self.populate_form()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Thêm người dùng" if not self.user else "Chỉnh sửa người dùng")
        self.resize(500, 400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_text = "Thêm người dùng mới" if not self.user else "Chỉnh sửa thông tin người dùng"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Form inside frame
        form_frame = QFrame()
        form_frame.setObjectName("form-frame")
        form_frame.setStyleSheet("""
            #form-frame {
                background-color: #f5f5f7;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        # Form layout
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        # Name field
        name_label = QLabel("Họ tên:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập họ tên")
        self.name_input.setMinimumHeight(35)
        form_layout.addRow(name_label, self.name_input)
        
        # Email field
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email")
        self.email_input.setMinimumHeight(35)
        form_layout.addRow(email_label, self.email_input)
        
        # Password field (only for new users)
        if not self.user:
            password_label = QLabel("Mật khẩu:")
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("Nhập mật khẩu")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setMinimumHeight(35)
            form_layout.addRow(password_label, self.password_input)
        
        # Birth date field
        birth_date_label = QLabel("Ngày sinh:")
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate())
        self.birth_date_input.setMinimumHeight(35)
        form_layout.addRow(birth_date_label, self.birth_date_input)
          # Citizen ID field
        citizen_id_label = QLabel("CCCD:")
        self.citizen_id_input = QLineEdit()
        self.citizen_id_input.setPlaceholderText("Nhập số CCCD (12 chữ số)")
        self.citizen_id_input.setMinimumHeight(35)
        form_layout.addRow(citizen_id_label, self.citizen_id_input)
        
        # Role is always set to Candidate
        # Hidden role field - not shown to the user
        self.role_combo = None
        
        main_layout.addWidget(form_frame)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.setProperty("secondary", "true")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Lưu")
        self.save_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(button_layout)
    
    def populate_form(self):
        # Populate form with user data
        self.name_input.setText(self.user.name)
        self.email_input.setText(self.user.email)
        
        # Set birth date if available
        if self.user.birth_date:
            try:
                # Try to parse date in format YYYY-MM-DD
                date_parts = self.user.birth_date.split('-')
                if len(date_parts) == 3:
                    year, month, day = map(int, date_parts)
                    self.birth_date_input.setDate(QDate(year, month, day))
            except:
                # If parsing fails, use current date
                self.birth_date_input.setDate(QDate.currentDate())
        
        self.citizen_id_input.setText(self.user.citizen_id)        
        # Role is always CANDIDATE, no need to set it in combo box
    
    def get_user(self):
        # Create a new user or update existing one
        name = self.name_input.text()
        email = self.email_input.text()
        birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")
        citizen_id = self.citizen_id_input.text()
        
        # Always set role to CANDIDATE
        role = Config.ROLE_CANDIDATE
        if self.user:
            # Update existing user
            user = User(
                user_id=self.user.user_id,
                name=name,
                email=email,
                birth_date=birth_date,
                citizen_id=citizen_id,
                role=role
            )
        else:
            # Create new user
            password = self.password_input.text()
            user = User(
                name=name,
                email=email,
                password=password,
                birth_date=birth_date,
                citizen_id=citizen_id,
                role=role
            )
        
        return user