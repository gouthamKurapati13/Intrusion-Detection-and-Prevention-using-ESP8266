"""
Streamlit Attack Simulator UI - Test different attack patterns against the IDPS
"""
import streamlit as st
import requests
import time
import json
import random
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.settings import SERVER_HOST, SERVER_PORT
from src.tools.attack_scenarios import get_all_scenarios, get_scenario, get_scenario_names

# Configure page
st.set_page_config(
    page_title="IDPS Attack Simulator",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for attack simulator theme
st.markdown("""
<style>
    /* Main styling */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Attack simulator theme */
    .attack-header {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3);
    }
    
    /* Status indicators */
    .status-running {
        color: #dc2626;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    .status-idle {
        color: #059669;
        font-weight: bold;
    }
    
    .status-warning {
        color: #d97706;
        font-weight: bold;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Attack cards */
    .attack-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #dc2626;
    }
    
    .attack-card h3 {
        color: #dc2626;
        margin-top: 0;
    }
    
    /* Results styling */
    .attack-results {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #92400e;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #fcd34d;
    }
    
    /* Success box */
    .success-box {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Sidebar styling for attack simulator */
    .css-1d391kg {
        background: linear-gradient(180deg, #dc2626 0%, #991b1b 100%);
    }
</style>
""", unsafe_allow_html=True)

# Global variables for tracking attack sessions
if 'attack_running' not in st.session_state:
    st.session_state.attack_running = False
if 'attack_results' not in st.session_state:
    st.session_state.attack_results = []
if 'attack_stats' not in st.session_state:
    st.session_state.attack_stats = {
        'total_attempts': 0,
        'successful_requests': 0,
        'blocked_requests': 0,
        'errors': 0
    }

class AttackSimulator:
    """Class to handle different types of attack simulations"""
    
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.timeout = 5
        self.stats = {
            'total_attempts': 0,
            'successful_requests': 0,
            'blocked_requests': 0,
            'errors': 0
        }
    
    def brute_force_attack(self, usernames, passwords, delay=1, max_threads=5):
        """Simulate brute force attack"""
        results = []
        
        # Sequential approach to avoid thread issues with session state
        for username in usernames:
            for password in passwords:
                # Check if we should continue (this check is safe in main thread)
                try:
                    if hasattr(st, 'session_state') and hasattr(st.session_state, 'attack_running'):
                        if not st.session_state.attack_running:
                            break
                except:
                    pass  # Continue if session state is not available
                
                result = self._attempt_login(username, password)
                results.append(result)
                time.sleep(delay)
                
        return results
    
    def dictionary_attack(self, target_username, password_list, delay=0.5):
        """Simulate dictionary attack on specific username"""
        results = []
        
        for password in password_list:
            try:
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'attack_running'):
                    if not st.session_state.attack_running:
                        break
            except:
                pass
                
            result = self._attempt_login(target_username, password)
            results.append(result)
            time.sleep(delay)
            
        return results
    
    def credential_stuffing(self, credential_pairs, delay=0.3):
        """Simulate credential stuffing attack"""
        results = []
        
        for username, password in credential_pairs:
            try:
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'attack_running'):
                    if not st.session_state.attack_running:
                        break
            except:
                pass
                
            result = self._attempt_login(username, password)
            results.append(result)
            time.sleep(delay)
            
        return results
    
    def volumetric_attack(self, username, password, num_requests=100, delay=0.1):
        """Simulate high-volume attack from single source"""
        results = []
        
        for i in range(num_requests):
            try:
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'attack_running'):
                    if not st.session_state.attack_running:
                        break
            except:
                pass
                
            result = self._attempt_login(f"{username}_{i}", password)
            results.append(result)
            time.sleep(delay)
            
        return results
    
    def _attempt_login(self, username, password):
        """Attempt a single login"""
        try:
            response = self.session.post(
                f"{self.target_url}/login",
                data={
                    'username': username,
                    'password': password
                },
                timeout=5
            )
            
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'username': username,
                'password': password,
                'status_code': response.status_code,
                'response': response.text[:100] if response.text else '',
                'success': response.status_code == 200
            }
            
            # Update local stats (thread-safe)
            self.stats['total_attempts'] += 1
            if response.status_code == 200:
                self.stats['successful_requests'] += 1
            elif response.status_code == 403:
                self.stats['blocked_requests'] += 1
            
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'username': username,
                'password': password,
                'status_code': 'ERROR',
                'response': str(e)[:100],
                'success': False
            }

def get_common_usernames():
    """Get list of common usernames for attacks"""
    return [
        'admin', 'administrator', 'root', 'user', 'guest', 'test',
        'demo', 'support', 'service', 'operator', 'manager', 'staff',
        'login', 'web', 'www', 'ftp', 'mail', 'email', 'sa', 'oracle'
    ]

def get_common_passwords():
    """Get list of common passwords for attacks"""
    return [
        'password', '123456', 'password123', 'admin', 'qwerty',
        'letmein', 'welcome', 'monkey', '1234567890', 'abc123',
        'Password1', 'password1', 'root', 'toor', 'pass', 'test',
        '12345', 'dragon', 'master', 'shadow', 'login', 'admin123'
    ]

def get_credential_pairs():
    """Get common username/password pairs"""
    return [
        ('admin', 'admin'),
        ('admin', 'password'),
        ('administrator', 'administrator'),
        ('root', 'root'),
        ('root', 'toor'),
        ('user', 'user'),
        ('guest', 'guest'),
        ('test', 'test'),
        ('demo', 'demo'),
        ('service', 'service')
    ]

def display_attack_header():
    """Display attack simulator header"""
    st.markdown("""
    <div class="attack-header">
        <h1>⚔️ IDPS Attack Simulator</h1>
        <p>Test and validate intrusion detection capabilities</p>
        <div style="font-size: 0.9rem; margin-top: 1rem; opacity: 0.9;">
            🎯 Target System Testing | 🛡️ Security Validation | 📊 Performance Analysis
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_target_config():
    """Display target configuration"""
    st.subheader("🎯 Target Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        target_host = st.text_input("Target Host", value=SERVER_HOST, help="IDPS server hostname or IP")
    
    with col2:
        target_port = st.number_input("Target Port", value=SERVER_PORT, min_value=1, max_value=65535)
    
    with col3:
        protocol = st.selectbox("Protocol", ["http", "https"], index=0)
    
    target_url = f"{protocol}://{target_host}:{target_port}"
    
    # Test connection
    if st.button("🔍 Test Connection"):
        try:
            response = requests.get(f"{target_url}/health", timeout=5)
            if response.status_code == 200:
                st.success(f"✅ Successfully connected to {target_url}")
            else:
                st.warning(f"⚠️ Connected but received status code: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
    
    return target_url

def display_attack_types():
    """Display available attack types"""
    st.subheader("⚔️ Attack Configuration")
    
    # Choice between pre-configured and custom attacks
    config_mode = st.radio(
        "Configuration Mode:",
        ["🎯 Pre-configured Scenarios", "🛠️ Custom Attack"],
        horizontal=True
    )
    
    if config_mode == "🎯 Pre-configured Scenarios":
        return "Pre-configured", display_scenario_selector()
    else:
        attack_type = st.selectbox(
            "Select Attack Type:",
            [
                "Brute Force Attack",
                "Dictionary Attack", 
                "Credential Stuffing",
                "Volumetric Attack"
            ]
        )
        return "Custom", attack_type

def display_scenario_selector():
    """Display pre-configured scenario selector"""
    st.markdown("### 🎯 Select Attack Scenario")
    
    scenarios = get_all_scenarios()
    scenario_names = get_scenario_names()
    
    # Create a mapping of display names to scenario keys
    display_names = [scenarios[name]["name"] for name in scenario_names]
    
    selected_display = st.selectbox(
        "Choose a pre-configured attack scenario:",
        display_names
    )
    
    # Find the corresponding scenario key
    selected_scenario = None
    for key, scenario in scenarios.items():
        if scenario["name"] == selected_display:
            selected_scenario = key
            break
    
    if selected_scenario:
        scenario_data = get_scenario(selected_scenario)
        
        # Display scenario information with clean styling
        attack_type_display = scenario_data['type'].replace('_', ' ').title()
        
        # Title with icon
        st.markdown(f"### 📋 {scenario_data['name']}")
        
        # Attack type badge
        st.markdown(f"""
        <div style="background: #2d3748; color: white; padding: 0.5rem 1rem; 
                    border-radius: 6px; text-align: center; font-weight: bold; 
                    display: inline-block; margin: 0.5rem 0;">
            ⚡ Attack Type: {attack_type_display.upper()}
        </div>
        """, unsafe_allow_html=True)
        
        # Description
        st.markdown("**📝 Attack Description:**")
        st.write(scenario_data['description'])
        
        # Additional details if available
        if 'detailed_info' in scenario_data:
            with st.expander("🔍 Technical Details", expanded=False):
                details = scenario_data['detailed_info']
                for key, value in details.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Show scenario details
        with st.expander("📊 Scenario Details", expanded=False):
            st.json(scenario_data)
    
    return selected_scenario

def configure_brute_force_attack():
    """Configure brute force attack parameters"""
    st.markdown("""
    <div class="attack-card">
        <h3>🔨 Brute Force Attack Configuration</h3>
        <p>Systematically attempts multiple username/password combinations</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Usernames:**")
        use_common_users = st.checkbox("Use common usernames", value=True)
        if use_common_users:
            usernames = get_common_usernames()
            st.write(f"Selected {len(usernames)} common usernames")
        else:
            custom_users = st.text_area("Custom usernames (one per line):", "admin\nroot\nuser")
            usernames = [u.strip() for u in custom_users.split('\n') if u.strip()]
    
    with col2:
        st.write("**Passwords:**")
        use_common_passwords = st.checkbox("Use common passwords", value=True)
        if use_common_passwords:
            passwords = get_common_passwords()
            st.write(f"Selected {len(passwords)} common passwords")
        else:
            custom_passwords = st.text_area("Custom passwords (one per line):", "password\n123456\nadmin")
            passwords = [p.strip() for p in custom_passwords.split('\n') if p.strip()]
    
    col3, col4, col5 = st.columns(3)
    with col3:
        delay = st.slider("Delay between attempts (seconds)", 0.1, 5.0, 1.0, 0.1)
    with col4:
        max_threads = st.number_input("Max concurrent threads", 1, 10, 3)
    with col5:
        max_attempts = st.number_input("Max total attempts", 10, 1000, 100)
    
    # Limit combinations if needed
    total_combinations = len(usernames) * len(passwords)
    if total_combinations > max_attempts:
        st.warning(f"⚠️ Total combinations ({total_combinations}) exceeds max attempts ({max_attempts}). Will be limited.")
        usernames = usernames[:max_attempts//len(passwords) + 1]
        passwords = passwords[:max_attempts//len(usernames) + 1]
    
    return {
        'usernames': usernames,
        'passwords': passwords,
        'delay': delay,
        'max_threads': max_threads
    }

def configure_dictionary_attack():
    """Configure dictionary attack parameters"""
    st.markdown("""
    <div class="attack-card">
        <h3>📚 Dictionary Attack Configuration</h3>
        <p>Tests a specific username against a dictionary of passwords</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_username = st.text_input("Target Username:", "admin")
        delay = st.slider("Delay between attempts (seconds)", 0.1, 3.0, 0.5, 0.1)
    
    with col2:
        use_common_passwords = st.checkbox("Use common password dictionary", value=True)
        if use_common_passwords:
            password_list = get_common_passwords()
            st.write(f"Using {len(password_list)} common passwords")
        else:
            custom_passwords = st.text_area("Custom password dictionary (one per line):")
            password_list = [p.strip() for p in custom_passwords.split('\n') if p.strip()]
    
    return {
        'target_username': target_username,
        'password_list': password_list,
        'delay': delay
    }

def configure_credential_stuffing():
    """Configure credential stuffing attack"""
    st.markdown("""
    <div class="attack-card">
        <h3>🔄 Credential Stuffing Configuration</h3>
        <p>Tests known username/password pairs from data breaches</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_common_pairs = st.checkbox("Use common credential pairs", value=True)
        delay = st.slider("Delay between attempts (seconds)", 0.1, 2.0, 0.3, 0.1)
    
    with col2:
        if use_common_pairs:
            credential_pairs = get_credential_pairs()
            st.write(f"Using {len(credential_pairs)} common credential pairs")
        else:
            st.write("Enter credentials in format 'username:password' (one per line):")
            custom_creds = st.text_area("Custom credentials:", "admin:admin\nroot:root")
            credential_pairs = []
            for line in custom_creds.split('\n'):
                if ':' in line:
                    user, pwd = line.strip().split(':', 1)
                    credential_pairs.append((user, pwd))
    
    return {
        'credential_pairs': credential_pairs,
        'delay': delay
    }

def configure_volumetric_attack():
    """Configure volumetric attack"""
    st.markdown("""
    <div class="attack-card">
        <h3>🌊 Volumetric Attack Configuration</h3>
        <p>High-volume attack to test rate limiting and DDoS protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        username = st.text_input("Base Username:", "admin")
        password = st.text_input("Password:", "password")
    
    with col2:
        num_requests = st.number_input("Number of requests", 10, 1000, 100)
        delay = st.slider("Delay between requests (seconds)", 0.01, 1.0, 0.1, 0.01)
    
    with col3:
        st.info("This attack will append numbers to the username to create variations")
        st.write(f"Will generate requests like: {username}_1, {username}_2, etc.")
    
    return {
        'username': username,
        'password': password,
        'num_requests': num_requests,  
        'delay': delay
    }

def display_attack_controls(target_url, attack_config, attack_type, config_mode="Custom"):
    """Display attack control buttons and status"""
    st.subheader("🎮 Attack Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 Start Attack", disabled=st.session_state.attack_running):
            st.session_state.attack_running = True
            st.session_state.attack_results = []
            st.session_state.attack_stats = {
                'total_attempts': 0,
                'successful_requests': 0,
                'blocked_requests': 0,
                'errors': 0
            }
            
            # Show progress message
            with st.spinner('Launching attack...'):
                # Run attack
                simulator = AttackSimulator(target_url)
                results = []
                
                try:
                    # Handle different attack types (both custom and pre-configured)
                    if attack_type == "brute_force" or attack_type == "Brute Force Attack":
                        # Extract parameters for brute force
                        params = {
                            'usernames': attack_config.get('usernames', ['admin']),
                            'passwords': attack_config.get('passwords', ['password']),
                            'delay': attack_config.get('delay', 1.0),
                            'max_threads': attack_config.get('max_threads', 3)
                        }
                        results = simulator.brute_force_attack(**params)
                        
                    elif attack_type == "dictionary" or attack_type == "Dictionary Attack":
                        params = {
                            'target_username': attack_config.get('target_username', 'admin'),
                            'password_list': attack_config.get('password_list', ['password']),
                            'delay': attack_config.get('delay', 0.5)
                        }
                        results = simulator.dictionary_attack(**params)
                        
                    elif attack_type == "credential_stuffing" or attack_type == "Credential Stuffing":
                        params = {
                            'credential_pairs': attack_config.get('credential_pairs', [('admin', 'admin')]),
                            'delay': attack_config.get('delay', 0.3)
                        }
                        results = simulator.credential_stuffing(**params)
                        
                    elif attack_type == "volumetric" or attack_type == "Volumetric Attack":
                        params = {
                            'username': attack_config.get('username', 'admin'),
                            'password': attack_config.get('password', 'password'),
                            'num_requests': attack_config.get('num_requests', 100),
                            'delay': attack_config.get('delay', 0.1)
                        }
                        results = simulator.volumetric_attack(**params)
                    
                    # Update session state with results and stats
                    st.session_state.attack_results.extend(results)
                    st.session_state.attack_stats = simulator.stats.copy()
                    
                except Exception as e:
                    st.error(f"Attack failed: {str(e)}")
                finally:
                    st.session_state.attack_running = False
            
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Attack"):
            st.session_state.attack_running = False
    
    with col3:
        if st.button("🧹 Clear Results"):
            st.session_state.attack_results = []
            st.session_state.attack_stats = {
                'total_attempts': 0,
                'successful_requests': 0,
                'blocked_requests': 0,
                'errors': 0
            }
    
    with col4:
        if st.button("📊 Export Results"):
            if st.session_state.attack_results:
                df = pd.DataFrame(st.session_state.attack_results)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"attack_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

def display_attack_status():
    """Display current attack status"""
    if st.session_state.attack_running:
        st.markdown("""
        <div class="warning-box">
            <h4 class="status-running">🔥 Attack in Progress</h4>
            <p>The attack simulation is currently running. Monitor the results below.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <h4 class="status-idle">✅ System Ready</h4>
            <p>Ready to launch attack simulation.</p>
        </div>
        """, unsafe_allow_html=True)

def display_attack_results():
    """Display attack results and statistics"""
    st.subheader("📊 Attack Results")
    
    # Display statistics
    stats = st.session_state.attack_stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Attempts", stats['total_attempts'])
    with col2:
        st.metric("Successful", stats['successful_requests'], delta_color="inverse")
    with col3:
        st.metric("Blocked", stats['blocked_requests'])
    with col4:
        st.metric("Errors", stats['errors'], delta_color="inverse")
    
    # Display detailed results
    if st.session_state.attack_results:
        st.subheader("📋 Detailed Results")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.attack_results)
        
        # Add status interpretation
        df['Status'] = df.apply(lambda row: 
            '✅ Success' if row['status_code'] == 200 
            else '🚫 Blocked' if row['status_code'] == 403
            else '❌ Error' if row['status_code'] == 'ERROR'
            else f"⚠️ {row['status_code']}", axis=1)
        
        # Reorder columns
        display_columns = ['timestamp', 'username', 'password', 'Status', 'response']
        df_display = df[display_columns]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Show response analysis
        if len(df) > 0:
            st.subheader("📈 Response Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Status code distribution
                status_counts = df['status_code'].value_counts()
                st.bar_chart(status_counts)
                st.caption("Response Status Distribution")
            
            with col2:
                # Timeline of attempts
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df_timeline = df.set_index('timestamp').resample('1min').size()
                st.line_chart(df_timeline)
                st.caption("Attempts per Minute")
    else:
        st.info("No attack results yet. Start an attack to see results here.")

def main():
    """Main application function"""
    display_attack_header()
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
            <h1 style="color: white; margin: 0; font-size: 1.5rem;">⚔️</h1>
            <h3 style="color: white; margin: 0.2rem 0 0 0; font-weight: 300;">Attack Simulator</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚠️ Warning")
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="color: white; font-size: 0.85rem;">
                This tool is for <strong>authorized testing only</strong>. 
                Only use against systems you own or have explicit permission to test.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Quick Stats")
        stats = st.session_state.attack_stats
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem;">
            <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; line-height: 1.4;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span>Total Attempts</span>
                    <span style="font-weight: 600;">{stats['total_attempts']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span>Blocked</span>
                    <span style="font-weight: 600;">{stats['blocked_requests']}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Errors</span>
                    <span style="font-weight: 600;">{stats['errors']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    target_url = display_target_config()
    config_mode, attack_selection = display_attack_types()
    
    attack_config = {}
    attack_type = ""
    
    # Configure attack based on mode
    if config_mode == "Pre-configured":
        if attack_selection:
            scenario_data = get_scenario(attack_selection)
            attack_config = scenario_data
            attack_type = scenario_data["type"]
            
            st.markdown("### ✅ Ready to Launch")
            st.success(f"Scenario '{scenario_data['name']}' loaded and ready to execute.")
    else:
        # Custom attack configuration
        attack_type = attack_selection
        if attack_type == "Brute Force Attack":
            attack_config = configure_brute_force_attack()
        elif attack_type == "Dictionary Attack":
            attack_config = configure_dictionary_attack()
        elif attack_type == "Credential Stuffing":
            attack_config = configure_credential_stuffing()
        elif attack_type == "Volumetric Attack":
            attack_config = configure_volumetric_attack()
    
    # Attack controls and status
    if attack_config:
        display_attack_controls(target_url, attack_config, attack_type, config_mode)
        display_attack_status()
        display_attack_results()
    
    # Footer
    st.markdown("""
    ---
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        ⚔️ IDPS Attack Simulator | For authorized security testing only | 
        Last updated: {}
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
