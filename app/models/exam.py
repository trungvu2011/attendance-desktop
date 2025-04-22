class Exam:
    def __init__(self, exam_id=None, name=None, subject=None, semester=None, exam_date=None, 
                 schedule=None, room=None):
        self.exam_id = exam_id
        self.name = name
        self.subject = subject
        self.semester = semester
        self.exam_date = exam_date
        self.schedule = schedule
        self.room = room
    
    @staticmethod
    def from_json(data):
        """Tạo đối tượng Exam từ dữ liệu JSON theo định dạng API mới"""
        return Exam(
            exam_id=data.get('examId'),
            name=data.get('name'),
            subject=data.get('subject'),
            semester=data.get('semester'),
            exam_date=data.get('date'),
            schedule=data.get('schedule'),
            room=data.get('room')
        )
    
    def to_json(self):
        """Chuyển đổi đối tượng Exam thành JSON để gửi lên API"""
        data = {
            'name': self.name,
            'subject': self.subject,
            'semester': self.semester,
            'date': self.exam_date,
        }
        
        # Trường scheduleId và roomId chỉ cần cho request tạo mới
        if isinstance(self.schedule, dict) and 'scheduleId' in self.schedule:
            data['scheduleId'] = self.schedule['scheduleId']
        elif isinstance(self.schedule, int):
            data['scheduleId'] = self.schedule
            
        if isinstance(self.room, dict) and 'roomId' in self.room:
            data['roomId'] = self.room['roomId']
        elif isinstance(self.room, int):
            data['roomId'] = self.room
            
        if self.exam_id:
            data['examId'] = self.exam_id
            
        return data