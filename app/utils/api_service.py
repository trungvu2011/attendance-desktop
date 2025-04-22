import requests
import json
import os
from config.config import Config

class ApiService:
    def __init__(self):
        self.token = None
        self.token_path = Config.TOKEN_STORAGE
        self._load_token()
    
    def _load_token(self):
        """Load token from storage if exists"""
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as f:
                    data = json.load(f)
                    self.token = data.get('token')
        except Exception as e:
            print(f"Error loading token: {e}")
    
    def _save_token(self, token):
        """Save token to storage"""
        try:
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as f:
                json.dump({'token': token}, f)
            self.token = token
        except Exception as e:
            print(f"Error saving token: {e}")
    
    def _get_headers(self):
        """Get headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def login(self, email, password):
        """Login to the system and save token"""
        response = requests.post(
            Config.AUTH_LOGIN,
            json={'email': email, 'password': password},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self._save_token(data.get('token'))
            return data
        return None
    
    def logout(self):
        """Logout from the system"""
        response = requests.post(
            Config.AUTH_LOGOUT,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
            self.token = None
            return True
        return False
    
    def refresh_token(self):
        """Refresh token if expired"""
        response = requests.post(
            Config.AUTH_REFRESH_TOKEN,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            self._save_token(data.get('token'))
            return True
        return False
    
    def validate_token(self):
        """Validate if token is still valid"""
        if not self.token:
            return False
            
        response = requests.get(
            Config.AUTH_VALIDATE_TOKEN,
            headers=self._get_headers()
        )
        
        return response.status_code == 200
    
    def get(self, url, params=None):
        """Generic GET request"""
        response = requests.get(
            url,
            params=params,
            headers=self._get_headers()
        )
        
        if response.status_code == 401:  # Unauthorized
            if self.refresh_token():
                return self.get(url, params)
            return None
        
        if response.status_code == 200:
            return response.json()
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