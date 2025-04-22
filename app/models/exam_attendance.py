class ExamAttendance:
    def __init__(self, attendance_id=None, user_id=None, exam_id=None, check_in_time=None, 
                 check_out_time=None, status=None):
        self.attendance_id = attendance_id
        self.user_id = user_id
        self.exam_id = exam_id
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.status = status
    
    @staticmethod
    def from_json(data):
        return ExamAttendance(
            attendance_id=data.get('id'),
            user_id=data.get('userId'),
            exam_id=data.get('examId'),
            check_in_time=data.get('checkInTime'),
            check_out_time=data.get('checkOutTime'),
            status=data.get('status')
        )
    
    def to_json(self):
        data = {
            'userId': self.user_id,
            'examId': self.exam_id,
            'status': self.status
        }
        if self.check_in_time:
            data['checkInTime'] = self.check_in_time
        if self.check_out_time:
            data['checkOutTime'] = self.check_out_time
        if self.attendance_id:
            data['id'] = self.attendance_id
        return data