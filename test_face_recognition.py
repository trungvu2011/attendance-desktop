"""
Test script for face_recognition module using the face_recognition library
"""

import os
import sys
from app.utils.face_recognition import detect_faces, face_encoding_from_image, compare_faces, crop_face_from_image

def main():
    # Directories
    data_dir = os.path.join("app", "data")
    cccd_dir = os.path.join(data_dir, "cccd_images")
    face_dir = os.path.join(data_dir, "captured_faces")
    
    # Check if we have any images
    cccd_files = [f for f in os.listdir(cccd_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    face_files = [f for f in os.listdir(face_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"Tìm thấy {len(cccd_files)} ảnh CCCD: {', '.join(cccd_files)}")
    print(f"Tìm thấy {len(face_files)} ảnh khuôn mặt: {', '.join(face_files)}")
    
    if not cccd_files:
        print("Không tìm thấy ảnh CCCD nào. Vui lòng quét CCCD trước.")
        return
    
    if not face_files:
        print("Không tìm thấy ảnh khuôn mặt nào. Vui lòng chụp khuôn mặt trước.")
        return
    
    # Test face detection
    print("\n--- Kiểm tra phát hiện khuôn mặt ---")
    cccd_path = os.path.join(cccd_dir, cccd_files[0])
    face_path = os.path.join(face_dir, face_files[0])
    
    print(f"Ảnh CCCD: {cccd_path}")
    cccd_face_locations = detect_faces(cccd_path)
    print(f"Đã phát hiện {len(cccd_face_locations)} khuôn mặt trong ảnh CCCD")
    
    print(f"Ảnh khuôn mặt: {face_path}")
    face_locations = detect_faces(face_path)
    print(f"Đã phát hiện {len(face_locations)} khuôn mặt trong ảnh chụp")
    
    # Test face encoding
    print("\n--- Kiểm tra mã hóa khuôn mặt ---")
    cccd_encodings = face_encoding_from_image(cccd_path)
    face_encodings = face_encoding_from_image(face_path)
    
    print(f"Số mã hóa khuôn mặt từ ảnh CCCD: {len(cccd_encodings)}")
    print(f"Số mã hóa khuôn mặt từ ảnh chụp: {len(face_encodings)}")
    
    # Test face comparison
    print("\n--- Kiểm tra so sánh khuôn mặt ---")
    result = compare_faces(cccd_path, face_path)
    print(f"Kết quả so sánh: {result}")
    
    print("\nKiểm tra hoàn tất!")

if __name__ == "__main__":
    main()
