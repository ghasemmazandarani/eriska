import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from utils.logger import log

class CredentialTester:
    def __init__(self):
        # Common default credentials for IoT/Cameras
        self.defaults = [
            ('admin', 'admin'),
            ('admin', '12345'),
            ('admin', '123456'),
            ('root', 'root'),
            ('root', '123456'),
            ('root', 'pass'),
            ('admin', 'password'),
            ('service', 'service'),
            ('guest', 'guest'),
            ('user', 'user')
        ]
        
    def test_http_auth(self, ip, port, use_ssl=False):
        """
        Tests default credentials against HTTP/HTTPS services.
        Returns: (is_vulnerable, username, password)
        """
        protocol = "https" if use_ssl else "http"
        base_url = f"{protocol}://{ip}:{port}/"
        
        # 1. Check if auth is actually required
        try:
            r = requests.get(base_url, timeout=2, verify=False)
            if r.status_code == 200:
                return False, None, None # No auth required (or already open)
            if r.status_code not in [401, 403]:
                return False, None, None # Service doesn't look like it needs standard auth
        except:
            return False, None, None

        # 2. Brute-force defaults
        for user, password in self.defaults:
            try:
                # Try Basic Auth
                r = requests.get(base_url, auth=HTTPBasicAuth(user, password), timeout=1, verify=False)
                if r.status_code == 200:
                    log.warning(f"CRITICAL: Found Default Creds for {ip}:{port} -> {user}/{password} (Basic)")
                    return True, user, password
                
                # Try Digest Auth (Common in IP Cameras)
                r = requests.get(base_url, auth=HTTPDigestAuth(user, password), timeout=1, verify=False)
                if r.status_code == 200:
                    log.warning(f"CRITICAL: Found Default Creds for {ip}:{port} -> {user}/{password} (Digest)")
                    return True, user, password
            except:
                continue
                
        return False, None, None
