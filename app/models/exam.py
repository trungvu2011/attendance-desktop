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
        # Thêm trường room_display kết hợp từ building và name
        self.room_display = self._get_room_display()
        # Thêm trường schedule_name (kíp thi)
        self.schedule_name = self._get_schedule_name()
    
    def _get_room_display(self):
        """Tạo trường hiển thị phòng thi theo format: building-name (ví dụ: D3-301)"""
        if not self.room:
            return ""
        
        room_name = ""
        building = ""
        
        if isinstance(self.room, dict):
            room_name = self.room.get('name', '')
            building = self.room.get('building', '')
        else:
            room_name = getattr(self.room, 'name', '')
            building = getattr(self.room, 'building', '')
            
        if building and room_name:
            return f"{building}-{room_name}"
        elif room_name:
            return room_name
        return ""
    
    def _get_schedule_name(self):
        """Lấy tên kíp thi"""
        if not self.schedule:
            return ""
        if isinstance(self.schedule, dict):
            return self.schedule.get('name', '')
        return getattr(self.schedule, 'name', '')
    
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
        
        # Trường scheduleId - hỗ trợ cả object schedule và scheduleId riêng lẻ
        if isinstance(self.schedule, dict) and 'scheduleId' in self.schedule:
            data['scheduleId'] = self.schedule['scheduleId']
        elif hasattr(self.schedule, 'scheduleId'):
            data['scheduleId'] = self.schedule.scheduleId
        elif isinstance(self.schedule, int):
            data['scheduleId'] = self.schedule
            
        # Trường roomId - hỗ trợ cả object room và roomId riêng lẻ
        if isinstance(self.room, dict) and 'roomId' in self.room:
            data['roomId'] = self.room['roomId']
        elif hasattr(self.room, 'roomId'):
            data['roomId'] = self.room.roomId
        elif isinstance(self.room, str):
            data['roomId'] = self.room
            
        if self.exam_id:
            data['examId'] = self.exam_id
            
        return data
    
    def get_schedule_name(self):
        """Lấy tên kíp thi"""
        return self.schedule_name
    
    def get_schedule_time(self):
        """Lấy thời gian của kíp thi theo format: startTime - endTime"""
        if not self.schedule:
            return ""
        
        start_time = ""
        end_time = ""
        
        if isinstance(self.schedule, dict):
            start_time = self.schedule.get('startTime', '')
            end_time = self.schedule.get('endTime', '')
        else:
            start_time = getattr(self.schedule, 'startTime', '')
            end_time = getattr(self.schedule, 'endTime', '')
            
        if start_time and end_time:
            return f"{start_time} - {end_time}"
        return ""
    
    def get_room_location(self):
        """Lấy địa điểm phòng thi theo format đầy đủ: name - building"""
        if not self.room:
            return ""
        
        room_name = ""
        building = ""
        
        if isinstance(self.room, dict):
            room_name = self.room.get('name', '')
            building = self.room.get('building', '')
        else:
            room_name = getattr(self.room, 'name', '')
            building = getattr(self.room, 'building', '')
            
        if room_name and building:
            return f"{room_name} - {building}"
        elif room_name:
            return room_name
        return ""
    
    def get_room_display(self):
        """Lấy địa điểm phòng thi theo format ngắn gọn: building-name"""
        return self.room_display