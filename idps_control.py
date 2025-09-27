#!/usr/bin/env python3
"""
IDPS Control Script - Master control for all IDPS components
"""
import sys
import os
import subprocess
import time
import signal
from pathlib import Path
from threading import Thread

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.logger import get_logger

logger = get_logger(__name__)

class IDPSController:
    """Controller for managing IDPS components"""
    
    def __init__(self):
        self.processes = {}
        self.project_root = Path(__file__).parent
        
    def start_component(self, component_name, script_name):
        """Start a component in a subprocess"""
        try:
            script_path = self.project_root / script_name
            
            logger.info(f"🚀 Starting {component_name}...")
            
            process = subprocess.Popen([
                sys.executable, str(script_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes[component_name] = process
            logger.info(f"✅ {component_name} started (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {component_name}: {e}")
            return False
    
    def stop_component(self, component_name):
        """Stop a component"""
        if component_name in self.processes:
            process = self.processes[component_name]
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"🛑 {component_name} stopped")
                del self.processes[component_name]
                return True
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⚠️  {component_name} force killed")
                del self.processes[component_name]
                return True
            except Exception as e:
                logger.error(f"❌ Error stopping {component_name}: {e}")
                return False
        else:
            logger.warning(f"⚠️  {component_name} is not running")
            return False
    
    def stop_all(self):
        """Stop all components"""
        logger.info("🛑 Stopping all IDPS components...")
        for component_name in list(self.processes.keys()):
            self.stop_component(component_name)
    
    def status(self):
        """Show status of all components"""
        logger.info("📊 IDPS Component Status:")
        logger.info("-" * 40)
        
        components = ["Server", "Monitor", "Dashboard"]
        
        for component in components:
            if component in self.processes:
                process = self.processes[component]
                if process.poll() is None:
                    logger.info(f"✅ {component}: Running (PID: {process.pid})")
                else:
                    logger.info(f"❌ {component}: Stopped")
                    del self.processes[component]
            else:
                logger.info(f"❌ {component}: Not running")
    
    def start_all(self, delay=2):
        """Start all components with delay between starts"""
        logger.info("🚀 Starting all IDPS components...")
        
        # Start server first
        if self.start_component("Server", "run_server.py"):
            time.sleep(delay)
        
        # Start monitor
        if self.start_component("Monitor", "run_monitor.py"):
            time.sleep(delay)
        
        # Start dashboard
        self.start_component("Dashboard", "run_dashboard.py")
        
        logger.info("\n✅ All components started!")
        logger.info("📋 Access points:")
        logger.info("  🌐 Web Server: http://localhost:5000")
        logger.info("  📊 Dashboard: http://localhost:8501")
        logger.info("\n💡 Use 'Ctrl+C' to stop all components")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        logger.info("🎮 IDPS Interactive Control Mode")
        logger.info("Commands: start, stop, status, restart, quit")
        
        while True:
            try:
                command = input("\nIDPS> ").strip().lower()
                
                if command == "start":
                    self.start_all()
                elif command == "stop":
                    self.stop_all()
                elif command == "status":
                    self.status()
                elif command == "restart":
                    self.stop_all()
                    time.sleep(2)
                    self.start_all()
                elif command in ["quit", "exit", "q"]:
                    self.stop_all()
                    break
                elif command == "help":
                    print("Available commands:")
                    print("  start   - Start all components")
                    print("  stop    - Stop all components")
                    print("  status  - Show component status")
                    print("  restart - Restart all components")
                    print("  quit    - Stop all and exit")
                else:
                    print(f"Unknown command: {command}")
                    
            except KeyboardInterrupt:
                self.stop_all()
                break
            except EOFError:
                self.stop_all()
                break

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global controller
    logger.info("\n🛑 Shutdown signal received")
    controller.stop_all()
    sys.exit(0)

def main():
    """Main function"""
    global controller
    controller = IDPSController()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🔐 IDPS Control Script")
    logger.info("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            controller.start_all()
            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                controller.stop_all()
                
        elif command == "stop":
            controller.stop_all()
            
        elif command == "status":
            controller.status()
            
        elif command == "restart":
            controller.stop_all()
            time.sleep(2)
            controller.start_all()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                controller.stop_all()
                
        elif command == "interactive":
            controller.interactive_mode()
            
        else:
            print("Usage: python idps_control.py [start|stop|status|restart|interactive]")
            return 1
    else:
        # Default to interactive mode
        controller.interactive_mode()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
