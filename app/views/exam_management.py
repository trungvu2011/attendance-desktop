from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QLineEdit, QDateEdit,
                              QMessageBox)
from PyQt5.QtCore import Qt, QDate
from app.models.exam import Exam
from config.config import Config

class ExamManagementPanel(QWidget):
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
        title_label = QLabel("Exam Management")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        self.add_exam_btn = QPushButton("Add Exam")
        self.add_exam_btn.clicked.connect(self.show_add_exam_dialog)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_exams)
        
        button_layout.addWidget(self.add_exam_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Exam table
        self.exam_table = QTableWidget()
        self.exam_table.setColumnCount(8)  # Changed from 6 to 8 to add room and schedule columns
        self.exam_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Subject", "Semester", "Exam Date", "Room", "Schedule", "Actions"]
        )
        self.exam_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.exam_table.horizontalHeader().setStretchLastSection(True)
        
        main_layout.addWidget(self.exam_table)
        
        # Set layout
        self.setLayout(main_layout)
    
    def load_exams(self):
        self.exams = self.exam_controller.get_all_exams()
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
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, e=exam: self.show_edit_exam_dialog(e))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, e=exam: self.delete_exam(e))
            
            view_schedules_btn = QPushButton("Schedules")
            view_schedules_btn.clicked.connect(lambda checked, e=exam: self.view_schedules(e))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(view_schedules_btn)
            
            action_widget.setLayout(action_layout)
            self.exam_table.setCellWidget(row, 7, action_widget)  # Changed from 5 to 7
    
    def show_add_exam_dialog(self):
        dialog = ExamDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            exam = dialog.get_exam()
            valid, message = self.exam_controller.validate_exam(exam)
            
            if valid:
                created_exam = self.exam_controller.create_exam(exam)
                if created_exam:
                    QMessageBox.information(self, "Success", "Exam created successfully.")
                    self.load_exams()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create exam.")
            else:
                QMessageBox.warning(self, "Validation Error", message)
    
    def show_edit_exam_dialog(self, exam):
        dialog = ExamDialog(parent=self, exam=exam)
        if dialog.exec_() == QDialog.Accepted:
            updated_exam = dialog.get_exam()
            valid, message = self.exam_controller.validate_exam(updated_exam)
            
            if valid:
                result = self.exam_controller.update_exam(updated_exam)
                if result:
                    QMessageBox.information(self, "Success", "Exam updated successfully.")
                    self.load_exams()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update exam.")
            else:
                QMessageBox.warning(self, "Validation Error", message)
    
    def delete_exam(self, exam):
        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            f'Are you sure you want to delete exam {exam.name}?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.exam_controller.delete_exam(exam.exam_id)
            if result:
                QMessageBox.information(self, "Success", "Exam deleted successfully.")
                self.load_exams()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete exam.")
    
    def view_schedules(self, exam):
        QMessageBox.information(
            self, 
            "View Schedules",
            f"This will open a dialog to manage schedules for exam: {exam.name}"
        )
        # This would typically open a dialog to manage schedules
        # We'll implement this in a future iteration


class ExamDialog(QDialog):
    def __init__(self, parent=None, exam=None):
        super().__init__(parent)
        self.exam = exam
        
        self.init_ui()
        if exam:
            self.populate_form()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Add Exam" if not self.exam else "Edit Exam")
        self.resize(400, 300)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        # Subject field
        self.subject_input = QLineEdit()
        form_layout.addRow("Subject:", self.subject_input)
        
        # Semester field
        self.semester_input = QLineEdit()
        form_layout.addRow("Semester:", self.semester_input)
        
        # Exam date field
        self.exam_date_input = QDateEdit()
        self.exam_date_input.setCalendarPopup(True)
        self.exam_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Exam Date:", self.exam_date_input)
        
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
    
    def populate_form(self):
        # Populate form with exam data
        self.name_input.setText(self.exam.name)
        self.subject_input.setText(self.exam.subject)
        self.semester_input.setText(self.exam.semester)
        
        # Set exam date if available
        if self.exam.exam_date:
            try:
                # Try to parse date in format YYYY-MM-DD
                date_parts = self.exam.exam_date.split('-')
                if len(date_parts) == 3:
                    year, month, day = map(int, date_parts)
                    self.exam_date_input.setDate(QDate(year, month, day))
            except:
                # If parsing fails, use current date
                self.exam_date_input.setDate(QDate.currentDate())
    
    def get_exam(self):
        # Create a new exam or update existing one
        name = self.name_input.text()
        subject = self.subject_input.text()
        semester = self.semester_input.text()
        exam_date = self.exam_date_input.date().toString("yyyy-MM-dd")
        
        if self.exam:
            # Update existing exam
            exam = Exam(
                exam_id=self.exam.exam_id,
                name=name,
                subject=subject,
                semester=semester,
                exam_date=exam_date,
                schedules=self.exam.schedules,
                rooms=self.exam.rooms
            )
        else:
            # Create new exam
            exam = Exam(
                name=name,
                subject=subject,
                semester=semester,
                exam_date=exam_date
            )
        
        return exam