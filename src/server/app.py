"""
Flask web server for IDPS - handles login attempts and logs them
"""
from flask import Flask, request, render_template, jsonify
import csv
import os
from datetime import datetime
from pathlib import Path
from config.settings import SERVER_HOST, SERVER_PORT, DEBUG_MODE, LOGIN_ATTEMPTS_LOG
from src.core.ip_manager import ip_manager
from src.core.logger import get_logger

logger = get_logger(__name__)
app = Flask(__name__, template_folder='templates')

def ensure_log_file():
    """Ensure the login attempts log file exists with headers"""
    if not LOGIN_ATTEMPTS_LOG.exists():
        LOGIN_ATTEMPTS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOGIN_ATTEMPTS_LOG, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header if needed (optional)
            pass

@app.before_first_request
def initialize():
    """Initialize the application"""
    ensure_log_file()
    logger.info("Flask server initialized")

@app.route('/')
def index():
    """Main page with login form"""
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login attempts"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Get client IP address
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    
    # Check if IP is blocked
    if ip_manager.is_ip_blocked(ip):
        logger.warning(f"Blocked IP {ip} attempted login")
        return "Access Denied - IP Blocked", 403
    
    # Get login credentials
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the attempt
    try:
        with open(LOGIN_ATTEMPTS_LOG, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ip, username, password, timestamp])
        
        logger.info(f"Login attempt logged: {ip} - {username}")
    except Exception as e:
        logger.error(f"Error logging login attempt: {e}")
    
    # Simulate login response (always fails for security)
    return "Invalid credentials", 401

@app.route('/status')
def status():
    """API endpoint for server status"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "blocked_ips_count": ip_manager.get_blocked_count()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error for {request.url} from {request.remote_addr}")
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error for {request.url}: {error}")
    return "Internal server error", 500

def run_server():
    """Run the Flask server"""
    logger.info(f"Starting IDPS server on {SERVER_HOST}:{SERVER_PORT}")
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG_MODE,
        threaded=True
    )

if __name__ == '__main__':
    run_server()
