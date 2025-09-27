# Intrusion Detection and Prevention System (IDPS)

A comprehensive Python-based Intrusion Det## 🚀 Running the System

### Super Simple Setup & Startion and Prevention System that monitors login attempts, detects suspicious activities using machine learning, and automatically blocks malicious IPs. Features a modern dark-themed dashboard and intuitive attack simulation interface.

## 🚀 Features

- **Real-time Monitoring**: Continuously monitors login attempts and network activity with live dashboard
- **Machine Learning Detection**: Uses Random Forest classifier to identify suspicious patterns
- **Automatic IP Blocking**: Automatically blocks IPs identified as threats
- **Modern Web Dashboard**: Real-time dark-themed dashboard with enhanced UI for monitoring system status
- **Interactive Attack Simulator**: User-friendly interface for testing various attack scenarios
- **Hardware Attack Simulator**: ESP8266-based physical device for real-world attack testing
- **Monitor Control**: Toggle monitoring on/off directly from the dashboard sidebar
- **Audit Logging**: Comprehensive logging and audit trail for security analysis
- **Attack Simulation**: Built-in software tools and hardware device for comprehensive testing

## 📁 Project Structure

```
idps/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logger.py        # Logging utilities
│   │   ├── ml_model.py      # Machine learning model
│   │   └── ip_manager.py    # IP blocking and management
│   ├── server/
│   │   ├── __init__.py
│   │   ├── app.py           # Flask web server
│   │   └── templates/
│   │       └── login.html   # Login form template
│   ├── monitor/
│   │   ├── __init__.py
│   │   └── ids_monitor.py   # Main monitoring service
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── dashboard.py     # Enhanced Streamlit dashboard with dark theme
│   └── tools/
│       ├── __init__.py
│       ├── train_model.py   # Model training utility
│       ├── attack_sim.py    # Command-line attack simulation tool
│       ├── attack_simulator_ui.py  # Interactive attack simulator UI
│       └── attack_scenarios.py     # Pre-configured attack scenarios
├── data/
│   ├── logs/
│   ├── audit_logs/
│   ├── models/
│   └── blocked_ips.txt
├── hardware/
│   ├── esp8266_attacker.ino    # ESP8266 hardware attacker code
│   ├── circuit_diagram.md      # Circuit schematic and connections
│   └── README.md               # Hardware setup guide
├── requirements.txt
├── setup.py
├── setup.py                # Complete system setup and startup
└── README.md
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd idps
   ```

2. **Create and activate virtual environment (recommended)**
   ```bash
   # Create virtual environment
   python -m venv idps_env
   
   # Activate virtual environment
   # On Linux/Mac:
   source idps_env/bin/activate
   # On Windows:
   # idps_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the system**
   ```bash
   python setup.py
   ```

## � Running the System

### Quick Start (Recommended)

**One Command Does Everything:**
```bash
# Make sure virtual environment is activated
source idps_env/bin/activate  # Linux/Mac
# idps_env\Scripts\activate   # Windows

# Setup and start everything (will ask if you want to start services)
python setup.py
```

That's it! The setup script will:
1. ✅ Initialize the system (create directories, train ML model)
2. ✅ Ask if you want to start all services
3. ✅ Start all services automatically if you choose 'yes'
4. ✅ Display all access URLs

**What gets started:**
- 🌐 **Flask Web Server** (port 5000) - Login form for testing
- 🛡️ **IDS Monitor** - Real-time intrusion detection 
- 📊 **Streamlit Dashboard** (port 8501) - Management interface
- 🧪 **Attack Simulator UI** (port 8502) - Interactive testing tool

### Stopping the System

To stop all services, simply press `Ctrl+C` in the terminal where you ran `python setup.py`.

### Accessing the System

Once all services are running (after running `python setup.py` and choosing 'yes'), you can access:
- **🌐 Web Server**: http://localhost:5000 (Login form for testing attacks)
- **📊 IDPS Dashboard**: http://localhost:8501 (Real-time monitoring and management with dark theme)
- **🧪 Attack Simulator**: http://localhost:8502 (Interactive testing interface)

### Testing the System

**Method 1: Interactive Attack Simulator UI (Software)**

The Attack Simulator UI is automatically started when you run `python setup.py`. Simply open your browser and go to:
- **🧪 Attack Simulator**: http://localhost:8502

The UI provides:
- Pre-configured attack scenarios with detailed descriptions
- Easy-to-use interface for testing different attack types
- Real-time feedback and results
- Options for gentle testing, volumetric attacks, and stealth approaches

**Method 2: Hardware Attack Simulator (ESP8266)**

For real-world testing with physical hardware:
1. Set up the ESP8266 hardware attacker (see `hardware/README.md`)
2. Configure WiFi and server settings in the Arduino code
3. Upload the code to ESP8266
4. Watch LED indicators for real-time attack status:
   - **Blue LED**: Attack blocked by IDPS
   - **White LED**: Attack successful
   - **Both LEDs**: Communication error


### Model Management

**Train/Retrain the ML Model**
```bash
# Make sure virtual environment is activated
source idps_env/bin/activate

# Train the machine learning model
python -m src.tools.train_model
```

### Stopping the System

Simply press `Ctrl+C` in the terminal where you ran `python setup.py`. This will gracefully stop all services.

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Server ports and hosts
- File paths for logs and data
- Model parameters
- Monitoring intervals
- Alert thresholds

## 📊 Dashboard Features

The enhanced web dashboard provides:
- **Modern Dark Theme**: Professional dark-themed interface with improved readability
- **Real-time Login Attempts**: View recent login attempts with styled tables
- **Monitor Control**: Toggle the monitoring system on/off directly from the sidebar
- **Blocked IPs Management**: View and manage blocked IP addresses with enhanced UI
- **Audit Logs**: Detailed logs for each IP address with better formatting
- **System Statistics**: Overview of system performance with real-time updates
- **Manual Controls**: Unblock IPs and clear logs with intuitive interface
- **Auto-refresh**: Optional automatic refresh for real-time monitoring

## 🎯 Attack Simulator Features

### Software Attack Simulator
The interactive web-based attack simulator includes:
- **Pre-configured Scenarios**: Multiple attack types with detailed descriptions
- **Gentle Testing**: Baseline measurements for system calibration
- **Volumetric Testing**: High-volume attack simulations
- **Stealth Testing**: Low and slow attack patterns
- **Real-time Feedback**: Immediate results and system response
- **User-friendly Interface**: Clean, intuitive design for easy testing

### Hardware Attack Simulator (ESP8266)
The physical hardware attacker provides:
- **Real-world Testing**: Physical device simulating actual attacker behavior
- **Visual Feedback**: LED indicators for attack status (blocked/success/error)
- **Autonomous Operation**: Continuous attack simulation without computer dependency
- **Network Integration**: WiFi-enabled for realistic network-based attacks
- **Serial Monitoring**: Detailed attack logs via USB serial connection
- **Configurable Attacks**: Customizable username/password combinations
- **Low Cost**: Affordable ESP8266 microcontroller-based solution

## 🔧 Hardware Attacker Setup

### ESP8266 Real-time Attacker

The hardware component uses an ESP8266 microcontroller to perform real-world attack simulations:

#### Quick Setup:
1. **Hardware Requirements**:
   - ESP8266 (NodeMCU or Wemos D1 Mini)
   - Blue LED + 220Ω resistor (attack blocked indicator)
   - White LED + 220Ω resistor (attack success indicator)
   - Breadboard and jumper wires

2. **Software Setup**:
   - Install Arduino IDE with ESP8266 board package
   - Open `hardware/esp8266_attacker.ino`
   - Configure WiFi credentials and IDPS server IP
   - Upload to ESP8266

3. **Circuit Connections**:
   ```
   ESP8266 D5 → [220Ω] → Blue LED → GND
   ESP8266 D6 → [220Ω] → White LED → GND
   ```

4. **LED Indicators**:
   - **Blue LED ON**: Attack blocked by IDPS (HTTP 403)
   - **White LED ON**: Attack successful (HTTP 200)
   - **Both LEDs ON**: Communication error

For detailed setup instructions, circuit diagrams, and troubleshooting, see `hardware/README.md`.

## 🤖 Machine Learning Model

The system uses a Random Forest classifier that analyzes:
- Username length patterns
- Password length patterns
- Request timing patterns
- IP address behavior

The model is trained on historical data and can be retrained as new data becomes available.

## 🔒 Security Features

- **Automatic IP Blocking**: Suspicious IPs are automatically blocked
- **Audit Logging**: All activities are logged with timestamps
- **Real-time Monitoring**: Continuous monitoring of login attempts
- **Configurable Thresholds**: Adjustable sensitivity settings
- **Manual Override**: Administrative controls for unblocking IPs

## 📝 Logging

The system maintains several types of logs:
- **Login Attempts**: `data/logs/login_attempts.csv`
- **Blocked IPs**: `data/blocked_ips.txt`
- **Audit Logs**: `data/audit_logs/{ip}.json`
- **System Logs**: Console output with timestamps

## 🧪 Testing

To test the system:

**Testing Method 1: Software UI (Recommended)**
1. Run `python setup.py` and choose 'yes' to start all services
2. Open the Attack Simulator UI: http://localhost:8502
3. Choose from pre-configured attack scenarios
4. Monitor the dashboard at http://localhost:8501 to see real-time detections and blocks
5. Check the audit logs for detailed activity records

**Testing Method 2: Hardware ESP8266**
1. Run `python setup.py` and choose 'yes' to start all services
2. Set up ESP8266 hardware attacker (see `hardware/README.md` for detailed setup)
3. Configure ESP8266 with your WiFi and server IP address
4. Upload and run the hardware attacker
5. Monitor LED indicators on ESP8266 and dashboard for real-time attack detection
6. Check audit logs for hardware-generated attack patterns

**Testing Method 3: Command Line**
1. Run `python setup.py` and choose 'yes' to start all services
2. In a new terminal, run the attack simulation: `python -m src.tools.attack_sim`
3. Monitor the dashboard at http://localhost:8501 to see detections and blocks
4. Check the audit logs for detailed activity records

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Notes

### Virtual Environment
Always activate your virtual environment before running any commands:
```bash
# Activate virtual environment (Linux/Mac)
source idps_env/bin/activate

# Activate virtual environment (Windows)
# idps_env\Scripts\activate

# Verify activation (you should see (idps_env) in your prompt)
which python  # Should point to idps_env/bin/python
```

### First Run Checklist
1. ✅ Virtual environment created and activated
2. ✅ Dependencies installed (`pip install -r requirements.txt`)
3. ✅ System setup and started (`python setup.py` → choose 'yes')
4. ✅ Access all interfaces (Dashboard: http://localhost:8501, Simulator: http://localhost:8502)
5. ✅ Tested with attack simulation using the web UI or command line

## 🆘 Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   ```bash
   # If virtual environment is not activated
   source idps_env/bin/activate
   
   # If packages are missing
   pip install -r requirements.txt
   ```

2. **Port Already in Use**
   ```bash
   # Kill processes on ports 5000 and 8501
   lsof -ti:5000 | xargs kill -9
   lsof -ti:8501 | xargs kill -9
   
   # Or change ports in config/settings.py
   ```

3. **Model Not Found**
   ```bash
   # Train the model first
   source idps_env/bin/activate
   python -m src.tools.train_model
   ```

4. **Permission Errors**
   - Check file permissions for log directories
   - Ensure you have write permissions in the project directory

5. **Import Errors**
   ```bash
   # Make sure you're in the project directory
   cd "/path/to/Intrusion Detection and Prevention System"
   
   # Make sure virtual environment is activated
   source idps_env/bin/activate
   ```

### Quick System Test

**Complete System Test**
```bash
# Complete system test sequence
source idps_env/bin/activate
python setup.py                  # Setup and start all services (choose 'yes')
# Wait for all services to start, then:
# 1. Open http://localhost:8502 for attack simulator
# 2. Open http://localhost:8501 for dashboard
# 3. Test attacks and monitor results
# 4. Press Ctrl+C to stop everything
```

## ⚠️ Disclaimer

This system is designed for educational and research purposes. When deploying in production environments, ensure proper security measures and compliance with applicable laws and regulations.

### Support

For additional support, please open an issue on the project repository.
