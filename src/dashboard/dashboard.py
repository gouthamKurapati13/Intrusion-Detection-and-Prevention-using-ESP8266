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

def display_system_overview():
    """Display enhanced system overview metrics with real-time data"""
    # Custom header with gradient background
    st.markdown("""
    <div class="dashboard-header">
        <h1>� IDPS System Dashboard</h1>
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
            label="🤖 ML Model Status",
            value=f"{model_emoji} {model_status}",
            delta=None
        )
        
        if model_info["status"] == "Trained":
            accuracy = model_info.get("accuracy", 0)
            st.markdown(f'<p class="status-good">🎯 Accuracy: {accuracy:.1%}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-warning">⚠️ Needs training</p>', unsafe_allow_html=True)
    
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
    """Display recent login attempts with enhanced filtering and visualization"""
    st.header("📄 Login Attempts Monitor")
    
    df = load_login_attempts()
    
    if df.empty:
        st.markdown("""
        <div class="alert-box alert-info">
            <h4>📭 No Data Available</h4>
            <p>No login attempts have been recorded yet. The system is ready to monitor incoming attempts.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Enhanced filters in columns
    st.subheader("🔍 Filter Options")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        hours_back = st.selectbox(
            "⏰ Time Range:", 
            [1, 6, 12, 24, 72, 168], 
            index=3,
            format_func=lambda x: f"Last {x}h" if x < 24 else f"Last {x//24}d"
        )
    
    with col2:
        ip_filter = st.text_input("🌐 Filter by IP:", placeholder="e.g., 192.168.1.1")
    
    with col3:
        username_filter = st.text_input("👤 Filter by Username:", placeholder="e.g., admin")
    
    with col4:
        show_blocked_only = st.checkbox("🚫 Show only blocked IPs")
    
    # Apply filters
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    filtered_df = df[df['Timestamp'] > cutoff_time].copy()
    
    if ip_filter:
        filtered_df = filtered_df[filtered_df['IP'].str.contains(ip_filter, case=False, na=False)]
    
    if username_filter:
        filtered_df = filtered_df[filtered_df['Username'].str.contains(username_filter, case=False, na=False)]
    
    # Add enhanced columns
    filtered_df['Blocked'] = filtered_df['IP'].apply(lambda x: ip_manager.is_ip_blocked(x))
    filtered_df['Risk Level'] = filtered_df.apply(assess_attempt_risk, axis=1)
    filtered_df['Country'] = filtered_df['IP'].apply(get_country_from_ip)  # Placeholder for geo data
    
    if show_blocked_only:
        filtered_df = filtered_df[filtered_df['Blocked'] == True]
    
    # Sort by timestamp (most recent first)
    filtered_df = filtered_df.sort_values('Timestamp', ascending=False)
    
    if not filtered_df.empty:
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        unique_ips = filtered_df['IP'].nunique()
        unique_users = filtered_df['Username'].nunique()
        blocked_ips = filtered_df[filtered_df['Blocked'] == True]['IP'].nunique()
        high_risk = len(filtered_df[filtered_df['Risk Level'] == 'High'])
        total_attempts = len(filtered_df)
        
        with col1:
            st.metric("Total Attempts", total_attempts)
        with col2:
            st.metric("Unique IPs", unique_ips)
        with col3:
            st.metric("Unique Users", unique_users)
        with col4:
            st.metric("Blocked IPs", blocked_ips, delta_color="inverse")
        with col5:
            st.metric("High Risk", high_risk, delta_color="inverse")
        
        # Enhanced data display with formatting
        st.subheader("📋 Detailed View")
        
        # Format the dataframe for better display
        display_df = filtered_df.copy()
        display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Add status icons
        display_df['Status'] = display_df.apply(lambda row: 
            '🚫 BLOCKED' if row['Blocked'] else '✅ ALLOWED', axis=1)
        
        # Reorder columns for better presentation
        column_order = ['Timestamp', 'IP', 'Username', 'Status', 'Risk Level', 'Country']
        display_df = display_df[column_order]
        
        # Style the dataframe
        styled_df = display_df.style.apply(lambda x: 
            ['background-color: #ffebee' if x['Status'] == '🚫 BLOCKED' 
             else 'background-color: #f3e5f5' if x['Risk Level'] == 'High'
             else 'background-color: #fff3e0' if x['Risk Level'] == 'Medium'
             else '' for i in x], axis=1)
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download option
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"login_attempts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
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
    
    df = load_login_attempts()
    
    if df.empty:
        st.markdown("""
        <div class="alert-box alert-info">
            <h4>📊 No Analytics Data</h4>
            <p>No login attempts available for analysis. Analytics will appear once data is collected.</p>
        </div>
        """, unsafe_allow_html=True)
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
        # Hourly attack pattern
        filtered_df['Hour'] = filtered_df['Timestamp'].dt.floor('H')
        hourly_counts = filtered_df.groupby('Hour').size().reset_index(name='Attempts')
        
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
    
    with col2:
        # Day of week analysis
        filtered_df['DayOfWeek'] = filtered_df['Timestamp'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = filtered_df['DayOfWeek'].value_counts().reindex(day_order, fill_value=0)
        
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
        # Attack method analysis
        st.markdown("**👤 Username Attack Patterns**")
        top_users = filtered_df['Username'].value_counts().head(10)
        
        fig = px.pie(
            values=top_users.values,
            names=top_users.index,
            title="Most Targeted Usernames",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
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
            
            # Create hour vs day heatmap
            filtered_df['Hour_Only'] = filtered_df['Timestamp'].dt.hour
            filtered_df['Day_Only'] = filtered_df['Timestamp'].dt.day_name()
            
            heatmap_data = filtered_df.groupby(['Day_Only', 'Hour_Only']).size().unstack(fill_value=0)
            
            if not heatmap_data.empty:
                fig = px.imshow(
                    heatmap_data.values,
                    x=[f"{h:02d}:00" for h in range(24)],
                    y=heatmap_data.index,
                    color_continuous_scale='Reds',
                    title="Attack Intensity by Hour & Day"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Geographic simulation (placeholder)
            st.markdown("**🌍 Simulated Geographic Distribution**")
            
            # Simulate geographic data based on IP patterns
            geo_data = {
                'Unknown/Private': len(filtered_df[filtered_df['IP'].str.contains(r'^(192\.168\.|10\.|172\.)')]),
                'Localhost': len(filtered_df[filtered_df['IP'].str.contains(r'^127\.')]),
                'External': len(filtered_df[~filtered_df['IP'].str.contains(r'^(192\.168\.|10\.|172\.|127\.)')])
            }
            
            fig = px.pie(
                values=list(geo_data.values()),
                names=list(geo_data.keys()),
                title="IP Address Categories",
                color_discrete_sequence=['#ff9999', '#66b3ff', '#99ff99']
            )
            st.plotly_chart(fig, use_container_width=True)
    
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
    st.header("🤖 Machine Learning Model")
    
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
            ("🤖", "ML Model Info")
        ]
        
        # Clean page selection
        selected_page = st.selectbox(
            "Navigate to:",
            options=[page[1] for page in pages],
            format_func=lambda x: f"{next(icon for icon, name in pages if name == x)} {x}",
            label_visibility="collapsed"
        )
        
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quick system status (compact)
        try:
            blocked_count = len(set(ip_manager.get_blocked_ips()))
            login_df = load_login_attempts()
            total_attempts = len(login_df)
            recent_attempts = len(login_df[
                login_df['Timestamp'] > datetime.now() - timedelta(hours=1)
            ]) if not login_df.empty else 0
            
            # Status indicator
            status_color = "#ef4444" if blocked_count > 5 else "#f59e0b" if blocked_count > 0 else "#10b981"
            status_text = "High Alert" if blocked_count > 5 else "Active" if blocked_count > 0 else "Secure"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                    <div style="width: 8px; height: 8px; background: {status_color}; border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="color: white; font-weight: 600; font-size: 0.9rem;">{status_text}</span>
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
        # Clean footer space
        st.markdown("""
        <small style="color: rgba(255,255,255,0.7);">
        IDPS v2.0<br>
        Intrusion Detection &<br>
        Prevention System<br><br>
        �️ Protecting your network<br>
        🔍 24/7 monitoring<br>
        🤖 AI-powered detection
        </small>
        """, unsafe_allow_html=True)
    
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
