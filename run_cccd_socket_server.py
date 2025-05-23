"""
Run the CCCD Socket Server to receive data from mobile devices.
"""
import sys
import time
from app.controllers.cccd_socket_server import CCCDSocketServer

def data_received_callback(citizen_id, image_path, data):
    """Callback function for when CCCD data is received"""
    print(f"[CALLBACK] Received CCCD data:")
    print(f"  Citizen ID: {citizen_id}")
    print(f"  Image saved at: {image_path}")
    print(f"  Additional data: {data.get('name', 'N/A')}")

if __name__ == "__main__":
    print("Starting CCCD Socket Server...")
    server = CCCDSocketServer.get_instance()
    
    # Register callback
    server.register_data_callback(data_received_callback)
    
    if server.start():
        try:
            # Keep the script running
            print("Server is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping server...")
            server.stop()
            print("Server stopped.")
    else:
        print("Failed to start server.")
        sys.exit(1)