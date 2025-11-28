import socket
import psutil
from utils.logger import log

def get_default_interface():
    """
    Tries to find the default network interface with an active gateway.
    Prioritizes Wi-Fi and Ethernet, ignores VPNs.
    """
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        
        # Keywords to avoid
        ignored_keywords = ['vpn', 'virtual', 'loopback', 'vmware', 'virtualbox', 'tap', 'tun']
        
        # 1. First pass: Look for active physical interfaces (Wi-Fi, Ethernet)
        for iface, stat in stats.items():
            if not stat.isup: continue
            
            lower_name = iface.lower()
            if any(k in lower_name for k in ignored_keywords):
                continue
                
            if iface in addrs:
                for addr in addrs[iface]:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        log.info(f"Detected active physical interface: {iface}")
                        return iface

        # 2. Second pass: If no physical found, accept anything with IP (fallback)
        for iface, stat in stats.items():
            if stat.isup and iface in addrs:
                for addr in addrs[iface]:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        log.warning(f"Using fallback interface (might be VPN): {iface}")
                        return iface
        
        log.error("No active network interface found.")
        return None
    except Exception as e:
        log.error(f"Error detecting interface: {e}")
        return None

def get_local_ip(iface):
    """
    Get IPv4 address of the specified interface.
    """
    try:
        addrs = psutil.net_if_addrs()
        if iface in addrs:
            for addr in addrs[iface]:
                if addr.family == socket.AF_INET:
                    return addr.address
    except Exception as e:
        log.error(f"Could not get IP for {iface}: {e}")
    return None

def get_network_range(ip, netmask):
    """
    Calculate CIDR from IP and Netmask (Simple implementation).
    For MVP we might just assume /24 if complex.
    """
    if ip:
        parts = ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    return None
