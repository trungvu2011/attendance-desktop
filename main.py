import sys
import os
from PyQt5.QtWidgets import QApplication
from app.views.main_window import MainWindow
from app.controllers.auth_controller import AuthController
from app.controllers.cccd_socket_server import CCCDSocketServer
from app.controllers.cccd_api import CCCDApiController
import threading
from flask import Flask, request, jsonify
import time
import socket

# Flask app for API server
flask_app = Flask(__name__)

@flask_app.route('/api/cccd', methods=['POST'])
def receive_cccd_data():
    """Endpoint to receive CCCD data from mobile app"""
    try:
        # Extract data from request
        data = request.json
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Check required fields
        if 'citizenId' not in data or 'faceImage' not in data:
            return jsonify({
                'status': 'error', 
                'message': 'Missing required fields (citizenId, faceImage)'
            }), 400
        
        print(f"Received CCCD data for ID: {data['citizenId']}")
        
        # Process the data using the socket server
        global socket_server
        if socket_server:
            socket_server._process_cccd_data(data)
        
        return jsonify({
            'status': 'success',
            'message': 'CCCD data received successfully'
        })
        
    except Exception as e:
        print(f"Error processing CCCD data: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@flask_app.route('/api/status', methods=['GET'])
def check_status():
    """Endpoint to check server status"""
    return jsonify({
        'status': 'online',
        'message': 'CCCD API Server is running',
        'timestamp': time.time()
    })

def run_flask_server():
    """Run Flask API server to receive requests from mobile app"""
    try:
        # Get local IP address for display
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external server to determine the local IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"Starting Flask API server on: http://{local_ip}:5000")
        print(f"Mobile app should connect to: {local_ip}")
        print(f"To test the API, you can use: GET http://{local_ip}:5000/api/status")
        
        # Run Flask on all network interfaces
        flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Failed to start Flask server: {e}")

if __name__ == "__main__":
    print("Starting Attendance Management System...")
    try:
        # Create necessary directories
        os.makedirs(os.path.join("app", "data", "cccd_images"), exist_ok=True)
        os.makedirs(os.path.join("app", "data", "captured_faces"), exist_ok=True)
        
        app = QApplication(sys.argv)
        print("Application instance created")
        
        # Start CCCD Socket Server in the background
        socket_server = CCCDSocketServer.get_instance()
        socket_server.start()
        print("CCCD Socket Server started")
        
        # Initialize CCCD API controller
        cccd_api = CCCDApiController()
        print("CCCD API controller initialized")
        
        # Start Flask server in background thread
        flask_thread = threading.Thread(target=run_flask_server, daemon=True)
        flask_thread.start()
        print("Flask API server started in background")
        
        auth_controller = AuthController()
        print("Auth controller initialized")
        
        main_window = MainWindow(auth_controller)
        print("Main window created")
        
        # Make sure the window is shown
        main_window.show()
        print("Main window displayed")
        
        print("Entering application event loop")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()