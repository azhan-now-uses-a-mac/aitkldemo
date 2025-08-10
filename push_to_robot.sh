#!/bin/bash

# Quick Push Camera Browser to Robot
# Deploys both advanced and simple versions

ROBOT_IP="172.16.215.191"
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)

echo "🚀 Pushing Camera Browser with Face Tracking to Robot"
echo "===================================================="
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
    echo "❌ Cannot connect to robot"
    exit 1
fi

# Stop any existing server
echo "🛑 Stopping existing servers..."
pkill -f camera_server.py 2>/dev/null || true

# Start server in background
echo "🌐 Starting camera server with face tracking..."
python3 camera_server.py --port 8080 --host 0.0.0.0 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Get server URL
SERVER_URL="https://$LOCAL_IP:8080"

echo "📡 Server running at: $SERVER_URL"
echo ""

# Open browser on robot - single attempt to avoid multiple tabs
echo "🤖 Opening browser on robot screen..."

# Close any existing browser tabs first
echo "📱 Closing existing browser tabs..."
adb shell "am force-stop com.android.chrome" 2>/dev/null
adb shell "am force-stop com.android.browser" 2>/dev/null

sleep 1

# Open single page with advanced features on ROBOT
echo "📱 Opening camera browser on ROBOT screen..."
adb shell "am start -a android.intent.action.VIEW -d '$SERVER_URL/camera_browser.html' --activity-clear-top --activity-new-task" 2>/dev/null

# Also try to open in robot's default browser
echo "📱 Attempting to launch on robot display..."
adb shell "am start -a android.intent.action.VIEW -d '$SERVER_URL/camera_browser.html' -n com.android.browser/com.android.browser.BrowserActivity" 2>/dev/null

# Force browser activity on robot
echo "📱 Forcing browser launch on robot..."
adb shell "am force-stop com.android.browser" 2>/dev/null
adb shell "am force-stop com.android.chrome" 2>/dev/null
sleep 1
adb shell "am start -a android.intent.action.VIEW -d '$SERVER_URL/camera_browser.html'" 2>/dev/null

echo ""
echo "✅ Browser commands sent to robot!"
echo "📹 Camera with Face Tracking URL: $SERVER_URL"
echo "🎯 Features:"
echo "   • Real-time face detection with green bounding boxes"
echo "   • Motion detection and tracking"
echo "   • Multiple face support"
echo "   • Confidence scores"
echo "   • All camera controls (brightness, contrast, etc.)"
echo ""
echo "🔧 If browser didn't open, manually navigate to: $SERVER_URL"
echo "🛑 Press Ctrl+C to stop server"
echo ""

# Keep server running
trap "echo '🛑 Stopping server...'; kill $SERVER_PID 2>/dev/null; exit 0" INT
wait $SERVER_PID
