from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QComboBox, QDialog, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from app.models.exam_attendance import ExamAttendance

class AttendancePanel(QWidget):
    def __init__(self, attendance_controller, user_controller, exam_controller, is_admin=True):
        super().__init__()
        self.attendance_controller = attendance_controller
        self.user_controller = user_controller
        self.exam_controller = exam_controller
        self.is_admin = is_admin
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
        headers = ["ID", "Exam", "User", "Check-in Time", "Check-out Time", "Status"]
        
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
        # Load exams
        self.exams = self.exam_controller.get_all_exams()
        
        # Load users
        self.users = self.user_controller.get_all_users()
        
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
            from app.controllers.auth_controller import AuthController
            auth_controller = AuthController()
            user = auth_controller.get_current_user()
            
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
            
            # Set attendance details
            self.attendance_table.setItem(row, 0, QTableWidgetItem(str(attendance.attendance_id)))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(exam_name))
            self.attendance_table.setItem(row, 2, QTableWidgetItem(user_name))
            self.attendance_table.setItem(row, 3, QTableWidgetItem(str(attendance.check_in_time or "")))
            self.attendance_table.setItem(row, 4, QTableWidgetItem(str(attendance.check_out_time or "")))
            self.attendance_table.setItem(row, 5, QTableWidgetItem(attendance.status or ""))
            
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
        dialog = MarkAttendanceDialog(self.users, self.exams, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            attendance = dialog.get_attendance()
            
            result = self.attendance_controller.mark_attendance(attendance)
            if result:
                QMessageBox.information(self, "Success", "Attendance marked successfully.")
                self.load_attendance_records()
            else:
                QMessageBox.warning(self, "Error", "Failed to mark attendance.")
    
    def edit_attendance(self, attendance):
        # Dialog to edit attendance record
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