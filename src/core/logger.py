"""
Logging utilities for IDPS
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from config.settings import LOG_FORMAT, LOG_LEVEL, LOGS_DIR

class IDPSLogger:
    """Custom logger for IDPS system"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_console_handler()
            self._setup_file_handler()
    
    def _setup_console_handler(self):
        """Setup console logging handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file logging handler"""
        log_file = LOGS_DIR / f"idps_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

def get_logger(name):
    """Get logger instance"""
    return IDPSLogger(name)
