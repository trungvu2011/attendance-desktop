class Room:
    def __init__(self, room_id=None, name=None, capacity=None, location=None):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.location = location
    
    @staticmethod
    def from_json(data):
        """Tạo đối tượng Room từ dữ liệu JSON theo định dạng API mới"""
        return Room(
            room_id=data.get('roomId'),
            name=data.get('name'),
            capacity=data.get('capacity'),
            location=data.get('location')
        )
    
    def to_json(self):
        """Chuyển đổi đối tượng Room thành JSON để gửi lên API"""
        data = {
            'name': self.name
        }
        if self.capacity:
            data['capacity'] = self.capacity
        if self.location:
            data['location'] = self.location
        if self.room_id:
            data['roomId'] = self.room_id
        return data