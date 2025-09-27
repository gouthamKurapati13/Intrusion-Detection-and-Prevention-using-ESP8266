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

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
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
    """Display system overview metrics"""
    st.header("📊 System Overview")
    
    # Get system statistics
    blocked_ips = ip_manager.get_blocked_ips()
    blocked_count = len(set(blocked_ips))  # Unique IPs
    
    login_attempts_df = load_login_attempts()
    total_attempts = len(login_attempts_df)
    
    recent_attempts = len(login_attempts_df[
        login_attempts_df['Timestamp'] > datetime.now() - timedelta(hours=1)
    ]) if not login_attempts_df.empty else 0
    
    model_info = intrusion_model.model_info()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚫 Blocked IPs",
            value=blocked_count,
            delta=None
        )
    
    with col2:
        st.metric(
            label="📊 Total Attempts",
            value=total_attempts,
            delta=None
        )
    
    with col3:
        st.metric(
            label="⏰ Recent Attempts (1h)",
            value=recent_attempts,
            delta=None
        )
    
    with col4:
        model_status = "✅ Trained" if model_info["status"] == "Trained" else "❌ Not Trained"
        st.metric(
            label="🤖 ML Model",
            value=model_status,
            delta=None
        )

def display_recent_attempts():
    """Display recent login attempts"""
    st.header("📄 Recent Login Attempts")
    
    df = load_login_attempts()
    
    if df.empty:
        st.info("No login attempts recorded yet.")
        return
    
    # Show filters
    col1, col2 = st.columns(2)
    with col1:
        hours_back = st.selectbox("Show attempts from last:", [1, 6, 12, 24, 72], index=3)
    with col2:
        ip_filter = st.text_input("Filter by IP (optional):")
    
    # Apply filters
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    filtered_df = df[df['Timestamp'] > cutoff_time].copy()
    
    if ip_filter:
        filtered_df = filtered_df[filtered_df['IP'].str.contains(ip_filter, na=False)]
    
    # Sort by timestamp (most recent first)
    filtered_df = filtered_df.sort_values('Timestamp', ascending=False)
    
    # Add blocked status
    filtered_df['Blocked'] = filtered_df['IP'].apply(lambda x: ip_manager.is_ip_blocked(x))
    
    # Display the data
    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Show statistics
        unique_ips = filtered_df['IP'].nunique()
        unique_users = filtered_df['Username'].nunique()
        st.info(f"Showing {len(filtered_df)} attempts from {unique_ips} unique IPs and {unique_users} unique usernames")
    else:
        st.info("No attempts found for the selected filters.")

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
    """Display analytics and visualizations"""
    st.header("📈 Analytics")
    
    df = load_login_attempts()
    
    if df.empty:
        st.info("No data available for analytics.")
        return
    
    # Time-based analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Attempts Over Time")
        if not df.empty:
            # Group by hour
            df['Hour'] = df['Timestamp'].dt.floor('H')
            hourly_counts = df.groupby('Hour').size().reset_index(name='Attempts')
            
            fig = px.line(
                hourly_counts, 
                x='Hour', 
                y='Attempts',
                title="Login Attempts by Hour"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top IPs by Attempts")
        if not df.empty:
            top_ips = df['IP'].value_counts().head(10)
            
            fig = px.bar(
                x=top_ips.values,
                y=top_ips.index,
                orientation='h',
                title="Top 10 IPs by Login Attempts"
            )
            fig.update_layout(xaxis_title="Attempts", yaxis_title="IP Address")
            st.plotly_chart(fig, use_container_width=True)
    
    # Username and password analysis
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Most Common Usernames")
        if not df.empty:
            top_users = df['Username'].value_counts().head(10)
            st.bar_chart(top_users)
    
    with col4:
        st.subheader("Password Length Distribution")
        if not df.empty:
            df['Password_Length'] = df['Password'].str.len()
            length_dist = df['Password_Length'].value_counts().sort_index()
            st.bar_chart(length_dist)

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
    """Main dashboard function"""
    st.title("🔐 Intrusion Detection & Prevention System Dashboard")
    st.markdown("Real-time monitoring and management interface")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select a page:",
            [
                "System Overview",
                "Login Attempts",
                "Blocked IPs",
                "Audit Logs",
                "Analytics",
                "ML Model Info"
            ]
        )
        
        # Auto-refresh option
        auto_refresh = st.checkbox("Auto-refresh (30s)")
        if auto_refresh:
            time.sleep(30)
            st.rerun()
        
        # Manual refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Display selected page
    if page == "System Overview":
        display_system_overview()
    elif page == "Login Attempts":
        display_recent_attempts()
    elif page == "Blocked IPs":
        display_blocked_ips()
    elif page == "Audit Logs":
        display_audit_logs()
    elif page == "Analytics":
        display_analytics()
    elif page == "ML Model Info":
        display_model_info()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🔒 IDPS Dashboard | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    main()
