from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QComboBox, QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from app.models.monitoring_log import MonitoringLog
from config.config import Config
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
        title_label = QLabel("Monitoring System")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        
        # Date filter
        self.date_filter_label = QLabel("Filter by Date:")
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        
        filter_layout.addWidget(self.date_filter_label)
        filter_layout.addWidget(self.date_filter)
        
        # Event type filter
        self.event_filter_label = QLabel("Filter by Event:")
        self.event_filter = QComboBox()
        self.event_filter.addItem("All Events", None)
        self.event_filter.addItem("Login", "LOGIN")
        self.event_filter.addItem("Logout", "LOGOUT")
        self.event_filter.addItem("Attendance", "ATTENDANCE")
        self.event_filter.addItem("Camera Activity", "CAMERA")
        self.event_filter.addItem("System", "SYSTEM")
        
        filter_layout.addWidget(self.event_filter_label)
        filter_layout.addWidget(self.event_filter)
        
        # Apply filter button
        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_logs)
        
        filter_layout.addStretch()
        filter_layout.addWidget(self.apply_filter_btn)
        filter_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels(
            ["ID", "User", "Exam", "Timestamp", "Event Type", "Description"]
        )
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.horizontalHeader().setStretchLastSection(True)
        
        main_layout.addWidget(self.log_table)
        
        # Status section
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        # Camera Status
        self.camera_status_label = QLabel("Camera Status:")
        self.camera_status = QLabel("Inactive")
        self.camera_status.setStyleSheet("color: red;")
        
        camera_btn = QPushButton("Start Camera")
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
        self.status_label.setText(f"Loaded {len(self.logs)} log entries")
    
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
        self.status_label.setText(f"Filtered: {len(self.logs)} log entries")
    
    def populate_log_table(self):
        self.log_table.setRowCount(0)
        
        for row, log in enumerate(self.logs):
            self.log_table.insertRow(row)
            
            # Set log details
            self.log_table.setItem(row, 0, QTableWidgetItem(str(log.log_id)))
            self.log_table.setItem(row, 1, QTableWidgetItem(str(log.user_id)))
            self.log_table.setItem(row, 2, QTableWidgetItem(str(log.exam_id)))
            self.log_table.setItem(row, 3, QTableWidgetItem(log.timestamp))
            self.log_table.setItem(row, 4, QTableWidgetItem(log.event_type))
            self.log_table.setItem(row, 5, QTableWidgetItem(log.description))
    
    def toggle_camera(self):
        # This would typically start/stop camera monitoring
        sender = self.sender()
        
        if sender.text() == "Start Camera":
            sender.setText("Stop Camera")
            self.camera_status.setText("Active")
            self.camera_status.setStyleSheet("color: green;")
            QMessageBox.information(self, "Camera", "Camera monitoring started")
        else:
            sender.setText("Start Camera")
            self.camera_status.setText("Inactive")
            self.camera_status.setStyleSheet("color: red;")
            QMessageBox.information(self, "Camera", "Camera monitoring stopped")
    
    def get_sample_logs(self):
        # Generate sample logs for demonstration
        sample_logs = []
        
        # Create timestamps for the last week
        now = datetime.datetime.now()
        
        for i in range(20):
            # Random timestamp in the last week
            days_ago = datetime.timedelta(days=i % 7)
            timestamp = (now - days_ago).strftime("%Y-%m-%d %H:%M:%S")
            
            # Random event type
            event_types = ["LOGIN", "LOGOUT", "ATTENDANCE", "CAMERA", "SYSTEM"]
            event_type = event_types[i % len(event_types)]
            
            # Description based on event type
            descriptions = {
                "LOGIN": "User logged in",
                "LOGOUT": "User logged out",
                "ATTENDANCE": "Attendance marked for exam",
                "CAMERA": "Face detected in camera feed",
                "SYSTEM": "System status check"
            }
            
            log = MonitoringLog(
                log_id=i + 1,
                user_id=i % 5 + 1,  # User IDs 1-5
                exam_id=i % 3 + 1,  # Exam IDs 1-3
                timestamp=timestamp,
                event_type=event_type,
                description=descriptions[event_type]
            )
            
            sample_logs.append(log)
        
        return sample_logs