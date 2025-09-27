"""
Streamlit Dashboard for IDPS - Real-time monitoring and management interface
"""
import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from config.settings import LOGIN_ATTEMPTS_LOG, AUDIT_LOGS_DIR
from src.core.ip_manager import ip_manager
from src.core.ml_model import intrusion_model
from src.core.logger import get_logger

# Configure page
st.set_page_config(
    page_title="IDPS Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = get_logger(__name__)

# Initialize session state for monitor control
if 'monitor_enabled' not in st.session_state:
    st.session_state.monitor_enabled = False
if 'monitor_process' not in st.session_state:
    st.session_state.monitor_process = None
if 'monitor_thread' not in st.session_state:
    st.session_state.monitor_thread = None

# Import for monitor control
import subprocess
import threading
import signal
from src.monitor.ids_monitor import IDSMonitor

# Enhanced Custom CSS for better styling
st.markdown("""
<style>
    /* Main styling improvements */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Custom metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    /* Enhanced alert boxes */
    .alert-box {
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .alert-danger {
        background: linear-gradient(135deg, #ff6b6b, #ffa8a8);
        border-left-color: #ff5252;
        color: #721c24;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #51cf66, #8ce99a);
        border-left-color: #40c057;
        color: #155724;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ffd43b, #fff3bf);
        border-left-color: #fab005;
        color: #856404;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #339af0, #74c0fc);
        border-left-color: #228be6;
        color: #0c5460;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Status indicators */
    .status-good {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* IP address styling */
    .ip-address {
        font-family: 'Courier New', monospace;
        background-color: #f8f9fa;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    
    /* Table improvements */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Enhanced table styling for login attempts */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        border: none;
    }
    
    .stDataFrame > div {
        border-radius: 15px;
    }
    
    /* Custom metrics styling */
    .metric-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .metric-high-risk {
        border-left-color: #dc3545;
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
    }
    
    .metric-medium-risk {
        border-left-color: #ffc107;
        background: linear-gradient(135deg, #fffbf0 0%, #fef3c7 100%);
    }
    
    .metric-low-risk {
        border-left-color: #28a745;
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
    }
    
    /* Pagination styling */
    .pagination-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Enhanced filter section */
    .filter-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #dee2e6;
    }
    
    /* Action buttons styling */
    .action-button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    }
    
    .action-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
    }
    
    .danger-button {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
    }
    
    .danger-button:hover {
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Chart container styling */
    .plotly-chart {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    /* Sidebar navigation */
    .nav-item {
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    
    .nav-item:hover {
        background-color: rgba(255,255,255,0.1);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Footer styling */
    .footer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def load_login_attempts():
    """Load login attempts from CSV file"""
    try:
        if LOGIN_ATTEMPTS_LOG.exists():
            df = pd.read_csv(
                LOGIN_ATTEMPTS_LOG, 
                header=None, 
                names=["IP", "Username", "Password", "Timestamp"]
            )
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            return df
        else:
            return pd.DataFrame(columns=["IP", "Username", "Password", "Timestamp"])
    except Exception as e:
        st.error(f"Error loading login attempts: {e}")
        return pd.DataFrame(columns=["IP", "Username", "Password", "Timestamp"])

def load_audit_logs():
    """Load audit logs for all IPs"""
    audit_data = []
    try:
        if AUDIT_LOGS_DIR.exists():
            for file_path in AUDIT_LOGS_DIR.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        ip_logs = json.load(f)
                        audit_data.extend(ip_logs)
                except Exception as e:
                    logger.error(f"Error loading audit file {file_path}: {e}")
        return audit_data
    except Exception as e:
        st.error(f"Error loading audit logs: {e}")
        return []

def start_monitor():
    """Start the IDS monitor in a separate thread"""
    try:
        if st.session_state.monitor_thread and st.session_state.monitor_thread.is_alive():
            return False, "Monitor is already running"
        
        # Create and start monitor thread
        monitor = IDSMonitor()
        
        def run_monitor_thread():
            try:
                st.session_state.monitor_enabled = True
                logger.info("🔍 Monitor started from dashboard")
                while st.session_state.monitor_enabled:
                    monitor.process_new_attempts()
                    time.sleep(5)  # Check every 5 seconds
                logger.info("🛑 Monitor stopped from dashboard")
            except Exception as e:
                logger.error(f"Monitor thread error: {e}")
                st.session_state.monitor_enabled = False
        
        thread = threading.Thread(target=run_monitor_thread, daemon=True)
        thread.start()
        st.session_state.monitor_thread = thread
        st.session_state.monitor_enabled = True
        
        return True, "Monitor started successfully"
        
    except Exception as e:
        logger.error(f"Error starting monitor: {e}")
        return False, f"Failed to start monitor: {str(e)}"

def stop_monitor():
    """Stop the IDS monitor"""
    try:
        st.session_state.monitor_enabled = False
        
        # Wait a moment for the thread to stop
        if st.session_state.monitor_thread:
            # Give the thread time to stop gracefully
            time.sleep(1)
        
        st.session_state.monitor_thread = None
        logger.info("🛑 Monitor stopped from dashboard")
        return True, "Monitor stopped successfully"
        
    except Exception as e:
        logger.error(f"Error stopping monitor: {e}")
        return False, f"Failed to stop monitor: {str(e)}"

def get_monitor_status():
    """Get current monitor status"""
    try:
        is_running = (st.session_state.monitor_enabled and 
                     st.session_state.monitor_thread and 
                     st.session_state.monitor_thread.is_alive())
        
        status = {
            "running": is_running,
            "enabled": st.session_state.monitor_enabled,
            "thread_alive": st.session_state.monitor_thread.is_alive() if st.session_state.monitor_thread else False
        }
        
        return status
    except Exception as e:
        logger.error(f"Error getting monitor status: {e}")
        return {"running": False, "enabled": False, "thread_alive": False}

def display_system_overview():
    """Display enhanced system overview metrics with real-time data"""
    # Custom header with gradient background
    st.markdown("""
    <div class="dashboard-header">
        <h1>🔐 IDPS System Dashboard</h1>
        <p>Real-time Intrusion Detection & Prevention System Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get system statistics
    blocked_ips = ip_manager.get_blocked_ips()
    blocked_count = len(set(blocked_ips))  # Unique IPs
    
    login_attempts_df = load_login_attempts()
    total_attempts = len(login_attempts_df)
    
    # Calculate various time-based metrics
    now = datetime.now()
    recent_1h = len(login_attempts_df[
        login_attempts_df['Timestamp'] > now - timedelta(hours=1)
    ]) if not login_attempts_df.empty else 0
    
    recent_24h = len(login_attempts_df[
        login_attempts_df['Timestamp'] > now - timedelta(hours=24)
    ]) if not login_attempts_df.empty else 0
    
    # Calculate previous hour for delta comparison
    prev_hour_attempts = len(login_attempts_df[
        (login_attempts_df['Timestamp'] > now - timedelta(hours=2)) &
        (login_attempts_df['Timestamp'] <= now - timedelta(hours=1))
    ]) if not login_attempts_df.empty else 0
    
    model_info = intrusion_model.model_info()
    
    # Enhanced metrics display
    st.subheader("📊 System Health Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_blocked = blocked_count if blocked_count > 0 else None
        st.metric(
            label="🚫 Blocked IPs",
            value=blocked_count,
            delta=delta_blocked,
            delta_color="inverse"
        )
        
        # Status indicator
        if blocked_count == 0:
            st.markdown('<p class="status-good">🟢 No threats detected</p>', unsafe_allow_html=True)
        elif blocked_count < 5:
            st.markdown('<p class="status-warning">🟡 Low threat level</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-danger">🔴 High threat activity</p>', unsafe_allow_html=True)
    
    with col2:
        st.metric(
            label="📊 Total Login Attempts",
            value=f"{total_attempts:,}",
            delta=f"+{recent_24h} (24h)" if recent_24h > 0 else None
        )
        
        if total_attempts == 0:
            st.markdown('<p class="status-good">🟢 No activity</p>', unsafe_allow_html=True)
        elif total_attempts < 100:
            st.markdown('<p class="status-good">🟢 Normal activity</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-warning">🟡 High activity</p>', unsafe_allow_html=True)
    
    with col3:
        delta_recent = recent_1h - prev_hour_attempts if prev_hour_attempts > 0 else None
        st.metric(
            label="⏰ Recent Activity (1h)",
            value=recent_1h,
            delta=delta_recent,
            delta_color="inverse"
        )
        
        if recent_1h == 0:
            st.markdown('<p class="status-good">🟢 Quiet</p>', unsafe_allow_html=True)
        elif recent_1h < 10:
            st.markdown('<p class="status-warning">🟡 Active</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-danger">🔴 Under attack</p>', unsafe_allow_html=True)
    
    with col4:
        model_status = "Trained" if model_info["status"] == "Trained" else "Not Trained"
        model_emoji = "✅" if model_info["status"] == "Trained" else "❌"
        
        st.metric(
            label="🧠 ML Model Status",
            value=f"{model_emoji} {model_status}",
            delta=None
        )
    
    # Real-time threat level assessment
    st.subheader("🚨 Threat Level Assessment")
    threat_level = calculate_threat_level(blocked_count, recent_1h, total_attempts)
    display_threat_level(threat_level)
    
    # Quick stats in expandable section
    with st.expander("📈 Detailed Statistics", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Attack Patterns**")
            if not login_attempts_df.empty:
                unique_ips = login_attempts_df['IP'].nunique()
                unique_users = login_attempts_df['Username'].nunique()
                st.write(f"• Unique IPs: {unique_ips}")
                st.write(f"• Unique Usernames: {unique_users}")
                st.write(f"• Avg attempts per IP: {total_attempts/unique_ips:.1f}" if unique_ips > 0 else "• No data")
        
        with col2:
            st.markdown("**Time Analysis**")
            st.write(f"• Last hour: {recent_1h} attempts")
            st.write(f"• Last 24h: {recent_24h} attempts")
            if not login_attempts_df.empty:
                last_attempt = login_attempts_df['Timestamp'].max()
                time_since = now - last_attempt
                if time_since.total_seconds() < 3600:
                    st.write(f"• Last attempt: {int(time_since.total_seconds()/60)} min ago")
                else:
                    st.write(f"• Last attempt: {int(time_since.total_seconds()/3600)} hours ago")
        
        with col3:
            st.markdown("**System Status**")
            st.write(f"• Blocked IPs: {blocked_count}")
            st.write(f"• Model Status: {model_info['status']}")
            st.write(f"• Dashboard Uptime: Active")

def calculate_threat_level(blocked_count, recent_attempts, total_attempts):
    """Calculate current threat level based on metrics"""
    score = 0
    
    # Factor in blocked IPs
    if blocked_count >= 10:
        score += 3
    elif blocked_count >= 5:
        score += 2
    elif blocked_count > 0:
        score += 1
    
    # Factor in recent activity
    if recent_attempts >= 20:
        score += 3
    elif recent_attempts >= 10:
        score += 2
    elif recent_attempts > 0:
        score += 1
    
    # Factor in total activity
    if total_attempts >= 1000:
        score += 2
    elif total_attempts >= 500:
        score += 1
    
    return min(score, 5)  # Cap at 5

def display_sidebar_monitor_controls():
    """Display compact monitor control interface for sidebar"""
    # Get current monitor status
    monitor_status = get_monitor_status()
    is_running = monitor_status["running"]
    
    # Compact status display
    if is_running:
        st.markdown("""
        <div style="background: rgba(40, 167, 69, 0.2); color: #28a745; padding: 0.5rem; 
                    border-radius: 6px; text-align: center; margin-bottom: 0.5rem; font-size: 0.9rem;">
            🟢 <strong>Monitor Active</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255, 193, 7, 0.2); color: #ffc107; padding: 0.5rem; 
                    border-radius: 6px; text-align: center; margin-bottom: 0.5rem; font-size: 0.9rem;">
            🟡 <strong>Monitor Stopped</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Start", disabled=is_running, use_container_width=True, key="sidebar_start_monitor"):
            success, message = start_monitor()
            if success:
                st.success("✅ Started")
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    with col2:
        if st.button("🛑 Stop", disabled=not is_running, use_container_width=True, key="sidebar_stop_monitor"):
            success, message = stop_monitor()
            if success:
                st.success("✅ Stopped")
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    # Compact statistics display
    if is_running:
        try:
            login_df = load_login_attempts()
            total_processed = len(login_df)
            blocked_ips = len(set(ip_manager.get_blocked_ips()))
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 6px; padding: 0.5rem; margin-top: 0.5rem;">
                <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem; line-height: 1.3;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                        <span>Processed:</span>
                        <span style="font-weight: 600;">{total_processed}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Blocked:</span>
                        <span style="font-weight: 600;">{blocked_ips}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.caption(f"⚠️ Stats unavailable: {str(e)[:30]}...")

def display_monitor_controls():
    """Display monitor control interface (legacy - kept for compatibility)"""
    st.info("Monitor controls have been moved to the sidebar for better accessibility.")
    
    # Get current monitor status for display
    monitor_status = get_monitor_status()
    is_running = monitor_status["running"]
    
    if is_running:
        st.success("🟢 Monitor is currently running - use sidebar controls to manage")
    else:
        st.warning("🟡 Monitor is currently stopped - use sidebar controls to manage")

def display_threat_level(level):
    """Display threat level with visual indicators"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if level == 0:
            st.markdown("""
            <div class="alert-box alert-success">
                <h3 style="margin:0;">🟢 LOW</h3>
                <p style="margin:0;">Threat Level: {}/5</p>
            </div>
            """.format(level), unsafe_allow_html=True)
        elif level <= 2:
            st.markdown("""
            <div class="alert-box alert-warning">
                <h3 style="margin:0;">🟡 MEDIUM</h3>
                <p style="margin:0;">Threat Level: {}/5</p>
            </div>
            """.format(level), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-box alert-danger">
                <h3 style="margin:0;">🔴 HIGH</h3>
                <p style="margin:0;">Threat Level: {}/5</p>
            </div>
            """.format(level), unsafe_allow_html=True)
    
    with col2:
        # Visual threat level bar
        progress_html = f"""
        <div style="background-color: #f0f0f0; border-radius: 10px; height: 30px; margin-top: 10px;">
            <div style="background: {'linear-gradient(90deg, #51cf66, #8ce99a)' if level <= 1 else 'linear-gradient(90deg, #ffd43b, #fff3bf)' if level <= 3 else 'linear-gradient(90deg, #ff6b6b, #ffa8a8)'}; 
                        height: 100%; width: {level * 20}%; border-radius: 10px; 
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {level}/5
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        # Threat description
        descriptions = [
            "System is secure with no active threats detected.",
            "Minimal threat activity. System is operating normally.",
            "Low level threat activity detected. Monitoring continues.",
            "Moderate threat activity. Enhanced monitoring recommended.",
            "Significant threat activity detected. Review security measures.",
            "High threat level! Immediate attention required."
        ]
        st.write(descriptions[level])

def display_recent_attempts():
    """Display recent login attempts with highly enhanced UI and visualization"""
    st.header("� Login Attempts Monitor")
    
    df = load_login_attempts()
    
    if df.empty:
        st.markdown("""
        <div class="alert-box alert-info">
            <h4>📭 No Data Available</h4>
            <p>No login attempts have been recorded yet. The system is ready to monitor incoming attempts.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Advanced filter section with better UI
    with st.expander("🔍 Advanced Filters & Settings", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            hours_back = st.selectbox(
                "⏰ Time Range:", 
                [1, 6, 12, 24, 72, 168], 
                index=3,
                format_func=lambda x: f"Last {x}h" if x < 24 else f"Last {x//24}d"
            )
        
        with col2:
            ip_filter = st.text_input("🌐 Filter by IP:", placeholder="192.168.1.100")
        
        with col3:
            username_filter = st.text_input("👤 Username:", placeholder="admin")
        
        with col4:
            risk_filter = st.selectbox("⚠️ Risk Level:", ["All", "High", "Medium", "Low"])
        
        with col5:
            show_blocked_only = st.checkbox("🚫 Blocked Only")
        
        # Add refresh controls
        st.markdown("---")
        col_refresh1, col_refresh2, col_refresh3 = st.columns(3)
        
        with col_refresh1:
            if st.button("🔄 Refresh Now", use_container_width=True):
                st.rerun()
        
        with col_refresh2:
            auto_refresh = st.checkbox("🔄 Auto-refresh (30s)")
        
        with col_refresh3:
            if st.button("📊 View Analytics", use_container_width=True):
                st.switch_page("Analytics") if hasattr(st, 'switch_page') else None
        
        if auto_refresh:
            st.info("⏳ Auto-refresh enabled - page will refresh in 30 seconds")
            time.sleep(30)
            st.rerun()
    
    # Apply filters
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    filtered_df = df[df['Timestamp'] > cutoff_time].copy()
    
    if ip_filter:
        filtered_df = filtered_df[filtered_df['IP'].str.contains(ip_filter, case=False, na=False)]
    
    if username_filter:
        filtered_df = filtered_df[filtered_df['Username'].str.contains(username_filter, case=False, na=False)]
    
    # Add enhanced columns with better logic
    filtered_df['Blocked'] = filtered_df['IP'].apply(lambda x: ip_manager.is_ip_blocked(x))
    filtered_df['Risk Level'] = filtered_df.apply(assess_attempt_risk, axis=1)
    filtered_df['Country'] = filtered_df['IP'].apply(get_country_from_ip)
    filtered_df['Attempts_Per_IP'] = filtered_df.groupby('IP')['IP'].transform('count')
    
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['Risk Level'] == risk_filter]
    
    if show_blocked_only:
        filtered_df = filtered_df[filtered_df['Blocked'] == True]
    
    # Sort by timestamp (most recent first)
    filtered_df = filtered_df.sort_values('Timestamp', ascending=False)
    
    if not filtered_df.empty:
        # Enhanced summary statistics with visual indicators
        st.subheader("📊 Attack Overview")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        unique_ips = filtered_df['IP'].nunique()
        unique_users = filtered_df['Username'].nunique()
        blocked_ips = filtered_df[filtered_df['Blocked'] == True]['IP'].nunique()
        high_risk = len(filtered_df[filtered_df['Risk Level'] == 'High'])
        medium_risk = len(filtered_df[filtered_df['Risk Level'] == 'Medium'])
        total_attempts = len(filtered_df)
        
        with col1:
            st.metric("🎯 Total Attempts", f"{total_attempts:,}")
        with col2:
            st.metric("🌐 Unique IPs", unique_ips)
        with col3:
            st.metric("👤 Unique Users", unique_users)
        with col4:
            st.metric("🚫 Blocked IPs", blocked_ips, delta_color="inverse")
        with col5:
            st.metric("🔴 High Risk", high_risk, delta_color="inverse")
        with col6:
            st.metric("🟡 Medium Risk", medium_risk, delta_color="inverse")
        
        # Real-time threat assessment
        threat_score = calculate_login_threat_score(filtered_df)
        col1, col2 = st.columns([2, 3])
        
        with col1:
            if threat_score >= 8:
                st.markdown("""
                <div class="alert-box alert-danger">
                    <h4>🚨 CRITICAL THREAT DETECTED</h4>
                    <p><strong>Threat Score: {}/10</strong><br>
                    Immediate action required! Multiple high-risk login attempts detected.</p>
                </div>
                """.format(threat_score), unsafe_allow_html=True)
            elif threat_score >= 5:
                st.markdown("""
                <div class="alert-box alert-warning">
                    <h4>⚠️ ELEVATED THREAT LEVEL</h4>
                    <p><strong>Threat Score: {}/10</strong><br>
                    Increased monitoring recommended.</p>
                </div>
                """.format(threat_score), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-box alert-success">
                    <h4>✅ NORMAL ACTIVITY</h4>
                    <p><strong>Threat Score: {}/10</strong><br>
                    System operating within normal parameters.</p>
                </div>
                """.format(threat_score), unsafe_allow_html=True)
        
        with col2:
            # Quick action buttons
            st.markdown("**🛠️ Quick Actions**")
            col2a, col2b, col2c = st.columns(3)
            
            with col2a:
                if st.button("🚫 Block All High Risk IPs", type="secondary"):
                    high_risk_ips = filtered_df[filtered_df['Risk Level'] == 'High']['IP'].unique()
                    for ip in high_risk_ips:
                        if not ip_manager.is_ip_blocked(ip):
                            ip_manager.block_ip(ip)
                    st.success(f"Blocked {len(high_risk_ips)} high-risk IPs!")
                    st.rerun()
            
            with col2b:
                if st.button("📊 Generate Report", type="secondary"):
                    report_data = generate_login_report(filtered_df)
                    st.download_button(
                        label="📥 Download Report",
                        data=report_data,
                        file_name=f"login_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            
            with col2c:
                if st.button("🔄 Refresh Data", type="secondary"):
                    st.rerun()
        
        # Enhanced table display with modern UI
        st.subheader("🔍 Detailed Login Attempts")
        
        # Create enhanced display dataframe
        display_df = create_enhanced_login_display(filtered_df)
        
        # Pagination for large datasets
        items_per_page = st.selectbox("Items per page:", [10, 25, 50, 100], index=1)
        total_pages = max(1, (len(display_df) - 1) // items_per_page + 1)
        
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                current_page = st.selectbox(
                    f"Page (1-{total_pages}):",
                    range(1, total_pages + 1),
                    format_func=lambda x: f"Page {x} of {total_pages}"
                )
        else:
            current_page = 1
        
        # Calculate page boundaries
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(display_df))
        page_df = display_df.iloc[start_idx:end_idx]
        
        # Enhanced dataframe display with custom styling
        display_styled_login_dataframe(page_df)
        
        # Enhanced pagination info with statistics
        blocked_on_page = len(page_df[page_df['Status'].str.contains('BLOCKED', na=False)])
        high_risk_on_page = len(page_df[page_df['Risk'].str.contains('HIGH', na=False)])
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    color: white; padding: 1rem; border-radius: 12px; margin: 1rem 0; text-align: center;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); border: 1px solid #4a5568;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div><strong>📄 Page {current_page} of {total_pages}</strong></div>
                <div><strong>📊 Showing {start_idx + 1}-{end_idx} of {len(display_df)} entries</strong></div>
                <div><strong><span style="color: #ff5252;">🚫 {blocked_on_page} Blocked</span> | <span style="color: #ffab40;">🔴 {high_risk_on_page} High Risk</span></strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Export options
        col1, col2, col3 = st.columns(3)
        with col1:
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📊 Export CSV",
                data=csv_data,
                file_name=f"login_attempts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data = filtered_df.to_json(orient='records', date_format='iso')
            st.download_button(
                label="� Export JSON",
                data=json_data,
                file_name=f"login_attempts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔍 Detailed Analysis", use_container_width=True):
                st.switch_page("Analytics")
        
    else:
        st.markdown("""
        <div class="alert-box alert-warning">
            <h4>🔍 No Results Found</h4>
            <p>No login attempts match your current filter criteria. Try adjusting the filters above.</p>
        </div>
        """, unsafe_allow_html=True)

def assess_attempt_risk(row):
    """Assess the risk level of a login attempt"""
    risk_score = 0
    
    # Check for common attack patterns
    username = row['Username'].lower()
    password = row['Password']
    
    # High-risk usernames
    high_risk_users = ['admin', 'administrator', 'root', 'user', 'test', 'guest']
    if username in high_risk_users:
        risk_score += 2
    
    # Common passwords
    common_passwords = ['password', '123456', 'admin', 'root', '1234', 'qwerty']
    if password.lower() in common_passwords:
        risk_score += 2
    
    # Short passwords
    if len(password) < 6:
        risk_score += 1
    
    # Blocked IP adds risk
    if row['Blocked'] if 'Blocked' in row else False:
        risk_score += 3
    
    if risk_score >= 4:
        return 'High'
    elif risk_score >= 2:
        return 'Medium'
    else:
        return 'Low'

def get_country_from_ip(ip):
    """Get country from IP address (placeholder function)"""
    # This is a placeholder - in a real implementation, you'd use a GeoIP service
    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
        return '🏠 Private'
    elif ip.startswith('127.'):
        return '🖥️ Localhost'
    else:
        return '🌍 Unknown'  # Would be replaced with actual country lookup

def calculate_login_threat_score(df):
    """Calculate threat score based on login attempts data"""
    if df.empty:
        return 0
    
    score = 0
    
    # High frequency attacks
    attempts_per_hour = len(df) / max(1, (df['Timestamp'].max() - df['Timestamp'].min()).total_seconds() / 3600)
    if attempts_per_hour > 50:
        score += 4
    elif attempts_per_hour > 20:
        score += 3
    elif attempts_per_hour > 10:
        score += 2
    elif attempts_per_hour > 5:
        score += 1
    
    # Multiple IPs
    unique_ips = df['IP'].nunique()
    if unique_ips > 10:
        score += 3
    elif unique_ips > 5:
        score += 2
    elif unique_ips > 2:
        score += 1
    
    # High risk attempts
    high_risk_count = len(df[df['Risk Level'] == 'High'])
    if high_risk_count > 20:
        score += 3
    elif high_risk_count > 10:
        score += 2
    elif high_risk_count > 0:
        score += 1
    
    return min(score, 10)

def create_enhanced_login_display(df):
    """Create enhanced display DataFrame with better formatting"""
    display_df = df.copy()
    
    # Format timestamp for better readability
    display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%m/%d %H:%M:%S')
    
    # Enhanced status with icons and colors
    display_df['Status'] = display_df.apply(lambda row: 
        '🚫 BLOCKED' if row['Blocked'] 
        else '⚠️ SUSPICIOUS' if row['Risk Level'] == 'High'
        else '⚡ ACTIVE', axis=1)
    
    # Risk level with icons
    risk_icons = {'High': '🔴 HIGH', 'Medium': '🟡 MED', 'Low': '🟢 LOW'}
    display_df['Risk'] = display_df['Risk Level'].map(risk_icons)
    
    # Format IP with styling hints
    display_df['IP_Display'] = display_df['IP']
    
    # Add frequency indicator
    display_df['Freq'] = display_df['Attempts_Per_IP'].apply(lambda x: 
        f'🔥 {x}x' if x > 10 
        else f'⚡ {x}x' if x > 5 
        else f'• {x}x')
    
    # Select and reorder columns
    return display_df[['Timestamp', 'IP_Display', 'Username', 'Status', 'Risk', 'Freq', 'Country']]

def display_styled_login_dataframe(df):
    """Display login attempts using Streamlit's native dataframe with enhanced styling"""
    if df.empty:
        return
    
    # Create a clean dataframe for display
    display_df = df.copy()
    
    # Rename columns for better display
    display_df = display_df.rename(columns={
        'Timestamp': '⏰ Time',
        'IP_Display': '🌐 IP Address', 
        'Username': '👤 Username',
        'Status': '📊 Status',
        'Risk': '⚠️ Risk Level',
        'Freq': '🔥 Frequency',
        'Country': '🌍 Location'
    })
    
    # Apply conditional formatting using Streamlit's styling
    def highlight_rows(row):
        """Apply row-level styling based on risk and status with dark theme"""
        styles = [''] * len(row)
        
        # Dark color coding based on status and risk
        if '🚫 BLOCKED' in str(row['📊 Status']):
            # Dark red background for blocked
            styles = ['background-color: #2d1b1b; color: #ffcdd2; border-left: 4px solid #f44336;'] * len(row)
        elif '🔴 HIGH' in str(row['⚠️ Risk Level']):
            # Dark orange background for high risk
            styles = ['background-color: #2d2416; color: #ffe0b2; border-left: 4px solid #ff9800;'] * len(row)
        elif '⚠️ SUSPICIOUS' in str(row['📊 Status']):
            # Dark yellow background for suspicious
            styles = ['background-color: #2d2a14; color: #fff3c4; border-left: 3px solid #ffc107;'] * len(row)
        else:
            # Dark blue background for normal
            styles = ['background-color: #1a1d2e; color: #e3f2fd; border-left: 2px solid #667eea;'] * len(row)
        
        return styles
    
    def style_cells(val, column_name):
        """Apply cell-level styling based on content with dark theme"""
        if column_name == '🌐 IP Address':
            return 'font-family: monospace; font-weight: bold; color: #64b5f6; background-color: #1e2a47; padding: 4px 8px; border-radius: 4px;'
        elif column_name == '👤 Username':
            return 'font-weight: bold; color: #e0e0e0; background-color: #2a2a2a; padding: 2px 6px; border-radius: 3px;'
        elif column_name == '📊 Status':
            if '🚫 BLOCKED' in str(val):
                return 'color: #ffffff; font-weight: bold; background-color: #c62828; padding: 2px 6px; border-radius: 12px; font-size: 0.9em;'
            elif '⚠️ SUSPICIOUS' in str(val):
                return 'color: #ffffff; font-weight: bold; background-color: #ef6c00; padding: 2px 6px; border-radius: 12px; font-size: 0.9em;'
            else:
                return 'color: #ffffff; font-weight: bold; background-color: #2e7d32; padding: 2px 6px; border-radius: 12px; font-size: 0.9em;'
        elif column_name == '⚠️ Risk Level':
            if '🔴 HIGH' in str(val):
                return 'color: #ffffff; font-weight: bold; background-color: #c62828; padding: 2px 5px; border-radius: 8px; font-size: 0.85em;'
            elif '🟡 MED' in str(val):
                return 'color: #ffffff; font-weight: bold; background-color: #ef6c00; padding: 2px 5px; border-radius: 8px; font-size: 0.85em;'
            else:
                return 'color: #ffffff; font-weight: bold; background-color: #2e7d32; padding: 2px 5px; border-radius: 8px; font-size: 0.85em;'
        elif column_name == '🔥 Frequency':
            if '🔥' in str(val):
                return 'color: #ff5252; font-weight: bold; font-size: 1.1em;'
            elif '⚡' in str(val):
                return 'color: #ffab40; font-weight: bold; font-size: 1.05em;'
            else:
                return 'color: #bdbdbd; font-size: 0.95em;'
        elif column_name == '⏰ Time':
            return 'font-family: monospace; color: #b0bec5; font-size: 0.9em;'
        elif column_name == '🌍 Location':
            return 'color: #81c784; font-size: 0.9em;'
        
        return ''
    
    # Enhanced table display with dark theme
    st.markdown("""
    <style>
    .stDataFrame {
        border: 2px solid #667eea;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        background-color: #1a1a1a;
    }
    
    .stDataFrame > div {
        border-radius: 15px;
        background-color: #1a1a1a;
    }
    
    .stDataFrame table {
        font-size: 14px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    .stDataFrame thead {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
        color: white !important;
    }
    
    .stDataFrame thead th {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 15px 12px !important;
        border-bottom: 2px solid #4a5568 !important;
    }
    
    .stDataFrame tbody tr {
        background-color: #2a2a2a !important;
        color: #e0e0e0 !important;
        border-bottom: 1px solid #404040 !important;
    }
    
    .stDataFrame tbody tr:hover {
        background-color: #3a3a3a !important;
        transform: scale(1.002);
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #252525 !important;
    }
    
    .stDataFrame tbody td {
        background-color: inherit !important;
        color: inherit !important;
        padding: 12px 8px !important;
    }
    
    /* Dark theme scrollbar */
    .stDataFrame ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    .stDataFrame ::-webkit-scrollbar-track {
        background: #2a2a2a;
        border-radius: 4px;
    }
    
    .stDataFrame ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    .stDataFrame ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the styled dataframe
    styled_df = display_df.style.apply(highlight_rows, axis=1)
    
    # Apply cell-level styling
    for col in display_df.columns:
        styled_df = styled_df.applymap(lambda x: style_cells(x, col), subset=[col])
    
    # Format the dataframe with enhanced options
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=min(600, len(display_df) * 45 + 100)  # Dynamic height based on rows
    )
    
    # Add dark theme summary info below the table
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%); 
                color: #e0e0e0; padding: 12px 20px; border-radius: 10px; margin-top: 10px; 
                border-left: 4px solid #667eea; font-size: 14px; 
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);">
        <strong>📊 Table Summary:</strong> Showing {len(display_df)} login attempts | 
        <span style="color: #ff5252; font-weight: bold;">🔴 High Risk: {len(display_df[display_df['⚠️ Risk Level'].str.contains('HIGH', na=False)])}</span> | 
        <span style="color: #ffab40; font-weight: bold;">🟡 Medium Risk: {len(display_df[display_df['⚠️ Risk Level'].str.contains('MED', na=False)])}</span> | 
        <span style="color: #69f0ae; font-weight: bold;">🟢 Low Risk: {len(display_df[display_df['⚠️ Risk Level'].str.contains('LOW', na=False)])}</span>
    </div>
    """, unsafe_allow_html=True)

def generate_login_report(df):
    """Generate a comprehensive login security report"""
    report = f"""
INTRUSION DETECTION SYSTEM - LOGIN SECURITY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================

EXECUTIVE SUMMARY
-----------------
Total Login Attempts: {len(df):,}
Unique IP Addresses: {df['IP'].nunique()}
Unique Usernames: {df['Username'].nunique()}
High Risk Attempts: {len(df[df['Risk Level'] == 'High'])}
Blocked IPs: {len(df[df['Blocked'] == True])}

THREAT ASSESSMENT
-----------------
Threat Score: {calculate_login_threat_score(df)}/10
"""
    
    if not df.empty:
        # Top attacking IPs
        report += "\nTOP ATTACKING IPs\n" + "-" * 20 + "\n"
        top_ips = df['IP'].value_counts().head(10)
        for i, (ip, count) in enumerate(top_ips.items(), 1):
            blocked_status = "BLOCKED" if ip_manager.is_ip_blocked(ip) else "ACTIVE"
            report += f"{i:2}. {ip:<15} | {count:>3} attempts | {blocked_status}\n"
        
        # Most targeted usernames
        report += "\nMOST TARGETED USERNAMES\n" + "-" * 25 + "\n"
        top_users = df['Username'].value_counts().head(10)
        for i, (user, count) in enumerate(top_users.items(), 1):
            report += f"{i:2}. {user:<15} | {count:>3} attempts\n"
        
        # Time analysis
        report += "\nTIME ANALYSIS\n" + "-" * 15 + "\n"
        if len(df) > 0:
            first_attempt = df['Timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')
            last_attempt = df['Timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
            duration = df['Timestamp'].max() - df['Timestamp'].min()
            report += f"First Attempt: {first_attempt}\n"
            report += f"Last Attempt:  {last_attempt}\n"
            report += f"Attack Duration: {duration}\n"
            report += f"Average Rate: {len(df) / max(1, duration.total_seconds() / 3600):.1f} attempts/hour\n"
    
    report += """
RECOMMENDATIONS
---------------
1. Monitor blocked IPs for persistent attack patterns
2. Implement rate limiting for high-frequency sources  
3. Consider geographic blocking for suspicious regions
4. Review and strengthen password policies
5. Enable multi-factor authentication for admin accounts
6. Regular security audit of user accounts

SYSTEM STATUS
-------------
Detection System: ✅ Active
Blocking System: ✅ Active
Real-time Monitoring: ✅ Active
ML Model: """ + ("✅ Trained" if intrusion_model.model_info()['status'] == 'Trained' else "❌ Needs Training") + """

================================================================
Report generated by IDPS Dashboard v2.0
    """
    
    return report

def display_blocked_ips():
    """Display and manage blocked IPs"""
    st.header("⛔ Blocked IP Management")
    
    blocked_ips = ip_manager.get_blocked_ips()
    unique_blocked_ips = list(set(blocked_ips))
    
    if not unique_blocked_ips:
        st.info("No IPs are currently blocked.")
        return
    
    # Display blocked IPs
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Currently Blocked IPs ({len(unique_blocked_ips)})")
        for ip in unique_blocked_ips:
            count = blocked_ips.count(ip)
            st.write(f"🚫 {ip} (blocked {count} times)")
    
    with col2:
        st.subheader("Actions")
        if st.button("🔓 Unblock All IPs", type="primary"):
            if ip_manager.unblock_all_ips():
                st.success("All IPs have been unblocked!")
                st.rerun()
            else:
                st.error("Failed to unblock IPs")
        
        if st.button("🧹 Clean Duplicates"):
            ip_manager.cleanup_duplicates()
            st.success("Cleaned up duplicate entries!")
            st.rerun()

def display_audit_logs():
    """Display audit logs with filtering"""
    st.header("🗂️ Audit Logs")
    
    audit_data = load_audit_logs()
    
    if not audit_data:
        st.info("No audit logs available.")
        return
    
    # Convert to DataFrame for easier handling
    audit_df = pd.DataFrame(audit_data)
    if 'analyzed_at' in audit_df.columns:
        audit_df['analyzed_at'] = pd.to_datetime(audit_df['analyzed_at'])
    
    # IP selector
    unique_ips = sorted(audit_df['ip'].unique()) if 'ip' in audit_df.columns else []
    
    if unique_ips:
        selected_ip = st.selectbox("Select IP to view audit logs:", ["All IPs"] + unique_ips)
        
        if selected_ip != "All IPs":
            filtered_audit = audit_df[audit_df['ip'] == selected_ip]
        else:
            filtered_audit = audit_df
        
        # Display filtered audit logs
        if not filtered_audit.empty:
            # Sort by timestamp
            if 'analyzed_at' in filtered_audit.columns:
                filtered_audit = filtered_audit.sort_values('analyzed_at', ascending=False)
            
            st.dataframe(
                filtered_audit,
                use_container_width=True,
                hide_index=True
            )
            
            # Show summary
            blocked_count = len(filtered_audit[filtered_audit['action'] == 'BLOCKED'])
            total_count = len(filtered_audit)
            st.info(f"Showing {total_count} audit entries ({blocked_count} resulted in blocks)")
        else:
            st.info("No audit logs found for the selected IP.")

def display_analytics():
    """Display enhanced analytics and visualizations with threat intelligence"""
    st.header("📈 Threat Intelligence & Analytics")
    
    try:
        df = load_login_attempts()
        
        if df.empty:
            st.markdown("""
            <div class="alert-box alert-info">
                <h4>📊 No Analytics Data</h4>
                <p>No login attempts available for analysis. Analytics will appear once data is collected.</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Validate required columns
        required_columns = ['IP', 'Username', 'Password', 'Timestamp']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            return
            
    except Exception as e:
        st.error(f"❌ Error loading analytics data: {str(e)}")
        return
    
    # Time period selector
    st.subheader("🕒 Analysis Period")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis_period = st.selectbox(
            "Select time period:",
            ["Last 24 hours", "Last 7 days", "Last 30 days", "All time"],
            index=1
        )
    
    with col2:
        chart_type = st.selectbox(
            "Chart style:",
            ["Modern", "Classic", "Minimal"],
            index=0
        )
    
    with col3:
        show_advanced = st.checkbox("Show advanced metrics", value=True)
    
    # Filter data based on selected period
    now = datetime.now()
    if analysis_period == "Last 24 hours":
        cutoff = now - timedelta(days=1)
    elif analysis_period == "Last 7 days":
        cutoff = now - timedelta(days=7)
    elif analysis_period == "Last 30 days":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = df['Timestamp'].min()
    
    filtered_df = df[df['Timestamp'] >= cutoff].copy()
    
    if filtered_df.empty:
        st.warning(f"No data available for {analysis_period.lower()}")
        return
    
    # Key metrics overview
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_attempts = len(filtered_df)
    unique_ips = filtered_df['IP'].nunique()
    unique_users = filtered_df['Username'].nunique()
    blocked_ips = len([ip for ip in filtered_df['IP'].unique() if ip_manager.is_ip_blocked(ip)])
    avg_attempts_per_ip = total_attempts / unique_ips if unique_ips > 0 else 0
    
    with col1:
        st.metric("Total Attempts", f"{total_attempts:,}")
    with col2:
        st.metric("Unique IPs", unique_ips)
    with col3:
        st.metric("Unique Users", unique_users)
    with col4:
        st.metric("Blocked IPs", blocked_ips, delta_color="inverse")
    with col5:
        st.metric("Avg/IP", f"{avg_attempts_per_ip:.1f}")
    
    # Time-based analysis with enhanced styling
    st.subheader("📈 Attack Timeline Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly attack pattern with error handling
        try:
            filtered_df['Hour'] = filtered_df['Timestamp'].dt.floor('H')
            hourly_counts = filtered_df.groupby('Hour').size().reset_index(name='Attempts')
            
            if not hourly_counts.empty:
                if chart_type == "Modern":
                    fig = px.area(
                        hourly_counts, 
                        x='Hour', 
                        y='Attempts',
                        title="🕐 Attack Timeline (Hourly)",
                        color_discrete_sequence=['#667eea']
                    )
                    fig.update_traces(fill='tonexty', fillcolor='rgba(102, 126, 234, 0.3)')
                else:
                    fig = px.line(
                        hourly_counts, 
                        x='Hour', 
                        y='Attempts',
                        title="🕐 Attack Timeline (Hourly)",
                        color_discrete_sequence=['#667eea']
                    )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Arial", size=12),
                    title_font_size=16
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No hourly data available")
        except Exception as e:
            st.warning(f"⚠️ Timeline chart error: {str(e)}")
            st.info("📊 Timeline visualization temporarily unavailable")
    
    with col2:
        # Day of week analysis with error handling
        try:
            filtered_df['DayOfWeek'] = filtered_df['Timestamp'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = filtered_df['DayOfWeek'].value_counts().reindex(day_order, fill_value=0)
            
            if day_counts.sum() > 0:
                fig = px.bar(
                    x=day_counts.index,
                    y=day_counts.values,
                    title="📅 Attacks by Day of Week",
                    color=day_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    xaxis_title="Day of Week",
                    yaxis_title="Attack Count"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No daily data available")
        except Exception as e:
            st.warning(f"⚠️ Daily chart error: {str(e)}")
            st.info("📊 Daily visualization temporarily unavailable")
    
    # Top attackers and attack patterns
    st.subheader("🎯 Attack Source Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top attacking IPs with risk assessment
        st.markdown("**🌐 Top Attacking IPs**")
        top_ips = filtered_df['IP'].value_counts().head(10)
        
        # Create enhanced IP display with risk levels
        ip_data = []
        for ip, count in top_ips.items():
            is_blocked = ip_manager.is_ip_blocked(ip)
            risk_level = "High" if count > 20 else "Medium" if count > 5 else "Low"
            ip_data.append({
                'IP': ip,
                'Attempts': count,
                'Status': '🚫 Blocked' if is_blocked else '✅ Active',
                'Risk': risk_level
            })
        
        ip_df = pd.DataFrame(ip_data)
        st.dataframe(ip_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Attack method analysis with error handling
        st.markdown("**👤 Username Attack Patterns**")
        try:
            top_users = filtered_df['Username'].value_counts().head(10)
            
            if not top_users.empty and top_users.sum() > 0:
                fig = px.pie(
                    values=top_users.values,
                    names=top_users.index,
                    title="Most Targeted Usernames",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No username data available")
        except Exception as e:
            st.warning(f"⚠️ Username chart error: {str(e)}")
            st.info("📊 Username visualization temporarily unavailable")
    
    if show_advanced:
        # Advanced analytics
        st.subheader("🔬 Advanced Threat Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Password complexity analysis
            st.markdown("**🔐 Password Complexity**")
            filtered_df['Password_Length'] = filtered_df['Password'].str.len()
            filtered_df['Has_Numbers'] = filtered_df['Password'].str.contains(r'\d', na=False)
            filtered_df['Has_Special'] = filtered_df['Password'].str.contains(r'[!@#$%^&*(),.?":{}|<>]', na=False)
            
            complexity_stats = {
                'Short (≤6 chars)': len(filtered_df[filtered_df['Password_Length'] <= 6]),
                'Medium (7-12 chars)': len(filtered_df[(filtered_df['Password_Length'] > 6) & (filtered_df['Password_Length'] <= 12)]),
                'Long (>12 chars)': len(filtered_df[filtered_df['Password_Length'] > 12]),
                'With Numbers': len(filtered_df[filtered_df['Has_Numbers']]),
                'With Special Chars': len(filtered_df[filtered_df['Has_Special']])
            }
            
            for stat, count in complexity_stats.items():
                percentage = (count / total_attempts) * 100 if total_attempts > 0 else 0
                st.metric(stat, f"{count} ({percentage:.1f}%)")
        
        with col2:
            # Attack intensity heatmap
            st.markdown("**🌡️ Attack Intensity Heatmap**")
            
            # Create hour vs day heatmap with proper data alignment
            try:
                filtered_df['Hour_Only'] = filtered_df['Timestamp'].dt.hour
                filtered_df['Day_Only'] = filtered_df['Timestamp'].dt.day_name()
                
                # Create pivot table with all hours (0-23) to ensure proper alignment
                heatmap_data = filtered_df.groupby(['Day_Only', 'Hour_Only']).size().unstack(fill_value=0)
                
                if not heatmap_data.empty:
                    # Ensure all hours 0-23 are present
                    all_hours = list(range(24))
                    for hour in all_hours:
                        if hour not in heatmap_data.columns:
                            heatmap_data[hour] = 0
                    
                    # Sort columns to ensure proper order
                    heatmap_data = heatmap_data.reindex(columns=sorted(heatmap_data.columns))
                    
                    # Create the heatmap with matching dimensions
                    fig = px.imshow(
                        heatmap_data.values,
                        x=[f"{h:02d}:00" for h in sorted(heatmap_data.columns)],
                        y=heatmap_data.index,
                        color_continuous_scale='Reds',
                        title="Attack Intensity by Hour & Day",
                        aspect="auto"
                    )
                    fig.update_layout(
                        height=300,
                        xaxis_title="Hour of Day",
                        yaxis_title="Day of Week"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 No data available for heatmap visualization")
            except Exception as e:
                st.warning(f"⚠️ Heatmap visualization unavailable: {str(e)}")
                # Fallback: Simple bar chart by hour
                try:
                    hourly_attacks = filtered_df.groupby(filtered_df['Timestamp'].dt.hour).size()
                    fig = px.bar(
                        x=hourly_attacks.index,
                        y=hourly_attacks.values,
                        title="Attacks by Hour of Day",
                        labels={'x': 'Hour', 'y': 'Attack Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("📊 Visualization data not available")
        
        with col3:
            # Geographic simulation (placeholder) with error handling
            st.markdown("**🌍 Simulated Geographic Distribution**")
            
            try:
                # Simulate geographic data based on IP patterns
                geo_data = {
                    'Private/Internal': len(filtered_df[filtered_df['IP'].str.contains(r'^(192\.168\.|10\.|172\.)', na=False)]),
                    'Localhost': len(filtered_df[filtered_df['IP'].str.contains(r'^127\.', na=False)]),
                    'External/Public': len(filtered_df[~filtered_df['IP'].str.contains(r'^(192\.168\.|10\.|172\.|127\.)', na=False)])
                }
                
                # Filter out zero values
                geo_data = {k: v for k, v in geo_data.items() if v > 0}
                
                if geo_data and sum(geo_data.values()) > 0:
                    fig = px.pie(
                        values=list(geo_data.values()),
                        names=list(geo_data.keys()),
                        title="IP Address Categories",
                        color_discrete_sequence=['#ff9999', '#66b3ff', '#99ff99']
                    )
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 No geographic data available")
            except Exception as e:
                st.warning(f"⚠️ Geographic chart error: {str(e)}")
                st.info("📊 Geographic visualization temporarily unavailable")
    
    # Export functionality
    st.subheader("📥 Export Analytics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export filtered data
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Raw Data",
            data=csv_data,
            file_name=f"idps_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export summary report
        summary_report = generate_analytics_summary(filtered_df, total_attempts, unique_ips, blocked_ips)
        st.download_button(
            label="📝 Download Summary Report",
            data=summary_report,
            file_name=f"idps_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with col3:
        if st.button("🔄 Refresh Analytics"):
            st.rerun()

def generate_analytics_summary(df, total_attempts, unique_ips, blocked_ips):
    """Generate a text summary of analytics"""
    summary = f"""
IDPS Analytics Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== OVERVIEW ===
Total Login Attempts: {total_attempts:,}
Unique IP Addresses: {unique_ips}
Blocked IP Addresses: {blocked_ips}
Success Rate: 0% (All attempts blocked/failed)

=== TOP ATTACKERS ===
"""
    
    top_ips = df['IP'].value_counts().head(5)
    for i, (ip, count) in enumerate(top_ips.items(), 1):
        summary += f"{i}. {ip}: {count} attempts\n"
    
    summary += f"""
=== ATTACK PATTERNS ===
Most Common Username: {df['Username'].mode().iloc[0] if not df.empty else 'N/A'}
Average Password Length: {df['Password'].str.len().mean():.1f} characters
Peak Attack Hour: {df['Timestamp'].dt.hour.mode().iloc[0] if not df.empty else 'N/A'}:00

=== RECOMMENDATIONS ===
1. Monitor blocked IPs for persistent attack patterns
2. Consider implementing rate limiting for high-frequency sources
3. Review and update detection rules based on common attack patterns
4. Enhance monitoring during peak attack hours

=== SYSTEM STATUS ===
Detection System: Active
Blocking System: Active  
ML Model: {'Trained' if intrusion_model.model_info()['status'] == 'Trained' else 'Needs Training'}
    """
    
    return summary

def display_model_info():
    """Display ML model information"""
    st.header("🧠 Machine Learning Model")
    
    model_info = intrusion_model.model_info()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Status")
        
        if model_info["status"] == "Trained":
            st.success("✅ Model is trained and ready")
            st.json(model_info)
        else:
            st.warning("⚠️ Model is not trained")
            st.info("To train the model, run: `python -m src.tools.train_model`")
    
    with col2:
        st.subheader("Feature Importance")
        
        if model_info.get("feature_importance"):
            importance_data = model_info["feature_importance"]
            fig = px.bar(
                x=list(importance_data.values()),
                y=list(importance_data.keys()),
                orientation='h',
                title="Feature Importance"
            )
            st.plotly_chart(fig, use_container_width=True)

def main():
    """Enhanced main dashboard function with improved navigation"""
    
    # Enhanced sidebar with better styling
    with st.sidebar:
        # Clean header
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
            <h1 style="color: white; margin: 0; font-size: 1.8rem;">🔐</h1>
            <h3 style="color: white; margin: 0.2rem 0 0 0; font-weight: 300;">IDPS Dashboard</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple navigation menu
        pages = [
            ("🏠", "System Overview"),
            ("📊", "Login Attempts"), 
            ("🚫", "Blocked IPs"),
            ("📋", "Audit Logs"),
            ("📈", "Analytics"),
            ("🧠", "ML Model Info")
        ]
        
        # Clean page selection
        selected_page = st.selectbox(
            "Navigate to:",
            options=[page[1] for page in pages],
            format_func=lambda x: f"{next(icon for icon, name in pages if name == x)} {x}",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Monitor Control in sidebar
        st.markdown("### 🔍 Monitor Control")
        display_sidebar_monitor_controls()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quick system status (compact)
        try:
            blocked_count = len(set(ip_manager.get_blocked_ips()))
            login_df = load_login_attempts()
            total_attempts = len(login_df)
            recent_attempts = len(login_df[
                login_df['Timestamp'] > datetime.now() - timedelta(hours=1)
            ]) if not login_df.empty else 0
            
            # Status indicator with monitor status
            status_color = "#ef4444" if blocked_count > 5 else "#f59e0b" if blocked_count > 0 else "#10b981"
            status_text = "High Alert" if blocked_count > 5 else "Active" if blocked_count > 0 else "Secure"
            
            # Get monitor status
            monitor_status = get_monitor_status()
            monitor_running = monitor_status["running"]
            monitor_color = "#10b981" if monitor_running else "#ef4444"
            monitor_text = "Running" if monitor_running else "Stopped"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                    <div style="width: 8px; height: 8px; background: {status_color}; border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="color: white; font-weight: 600; font-size: 0.9rem;">{status_text}</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                    <div style="width: 8px; height: 8px; background: {monitor_color}; border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="color: white; font-weight: 600; font-size: 0.9rem;">Monitor: {monitor_text}</span>
                </div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; line-height: 1.4;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span>Blocked IPs</span>
                        <span style="font-weight: 600;">{blocked_count}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span>Total Attempts</span>
                        <span style="font-weight: 600;">{total_attempts:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Last Hour</span>
                        <span style="font-weight: 600;">{recent_attempts}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <div style="color: rgba(255,255,255,0.7); font-size: 0.85rem; text-align: center;">
                    Status unavailable
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Simple controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄", help="Refresh data", use_container_width=True):
                st.rerun()
        with col2:
            auto_refresh = st.checkbox("Auto", help="Auto-refresh every 30s")
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()

    # Display selected page with enhanced error handling
    try:
        if selected_page == "System Overview":
            display_system_overview()
        elif selected_page == "Login Attempts":
            display_recent_attempts()
        elif selected_page == "Blocked IPs":
            display_blocked_ips()
        elif selected_page == "Audit Logs":
            display_audit_logs()
        elif selected_page == "Analytics":
            display_analytics()
        elif selected_page == "ML Model Info":
            display_model_info()
    except Exception as e:
        st.error(f"Error loading page: {e}")
        st.markdown("""
        <div class="alert-box alert-danger">
            <h4>⚠️ Page Load Error</h4>
            <p>There was an error loading this page. Please try refreshing or contact support.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>🔒 IDPS Dashboard</strong><br>
                <small>Intrusion Detection & Prevention System</small>
            </div>
            <div style="text-align: right;">
                <small>Last updated: {}</small><br>
                <small>🟢 System Online</small>
            </div>
        </div>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
