# 🤖 Robot Camera Browser

A standalone web browser application with built-in camera functionality designed to run directly on the robot. This provides immediate camera access and real-time video controls similar to [webcammictest.com](https://webcammictest.com).

## 📋 Features

- **🎥 Live Camera Feed**: Immediate camera access when the page loads
- **🎛️ Real-time Controls**: Brightness, contrast, saturation, and hue adjustments
- **📏 Grid Overlay**: Positioning grid for camera alignment
- **⛶ Fullscreen Mode**: Full-screen camera view
- **🔒 HTTPS Support**: Secure connection required for camera access
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Option 1: Use the Launcher (Recommended)
```bash
./start_camera_browser.sh
```

### Option 2: Direct Python Server
```bash
# HTTPS (Recommended)
python3 camera_server.py

# HTTP (Fallback)
python3 camera_server.py --http

# Custom Port
python3 camera_server.py --port 8081
```

### Option 3: Simple File Server (Limited functionality)
```bash
# Open the HTML file directly in browser (may have camera restrictions)
open camera_browser.html
```

## 🌐 Access URLs

Once the server is running:
- **Main Interface**: `https://localhost:8080/`
- **Direct Camera Page**: `https://localhost:8080/camera_browser.html`

## 🎮 Camera Controls

| Control | Function |
|---------|----------|
| **📹 Start Camera** | Request camera access and begin video feed |
| **⏹️ Stop Camera** | Stop the camera and release resources |
| **📏 Toggle Grid** | Show/hide positioning grid overlay |
| **⛶ Fullscreen** | Enter/exit fullscreen mode |
| **🔄 Reset Filters** | Reset all visual filters to default |

## 🎨 Visual Adjustments

- **💡 Brightness**: Adjust image brightness (0-200%)
- **🌓 Contrast**: Modify image contrast (0-200%)
- **🎨 Saturation**: Control color saturation (0-200%)
- **🌈 Hue**: Rotate color hue (0-360°)

## 🔧 Technical Details

### Files
- `camera_browser.html` - Main camera interface
- `camera_server.py` - Python HTTP/HTTPS server
- `start_camera_browser.sh` - Launcher script

### Requirements
- **Python 3.x** - For running the server
- **Modern Browser** - Chrome, Firefox, Safari, Edge
- **Camera Device** - Webcam or built-in camera
- **HTTPS** - Required for camera access (auto-generated certificates)

### Browser Compatibility
- ✅ Chrome 63+
- ✅ Firefox 60+
- ✅ Safari 11+
- ✅ Edge 79+

## 🔒 Security & Permissions

### Camera Access
Modern browsers require HTTPS for camera access. The server automatically creates self-signed certificates.

**First-time setup:**
1. Browser will show security warning
2. Click "Advanced" or "Show Details"
3. Click "Proceed to localhost" or "Accept Risk"
4. Allow camera access when prompted

### Certificate Warnings
Self-signed certificates trigger browser warnings. This is normal and safe for local development.

## 🛠️ Troubleshooting

### Camera Not Working
1. **Check HTTPS**: Ensure using `https://` not `http://`
2. **Allow Permissions**: Grant camera access in browser
3. **Close Other Apps**: Ensure camera isn't used by other applications
4. **Try Different Browser**: Some browsers have stricter policies

### Server Won't Start
```bash
# If port 8080 is busy, try different port
python3 camera_server.py --port 8081
```

### Certificate Issues
```bash
# Regenerate certificates
rm server.crt server.key
python3 camera_server.py
```

## 🤖 Robot Integration

This camera browser is designed to run directly on the robot system:

1. **Copy files** to robot's web directory
2. **Start server** using the launcher script
3. **Access via robot's IP**: `https://robot-ip:8080/`
4. **Control remotely** from any device on the network

## 📝 Command Line Options

```bash
python3 camera_server.py [OPTIONS]

Options:
  --port PORT     Server port (default: 8080)
  --http          Use HTTP instead of HTTPS
  --no-browser    Don't auto-open browser
  -h, --help      Show help message
```

## 🔍 Example Usage

```bash
# Start with default HTTPS on port 8080
python3 camera_server.py

# Start on custom port with HTTP
python3 camera_server.py --port 9000 --http

# Start without opening browser automatically
python3 camera_server.py --no-browser
```

## 📞 Support

The camera browser is designed to work out-of-the-box with minimal configuration. If you encounter issues:

1. Check browser console for error messages
2. Verify camera device is connected and working
3. Ensure no other applications are using the camera
4. Try a different browser or incognito mode

---

**Built for robot vision and remote monitoring applications** 🤖📹
