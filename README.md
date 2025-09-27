# Intrusion Detection and Prevention System (IDPS)

A comprehensive Python-based Intrusion Detection and Prevention System that monitors login attempts, detects suspicious activities using machine learning, and automatically blocks malicious IPs.

## 🚀 Features

- **Real-time Monitoring**: Continuously monitors login attempts and network activity
- **Machine Learning Detection**: Uses Random Forest classifier to identify suspicious patterns
- **Automatic IP Blocking**: Automatically blocks IPs identified as threats
- **Web Dashboard**: Real-time dashboard to monitor system status and manage blocked IPs
- **Audit Logging**: Comprehensive logging and audit trail for security analysis
- **Attack Simulation**: Built-in tools for testing system effectiveness

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
│   │   └── dashboard.py     # Streamlit dashboard
│   └── tools/
│       ├── __init__.py
│       ├── train_model.py   # Model training utility
│       └── attack_sim.py    # Attack simulation tool
├── data/
│   ├── logs/
│   ├── audit_logs/
│   ├── models/
│   └── blocked_ips.txt
├── requirements.txt
├── setup.py
├── run_server.py           # Server startup script
├── run_monitor.py          # Monitor startup script
├── run_dashboard.py        # Dashboard startup script
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

**Option A: Start All Components at Once**
```bash
# Make sure virtual environment is activated
source idps_env/bin/activate  # Linux/Mac
# idps_env\Scripts\activate   # Windows

# Start all components with one command
python idps_control.py start
```

**Option B: Interactive Control Mode**
```bash
# Make sure virtual environment is activated
source idps_env/bin/activate

# Launch interactive control
python idps_control.py

# Available commands in interactive mode:
# start   - Start all components
# stop    - Stop all components
# status  - Show component status
# restart - Restart all components
# quit    - Exit interactive mode
```

### Manual Start (Advanced Users)

If you prefer to start each component separately in different terminals:

**Terminal 1: Web Server**
```bash
source idps_env/bin/activate
python run_server.py
```

**Terminal 2: IDS Monitor**
```bash
source idps_env/bin/activate
python run_monitor.py
```

**Terminal 3: Dashboard**
```bash
source idps_env/bin/activate
python run_dashboard.py
```

### Control Commands

```bash
# Direct control commands (with virtual environment activated)
python idps_control.py start      # Start all components
python idps_control.py stop       # Stop all components
python idps_control.py status     # Show status of all components
python idps_control.py restart    # Restart all components
python idps_control.py            # Interactive mode (default)
```

### Accessing the System

Once the system is running, you can access:
- **Web Server**: http://localhost:5000 (Login form for testing attacks)
- **Dashboard**: http://localhost:8501 (Real-time monitoring and management)

### Testing the System

**Basic Attack Simulation**
```bash
# Make sure virtual environment is activated
source idps_env/bin/activate

# Run basic brute force attack simulation
python -m src.tools.attack_sim
```

**Advanced Attack Simulations**
```bash
# Brute force attack with custom parameters
python -m src.tools.attack_sim --type brute_force --attempts 30 --delay 1

# Credential stuffing attack
python -m src.tools.attack_sim --type credential_stuffing

# Slow stealth attack
python -m src.tools.attack_sim --type slow --attempts 20

# Mixed attack pattern
python -m src.tools.attack_sim --type mixed
```

### Model Management

**Train/Retrain the ML Model**
```bash
# Make sure virtual environment is activated
source idps_env/bin/activate

# Train the machine learning model
python -m src.tools.train_model
```

### Stopping the System

**Using Control Script**
```bash
python idps_control.py stop
```

**Manual Stop**
- Use `Ctrl+C` in each terminal running the components
- Or use the interactive control mode to stop all components

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Server ports and hosts
- File paths for logs and data
- Model parameters
- Monitoring intervals
- Alert thresholds

## 📊 Dashboard Features

The web dashboard provides:
- **Real-time Login Attempts**: View recent login attempts
- **Blocked IPs Management**: View and manage blocked IP addresses
- **Audit Logs**: Detailed logs for each IP address
- **System Statistics**: Overview of system performance
- **Manual Controls**: Unblock IPs and clear logs

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

1. Start all three components (server, monitor, dashboard)
2. Run the attack simulation: `python -m src.tools.attack_sim`
3. Monitor the dashboard to see detections and blocks
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
3. ✅ System initialized (`python setup.py`)
4. ✅ System started (`python idps_control.py start`)
5. ✅ Tested with attack simulation (`python -m src.tools.attack_sim`)

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
```bash
# Complete system test sequence
source idps_env/bin/activate
python idps_control.py status    # Check system status
python idps_control.py start     # Start all components
# Wait 10 seconds for startup
python -m src.tools.attack_sim   # Run attack simulation
python idps_control.py stop      # Stop all components
```

## ⚠️ Disclaimer

This system is designed for educational and research purposes. When deploying in production environments, ensure proper security measures and compliance with applicable laws and regulations.

### Support

For additional support, please open an issue on the project repository.
