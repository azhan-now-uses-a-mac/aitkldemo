#!/usr/bin/env python3
"""
Voice AI Server for Robot Interaction
Integrates ElevenLabs TTS with robot control
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

# ElevenLabs configuration
ELEVENLABS_API_KEY = "sk_f9503831910fa606e1fedf8e3ce4189dd02c9882a5fcd16e"
VOICE_ID = "yj30vwTGJxSHezdAGsv9"

class VoiceAIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests for voice AI"""
        if self.path == '/voice/speak':
            self.handle_text_to_speech()
        elif self.path == '/voice/process':
            self.handle_voice_command()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_text_to_speech(self):
        """Convert text to speech using ElevenLabs"""
        try:
            # Read POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            if not text:
                self.send_error(400, "Missing text parameter")
                return
            
            logger.info(f"🎤 Converting to speech: {text}")
            
            # Generate speech using ElevenLabs
            audio_content = self.generate_speech(text)
            
            if audio_content:
                # Send audio response
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(audio_content)
                logger.info("✅ Speech generated successfully")
            else:
                self.send_error(500, "Speech generation failed")
                
        except Exception as e:
            logger.error(f"❌ TTS error: {e}")
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
    
    def generate_speech(self, text):
        """Generate speech using ElevenLabs API"""
        try:
            import sys
            sys.path.insert(0, '/Users/azhan/Library/Python/3.9/lib/python/site-packages')
            
            # Try to import and use ElevenLabs
            from elevenlabs import generate, set_api_key
            
            # Set API key
            set_api_key(ELEVENLABS_API_KEY)
            
            # Generate audio
            logger.info(f"🎤 Generating speech with ElevenLabs: {text}")
            audio = generate(
                text=text,
                voice=VOICE_ID,
                model="eleven_monolingual_v1"
            )
            
            if audio and len(audio) > 0:
                logger.info("✅ ElevenLabs speech generated successfully")
                return audio
            else:
                logger.error("❌ ElevenLabs returned empty audio")
                return None
                
        except ImportError as e:
            logger.error(f"❌ ElevenLabs import failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ ElevenLabs generation error: {e}")
            return None
    
    def process_robot_command(self, text):
        """Process voice commands and execute robot actions"""
        try:
            # Robot movement commands
            if any(word in text for word in ['forward', 'ahead', 'move forward', 'go forward']):
                result = subprocess.run(['python3', 'execute_robot_command.py', '-800', '800'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True)
                return 'moving_forward'
                
            elif any(word in text for word in ['backward', 'back', 'move back', 'go back']):
                result = subprocess.run(['python3', 'execute_robot_command.py', '800', '-800'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True)
                return 'moving_backward'
                
            elif any(word in text for word in ['left', 'turn left', 'go left']):
                result = subprocess.run(['python3', 'execute_robot_command.py', '-600', '-600'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True)
                return 'turning_left'
                
            elif any(word in text for word in ['right', 'turn right', 'go right']):
                result = subprocess.run(['python3', 'execute_robot_command.py', '600', '600'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True)
                return 'turning_right'
                
            elif any(word in text for word in ['stop', 'halt', 'freeze', 'stay']):
                result = subprocess.run(['python3', 'execute_robot_command.py', '0', '0'], 
                                      cwd='/Users/azhan/Pictures/Mizo_Main', capture_output=True)
                return 'stopped'
                
            elif any(word in text for word in ['follow', 'follow me', 'track', 'come with']):
                return 'start_following'
                
            elif any(word in text for word in ['don\'t follow', 'stop following', 'stay there']):
                return 'stop_following'
                
            else:
                return 'no_action'
                
        except Exception as e:
            logger.error(f"Robot command error: {e}")
            return 'error'
    
    def generate_response(self, command, robot_action):
        """Generate appropriate response text based on command and action"""
        responses = {
            'moving_forward': [
                "Moving forward as requested!",
                "Going forward now!",
                "Moving ahead for you!"
            ],
            'moving_backward': [
                "Moving backward now!",
                "Going back as you asked!",
                "Moving in reverse!"
            ],
            'turning_left': [
                "Turning left now!",
                "Going left as requested!",
                "Rotating to the left!"
            ],
            'turning_right': [
                "Turning right now!",
                "Going right as you asked!",
                "Rotating to the right!"
            ],
            'stopped': [
                "Stopped and ready!",
                "All stopped, awaiting your next command!",
                "Standing by!"
            ],
            'start_following': [
                "I'll follow you now! Put on your red cap!",
                "Following mode activated! Wear your red cap and I'll track you!",
                "Ready to follow! Show me your red cap!"
            ],
            'stop_following': [
                "I'll stop following and stay here!",
                "Following mode disabled, staying in place!",
                "Staying put as requested!"
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
            ]
        }
        
        import random
        return random.choice(responses.get(robot_action, responses['no_action']))

def main():
    """Start the voice AI server"""
    try:
        server_port = 8083
        httpd = HTTPServer(('0.0.0.0', server_port), VoiceAIHandler)
        
        logger.info(f"🎤 Voice AI server started on port {server_port}")
        logger.info("🤖 Ready for voice commands!")
        logger.info("🛑 Press Ctrl+C to stop")
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("🛑 Voice AI server stopped")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
