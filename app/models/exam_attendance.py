class ExamAttendance:
    def __init__(self, attendance_id=None, user=None, exam=None, attendance_time=None, status=None, 
                 user_id=None, exam_id=None, check_in_time=None, check_out_time=None, 
                 verification_method=None, verification_data=None,
                 citizen_card_verified=False, face_verified=False):
        self.attendance_id = attendance_id
        self.user = user  # Đối tượng user hoặc thông tin user từ API
        self.exam = exam  # Đối tượng exam hoặc thông tin exam từ API
        self.attendance_time = attendance_time
        self.status = status
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.verification_method = verification_method  # Phương thức xác minh: MANUAL, FACE, FACE_CCCD
        self.verification_data = verification_data  # Dữ liệu xác minh bổ sung (ảnh, độ tin cậy, thời gian, v.v.)
        self.citizen_card_verified = citizen_card_verified  # Xác thực CCCD
        self.face_verified = face_verified  # Xác thực khuôn mặt
        
        # Lưu riêng ID để dễ dàng thao tác
        self.user_id = user_id or (user.get('userId') if isinstance(user, dict) else None)
        self.exam_id = exam_id or (exam.get('examId') if isinstance(exam, dict) else None)
        
    @staticmethod
    def from_json(data):
        """Tạo đối tượng ExamAttendance từ dữ liệu JSON theo định dạng API mới"""
        # Hỗ trợ cả định dạng cũ và mới
        if 'candidate' in data and 'exam' in data:
            # Định dạng mới
            user = data.get('candidate', {})
            exam = data.get('exam', {})
            
            attendance = ExamAttendance(
                attendance_id=data.get('id'),
                user=user,
                exam=exam,
                attendance_time=data.get('attendanceTime'),
                user_id=user.get('userId') if user else None,
                exam_id=exam.get('examId') if exam else None,
                citizen_card_verified=data.get('citizenCardVerified', False),
                face_verified=data.get('faceVerified', False)
            )
            
            # Also set direct field access for convenience
            attendance.candidate = user
            attendance.attendanceTime = data.get('attendanceTime')
            attendance.citizenCardVerified = data.get('citizenCardVerified', False)
            attendance.faceVerified = data.get('faceVerified', False)
            
            return attendance
        else:
            # Định dạng cũ
            return ExamAttendance(
                attendance_id=data.get('attendanceId'),
                user=data.get('user'),
                exam=data.get('exam'),
                attendance_time=data.get('attendanceTime'),
                status=data.get('status'),
                check_in_time=data.get('checkInTime'),
                check_out_time=data.get('checkOutTime'),
                verification_method=data.get('verificationMethod'),
                verification_data=data.get('verificationData')
            )
    
    def to_json(self):
        """Chuyển đổi đối tượng ExamAttendance thành JSON để gửi lên API"""
        return {
            "attendanceId": self.attendance_id,
            "userId": self.user_id,
            "examId": self.exam_id,
            "attendanceTime": self.attendance_time,
            "status": self.status,
            "checkInTime": self.check_in_time,
            "checkOutTime": self.check_out_time,
            "verificationMethod": self.verification_method,
            "verificationData": self.verification_data,
            "citizenCardVerified": self.citizen_card_verified,
            "faceVerified": self.face_verified
        }
    
    def to_dict(self):
        """Chuyển đổi đối tượng thành dictionary"""
        return {
            "attendance_id": self.attendance_id,
            "user": self.user,
            "exam": self.exam,
            "attendance_time": self.attendance_time,
            "status": self.status,
            "user_id": self.user_id,
            "exam_id": self.exam_id,
            "check_in_time": self.check_in_time,
            "check_out_time": self.check_out_time,
            "verification_method": self.verification_method,
            "verification_data": self.verification_data,
            "citizen_card_verified": self.citizen_card_verified,
            "face_verified": self.face_verified
        }
    
    def __str__(self):
        return f"ExamAttendance(id={self.attendance_id}, user_id={self.user_id}, exam_id={self.exam_id}, status={self.status})"
    
    def __repr__(self):
        return self.__str__()