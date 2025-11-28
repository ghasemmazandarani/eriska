from utils.logger import log

class RiskAnalyzer:
    def __init__(self):
        self.risk_rules = [
            {"id": "telnet_open", "score": 3.0, "desc": "Telnet service is open (Insecure Protocol)"},
            {"id": "rtsp_no_auth", "score": 10.0, "desc": "RTSP stream accessible without authentication"},
            {"id": "http_basic_clear", "score": 2.0, "desc": "HTTP Basic Auth used without HTTPS"},
            {"id": "smb_open", "score": 5.0, "desc": "SMB (445) File Sharing is open (Ransomware Target)"},
            {"id": "netbios_open", "score": 3.0, "desc": "NetBIOS (139) is open (Legacy Protocol)"},
            {"id": "rdp_open", "score": 4.0, "desc": "RDP (3389) Remote Desktop is open"},
            {"id": "default_creds_hint", "score": 4.0, "desc": "Realm suggests default credentials"},
            {"id": "vulnerable_server", "score": 7.0, "desc": "Server header matches known vulnerable software"},
            {"id": "expired_ssl", "score": 1.0, "desc": "SSL Certificate issues"}
        ]

    def analyze(self, device_data):
        """
        Calculates a risk score (0-100) based on multiple factors.
        """
        score = 0
        issues = []
        
        ports = device_data.get('ports', [])
        fingerprints = device_data.get('fingerprints', {})
        vendor = device_data.get('vendor', 'Unknown')
        
        # --- Factor 1: Device Sensitivity (Base Multiplier) ---
        # Cameras and Routers are high value targets
        sensitivity = 1.0
        if "Camera" in device_data.get('type', '') or "Hikvision" in vendor or "Dahua" in vendor:
            sensitivity = 1.3
            issues.append("High Value Target (Camera/NVR)")
        
        # --- Factor 2: Port Exposure ---
        # More ports = more attack surface
        score += len(ports) * 2
        
        # --- Factor 3: Specific Vulnerabilities ---
        
        # Critical Risks (Score +30)
        if device_data.get('vulnerable_creds'):
            score += 30
            creds = device_data['vulnerable_creds']
            issues.append(f"CRITICAL: Default Credentials Found ({creds['user']}/{creds['pass']})")
            
        for key, fp in fingerprints.items():
            if "rtsp" in key and not fp.get('auth_needed', True):
                score += 30
                issues.append("CRITICAL: RTSP Stream has NO AUTHENTICATION")

        # High Risks (Score +15)
        if 445 in ports:
            score += 15
            issues.append("SMB (445) File Sharing is exposed (Ransomware Risk)")
        if 23 in ports:
            score += 15
            issues.append("Telnet (23) is open (Insecure Protocol)")
            
        # Medium Risks (Score +5)
        if 80 in ports and not 443 in ports:
            score += 5
            issues.append("Unencrypted HTTP Interface")
        if 139 in ports:
            score += 5
            issues.append("NetBIOS (139) exposed")
        if 3389 in ports:
            score += 10
            issues.append("RDP (3389) exposed")

        # Apply Sensitivity Multiplier
        final_score = int(score * sensitivity)
        
        # Cap at 100
        final_score = min(final_score, 100)
        
        return final_score, issues
