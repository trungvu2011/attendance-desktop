"""
Attendance CCCD Scanner Dialog
This module provides a dialog for scanning CCCD data for attendance purposes.
It integrates with the mobile app to receive CCCD data and perform face verification.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QFrame, QTabWidget,
                             QListWidget, QListWidgetItem, QSplitter, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
import cv2
import time
import os
import json
import face_recognition
import socket
from app.controllers.cccd_api import CCCDApiController
from app.controllers.cccd_socket_server import CCCDSocketServer
from app.utils.face_recognition import compare_faces
from app.utils.datetime_utils import format_datetime_for_api, format_datetime_for_filename, format_time_from_iso

class AttendanceCCCDScannerDialog(QDialog):
    """Dialog for scanning CCCD data for attendance verification"""
    
    # Signal emitted when attendance is successfully recorded
    attendance_recorded = pyqtSignal(str, str, str)  # user_id, exam_id, timestamp
    
    def __init__(self, parent, exam=None, attendees=None):
        """
        Initialize the dialog
        
        Args:
            parent: Parent widget
            exam: Exam object (if applicable)
            attendees: List of attendees (if applicable)
        """
        super().__init__(parent)
        self.exam = exam
        self.attendees = attendees or []
        self.current_user = None
        self.scanning = False
        self.camera = None
        self.timer = None
        self.scan_timer = None
        self.countdown_remaining = 3
        
        # CCCD verification related variables
        self.cccd_api = CCCDApiController()
        self.captured_face_path = None
        self.cccd_data_received = {}  # Store all received CCCD data
        
        # Initialize socket server if not already running
        self.socket_server = CCCDSocketServer.get_instance()
        if not self.socket_server.is_running:
            self.socket_server.start()
        
        # Register for CCCD data callbacks
        self.socket_server.register_data_callback(self.on_cccd_data_received)
        
        # Create data directories
        self.data_dir = os.path.join("app", "data", "captured_faces")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.setWindowTitle("Điểm danh CCCD")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create title
        title_label = QLabel("Điểm danh bằng CCCD và nhận dạng khuôn mặt")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Attendees list
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        attendees_label = QLabel("Danh sách thí sinh")
        attendees_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        left_layout.addWidget(attendees_label)
        
        # IP Address instructions
        ip_instruction = QLabel(f"Địa chỉ IP để kết nối ứng dụng di động: {self.get_local_ip()}")
        ip_instruction.setWordWrap(True)
        ip_instruction.setStyleSheet("margin-top: 5px; margin-bottom: 10px; color: #555; font-weight: bold;")
        left_layout.addWidget(ip_instruction)
        
        # CCCD scanner status
        self.cccd_status = QLabel("Đang chờ dữ liệu CCCD từ ứng dụng di động...")
        self.cccd_status.setStyleSheet("color: #1a73e8; margin-bottom: 10px;")
        left_layout.addWidget(self.cccd_status)
        
        # Attendee list
        self.attendee_list = QListWidget()
        self.attendee_list.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
        self.attendee_list.setMinimumHeight(200)
        self.attendee_list.currentItemChanged.connect(self.on_attendee_selected)
        left_layout.addWidget(self.attendee_list)
        
        # Populate attendee list
        self.populate_attendee_list()
        
        # Received CCCD data
        received_cccd_label = QLabel("CCCD đã nhận")
        received_cccd_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-top: 20px;")
        left_layout.addWidget(received_cccd_label)
        
        self.received_cccd_list = QTableWidget(0, 3)  # columns: CCCD number, time, status
        self.received_cccd_list.setHorizontalHeaderLabels(["Số CCCD", "Thời gian", "Trạng thái"])
        self.received_cccd_list.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
        self.received_cccd_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.received_cccd_list.setEditTriggers(QTableWidget.NoEditTriggers)
        left_layout.addWidget(self.received_cccd_list)
        
        # Add left panel to splitter
        splitter.addWidget(left_panel)
        
        # Right panel
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Current user info
        current_user_frame = QFrame()
        current_user_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 8px; padding: 10px;")
        current_user_layout = QVBoxLayout(current_user_frame)
        
        self.user_name_label = QLabel("Chưa chọn thí sinh")
        self.user_name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        current_user_layout.addWidget(self.user_name_label)
        
        self.user_cccd_label = QLabel("CCCD: ")
        current_user_layout.addWidget(self.user_cccd_label)
        
        right_layout.addWidget(current_user_frame)
        
        # Tab widget for CCCD and face verification
        self.tab_widget = QTabWidget()
        right_layout.addWidget(self.tab_widget)
        
        # CCCD Image Tab
        cccd_tab = QFrame()
        cccd_layout = QVBoxLayout(cccd_tab)
        
        cccd_instruction = QLabel("Ảnh từ CCCD được gửi từ ứng dụng di động")
        cccd_instruction.setAlignment(Qt.AlignCenter)
        cccd_instruction.setStyleSheet("color: #555;")
        cccd_layout.addWidget(cccd_instruction)
        
        self.cccd_image = QLabel()
        self.cccd_image.setAlignment(Qt.AlignCenter)
        self.cccd_image.setMinimumHeight(300)
        self.cccd_image.setStyleSheet("border: 2px solid #ccc; border-radius: 8px;")
        cccd_layout.addWidget(self.cccd_image)
        
        # Add tab to tab widget
        self.tab_widget.addTab(cccd_tab, "Ảnh CCCD")
        
        # Face Verification Tab
        face_tab = QFrame()
        face_layout = QVBoxLayout(face_tab)
        
        # Face recognition instructions
        face_instruction = QLabel("Hãy đảm bảo khuôn mặt của thí sinh nằm trong khung và nhìn thẳng vào camera")
        face_instruction.setWordWrap(True)
        face_instruction.setAlignment(Qt.AlignCenter)
        face_instruction.setStyleSheet("color: #555;")
        face_layout.addWidget(face_instruction)
        
        # Camera frame
        self.camera_frame = QLabel()
        self.camera_frame.setAlignment(Qt.AlignCenter)
        self.camera_frame.setMinimumHeight(300)
        self.camera_frame.setStyleSheet("border: 2px solid #ccc; border-radius: 8px;")
        face_layout.addWidget(self.camera_frame)
        
        # Status label
        self.status_label = QLabel("Chuẩn bị...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; color: #1a73e8;")
        face_layout.addWidget(self.status_label)
        
        # Camera control buttons
        camera_button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("Bắt đầu quét khuôn mặt")
        self.scan_btn.setEnabled(False)  # Disabled until CCCD is verified
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #A9A9A9;
            }
        """)
        self.scan_btn.clicked.connect(self.toggle_scanning)
        
        camera_button_layout.addStretch()
        camera_button_layout.addWidget(self.scan_btn)
        camera_button_layout.addStretch()
        
        face_layout.addLayout(camera_button_layout)
        
        # Add tab to tab widget
        self.tab_widget.addTab(face_tab, "Xác thực khuôn mặt")
        
        # Add to splitter
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([int(self.width() * 0.4), int(self.width() * 0.6)])
        
        # Main button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Đóng")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.confirm_btn = QPushButton("Xác nhận điểm danh")
        self.confirm_btn.setMinimumWidth(150)
        self.confirm_btn.setEnabled(False)  # Disabled until face verification passes
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #34A853;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #137333;
            }
            QPushButton:disabled {
                background-color: #A9A9A9;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm_attendance)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn)
        
        main_layout.addLayout(button_layout)
    
    def get_local_ip(self):
        """Get local IP address for mobile app connection"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to a public IP (Google DNS)
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Không thể xác định IP"
    
    def populate_attendee_list(self):
        """Populate the attendee list with data"""
        self.attendee_list.clear()
        
        for attendee in self.attendees:
            item = QListWidgetItem(f"{attendee.name} - {attendee.citizen_id}")
            item.setData(Qt.UserRole, attendee)
            self.attendee_list.addItem(item)
    
    def on_attendee_selected(self, current, previous):
        """Handle attendee selection change"""
        if not current:
            self.current_user = None
            self.user_name_label.setText("Chưa chọn thí sinh")
            self.user_cccd_label.setText("CCCD: ")
            self.scan_btn.setEnabled(False)
            return
        
        # Update current user
        self.current_user = current.data(Qt.UserRole)
        
        # Update UI
        self.user_name_label.setText(f"Thí sinh: {self.current_user.name}")
        self.user_cccd_label.setText(f"CCCD: {self.current_user.citizen_id}")
        
        # Check if we already have CCCD data for this user
        if self.current_user.citizen_id in self.cccd_data_received:
            cccd_data = self.cccd_data_received[self.current_user.citizen_id]
            
            # Update CCCD image
            image_path = cccd_data['image_path']
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                self.cccd_image.setPixmap(pixmap.scaled(
                    self.cccd_image.width(), 
                    self.cccd_image.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
            
            # Enable face scanning
            self.scan_btn.setEnabled(True)
            
            # Switch to face tab
            self.tab_widget.setCurrentIndex(1)
        else:
            # No CCCD data yet
            self.cccd_image.clear()
            self.scan_btn.setEnabled(False)
            
            # Switch to CCCD tab
            self.tab_widget.setCurrentIndex(0)
    
    def on_cccd_data_received(self, citizen_id, image_path, data):
        """Callback when CCCD data is received from mobile app"""        # Store the received data
        self.cccd_data_received[citizen_id] = {
            'image_path': image_path,
            'data': data,
            'timestamp': format_datetime_for_api()
        }
        
        # Update CCCD status
        self.cccd_status.setText(f"Đã nhận dữ liệu CCCD: {citizen_id}")
        
        # Update received CCCD list
        self.update_received_cccd_table()
        
        # If this matches the current user, update UI
        if self.current_user and self.current_user.citizen_id == citizen_id:
            # Update CCCD image
            pixmap = QPixmap(image_path)
            self.cccd_image.setPixmap(pixmap.scaled(
                self.cccd_image.width(), 
                self.cccd_image.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            
            # Enable face scanning
            self.scan_btn.setEnabled(True)
            
            # Switch to face tab
            self.tab_widget.setCurrentIndex(1)
    
    def update_received_cccd_table(self):
        """Update the table of received CCCD data"""
        self.received_cccd_list.setRowCount(0)
        
        row = 0
        for citizen_id, data in self.cccd_data_received.items():
            self.received_cccd_list.insertRow(row)
            
            # CCCD number
            self.received_cccd_list.setItem(row, 0, QTableWidgetItem(citizen_id))
              # Timestamp
            timestamp = format_time_from_iso(data['timestamp'])
            self.received_cccd_list.setItem(row, 1, QTableWidgetItem(timestamp))
            
            # Status
            status_item = QTableWidgetItem("Chưa xác thực")
            status_item.setForeground(QColor("#EA4335"))  # Red color
            self.received_cccd_list.setItem(row, 2, status_item)
            
            row += 1
    
    def toggle_scanning(self):
        """Start or stop the facial scan process"""
        if not self.scanning:
            # Start scanning
            self.start_camera()
            self.scan_btn.setText("Dừng quét")
            self.status_label.setText("Đang quét khuôn mặt...")
            self.scanning = True
        else:
            # Stop scanning
            self.stop_camera()
            self.scan_btn.setText("Bắt đầu quét khuôn mặt")
            self.status_label.setText("Đã dừng quét")
            self.scanning = False
    
    def start_camera(self):
        """Initialize and start the camera"""
        self.camera = cv2.VideoCapture(0)  # Use default camera (index 0)
        
        if not self.camera.isOpened():
            QMessageBox.warning(self, "Lỗi", "Không thể mở camera. Vui lòng kiểm tra và thử lại.")
            return
        
        # Start the timer for camera frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms
    
    def update_frame(self):
        """Update camera frame and process face detection using face_recognition library"""
        if not self.camera:
            return
            
        ret, frame = self.camera.read()
        
        if not ret:
            return
        
        try:
            # Convert frame to RGB for face_recognition (it expects RGB, not BGR which OpenCV uses)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations with face_recognition
            # Use a smaller scale to improve performance (process 1/4 size image)
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_frame)
            
            # Scale back up the face locations
            face_locations_original = [(top*4, right*4, bottom*4, left*4) 
                                      for (top, right, bottom, left) in face_locations]
            
            # Draw rectangle around faces
            for (top, right, bottom, left) in face_locations_original:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Check if a face is found
            if len(face_locations_original) == 1:
                if not self.scan_timer:
                    self.scan_timer = time.time()
                    self.countdown_remaining = 3
                
                # Calculate elapsed time
                elapsed = time.time() - self.scan_timer
                remaining = 3 - int(elapsed)
                
                if remaining != self.countdown_remaining:
                    self.countdown_remaining = remaining
                    self.status_label.setText(f"Đã phát hiện khuôn mặt! Giữ nguyên trong {remaining + 1}...")
                
                if elapsed >= 3:
                    # Face has been detected continuously for 3 seconds
                    self.status_label.setText("Đang xử lý khuôn mặt...")
                    self.scan_btn.setEnabled(False)
                      # Capture the current frame and save it
                    timestamp = format_datetime_for_filename()
                    self.captured_face_path = os.path.join(self.data_dir, f"face_{timestamp}.jpg")
                    cv2.imwrite(self.captured_face_path, frame)
                    
                    # Wait a second to show success message before moving on
                    QTimer.singleShot(1000, self.verify_face_with_cccd)
                    self.timer.stop()
                    return
            else:
                # Reset timer if face is lost
                self.scan_timer = None
                self.status_label.setText("Đang quét khuôn mặt... Vui lòng nhìn thẳng vào camera")
            
            # Convert for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            
            # Convert to QImage
            image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit in the frame
            pixmap = QPixmap.fromImage(image)
            self.camera_frame.setPixmap(pixmap.scaled(
                self.camera_frame.width(), 
                self.camera_frame.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        
        except Exception as e:
            print(f"Error in face detection: {e}")
            self.status_label.setText("Lỗi phát hiện khuôn mặt")
    
    def verify_face_with_cccd(self):
        """Compare the captured face with the CCCD image"""
        if not self.current_user or not self.captured_face_path:
            self.status_label.setText("Không thể xác thực: Thiếu dữ liệu CCCD hoặc khuôn mặt")
            self.scan_btn.setEnabled(True)
            return
        
        self.status_label.setText("Đang so sánh khuôn mặt với ảnh CCCD...")
        
        # Get CCCD data
        citizen_id = self.current_user.citizen_id
        if citizen_id not in self.cccd_data_received:
            self.status_label.setText("Lỗi: Không tìm thấy dữ liệu CCCD")
            self.scan_btn.setEnabled(True)
            return
        
        cccd_data = self.cccd_data_received[citizen_id]
        cccd_image_path = cccd_data['image_path']
        
        # Compare faces
        result = self.cccd_api.verify_face_with_cccd(citizen_id, self.captured_face_path)
        
        if result['is_match']:
            self.status_label.setText(f"Xác thực thành công! {result['message']} Độ chính xác: {result['confidence']:.1%}")
            self.status_label.setStyleSheet("font-weight: bold; color: #34A853;")
            
            # Update CCCD status in the table
            self.update_cccd_status(citizen_id, "Đã xác thực", "#34A853")  # Green color
            
            # Enable confirm button
            self.confirm_btn.setEnabled(True)
        else:
            self.status_label.setText(f"Xác thực thất bại! {result['message']} Độ chính xác: {result['confidence']:.1%}")
            self.status_label.setStyleSheet("font-weight: bold; color: #EA4335;")
            
            # Update CCCD status in the table
            self.update_cccd_status(citizen_id, "Xác thực thất bại", "#EA4335")  # Red color
            
            self.scan_btn.setEnabled(True)
    
    def update_cccd_status(self, citizen_id, status_text, color):
        """Update the status of a CCCD in the table"""
        for row in range(self.received_cccd_list.rowCount()):
            if self.received_cccd_list.item(row, 0).text() == citizen_id:
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor(color))
                self.received_cccd_list.setItem(row, 2, status_item)
                break
    
    def confirm_attendance(self):
        """Confirm attendance for the current user"""
        if not self.current_user:
            return
          # Record attendance
        timestamp = format_datetime_for_api()
        
        if self.exam:
            # If this is for a specific exam
            self.attendance_recorded.emit(self.current_user.id, self.exam.id, timestamp)
            
            QMessageBox.information(self, "Điểm danh thành công", 
                                   f"Đã điểm danh thành công cho thí sinh {self.current_user.name} tham dự kỳ thi {self.exam.name}.")
        else:
            # General attendance
            self.attendance_recorded.emit(self.current_user.id, "", timestamp)
            
            QMessageBox.information(self, "Điểm danh thành công", 
                                   f"Đã điểm danh thành công cho thí sinh {self.current_user.name}.")
        
        # Reset for next user
        self.reset_verification()
    
    def reset_verification(self):
        """Reset the verification state for a new user"""
        self.stop_camera()
        self.scan_btn.setEnabled(True)
        self.confirm_btn.setEnabled(False)
        self.status_label.setText("Chuẩn bị...")
        self.status_label.setStyleSheet("font-weight: bold; color: #1a73e8;")
    
    def stop_camera(self):
        """Stop the camera feed"""
        if self.timer:
            self.timer.stop()
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.scanning = False
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        self.stop_camera()
        event.accept()
