"""
Example script to demonstrate the use of AttendanceCCCDScanner
"""

import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from app.views.attendance_cccd_scanner import AttendanceCCCDScannerDialog
from app.controllers.cccd_api import CCCDApiController
from app.controllers.cccd_socket_server import CCCDSocketServer
from flask import Flask, request, jsonify
import time
import socket

# Flask app for API server
flask_app = Flask(__name__)
socket_server = None
cccd_api_controller = None

@flask_app.route('/api/cccd', methods=['POST'])
def receive_cccd_data():
    """Endpoint to receive CCCD data from mobile app"""
    try:
        # Extract data from request
        data = request.json
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Check required fields
        if 'citizenId' not in data or 'faceImage' not in data:
            return jsonify({
                'status': 'error', 
                'message': 'Missing required fields (citizenId, faceImage)'
            }), 400
        
        print(f"Received CCCD data for ID: {data['citizenId']}")
        
        # Process the data using the socket server
        global socket_server
        if socket_server:
            socket_server._process_cccd_data(data)
        
        return jsonify({
            'status': 'success',
            'message': 'CCCD data received successfully'
        })
        
    except Exception as e:
        print(f"Error processing CCCD data: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@flask_app.route('/api/status', methods=['GET'])
def check_status():
    """Endpoint to check server status"""
    return jsonify({
        'status': 'online',
        'message': 'CCCD API Server is running',
        'timestamp': time.time()
    })

# Sample data for demonstration
class User:
    def __init__(self, id, name, citizen_id):
        self.id = id
        self.name = name
        self.citizen_id = citizen_id

class Exam:
    def __init__(self, id, name, date):
        self.id = id
        self.name = name
        self.date = date

# Sample data
sample_users = [
    User("1", "Vũ Đức Trung", "022204000881"),
    User("2", "Nguyễn Hà Anh", "022303004998"),
    User("3", "Nguyễn Hoàng Chiến", "001204038012"),
    User("4", "Phạm Thị D", "022208009012"),
    User("5", "Hoàng Văn E", "022203003456"),
]

sample_exam = Exam("1", "Kỳ thi học kỳ 1", "2023-05-15")

class AttendanceTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo Điểm Danh CCCD")
        self.setGeometry(100, 100, 600, 400)
        
        # Initialize controllers
        global cccd_api_controller, socket_server
        cccd_api_controller = CCCDApiController()
        socket_server = CCCDSocketServer.get_instance()
        if not socket_server.is_running:
            socket_server.start()
        
        # Start Flask server in background thread
        self.flask_thread = threading.Thread(target=self.run_flask_server, daemon=True)
        self.flask_thread.start()
        
        # Wait briefly for Flask to start
        time.sleep(1)
        
        # Display connection information
        self.show_connection_info()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Demo Điểm Danh bằng CCCD và Nhận Diện Khuôn Mặt")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Đây là ứng dụng demo cho hệ thống điểm danh sử dụng CCCD và nhận diện khuôn mặt.\n\n"
            "Quy trình làm việc:\n"
            "1. Sử dụng ứng dụng di động để quét CCCD\n"
            "2. Gửi dữ liệu CCCD đến hệ thống điểm danh (ứng dụng này)\n"
            "3. Xác thực khuôn mặt bằng camera\n"
            "4. Xác nhận điểm danh\n\n"
            "Hướng dẫn sử dụng:\n"
            "- Nhấn nút 'Mở màn hình điểm danh' để bắt đầu quy trình\n"
            "- Trên màn hình điểm danh, chọn thí sinh cần điểm danh\n"
            "- Sử dụng ứng dụng di động để quét CCCD và gửi dữ liệu\n"
            "- Khi dữ liệu CCCD được nhận, nhấn 'Bắt đầu quét khuôn mặt' để xác thực"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 20px;")
        layout.addWidget(instructions)
        
        # Open attendance dialog button
        open_btn = QPushButton("Mở màn hình điểm danh")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
        """)
        open_btn.clicked.connect(self.open_attendance_dialog)
        layout.addWidget(open_btn)
        
    def open_attendance_dialog(self):
        """Open the attendance dialog"""
        dialog = AttendanceCCCDScannerDialog(self, sample_exam, sample_users)
        dialog.attendance_recorded.connect(self.on_attendance_recorded)
        dialog.exec_()
    
    def on_attendance_recorded(self, user_id, exam_id, timestamp):
        """Handle attendance recording"""
        print(f"Attendance recorded for user {user_id} in exam {exam_id} at {timestamp}")
        
    def run_flask_server(self):
        """Run Flask API server to receive requests from mobile app"""
        try:
            # Get local IP address for display
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to an external server to determine the local IP
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            print(f"Starting Flask API server on: http://{local_ip}:5000")
            print(f"Mobile app should connect to: {local_ip}")
            print(f"To test the API, you can use: GET http://{local_ip}:5000/api/status")
            
            # Run Flask on all network interfaces
            flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Failed to start Flask server: {e}")
        
    def show_connection_info(self):
        """Show connection information to help user connect from mobile app"""
        try:
            # Get local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Thông tin kết nối")
            msg.setText("Thông tin kết nối cho ứng dụng di động")
            
            # Format detailed instructions
            details = (
                f"Địa chỉ IP của máy tính: {local_ip}\n"
                f"Cổng API: 5000\n"
                f"Cổng Socket: 9999\n\n"
                f"Hướng dẫn cài đặt trên ứng dụng di động:\n"
                f"1. Mở ứng dụng CCCD Vietnam trên điện thoại\n"
                f"2. Nhập địa chỉ IP: {local_ip}\n"
                f"3. Nhấn nút 'Kết nối' hoặc 'Kiểm tra kết nối'\n\n"
                f"Lưu ý: Đảm bảo điện thoại và máy tính kết nối cùng một mạng WiFi\n\n"
                f"Nếu không kết nối được, hãy kiểm tra:\n"
                f"- Tường lửa Windows có cho phép kết nối đến cổng 5000 và 9999\n"
                f"- Phần mềm diệt virus không chặn kết nối\n"
                f"- Điện thoại và máy tính nằm trong cùng một mạng"
            )
            
            msg.setDetailedText(details)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
        except Exception as e:
            print(f"Error showing connection info: {e}")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceTestWindow()
    window.show()
    sys.exit(app.exec_())
