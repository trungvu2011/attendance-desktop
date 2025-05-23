import cv2
import numpy as np
import os
from PIL import Image
import face_recognition

def detect_faces(image_path):
    """
    Detect faces in an image and return their coordinates using face_recognition
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        list: List of face locations (top, right, bottom, left)
    """
    # Load the image using face_recognition library
    try:
        image = face_recognition.load_image_file(image_path)
        
        # Try to use the more accurate CNN model if available, otherwise use HOG
        try:
            # CNN model is more accurate but requires GPU and is slower
            face_locations = face_recognition.face_locations(image, model="cnn")
        except:
            # HOG model is faster but less accurate, good for CPU-only environments
            face_locations = face_recognition.face_locations(image, model="hog")
            
        return face_locations
    except Exception as e:
        print(f"Error detecting faces: {e}")
        return []

def face_encoding_from_image(image_path):
    """
    Generate face encodings from an image using face_recognition
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        list: Face encodings for the detected faces
    """
    try:
        # Load the image
        image = face_recognition.load_image_file(image_path)
        
        # Find face locations
        face_locations = face_recognition.face_locations(image, model="hog")
        
        if len(face_locations) == 0:
            print(f"No faces found in {image_path}")
            return []
        
        # Get face encodings with higher number of jitters for better accuracy
        # Higher jitters means more GPU/CPU time but better accuracy
        face_encodings = face_recognition.face_encodings(image, face_locations, num_jitters=3)
        return face_encodings
    except Exception as e:
        print(f"Error getting face encodings: {e}")
        return []

def compare_faces(cccd_image_path, captured_face_image_path, tolerance=0.55):
    """
    Compare faces between two images using face_recognition library
    
    Args:
        cccd_image_path (str): Path to the CCCD (ID card) image
        captured_face_image_path (str): Path to the captured face image
        tolerance (float): Matching tolerance (lower is stricter)
        
    Returns:
        dict: Comparison result with keys:
            - is_match: True if faces match, False otherwise
            - confidence: Matching confidence (0.0 to 1.0)
            - message: Human-readable message about the comparison
    """
    # Get face encodings
    cccd_face_encodings = face_encoding_from_image(cccd_image_path)
    captured_face_encodings = face_encoding_from_image(captured_face_image_path)
    
    # Check if faces were detected in both images
    if not cccd_face_encodings:
        return {
            'is_match': False,
            'confidence': 0.0,
            'message': 'Không tìm thấy khuôn mặt trong ảnh CCCD. Vui lòng quét lại.'
        }
    
    if not captured_face_encodings:
        return {
            'is_match': False,
            'confidence': 0.0,
            'message': 'Không tìm thấy khuôn mặt trong ảnh chụp. Vui lòng chụp lại.'
        }
    
    # Compare faces - use the first face from each image
    cccd_encoding = cccd_face_encodings[0]
    captured_encoding = captured_face_encodings[0]
    
    # Calculate face distance - lower means more similar
    face_distance = face_recognition.face_distance([cccd_encoding], captured_encoding)[0]
      # Convert distance to confidence (0.0 to 1.0)
    # Distance of 0 means perfect match, 0.45 is now our stricter threshold for face_recognition
    # Convert to a confidence score from 0 to 1
    confidence = max(0, min(1, 1 - face_distance))
    
    # Check if it's a match
    # Use face_recognition compare_faces as well for added confidence
    direct_compare = face_recognition.compare_faces([cccd_encoding], captured_encoding, tolerance=tolerance)[0]
    
    # Combine results: require both confidence above threshold and direct comparison
    # Increase confidence threshold from 0.4 to 0.50 for stricter matching
    is_match = direct_compare and confidence >= 0.50
    
    # Create result message
    if is_match:
        if confidence >= 0.75:
            message = 'Xác thực khuôn mặt thành công (độ tin cậy cao).'
        else:
            message = 'Xác thực khuôn mặt thành công (độ tin cậy trung bình).'
    else:
        message = 'Xác thực khuôn mặt thất bại. Khuôn mặt không khớp với ảnh CCCD.'
    
    return {
        'is_match': is_match,
        'confidence': confidence,
        'message': message
    }

def crop_face_from_image(image_path, output_path):
    """
    Crop a detected face from an image and save it using face_recognition library
    
    Args:
        image_path (str): Path to the image to crop
        output_path (str): Path to save the cropped face
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load the image with face_recognition
        image = face_recognition.load_image_file(image_path)
        
        # Find face locations
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            print(f"No faces found in {image_path}")
            return False
        
        # Use the first face found
        top, right, bottom, left = face_locations[0]
        
        # Add some margin
        margin = 30
        top = max(0, top - margin)
        left = max(0, left - margin)
        bottom = min(image.shape[0], bottom + margin)
        right = min(image.shape[1], right + margin)
        
        # Crop the face
        face_image = image[top:bottom, left:right]
        
        # Convert to PIL Image and save
        pil_image = Image.fromarray(face_image)
        pil_image.save(output_path)
        
        return True
    except Exception as e:
        print(f"Error cropping face: {e}")
        return False