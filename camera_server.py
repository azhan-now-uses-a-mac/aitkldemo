#!/usr/bin/env python3
"""
Simple HTTP Server for Robot Camera Browser
Serves the camera browser HTML page with proper MIME types and HTTPS support for camera access
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs
import ssl
import threading
import time
import subprocess
import json

class CameraHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with proper MIME types and security headers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='/Users/azhan/Pictures/Mizo_Main', **kwargs)
    
    def end_headers(self):
        # Add security headers for camera access
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Permissions-Policy', 'camera=*, microphone=*')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Handle robot command execution
        if self.path.startswith('/execute_robot_command'):
            self.handle_robot_command()
            return
        
        # Redirect root to landing page
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        super().do_GET()
    
    def do_POST(self):
        # Handle robot dual wheel commands
        if self.path == '/robot/dual_wheel':
            self.handle_dual_wheel_command()
            return
        super().do_POST()
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_robot_command(self):
        """Handle robot command execution via GET request"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            
            left_speed = int(params.get('left', [0])[0])
            right_speed = int(params.get('right', [0])[0])
            
            print(f"🤖 Robot command: L:{left_speed}, R:{right_speed}")
            
            # Execute robot command
            success = self.execute_robot_movement(left_speed, right_speed)
            
            # Send response
            self.send_response(200 if success else 500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': success,
                'left_speed': left_speed,
                'right_speed': right_speed,
                'timestamp': time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"❌ Robot command error: {e}")
            self.send_error(500, str(e))
    
    def handle_dual_wheel_command(self):
        """Handle robot dual wheel command via POST request"""
        try:
            # Read POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            left_speed = data.get('left_speed', 0)
            right_speed = data.get('right_speed', 0)
            
            print(f"🤖 Dual wheel command: L:{left_speed}, R:{right_speed}")
            
            # Execute robot command
            success = self.execute_robot_movement(left_speed, right_speed)
            
            # Send response
            self.send_response(200 if success else 500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': success,
                'left_speed': left_speed,
                'right_speed': right_speed,
                'timestamp': time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"❌ Dual wheel command error: {e}")
            self.send_error(500, str(e))
    
    def execute_robot_movement(self, left_speed, right_speed):
        """Execute robot movement using the execute_robot_command.py script"""
        try:
            # Use the execute_robot_command.py script
            cmd = ['python3', 'execute_robot_command.py', str(left_speed), str(right_speed)]
            result = subprocess.run(cmd, cwd='/Users/azhan/Pictures/Mizo_Main', 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print(f"✅ Robot movement executed: L:{left_speed}, R:{right_speed}")
                return True
            else:
                print(f"❌ Robot movement failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ Robot movement timeout: L:{left_speed}, R:{right_speed}")
            return False
        except Exception as e:
            print(f"❌ Robot movement error: {e}")
            return False
    
    def log_message(self, format, *args):
        # Custom logging
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def create_self_signed_cert():
    """Create a self-signed certificate for HTTPS (required for camera access in modern browsers)"""
    try:
        import ssl
        import tempfile
        import subprocess
        
        cert_dir = '/Users/azhan/Pictures/Mizo_Main'
        cert_file = os.path.join(cert_dir, 'server.crt')
        key_file = os.path.join(cert_dir, 'server.key')
        
        if os.path.exists(cert_file) and os.path.exists(key_file):
            return cert_file, key_file
        
        # Create self-signed certificate using openssl
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', key_file,
            '-out', cert_file, '-days', '30', '-nodes', '-subj',
            '/C=US/ST=State/L=City/O=Robot/CN=localhost'
        ]
        
        print("🔐 Creating self-signed certificate for HTTPS...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Certificate created successfully")
            return cert_file, key_file
        else:
            print(f"❌ Certificate creation failed: {result.stderr}")
            return None, None
            
    except Exception as e:
        print(f"❌ Certificate creation error: {e}")
        return None, None

def start_server(port=8080, use_https=True, host="0.0.0.0", robot_ip=None):
    """Start the camera server"""
    
    print("🤖 Starting Robot Camera Browser Server")
    print("=" * 40)
    
    # Change to the correct directory
    os.chdir('/Users/azhan/Pictures/Mizo_Main')
    
    try:
        with socketserver.TCPServer((host, port), CameraHTTPRequestHandler) as httpd:
            
            if use_https:
                # Try to create HTTPS server for camera access
                cert_file, key_file = create_self_signed_cert()
                
                if cert_file and key_file:
                    try:
                        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                        context.load_cert_chain(cert_file, key_file)
                        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
                        protocol = "https"
                        print("🔒 HTTPS server enabled (required for camera access)")
                    except Exception as e:
                        print(f"⚠️  HTTPS setup failed, falling back to HTTP: {e}")
                        protocol = "http"
                        use_https = False
                else:
                    protocol = "http"
                    use_https = False
                    print("⚠️  Using HTTP (camera may not work in some browsers)")
            else:
                protocol = "http"
                print("⚠️  Using HTTP (camera may not work in some browsers)")
            
            # Determine the correct URL for access
            if robot_ip:
                server_url = f"{protocol}://{robot_ip}:{port}"
                display_url = server_url
            elif host == "0.0.0.0":
                server_url = f"{protocol}://localhost:{port}"
                display_url = f"{protocol}://[robot-ip]:{port}"
            else:
                server_url = f"{protocol}://{host}:{port}"
                display_url = server_url
            
            print(f"📡 Server running at: {display_url}")
            print(f"📹 Camera Browser: {display_url}/camera_browser.html")
            print("🔧 Controls:")
            print("   - Start/Stop Camera")
            print("   - Brightness/Contrast/Saturation/Hue adjustments")
            print("   - Grid overlay for positioning")
            print("   - Fullscreen mode")
            print("")
            print("⚠️  Note: Camera access requires HTTPS in modern browsers")
            print("   If you see certificate warnings, click 'Advanced' -> 'Proceed to localhost'")
            print("")
            print("🛑 Press Ctrl+C to stop the server")
            print("")
            
            # Only open browser locally if no robot IP specified
            def open_browser():
                time.sleep(2)
                try:
                    if robot_ip:
                        # Don't auto-open locally when targeting robot
                        print(f"🤖 Server ready for robot at {robot_ip}")
                        print("Robot browser will be opened by deployment script")
                    else:
                        webbrowser.open(server_url)
                        print(f"🌐 Opened browser at {server_url}")
                except Exception as e:
                    print(f"💻 Could not auto-open browser: {e}")
                    print("Please manually open your browser and navigate to the URL above")
            
            if not robot_ip:  # Only auto-open if not targeting robot
                browser_thread = threading.Thread(target=open_browser, daemon=True)
                browser_thread.start()
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"   python3 camera_server.py --port {port + 1}")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function with command line argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Robot Camera Browser Server')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--http', action='store_true', help='Use HTTP instead of HTTPS')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t auto-open browser')
    parser.add_argument('--robot-ip', type=str, help='Robot IP address to open browser on robot')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Server host address (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    use_https = not args.http
    
    start_server(port=args.port, use_https=use_https, host=args.host, robot_ip=args.robot_ip)

if __name__ == "__main__":
    main()
