class MonitoringLog:
    def __init__(self, log_id=None, user_id=None, exam_id=None, timestamp=None, 
                 event_type=None, message=None):
        self.log_id = log_id
        self.user_id = user_id
        self.exam_id = exam_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.message = message
    
    @staticmethod
    def from_json(data):
        """Tạo đối tượng MonitoringLog từ dữ liệu JSON theo định dạng API mới"""
        return MonitoringLog(
            log_id=data.get('logId'),
            user_id=data.get('userId'),
            exam_id=data.get('examId'),
            timestamp=data.get('timestamp'),
            event_type=data.get('eventType'),
            message=data.get('message')
        )
    
    def to_json(self):
        """Chuyển đổi đối tượng MonitoringLog thành JSON để gửi lên API"""
        data = {
            'userId': self.user_id,
            'examId': self.exam_id,
            'eventType': self.event_type,
            'message': self.message
        }
        if self.timestamp:
            data['timestamp'] = self.timestamp
        if self.log_id:
            data['logId'] = self.log_id
        return data