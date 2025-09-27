"""
IP management utilities for blocking and unblocking IPs
"""
import os
from pathlib import Path
from typing import List, Set
from config.settings import BLOCKED_IPS_FILE
from src.core.logger import get_logger

logger = get_logger(__name__)

class IPManager:
    """Manages IP blocking and unblocking operations"""
    
    def __init__(self):
        self.blocked_ips_file = BLOCKED_IPS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the blocked IPs file exists"""
        if not self.blocked_ips_file.exists():
            self.blocked_ips_file.touch()
            logger.info(f"Created blocked IPs file: {self.blocked_ips_file}")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP address is blocked"""
        try:
            with open(self.blocked_ips_file, 'r') as f:
                blocked_ips = set(line.strip() for line in f if line.strip())
                return ip in blocked_ips
        except FileNotFoundError:
            logger.warning(f"Blocked IPs file not found: {self.blocked_ips_file}")
            return False
        except Exception as e:
            logger.error(f"Error checking blocked IP {ip}: {e}")
            return False
    
    def block_ip(self, ip: str) -> bool:
        """Block an IP address"""
        try:
            if self.is_ip_blocked(ip):
                logger.info(f"IP {ip} is already blocked")
                return True
            
            with open(self.blocked_ips_file, 'a') as f:
                f.write(f"{ip}\n")
            
            logger.info(f"Blocked IP: {ip}")
            return True
        except Exception as e:
            logger.error(f"Error blocking IP {ip}: {e}")
            return False
    
    def unblock_ip(self, ip: str) -> bool:
        """Unblock a specific IP address"""
        try:
            blocked_ips = self.get_blocked_ips()
            if ip not in blocked_ips:
                logger.info(f"IP {ip} is not blocked")
                return True
            
            blocked_ips.remove(ip)
            self._write_blocked_ips(blocked_ips)
            logger.info(f"Unblocked IP: {ip}")
            return True
        except Exception as e:
            logger.error(f"Error unblocking IP {ip}: {e}")
            return False
    
    def unblock_all_ips(self) -> bool:
        """Unblock all IP addresses"""
        try:
            with open(self.blocked_ips_file, 'w') as f:
                f.write("")
            logger.info("Unblocked all IPs")
            return True
        except Exception as e:
            logger.error(f"Error unblocking all IPs: {e}")
            return False
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of all blocked IP addresses"""
        try:
            with open(self.blocked_ips_file, 'r') as f:
                # Remove duplicates while preserving order
                blocked_ips = []
                seen = set()
                for line in f:
                    ip = line.strip()
                    if ip and ip not in seen:
                        blocked_ips.append(ip)
                        seen.add(ip)
                return blocked_ips
        except FileNotFoundError:
            logger.warning(f"Blocked IPs file not found: {self.blocked_ips_file}")
            return []
        except Exception as e:
            logger.error(f"Error reading blocked IPs: {e}")
            return []
    
    def _write_blocked_ips(self, ips: List[str]):
        """Write list of IPs to blocked IPs file"""
        with open(self.blocked_ips_file, 'w') as f:
            for ip in ips:
                f.write(f"{ip}\n")
    
    def get_blocked_count(self) -> int:
        """Get count of unique blocked IPs"""
        return len(set(self.get_blocked_ips()))
    
    def cleanup_duplicates(self):
        """Remove duplicate entries from blocked IPs file"""
        try:
            unique_ips = list(set(self.get_blocked_ips()))
            self._write_blocked_ips(unique_ips)
            logger.info(f"Cleaned up blocked IPs file, removed duplicates")
        except Exception as e:
            logger.error(f"Error cleaning up blocked IPs: {e}")

# Global IP manager instance
ip_manager = IPManager()
