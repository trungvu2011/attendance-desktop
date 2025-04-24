#!/usr/bin/env python
"""
Script hot reload cho ứng dụng Attendance Desktop
Tự động khởi động lại ứng dụng khi phát hiện thay đổi trong mã nguồn
"""

import sys
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Định cấu hình
MAIN_SCRIPT = "main.py"  # Script chính để chạy
IGNORE_PATTERNS = [".git", "__pycache__", "*.pyc", "*.pyo", "*.pyd", ".DS_Store", "venv"]
WAIT_SECONDS = 1  # Thời gian chờ giữa các lần khởi động lại

# Biến toàn cục
process = None
restart_pending = False
last_change_time = time.time()


class ChangeHandler(FileSystemEventHandler):
    """Xử lý sự kiện thay đổi tệp tin"""
    
    def on_any_event(self, event):
        """Được gọi khi bất kỳ tệp tin nào thay đổi"""
        global restart_pending, last_change_time
        
        # Bỏ qua thư mục/tập tin nằm trong danh sách bỏ qua
        for pattern in IGNORE_PATTERNS:
            if pattern in event.src_path:
                return
        
        # Chỉ quan tâm đến tệp Python
        if not event.src_path.endswith(".py"):
            return
            
        print(f"Đã phát hiện thay đổi: {event.src_path}")
        restart_pending = True
        last_change_time = time.time()


def start_app():
    """Khởi động ứng dụng"""
    global process
    cmd = [sys.executable, MAIN_SCRIPT]
    print(f"Khởi động ứng dụng: {' '.join(cmd)}")
    
    # Khởi động ứng dụng mới
    process = subprocess.Popen(cmd)


def stop_app():
    """Dừng ứng dụng hiện tại"""
    global process
    if process:
        print("Dừng ứng dụng...")
        process.terminate()
        try:
            # Đợi quá trình kết thúc
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Không thể kết thúc tiến trình, buộc dừng...")
            process.kill()
        process = None


def restart_app():
    """Khởi động lại ứng dụng"""
    stop_app()
    start_app()


def main():
    """Hàm chính"""
    global restart_pending, last_change_time
    
    # Khởi tạo observer để theo dõi thay đổi
    observer = Observer()
    observer.schedule(ChangeHandler(), path=".", recursive=True)
    observer.start()
    
    print("Hot reload đã được kích hoạt. Nhấn Ctrl+C để dừng.")
    
    try:
        # Khởi động ứng dụng lần đầu
        start_app()
        
        while True:
            # Kiểm tra xem có cần khởi động lại không
            if restart_pending and (time.time() - last_change_time) > WAIT_SECONDS:
                print("Khởi động lại ứng dụng...")
                restart_app()
                restart_pending = False
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("Đang dừng...")
    finally:
        # Đảm bảo dọn dẹp
        stop_app()
        observer.stop()
        observer.join()
        print("Hot reload đã bị dừng.")


if __name__ == "__main__":
    main()