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
            
            return ExamAttendance(
                attendance_id=data.get('id'),
                user=user,
                exam=exam,
                attendance_time=data.get('attendanceTime'),
                user_id=user.get('userId') if user else None,
                exam_id=exam.get('examId') if exam else None,
                citizen_card_verified=data.get('citizenCardVerified', False),
                face_verified=data.get('faceVerified', False)
            )
        else:
            # Định dạng cũ
            return ExamAttendance(
                attendance_id=data.get('attendanceId'),
                user=data.get('user'),
                exam=data.get('exam'),
                attendance_time=data.get('attendanceTime'),
                status=data.get('status'),
                check_in_time=data.get('checkInTime'),                check_out_time=data.get('checkOutTime'),
                verification_method=data.get('verificationMethod'),
                verification_data=data.get('verificationData')
            )
    
    def to_json(self):
        """Chuyển đổi đối tượng ExamAttendance thành JSON để gửi lên API"""
        # Cấu trúc JSON mới
        data = {}
        
        # Thêm thông tin thí sinh
        candidate_data = {}
        if self.user_id:
            candidate_data['userId'] = self.user_id
        elif isinstance(self.user, dict) and 'userId' in self.user:
            candidate_data['userId'] = self.user['userId']
            
        if isinstance(self.user, dict):
            if 'name' in self.user:
                candidate_data['name'] = self.user['name']
            if 'citizenId' in self.user:
                candidate_data['citizenId'] = self.user['citizenId']
        
        if candidate_data:
            data['candidate'] = candidate_data
            
        # Thêm thông tin kỳ thi
        exam_data = {}
        if self.exam_id:
            exam_data['examId'] = self.exam_id
        elif isinstance(self.exam, dict) and 'examId' in self.exam:
            exam_data['examId'] = self.exam['examId']
            
        if isinstance(self.exam, dict) and 'name' in self.exam:
            exam_data['name'] = self.exam['name']
            
        if exam_data:
            data['exam'] = exam_data
            
        # Thêm ID cho cập nhật
        if self.attendance_id:
            data['id'] = self.attendance_id
        
        # Thêm thông tin xác thực
        data['citizenCardVerified'] = self.citizen_card_verified
        data['faceVerified'] = self.face_verified
        
        # Thêm thời gian điểm danh
        if self.attendance_time:
            data['attendanceTime'] = self.attendance_time
        
        # Các trường cũ giữ lại cho khả năng tương thích
        if self.verification_method:
            data['verificationMethod'] = self.verification_method
            
        if self.verification_data:
            data['verificationData'] = self.verification_data
            
        if self.check_in_time:
            data['checkInTime'] = self.check_in_time
            
        if self.check_out_time:
            data['checkOutTime'] = self.check_out_time
            
        if self.status:
            data['status'] = self.status
            
        return data