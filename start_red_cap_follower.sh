#!/bin/bash

# Red Cap Follower Robot Startup Script
# Launches the complete system for red cap following with distance control

ROBOT_IP="172.16.215.191"
SERVER_PORT="8080"
CONTROLLER_PORT="8081"
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)

echo "🔴 Starting Red Cap Follower Robot System"
echo "=========================================="
echo "Robot IP: $ROBOT_IP"
echo "Local IP: $LOCAL_IP"
echo "Camera Server Port: $SERVER_PORT"
echo "Robot Controller Port: $CONTROLLER_PORT"
echo ""

# Check if ADB is available
if ! command -v adb &> /dev/null; then
    echo "❌ ADB is not installed or not in PATH"
    echo "Please install Android Debug Bridge (ADB)"
    exit 1
fi

# Check ADB connection
echo "📱 Checking ADB connection to robot..."
adb devices | grep -q "$ROBOT_IP"
if [ $? -ne 0 ]; then
    echo "⚠️  Robot not found. Attempting to connect..."
    adb connect $ROBOT_IP:5555
    sleep 3
    
    adb devices | grep -q "$ROBOT_IP"
    if [ $? -ne 0 ]; then
        echo "❌ Could not connect to robot at $ROBOT_IP"
        echo "Trying to wake up robot and enable ADB..."
        
        # Try to wake up the robot
        ping -c 1 $ROBOT_IP > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ Robot is reachable, retrying ADB connection..."
            adb connect $ROBOT_IP:5555
            sleep 2
        else
            echo "❌ Robot is not reachable. Please check:"
            echo "  1. Robot is powered on"
            echo "  2. Robot is connected to the same network"
            echo "  3. IP address is correct: $ROBOT_IP"
            exit 1
        fi
    fi
fi

if adb devices | grep -q "$ROBOT_IP"; then
    echo "✅ Connected to robot successfully"
else
    echo "❌ Still cannot connect to robot"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Red Cap Follower system..."
    
    # Kill background processes
    if [ ! -z "$CAMERA_SERVER_PID" ]; then
        kill $CAMERA_SERVER_PID 2>/dev/null
        echo "📹 Camera server stopped"
    fi
    
    if [ ! -z "$ROBOT_CONTROLLER_PID" ]; then
        kill $ROBOT_CONTROLLER_PID 2>/dev/null
        echo "🤖 Robot controller stopped"
    fi
    
    # Stop robot movement
    echo "🛑 Stopping robot movement..."
    adb shell "su -c 'cd /data/data/com.ohmnilabs.telebot_rtc/files/assets/node-files && (echo \"rot 0 0\"; echo \"rot 1 0\") | ./node bot_shell_client.js'" > /dev/null 2>&1
    
    echo "👋 Red Cap Follower system stopped"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Start robot HTTP controller in background
echo "🤖 Starting robot HTTP controller..."
python3 robot_controller.py &
ROBOT_CONTROLLER_PID=$!

# Wait for robot controller to initialize
sleep 3

# Check if robot controller is running
if ! kill -0 $ROBOT_CONTROLLER_PID 2>/dev/null; then
    echo "❌ Failed to start robot HTTP controller"
    exit 1
fi

echo "✅ Robot HTTP controller started (PID: $ROBOT_CONTROLLER_PID)"

# Start camera server in background
echo "🌐 Starting camera server..."
python3 camera_server.py --port $SERVER_PORT --host 0.0.0.0 &
CAMERA_SERVER_PID=$!

# Wait for camera server to start
sleep 3

# Check if camera server is running
if ! kill -0 $CAMERA_SERVER_PID 2>/dev/null; then
    echo "❌ Failed to start camera server"
    cleanup
    exit 1
fi

echo "✅ Camera server started (PID: $CAMERA_SERVER_PID)"

# Get the server URL
if [ -n "$LOCAL_IP" ]; then
    SERVER_URL="https://$LOCAL_IP:$SERVER_PORT"
else
    echo "⚠️  Could not detect local IP, using localhost"
    SERVER_URL="https://localhost:$SERVER_PORT"
fi

echo "📡 Camera server running at: $SERVER_URL"
echo ""

# Open red cap follower on robot
echo "🤖 Opening Red Cap Follower on robot screen..."
FOLLOWER_URL="$SERVER_URL/red_cap_follower.html"
echo "URL: $FOLLOWER_URL"

# Try multiple methods to open browser on robot
echo "🔄 Attempting to open browser on robot..."

# Method 1: Open with default browser
adb shell "am start -a android.intent.action.VIEW -d '$FOLLOWER_URL'" 2>/dev/null
sleep 2

# Method 2: Try Chrome specifically
adb shell "am start -n com.android.chrome/com.google.android.apps.chrome.Main -a android.intent.action.VIEW -d '$FOLLOWER_URL'" 2>/dev/null
sleep 2

echo "✅ Browser commands sent to robot"
echo ""
echo "🔴 Red Cap Follower System Ready!"
echo "=================================="
echo "📱 The Red Cap Follower should now be opening on the robot's screen"
echo "🌐 Follower URL: $FOLLOWER_URL"
echo "🤖 Robot Controller: http://localhost:8081"
echo ""
echo "📋 Instructions:"
echo "  1. Put on your red cap/hat"
echo "  2. Click 'Start Camera' on the robot screen"
echo "  3. Click 'Start Tracking' to detect red objects"
echo "  4. Adjust red sensitivity if needed"
echo "  5. Click 'Calibrate Distance' when at your desired follow distance"
echo "  6. Click 'Start Following' to make the robot follow you!"
echo ""
echo "⚠️  Safety Notes:"
echo "  • Keep clear space around the robot"
echo "  • Robot will follow at the configured distance"
echo "  • Stay visible to the camera"
echo "  • Click 'Stop Following' to stop"
echo ""
echo "🔧 If the browser didn't open automatically on the robot:"
echo "  1. Open a browser on the robot manually"
echo "  2. Navigate to: $FOLLOWER_URL"
echo "  3. Allow camera permissions when prompted"
echo ""
echo "🛑 Press Ctrl+C to stop the entire system"
echo ""

# Monitor system status
echo "📊 System Status:"
echo "  Camera Server PID: $CAMERA_SERVER_PID"
echo "  Robot Controller PID: $ROBOT_CONTROLLER_PID"
echo "  Robot IP: $ROBOT_IP"
echo ""

# Wait for user interrupt
while true; do
    # Check if processes are still running
    if ! kill -0 $CAMERA_SERVER_PID 2>/dev/null; then
        echo "❌ Camera server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $ROBOT_CONTROLLER_PID 2>/dev/null; then
        echo "❌ Robot controller stopped unexpectedly"  
        cleanup
        exit 1
    fi
    
    sleep 5
done
