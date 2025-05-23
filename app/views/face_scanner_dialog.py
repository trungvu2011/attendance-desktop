from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QMessageBox, QFrame, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
import os
import socket
import face_recognition
from app.controllers.cccd_api import CCCDApiController
from app.controllers.cccd_socket_server import CCCDSocketServer
from app.utils.face_recognition import compare_faces
from app.utils.api_service import ApiService
from app.models.user import User

class FaceScannerDialog(QDialog):
    cccd_data_received_signal = pyqtSignal(str, str, dict)
    
    def __init__(self, parent, exam, user=None):
        super().__init__(parent)
        self.exam = exam
        self.user = user
        self.scanning = False
        self.scan_complete = False
        self.camera = None
        self.scan_timer = None
        self.countdown_remaining = 3  # 3 seconds countdown        # CCCD verification related variables
        self.cccd_api = CCCDApiController()
        self.cccd_data = None
        self.cccd_verified = False
        self.face_verified = False
        self.captured_face_path = None
        self.timer = None
        
        # Initialize socket server if not already running
        self.socket_server = CCCDSocketServer.get_instance()
        if not self.socket_server.is_running:
            self.socket_server.start()
        
        # Register for CCCD data callbacks
        print("Registering CCCD data callback in FaceScannerDialog")
        self.cccd_data_received_signal.connect(self.handle_cccd_data_received)
        self.socket_server.register_data_callback(self._cccd_data_callback_threadsafe)
        
        # Create data directories
        self.data_dir = os.path.join("app", "data", "captured_faces")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.setWindowTitle("Xác thực thí sinh")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create title
        title_label = QLabel("Xác thực thí sinh tham dự kỳ thi")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a73e8;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create tabs for different verification methods
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # CCCD Tab
        cccd_tab = QFrame()
        cccd_layout = QVBoxLayout(cccd_tab)
        
        # CCCD instructions
        cccd_instruction = QLabel("Sử dụng ứng dụng di động để quét Căn Cước Công Dân của thí sinh")
        cccd_instruction.setWordWrap(True)
        cccd_instruction.setAlignment(Qt.AlignCenter)
        cccd_instruction.setStyleSheet("color: #555;")
        cccd_layout.addWidget(cccd_instruction)
        
        # IP Address instructions
        ip_instruction = QLabel(f"Hãy nhập IP của máy tính này vào ứng dụng di động: {self.get_local_ip()}")
        ip_instruction.setWordWrap(True)
        ip_instruction.setAlignment(Qt.AlignCenter)
        ip_instruction.setStyleSheet("color: #555; font-weight: bold;")
        cccd_layout.addWidget(ip_instruction)
        
        # CCCD Status
        self.cccd_status = QLabel("Đang chờ dữ liệu CCCD từ ứng dụng di động...")
        self.cccd_status.setAlignment(Qt.AlignCenter)
        self.cccd_status.setStyleSheet("font-weight: bold; color: #1a73e8;")
        cccd_layout.addWidget(self.cccd_status)
        
        # CCCD Image
        self.cccd_image = QLabel()
        self.cccd_image.setAlignment(Qt.AlignCenter)
        self.cccd_image.setMinimumHeight(300)
        self.cccd_image.setStyleSheet("border: 2px solid #ccc; border-radius: 8px;")
        cccd_layout.addWidget(self.cccd_image)
        
        # Add the CCCD tab
        self.tab_widget.addTab(cccd_tab, "Xác thực CCCD")
        
        # Face Recognition Tab
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
        
        # Button layout for face tab
        face_button_layout = QHBoxLayout()
        face_button_layout.addStretch()
        
        self.scan_btn = QPushButton("Bắt đầu quét")
        self.scan_btn.setMinimumWidth(150)
        self.scan_btn.setStyleSheet("""
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
        self.scan_btn.clicked.connect(self.toggle_scanning)
        
        face_button_layout.addWidget(self.scan_btn)
        face_button_layout.addStretch()
        
        face_layout.addLayout(face_button_layout)
        
        # Add the face recognition tab
        self.tab_widget.addTab(face_tab, "Xác thực khuôn mặt")
        
        # Initially disable the face tab until CCCD is verified
        self.tab_widget.setTabEnabled(1, False)
        
        # Main button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.verify_btn = QPushButton("Xác nhận điểm danh")
        self.verify_btn.setMinimumWidth(150)
        self.verify_btn.setEnabled(False)  # Disabled until verification complete
        self.verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #34A853;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
            QPushButton:disabled {
                background-color: #A9A9A9;
            }
        """)
        self.verify_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.verify_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def get_local_ip(self):
        """Get the local IP address to display to the user"""
        import socket
        try:
            # Get the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to a public IP (Google DNS)
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Không thể xác định IP"
    
    def get_logged_in_user(self):
        """Lấy thông tin user đã đăng nhập từ API nội bộ (dùng ApiService để đảm bảo có token)"""
        try:
            api = ApiService.get_instance()
            data = api.get("http://localhost:8080/api/user/profile")
            print(f"API /api/user/profile data: {data}")
            if data and data.get("citizenId"):
                user = User(
                    user_id=data.get("userId"),
                    name=data.get("name"),
                    email=data.get("email"),
                    birth_date=data.get("birth"),
                    citizen_id=data.get("citizenId"),
                    role=data.get("role")
                )
                return user
            else:
                print(f"Không lấy được user profile hoặc thiếu citizenId! Data: {data}")
        except Exception as e:
            print(f"Error fetching logged-in user: {e}")
        return None

    def _cccd_data_callback_threadsafe(self, citizen_id, image_path, data):
        # This is called from the socket server thread, emit signal to main thread
        self.cccd_data_received_signal.emit(citizen_id, image_path, data)

    def on_cccd_data_received(self, citizen_id, image_path, data):
        # Deprecated: do not use directly, use handle_cccd_data_received instead
        pass

    def handle_cccd_data_received(self, citizen_id, image_path, data):
        """Handle CCCD data in the main thread (UI safe)"""
        print(f"CCCD data received in FaceScannerDialog: {citizen_id}")
        print(f"Current user: {self.user.citizen_id if self.user else 'None'}")

        # Nếu chưa có self.user, lấy user đăng nhập từ API
        if not self.user:
            self.user = self.get_logged_in_user()
            if self.user:
                print(f"Fetched logged-in user: {self.user.name} ({self.user.citizen_id})")
            else:
                print("Không lấy được user đăng nhập từ API!")
                self.cccd_status.setText(f"Không thể xác thực CCCD: Không có thông tin người dùng đăng nhập.")
                QMessageBox.warning(self, "Lỗi xác thực CCCD", "Không xác định được người dùng đăng nhập để xác thực CCCD. Hãy đăng nhập lại.")
                return

        # Luôn dùng self.user là người đăng nhập để xác thực CCCD
        if not self.user:
            print("No user (người đăng nhập) được truyền vào dialog!")
            self.cccd_status.setText(f"Không thể xác thực CCCD: Không có thông tin người dùng đăng nhập.")
            QMessageBox.warning(self, "Lỗi xác thực CCCD", "Không xác định được người dùng đăng nhập để xác thực CCCD. Hãy đăng nhập lại.")
            return

        # Check if this CCCD matches the current user
        if self.user.citizen_id == citizen_id:
            print(f"CCCD match found for user: {self.user.name}")
            self.cccd_data = data
            self.cccd_status.setText(f"Đã nhận dữ liệu CCCD: {citizen_id}")
            # Mark CCCD as verified
            self.cccd_verified = True
            # Show the CCCD image
            try:
                pixmap = QPixmap(image_path)
                self.cccd_image.setPixmap(pixmap.scaled(
                    self.cccd_image.width(), 
                    self.cccd_image.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                print(f"CCCD image loaded from: {image_path}")
            except Exception as e:
                print(f"Error loading CCCD image: {e}")
            # Enable the face tab
            self.tab_widget.setTabEnabled(1, True)
            # Auto switch to face tab after a delay
            QTimer.singleShot(2000, lambda: self.tab_widget.setCurrentIndex(1))
        else:
            print(f"CCCD mismatch. Received: {citizen_id}, Expected: {self.user.citizen_id}")
            self.cccd_status.setText(f"CCCD không khớp! Nhận được: {citizen_id}, mong đợi: {self.user.citizen_id}")
            QMessageBox.warning(self, "Lỗi xác thực CCCD", f"CCCD không khớp với tài khoản đăng nhập. Hãy dùng đúng CCCD của bạn.")

    def on_tab_changed(self, index):
        """Handle tab changes"""
        if index == 1 and not self.camera:  # Face recognition tab
            self.start_camera()
    
    def toggle_scanning(self):
        """Start or stop the facial scan process"""
        if not self.scanning:
            # Start scanning
            self.start_camera()
            self.scan_btn.setText("Dừng")
            self.status_label.setText("Đang quét khuôn mặt...")
            self.scanning = True
        else:
            # Stop scanning
            self.stop_camera()
            self.scan_btn.setText("Bắt đầu quét")
            self.status_label.setText("Đã dừng quét")
            self.scanning = False
    
    def start_camera(self):
        """Initialize and start the camera"""
        self.camera = cv2.VideoCapture(0)  # Use default camera (index 0)
        
        if not self.camera.isOpened():
            QMessageBox.warning(self, "Lỗi", "Không thể mở camera. Vui lòng kiểm tra và thử lại.")
            self.reject()
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
            # Use a smaller scale to improve performance (process 1/3 size image)
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.33, fy=0.33)
            face_locations = face_recognition.face_locations(small_frame, model="hog")
            
            # Scale back up the face locations
            face_locations_original = [(top*3, right*3, bottom*3, left*3) 
                                      for (top, right, bottom, left) in face_locations]
            
            # Draw rectangle around faces
            for (top, right, bottom, left) in face_locations_original:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                # Add text showing "Checking Face" to indicate active face detection
                cv2.putText(frame, "Checking Face", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Check if exactly one face is found - this prevents confusion when multiple faces are in frame
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
                    self.scan_complete = True
                    
                    # Capture the current frame and save it
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
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
    
    def check_in_attendance_api(self):
        """Gọi API điểm danh sau khi xác thực khuôn mặt thành công (gửi form-data, không dùng api.post)"""
        import requests
        from app.utils.api_service import ApiService
        api = ApiService.get_instance()
        print(f"[DEBUG] self.user: {self.user}")
        print(f"[DEBUG] self.exam: {self.exam}")
        candidate_id = getattr(self.user, 'user_id', None)
        citizen_card_number = getattr(self.user, 'citizen_id', None)
        exam_id = getattr(self.exam, 'exam_id', None) if hasattr(self.exam, 'exam_id') else self.exam.get('examId') if isinstance(self.exam, dict) else None
        print(f"[DEBUG] candidate_id: {candidate_id}, exam_id: {exam_id}, citizen_card_number: {citizen_card_number}")
        if not (candidate_id and exam_id and citizen_card_number):
            QMessageBox.warning(self, "Lỗi điểm danh", f"Thiếu thông tin để điểm danh (user, exam hoặc CCCD).\nuser: {self.user}\nexam: {self.exam}")
            return False
        url = "http://localhost:8080/api/attendance/check-in"
        data = {
            'candidateId': candidate_id,
            'examId': exam_id,
            'citizenCardNumber': citizen_card_number
        }
        headers = {}
        if api.token:
            headers['Authorization'] = f'Bearer {api.token}'
        try:
            resp = requests.post(url, data=data, headers=headers)
            print(f"[DEBUG] Attendance API response: {resp.status_code} {resp.text}")
            if resp.status_code == 200:
                QMessageBox.information(self, "Điểm danh thành công", "Bạn đã được điểm danh thành công!")
                return True
            else:
                QMessageBox.warning(self, "Lỗi điểm danh", f"Lỗi: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            QMessageBox.warning(self, "Lỗi điểm danh", f"Lỗi khi gọi API điểm danh: {e}")
            return False

    def verify_face_with_cccd(self):
        """Compare the captured face with the CCCD image"""
        if not self.user or not self.cccd_verified or not self.captured_face_path:
            self.status_label.setText("Không thể xác thực: Thiếu dữ liệu CCCD hoặc khuôn mặt")
            self.scan_btn.setEnabled(True)
            return
        
        self.status_label.setText("Đang so sánh khuôn mặt với ảnh CCCD...")
        
        # Get CCCD verification data
        cccd_data = self.socket_server.get_cccd_data(self.user.citizen_id)
        
        if not cccd_data:
            self.status_label.setText("Lỗi: Không tìm thấy dữ liệu CCCD")
            self.scan_btn.setEnabled(True)
            return
          # Compare faces
        result = self.cccd_api.verify_face_with_cccd(self.user.citizen_id, self.captured_face_path)
        
        if result['is_match']:
            self.status_label.setText(f"Xác thực thành công! {result['message']} Độ chính xác: {result['confidence']:.1%}")
            self.status_label.setStyleSheet("font-weight: bold; color: #34A853;")
            self.face_verified = True
            self.verify_btn.setEnabled(True)
            # Gọi API điểm danh tự động
            self.check_in_attendance_api()
        else:
            self.status_label.setText(f"Xác thực thất bại! {result['message']} Độ chính xác: {result['confidence']:.1%}")
            self.status_label.setStyleSheet("font-weight: bold; color: #EA4335;")
            self.scan_btn.setEnabled(True)
    
    def process_successful_scan(self):
        """Process after successful face scan"""
        self.stop_camera()
        
        # In a real application, you would add code to verify the face
        # against the student's registered face in the database
        # For demonstration, we'll just simulate a successful verification
        self.accept()
    
    def stop_camera(self):
        """Stop and release the camera"""
        if self.timer and self.timer.isActive():
            self.timer.stop()
        
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def closeEvent(self, event):
        """Handle close event"""
        self.stop_camera()
        self.socket_server.unregister_data_callback(self.on_cccd_data_received)
        event.accept()
    
    def reject(self):
        """Handle dialog rejection"""
        self.stop_camera()
        self.socket_server.unregister_data_callback(self.on_cccd_data_received)
        super().reject()
    
    def accept(self):
        """Handle dialog acceptance"""
        if not self.cccd_verified or not self.face_verified:
            QMessageBox.warning(self, "Lỗi xác thực", 
                               "Thí sinh chưa được xác thực đầy đủ. Vui lòng hoàn tất quy trình xác thực.")
            return
            
        self.stop_camera()
        self.socket_server.unregister_data_callback(self.on_cccd_data_received)
        super().accept()
