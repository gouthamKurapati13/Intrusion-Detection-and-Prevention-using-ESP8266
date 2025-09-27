"""
Attack simulation utility for testing IDPS
"""
import requests
import time
import random
from datetime import datetime
from config.settings import (
    SERVER_HOST, SERVER_PORT, 
    ATTACK_USERNAMES, ATTACK_PASSWORDS, ATTACK_DELAY
)
from src.core.logger import get_logger

logger = get_logger(__name__)

class AttackSimulator:
    """Simulates various types of attacks for testing IDPS"""
    
    def __init__(self, target_host=None, target_port=None):
        self.target_host = target_host or SERVER_HOST
        self.target_port = target_port or SERVER_PORT
        self.base_url = f"http://{self.target_host}:{self.target_port}"
        self.session = requests.Session()
        
        logger.info(f"Attack simulator initialized for {self.base_url}")
    
    def check_server(self):
        """Check if the target server is reachable"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def brute_force_attack(self, num_attempts=50, delay=None):
        """Simulate a brute force attack"""
        if delay is None:
            delay = ATTACK_DELAY
        
        logger.info(f"🔥 Starting brute force attack with {num_attempts} attempts")
        logger.info(f"Target: {self.base_url}/login")
        
        successful_attempts = 0
        failed_attempts = 0
        
        for i in range(num_attempts):
            username = random.choice(ATTACK_USERNAMES)
            password = random.choice(ATTACK_PASSWORDS)
            
            try:
                response = self.session.post(
                    f"{self.base_url}/login",
                    data={"username": username, "password": password},
                    timeout=10
                )
                
                if response.status_code == 403:
                    logger.warning(f"🚫 IP blocked after {i+1} attempts")
                    break
                elif response.status_code == 401:
                    failed_attempts += 1
                    logger.debug(f"Attempt {i+1}: {username}:{password} → {response.status_code}")
                else:
                    successful_attempts += 1
                    logger.info(f"Unexpected response: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                failed_attempts += 1
            
            # Add delay between attempts
            if delay > 0:
                time.sleep(delay)
        
        logger.info(f"Attack completed: {successful_attempts} successful, {failed_attempts} failed")
        return successful_attempts, failed_attempts
    
    def credential_stuffing_attack(self, credentials_list=None, delay=None):
        """Simulate credential stuffing attack with specific username/password combinations"""
        if delay is None:
            delay = ATTACK_DELAY
        
        if credentials_list is None:
            # Default credential combinations
            credentials_list = [
                ("admin", "admin"),
                ("admin", "password"),
                ("admin", "123456"),
                ("root", "root"),
                ("root", "toor"),
                ("administrator", "administrator"),
                ("test", "test"),
                ("guest", "guest"),
                ("user", "user"),
                ("admin", ""),
            ]
        
        logger.info(f"🎯 Starting credential stuffing attack with {len(credentials_list)} combinations")
        
        successful_attempts = 0
        failed_attempts = 0
        
        for i, (username, password) in enumerate(credentials_list):
            try:
                response = self.session.post(
                    f"{self.base_url}/login",
                    data={"username": username, "password": password},
                    timeout=10
                )
                
                if response.status_code == 403:
                    logger.warning(f"🚫 IP blocked after {i+1} attempts")
                    break
                elif response.status_code == 401:
                    failed_attempts += 1
                    logger.debug(f"Attempt {i+1}: {username}:{password} → Failed")
                else:
                    successful_attempts += 1
                    logger.info(f"Attempt {i+1}: {username}:{password} → Unexpected: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                failed_attempts += 1
            
            if delay > 0:
                time.sleep(delay)
        
        logger.info(f"Credential stuffing completed: {successful_attempts} successful, {failed_attempts} failed")
        return successful_attempts, failed_attempts
    
    def slow_attack(self, num_attempts=20, min_delay=5, max_delay=30):
        """Simulate a slow, stealthy attack to test detection over time"""
        logger.info(f"🐌 Starting slow attack with {num_attempts} attempts")
        logger.info(f"Delay range: {min_delay}-{max_delay} seconds")
        
        successful_attempts = 0
        failed_attempts = 0
        
        for i in range(num_attempts):
            username = random.choice(ATTACK_USERNAMES)
            password = random.choice(ATTACK_PASSWORDS)
            
            try:
                response = self.session.post(
                    f"{self.base_url}/login",
                    data={"username": username, "password": password},
                    timeout=10
                )
                
                if response.status_code == 403:
                    logger.warning(f"🚫 IP blocked after {i+1} attempts")
                    break
                elif response.status_code == 401:
                    failed_attempts += 1
                    logger.debug(f"Slow attempt {i+1}: {username}:{password}")
                else:
                    successful_attempts += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                failed_attempts += 1
            
            # Random delay between attempts
            delay = random.uniform(min_delay, max_delay)
            logger.info(f"Waiting {delay:.1f} seconds before next attempt...")
            time.sleep(delay)
        
        logger.info(f"Slow attack completed: {successful_attempts} successful, {failed_attempts} failed")
        return successful_attempts, failed_attempts
    
    def mixed_attack(self):
        """Simulate a mixed attack pattern"""
        logger.info("🎭 Starting mixed attack simulation")
        
        # Start with some legitimate-looking attempts
        logger.info("Phase 1: Legitimate-looking attempts")
        legit_credentials = [
            ("john.doe", "WrongPassword123"),
            ("jane.smith", "OldPassword456"),
            ("alice.brown", "ForgottenPass789")
        ]
        
        for username, password in legit_credentials:
            try:
                response = self.session.post(
                    f"{self.base_url}/login",
                    data={"username": username, "password": password},
                    timeout=10
                )
                logger.debug(f"Legit attempt: {username} → {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
            
            time.sleep(2)
        
        # Then escalate to brute force
        logger.info("Phase 2: Escalating to brute force")
        self.brute_force_attack(num_attempts=25, delay=0.5)

def run_simulation(attack_type="brute_force", **kwargs):
    """Run attack simulation"""
    simulator = AttackSimulator()
    
    # Check if server is running
    if not simulator.check_server():
        logger.error("❌ Target server is not reachable!")
        logger.error(f"Make sure the server is running at {simulator.base_url}")
        return False
    
    logger.info(f"✅ Server is reachable at {simulator.base_url}")
    
    try:
        if attack_type == "brute_force":
            return simulator.brute_force_attack(**kwargs)
        elif attack_type == "credential_stuffing":
            return simulator.credential_stuffing_attack(**kwargs)
        elif attack_type == "slow":
            return simulator.slow_attack(**kwargs)
        elif attack_type == "mixed":
            return simulator.mixed_attack()
        else:
            logger.error(f"Unknown attack type: {attack_type}")
            return False
    except KeyboardInterrupt:
        logger.info("👋 Attack simulation stopped by user")
        return False
    except Exception as e:
        logger.error(f"Error during attack simulation: {e}")
        return False

def main():
    """Main function for attack simulation"""
    logger.info("⚔️  IDPS Attack Simulation Tool")
    logger.info("=" * 50)
    
    import argparse
    
    parser = argparse.ArgumentParser(description="IDPS Attack Simulation Tool")
    parser.add_argument(
        "--type", 
        choices=["brute_force", "credential_stuffing", "slow", "mixed"],
        default="brute_force",
        help="Type of attack to simulate"
    )
    parser.add_argument(
        "--attempts", 
        type=int, 
        default=50,
        help="Number of attempts (for brute force and slow attacks)"
    )
    parser.add_argument(
        "--delay", 
        type=float, 
        default=0.5,
        help="Delay between attempts in seconds"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Target host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Target port"
    )
    
    args = parser.parse_args()
    
    # Set up simulator with custom host/port if provided
    if args.host != "127.0.0.1" or args.port != 5000:
        global SERVER_HOST, SERVER_PORT
        SERVER_HOST = args.host
        SERVER_PORT = args.port
    
    logger.info(f"Attack type: {args.type}")
    logger.info(f"Target: http://{args.host}:{args.port}")
    
    if args.type in ["brute_force", "slow"]:
        logger.info(f"Attempts: {args.attempts}")
    
    logger.info(f"Delay: {args.delay}s")
    logger.info("-" * 50)
    
    # Run the simulation
    result = run_simulation(
        attack_type=args.type,
        num_attempts=args.attempts,
        delay=args.delay
    )
    
    if result:
        logger.info("\n✅ Attack simulation completed!")
        logger.info("Check the dashboard to see the detection results.")
    else:
        logger.error("\n❌ Attack simulation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
