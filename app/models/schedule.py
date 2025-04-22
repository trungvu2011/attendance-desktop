class Schedule:
    STATUS_UPCOMING = "UPCOMING"
    STATUS_ONGOING = "ONGOING"
    STATUS_COMPLETED = "COMPLETED"
    
    def __init__(self, schedule_id=None, start_time=None, end_time=None, status=None, exam_id=None):
        self.schedule_id = schedule_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.exam_id = exam_id
    
    @staticmethod
    def from_json(data):
        """Tạo đối tượng Schedule từ dữ liệu JSON theo định dạng API mới"""
        return Schedule(
            schedule_id=data.get('scheduleId'),
            start_time=data.get('startTime'),
            end_time=data.get('endTime'),
            status=data.get('status'),
            exam_id=data.get('examId')
        )
    
    def to_json(self):
        """Chuyển đổi đối tượng Schedule thành JSON để gửi lên API"""
        data = {
            'startTime': self.start_time,
            'endTime': self.end_time,
            'status': self.status
        }
        if self.exam_id:
            data['examId'] = self.exam_id
        if self.schedule_id:
            data['scheduleId'] = self.schedule_id
        return data