from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDialog, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from app.models.exam_attendance import ExamAttendance
from app.views.attendance_cccd_scanner import AttendanceCCCDScannerDialog

class AttendancePanel(QWidget):
    def __init__(self, attendance_controller, user_controller, exam_controller, is_admin=True, auth_controller=None, is_candidate=False):
        super().__init__()
        self.attendance_controller = attendance_controller
        self.user_controller = user_controller
        self.exam_controller = exam_controller
        self.auth_controller = auth_controller  # Store the auth controller instance
        self.is_admin = is_admin
        self.is_candidate = is_candidate  # Flag để xác định đây là view của candidate
        self.attendance_records = []
        self.users = []
        self.exams = []
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Title
        title_text = "Attendance Management" if self.is_admin else "My Exams"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        if self.is_admin:
            # Admin view - full attendance management
            # Filter section
            filter_layout = QHBoxLayout()
            
            self.exam_filter_label = QLabel("Filter by Exam:")
            self.exam_filter_combo = QComboBox()
            self.exam_filter_combo.addItem("All Exams", None)
            self.exam_filter_combo.currentIndexChanged.connect(self.filter_attendance)
            
            filter_layout.addWidget(self.exam_filter_label)
            filter_layout.addWidget(self.exam_filter_combo)
            filter_layout.addStretch()
            
            self.refresh_btn = QPushButton("Refresh")
            self.refresh_btn.clicked.connect(self.load_data)
            
            self.mark_attendance_btn = QPushButton("Mark Attendance")
            self.mark_attendance_btn.clicked.connect(self.show_mark_attendance_dialog)
            
            self.mark_face_cccd_btn = QPushButton("Mark with CCCD & Face")
            self.mark_face_cccd_btn.clicked.connect(self.show_face_cccd_dialog)
            self.mark_face_cccd_btn.setStyleSheet("""
                QPushButton {
                    background-color: #34A853;
                    color: white;
                    font-weight: bold;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #2E8B57;
                }
            """)
            
            filter_layout.addWidget(self.mark_face_cccd_btn)
            filter_layout.addWidget(self.mark_attendance_btn)
            filter_layout.addWidget(self.refresh_btn)
            
            main_layout.addLayout(filter_layout)
        else:
            # Candidate view - only view attendance
            # Button bar
            button_layout = QHBoxLayout()
            
            self.refresh_btn = QPushButton("Refresh")
            self.refresh_btn.clicked.connect(self.load_data)
            
            button_layout.addStretch()
            button_layout.addWidget(self.refresh_btn)
            
            main_layout.addLayout(button_layout)
          # Attendance table
        self.attendance_table = QTableWidget()
        headers = ["ID", "Exam", "Candidate", "Attendance Time", "CCCD Verified", "Face Verified"]
        
        if self.is_admin:
            headers.append("Actions")
        
        self.attendance_table.setColumnCount(len(headers))
        self.attendance_table.setHorizontalHeaderLabels(headers)
        self.attendance_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.attendance_table.horizontalHeader().setStretchLastSection(True)
        
        main_layout.addWidget(self.attendance_table)
        
        # Set layout
        self.setLayout(main_layout)
    
    def load_data(self):
        # Load exams - chỉ tải dữ liệu cần thiết dựa trên quyền
        if self.is_admin:
            # Admin cần tất cả exams
            self.exams = self.exam_controller.get_all_exams()
        else:
            # Candidate chỉ cần exams của họ
            if self.is_candidate:
                self.exams = self.exam_controller.get_my_exams()
            else:
                # Fallback cho các trường hợp khác
                self.exams = self.exam_controller.get_all_exams()
        
        # Load users - chỉ tải dữ liệu users khi cần thiết
        if self.is_admin:
            # Admin cần thông tin tất cả users
            self.users = self.user_controller.get_all_users()
        else:
            # Candidate chỉ cần thông tin của họ
            if self.auth_controller:
                user = self.auth_controller.get_current_user()
                if user:
                    self.users = [user]  # Chỉ lưu thông tin của user hiện tại
            
        # Update exam filter
        if self.is_admin:
            self.exam_filter_combo.clear()
            self.exam_filter_combo.addItem("All Exams", None)
            
            for exam in self.exams:
                self.exam_filter_combo.addItem(exam.name, exam.exam_id)
        
        # Load attendance records
        self.load_attendance_records()
    
    def load_attendance_records(self):
        if self.is_admin:
            # Admin view - load all attendance records
            self.attendance_records = self.attendance_controller.get_all_attendance()
        else:
            # Candidate view - load only current user's attendance
            user = self.auth_controller.get_current_user() if self.auth_controller else None
            
            if user:
                self.attendance_records = self.attendance_controller.get_attendance_by_user(user.user_id)
        
        self.populate_attendance_table()
    
    def filter_attendance(self):
        # Get selected exam ID
        selected_index = self.exam_filter_combo.currentIndex()
        exam_id = self.exam_filter_combo.itemData(selected_index)
        
        if exam_id:
            # Filter by exam
            self.attendance_records = self.attendance_controller.get_attendance_by_exam(exam_id)
        else:
            # Show all attendance
            self.attendance_records = self.attendance_controller.get_all_attendance()
        
        self.populate_attendance_table()
    
    def populate_attendance_table(self):
        self.attendance_table.setRowCount(0)
        
        for row, attendance in enumerate(self.attendance_records):
            self.attendance_table.insertRow(row)
            
            # Find exam and user names
            exam_name = "Unknown"
            user_name = "Unknown"
            
            for exam in self.exams:
                if exam.exam_id == attendance.exam_id:
                    exam_name = exam.name
                    break
            
            for user in self.users:
                if user.user_id == attendance.user_id:
                    user_name = user.name
                    break
              # Set attendance details - using new API format
            attendance_id = attendance.attendance_id if hasattr(attendance, 'attendance_id') else (str(getattr(attendance, 'id', 'Unknown')))
            self.attendance_table.setItem(row, 0, QTableWidgetItem(str(attendance_id)))
              # Exam info - Display both name and subject
            exam_display = exam_name  # Default fallback
            if hasattr(attendance, 'exam') and isinstance(attendance.exam, dict):
                exam_name = attendance.exam.get('name', 'Unknown')
                exam_subject = attendance.exam.get('subject', '')
                if exam_subject:
                    exam_display = f"{exam_name} - {exam_subject}"
                else:
                    exam_display = exam_name
            self.attendance_table.setItem(row, 1, QTableWidgetItem(exam_display))
            
            # Candidate info
            if hasattr(attendance, 'candidate') and isinstance(attendance.candidate, dict) and 'name' in attendance.candidate:
                user_name = attendance.candidate['name']
            self.attendance_table.setItem(row, 2, QTableWidgetItem(user_name))
              # Attendance time
            attendance_time = ""
            if hasattr(attendance, 'attendanceTime') and attendance.attendanceTime:
                attendance_time = attendance.attendanceTime
            elif hasattr(attendance, 'attendance_time') and attendance.attendance_time:
                attendance_time = attendance.attendance_time
            elif hasattr(attendance, 'check_in_time') and attendance.check_in_time:
                attendance_time = attendance.check_in_time
            
            print(f"DEBUG: Attendance time for attendance {attendance.attendance_id if hasattr(attendance, 'attendance_id') else 'unknown'}: {attendance_time}")
                
            attendance_time_item = QTableWidgetItem(str(attendance_time))
            self.attendance_table.setItem(row, 3, attendance_time_item)
              # CCCD Verification status
            cccd_verified = False
            if hasattr(attendance, 'citizenCardVerified'):
                cccd_verified = attendance.citizenCardVerified
            
            print(f"DEBUG: CCCD Verified for attendance {attendance.attendance_id if hasattr(attendance, 'attendance_id') else 'unknown'}: {cccd_verified} (type: {type(cccd_verified)})")
            
            cccd_item = QTableWidgetItem("✅" if cccd_verified else "❌")
            cccd_item.setBackground(Qt.green if cccd_verified else Qt.red)
            cccd_item.setTextAlignment(Qt.AlignCenter)
            self.attendance_table.setItem(row, 4, cccd_item)
            
            # Face Verification status
            face_verified = False
            if hasattr(attendance, 'faceVerified'):
                face_verified = attendance.faceVerified
            
            print(f"DEBUG: Face Verified for attendance {attendance.attendance_id if hasattr(attendance, 'attendance_id') else 'unknown'}: {face_verified} (type: {type(face_verified)})")
            
            face_item = QTableWidgetItem("✅" if face_verified else "❌")
            face_item.setBackground(Qt.green if face_verified else Qt.red)
            face_item.setTextAlignment(Qt.AlignCenter)
            self.attendance_table.setItem(row, 5, face_item)
            if self.is_admin:
                # Action buttons for admin
                action_widget = QWidget()
                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(lambda checked, a=attendance: self.edit_attendance(a))
                
                action_layout.addWidget(edit_btn)
                
                action_widget.setLayout(action_layout)
                self.attendance_table.setCellWidget(row, 6, action_widget)
    
    def show_mark_attendance_dialog(self):
        """Show dialog to mark attendance manually"""
        dialog = MarkAttendanceDialog(self.users, self.exams, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            attendance = dialog.get_attendance()
            
            result = self.attendance_controller.mark_attendance(attendance)
            if result:
                QMessageBox.information(self, "Success", "Attendance recorded successfully.")
                self.load_attendance_records()
            else:
                QMessageBox.warning(self, "Error", "Failed to record attendance.")
    
    def show_face_cccd_dialog(self):
        """Show dialog to mark attendance with CCCD and face recognition"""
        # Only admin users can mark attendance
        if not self.is_admin:
            return
        
        # Get the current selected exam from the filter dropdown
        selected_index = self.exam_filter_combo.currentIndex()
        exam_id = self.exam_filter_combo.itemData(selected_index)
        selected_exam = None
        
        # Find the selected exam
        for exam in self.exams:
            if exam.exam_id == exam_id:
                selected_exam = exam
                break
          # Launch the CCCD scanner dialog
        dialog = AttendanceCCCDScannerDialog(self, selected_exam, self.users)
        dialog.attendance_recorded.connect(self.on_face_attendance_recorded)
        dialog.exec_()
    
    def on_face_attendance_recorded(self, user_id, exam_id, timestamp):
        """Process the attendance recorded by face verification"""
        # Gọi phương thức API mới theo định dạng JSON mới
        result = self.attendance_controller.mark_attendance_with_cccd(
            user_id, exam_id
        )
        
        if result:
            QMessageBox.information(self, "Thành công", "Điểm danh thành công với xác thực CCCD và khuôn mặt.")
            self.load_attendance_records()  # Refresh the attendance records
        
    def edit_attendance(self, attendance):
        """Show dialog to edit an existing attendance record"""
        dialog = EditAttendanceDialog(attendance, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            updated_attendance = dialog.get_attendance()
            
            result = self.attendance_controller.update_attendance(updated_attendance)
            if result:
                QMessageBox.information(self, "Success", "Attendance updated successfully.")
                self.load_attendance_records()
            else:
                QMessageBox.warning(self, "Error", "Failed to update attendance.")

class MarkAttendanceDialog(QDialog):
    def __init__(self, users, exams, parent=None):
        super().__init__(parent)
        self.users = users
        self.exams = exams
        
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Mark Attendance")
        self.resize(400, 200)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # User selection
        self.user_combo = QComboBox()
        for user in self.users:
            if user.role == "CANDIDATE":  # Only candidates can have attendance
                self.user_combo.addItem(user.name, user.user_id)
        
        form_layout.addRow("User:", self.user_combo)
        
        # Exam selection
        self.exam_combo = QComboBox()
        for exam in self.exams:
            self.exam_combo.addItem(exam.name, exam.exam_id)
        
        form_layout.addRow("Exam:", self.exam_combo)
        
        # Status field
        self.status_combo = QComboBox()
        self.status_combo.addItem("Present", "PRESENT")
        self.status_combo.addItem("Absent", "ABSENT")
        self.status_combo.addItem("Late", "LATE")
        
        form_layout.addRow("Status:", self.status_combo)
        
        main_layout.addLayout(form_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(main_layout)
    
    def get_attendance(self):
        # Get selected user and exam IDs
        user_id = self.user_combo.currentData()
        exam_id = self.exam_combo.currentData()
        status = self.status_combo.currentData()
        
        # Create attendance record
        attendance = ExamAttendance(
            user_id=user_id,
            exam_id=exam_id,
            status=status
        )
        
        return attendance


class EditAttendanceDialog(QDialog):
    def __init__(self, attendance, parent=None):
        super().__init__(parent)
        self.attendance = attendance
        
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Edit Attendance")
        self.resize(400, 200)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Display user ID and exam ID (non-editable)
        self.user_id_label = QLabel(str(self.attendance.user_id))
        form_layout.addRow("User ID:", self.user_id_label)
        
        self.exam_id_label = QLabel(str(self.attendance.exam_id))
        form_layout.addRow("Exam ID:", self.exam_id_label)
        
        # Status field
        self.status_combo = QComboBox()
        self.status_combo.addItem("Present", "PRESENT")
        self.status_combo.addItem("Absent", "ABSENT")
        self.status_combo.addItem("Late", "LATE")
        
        # Set current status
        if self.attendance.status:
            index = self.status_combo.findData(self.attendance.status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        form_layout.addRow("Status:", self.status_combo)
        
        main_layout.addLayout(form_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(main_layout)
    
    def get_attendance(self):
        # Update attendance status
        self.attendance.status = self.status_combo.currentData()
        return self.attendance