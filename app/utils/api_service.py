import requests
import json
import os
import time
from config.config import Config

class ApiService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Singleton pattern để đảm bảo chỉ có một instance của ApiService trong toàn bộ ứng dụng"""
        if cls._instance is None:
            cls._instance = ApiService()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset instance của ApiService - sử dụng khi cần làm mới hoàn toàn trạng thái API"""
        if cls._instance is not None:
            # Đảm bảo xóa token nếu có
            if cls._instance.token and os.path.exists(cls._instance.token_path):
                try:
                    os.remove(cls._instance.token_path)
                except Exception as e:
                    print(f"Error removing token file during reset: {e}")
            # Xóa instance để tạo mới khi cần
            cls._instance = None
        return cls.get_instance()
    
    def __init__(self):
        self.token = None
        self.token_path = Config.TOKEN_STORAGE
        self.user_data = None  # Lưu trữ thông tin người dùng trong phiên làm việc hiện tại
        # Đã loại bỏ việc tự động tải token cũ khi khởi tạo
    
    def _load_token(self):
        """Load token and user data from storage if exists"""
        # Phương thức này đã bị vô hiệu hóa để loại bỏ tính năng tự động đăng nhập
        pass
    
    def _save_token(self, token, user_data=None, remember=False):
        """Save token and user data to memory only"""
        # Chỉ lưu token và dữ liệu người dùng vào bộ nhớ, không lưu vào file
        self.token = token
        if user_data:
            self.user_data = user_data
            
        # Thông báo về việc không còn lưu token vào file
        print("Token saved to memory only. Auto-login has been disabled.")
    
    def _get_headers(self):
        """Get headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def login(self, email, password, remember=False):
        """Login to the system and save token with option to remember login"""
        # Đảm bảo xóa token cũ nếu có trước khi đăng nhập
        self.clear_token()
        
        try:
            response = requests.post(
                Config.AUTH_LOGIN,
                json={'email': email, 'password': password},
                headers={'Content-Type': 'application/json'},
                timeout=10  # Timeout để không đợi quá lâu
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Login response: {data}")
                # Theo tài liệu API: lấy token từ cấu trúc authentication
                if 'authentication' in data and 'token' in data['authentication']:
                    token = data['authentication']['token']
                    user_data = data['authentication']
                    
                    # Đảm bảo user_data có đầy đủ thông tin profile
                    if 'user' in data:
                        print("Found user object in login response, using it for profile")
                        # Nếu API trả về user object riêng, sử dụng nó
                        user_data.update(data['user'])
                    
                    # Lưu token và dữ liệu người dùng vào bộ nhớ
                    self._save_token(token, user_data, remember)
                    return data['authentication']  # Trả về thông tin người dùng đã xác thực
                return None
            return None
        except requests.RequestException as e:
            print(f"Network error during login: {str(e)}")
            return None
    
    def clear_token(self):
        """Xóa token khỏi bộ nhớ và file lưu trữ"""
        # Xóa token và user_data khỏi bộ nhớ
        self.token = None
        self.user_data = None
        
        # Xóa file token.json
        if os.path.exists(self.token_path):
            try:
                os.remove(self.token_path)
                print("Token file removed successfully")
            except Exception as e:
                print(f"Error removing token file: {e}")
    
    def logout(self):
        """Logout from the system"""
        try:
            # Thử gọi API logout nếu có token
            if self.token:
                response = requests.post(
                    Config.AUTH_LOGOUT,
                    headers=self._get_headers()
                )
        except Exception as e:
            print(f"Error calling logout API: {e}")
            response = None
        
        # Xóa token khỏi bộ nhớ và file
        self.clear_token()
        
        # Dù API có thành công hay không, vẫn trả về True vì đã xóa token cục bộ
        return True
    
    def refresh_token(self):
        """Refresh token if expired"""
        response = requests.post(
            Config.AUTH_REFRESH_TOKEN,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            # Theo tài liệu API mới: lấy accessToken
            if 'accessToken' in data:
                self._save_token(data['accessToken'])
                return True
            return False
        return False
    
    def validate_token(self):
        """Validate if token is still valid"""
        if not self.token:
            return False
            
        response = requests.get(
            Config.AUTH_VALIDATE_TOKEN,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('valid', False)
        return False
    
    def get(self, url, params=None):
        """Generic GET request"""
        try:
            print(f"\n=== GET request to: {url} ===")
            # In ra headers để kiểm tra token authentication
            headers = self._get_headers()
            print(f"Headers: {headers}")
            
            response = requests.get(
                url,
                params=params,
                headers=headers
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 401:  # Unauthorized
                print("Unauthorized response (401). Attempting to refresh token...")
                if self.refresh_token():
                    print("Token refreshed successfully, retrying request...")
                    return self.get(url, params)
                print("Token refresh failed")
                return None
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    return json_data
                except json.JSONDecodeError:
                    print(f"Error decoding JSON response: {response.text}")
                    return None
            else:
                print(f"API error: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"Exception during GET request to {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def post(self, url, data):
        """Generic POST request"""
        response = requests.post(
            url,
            json=data,
            headers=self._get_headers()
        )
        
        if response.status_code == 401:  # Unauthorized
            if self.refresh_token():
                return self.post(url, data)
            return None
        
        if response.status_code in [200, 201]:
            return response.json() if response.content else {'status': 'success'}
        return None
    
    def put(self, url, data):
        """Generic PUT request"""
        response = requests.put(
            url,
            json=data,
            headers=self._get_headers()
        )
        
        if response.status_code == 401:  # Unauthorized
            if self.refresh_token():
                return self.put(url, data)
            return None
        
        if response.status_code in [200, 204]:
            return response.json() if response.content else {'status': 'success'}
        return None
    
    def delete(self, url):
        """Generic DELETE request"""
        response = requests.delete(
            url,
            headers=self._get_headers()
        )
        
        if response.status_code == 401:  # Unauthorized
            if self.refresh_token():
                return self.delete(url)
            return None
        
        if response.status_code in [200, 204]:
            return {'status': 'success'}
        return None