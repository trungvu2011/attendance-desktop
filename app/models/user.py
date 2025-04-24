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
        """
        Tạo đối tượng User từ dữ liệu JSON
        Hỗ trợ cả hai format từ API đăng nhập và API users
        """
        # Hỗ trợ cả các định dạng id khác nhau
        user_id = data.get('userId') or data.get('id') or data.get('user_id')
        
        # Hỗ trợ cả định dạng birthDate, birth và birth_date
        birth_date = data.get('birth') or data.get('birthDate') or data.get('birth_date')
        
        # Hỗ trợ cả định dạng citizenId và citizen_id
        citizen_id = data.get('citizenId') or data.get('citizen_id')
        
        # In ra log để debug
        print(f"Parsing user data: {data}")
        print(f"Extracted: user_id={user_id}, name={data.get('name')}, birth_date={birth_date}, citizen_id={citizen_id}")
        
        return User(
            user_id=user_id,
            name=data.get('name'),
            email=data.get('email'),
            birth_date=birth_date,
            citizen_id=citizen_id,
            role=data.get('role')
        )
    
    def to_json(self):
        """Chuyển đổi đối tượng User thành JSON để gửi lên API"""
        data = {
            'name': self.name,
            'email': self.email,
            'birth': self.birth_date,  # Sử dụng trường 'birth' theo tài liệu API
            'citizenId': self.citizen_id,
            'role': self.role
        }
        if self.password:
            data['password'] = self.password
        if self.user_id:
            data['userId'] = self.user_id  # Sử dụng trường 'userId' theo tài liệu API
        return data