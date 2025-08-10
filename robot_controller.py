#!/usr/bin/env python3
"""
Robot Controller for Red Cap Follower
Bridges web interface commands to robot control system
"""

import subprocess
import sys
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RobotController:
    def __init__(self):
        self.robot_ip = "172.16.215.191"
        self.node_path = "/data/data/com.ohmnilabs.telebot_rtc/files/assets/node-files"
        self.power = 2000
        self.turn_power = 1500
        self.last_command = None
        self.command_cooldown = 0.3  # seconds between commands
        self.last_command_time = 0
        
        # Initialize robot on startup
        self.initialize_robot()
    
    def initialize_robot(self):
        """Initialize robot with torque enabled"""
        try:
            logger.info("🤖 Initializing robot...")
            self.send_command("torque 0 on")
            self.send_command("torque 1 on") 
            self.send_command("torque 3 on")
            logger.info("✅ Robot initialized successfully")
        except Exception as e:
            logger.error(f"❌ Robot initialization failed: {e}")
    
    def send_command(self, cmd):
        """Send command to robot via ADB"""
        try:
            full_cmd = f"adb shell \"su -c 'cd {self.node_path} && echo \\\"{cmd}\\\" | ./node bot_shell_client.js'\""
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                logger.debug(f"✅ Command sent: {cmd}")
                return True
            else:
                logger.error(f"❌ Command failed: {cmd} - {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ Command timeout: {cmd}")
            return False
        except Exception as e:
            logger.error(f"❌ Command error: {cmd} - {e}")
            return False
    
    def send_dual_wheel(self, left_speed, right_speed):
        """Send synchronized wheel commands for precise movement"""
        try:
            cmd = f"adb shell \"su -c 'cd {self.node_path} && (echo \\\"rot 0 {left_speed}\\\"; echo \\\"rot 1 {right_speed}\\\") | ./node bot_shell_client.js'\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                logger.debug(f"✅ Dual wheel command: L:{left_speed}, R:{right_speed}")
                return True
            else:
                logger.error(f"❌ Dual wheel command failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Dual wheel error: {e}")
            return False
    
    def execute_movement(self, command):
        """Execute movement command with rate limiting"""
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_command_time < self.command_cooldown:
            return False
        
        # Don't repeat the same command
        if command == self.last_command:
            return True
        
        success = False
        
        if command == 'forward':
            logger.info("🔼 Moving forward...")
            success = self.send_dual_wheel(-self.power, self.power)
            
        elif command == 'backward':
            logger.info("🔽 Moving backward...")
            success = self.send_dual_wheel(self.power, -self.power)
            
        elif command == 'left':
            logger.info("◀️ Turning left...")
            success = self.send_dual_wheel(-self.turn_power, -self.turn_power)
            
        elif command == 'right':
            logger.info("▶️ Turning right...")
            success = self.send_dual_wheel(self.turn_power, self.turn_power)
            
        elif command == 'stop':
            logger.info("🛑 Stopping...")
            success = self.send_dual_wheel(0, 0)
            
        else:
            logger.warning(f"❓ Unknown command: {command}")
            return False
        
        if success:
            self.last_command = command
            self.last_command_time = current_time
        
        return success
    
    def shutdown(self):
        """Safely shutdown robot"""
        logger.info("🛑 Shutting down robot...")
        self.send_dual_wheel(0, 0)
        self.send_command("torque 0 off")
        self.send_command("torque 1 off")
        self.send_command("torque 3 off")
        logger.info("👋 Robot shutdown complete")

class RobotHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, robot_controller, *args, **kwargs):
        self.robot_controller = robot_controller
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests for robot commands"""
        if self.path == '/robot/command':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                command = data.get('command')
                if command:
                    success = self.robot_controller.execute_movement(command)
                    
                    response = {
                        'success': success,
                        'command': command,
                        'timestamp': time.time()
                    }
                    
                    self.send_response(200 if success else 500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_error(400, "Missing command parameter")
                    
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            except Exception as e:
                logger.error(f"Request handling error: {e}")
                self.send_error(500, str(e))
                
        elif self.path == '/robot/dual_wheel':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                left_speed = data.get('left_speed', 0)
                right_speed = data.get('right_speed', 0)
                
                success = self.robot_controller.send_dual_wheel(left_speed, right_speed)
                
                response = {
                    'success': success,
                    'left_speed': left_speed,
                    'right_speed': right_speed,
                    'timestamp': time.time()
                }
                
                self.send_response(200 if success else 500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            except Exception as e:
                logger.error(f"Dual wheel request handling error: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging to avoid cluttering output"""
        logger.debug(f"HTTP: {format % args}")

def create_handler(robot_controller):
    """Create HTTP handler with robot controller"""
    def handler(*args, **kwargs):
        return RobotHTTPHandler(robot_controller, *args, **kwargs)
    return handler

def main():
    """Main function to start robot controller server"""
    robot_controller = RobotController()
    
    try:
        # Start HTTP server for web interface communication
        server_port = 8081
        httpd = HTTPServer(('0.0.0.0', server_port), create_handler(robot_controller))
        
        logger.info(f"🌐 Robot controller server started on port {server_port}")
        logger.info("📡 Ready to receive commands from web interface")
        logger.info("🛑 Press Ctrl+C to stop")
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested...")
            
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    
    finally:
        robot_controller.shutdown()
        if 'httpd' in locals():
            httpd.shutdown()
        logger.info("👋 Controller stopped")

if __name__ == "__main__":
    main()
