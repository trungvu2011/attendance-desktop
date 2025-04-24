from app.utils.api_service import ApiService
from app.models.exam_attendance import ExamAttendance
from config.config import Config

class AttendanceController:
    def __init__(self):
        self.api_service = ApiService.get_instance()
    
    def get_all_attendance(self):
        """Get all attendance records from the system"""
        result = self.api_service.get(Config.ATTENDANCE_URL)
        if result:
            return [ExamAttendance.from_json(attendance_data) for attendance_data in result]
        return []
    
    def get_attendance_by_id(self, attendance_id):
        """Get an attendance record by ID"""
        result = self.api_service.get(f"{Config.ATTENDANCE_URL}/{attendance_id}")
        if result:
            return ExamAttendance.from_json(result)
        return None
    
    def get_attendance_by_exam(self, exam_id):
        """Get attendance records for a specific exam"""
        result = self.api_service.get(f"{Config.ATTENDANCE_URL}/exam/{exam_id}")
        if result:
            return [ExamAttendance.from_json(attendance_data) for attendance_data in result]
        return []
    
    def get_attendance_by_user(self, user_id):
        """Get attendance records for a specific user"""
        result = self.api_service.get(f"{Config.ATTENDANCE_URL}/user/{user_id}")
        if result:
            return [ExamAttendance.from_json(attendance_data) for attendance_data in result]
        return []
    
    def mark_attendance(self, attendance):
        """Mark attendance for a user in an exam"""
        result = self.api_service.post(Config.ATTENDANCE_URL, attendance.to_json())
        if result:
            return ExamAttendance.from_json(result)
        return None
    
    def update_attendance(self, attendance):
        """Update an existing attendance record"""
        result = self.api_service.put(
            f"{Config.ATTENDANCE_URL}/{attendance.attendance_id}", 
            attendance.to_json()
        )
        if result:
            return ExamAttendance.from_json(result)
        return None