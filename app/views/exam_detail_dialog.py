from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QFormLayout, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from app.models.exam_attendance import ExamAttendance
from app.controllers.attendance_controller import AttendanceController
from app.utils.api_service import ApiService
import datetime

class ExamDetailDialog(QDialog):
    def __init__(self, parent, exam, exam_controller):
        super().__init__(parent)
        self.exam = exam
        self.exam_controller = exam_controller
        self.attendance_controller = AttendanceController()
        self.api_service = ApiService.get_instance()
        
        self.setWindowTitle(f"Chi tiết kỳ thi: {exam.name}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create content frame
        content_frame = QFrame()
        content_frame.setObjectName("content-frame")
        content_frame.setStyleSheet("""
            #content-frame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
            .header {
                font-size: 18px;
                font-weight: bold;
                color: #1a73e8;
                margin-bottom: 15px;
            }
            .label {
                font-weight: bold;
            }
            .value {
                padding: 8px;
                background-color: #f5f5f7;
                border-radius: 4px;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        
        # Header
        header_label = QLabel(self.exam.name)
        header_label.setProperty("class", "header")
        header_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(header_label)
        
        # Exam information form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Exam ID
        id_label = QLabel("ID kỳ thi:")
        id_label.setProperty("class", "label")
        id_value = QLabel(str(self.exam.exam_id))
        id_value.setProperty("class", "value")
        form_layout.addRow(id_label, id_value)
        
        # Subject
        subject_label = QLabel("Môn học:")
        subject_label.setProperty("class", "label")
        subject_value = QLabel(self.exam.subject)
        subject_value.setProperty("class", "value")
        form_layout.addRow(subject_label, subject_value)
        
        # Semester
        semester_label = QLabel("Học kỳ:")
        semester_label.setProperty("class", "label")
        semester_value = QLabel(self.exam.semester)
        semester_value.setProperty("class", "value")
        form_layout.addRow(semester_label, semester_value)
        
        # Exam date
        date_label = QLabel("Ngày thi:")
        date_label.setProperty("class", "label")
        date_value = QLabel(self.exam.exam_date)
        date_value.setProperty("class", "value")
        form_layout.addRow(date_label, date_value)
        
        # Room
        room_label = QLabel("Phòng thi:")
        room_label.setProperty("class", "label")
        room_value = QLabel(self.exam.room_display)
        room_value.setProperty("class", "value")
        form_layout.addRow(room_label, room_value)
        
        # Schedule
        schedule_label = QLabel("Kíp thi:")
        schedule_label.setProperty("class", "label")
        schedule_value = QLabel(self.exam.schedule_name)
        schedule_value.setProperty("class", "value")
        form_layout.addRow(schedule_label, schedule_value)
        
        content_layout.addLayout(form_layout)
        
        # Attendance button
        attendance_layout = QHBoxLayout()
        attendance_layout.addStretch()
        
        self.attendance_btn = QPushButton("Điểm danh")
        self.attendance_btn.setMinimumWidth(150)
        self.attendance_btn.setMinimumHeight(40)
        self.attendance_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
        """)
        self.attendance_btn.clicked.connect(self.start_face_scan_attendance)
        
        attendance_layout.addWidget(self.attendance_btn)
        attendance_layout.addStretch()
        
        content_layout.addSpacing(20)
        content_layout.addLayout(attendance_layout)
        content_layout.addStretch()
        
        # Add content frame to main layout
        main_layout.addWidget(content_frame)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Đóng")
        self.close_btn.setMinimumWidth(100)
        self.close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.close_btn)
        
        # Add to main layout
        main_layout.addLayout(button_layout)
    
    def start_face_scan_attendance(self):
        """Start the face scan attendance process"""
        from app.views.face_scanner_dialog import FaceScannerDialog
        face_scanner = FaceScannerDialog(self, self.exam)
        result = face_scanner.exec_()
        
        if result == QDialog.Accepted:
            # Mark attendance in the system
            user = self.api_service.user_data
            user_id = user.get('userId') if isinstance(user, dict) else None
            
            if not user_id:
                QMessageBox.warning(self, "Lỗi", "Không xác định được thông tin người dùng.")
                return
            
            # Create attendance object
            attendance = ExamAttendance(
                user_id=user_id,
                exam_id=self.exam.exam_id,
                status="PRESENT",
                attendance_time=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            )
            
            # Submit attendance
            result = self.attendance_controller.mark_attendance(attendance)
            
            if result:
                QMessageBox.information(
                    self, 
                    "Thành công", 
                    "Đã điểm danh thành công. Chúc bạn làm bài thi tốt!"
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self, 
                    "Lỗi", 
                    "Không thể điểm danh. Vui lòng thử lại hoặc liên hệ giám thị."
                )
