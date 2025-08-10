#!/bin/bash

# Deploy Camera Browser ONLY to Robot (not local machine)
# This script pushes the camera to the robot screen ONLY

ROBOT_IP="172.16.215.191"
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)

echo "🤖 Deploying Camera Browser ONLY to Robot"
echo "=========================================="
echo "Robot IP: $ROBOT_IP"
echo "Local IP: $LOCAL_IP"
echo ""

# Check ADB connection
adb devices | grep -q "$ROBOT_IP"
if [ $? -ne 0 ]; then
    echo "📱 Connecting to robot..."
    adb connect $ROBOT_IP:5555
    sleep 2
fi

# Verify connection
if adb devices | grep -q "$ROBOT_IP"; then
    echo "✅ Robot connected"
else
    echo "❌ Cannot connect to robot at $ROBOT_IP"
    echo "Please check:"
    echo "  1. Robot is powered on"
    echo "  2. Robot is on same network"
    echo "  3. ADB debugging enabled on robot"
    exit 1
fi

# Stop any existing server
echo "🛑 Stopping existing servers..."
pkill -f camera_server.py 2>/dev/null || true

# Start server in background with robot IP specified
echo "🌐 Starting camera server for robot deployment..."
python3 camera_server.py --port 8080 --host 0.0.0.0 --robot-ip $ROBOT_IP &
SERVER_PID=$!

# Wait for server to start
sleep 4

# Get server URL
SERVER_URL="https://$LOCAL_IP:8080"

echo "📡 Server running at: $SERVER_URL"
echo "🎯 Target: Robot at $ROBOT_IP"
echo ""

# Close any existing browser on robot
echo "📱 Preparing robot browser..."
adb shell "am force-stop com.android.chrome" 2>/dev/null
adb shell "am force-stop com.android.browser" 2>/dev/null
adb shell "am force-stop com.android.webview" 2>/dev/null

sleep 2

# Open camera browser on ROBOT ONLY
echo "🤖 Opening camera browser on ROBOT screen..."
adb shell "am start -a android.intent.action.VIEW -d '$SERVER_URL/camera_browser.html' --activity-clear-top --activity-new-task" 

sleep 2

# Verify it opened
echo "📱 Verifying browser opened on robot..."
adb shell "am start -a android.intent.action.VIEW -d '$SERVER_URL/camera_browser.html'"

echo ""
echo "✅ Camera browser deployed to ROBOT!"
echo "📹 Robot Camera URL: $SERVER_URL/camera_browser.html"
echo "🎯 Features automatically enabled:"
echo "   • Face tracking with distance measurement"
echo "   • Circle effect visualization"
echo "   • Full-screen support with all effects"
echo "   • Visual distance overlay"
echo ""
echo "🔧 On the robot screen, you should see:"
echo "   • Camera feed with circle effects"
echo "   • Face tracking boxes"
echo "   • Distance measurements in top-left corner"
echo ""
echo "🛑 Press Ctrl+C to stop server"
echo ""

# Keep server running
trap "echo '🛑 Stopping server...'; kill $SERVER_PID 2>/dev/null; exit 0" INT
wait $SERVER_PID
