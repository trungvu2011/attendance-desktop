"""
REST API server for CCCD verification.
This allows the mobile app to communicate with the desktop app.
"""

import sys
from flask import Flask, request, jsonify
import threading
import base64
import os
import time
from app.controllers.cccd_socket_server import CCCDSocketServer
from app.controllers.cccd_api import CCCDApiController

app = Flask(__name__)
socket_server = None
cccd_api_controller = None

@app.route('/api/cccd', methods=['POST'])
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

@app.route('/api/status', methods=['GET'])
def check_status():
    """Endpoint to check server status"""
    return jsonify({
        'status': 'online',
        'message': 'CCCD API Server is running',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("Starting CCCD API Server...")
    
    # Initialize socket server
    socket_server = CCCDSocketServer.get_instance()
    socket_server.start()
    
    # Initialize CCCD API controller
    cccd_api_controller = CCCDApiController()
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)