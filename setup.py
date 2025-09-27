#!/usr/bin/env python3
"""
Setup script for IDPS - Initialize the system
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import ensure_directories
from src.core.logger import get_logger
from src.tools.train_model import train_model

logger = get_logger(__name__)

def setup_system():
    """Initialize the IDPS system"""
    logger.info("🔧 Initializing IDPS System...")
    logger.info("=" * 50)
    
    try:
        # Ensure all directories exist
        logger.info("📁 Creating necessary directories...")
        ensure_directories()
        logger.info("✅ Directories created successfully")
        
        # Train initial model
        logger.info("🤖 Training initial ML model...")
        if train_model():
            logger.info("✅ Model trained successfully")
        else:
            logger.warning("⚠️  Model training failed, but system can still run")
        
        logger.info("\n" + "=" * 50)
        logger.info("✅ IDPS System initialization completed!")
        logger.info("\nNext steps:")
        logger.info("1. Start the server: python run_server.py")
        logger.info("2. Start the monitor: python run_monitor.py")
        logger.info("3. Start the dashboard: python run_dashboard.py")
        logger.info("4. Test the system: python -m src.tools.attack_sim")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

def main():
    """Main setup function"""
    if setup_system():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
