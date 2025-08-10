#!/bin/bash

# Open Camera Browser on Robot Screen
# This script starts the camera server locally and opens it on the robot's display

ROBOT_IP="172.16.215.191"
SERVER_PORT="8080"
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)

echo "🤖 Opening Camera Browser on Robot Screen"
echo "=========================================="
echo "Robot IP: $ROBOT_IP"
echo "Local IP: $LOCAL_IP"
echo "Server Port: $SERVER_PORT"
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

# Start local camera server in background
echo "🌐 Starting local camera server..."
python3 camera_server.py --port $SERVER_PORT --host 0.0.0.0 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Get the actual local IP for the server URL
if [ -n "$LOCAL_IP" ]; then
    SERVER_URL="https://$LOCAL_IP:$SERVER_PORT"
else
    echo "⚠️  Could not detect local IP, using localhost"
    SERVER_URL="https://localhost:$SERVER_PORT"
fi

echo "📡 Server running at: $SERVER_URL"
echo ""

# Open browser on robot
echo "🤖 Opening browser on robot screen..."
echo "URL: $SERVER_URL"

# Try multiple methods to open browser on robot
echo "🔄 Attempting to open browser..."

# Method 1: Open with default browser
adb shell "am start -a android.intent.action.VIEW -d '$SERVER_URL'" 2>/dev/null
sleep 2

# Method 2: Try Chrome specifically
adb shell "am start -n com.android.chrome/com.google.android.apps.chrome.Main -a android.intent.action.VIEW -d '$SERVER_URL'" 2>/dev/null
sleep 2

# Method 3: Try generic browser
adb shell "am start -a android.intent.action.VIEW -d '$SERVER_URL' -t text/html" 2>/dev/null
sleep 2

echo "✅ Browser commands sent to robot"
echo ""
echo "📱 The camera browser should now be opening on the robot's screen"
echo "📹 Server URL: $SERVER_URL"
echo ""
echo "🔧 If the browser didn't open automatically, you can:"
echo "  1. Open a browser on the robot manually"
echo "  2. Navigate to: $SERVER_URL"
echo "  3. Allow camera permissions when prompted"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Keep server running and monitor
trap "echo '🛑 Stopping server...'; kill $SERVER_PID 2>/dev/null; exit 0" INT

# Wait for server process
wait $SERVER_PID
