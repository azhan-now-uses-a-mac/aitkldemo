#!/usr/bin/env python3
"""
Simple test script to verify robot commands work
"""

import asyncio
import websockets
import json
import time

async def test_robot_commands():
    """Test robot commands via WebSocket"""
    
    try:
        uri = "ws://localhost:8082"
        print(f"🔌 Connecting to robot WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to robot WebSocket!")
            
            # Test commands
            test_commands = ['stop', 'forward', 'stop', 'left', 'stop', 'right', 'stop', 'backward', 'stop']
            
            print("🤖 Testing robot commands...")
            
            for command in test_commands:
                print(f"📤 Sending command: {command}")
                
                message = json.dumps({'command': command})
                await websocket.send(message)
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    print(f"📥 Response: {data}")
                except asyncio.TimeoutError:
                    print("⏱️ No response received")
                
                # Wait between commands
                time.sleep(1)
            
            print("✅ Robot command test completed!")
            
    except ConnectionRefusedError:
        print("❌ Cannot connect to robot WebSocket. Make sure robot_websocket_bridge.py is running.")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_robot_commands())
