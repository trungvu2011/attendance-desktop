from app.utils.api_service import ApiService
from app.models.user import User
from config.config import Config

class UserController:
    def __init__(self):
        self.api_service = ApiService()
    
    def get_all_users(self):
        """Get all users from the system"""
        result = self.api_service.get(Config.USERS_URL)
        if result:
            return [User.from_json(user_data) for user_data in result]
        return []
    
    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        result = self.api_service.get(f"{Config.USERS_URL}/{user_id}")
        if result:
            return User.from_json(result)
        return None
    
    def get_current_user_profile(self):
        """Get current user profile from API"""
        result = self.api_service.get(Config.USER_PROFILE_URL)
        if result:
            return User.from_json(result)
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