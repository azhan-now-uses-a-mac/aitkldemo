#!/usr/bin/env python3
"""
Simple script to execute robot commands from command line
This bridges the gap between detection and robot movement
"""

import subprocess
import sys
import time

ROBOT_IP = "172.16.215.191"
NODE_PATH = "/data/data/com.ohmnilabs.telebot_rtc/files/assets/node-files"

def send_robot_command(cmd):
    """Send command directly to robot"""
    try:
        full_cmd = f"adb shell \"su -c 'cd {NODE_PATH} && echo \\\"{cmd}\\\" | ./node bot_shell_client.js'\""
        print(f"🤖 Executing: {cmd}")
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=3)
        
        if result.returncode == 0:
            print(f"✅ Command executed: {cmd}")
            return True
        else:
            print(f"❌ Command failed: {cmd}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_dual_wheel(left_speed, right_speed):
    """Send synchronized wheel commands"""
    try:
        cmd = f"adb shell \"su -c 'cd {NODE_PATH} && (echo \\\"rot 0 {left_speed}\\\"; echo \\\"rot 1 {right_speed}\\\") | ./node bot_shell_client.js'\""
        print(f"🤖 Moving: L:{left_speed}, R:{right_speed}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Movement error: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 execute_robot_command.py <left_speed> <right_speed>")
        print("Examples:")
        print("  python3 execute_robot_command.py 0 0        # Stop")
        print("  python3 execute_robot_command.py -800 800   # Forward (slow)")
        print("  python3 execute_robot_command.py 800 -800   # Backward (slow)")
        print("  python3 execute_robot_command.py -600 -600  # Left (slow)")
        print("  python3 execute_robot_command.py 600 600    # Right (slow)")
        sys.exit(1)
    
    left_speed = int(sys.argv[1])
    right_speed = int(sys.argv[2])
    
    print(f"🤖 Robot Command Executor")
    print(f"Left Speed: {left_speed}")
    print(f"Right Speed: {right_speed}")
    print("-" * 30)
    
    success = send_dual_wheel(left_speed, right_speed)
    
    if success:
        print("✅ Command executed successfully!")
    else:
        print("❌ Command failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
