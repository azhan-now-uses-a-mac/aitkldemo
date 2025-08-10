#!/usr/bin/env python3
"""
Simple Voice Server - No External Dependencies
Just processes voice commands and controls robot
"""

import os
import sys
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleVoiceHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for voice commands"""
        if self.path == '/voice/process':
            self.handle_voice_command()
        elif self.path == '/voice/speak':
            self.handle_speak_request()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_speak_request(self):
        """Handle speech requests - return empty for browser fallback"""
        try:
            # Read POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            logger.info(f"🔊 Speech request: {text}")
            
            # Return empty response to trigger browser TTS fallback
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send empty audio to trigger fallback
            self.wfile.write(b'')
            
        except Exception as e:
            logger.error(f"❌ Speech request error: {e}")
            self.send_error(500, str(e))
    
    def handle_voice_command(self):
        """Process voice commands and control robot"""
        try:
            # Read POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '').lower()
            if not text:
                self.send_error(400, "Missing text parameter")
                return
            
            logger.info(f"🎯 Processing voice command: {text}")
            
            # Process robot commands
            robot_response = self.process_robot_command(text)
            
            # Generate response text
            response_text = self.generate_response(text, robot_response)
            
            # Send JSON response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'command': text,
                'robot_action': robot_response,
                'response_text': response_text,
                'timestamp': time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"❌ Voice command error: {e}")
            self.send_error(500, str(e))
    
    def process_robot_command(self, text):
        """Process voice commands and execute robot actions"""
        try:
            logger.info(f"🤖 Analyzing command: '{text}'")
            
            # Robot movement commands with more variations
            if any(word in text for word in ['forward', 'ahead', 'move forward', 'go forward', 'go ahead', 'move up']):
                logger.info("🔼 Executing forward movement")
                result = subprocess.run(['python3', 'execute_robot_command.py', '-800', '800'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("✅ Forward movement successful")
                    return 'moving_forward'
                else:
                    logger.error(f"❌ Forward movement failed: {result.stderr.decode()}")
                    return 'error'
                
            elif any(word in text for word in ['backward', 'back', 'move back', 'go back', 'reverse']):
                logger.info("🔽 Executing backward movement")
                result = subprocess.run(['python3', 'execute_robot_command.py', '800', '-800'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("✅ Backward movement successful")
                    return 'moving_backward'
                else:
                    logger.error(f"❌ Backward movement failed: {result.stderr.decode()}")
                    return 'error'
                
            elif any(word in text for word in ['left', 'turn left', 'go left', 'rotate left']):
                logger.info("◀️ Executing left turn")
                result = subprocess.run(['python3', 'execute_robot_command.py', '-600', '-600'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("✅ Left turn successful")
                    return 'turning_left'
                else:
                    logger.error(f"❌ Left turn failed: {result.stderr.decode()}")
                    return 'error'
                
            elif any(word in text for word in ['right', 'turn right', 'go right', 'rotate right']):
                logger.info("▶️ Executing right turn")
                result = subprocess.run(['python3', 'execute_robot_command.py', '600', '600'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("✅ Right turn successful")
                    return 'turning_right'
                else:
                    logger.error(f"❌ Right turn failed: {result.stderr.decode()}")
                    return 'error'
                
            elif any(word in text for word in ['stop', 'halt', 'freeze', 'stay', 'pause']):
                logger.info("🛑 Executing stop")
                result = subprocess.run(['python3', 'execute_robot_command.py', '0', '0'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("✅ Stop successful")
                    return 'stopped'
                else:
                    logger.error(f"❌ Stop failed: {result.stderr.decode()}")
                    return 'error'
                
            elif any(word in text for word in ['follow', 'follow me', 'track', 'come with', 'come here']):
                logger.info("🎯 Follow mode requested")
                return 'start_following'
                
            elif any(word in text for word in ['don\'t follow', 'stop following', 'stay there', 'don\'t track']):
                logger.info("🛑 Stop following requested")
                return 'stop_following'
                
            elif any(word in text for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']):
                logger.info("👋 Greeting detected")
                return 'greeting'
                
            else:
                logger.info(f"❓ Unknown command: {text}")
                return 'no_action'
                
        except subprocess.TimeoutExpired:
            logger.error("⏱️ Robot command timeout")
            return 'timeout'
        except Exception as e:
            logger.error(f"❌ Robot command error: {e}")
            return 'error'
    
    def generate_response(self, command, robot_action):
        """Generate appropriate response text based on command and action"""
        responses = {
            'moving_forward': [
                "Moving forward now!",
                "Going ahead!",
                "Moving forward as requested!"
            ],
            'moving_backward': [
                "Moving backward now!",
                "Going back!",
                "Moving in reverse!"
            ],
            'turning_left': [
                "Turning left now!",
                "Rotating left!",
                "Going left as requested!"
            ],
            'turning_right': [
                "Turning right now!",
                "Rotating right!",
                "Going right as requested!"
            ],
            'stopped': [
                "Stopped and ready!",
                "All stopped!",
                "Standing by!"
            ],
            'start_following': [
                "I'll follow you now! Put on your red cap!",
                "Following mode activated! Show me your red cap!",
                "Ready to follow! Wear your red cap!"
            ],
            'stop_following': [
                "I'll stop following and stay here!",
                "Following mode disabled!",
                "Staying put as requested!"
            ],
            'greeting': [
                "Hello! I'm your robot assistant. I can move in any direction or follow your red cap!",
                "Hi there! Tell me to go forward, back, turn, stop, or follow you!",
                "Greetings! I'm ready for your commands!"
            ],
            'no_action': [
                "I'm here and ready! You can ask me to move forward, backward, left, right, stop, or follow you!",
                "Hello! I can move in any direction or follow your red cap. What would you like me to do?",
                "I'm listening! Tell me to go forward, back, turn, stop, or follow you!"
            ],
            'error': [
                "Sorry, I had trouble with that command. Please try again!",
                "Something went wrong. Could you repeat that?",
                "I didn't catch that properly. Please try again!"
            ],
            'timeout': [
                "The command took too long to execute. Please try again!",
                "Command timeout. Please try again!",
                "That took too long. Please repeat your command!"
            ]
        }
        
        import random
        return random.choice(responses.get(robot_action, responses['no_action']))

def main():
    """Start the simple voice server"""
    try:
        server_port = 8083
        httpd = HTTPServer(('0.0.0.0', server_port), SimpleVoiceHandler)
        
        logger.info(f"🎤 Simple Voice server started on port {server_port}")
        logger.info("🤖 Ready for voice commands!")
        logger.info("💬 Using browser TTS for speech responses")
        logger.info("🛑 Press Ctrl+C to stop")
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("🛑 Simple Voice server stopped")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
