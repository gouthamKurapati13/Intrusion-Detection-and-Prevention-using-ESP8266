"""
Attack Test Scenarios - Pre-configured attack patterns for testing
"""

# Common attack scenarios for IDPS testing
ATTACK_SCENARIOS = {
    "basic_brute_force": {
        "name": "Basic Brute Force",
        "description": "Simple brute force attack with common credentials - A straightforward attack simulation that systematically tries common username and password combinations. This attack tests the most basic security weakness by attempting obvious credentials like 'admin/password' and 'root/123456'. Perfect for initial security testing and validation of basic protection mechanisms.",
        "type": "brute_force",
        "usernames": ["admin", "root", "user", "guest"],
        "passwords": ["password", "123456", "admin", "root"],
        "delay": 1.0,
        "max_threads": 3,
        "detailed_info": {
            "attack_method": "Systematic credential enumeration",
            "purpose": "Basic security validation",
            "intensity": "Low to Medium",
            "detection_difficulty": "Easy - uses common patterns",
            "typical_use": "Initial security testing and baseline validation"
        }
    },
    
    "advanced_brute_force": {
        "name": "Advanced Brute Force",
        "description": "Comprehensive brute force with extended wordlists",
        "type": "brute_force", 
        "usernames": [
            "admin", "administrator", "root", "user", "guest", "test",
            "demo", "support", "service", "operator", "manager", "staff",
            "login", "web", "www", "ftp", "mail", "email", "sa", "oracle",
            "postgres", "mysql", "tomcat", "jenkins", "gitlab", "jira"
        ],
        "passwords": [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890", "abc123",
            "Password1", "password1", "root", "toor", "pass", "test",
            "12345", "dragon", "master", "shadow", "login", "admin123",
            "passw0rd", "p@ssw0rd", "P@ssword1", "Welcome1", "Password!",
            "secret", "changeme", "default", "guest", "demo"
        ],
        "delay": 0.5,
        "max_threads": 5
    },
    
    "targeted_dictionary": {
        "name": "Targeted Dictionary Attack",
        "description": "Dictionary attack focused on admin account - A focused attack simulation that targets a specific user account (typically 'admin') with an extensive list of common passwords. This attack mimics real-world scenarios where attackers have identified a valid username and systematically try various passwords from leaked password databases and common password lists.",
        "type": "dictionary",
        "target_username": "admin",
        "password_list": [
            "admin", "password", "123456", "admin123", "administrator",
            "passw0rd", "p@ssw0rd", "welcome", "letmein", "changeme",
            "default", "secret", "password1", "Password1", "admin1",
            "root", "toor", "guest", "test", "demo", "service"
        ],
        "delay": 0.3,
        "detailed_info": {
            "attack_method": "Focused password enumeration on known username",
            "purpose": "Account-specific security testing",
            "intensity": "Medium",
            "detection_difficulty": "Moderate - focused on single account",
            "typical_use": "Testing password policies and account lockout mechanisms"
        }
    },
    
    "credential_stuffing_basic": {
        "name": "Basic Credential Stuffing",
        "description": "Common username/password combinations",
        "type": "credential_stuffing",
        "credential_pairs": [
            ("admin", "admin"),
            ("admin", "password"),
            ("administrator", "administrator"),
            ("root", "root"),
            ("root", "toor"),
            ("user", "user"),
            ("guest", "guest"),
            ("test", "test"),
            ("demo", "demo"),
            ("service", "service")
        ],
        "delay": 0.5
    },
    
    "credential_stuffing_extended": {
        "name": "Extended Credential Stuffing",
        "description": "Extensive list of leaked credential pairs",
        "type": "credential_stuffing",
        "credential_pairs": [
            ("admin", "admin"), ("admin", "password"), ("admin", "123456"),
            ("administrator", "administrator"), ("administrator", "password"),
            ("root", "root"), ("root", "toor"), ("root", "password"),
            ("user", "user"), ("user", "password"), ("user", "123456"),
            ("guest", "guest"), ("guest", "password"),
            ("test", "test"), ("test", "password"), ("test", "123456"),
            ("demo", "demo"), ("demo", "password"),
            ("service", "service"), ("operator", "operator"),
            ("support", "support"), ("manager", "manager"),
            ("sa", "sa"), ("oracle", "oracle"), ("postgres", "postgres"),
            ("mysql", "mysql"), ("tomcat", "tomcat"), ("jenkins", "jenkins")
        ],
        "delay": 0.3
    },
    
    "low_volume_test": {
        "name": "Low Volume Test",
        "description": "Gentle testing for baseline measurements - A controlled, low-intensity attack simulation that sends a small number of login attempts at a slow pace. This test is designed to establish baseline performance metrics without overwhelming the target system. Perfect for initial testing of detection capabilities and system response times.",
        "type": "volumetric",
        "username": "testuser",
        "password": "testpass",
        "num_requests": 20,
        "delay": 2.0,
        "detailed_info": {
            "attack_method": "Low-frequency volumetric testing",
            "purpose": "Baseline measurement and initial system testing",
            "intensity": "Very Low",
            "detection_difficulty": "Easy to detect due to slow pace",
            "typical_use": "System validation and performance baseline establishment"
        }
    },
    
    "medium_volume_test": {
        "name": "Medium Volume Test", 
        "description": "Moderate load testing - A balanced attack simulation that tests system performance under moderate stress. This scenario sends a medium number of login attempts at a moderate pace to evaluate how well the IDPS handles sustained attack traffic. Useful for testing rate limiting and detection accuracy under realistic attack conditions.",
        "type": "volumetric",
        "username": "attacker",
        "password": "password",
        "num_requests": 100,
        "delay": 0.5,
        "detailed_info": {
            "attack_method": "Medium-frequency volumetric testing",
            "purpose": "Performance testing under moderate load",
            "intensity": "Medium",
            "detection_difficulty": "Moderate - balanced between stealth and speed",
            "typical_use": "Realistic attack simulation and performance validation"
        }
    },
    
    "high_volume_test": {
        "name": "High Volume Test",
        "description": "Stress testing for rate limiting - An aggressive, high-intensity attack simulation designed to test the system's ability to handle and block large volumes of rapid login attempts. This scenario simulates a bot-driven attack with many requests sent in quick succession to validate rate limiting, DDoS protection, and system stability under extreme load conditions.",
        "type": "volumetric", 
        "username": "bot",
        "password": "automated",
        "num_requests": 500,
        "delay": 0.1,
        "detailed_info": {
            "attack_method": "High-frequency volumetric flooding",
            "purpose": "Stress testing and DDoS simulation",
            "intensity": "Very High",
            "detection_difficulty": "Easy to detect due to high volume",
            "typical_use": "Rate limiting validation and system stress testing"
        }
    },
    
    "stealth_attack": {
        "name": "Stealth Attack",
        "description": "Slow, low-profile attack to evade detection",
        "type": "brute_force",
        "usernames": ["admin", "user", "guest"],
        "passwords": ["password", "123456", "admin"],
        "delay": 5.0,
        "max_threads": 1
    },
    
    "rapid_fire": {
        "name": "Rapid Fire Attack",
        "description": "Fast attack to trigger immediate blocking",
        "type": "brute_force",
        "usernames": ["admin"],
        "passwords": ["password", "123456", "admin", "root", "test"],
        "delay": 0.1,
        "max_threads": 10
    }
}

# Password lists for different attack types
PASSWORD_LISTS = {
    "common": [
        "password", "123456", "password123", "admin", "qwerty",
        "letmein", "welcome", "monkey", "abc123", "Password1"
    ],
    
    "rockyou_top20": [
        "123456", "password", "12345678", "qwerty", "123456789",
        "12345", "1234", "111111", "1234567", "dragon",
        "123123", "baseball", "abc123", "football", "monkey",
        "letmein", "696969", "shadow", "master", "666666"
    ],
    
    "weak_passwords": [
        "password", "123456", "qwerty", "abc123", "monkey",
        "12345", "letmein", "dragon", "111111", "baseball",
        "iloveyou", "trustno1", "1234567", "sunshine", "master"
    ],
    
    "admin_focused": [
        "admin", "administrator", "password", "admin123", "root",
        "passw0rd", "p@ssw0rd", "welcome", "changeme", "default",
        "secret", "guest", "toor", "service", "manager"
    ],
    
    "numeric": [
        "123456", "1234567", "12345678", "123456789", "1234567890",
        "12345", "1234", "123", "111111", "000000",
        "654321", "987654321", "102030", "112233", "121212"
    ]
}

# Username lists for different scenarios
USERNAME_LISTS = {
    "common": [
        "admin", "administrator", "root", "user", "guest",
        "test", "demo", "support", "service", "operator"
    ],
    
    "system_accounts": [
        "root", "admin", "administrator", "sa", "system",
        "service", "daemon", "operator", "manager", "supervisor"
    ],
    
    "web_services": [
        "admin", "webadmin", "web", "www", "apache", "nginx",
        "tomcat", "jenkins", "gitlab", "jira", "confluence"
    ],
    
    "database": [
        "sa", "admin", "root", "oracle", "postgres", "mysql",
        "mongodb", "redis", "elastic", "kibana", "grafana"
    ],
    
    "email_services": [
        "admin", "postmaster", "mail", "email", "smtp",
        "imap", "pop3", "exchange", "outlook", "webmail"
    ]
}

def get_scenario(scenario_name):
    """Get a specific attack scenario by name"""
    return ATTACK_SCENARIOS.get(scenario_name)

def get_all_scenarios():
    """Get all available attack scenarios"""
    return ATTACK_SCENARIOS

def get_password_list(list_name):
    """Get a specific password list by name"""
    return PASSWORD_LISTS.get(list_name, PASSWORD_LISTS["common"])

def get_username_list(list_name):
    """Get a specific username list by name"""
    return USERNAME_LISTS.get(list_name, USERNAME_LISTS["common"])

def get_scenario_names():
    """Get list of all scenario names"""
    return list(ATTACK_SCENARIOS.keys())

def get_scenario_description(scenario_name):
    """Get description of a specific scenario"""
    scenario = ATTACK_SCENARIOS.get(scenario_name)
    return scenario["description"] if scenario else "Unknown scenario"
