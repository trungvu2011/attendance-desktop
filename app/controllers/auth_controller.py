from app.utils.api_service import ApiService
from app.models.user import User

class AuthController:
    def __init__(self):
        self.api_service = ApiService()
        self.current_user = None
    
    def login(self, email, password):
        """Login to the system and get current user"""
        result = self.api_service.login(email, password)
        if result:
            # API trả về trực tiếp thông tin người dùng từ authentication
            self.current_user = User.from_json(result)
            return True
        return False
    
    def logout(self):
        """Logout from the system"""
        result = self.api_service.logout()
        if result:
            self.current_user = None
        return result
    
    def is_logged_in(self):
        """Check if user is logged in"""
        if not self.current_user:
            return False
        return self.api_service.validate_token()
    
    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user
    
    def is_admin(self):
        """Check if current user is admin"""
        if not self.current_user:
            return False
        from config.config import Config
        return self.current_user.role == Config.ROLE_ADMIN