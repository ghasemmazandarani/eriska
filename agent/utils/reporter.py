import requests
import json
import os
from utils.logger import log

# Default Backend URL (Can be overridden by env var)
BACKEND_URL = os.getenv("ERISKA_BACKEND_URL", "http://localhost:8000/api")
API_KEY_FILE = "agent_key.secret"

class Reporter:
    def __init__(self):
        self.api_key = self._load_api_key()

    def _load_api_key(self):
        if os.path.exists(API_KEY_FILE):
            try:
                with open(API_KEY_FILE, "r") as f:
                    return f.read().strip()
            except Exception as e:
                log.error(f"Failed to load API key: {e}")
        return None

    def _save_api_key(self, api_key):
        try:
            with open(API_KEY_FILE, "w") as f:
                f.write(api_key)
            self.api_key = api_key
            log.info(f"✅ API Key saved to {API_KEY_FILE}")
            return True
        except Exception as e:
            log.error(f"❌ Failed to save API key: {e}")
            return False

    def connect(self, token):
        """Exchange connection token for API Key"""
        url = f"{BACKEND_URL}/agent/connect/"
        log.info(f"🔌 Connecting to backend at {url}...")
        
        try:
            response = requests.post(url, json={"token": token})
            if response.status_code == 200:
                data = response.json()
                api_key = data.get("api_key")
                name = data.get("name")
                if api_key:
                    log.info(f"✅ Successfully connected as agent: {name}")
                    return self._save_api_key(api_key)
            else:
                log.error(f"❌ Connection failed: {response.text}")
        except Exception as e:
            log.error(f"❌ Connection error: {e}")
        return False

    def upload_report(self, report, scan_type="network"):
        """Upload scan report to backend"""
        if not self.api_key:
            log.warning("⚠️ No API Key found. Skipping upload. Run with --connect <TOKEN> first.")
            return False

        url = f"{BACKEND_URL}/agent/upload/"
        headers = {"X-Agent-Key": self.api_key}
        payload = {
            "scan_type": scan_type,
            "data": report
        }

        log.info(f"📤 Uploading report to {url}...")
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                log.info("✅ Report uploaded successfully!")
                return True
            elif response.status_code == 401:
                log.error("❌ Unauthorized: Invalid API Key. Please reconnect.")
            else:
                log.error(f"❌ Upload failed: {response.text}")
        except Exception as e:
            log.error(f"❌ Upload error: {e}")
        return False
