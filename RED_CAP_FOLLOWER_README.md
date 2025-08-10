# 🔴 Red Cap Follower Robot

An advanced AI-powered system that makes your robot follow a red cap/hat while maintaining a safe distance using computer vision and real-time distance calculation.

## 🌟 Features

- **Real-time Red Object Detection**: Advanced computer vision to detect and track red caps/hats
- **Distance Measurement**: Calculates distance to the target using object size analysis
- **Intelligent Following**: Maintains configurable safe distance while following
- **Robot Integration**: Direct integration with Ohmni robot control system
- **Web-based Interface**: Modern, responsive web interface with live camera feed
- **Safety Features**: Emergency stop, collision avoidance, and manual override
- **Calibration System**: Distance calibration for accurate measurements

## 🚀 Quick Start

### 1. Launch the System
```bash
./start_red_cap_follower.sh
```

### 2. Put on Your Red Cap
Make sure you're wearing a bright red cap or hat that's clearly visible.

### 3. Use the Interface
1. Click **"Start Camera"** on the robot screen
2. Click **"Start Tracking"** to begin red object detection
3. Adjust settings if needed (red sensitivity, follow distance)
4. Click **"Calibrate Distance"** when you're at your desired follow distance
5. Click **"Start Following"** to activate robot following

## 🎮 Controls

### Main Controls
- **📹 Start Camera**: Activates the camera feed
- **🎯 Start Tracking**: Begins red object detection
- **🤖 Start Following**: Activates robot following mode
- **📏 Calibrate Distance**: Calibrates distance measurement
- **🔄 Reset**: Resets all systems

### Settings
- **🔴 Red Sensitivity**: Adjusts how sensitive the detection is to red objects (10-100)
- **📏 Min Object Size**: Minimum size for object detection (100-2000 pixels)
- **🎯 Follow Distance**: Target distance to maintain (50-200 cm)
- **⚡ Robot Speed**: Robot movement speed (500-3000)

## 📊 Visual Indicators

### Distance Display
- **🔴 TOO CLOSE**: Robot will back away
- **✅ PERFECT**: Ideal following distance
- **🟠 TOO FAR**: Robot will move closer

### Object Detection
- **Green Box**: Red object detected at good distance
- **Orange Box**: Object too far away
- **Red Box**: Object too close
- **Crosshair**: Center point of detected object

## 🔧 Technical Details

### System Components

1. **red_cap_follower.html**: Web interface with computer vision
2. **robot_controller.py**: Python server for robot communication
3. **camera_server.py**: HTTPS camera server
4. **start_red_cap_follower.sh**: System launcher

### Robot Commands
The system translates visual tracking into robot movements:
- **Forward**: Move closer to target
- **Backward**: Move away from target
- **Left/Right**: Turn to center target
- **Stop**: Maintain current position

### Communication Flow
```
Web Interface → HTTP Commands → Python Controller → ADB → Robot
```

## ⚙️ Configuration

### Distance Calibration
1. Stand at your desired follow distance from the robot
2. Make sure you're wearing the red cap and it's clearly visible
3. Click **"Calibrate Distance"** 
4. The system will calculate the focal length for accurate distance measurement

### Red Detection Tuning
- **High Sensitivity**: Detects more red objects but may include false positives
- **Low Sensitivity**: More selective but may miss faint red objects
- **Object Size**: Filters out small red objects (prevents false detections)

## 🚨 Safety Features

### Automatic Safety
- **Rate Limiting**: Commands are rate-limited to prevent jerky movements
- **Dead Zone**: Small movements are ignored for stability
- **Emergency Stop**: Automatic stop if target is lost
- **Distance Limits**: Won't move closer than minimum safe distance

### Manual Safety
- **Stop Button**: Immediately stops robot movement
- **Manual Override**: Can manually control robot at any time
- **Fallback Mode**: Shows manual commands if automatic control fails

## 🛠️ Troubleshooting

### Robot Not Connecting
```bash
# Check ADB connection
adb devices

# Reconnect to robot
adb connect 172.16.215.191:5555
```

### Camera Not Working
- Ensure HTTPS permissions are granted
- Check camera permissions in browser
- Try refreshing the page

### Red Detection Issues
- Increase red sensitivity
- Ensure good lighting
- Use a bright, solid red cap
- Adjust minimum object size

### Robot Not Following
- Check robot controller is running (port 8081)
- Verify robot commands in console
- Ensure robot is powered and connected
- Check ADB connection

## 📱 Browser Compatibility

### Recommended Browsers
- ✅ Chrome/Chromium (best performance)
- ✅ Firefox
- ✅ Safari
- ⚠️ Edge (may have camera issues)

### Requirements
- HTTPS support (for camera access)
- WebRTC/getUserMedia support
- Canvas 2D support
- Modern JavaScript (ES6+)

## 🔍 Advanced Usage

### Custom Robot Integration
The system can be adapted for other robots by modifying `robot_controller.py`:

```python
# Customize these methods for your robot
def send_command(self, cmd):
    # Your robot command implementation
    pass

def send_dual_wheel(self, left_speed, right_speed):
    # Your robot movement implementation  
    pass
```

### API Endpoints
- `POST /robot/command`: Send movement commands
  ```json
  {"command": "forward|backward|left|right|stop"}
  ```

### Distance Calculation
The system uses pinhole camera model:
```
distance = (real_object_width * focal_length) / pixel_width
```

## 📈 Performance Tips

### For Better Detection
- Use solid, bright red objects
- Ensure good lighting conditions
- Avoid shadows and reflections
- Keep the red object clearly visible

### For Smooth Following
- Calibrate distance for accurate measurements
- Adjust follow distance based on environment
- Use moderate robot speed settings
- Ensure stable network connection

## 🔄 System Restart

To restart the entire system:
```bash
# Stop current system (Ctrl+C)
# Then restart
./start_red_cap_follower.sh
```

## 📞 Support

### Log Files
Check console output for debugging information:
- Camera server logs
- Robot controller logs  
- Browser console (F12)

### Common Issues
1. **"Robot command failed"**: Check ADB connection
2. **"No red objects detected"**: Adjust sensitivity/lighting
3. **"Camera access failed"**: Check browser permissions
4. **"Controller not responding"**: Restart Python controller

---

## 🎯 Enjoy Your Red Cap Following Robot!

The system is designed to be safe, reliable, and fun to use. Start with conservative settings and gradually adjust for optimal performance in your environment.

**Remember**: Always supervise the robot and keep the emergency stop ready! 🛑
