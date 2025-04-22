class User:
    def __init__(self, user_id=None, name=None, email=None, password=None, birth_date=None, 
                 citizen_id=None, role=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.birth_date = birth_date
        self.citizen_id = citizen_id
        self.role = role
    
    @staticmethod
    def from_json(data):
        return User(
            user_id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            birth_date=data.get('birthDate'),
            citizen_id=data.get('citizenId'),
            role=data.get('role')
        )
    
    def to_json(self):
        data = {
            'name': self.name,
            'email': self.email,
            'birthDate': self.birth_date,
            'citizenId': self.citizen_id,
            'role': self.role
        }
        if self.password:
            data['password'] = self.password
        if self.user_id:
            data['id'] = self.user_id
        return data