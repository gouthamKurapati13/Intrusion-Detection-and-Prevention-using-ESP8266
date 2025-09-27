"""
Intrusion Detection System Monitor - Main monitoring service
"""
import pandas as pd
import time
import json
import os
from datetime import datetime
from pathlib import Path
from config.settings import (
    LOGIN_ATTEMPTS_LOG, AUDIT_LOGS_DIR, 
    MONITOR_INTERVAL, DETECTION_THRESHOLD
)
from src.core.ml_model import intrusion_model
from src.core.ip_manager import ip_manager
from src.core.logger import get_logger

logger = get_logger(__name__)

class IDSMonitor:
    """Main intrusion detection monitoring service"""
    
    def __init__(self):
        self.seen_rows = 0
        self.log_file = LOGIN_ATTEMPTS_LOG
        self.audit_dir = AUDIT_LOGS_DIR
        self.monitor_interval = MONITOR_INTERVAL
        self.detection_threshold = DETECTION_THRESHOLD
        
        # Ensure directories exist
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("IDS Monitor initialized")
    
    def log_audit(self, ip, record):
        """Log audit information for an IP address"""
        try:
            # Create filename from IP (replace dots with underscores)
            filename = f"{ip.replace('.', '_')}.json"
            filepath = self.audit_dir / filename
            
            # Load existing data or create new list
            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Add new record
            data.append(record)
            
            # Save updated data
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Audit logged for IP {ip}")
            
        except Exception as e:
            logger.error(f"Error logging audit for IP {ip}: {e}")
    
    def process_new_attempts(self):
        """Process new login attempts from the log file"""
        try:
            if not self.log_file.exists():
                logger.debug("Login attempts log file does not exist yet")
                return
            
            # Read the CSV file
            df = pd.read_csv(
                self.log_file, 
                header=None, 
                names=["ip", "username", "password", "timestamp"]
            )
            
            # Get only new rows
            new_df = df.iloc[self.seen_rows:]
            
            if len(new_df) == 0:
                return
            
            logger.info(f"Processing {len(new_df)} new login attempts")
            
            # Update seen rows count
            self.seen_rows = len(df)
            
            # Process each new attempt
            for _, row in new_df.iterrows():
                self.analyze_attempt(row)
                
        except Exception as e:
            logger.error(f"Error processing login attempts: {e}")
    
    def analyze_attempt(self, row):
        """Analyze a single login attempt"""
        try:
            ip = row['ip']
            username = row['username']
            password = row['password']
            timestamp = row['timestamp']
            
            # Skip if IP is already blocked
            if ip_manager.is_ip_blocked(ip):
                logger.debug(f"IP {ip} already blocked, skipping analysis")
                return
            
            # Make prediction using ML model
            prediction = intrusion_model.predict(username, password, timestamp)
            
            # Create audit record
            audit_record = {
                "ip": ip,
                "username": username,
                "password": password,
                "timestamp": timestamp,
                "prediction": int(prediction),
                "analyzed_at": datetime.now().isoformat(),
                "action": "MONITORED"
            }
            
            # If intrusion detected
            if prediction == 1:
                logger.warning(f"🚨 INTRUSION DETECTED from IP: {ip} (user: {username})")
                
                # Block the IP
                if ip_manager.block_ip(ip):
                    audit_record["action"] = "BLOCKED"
                    logger.info(f"✅ IP {ip} has been blocked")
                else:
                    logger.error(f"❌ Failed to block IP {ip}")
                    audit_record["action"] = "BLOCK_FAILED"
            else:
                logger.debug(f"Normal activity from IP: {ip} (user: {username})")
            
            # Log audit information
            self.log_audit(ip, audit_record)
            
        except Exception as e:
            logger.error(f"Error analyzing attempt from {row.get('ip', 'unknown')}: {e}")
    
    def get_statistics(self):
        """Get monitoring statistics"""
        try:
            stats = {
                "monitor_active": True,
                "seen_rows": self.seen_rows,
                "blocked_ips_count": ip_manager.get_blocked_count(),
                "model_info": intrusion_model.model_info(),
                "last_check": datetime.now().isoformat()
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}
    
    def run(self):
        """Main monitoring loop"""
        logger.info("🔍 Starting IDS Monitor...")
        logger.info(f"Monitoring interval: {self.monitor_interval} seconds")
        
        # Check if model is trained
        if not intrusion_model.is_trained:
            logger.warning("⚠️  ML model is not trained. Predictions may be inaccurate.")
            logger.info("To train the model, run: python -m src.tools.train_model")
        
        try:
            while True:
                self.process_new_attempts()
                time.sleep(self.monitor_interval)
                
        except KeyboardInterrupt:
            logger.info("👋 IDS Monitor stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error in monitor: {e}")
            raise

def run_monitor():
    """Run the IDS monitor"""
    monitor = IDSMonitor()
    monitor.run()

if __name__ == '__main__':
    run_monitor()
