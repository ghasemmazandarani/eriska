"""
Router Interface Scanner Module
اسکنر امنیتی از طریق وب اینترفیس روتر
"""

import requests
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from utils.logger import log
from core.fingerprint import FingerprintEngine
from core.analysis import RiskAnalyzer


class RouterScanner:
    def __init__(self, router_ip, username, password, router_type="auto"):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.router_type = router_type
        self.session = requests.Session()
        self.router_info = {}
        self.found_devices = {}

        # Timeout settings
        self.timeout = 10

        # Initialize components
        self.fingerprint_engine = FingerprintEngine()
        self.risk_analyzer = RiskAnalyzer()

    def authenticate(self):
        """احراز هویت با روتر"""

        log.info(f"🔐 Attempting authentication to {self.router_ip}")

        # Auto-detect router type if needed
        if self.router_type == "auto":
            self.router_type = self._detect_router_type()
            log.info(f"🔍 Detected router type: {self.router_type}")

        # Try different authentication methods
        auth_methods = [
            self._try_basic_auth,
            self._try_form_post_auth,
            self._try_json_auth
        ]

        for i, method in enumerate(auth_methods):
            try:
                log.info(f"🔄 Trying authentication method {i+1}/3...")
                if method():
                    log.info("✅ Authentication successful!")
                    return True
            except Exception as e:
                log.debug(f"Auth method {i+1} failed: {e}")
                continue

        log.error("❌ All authentication methods failed")
        return False

    def _detect_router_type(self):
        """تشخیص نوع روتر از صفحه اصلی"""

        try:
            response = self.session.get(f"http://{self.router_ip}/", timeout=self.timeout)

            if response.status_code != 200:
                return "unknown"

            content = response.text.lower()

            # Detection patterns
            patterns = {
                "tp-link": ["tp-link", "tplink", "archer", "dec", "wr", "td"],
                "d-link": ["d-link", "dlink", "dir-", "dsl-", "covr"],
                "asus": ["asus", "rt-", "ac", "xd", "zenwifi"],
                "netgear": ["netgear", "r", "nighthawk", "orbi"],
                "tenda": ["tenda", "ac", "nova"],
                "cisco": ["cisco", "linksys", "ea", "mr"]
            }

            for brand, keywords in patterns.items():
                if any(keyword in content for keyword in keywords):
                    return brand

            return "unknown"

        except Exception as e:
            log.debug(f"Router detection failed: {e}")
            return "unknown"

    def _try_basic_auth(self):
        """احراز هویت Basic HTTP Auth"""

        try:
            self.session.auth = (self.username, self.password)
            response = self.session.get(f"http://{self.router_ip}/", timeout=self.timeout)

            if response.status_code == 200:
                # Check if we got a login page or actual content
                if "login" not in response.text.lower() and "password" not in response.text.lower():
                    return True
        except:
            pass

        return False

    def _try_form_post_auth(self):
        """احراز هویت از طریق فرم POST"""

        try:
            # Get login page
            response = self.session.get(f"http://{self.router_ip}/", timeout=self.timeout)

            if response.status_code != 200:
                return False

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find login form
            form = soup.find('form')
            if not form:
                return False

            # Build form data
            form_data = {
                'username': self.username,
                'password': self.password
            }

            # Add any hidden fields
            for hidden in form.find_all('input', {'type': 'hidden'}):
                if hidden.get('name') and hidden.get('value'):
                    form_data[hidden.get('name')] = hidden.get('value')

            # Submit form
            action_url = urljoin(f"http://{self.router_ip}/", form.get('action', '/login'))
            login_response = self.session.post(action_url, data=form_data, timeout=self.timeout, allow_redirects=False)

            # Check if successful (redirect or success page)
            if login_response.status_code in [200, 302]:
                return True

        except Exception as e:
            log.debug(f"Form auth failed: {e}")

        return False

    def _try_json_auth(self):
        """احراز هویت JSON-based (روترهای مدرن)"""

        try:
            # Try common JSON login endpoints
            endpoints = [
                '/api/login',
                '/cgi-bin/login',
                '/api/v1/auth/login',
                '/router/api/login'
            ]

            for endpoint in endpoints:
                url = f"http://{self.router_ip}{endpoint}"

                auth_data = {
                    'username': self.username,
                    'password': self.password
                }

                response = self.session.post(url, json=auth_data, timeout=self.timeout)

                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get('success') or result.get('status') == 'success':
                            return True
                    except:
                        pass

        except:
            pass

        return False

    def get_router_info(self):
        """دریافت اطلاعات روتر"""

        log.info("📡 Gathering router information...")

        info = {
            'ip': self.router_ip,
            'type': self.router_type,
            'model': 'Unknown',
            'firmware': 'Unknown',
            'mac': 'Unknown',
            'uptime': 'Unknown'
        }

        try:
            # Try to get detailed info based on router type
            if self.router_type == "tp-link":
                info.update(self._get_tp_link_info())
            elif self.router_type == "d-link":
                info.update(self._get_dlink_info())
            elif self.router_type == "asus":
                info.update(self._get_asus_info())
            else:
                # Generic info extraction
                info.update(self._get_generic_info())

        except Exception as e:
            log.debug(f"Failed to get detailed router info: {e}")

        self.router_info = info
        return info

    def get_connected_devices(self):
        """دریافت لیست کامل دستگاه‌های متصل"""

        log.info("🔍 Scanning for connected devices...")

        all_devices = []

        # Try different device discovery methods
        device_sources = [
            self._get_dhcp_devices,
            self._get_arp_devices,
            self._get_wireless_devices,
            self._get_active_sessions
        ]

        for method in device_sources:
            try:
                log.debug(f"Trying device discovery method: {method.__name__}")
                devices = method()
                if devices:
                    all_devices.extend(devices)
                    log.info(f"✓ Found {len(devices)} devices via {method.__name__}")
            except Exception as e:
                log.debug(f"Device discovery method {method.__name__} failed: {e}")

        # Remove duplicates and merge information
        unique_devices = self._merge_device_info(all_devices)

        # Enrich with additional analysis
        for device in unique_devices.values():
            # OUI lookup
            device['vendor'] = self.fingerprint_engine.lookup_oui(device['mac'])

            # Risk analysis
            risk_score, issues = self.risk_analyzer.analyze(device)
            device['risk_score'] = risk_score
            device['risk_issues'] = issues

            # Add timestamp
            device['scan_timestamp'] = time.time()

        self.found_devices = unique_devices
        log.info(f"🎯 Total unique devices found: {len(unique_devices)}")

        return unique_devices

    def _get_dhcp_devices(self):
        """دریافت دستگاه‌ها از لیست DHCP"""

        devices = []

        # Common DHCP page URLs
        dhcp_urls = [
            '/userRpm/LanDhcpServerRpm.htm',  # TP-Link
            '/dhcp_client.htm',               # General
            '/network/dhcp_clients.html',     # Modern routers
            '/cgi-bin/dhcp.cgi'              # CGI-based
        ]

        for url in dhcp_urls:
            try:
                response = self.session.get(f"http://{self.router_ip}{url}", timeout=self.timeout)
                if response.status_code == 200:
                    devices.extend(self._parse_device_table(response.text, 'dhcp'))
                    break
            except:
                continue

        return devices

    def _get_arp_devices(self):
        """دریافت دستگاه‌ها از جدول ARP"""

        devices = []

        arp_urls = [
            '/userRpm/ArpListRpm.htm',       # TP-Link
            '/arp_table.htm',                # General
            '/network/arp_table.html',       # Modern
            '/cgi-bin/arp.cgi'              # CGI-based
        ]

        for url in arp_urls:
            try:
                response = self.session.get(f"http://{self.router_ip}{url}", timeout=self.timeout)
                if response.status_code == 200:
                    devices.extend(self._parse_device_table(response.text, 'arp'))
                    break
            except:
                continue

        return devices

    def _get_wireless_devices(self):
        """دریافت دستگاه‌های بی‌سیم"""

        devices = []

        wireless_urls = [
            '/userRpm/WlanStationRpm.htm',   # TP-Link
            '/wireless_clients.htm',         # General
            '/network/wireless.html',        # Modern
            '/wlstat.htm'                    # ASUS
        ]

        for url in wireless_urls:
            try:
                response = self.session.get(f"http://{self.router_ip}{url}", timeout=self.timeout)
                if response.status_code == 200:
                    wireless_devices = self._parse_device_table(response.text, 'wireless')
                    # Mark as wireless
                    for device in wireless_devices:
                        device['connection_type'] = 'wireless'
                    devices.extend(wireless_devices)
                    break
            except:
                continue

        return devices

    def _get_active_sessions(self):
        """دریافت sessionهای فعال"""

        devices = []

        session_urls = [
            '/userRpm/SessionRpm.htm',       # TP-Link
            '/active_sessions.htm',           # General
            '/network/sessions.html'          # Modern
        ]

        for url in session_urls:
            try:
                response = self.session.get(f"http://{self.router_ip}{url}", timeout=self.timeout)
                if response.status_code == 200:
                    devices.extend(self._parse_device_table(response.text, 'sessions'))
                    break
            except:
                continue

        return devices

    def _parse_device_table(self, html_content, table_type):
        """Parse device information from HTML tables"""

        devices = []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find device tables
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')

                if len(rows) < 2:  # Skip empty tables
                    continue

                # Try to identify headers
                headers = []
                header_row = rows[0].find_all(['th', 'td'])
                for header in header_row:
                    headers.append(header.get_text().strip().lower())

                # Parse data rows
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) < 2:  # Skip empty rows
                        continue

                    device = {}

                    # Map columns to device properties
                    for i, col in enumerate(cols):
                        if i >= len(headers):
                            continue

                        col_text = col.get_text().strip()

                        if 'ip' in headers[i] or 'address' in headers[i]:
                            device['ip'] = col_text
                        elif 'mac' in headers[i]:
                            device['mac'] = col_text
                        elif 'name' in headers[i] or 'hostname' in headers[i]:
                            device['hostname'] = col_text
                        elif 'type' in headers[i]:
                            device['type'] = col_text

                    # Validate and add device
                    if device.get('ip') and ':' in device.get('mac', ''):
                        if 'connection_type' not in device:
                            device['connection_type'] = 'wired' if table_type != 'wireless' else 'wireless'

                        # Add metadata
                        device['source'] = table_type
                        device['router_type'] = self.router_type

                        devices.append(device)

        except Exception as e:
            log.debug(f"Failed to parse device table: {e}")

        return devices

    def _merge_device_info(self, devices):
        """ادغام اطلاعات دستگاه‌ها و حذف موارد تکراری"""

        unique_devices = {}

        for device in devices:
            key = device.get('mac', device.get('ip'))

            if key not in unique_devices:
                unique_devices[key] = {
                    'ip': device.get('ip'),
                    'mac': device.get('mac'),
                    'hostname': device.get('hostname', 'Unknown'),
                    'type': device.get('type', 'Unknown'),
                    'connection_type': device.get('connection_type', 'unknown'),
                    'sources': []
                }

            # Merge additional information
            for field, value in device.items():
                if field in ['ip', 'mac', 'hostname', 'type', 'connection_type'] and value:
                    unique_devices[key][field] = value

            # Track data sources
            if device.get('source'):
                unique_devices[key]['sources'].append(device['source'])

        return unique_devices

    def _get_generic_info(self):
        """Generic router information extraction"""

        info = {}

        try:
            response = self.session.get(f"http://{self.router_ip}/", timeout=self.timeout)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract title/model info
                title = soup.find('title')
                if title:
                    title_text = title.get_text()
                    info['model'] = title_text.strip()

                # Look for model info in content
                content = response.text

                # Firmware version patterns
                import re
                firmware_patterns = [
                    r'version[:\s]+([0-9\.]+)',
                    r'firmware[:\s]+([0-9\.]+)',
                    r'v([0-9\.]+)'
                ]

                for pattern in firmware_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        info['firmware'] = match.group(1)
                        break

        except Exception as e:
            log.debug(f"Generic info extraction failed: {e}")

        return info

    # Router-specific info extraction methods can be added here
    def _get_tp_link_info(self):
        """Extract TP-Link specific information"""
        return self._get_generic_info()

    def _get_dlink_info(self):
        """Extract D-Link specific information"""
        return self._get_generic_info()

    def _get_asus_info(self):
        """Extract ASUS specific information"""
        return self._get_generic_info()

    def generate_report(self):
        """تولید گزارش کامل"""

        return {
            'scan_info': {
                'timestamp': time.time(),
                'scan_type': 'router_interface',
                'router_ip': self.router_ip,
                'router_type': self.router_type
            },
            'router_info': self.router_info,
            'devices': list(self.found_devices.values()),
            'summary': {
                'total_devices': len(self.found_devices),
                'wired_devices': len([d for d in self.found_devices.values() if d.get('connection_type') == 'wired']),
                'wireless_devices': len([d for d in self.found_devices.values() if d.get('connection_type') == 'wireless']),
                'high_risk_devices': len([d for d in self.found_devices.values() if d.get('risk_score', 0) >= 70])
            }
        }