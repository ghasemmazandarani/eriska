"""
Security Knowledge Base Tools for LangGraph Agents

These tools provide access to security data:
- CVE Database (local JSON index)
- OUI Device Fingerprints (MAC vendor lookup)
- MITRE ATT&CK Patterns
- Remediation Guidance
"""

import json
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

from .local_database import get_database


@tool
def search_cve_by_device(
    vendor: str,
    product: Optional[str] = None,
    firmware_version: Optional[str] = None,
    min_cvss: float = 0.0
) -> str:
    """
    Search the CVE database for vulnerabilities affecting a specific device.

    Args:
        vendor: Device vendor name (e.g., "Hikvision", "Dahua", "TP-Link")
        product: Optional product/model name (e.g., "DS-2CD2032")
        firmware_version: Optional firmware version (for context, not strict matching)
        min_cvss: Minimum CVSS score threshold (0.0 to 10.0)

    Returns:
        JSON string with matching CVEs including:
        - cve_id, description, cvss_score, severity
        - affected_versions, remediation guidance
    """
    db = get_database()

    # Search CVEs
    cves = db.search_cve(
        vendor=vendor,
        product=product,
        min_cvss=min_cvss,
        max_results=15
    )

    if not cves:
        return json.dumps({
            "success": True,
            "query": f"vendor={vendor}, product={product}, min_cvss={min_cvss}",
            "count": 0,
            "cves": [],
            "message": f"No CVEs found for vendor '{vendor}' matching criteria. "
                      "This may mean the device is not in our CVE database or has no known vulnerabilities."
        }, indent=2)

    # Format results
    formatted_cves = []
    for cve in cves:
        formatted = {
            "cve_id": cve['cve_id'],
            "description": cve.get('description', '')[:500],  # Truncate long descriptions
            "cvss_score": cve.get('cvss_score', 0),
            "severity": cve.get('severity', 'UNKNOWN'),
            "affected_products": [
                f"{item.get('vendor', '')} {item.get('product', '')}"
                for item in cve.get('affected', [])[:5]
            ],
            "remediation": cve.get('remediation', 'Check vendor website for patches.')
        }
        formatted_cves.append(formatted)

    return json.dumps({
        "success": True,
        "query": f"vendor={vendor}, product={product}, min_cvss={min_cvss}",
        "count": len(formatted_cves),
        "cves": formatted_cves
    }, indent=2)


@tool
def identify_device_from_fingerprint(
    mac_prefix: Optional[str] = None,
    http_server: Optional[str] = None,
    http_title: Optional[str] = None,
    open_ports: Optional[List[int]] = None,
    banners: Optional[Dict[str, str]] = None
) -> str:
    """
    Identify a device type, vendor, and model from scan fingerprints.

    Combines OUI lookup with signature matching for device identification.

    Args:
        mac_prefix: First 3 octets of MAC address (e.g., "C4:2F:90")
        http_server: HTTP Server header value
        http_title: HTML page title
        open_ports: List of open ports
        banners: Service banners (e.g., {"rtsp": "HiIpcam...", "telnet": "..."})

    Returns:
        JSON with device identification:
        - vendor, device_type, confidence score
        - known security issues for this device type
    """
    db = get_database()

    result = {
        "vendor": "Unknown",
        "device_type": "unknown",
        "model": None,
        "confidence": 0.0,
        "known_issues": []
    }

    # MAC prefix identification (OUI lookup)
    if mac_prefix:
        vendor = db.lookup_vendor(mac_prefix)
        if vendor:
            result["vendor"] = vendor
            result["confidence"] = 0.85

            # Infer device type from vendor
            vendor_lower = vendor.lower()
            if any(x in vendor_lower for x in ['hikvision', 'dahua', 'axis', 'foscam', 'amcrest', 'reolink', 'vivotek']):
                result["device_type"] = "camera"
                result["confidence"] = 0.9
            elif any(x in vendor_lower for x in ['tp-link', 'netgear', 'd-link', 'asus', 'linksys', 'ubiquiti', 'mikrotik']):
                result["device_type"] = "router"
                result["confidence"] = 0.9
            elif any(x in vendor_lower for x in ['synology', 'qnap', 'western digital', 'seagate']):
                result["device_type"] = "nas"
                result["confidence"] = 0.9
            elif any(x in vendor_lower for x in ['raspberry', 'espressif', 'arduino']):
                result["device_type"] = "iot_device"
                result["confidence"] = 0.85
            elif any(x in vendor_lower for x in ['cisco', 'juniper', 'arista', 'huawei']):
                result["device_type"] = "networking"
                result["confidence"] = 0.9

    # HTTP signature identification (supplements OUI)
    if http_server:
        server_lower = http_server.lower()
        http_signatures = {
            'hikvision': ('Hikvision', 'camera', 0.95),
            'dahua': ('Dahua', 'camera', 0.95),
            'dvrdvs': ('Generic DVR', 'camera', 0.8),
            'tp-link': ('TP-Link', 'router', 0.9),
            'netgear': ('NETGEAR', 'router', 0.9),
            'boa': ('Embedded Linux', 'iot_device', 0.7),
            'rompager': ('Embedded', 'iot_device', 0.7),
            'mini_httpd': ('Embedded', 'iot_device', 0.7),
            'synology': ('Synology', 'nas', 0.95),
        }
        for sig, (vendor, dev_type, conf) in http_signatures.items():
            if sig in server_lower:
                if conf > result["confidence"]:
                    result["vendor"] = vendor
                    result["device_type"] = dev_type
                    result["confidence"] = conf

    # Title-based identification
    if http_title:
        title_lower = http_title.lower()
        if any(x in title_lower for x in ['camera', 'dvr', 'nvr', 'ipc', 'video']):
            result["device_type"] = "camera"
        elif any(x in title_lower for x in ['router', 'gateway', 'admin', 'management']):
            if result["device_type"] == "unknown":
                result["device_type"] = "router"

    # Port-based identification and security issues
    if open_ports:
        port_info = {
            554: ("RTSP port open", "camera"),
            8554: ("Alternate RTSP port open", "camera"),
            37777: ("Dahua protocol port open", "camera"),
            23: ("Telnet open - insecure protocol, check for default credentials", None),
            22: ("SSH open - verify strong authentication", None),
            445: ("SMB open - potential ransomware/lateral movement target", None),
            139: ("NetBIOS open - potential enumeration target", None),
            21: ("FTP open - check for anonymous access", None),
            80: ("HTTP open - check for web vulnerabilities", None),
            443: ("HTTPS open", None),
            8080: ("Alternate HTTP port open", None),
            5000: ("Synology DSM or similar service", "nas"),
            5001: ("Synology DSM HTTPS", "nas"),
            8443: ("HTTPS management interface", None),
        }

        for port in open_ports:
            if port in port_info:
                issue, inferred_type = port_info[port]
                if "insecure" in issue.lower() or "default" in issue.lower() or "potential" in issue.lower():
                    result["known_issues"].append(issue)
                if inferred_type and result["device_type"] == "unknown":
                    result["device_type"] = inferred_type

    # Banner analysis
    if banners:
        for service, banner in banners.items():
            banner_lower = banner.lower()
            if 'hikvision' in banner_lower or 'hipcam' in banner_lower:
                result["vendor"] = "Hikvision"
                result["device_type"] = "camera"
                result["confidence"] = max(result["confidence"], 0.9)
            elif 'dahua' in banner_lower:
                result["vendor"] = "Dahua"
                result["device_type"] = "camera"
                result["confidence"] = max(result["confidence"], 0.9)

    return json.dumps({
        "success": True,
        "identification": result
    }, indent=2)


@tool
def get_attack_patterns(
    device_type: str,
    vulnerabilities: List[str],
    network_position: str = "internal"
) -> str:
    """
    Get relevant attack patterns for constructing attack path scenarios.

    Retrieves MITRE ATT&CK patterns relevant to the device type and vulnerabilities.

    Args:
        device_type: Type of device (camera, router, iot_sensor, nas, etc.)
        vulnerabilities: List of CVE IDs or vulnerability types found
        network_position: Device's network position (gateway, internal, dmz)

    Returns:
        JSON with attack patterns including:
        - MITRE ATT&CK technique IDs and names
        - Attack sequence steps
        - Prerequisites and impact
    """
    db = get_database()

    # Map device types to relevant tactics
    device_tactics = {
        'camera': ['initial-access', 'collection', 'command-and-control'],
        'router': ['initial-access', 'lateral-movement', 'command-and-control', 'impact'],
        'nas': ['initial-access', 'collection', 'exfiltration', 'impact'],
        'iot_device': ['initial-access', 'persistence', 'command-and-control'],
        'workstation': ['initial-access', 'execution', 'persistence', 'privilege-escalation'],
    }

    tactics = device_tactics.get(device_type.lower(), ['initial-access', 'persistence'])

    # Get ATT&CK patterns
    attack_patterns = db.get_attack_patterns(
        device_type=device_type,
        tactics=tactics,
        max_results=10
    )

    # Format results
    formatted_patterns = []
    for pattern in attack_patterns:
        formatted = {
            "mitre_id": pattern['id'],
            "name": pattern['name'],
            "description": pattern.get('description', '')[:300],
            "tactics": pattern.get('tactics', []),
            "platforms": pattern.get('platforms', [])
        }
        formatted_patterns.append(formatted)

    # Add IoT-specific attack patterns
    iot_patterns = _get_iot_specific_patterns(device_type, network_position, vulnerabilities)
    formatted_patterns.extend(iot_patterns)

    return json.dumps({
        "success": True,
        "device_type": device_type,
        "network_position": network_position,
        "vulnerability_context": vulnerabilities[:5] if vulnerabilities else [],
        "pattern_count": len(formatted_patterns),
        "patterns": formatted_patterns
    }, indent=2)


def _get_iot_specific_patterns(
    device_type: str,
    network_position: str,
    vulnerabilities: List[str]
) -> List[Dict]:
    """Generate IoT-specific attack patterns based on context."""
    patterns = []

    # Common IoT attack patterns
    if device_type in ('camera', 'dvr', 'nvr'):
        patterns.append({
            "mitre_id": "T1190",
            "name": "Exploit Public-Facing Application",
            "description": "Exploit web interface vulnerabilities common in IP cameras",
            "tactics": ["initial-access"],
            "steps": [
                "Identify camera web interface",
                "Test for known CVEs (authentication bypass, command injection)",
                "Exploit vulnerability to gain shell access or admin control"
            ]
        })
        patterns.append({
            "mitre_id": "T1078",
            "name": "Default Credentials",
            "description": "IP cameras often ship with known default credentials",
            "tactics": ["initial-access", "persistence"],
            "steps": [
                "Identify login interface",
                "Test vendor-specific default credentials",
                "Gain administrative access"
            ]
        })

    if device_type == 'router' or network_position == 'gateway':
        patterns.append({
            "mitre_id": "T1557",
            "name": "Adversary-in-the-Middle",
            "description": "Compromised router enables traffic interception",
            "tactics": ["collection", "credential-access"],
            "steps": [
                "Gain router administrative access",
                "Modify DNS settings or enable traffic mirroring",
                "Capture credentials and sensitive data"
            ]
        })
        patterns.append({
            "mitre_id": "T1570",
            "name": "Lateral Tool Transfer",
            "description": "Use compromised gateway for internal network pivot",
            "tactics": ["lateral-movement"],
            "steps": [
                "Establish foothold on gateway device",
                "Enumerate internal network from gateway",
                "Transfer tools and pivot to internal targets"
            ]
        })

    # Add vulnerability-specific patterns
    vuln_has_rce = any('injection' in v.lower() or 'rce' in v.lower() or 'remote code' in v.lower()
                       for v in vulnerabilities)
    vuln_has_auth_bypass = any('bypass' in v.lower() or 'authentication' in v.lower()
                               for v in vulnerabilities)

    if vuln_has_rce:
        patterns.append({
            "mitre_id": "T1059",
            "name": "Command and Scripting Interpreter",
            "description": "RCE vulnerability enables arbitrary command execution",
            "tactics": ["execution"],
            "steps": [
                "Exploit command injection vulnerability",
                "Execute system commands on target",
                "Establish persistent backdoor"
            ]
        })

    if vuln_has_auth_bypass:
        patterns.append({
            "mitre_id": "T1556",
            "name": "Modify Authentication Process",
            "description": "Authentication bypass enables unauthorized access",
            "tactics": ["credential-access", "defense-evasion"],
            "steps": [
                "Exploit authentication bypass",
                "Access protected functionality",
                "Create backdoor account or modify authentication"
            ]
        })

    return patterns


@tool
def get_remediation(
    cve_ids: Optional[List[str]] = None,
    device_type: Optional[str] = None,
    issues: Optional[List[str]] = None
) -> str:
    """
    Get remediation guidance for identified vulnerabilities and security issues.

    Args:
        cve_ids: List of CVE IDs to get remediation for
        device_type: Type of device for device-specific guidance
        issues: List of security issues (e.g., "default credentials", "telnet open")

    Returns:
        JSON with prioritized remediation steps
    """
    db = get_database()
    remediation_steps = []

    # Get CVE-specific remediation from database
    if cve_ids:
        for cve_id in cve_ids:
            cve = db.get_cve_by_id(cve_id)
            if cve and cve.get('remediation'):
                remediation_steps.append({
                    "priority": _severity_to_priority(cve.get('severity', 'UNKNOWN')),
                    "title": f"Fix {cve_id}",
                    "related_cve": cve_id,
                    "cvss_score": cve.get('cvss_score', 0),
                    "steps": [cve['remediation']],
                    "effort": "Moderate"
                })
            elif cve:
                # Generic remediation for CVE without specific guidance
                remediation_steps.append({
                    "priority": _severity_to_priority(cve.get('severity', 'UNKNOWN')),
                    "title": f"Address {cve_id}",
                    "related_cve": cve_id,
                    "cvss_score": cve.get('cvss_score', 0),
                    "steps": [
                        "Check vendor website for security patches",
                        "Update firmware to latest version",
                        "If no patch available, consider network isolation"
                    ],
                    "effort": "Moderate"
                })

    # Issue-based remediation
    issue_remediation = {
        "default credentials": {
            "priority": "CRITICAL",
            "title": "Change Default Credentials",
            "steps": [
                "Access device admin interface",
                "Navigate to user/password settings",
                "Set strong, unique password (min 12 chars, mixed case, numbers, symbols)",
                "Document new credentials in password manager"
            ],
            "effort": "Minimal"
        },
        "telnet": {
            "priority": "HIGH",
            "title": "Disable Telnet Service",
            "steps": [
                "Access device admin interface",
                "Disable Telnet service in settings",
                "Use SSH if remote access needed",
                "Verify Telnet port (23) is closed"
            ],
            "effort": "Minimal"
        },
        "ftp": {
            "priority": "MEDIUM",
            "title": "Secure or Disable FTP",
            "steps": [
                "Disable anonymous FTP access",
                "Consider replacing FTP with SFTP",
                "If FTP required, use strong credentials and restrict access"
            ],
            "effort": "Minimal"
        },
        "smb": {
            "priority": "HIGH",
            "title": "Secure SMB Service",
            "steps": [
                "Disable SMBv1 if not needed",
                "Restrict SMB access to trusted IPs/VLANs",
                "Enable SMB signing",
                "Keep system patches up to date"
            ],
            "effort": "Moderate"
        },
        "rtsp": {
            "priority": "HIGH",
            "title": "Secure RTSP Streaming",
            "steps": [
                "Enable RTSP authentication",
                "Use RTSPS (RTSP over TLS) if supported",
                "Restrict RTSP access to internal network only",
                "Disable multicast streaming if not needed"
            ],
            "effort": "Moderate"
        },
        "http": {
            "priority": "MEDIUM",
            "title": "Secure Web Interface",
            "steps": [
                "Enable HTTPS and disable plain HTTP",
                "Set strong admin credentials",
                "Keep firmware updated for web security patches"
            ],
            "effort": "Minimal"
        }
    }

    if issues:
        for issue in issues:
            issue_lower = issue.lower()
            for key, fix in issue_remediation.items():
                if key in issue_lower:
                    fix_copy = fix.copy()
                    fix_copy["related_issue"] = issue
                    remediation_steps.append(fix_copy)
                    break

    # Device-type specific recommendations
    device_recommendations = {
        "camera": [
            {"priority": "HIGH", "title": "Network Isolation",
             "steps": ["Place cameras on separate VLAN", "Block internet access for cameras",
                      "Allow only necessary ports through firewall"],
             "effort": "Moderate"},
            {"priority": "MEDIUM", "title": "Disable Unnecessary Services",
             "steps": ["Disable UPnP", "Disable P2P cloud features if not used",
                      "Disable unused protocols (ONVIF, SDK)"],
             "effort": "Minimal"}
        ],
        "router": [
            {"priority": "CRITICAL", "title": "Secure Admin Interface",
             "steps": ["Change default admin password", "Disable remote management if not needed",
                      "Use HTTPS for admin interface"],
             "effort": "Minimal"},
            {"priority": "HIGH", "title": "Firmware Update",
             "steps": ["Check for latest firmware from vendor", "Backup configuration before update",
                      "Apply security updates promptly"],
             "effort": "Moderate"},
            {"priority": "MEDIUM", "title": "Disable Insecure Features",
             "steps": ["Disable WPS", "Disable UPnP", "Use WPA3 if available"],
             "effort": "Minimal"}
        ],
        "nas": [
            {"priority": "HIGH", "title": "Restrict External Access",
             "steps": ["Disable QuickConnect/EZ-Connect if not needed",
                      "Use VPN for remote access instead of port forwarding",
                      "Enable firewall on NAS"],
             "effort": "Moderate"},
            {"priority": "HIGH", "title": "Enable Security Features",
             "steps": ["Enable 2FA for admin accounts", "Configure auto-block for failed logins",
                      "Enable security advisor/scanner"],
             "effort": "Minimal"}
        ]
    }

    if device_type and device_type.lower() in device_recommendations:
        for rec in device_recommendations[device_type.lower()]:
            rec_copy = rec.copy()
            rec_copy["related_device_type"] = device_type
            remediation_steps.append(rec_copy)

    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    remediation_steps.sort(key=lambda x: (priority_order.get(x.get("priority", "LOW"), 4),
                                          -x.get("cvss_score", 0)))

    # Remove duplicates
    seen_titles = set()
    unique_steps = []
    for step in remediation_steps:
        if step["title"] not in seen_titles:
            seen_titles.add(step["title"])
            unique_steps.append(step)

    return json.dumps({
        "success": True,
        "remediation_count": len(unique_steps),
        "remediation_steps": unique_steps
    }, indent=2)


def _severity_to_priority(severity: str) -> str:
    """Convert CVSS severity to priority."""
    mapping = {
        'CRITICAL': 'CRITICAL',
        'HIGH': 'HIGH',
        'MEDIUM': 'MEDIUM',
        'LOW': 'LOW'
    }
    return mapping.get(severity.upper(), 'MEDIUM')


# Export all tools
RAG_TOOLS = [
    search_cve_by_device,
    identify_device_from_fingerprint,
    get_attack_patterns,
    get_remediation
]
