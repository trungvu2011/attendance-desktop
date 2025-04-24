from app.utils.api_service import ApiService
from app.models.user import User
from config.config import Config
import logging

class UserController:
    def __init__(self):
        self.api_service = ApiService.get_instance()
    
    def get_all_users(self):
        """Get all users from the system with admin permission"""
        # Sử dụng API endpoint cho admin /api/user/all
        print(f"Đang lấy danh sách tất cả người dùng từ {Config.USER_ALL_URL}")
        result = self.api_service.get(Config.USER_ALL_URL)
        
        if result:
            print(f"Đã nhận được dữ liệu: {len(result)} người dùng")
            return [User.from_json(user_data) for user_data in result]
        else:
            print(f"Không thể lấy danh sách người dùng từ API admin. Đảm bảo bạn đang đăng nhập với quyền admin.")
            # Không quay lại API cũ vì API cũ không trả về tất cả người dùng cho admin
            return []
    
    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        result = self.api_service.get(f"{Config.USERS_URL}/{user_id}")
        if result:
            return User.from_json(result)
        return None
    
    def get_current_user_profile(self):
        """Get current user profile from API"""
        # In ra log để dễ debug
        print(f"\n=== ĐANG LẤY THÔNG TIN PROFILE TỪ {Config.USER_PROFILE_URL} ===")
        
        try:
            # Gọi API lấy profile
            print("Gửi GET request tới API profile...")
            result = self.api_service.get(Config.USER_PROFILE_URL)
            
            if result:
                print(f"API trả về dữ liệu: {result}")
                user = User.from_json(result)
                print(f"Đã parse thành công dữ liệu người dùng: {user.name}, {user.email}, {user.role}")
                return user
            else:
                print("API trả về None hoặc dữ liệu trống")
                
                # Kiểm tra xem có token hay không
                if not self.api_service.token:
                    print("Không có token, không thể lấy thông tin profile")
                    return None
                
                # Kiểm tra xem có dữ liệu user trong cache của api_service không
                if hasattr(self.api_service, 'user_data') and self.api_service.user_data:
                    print("Sử dụng dữ liệu user được cache trong api_service")
                    return User.from_json(self.api_service.user_data)
                
                return None
        except Exception as e:
            print(f"Lỗi khi gọi API profile: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_user(self, user):
        """Create a new user"""
        result = self.api_service.post(Config.USERS_URL, user.to_json())
        if result:
            return User.from_json(result)
        return None
    
    def update_user(self, user):
        """Update an existing user"""
        result = self.api_service.put(f"{Config.USERS_URL}/{user.user_id}", user.to_json())
        if result:
            return User.from_json(result)
        return None
    
    def delete_user(self, user_id):
        """Delete a user"""
        return self.api_service.delete(f"{Config.USERS_URL}/{user_id}")
    
    def validate_user(self, user):
        """Validate user data"""
        if not user.name or not user.email or not user.citizen_id or not user.role:
            return False, "All fields must be filled"
        
        # Validate citizen ID (must be 12 digits)
        if not user.citizen_id.isdigit() or len(user.citizen_id) != 12:
            return False, "Citizen ID must be 12 digits"
        
        # Basic email validation
        if '@' not in user.email:
            return False, "Invalid email format"
        
        return True, "Validation passed"
    
    def register_user(self, user):
        """Register a new user using the dedicated registration endpoint"""
        registration_data = {
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "citizenId": user.citizen_id,
            "birth": user.birth_date,
            "role": user.role
        }
        
        result = self.api_service.post(Config.USER_REGISTER_URL, registration_data)
        if result:
            return User.from_json(result)
        return None