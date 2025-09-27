#!/usr/bin/env python3
"""
Dashboard startup script for IDPS
"""
import sys
import os
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import DASHBOARD_HOST, DASHBOARD_PORT
from src.core.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main function to run the dashboard"""
    try:
        logger.info("📊 Starting IDPS Dashboard...")
        logger.info(f"Dashboard will be available at http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
        
        # Run streamlit dashboard
        dashboard_script = project_root / "src" / "dashboard" / "dashboard.py"
        
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(dashboard_script),
            "--server.address", DASHBOARD_HOST,
            "--server.port", str(DASHBOARD_PORT),
            "--server.headless", "true"
        ]
        
        # Start the dashboard
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        logger.info("👋 Dashboard stopped by user")
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
