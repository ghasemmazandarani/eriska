"""
Scanner Tool Wrappers for LangGraph Agents

These tools wrap the existing Eriska scanner modules (discovery, fingerprint, analysis)
as LangGraph-compatible tools that agents can invoke.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.discovery import DiscoveryEngine
from core.fingerprint import FingerprintEngine
from core.analysis import RiskAnalyzer
from utils.network import get_default_interface, get_local_ip, get_network_range


# Singleton instances to avoid recreating
_discovery_engine: Optional[DiscoveryEngine] = None
_fingerprint_engine: Optional[FingerprintEngine] = None
_risk_analyzer: Optional[RiskAnalyzer] = None


def get_discovery_engine(iface: str = None) -> DiscoveryEngine:
    """Get or create a DiscoveryEngine singleton."""
    global _discovery_engine
    if _discovery_engine is None:
        if iface is None:
            iface = get_default_interface()
        _discovery_engine = DiscoveryEngine(iface)
    return _discovery_engine


def get_fingerprint_engine() -> FingerprintEngine:
    """Get or create a FingerprintEngine singleton."""
    global _fingerprint_engine
    if _fingerprint_engine is None:
        _fingerprint_engine = FingerprintEngine()
    return _fingerprint_engine


def get_risk_analyzer() -> RiskAnalyzer:
    """Get or create a RiskAnalyzer singleton."""
    global _risk_analyzer
    if _risk_analyzer is None:
        _risk_analyzer = RiskAnalyzer()
    return _risk_analyzer


@tool
def scan_network(network_range: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform an ARP network scan to discover devices on the local network.

    Args:
        network_range: Optional CIDR range (e.g., "192.168.1.0/24").
                      If not provided, auto-detects local network.

    Returns:
        Dictionary with scan results including discovered devices.
    """
    try:
        iface = get_default_interface()
        if not iface:
            return {"success": False, "error": "No network interface found"}

        if not network_range:
            local_ip = get_local_ip(iface)
            if not local_ip:
                return {"success": False, "error": "Could not determine local IP"}
            network_range = get_network_range(local_ip, "255.255.255.0")

        discovery = get_discovery_engine(iface)
        devices = discovery.scan_network(network_range)

        return {
            "success": True,
            "network_range": network_range,
            "device_count": len(devices),
            "devices": devices
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool
def scan_ports(target_ip: str, ports: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Scan specific ports on a target IP address.

    Args:
        target_ip: The IP address to scan.
        ports: Optional list of ports. Defaults to common IoT ports if not specified.

    Returns:
        Dictionary with open ports and service information.
    """
    try:
        discovery = get_discovery_engine()
        default_ports = [80, 443, 8080, 8081, 8000, 554, 22, 23, 21, 53, 445, 139, 3389, 1883]
        open_ports = discovery.scan_ports(target_ip, ports or default_ports)

        # Get service guesses for open ports
        fp_engine = get_fingerprint_engine()
        services = {}
        for port in open_ports:
            services[port] = fp_engine.guess_service(port)

        return {
            "success": True,
            "target_ip": target_ip,
            "open_ports": open_ports,
            "services": services,
            "port_count": len(open_ports)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool
def fingerprint_device(ip: str, mac: str, ports: List[int]) -> Dict[str, Any]:
    """
    Perform deep fingerprinting on a device to identify vendor, services, and vulnerabilities.

    Args:
        ip: Device IP address
        mac: Device MAC address
        ports: List of open ports to probe

    Returns:
        Fingerprint data including vendor, services, and risk indicators.
    """
    try:
        fp_engine = get_fingerprint_engine()

        result = {
            "ip": ip,
            "mac": mac,
            "vendor": fp_engine.lookup_oui(mac),
            "fingerprints": {},
            "risk_indicators": [],
            "device_type": "unknown"
        }

        # Probe HTTP ports
        for port in ports:
            if port in [80, 8080, 8000, 8081]:
                http_data = fp_engine.probe_http(ip, port, use_ssl=False)
                result["fingerprints"][f"http_{port}"] = http_data
                if http_data.get("risk_score", 0) > 0:
                    result["risk_indicators"].append(
                        f"HTTP risk on port {port}: vulnerable server signature detected"
                    )
                # Try to identify device type from title/server
                if http_data.get("title"):
                    title_lower = http_data["title"].lower()
                    if any(x in title_lower for x in ["camera", "dvr", "nvr", "ipc"]):
                        result["device_type"] = "camera"
                    elif any(x in title_lower for x in ["router", "gateway"]):
                        result["device_type"] = "router"

            elif port == 443:
                https_data = fp_engine.probe_http(ip, port, use_ssl=True)
                result["fingerprints"][f"https_{port}"] = https_data

        # Probe RTSP (common on cameras)
        if 554 in ports:
            rtsp_data = fp_engine.probe_rtsp(ip, 554)
            result["fingerprints"]["rtsp_554"] = rtsp_data
            if not rtsp_data.get("auth_needed", True):
                result["risk_indicators"].append("CRITICAL: RTSP stream has NO AUTHENTICATION")
            result["device_type"] = "camera"

        # Probe ONVIF (camera standard)
        if 80 in ports:
            onvif_data = fp_engine.probe_onvif(ip, 80)
            if onvif_data.get("is_onvif"):
                result["fingerprints"]["onvif"] = onvif_data
                result["device_type"] = "camera"
                if onvif_data.get("info"):
                    result["vendor"] = onvif_data["info"]

        # Probe SNMP
        snmp_data = fp_engine.probe_snmp(ip)
        if snmp_data.get("is_snmp"):
            result["fingerprints"]["snmp"] = snmp_data
            result["risk_indicators"].append("SNMP service responding (potential info disclosure)")

        # Probe SSDP/UPnP
        ssdp_data = fp_engine.probe_ssdp(ip)
        if ssdp_data.get("is_upnp"):
            result["fingerprints"]["ssdp"] = ssdp_data
            if ssdp_data.get("model"):
                result["model"] = ssdp_data["model"]
            if ssdp_data.get("info"):
                result["vendor"] = ssdp_data["info"]

        # Infer device type from vendor if not already set
        if result["device_type"] == "unknown":
            vendor_lower = result["vendor"].lower()
            if any(x in vendor_lower for x in ["hikvision", "dahua", "axis", "vivotek", "foscam"]):
                result["device_type"] = "camera"
            elif any(x in vendor_lower for x in ["tp-link", "netgear", "asus", "dlink", "linksys"]):
                result["device_type"] = "router"
            elif "raspberry" in vendor_lower:
                result["device_type"] = "iot_device"

        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool
def analyze_device_risk(device_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze security risks for a device based on its scan data.

    Args:
        device_data: Device information including ports, fingerprints, vendor.
                    Should contain: ports (list), fingerprints (dict), vendor (str)

    Returns:
        Risk score (0-100) and list of security issues.
    """
    try:
        analyzer = get_risk_analyzer()
        score, issues = analyzer.analyze(device_data)

        risk_level = "LOW"
        if score > 70:
            risk_level = "CRITICAL"
        elif score > 50:
            risk_level = "HIGH"
        elif score > 30:
            risk_level = "MEDIUM"

        return {
            "success": True,
            "risk_score": score,
            "risk_level": risk_level,
            "issues": issues,
            "issue_count": len(issues)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool
def get_network_info() -> Dict[str, Any]:
    """
    Get information about the local network configuration.

    Returns:
        Network interface, local IP, and suggested scan range.
    """
    try:
        iface = get_default_interface()
        if not iface:
            return {"success": False, "error": "No network interface found"}

        local_ip = get_local_ip(iface)
        if not local_ip:
            return {"success": False, "error": "Could not determine local IP"}

        network_range = get_network_range(local_ip, "255.255.255.0")

        return {
            "success": True,
            "interface": iface,
            "local_ip": local_ip,
            "network_range": network_range,
            "subnet_mask": "255.255.255.0"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Export all tools
SCANNER_TOOLS = [
    scan_network,
    scan_ports,
    fingerprint_device,
    analyze_device_risk,
    get_network_info
]
