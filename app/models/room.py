class Room:
    def __init__(self, room_id=None, name=None, capacity=None, location=None):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.location = location
    
    @staticmethod
    def from_json(data):
        return Room(
            room_id=data.get('id'),
            name=data.get('name'),
            capacity=data.get('capacity'),
            location=data.get('location')
        )
    
    def to_json(self):
        data = {
            'name': self.name,
            'capacity': self.capacity,
            'location': self.location
        }
        if self.room_id:
            data['id'] = self.room_id
        return data