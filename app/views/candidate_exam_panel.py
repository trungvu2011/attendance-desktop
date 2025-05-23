from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from app.models.exam import Exam
from config.config import Config
# These imports will be used in the show_exam_detail method
# We don't import them at the top to avoid circular imports

class CandidateExamPanel(QWidget):
    def __init__(self, exam_controller):
        super().__init__()
        self.exam_controller = exam_controller
        self.exams = []        
        self.init_ui()
        self.load_exams()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Kỳ thi của tôi")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.clicked.connect(self.load_exams)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Exam table
        self.exam_table = QTableWidget()
        self.exam_table.setColumnCount(7)  # ID, Name, Subject, Semester, Date, Room, Schedule
        self.exam_table.setHorizontalHeaderLabels(
            ["ID", "Tên kỳ thi", "Môn học", "Học kỳ", "Ngày thi", "Phòng", "Kíp thi"]
        )
        self.exam_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.exam_table.horizontalHeader().setStretchLastSection(True)
        self.exam_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.exam_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Connect double click signal to show exam details
        self.exam_table.doubleClicked.connect(self.show_exam_detail)
        
        main_layout.addWidget(self.exam_table)
        
        # Set layout
        self.setLayout(main_layout)
    
    def load_exams(self):
        self.exams = self.exam_controller.get_my_exams()
        self.populate_exam_table()
    
    def populate_exam_table(self):
        self.exam_table.setRowCount(0)
        
        for row, exam in enumerate(self.exams):
            self.exam_table.insertRow(row)
            
            # Set exam details
            self.exam_table.setItem(row, 0, QTableWidgetItem(str(exam.exam_id)))
            self.exam_table.setItem(row, 1, QTableWidgetItem(exam.name))
            self.exam_table.setItem(row, 2, QTableWidgetItem(exam.subject))
            self.exam_table.setItem(row, 3, QTableWidgetItem(exam.semester))
            self.exam_table.setItem(row, 4, QTableWidgetItem(exam.exam_date))
            
            # Thêm cột Room và Schedule
            room_display = exam.get_room_display() if hasattr(exam, 'get_room_display') else ""
            schedule_name = exam.get_schedule_name() if hasattr(exam, 'get_schedule_name') else ""
            self.exam_table.setItem(row, 5, QTableWidgetItem(room_display))
            self.exam_table.setItem(row, 6, QTableWidgetItem(schedule_name))
    
    def show_exam_detail(self, index):
        """Show exam detail dialog when an exam is double-clicked"""
        row = index.row()
        exam_id = self.exam_table.item(row, 0).text()  # Do not cast to int, keep as string (UUID or int)
        
        # Get the selected exam object
        selected_exam = None
        for exam in self.exams:
            if str(exam.exam_id) == exam_id:
                selected_exam = exam
                break
        
        if selected_exam:
            from app.views.exam_detail_dialog import ExamDetailDialog
            dialog = ExamDetailDialog(self, selected_exam, self.exam_controller)
            dialog.exec_()