from app.utils.api_service import ApiService
from app.models.exam_attendance import ExamAttendance
from config.config import Config
from app.controllers.cccd_api import CCCDApiController
from datetime import datetime

class AttendanceController:
    def __init__(self):
        self.api_service = ApiService.get_instance()
        self.cccd_api = CCCDApiController()
    
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
        # API endpoint cho điểm danh của candidate: /api/attendance/candidate/{userId}
        attendance_candidate_url = f"{Config.API_BASE_URL}/attendance/candidate/{user_id}"
        print(f"=== GET request to: {attendance_candidate_url} ===")
        result = self.api_service.get(attendance_candidate_url)
        print(f"Response: {result}")
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
    
    def mark_attendance_with_face_verification(self, user_id, exam_id, verification_data=None):
        """Mark attendance with face verification using CCCD
        
        Args:
            user_id (str): The ID of the user to mark attendance for
            exam_id (str): The ID of the exam to mark attendance for
            verification_data (dict, optional): Data from face verification
            
        Returns:
            ExamAttendance: The created attendance record if successful, None otherwise
        """
        # Tạo attendance data với định dạng API mới
        attendance = ExamAttendance(
            user_id=user_id,
            exam_id=exam_id,
            status="PRESENT", 
            verification_method="FACE_CCCD",
            citizen_card_verified=True,
            face_verified=True,
            attendance_time=datetime.now().isoformat()
        )
        
        # Thêm verification data nếu có
        if verification_data:
            attendance.verification_data = verification_data
            
        # Gửi lên API
        result = self.api_service.post(Config.ATTENDANCE_URL, attendance.to_json())
        if result:
            return ExamAttendance.from_json(result)
        return None
    
    def mark_cccd_attendance(self, user_id, exam_id, cccd_data=None, face_image_path=None):
        """Mark attendance using CCCD data and face recognition
        
        Args:
            user_id: The user ID
            exam_id: The exam ID
            cccd_data: Additional CCCD data (optional)
            face_image_path: Path to verified face image (optional)
            
        Returns:
            ExamAttendance object if successful, None otherwise
        """
        # API mới có dạng như sau:
        # {
        #    "id": "358a2f35-2942-47b4-8cfe-586eedced359",
        #    "candidate": {
        #        "userId": "...",
        #        "name": "...",
        #        "citizenId": "..."
        #    },
        #    "exam": {
        #        "examId": "..."
        #    },
        #    "citizenCardVerified": true,
        #    "faceVerified": true,
        #    "attendanceTime": "..."
        # }
        
        # Tạo dữ liệu phù hợp với API mới
        attendance_data = {
            "candidate": {
                "userId": user_id
            },
            "exam": {
                "examId": exam_id
            },
            "citizenCardVerified": cccd_data is not None,
            "faceVerified": face_image_path is not None,
            "attendanceTime": datetime.now().isoformat()
        }
        
        # Gửi yêu cầu tới API
        result = self.api_service.post(Config.ATTENDANCE_URL, attendance_data)
        if result:
            return ExamAttendance.from_json(result)
        return None
    
    def mark_attendance_with_cccd(self, user_id, exam_id, status="PRESENT"):
        """Mark attendance with CCCD and face verification"""
        attendance_data = {
            "candidate": {
                "userId": user_id
            },
            "exam": {
                "examId": exam_id
            },
            "citizenCardVerified": True,
            "faceVerified": True,
            "attendanceTime": datetime.now().isoformat()
        }
        
        # Gửi yêu cầu tới API
        result = self.api_service.post(Config.ATTENDANCE_URL, attendance_data)
        if result:
            return ExamAttendance.from_json(result)
        return None