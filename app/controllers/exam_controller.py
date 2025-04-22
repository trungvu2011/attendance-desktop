from app.utils.api_service import ApiService
from app.models.exam import Exam
from config.config import Config

class ExamController:
    def __init__(self):
        self.api_service = ApiService()
    
    def get_all_exams(self):
        """Get all exams from the system"""
        result = self.api_service.get(Config.EXAMS_URL)
        if result:
            return [Exam.from_json(exam_data) for exam_data in result]
        return []
    
    def get_exam_by_id(self, exam_id):
        """Get an exam by ID"""
        result = self.api_service.get(f"{Config.EXAMS_URL}/{exam_id}")
        if result:
            return Exam.from_json(result)
        return None
    
    def create_exam(self, exam):
        """Create a new exam"""
        result = self.api_service.post(Config.EXAMS_URL, exam.to_json())
        if result:
            return Exam.from_json(result)
        return None
    
    def update_exam(self, exam):
        """Update an existing exam"""
        result = self.api_service.put(f"{Config.EXAMS_URL}/{exam.exam_id}", exam.to_json())
        if result:
            return Exam.from_json(result)
        return None
    
    def delete_exam(self, exam_id):
        """Delete an exam"""
        return self.api_service.delete(f"{Config.EXAMS_URL}/{exam_id}")
    
    def validate_exam(self, exam):
        """Validate exam data"""
        if not exam.name or not exam.subject or not exam.semester or not exam.exam_date:
            return False, "All fields must be filled"
        return True, "Validation passed"