class MonitoringLog:
    def __init__(self, log_id=None, user_id=None, exam_id=None, timestamp=None, 
                 event_type=None, description=None):
        self.log_id = log_id
        self.user_id = user_id
        self.exam_id = exam_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.description = description
    
    @staticmethod
    def from_json(data):
        return MonitoringLog(
            log_id=data.get('id'),
            user_id=data.get('userId'),
            exam_id=data.get('examId'),
            timestamp=data.get('timestamp'),
            event_type=data.get('eventType'),
            description=data.get('description')
        )
    
    def to_json(self):
        data = {
            'userId': self.user_id,
            'examId': self.exam_id,
            'eventType': self.event_type,
            'description': self.description
        }
        if self.timestamp:
            data['timestamp'] = self.timestamp
        if self.log_id:
            data['id'] = self.log_id
        return data