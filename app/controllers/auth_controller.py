from app.utils.api_service import ApiService
from app.models.user import User

class AuthController:
    def __init__(self):
        self.api_service = ApiService.get_instance()
        self.current_user = None
        self._init_user_from_cache()
    
    def _init_user_from_cache(self):
        """Khởi tạo thông tin người dùng từ cache nếu có token hợp lệ"""
        if self.api_service.token and self.api_service.user_data:
            # Tạo đối tượng User từ dữ liệu cached
            self.current_user = User.from_json(self.api_service.user_data)
    
    def login(self, email, password, remember=False):
        """Login to the system and get current user"""
        # Đảm bảo xóa thông tin người dùng cũ trước khi đăng nhập
        self.current_user = None
        
        # Sử dụng ApiService với tham số remember mới
        result = self.api_service.login(email, password, remember)
        if result:
            # API trả về trực tiếp thông tin người dùng từ authentication
            self.current_user = User.from_json(result)
            return True
        return False
    
    def logout(self):
        """Logout from the system"""
        result = self.api_service.logout()
        # Luôn xóa thông tin người dùng hiện tại, ngay cả khi API logout thất bại
        self.current_user = None
        return result
    
    def refresh_user_info(self):
        """Refresh thông tin người dùng từ API - sử dụng khi cần cập nhật thông tin mới nhất"""
        if not self.api_service.token:
            self.current_user = None
            return False
            
        # Nếu có dữ liệu người dùng trong cache và chưa hết hạn, sử dụng nó
        if self.api_service.user_data:
            self.current_user = User.from_json(self.api_service.user_data)
            return True
            
        # Nếu không có dữ liệu trong cache, gọi API
        from config.config import Config
        try:
            user_data = self.api_service.get(Config.USER_PROFILE_URL)
            
            if user_data:
                self.current_user = User.from_json(user_data)
                # Lưu user_data vào ApiService để cache
                self.api_service.user_data = user_data
                return True
        except Exception as e:
            print(f"Error refreshing user info: {e}")
            
        # Nếu không lấy được thông tin người dùng, đánh dấu không đăng nhập
        self.current_user = None
        return False
    
    def is_logged_in(self):
        """Check if user is logged in"""
        # Nếu đã có thông tin người dùng, xem như đã đăng nhập
        if self.current_user:
            return True
            
        # Nếu có token nhưng chưa có thông tin người dùng, thử khởi tạo từ cache
        if not self.current_user and self.api_service.token:
            self._init_user_from_cache()
            if self.current_user:
                return True
        
        # Cuối cùng, kiểm tra token có hợp lệ không
        is_valid = self.api_service.validate_token()
        
        # Nếu token không hợp lệ, reset thông tin người dùng
        if not is_valid:
            self.current_user = None
            
        return is_valid
    
    def get_current_user(self):
        """Get current logged in user"""
        # Nếu đã có thông tin người dùng, trả về luôn
        if self.current_user:
            return self.current_user
            
        # Nếu có token nhưng chưa có thông tin người dùng, thử khởi tạo từ cache
        if not self.current_user and self.api_service.token:
            self._init_user_from_cache()
            if self.current_user:
                return self.current_user
                
            # Nếu không có thông tin trong cache, thử refresh
            self.refresh_user_info()
            
        return self.current_user
    def is_admin(self):
        """Check if current user is admin"""
        # Always return False to ensure only candidate view is shown
        return False