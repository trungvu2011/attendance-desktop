class Exam:
    def __init__(self, exam_id=None, name=None, subject=None, semester=None, exam_date=None, 
                 schedules=None, rooms=None):
        self.exam_id = exam_id
        self.name = name
        self.subject = subject
        self.semester = semester
        self.exam_date = exam_date
        self.schedules = schedules or []
        self.rooms = rooms or []
    
    @staticmethod
    def from_json(data):
        return Exam(
            exam_id=data.get('id'),
            name=data.get('name'),
            subject=data.get('subject'),
            semester=data.get('semester'),
            exam_date=data.get('examDate'),
            schedules=data.get('schedules'),
            rooms=data.get('rooms')
        )
    
    def to_json(self):
        data = {
            'name': self.name,
            'subject': self.subject,
            'semester': self.semester,
            'examDate': self.exam_date,
        }
        if self.schedules:
            data['schedules'] = self.schedules
        if self.rooms:
            data['rooms'] = self.rooms
        if self.exam_id:
            data['id'] = self.exam_id
        return data