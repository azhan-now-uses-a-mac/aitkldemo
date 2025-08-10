#!/bin/bash

# Robot Camera Browser Launcher
# Quick launcher for the camera browser server

echo "🤖 Robot Camera Browser Launcher"
echo "================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 to run the camera server"
    exit 1
fi

# Change to the script directory
cd "$(dirname "$0")"

echo "📁 Working directory: $(pwd)"
echo "🐍 Python version: $(python3 --version)"
echo ""

# Check if camera_browser.html exists
if [ ! -f "camera_browser.html" ]; then
    echo "❌ camera_browser.html not found in current directory"
    exit 1
fi

# Check if camera_server.py exists
if [ ! -f "camera_server.py" ]; then
    echo "❌ camera_server.py not found in current directory"
    exit 1
fi

echo "✅ All files found"
echo ""

# Make the Python server executable
chmod +x camera_server.py

# Show available options
echo "🚀 Starting Camera Browser Server..."
echo ""
echo "Available options:"
echo "  1. HTTPS (Recommended - required for camera)"
echo "  2. HTTP (Fallback - may not work with camera)"
echo "  3. Custom port"
echo "  4. Exit"
echo ""

read -p "Choose option (1-4) [default: 1]: " choice

case $choice in
    1|"")
        echo "🔒 Starting HTTPS server on port 8080..."
        python3 camera_server.py
        ;;
    2)
        echo "⚠️  Starting HTTP server on port 8080..."
        python3 camera_server.py --http
        ;;
    3)
        read -p "Enter port number [8080]: " port
        port=${port:-8080}
        echo "🔒 Starting HTTPS server on port $port..."
        python3 camera_server.py --port $port
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Starting default HTTPS server..."
        python3 camera_server.py
        ;;
esac
