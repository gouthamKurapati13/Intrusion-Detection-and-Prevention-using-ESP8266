#!/usr/bin/env python3
"""
Server startup script for IDPS
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.server.app import run_server
from src.core.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main function to run the server"""
    try:
        logger.info("🚀 Starting IDPS Web Server...")
        run_server()
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
