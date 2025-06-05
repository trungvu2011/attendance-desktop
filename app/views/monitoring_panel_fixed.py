from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QComboBox, QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from app.models.monitoring_log import MonitoringLog
from config.config import Config
from app.utils.datetime_utils import get_current_time, format_datetime_vietnamese, format_timestamp_for_display
import datetime

class MonitoringPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.logs = []
        
        self.init_ui()
        self.load_logs()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Hệ thống Giám sát")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        
        # Date filter
        self.date_filter_label = QLabel("Lọc theo ngày:")
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        
        filter_layout.addWidget(self.date_filter_label)
        filter_layout.addWidget(self.date_filter)
        
        # Event type filter
        self.event_filter_label = QLabel("Lọc theo sự kiện:")
        self.event_filter = QComboBox()
        self.event_filter.addItem("Tất cả sự kiện", None)
        self.event_filter.addItem("Đăng nhập", "LOGIN")
        self.event_filter.addItem("Đăng xuất", "LOGOUT")
        self.event_filter.addItem("Điểm danh", "ATTENDANCE")
        self.event_filter.addItem("Hoạt động Camera", "CAMERA")
        self.event_filter.addItem("Hệ thống", "SYSTEM")
        
        filter_layout.addWidget(self.event_filter_label)
        filter_layout.addWidget(self.event_filter)
        
        # Apply filter button
        self.apply_filter_btn = QPushButton("Áp dụng bộ lọc")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        
        # Refresh button
        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.clicked.connect(self.load_logs)
        
        filter_layout.addStretch()
        filter_layout.addWidget(self.apply_filter_btn)
        filter_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels(
            ["ID", "Người dùng", "Kỳ thi", "Thời gian", "Loại sự kiện", "Mô tả"]
        )
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.horizontalHeader().setStretchLastSection(True)
        
        main_layout.addWidget(self.log_table)
        
        # Status section
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Sẵn sàng")
        status_layout.addWidget(self.status_label)
        
        # Camera Status
        self.camera_status_label = QLabel("Trạng thái Camera:")
        self.camera_status = QLabel("Không hoạt động")
        self.camera_status.setStyleSheet("color: red;")
        
        camera_btn = QPushButton("Bật Camera")
        camera_btn.clicked.connect(self.toggle_camera)
        
        status_layout.addStretch()
        status_layout.addWidget(self.camera_status_label)
        status_layout.addWidget(self.camera_status)
        status_layout.addWidget(camera_btn)
        
        main_layout.addLayout(status_layout)
        
        # Set layout
        self.setLayout(main_layout)
    
    def load_logs(self):
        # This would typically fetch logs from the server
        # For now, we'll create some sample data
        self.logs = self.get_sample_logs()
        self.populate_log_table()
        self.status_label.setText(f"Đã tải {len(self.logs)} bản ghi nhật ký")
    
    def apply_filters(self):
        # Get filter values
        date = self.date_filter.date().toString("yyyy-MM-dd")
        event_type = self.event_filter.currentData()
        
        # Apply filters
        filtered_logs = []
        for log in self.get_sample_logs():
            # Check date filter
            if date and log.timestamp and date in log.timestamp:
                # Check event type filter
                if not event_type or log.event_type == event_type:
                    filtered_logs.append(log)
        
        self.logs = filtered_logs
        self.populate_log_table()
        self.status_label.setText(f"Đã lọc: {len(self.logs)} bản ghi nhật ký")
    
    def populate_log_table(self):
        self.log_table.setRowCount(0)
        
        for row, log in enumerate(self.logs):
            self.log_table.insertRow(row)
            
            # Set log details
            self.log_table.setItem(row, 0, QTableWidgetItem(str(log.log_id)))
            self.log_table.setItem(row, 1, QTableWidgetItem(str(log.user_id)))
            self.log_table.setItem(row, 2, QTableWidgetItem(str(log.exam_id)))
            # Format timestamp for better readability
            formatted_timestamp = format_timestamp_for_display(log.timestamp)
            self.log_table.setItem(row, 3, QTableWidgetItem(formatted_timestamp))
            self.log_table.setItem(row, 4, QTableWidgetItem(log.event_type))
            self.log_table.setItem(row, 5, QTableWidgetItem(log.message))
    
    def toggle_camera(self):
        # This would typically start/stop camera monitoring
        sender = self.sender()
        
        if sender.text() == "Bật Camera":
            sender.setText("Tắt Camera")
            self.camera_status.setText("Đang hoạt động")
            self.camera_status.setStyleSheet("color: green;")
            QMessageBox.information(self, "Camera", "Đã bắt đầu giám sát camera")
        else:
            sender.setText("Bật Camera")
            self.camera_status.setText("Không hoạt động")
            self.camera_status.setStyleSheet("color: red;")
            QMessageBox.information(self, "Camera", "Đã dừng giám sát camera")
    
    def get_sample_logs(self):
        # Generate sample logs for demonstration
        sample_logs = []
        
        # Create timestamps for the last week
        now = get_current_time()
        
        for i in range(20):
            # Random timestamp in the last week
            days_ago = datetime.timedelta(days=i % 7)
            timestamp = format_datetime_vietnamese(now - days_ago, 'full')
            
            # Random event type
            event_types = ["LOGIN", "LOGOUT", "ATTENDANCE", "CAMERA", "SYSTEM"]
            event_type = event_types[i % len(event_types)]
            
            # Message based on event type
            messages = {
                "LOGIN": "Người dùng đăng nhập vào hệ thống",
                "LOGOUT": "Người dùng đăng xuất khỏi hệ thống", 
                "ATTENDANCE": "Đã ghi nhận điểm danh cho kỳ thi",
                "CAMERA": "Phát hiện khuôn mặt qua camera",
                "SYSTEM": "Kiểm tra trạng thái hệ thống"
            }
            
            log = MonitoringLog(
                log_id=i + 1,
                user_id=i % 5 + 1,  # User IDs 1-5
                exam_id=i % 3 + 1,  # Exam IDs 1-3
                timestamp=timestamp,
                event_type=event_type,
                message=messages[event_type]
            )
            
            sample_logs.append(log)
        
        return sample_logs
