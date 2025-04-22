class ExamAttendance:
    def __init__(self, attendance_id=None, user=None, exam=None, attendance_time=None, status=None, 
                 user_id=None, exam_id=None):
        self.attendance_id = attendance_id
        self.user = user  # Đối tượng user hoặc thông tin user từ API
        self.exam = exam  # Đối tượng exam hoặc thông tin exam từ API
        self.attendance_time = attendance_time
        self.status = status
        
        # Lưu riêng ID để dễ dàng thao tác
        self.user_id = user_id or (user.get('userId') if isinstance(user, dict) else None)
        self.exam_id = exam_id or (exam.get('examId') if isinstance(exam, dict) else None)
    
    @staticmethod
    def from_json(data):
        """Tạo đối tượng ExamAttendance từ dữ liệu JSON theo định dạng API mới"""
        return ExamAttendance(
            attendance_id=data.get('attendanceId'),
            user=data.get('user'),
            exam=data.get('exam'),
            attendance_time=data.get('attendanceTime'),
            status=data.get('status')
        )
    
    def to_json(self):
        """Chuyển đổi đối tượng ExamAttendance thành JSON để gửi lên API"""
        # Khi tạo mới, chỉ cần gửi ID
        data = {
            'status': self.status
        }
        
        # Ưu tiên dùng ID riêng nếu có
        if self.user_id:
            data['userId'] = self.user_id
        elif isinstance(self.user, dict) and 'userId' in self.user:
            data['userId'] = self.user['userId']
            
        if self.exam_id:
            data['examId'] = self.exam_id
        elif isinstance(self.exam, dict) and 'examId' in self.exam:
            data['examId'] = self.exam['examId']
            
        if self.attendance_id:
            data['attendanceId'] = self.attendance_id
            
        return data