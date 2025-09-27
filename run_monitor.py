#!/usr/bin/env python3
"""
Monitor startup script for IDPS
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.monitor.ids_monitor import run_monitor
from src.core.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main function to run the monitor"""
    try:
        logger.info("🔍 Starting IDPS Monitor...")
        run_monitor()
    except KeyboardInterrupt:
        logger.info("👋 Monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitor error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
