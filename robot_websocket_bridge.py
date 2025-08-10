#!/usr/bin/env python3
"""
WebSocket Bridge for Real-time Robot Control
Provides real-time communication between web interface and robot
"""

import asyncio
import websockets
import json
import subprocess
import logging
import time
from threading import Thread
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RobotWebSocketBridge:
    def __init__(self):
        self.robot_ip = "172.16.215.191"
        self.node_path = "/data/data/com.ohmnilabs.telebot_rtc/files/assets/node-files"
        self.power = 2000
        self.turn_power = 1500
        self.connected_clients = set()
        self.last_command = None
        self.command_cooldown = 0.2
        self.last_command_time = 0
        
        # Initialize robot
        self.initialize_robot()
    
    def initialize_robot(self):
        """Initialize robot with torque enabled"""
        try:
            logger.info("🤖 Initializing robot...")
            self.send_robot_command("torque 0 on")
            self.send_robot_command("torque 1 on") 
            self.send_robot_command("torque 3 on")
            logger.info("✅ Robot initialized successfully")
        except Exception as e:
            logger.error(f"❌ Robot initialization failed: {e}")
    
    def send_robot_command(self, cmd):
        """Send command directly to robot"""
        try:
            full_cmd = f"adb shell \"su -c 'cd {self.node_path} && echo \\\"{cmd}\\\" | ./node bot_shell_client.js'\""
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                logger.debug(f"✅ Robot command: {cmd}")
                return True
            else:
                logger.error(f"❌ Robot command failed: {cmd}")
                return False
        except Exception as e:
            logger.error(f"❌ Robot command error: {cmd} - {e}")
            return False
    
    def send_dual_wheel(self, left_speed, right_speed):
        """Send synchronized wheel commands"""
        try:
            cmd = f"adb shell \"su -c 'cd {self.node_path} && (echo \\\"rot 0 {left_speed}\\\"; echo \\\"rot 1 {right_speed}\\\") | ./node bot_shell_client.js'\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"❌ Dual wheel error: {e}")
            return False
    
    def execute_movement(self, command):
        """Execute movement command with rate limiting"""
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_command_time < self.command_cooldown:
            return True
        
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
        
        if success:
            self.last_command = command
            self.last_command_time = current_time
        
        return success
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.connected_clients.add(websocket)
        client_ip = websocket.remote_address[0]
        logger.info(f"🔗 Client connected: {client_ip}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    command = data.get('command')
                    
                    if command:
                        logger.info(f"📨 Received command: {command} from {client_ip}")
                        success = self.execute_movement(command)
                        
                        # Send response back to client
                        response = {
                            'success': success,
                            'command': command,
                            'timestamp': time.time()
                        }
                        await websocket.send(json.dumps(response))
                        
                        # Broadcast to all clients
                        await self.broadcast_status(command, success)
                        
                except json.JSONDecodeError:
                    logger.error("❌ Invalid JSON received")
                except Exception as e:
                    logger.error(f"❌ Message handling error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client disconnected: {client_ip}")
        finally:
            self.connected_clients.remove(websocket)
    
    async def broadcast_status(self, command, success):
        """Broadcast status to all connected clients"""
        if self.connected_clients:
            status_message = {
                'type': 'status',
                'command': command,
                'success': success,
                'timestamp': time.time()
            }
            
            # Send to all clients
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(json.dumps(status_message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.connected_clients -= disconnected
    
    def shutdown(self):
        """Safely shutdown robot"""
        logger.info("🛑 Shutting down robot...")
        self.send_dual_wheel(0, 0)
        self.send_robot_command("torque 0 off")
        self.send_robot_command("torque 1 off")
        self.send_robot_command("torque 3 off")
        logger.info("👋 Robot shutdown complete")

async def main():
    """Main function to start WebSocket server"""
    bridge = RobotWebSocketBridge()
    
    def signal_handler(signum, frame):
        logger.info("🛑 Shutdown signal received...")
        bridge.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start WebSocket server
        server_port = 8082
        logger.info(f"🌐 Starting WebSocket robot bridge on port {server_port}")
        
        async with websockets.serve(bridge.handle_client, "0.0.0.0", server_port):
            logger.info("📡 WebSocket server ready for robot commands")
            logger.info("🛑 Press Ctrl+C to stop")
            
            # Keep server running
            await asyncio.Future()  # Run forever
            
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    finally:
        bridge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
