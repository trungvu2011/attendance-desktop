import os

class Config:
    # API Base URL
    API_BASE_URL = "http://localhost:8080/api"
    
    # Auth Endpoints
    AUTH_LOGIN = f"{API_BASE_URL}/auth/login"
    AUTH_LOGOUT = f"{API_BASE_URL}/auth/signout"  # Hỗ trợ cả /signout và /logout
    AUTH_REFRESH_TOKEN = f"{API_BASE_URL}/auth/refresh-token"
    AUTH_VALIDATE_TOKEN = f"{API_BASE_URL}/auth/validate-token"
    
    # User Endpoints
    USERS_URL = f"{API_BASE_URL}/users"
    USER_PROFILE_URL = f"{API_BASE_URL}/user/profile"
    
    # Exam Endpoints
    EXAMS_URL = f"{API_BASE_URL}/exams"
    
    # Schedule Endpoints
    SCHEDULES_URL = f"{API_BASE_URL}/schedules"
    
    # Attendance Endpoints
    ATTENDANCE_URL = f"{API_BASE_URL}/exam-attendances"
    
    # Monitoring Endpoints
    MONITORING_URL = f"{API_BASE_URL}/monitoring-logs"

    # Role constants
    ROLE_ADMIN = "ADMIN"
    ROLE_CANDIDATE = "CANDIDATE"
    
    # Token storage path
    TOKEN_STORAGE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "data", "token.json")