import socket
import json
import threading
import base64
import os
from app.utils.datetime_utils import format_datetime_for_filename, format_datetime_for_api

class CCCDSocketServer:
    """Socket server that listens for CCCD data from mobile devices"""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CCCDSocketServer()
        return cls._instance
    
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.clients = {}
        self.received_data = {}  # Store received CCCD data
        self.data_callbacks = []  # Callbacks to notify when data is received
        
        # Ensure data directory exists
        self.data_dir = os.path.join("app", "data", "cccd_images")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def start(self):
        """Start the socket server in a separate thread"""
        if self.is_running:
            print("Server is already running")
            return
        
        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self._accept_connections)
            server_thread.daemon = True
            server_thread.start()
            
            print(f"CCCD Socket Server started on {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Error starting CCCD Socket Server: {e}")
            return False
    
    def stop(self):
        """Stop the socket server"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
            print("CCCD Socket Server stopped")
    
    def _accept_connections(self):
        """Accept client connections"""
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"New connection from {client_address}")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.is_running:
                    print(f"Error accepting connections: {e}")
    
    def _handle_client(self, client_socket, client_address):
        """Handle communication with a client"""
        self.clients[client_address] = client_socket
        
        try:
            # Receive data
            buffer = b""
            while self.is_running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Check if we have received the complete JSON
                try:
                    # Try to parse the data as JSON
                    decoded_data = buffer.decode('utf-8')
                    json_data = json.loads(decoded_data)
                    
                    # Process the received CCCD data
                    self._process_cccd_data(json_data)
                    
                    # Send acknowledgment
                    response = {"status": "success", "message": "CCCD data received"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                    # Clear buffer after processing
                    buffer = b""
                    
                except json.JSONDecodeError:
                    # JSON is incomplete, continue receiving
                    pass
                except UnicodeDecodeError:
                    # Not valid UTF-8, might be corrupted
                    buffer = b""
                    
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            if client_address in self.clients:
                del self.clients[client_address]
            print(f"Connection from {client_address} closed")
    
    def _process_cccd_data(self, data):
        """Process received CCCD data"""
        try:
            # Extract the CCCD data
            citizen_id = data.get('citizenId')
            image_data = data.get('faceImage')
            
            if citizen_id and image_data:
                # Decode base64 image data
                image_bytes = base64.b64decode(image_data)
                  # Save image to file
                timestamp = format_datetime_for_filename()
                file_path = os.path.join(self.data_dir, f"cccd_{citizen_id}_{timestamp}.jpg")
                
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                  # Store the data for retrieval
                self.received_data[citizen_id] = {
                    'citizenId': citizen_id,
                    'image_path': file_path,
                    'timestamp': format_datetime_for_api(),
                    'raw_data': data
                }
                
                print(f"Received CCCD data for ID: {citizen_id}")
                
                # Notify callbacks
                for callback in self.data_callbacks:
                    try:
                        callback(citizen_id, file_path, data)
                    except Exception as e:
                        print(f"Error in CCCD data callback: {e}")
                
        except Exception as e:
            print(f"Error processing CCCD data: {e}")
    
    def get_cccd_data(self, citizen_id):
        """Get the latest CCCD data for a specific citizen ID"""
        return self.received_data.get(citizen_id)
    
    def register_data_callback(self, callback):
        """Register a callback for when CCCD data is received"""
        if callback not in self.data_callbacks:
            self.data_callbacks.append(callback)
    
    def unregister_data_callback(self, callback):
        """Unregister a callback"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
