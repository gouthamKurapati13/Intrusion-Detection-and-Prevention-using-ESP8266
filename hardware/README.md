# ESP8266 Hardware Attacker Setup Guide

## Overview
This hardware-based attack simulator uses an ESP8266 microcontroller to perform real-time brute force attacks against your IDPS system. It provides visual feedback through LEDs and detailed logging via serial output.

## Prerequisites

### Hardware Requirements:
- ESP8266 development board (NodeMCU v1.0 or Wemos D1 Mini recommended)
- 2x LEDs (Blue and White/Red)
- 2x 220Ω resistors
- Breadboard and jumper wires
- USB cable for programming

### Software Requirements:
- Arduino IDE (1.8.x or newer)
- ESP8266 Board Package for Arduino IDE
- ESP8266WiFi and ESP8266HTTPClient libraries (included with board package)

## Arduino IDE Setup

### 1. Install ESP8266 Board Package:
1. Open Arduino IDE
2. Go to `File` → `Preferences`
3. Add this URL to "Additional Board Manager URLs":
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
4. Go to `Tools` → `Board` → `Boards Manager`
5. Search for "ESP8266" and install the package by ESP8266 Community

### 2. Configure Board Settings:
- **Board**: "NodeMCU 1.0 (ESP-12E Module)" or "LOLIN(WEMOS) D1 R2 & mini"
- **Upload Speed**: 115200
- **CPU Frequency**: 80 MHz
- **Flash Size**: "4MB (FS:2MB OTA:~1019KB)"
- **Port**: Select your ESP8266's COM port

## Configuration

### 1. WiFi Settings:
Update these lines in `esp8266_attacker.ino`:
```cpp
const char* ssid = "YourWiFiName";        // Your WiFi network name
const char* password = "YourWiFiPassword"; // Your WiFi password
```

### 2. IDPS Server Settings:
Update the server URL to match your IDPS system:
```cpp
const char* server = "http://YOUR_IDPS_IP:5000/login";
```

To find your IDPS server IP:
1. Run your IDPS system with `python setup.py`
2. Note the IP address displayed in the terminal
3. Or use `ip addr show` on Linux/Mac or `ipconfig` on Windows

### 3. Attack Credentials (Optional):
Modify the username and password arrays to test different credentials:
```cpp
String usernames[] = {"admin", "user", "test", "root", "guest"};
String passwords[] = {"123", "admin", "pass", "password", "test", "123456", "qwerty"};
```

## Upload and Testing

### 1. Upload Code:
1. Connect ESP8266 to computer via USB
2. Select correct board and port in Arduino IDE
3. Open `esp8266_attacker.ino`
4. Click "Upload" button
5. Wait for compilation and upload to complete

### 2. Monitor Serial Output:
1. After upload, open `Tools` → `Serial Monitor`
2. Set baud rate to 115200
3. You should see connection status and attack logs

### 3. Expected Serial Output:
```
=== ESP8266 IDPS Attacker Started ===
Connecting to WiFi: YourWiFiName.....
✅ Connected to WiFi!
📍 Local IP: 192.168.1.123
🎯 Target Server: http://192.168.1.100:5000/login
🚀 Starting attack simulation...

[ATTACK] admin:123 → HTTP 401 ❌ INVALID
[ATTACK] admin:admin → HTTP 403 🚫 BLOCKED
[ATTACK] admin:pass → HTTP 401 ❌ INVALID
```

## LED Indicators

| LED State | Meaning | HTTP Response |
|-----------|---------|---------------|
| Blue LED ON | Attack Blocked | HTTP 403 (Forbidden) |
| White LED ON | Attack Success | HTTP 200 (OK) |
| Both LEDs ON | Error/Unknown | Other HTTP codes |
| Both LEDs OFF | Normal/Invalid | HTTP 401 (Unauthorized) |

## Troubleshooting

### Common Issues:

1. **WiFi Connection Failed**:
   - Check SSID and password
   - Ensure ESP8266 is within WiFi range
   - Try 2.4GHz networks only (ESP8266 doesn't support 5GHz)

2. **HTTP Connection Failed**:
   - Verify IDPS server IP address
   - Ensure IDPS system is running
   - Check if ESP8266 and server are on same network

3. **Upload Failed**:
   - Check USB cable connection
   - Try different COM port
   - Press and hold FLASH button during upload (some boards)

4. **LEDs Not Working**:
   - Check LED polarity (longer leg is positive)
   - Verify resistor values (220Ω)
   - Check GPIO pin connections

### Debug Steps:
1. Monitor Serial output for detailed logs
2. Test WiFi connection first
3. Verify server accessibility from browser
4. Check LED connections with simple blink test

## Safety and Legal Notes

⚠️ **Important Warnings**:
- Only use this against your own IDPS system
- Do not use for unauthorized access attempts
- This is for educational and testing purposes only
- Ensure you have permission before testing on any network
- Be aware of your local laws regarding network security testing

## Integration with IDPS

Once the hardware attacker is running:
1. Monitor your IDPS dashboard at http://localhost:8501
2. Check for blocked IPs and attack detection
3. Review audit logs for attack patterns
4. Test different attack scenarios by modifying the credential arrays
5. Use this as a real-world testing tool for your IDPS effectiveness
