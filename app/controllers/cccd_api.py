from app.utils.api_service import ApiService
from app.controllers.cccd_socket_server import CCCDSocketServer
from app.utils.face_recognition import compare_faces, face_encoding_from_image
from config.config import Config
import os

class CCCDApiController:
    """Controller for handling CCCD-related operations"""
    
    def __init__(self):
        self.api_service = ApiService.get_instance()
        self.socket_server = CCCDSocketServer.get_instance()
    
    def verify_cccd(self, user_citizen_id, exam_id=None):
        """
        Verify if there's a matching CCCD data received from the mobile app
        
        Args:
            user_citizen_id (str): Citizen ID from the user database
            exam_id (str, optional): The exam ID if applicable
            
        Returns:
            dict: Verification result with keys:
                - is_valid: True if the CCCD is valid, False otherwise
                - image_path: Path to the scanned CCCD image (if available)
                - message: Human-readable message about the verification
        """
        # Check if we have received CCCD data for this citizen ID
        cccd_data = self.socket_server.get_cccd_data(user_citizen_id)
        
        if not cccd_data:
            return {
                'is_valid': False,
                'image_path': None,
                'message': 'Không tìm thấy dữ liệu CCCD. Vui lòng quét lại.'
            }
        
        # Verify the CCCD data
        image_path = cccd_data['image_path']
        
        if not os.path.exists(image_path):
            return {
                'is_valid': False,
                'image_path': None,
                'message': 'Ảnh CCCD không tồn tại hoặc bị lỗi. Vui lòng quét lại.'
            }
        
        # Return success result
        return {
            'is_valid': True,
            'image_path': image_path,
            'message': 'Xác thực CCCD thành công.',
            'cccd_data': cccd_data
        }
    
    def verify_face_with_cccd(self, user_citizen_id, captured_face_image_path):
        """
        Compare a captured face with the face in the CCCD
        
        Args:
            user_citizen_id (str): The citizen ID of the user
            captured_face_image_path (str): Path to the captured face image
            
        Returns:
            dict: Comparison result with keys:
                - is_match: True if faces match, False otherwise
                - confidence: Matching confidence (0.0 to 1.0)
                - message: Human-readable message about the comparison
        """
        # Get CCCD data
        cccd_data = self.socket_server.get_cccd_data(user_citizen_id)
        
        if not cccd_data:
            return {
                'is_match': False,
                'confidence': 0.0,
                'message': 'Không tìm thấy dữ liệu CCCD. Vui lòng quét lại.'
            }
        
        cccd_image_path = cccd_data['image_path']
        
        if not os.path.exists(cccd_image_path):
            return {
                'is_match': False,
                'confidence': 0.0,
                'message': 'Ảnh CCCD không tồn tại hoặc bị lỗi. Vui lòng quét lại.'
            }
        
        if not os.path.exists(captured_face_image_path):
            return {
                'is_match': False,
                'confidence': 0.0,
                'message': 'Ảnh khuôn mặt người dùng không tồn tại hoặc bị lỗi.'
            }
        
        # Compare the faces
        comparison_result = compare_faces(cccd_image_path, captured_face_image_path)
        
        return comparison_result
