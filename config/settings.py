"""
Configuration settings for the Intrusion Detection and Prevention System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
AUDIT_LOGS_DIR = DATA_DIR / "audit_logs"
MODELS_DIR = DATA_DIR / "models"

# File paths
LOGIN_ATTEMPTS_LOG = LOGS_DIR / "login_attempts.csv"
BLOCKED_IPS_FILE = DATA_DIR / "blocked_ips.txt"
MODEL_FILE = MODELS_DIR / "intrusion_model.pkl"

# Server configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
DEBUG_MODE = False

# Dashboard configuration
DASHBOARD_HOST = "localhost"
DASHBOARD_PORT = 8501

# Monitoring configuration
MONITOR_INTERVAL = 2  # seconds
DETECTION_THRESHOLD = 0.5  # ML model threshold

# Model configuration
MODEL_FEATURES = ['username_len', 'password_len', 'timestamp']
RETRAIN_INTERVAL = 3600  # seconds (1 hour)

# Attack patterns (for simulation)
ATTACK_USERNAMES = ["admin", "user", "test", "root", "administrator"]
ATTACK_PASSWORDS = ["123", "admin", "pass", "password", "test", "123456"]
ATTACK_DELAY = 0.5  # seconds between attempts

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [DATA_DIR, LOGS_DIR, AUDIT_LOGS_DIR, MODELS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create empty blocked IPs file if it doesn't exist
    if not BLOCKED_IPS_FILE.exists():
        BLOCKED_IPS_FILE.touch()

# Initialize directories when module is imported
ensure_directories()
