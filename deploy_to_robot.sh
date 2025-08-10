#!/bin/bash

# Deploy Camera Browser to Robot
# This script copies the camera browser files to the robot and starts the server

ROBOT_IP="172.16.215.191"
ROBOT_PATH="/data/data/com.ohmnilabs.telebot_rtc/files/camera_browser"
LOCAL_PATH="/Users/azhan/Pictures/Mizo_Main"

echo "🤖 Deploying Camera Browser to Robot"
echo "====================================="
echo "Robot IP: $ROBOT_IP"
echo "Robot Path: $ROBOT_PATH"
echo ""

# Check if ADB is available
if ! command -v adb &> /dev/null; then
    echo "❌ ADB is not installed or not in PATH"
    echo "Please install Android Debug Bridge (ADB) to deploy to robot"
    exit 1
fi

# Check ADB connection
echo "📱 Checking ADB connection..."
adb devices | grep -q "$ROBOT_IP"
if [ $? -ne 0 ]; then
    echo "⚠️  Robot not found in ADB devices. Attempting to connect..."
    adb connect $ROBOT_IP
    sleep 2
    
    adb devices | grep -q "$ROBOT_IP"
    if [ $? -ne 0 ]; then
        echo "❌ Could not connect to robot at $ROBOT_IP"
        echo "Please ensure:"
        echo "  1. Robot is powered on and connected to network"
        echo "  2. ADB debugging is enabled on robot"
        echo "  3. Robot IP address is correct in script"
        exit 1
    fi
fi

echo "✅ Connected to robot"

# Create directory on robot
echo "📁 Creating directory on robot..."
adb shell "su -c 'mkdir -p $ROBOT_PATH'"

# Copy files to robot
echo "📤 Copying camera browser files..."
adb push "$LOCAL_PATH/camera_browser.html" "$ROBOT_PATH/"
adb push "$LOCAL_PATH/camera_server.py" "$ROBOT_PATH/"

# Make Python script executable
adb shell "su -c 'chmod +x $ROBOT_PATH/camera_server.py'"

echo "✅ Files deployed successfully"
echo ""

# Check if Python is available on robot
echo "🐍 Checking Python on robot..."
PYTHON_CMD=""
if adb shell "python3 --version" 2>/dev/null | grep -q "Python"; then
    PYTHON_CMD="python3"
    echo "✅ Python 3 found"
elif adb shell "python --version" 2>/dev/null | grep -q "Python"; then
    PYTHON_CMD="python"
    echo "✅ Python found"
else
    echo "❌ Python not found on robot"
    echo "Please install Python on the robot or use alternative method"
    exit 1
fi

echo ""
echo "🚀 Starting camera server on robot..."
echo "Server will be accessible at: https://$ROBOT_IP:8080/"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the server on robot and open browser
adb shell "su -c 'cd $ROBOT_PATH && $PYTHON_CMD camera_server.py --robot-ip $ROBOT_IP --port 8080'"
