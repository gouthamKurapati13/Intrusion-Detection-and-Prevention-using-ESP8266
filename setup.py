#!/usr/bin/env python3
"""
Setup script for IDPS - Initialize the system and start all services
"""
import sys
import os
import subprocess
import time
import threading
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import ensure_directories
from src.core.logger import get_logger
from src.tools.train_model import train_model

logger = get_logger(__name__)

def start_flask_server():
    """Start the Flask server"""
    try:
        logger.info("🚀 Starting Flask Server...")
        from src.server.app import app
        
        def run_flask():
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(2)  # Give server time to start
        logger.info("✅ Flask Server started successfully on http://localhost:5000")
        return flask_thread
    except Exception as e:
        logger.error(f"❌ Failed to start Flask Server: {e}")
        return None

def start_ids_monitor():
    """Start the IDS Monitor"""
    try:
        logger.info("🚀 Starting IDS Monitor...")
        from src.monitor.ids_monitor import main as monitor_main
        
        def run_monitor():
            monitor_main()
        
        monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        monitor_thread.start()
        time.sleep(2)  # Give monitor time to start
        logger.info("✅ IDS Monitor started successfully")
        return monitor_thread
    except Exception as e:
        logger.error(f"❌ Failed to start IDS Monitor: {e}")
        return None

def start_streamlit_dashboard():
    """Start the Streamlit Dashboard"""
    try:
        logger.info("🚀 Starting Streamlit Dashboard...")
        dashboard_path = project_root / "src" / "dashboard" / "dashboard.py"
        
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)  # Give Streamlit time to start
        
        if process.poll() is None:
            logger.info("✅ Streamlit Dashboard started successfully on http://localhost:8501")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Streamlit Dashboard failed to start: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start Streamlit Dashboard: {e}")
        return None

def start_attack_simulator():
    """Start the Attack Simulator UI"""
    try:
        logger.info("🚀 Starting Attack Simulator UI...")
        ui_path = project_root / "src" / "tools" / "attack_simulator_ui.py"
        
        if not ui_path.exists():
            logger.error(f"❌ Attack simulator UI not found at: {ui_path}")
            return None
        
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            str(ui_path),
            "--server.port", "8502",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)  # Give Streamlit time to start
        
        if process.poll() is None:
            logger.info("✅ Attack Simulator UI started successfully on http://localhost:8502")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Attack Simulator UI failed to start: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start Attack Simulator UI: {e}")
        return None

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
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

def start_all_services():
    """Start all IDPS services"""
    logger.info("\n🚀 Starting all IDPS services...")
    logger.info("=" * 50)
    
    services = []
    threads = []
    processes = []
    
    # Start Flask server
    flask_thread = start_flask_server()
    if flask_thread:
        services.append("Flask Server")
        threads.append(flask_thread)
    
    # Start IDS Monitor
    monitor_thread = start_ids_monitor()
    if monitor_thread:
        services.append("IDS Monitor")
        threads.append(monitor_thread)
    
    # Start Streamlit Dashboard
    dashboard_process = start_streamlit_dashboard()
    if dashboard_process:
        services.append("Streamlit Dashboard")
        processes.append(("Streamlit Dashboard", dashboard_process))
    
    # Start Attack Simulator UI
    simulator_process = start_attack_simulator()
    if simulator_process:
        services.append("Attack Simulator UI")
        processes.append(("Attack Simulator UI", simulator_process))
    
    if services:
        logger.info("\n" + "=" * 50)
        logger.info("🎉 All services started successfully!")
        logger.info("\n📍 Access Points:")
        logger.info("• 🌐 Web Server (Login Test): http://localhost:5000")
        logger.info("• 📊 IDPS Dashboard: http://localhost:8501")
        logger.info("• 🧪 Attack Simulator: http://localhost:8502")
        logger.info("\n🧪 Additional Testing:")
        logger.info("• Command Line Attack: python -m src.tools.attack_sim")
        logger.info("\n⚠️  Note: All services are running. Press Ctrl+C to stop everything.")
        
        try:
            # Keep the main process alive to manage services
            logger.info("\n🔄 All services running... (Press Ctrl+C to stop all)")
            while True:
                time.sleep(10)
                # Check if processes are still running
                for service_name, process in processes[:]:
                    if process.poll() is not None:
                        logger.warning(f"⚠️  {service_name} has stopped unexpectedly")
                        processes.remove((service_name, process))
                        
                if not processes:
                    logger.error("❌ All Streamlit services have stopped")
                    break
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping all services...")
            
            # Stop processes
            for service_name, process in processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info(f"✅ {service_name} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.info(f"🔪 {service_name} force killed")
                except Exception as e:
                    logger.error(f"❌ Error stopping {service_name}: {e}")
            
            # Threads will stop automatically when main process exits
            logger.info("✅ All services stopped")
    else:
        logger.error("❌ No services could be started")
        return False
    
    return True

def main():
    """Main setup function"""
    # First initialize the system
    if not setup_system():
        return 1
    
    # Ask user if they want to start services
    logger.info("\n" + "=" * 50)
    try:
        response = input("🤔 Do you want to start all services now? (y/n): ").lower().strip()
        if response in ['y', 'yes', '']:
            if start_all_services():
                return 0
            else:
                return 1
        else:
            logger.info("✅ Setup completed. You can start services later using:")
            logger.info("   python idps_control.py start")
            return 0
    except KeyboardInterrupt:
        logger.info("\n✅ Setup completed without starting services")
        return 0

if __name__ == "__main__":
    sys.exit(main())
