"""
Camera Interface Scanner Module
اسکنر امنیتی از طریق وب اینترفیس دوربین‌های مداربسته
"""

import requests
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from utils.logger import log
from core.fingerprint import FingerprintEngine
from core.analysis import RiskAnalyzer


class CameraScanner:
    def __init__(self, camera_ip, username, password, camera_type="auto"):
        self.camera_ip = camera_ip
        self.username = username
        self.password = password
        self.camera_type = camera_type
        self.session = requests.Session()
        self.camera_info = {}
        self.security_issues = []

        # Timeout settings
        self.timeout = 15

        # Initialize components
        self.fingerprint_engine = FingerprintEngine()
        self.risk_analyzer = RiskAnalyzer()

        # Common camera ports
        self.camera_ports = [80, 443, 8080, 8000, 554, 8008]

    def authenticate(self):
        """احراز هویت با دوربین"""

        log.info(f"🎥 Attempting authentication to camera {self.camera_ip}")

        # Auto-detect camera type if needed
        if self.camera_type == "auto":
            self.camera_type = self._detect_camera_type()
            log.info(f"🔍 Detected camera type: {self.camera_type}")

        # Try different authentication methods
        auth_methods = [
            self._try_camera_web_auth,
            self._try_onvif_auth,
            self._try_api_auth
        ]

        for i, method in enumerate(auth_methods):
            try:
                log.info(f"🔄 Trying camera auth method {i+1}/3...")
                if method():
                    log.info("✅ Camera authentication successful!")
                    return True
            except Exception as e:
                log.debug(f"Camera auth method {i+1} failed: {e}")
                continue

        log.error("❌ All camera authentication methods failed")
        return False

    def _detect_camera_type(self):
        """تشخیص نوع دوربین از طریق اسکن اولیه"""

        try:
            # Try different ports
            for port in self.camera_ports:
                try:
                    url = f"http{'s' if port == 443 else ''}://{self.camera_ip}:{port}"
                    response = requests.get(url, timeout=5, verify=False)

                    if response.status_code == 200:
                        content = response.text.lower()

                        # Detection patterns
                        patterns = {
                            "hikvision": ["hikvision", "ds-2cd", "nv", "dvr"],
                            "dahua": ["dahua", "ipc-hfw", "dh-", "dhi"],
                            "axis": ["axis", "communications", "camera management"],
                            "vivotek": ["vivotek", "ib", "network camera"],
                            "foscam": ["foscam", "webcam"],
                            "tplink": ["tp-link", "tapo", "camera"],
                            "dlink": ["d-link", "dcs-", "camera"]
                        }

                        for brand, keywords in patterns.items():
                            if any(keyword in content for keyword in keywords):
                                log.info(f"Detected {brand} camera on port {port}")
                                return brand

                        # Check for ONVIF
                        if "onvif" in content or "getdeviceinformation" in content:
                            return "onvif"

                except:
                    continue

        except Exception as e:
            log.debug(f"Camera type detection failed: {e}")

        return "unknown"

    def _try_camera_web_auth(self):
        """احراز هویت از طریق وب اینترفیس دوربین"""

        # Try different camera web interfaces
        web_interfaces = [
            "/",                     # Main interface
            "/login.html",          # Common login page
            "/index.html",          # Alternative main page
            "/doc/page/login.asp",  # Hikvision specific
            "/web/index.html",      # Dahua specific
            "/cgi-bin/hi3510",     # Generic interface
            "/dvr"                  # DVR interface
        ]

        for port in [80, 443, 8080]:
            for path in web_interfaces:
                try:
                    protocol = "https" if port == 443 else "http"
                    url = f"{protocol}://{self.camera_ip}:{port}{path}"

                    # Get login page
                    response = self.session.get(url, timeout=5, verify=False)

                    if response.status_code == 200:
                        # Try form-based login
                        if self._try_camera_form_login(url, response.text):
                            return True

                        # Try basic auth
                        if self._try_camera_basic_auth(url):
                            return True

                except:
                    continue

        return False

    def _try_camera_form_login(self, login_url, html_content):
        """تلاش برای ورود از طریق فرم"""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find login form
            form = soup.find('form')
            if not form:
                return False

            # Determine field names (varies by camera)
            username_field = None
            password_field = None

            # Common field name patterns
            username_patterns = ["username", "user", "name", "id", "account"]
            password_patterns = ["password", "pwd", "pass", "key"]

            # Try to find form fields
            all_inputs = form.find_all('input')
            for input_tag in all_inputs:
                field_name = input_tag.get('name', '').lower()
                field_type = input_tag.get('type', '').lower()

                if field_type == 'text' or not field_type:
                    if any(pattern in field_name for pattern in username_patterns):
                        username_field = field_name
                elif field_type == 'password':
                    password_field = field_name

            # If we couldn't find standard fields, try common names
            if not username_field:
                username_field = "username"
            if not password_field:
                password_field = "password"

            # Prepare login data
            login_data = {
                username_field: self.username,
                password_field: self.password
            }

            # Add any hidden fields
            for hidden in form.find_all('input', {'type': 'hidden'}):
                if hidden.get('name') and hidden.get('value'):
                    login_data[hidden.get('name')] = hidden.get('value')

            # Submit login form
            action_url = urljoin(login_url, form.get('action', login_url))

            login_response = self.session.post(
                action_url,
                data=login_data,
                timeout=10,
                verify=False,
                allow_redirects=False
            )

            # Check if login was successful
            if login_response.status_code in [200, 302]:
                # Try to access a protected page to verify
                test_urls = [
                    "/",
                    "/index.html",
                    "/live.html",
                    "/camera.html",
                    "/setup.html"
                ]

                for test_url in test_urls:
                    try:
                        test_response = self.session.get(
                            urljoin(login_url, test_url),
                            timeout=5,
                            verify=False
                        )
                        if test_response.status_code == 200:
                            if "login" not in test_response.text.lower():
                                return True
                    except:
                        continue

        except Exception as e:
            log.debug(f"Camera form login failed: {e}")

        return False

    def _try_camera_basic_auth(self, login_url):
        """تلاش برای احراز هویت Basic"""

        try:
            self.session.auth = (self.username, self.password)

            response = self.session.get(login_url, timeout=5, verify=False)

            # Check if we got a login page or actual content
            if response.status_code == 200:
                if "login" not in response.text.lower() and "unauthorized" not in response.text.lower():
                    return True

        except Exception as e:
            log.debug(f"Camera basic auth failed: {e}")

        return False

    def _try_onvif_auth(self):
        """احراز هویت از طریق ONVIF"""

        try:
            # ONVIF GetDeviceInformation request
            onvif_url = f"http://{self.camera_ip}/onvif/device_service"

            soap_payload = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
  <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>
  </s:Body>
</s:Envelope>"""

            headers = {
                'Content-Type': 'application/soap+xml',
                'SOAPAction': 'http://www.onvif.org/ver10/device/wsdl/GetDeviceInformation'
            }

            # Try with digest auth first (common in cameras)
            from requests.auth import HTTPDigestAuth
            response = requests.post(
                onvif_url,
                data=soap_payload,
                headers=headers,
                auth=HTTPDigestAuth(self.username, self.password),
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                if "GetDeviceInformationResponse" in response.text:
                    return True

        except Exception as e:
            log.debug(f"ONVIF auth failed: {e}")

        return False

    def _try_api_auth(self):
        """احراز هویت از طریق REST API (دوربین‌های مدرن)"""

        api_endpoints = [
            "/api/v1/login",
            "/api/auth/login",
            "/cgi-bin/api.cgi",
            "/cgi-bin/login.cgi"
        ]

        for endpoint in api_endpoints:
            try:
                url = f"http://{self.camera_ip}{endpoint}"

                auth_data = {
                    'username': self.username,
                    'password': self.password
                }

                response = requests.post(url, json=auth_data, timeout=10, verify=False)

                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get('success') or result.get('token') or result.get('status') == 'success':
                            return True
                    except:
                        pass

            except:
                continue

        return False

    def get_camera_info(self):
        """دریافت اطلاعات کامل دوربین"""

        log.info("📷 Gathering camera information...")

        info = {
            'ip': self.camera_ip,
            'type': self.camera_type,
            'model': 'Unknown',
            'firmware': 'Unknown',
            'serial': 'Unknown',
            'mac': 'Unknown',
            'resolution': 'Unknown',
            'capabilities': []
        }

        try:
            # Try to get detailed info based on camera type
            if self.camera_type == "hikvision":
                info.update(self._get_hikvision_info())
            elif self.camera_type == "dahua":
                info.update(self._get_dahua_info())
            elif self.camera_type == "axis":
                info.update(self._get_axis_info())
            else:
                # Generic info extraction
                info.update(self._get_generic_camera_info())

        except Exception as e:
            log.debug(f"Failed to get detailed camera info: {e}")

        self.camera_info = info
        return info

    def _get_hikvision_info(self):
        """استخراج اطلاعات دوربین Hikvision"""

        info = {}

        try:
            # Try Hikvision-specific endpoints
            hikvision_endpoints = [
                "/ISAPI/System/deviceInfo",
                "/ISAPI/Device/info",
                "/doc/page/login.asp"
            ]

            for endpoint in hikvision_endpoints:
                try:
                    url = f"http://{self.camera_ip}{endpoint}"
                    response = self.session.get(url, timeout=10, verify=False)

                    if response.status_code == 200:
                        # Parse XML response (Hikvision uses XML)
                        if "deviceName" in response.text:
                            info.update(self._parse_hikvision_xml(response.text))

                except:
                    continue

        except Exception as e:
            log.debug(f"Hikvision info extraction failed: {e}")

        return info

    def _get_dahua_info(self):
        """استخراج اطلاعات دوربین Dahua"""

        info = {}

        try:
            # Try Dahua-specific endpoints
            dahua_endpoints = [
                "/cgi-bin/global.cgi",
                "/cgi-bin/magicBox.cgi",
                "/web/index.html"
            ]

            for endpoint in dahua_endpoints:
                try:
                    url = f"http://{self.camera_ip}{endpoint}"
                    response = self.session.get(url, timeout=10, verify=False)

                    if response.status_code == 200:
                        # Parse response
                        info.update(self._parse_dahua_response(response.text))

                except:
                    continue

        except Exception as e:
            log.debug(f"Dahua info extraction failed: {e}")

        return info

    def _get_generic_camera_info(self):
        """استخراج اطلاعات عمومی دوربین"""

        info = {}

        try:
            # Try to get info from main interface
            for port in self.camera_ports:
                try:
                    url = f"http://{self.camera_ip}:{port}/"
                    response = self.session.get(url, timeout=5, verify=False)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # Extract title/model info
                        title = soup.find('title')
                        if title:
                            title_text = title.get_text()
                            info['model'] = title_text.strip()

                        # Look for firmware info
                        content = response.text

                        # Firmware patterns
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

                        # MAC address patterns
                        mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
                        mac_matches = re.findall(mac_pattern, content)
                        if mac_matches:
                            info['mac'] = mac_matches[0][0]

                except:
                    continue

        except Exception as e:
            log.debug(f"Generic camera info extraction failed: {e}")

        return info

    def analyze_camera_security(self):
        """تحلیل امنیتی دوربین"""

        log.info("🔒 Analyzing camera security...")

        security_issues = []

        # 1. Check for default credentials
        if self._has_default_credentials():
            security_issues.append({
                'severity': 'CRITICAL',
                'type': 'default_credentials',
                'description': 'Camera using default credentials',
                'recommendation': 'Change default password immediately'
            })

        # 2. Check for insecure protocols
        if self._has_insecure_protocols():
            security_issues.append({
                'severity': 'HIGH',
                'type': 'insecure_protocols',
                'description': 'Camera allows unencrypted access',
                'recommendation': 'Use HTTPS and RTSPS encryption'
            })

        # 3. Check for firmware vulnerabilities
        firmware_issues = self._check_firmware_vulnerabilities()
        security_issues.extend(firmware_issues)

        # 4. Check for exposed admin interface
        if self._has_exposed_admin():
            security_issues.append({
                'severity': 'MEDIUM',
                'type': 'exposed_admin',
                'description': 'Admin interface accessible from WAN',
                'recommendation': 'Restrict admin access to local network only'
            })

        # 5. Check for default ports
        if self._has_default_ports():
            security_issues.append({
                'severity': 'LOW',
                'type': 'default_ports',
                'description': 'Using default camera ports',
                'recommendation': 'Change default HTTP/RTSP ports'
            })

        self.security_issues = security_issues
        return security_issues

    def _has_default_credentials(self):
        """بررسی استفاده از credentials پیش‌فرض"""

        common_defaults = [
            ('admin', 'admin'),
            ('admin', '12345'),
            ('admin', '123456'),
            ('admin', 'password'),
            ('root', 'root'),
            ('root', '123456'),
            ('user', 'user'),
            ('guest', 'guest')
        ]

        # Check if current credentials are default
        for username, password in common_defaults:
            if (self.username.lower() == username.lower() and
                self.password.lower() == password.lower()):
                return True

        return False

    def _has_insecure_protocols(self):
        """بررسی پروتکل‌های ناامن"""

        try:
            # Check if HTTP (not HTTPS) is accessible
            response = requests.get(f"http://{self.camera_ip}/", timeout=5, verify=False)
            if response.status_code == 200:
                return True

            # Check for unencrypted RTSP
            rtsp_response = self._test_rtsp_access()
            if rtsp_response:
                return True

        except:
            pass

        return False

    def _test_rtsp_access(self):
        """تست دسترسی RTSP"""

        try:
            import socket

            for port in [554, 8554, 1935]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((self.camera_ip, port))
                    sock.close()

                    if result == 0:
                        return True

                except:
                    continue

        except:
            pass

        return False

    def _check_firmware_vulnerabilities(self):
        """بررسی آسیب‌پذیری‌های فریمور"""

        issues = []
        firmware = self.camera_info.get('firmware', '').lower()

        # Known vulnerable firmware patterns
        vulnerable_patterns = {
            'hikvision': {
                'v5.5.0': ['CVE-2017-7921', 'Command Injection'],
                'v5.4.5': ['CVE-2017-7921', 'Buffer Overflow'],
                'v5.3.0': ['CVE-2016-1005', 'Directory Traversal']
            },
            'dahua': {
                'v2.400': ['CVE-2019-10939', 'Hardcoded Credentials'],
                'v2.460': ['CVE-2018-10088', 'Remote Code Execution'],
                'v2.420': ['CVE-2017-7925', 'Information Disclosure']
            }
        }

        camera_type_lower = self.camera_type.lower()
        if camera_type_lower in vulnerable_patterns:
            vulnerabilities = vulnerable_patterns[camera_type_lower]
            for version, vuln_info in vulnerabilities.items():
                if version in firmware:
                    issues.append({
                        'severity': 'HIGH',
                        'type': 'firmware_vulnerability',
                        'description': f'{vuln_info[0]} detected in firmware {firmware}',
                        'recommendation': f'Update firmware immediately. {vuln_info[1]} vulnerability'
                    })

        return issues

    def _has_exposed_admin(self):
        """بررسی دسترسی exposed admin interface"""

        # This would typically require external testing or network configuration analysis
        # For now, return False (would need WAN/external access testing)
        return False

    def _has_default_ports(self):
        """بررسی استفاده از پورت‌های پیش‌فرض"""

        default_ports = [80, 554, 8080, 8000]
        found_default_ports = []

        for port in default_ports:
            try:
                response = requests.get(f"http://{self.camera_ip}:{port}/", timeout=2, verify=False)
                if response.status_code == 200:
                    found_default_ports.append(port)
            except:
                continue

        return len(found_default_ports) > 0

    def generate_report(self):
        """تولید گزارش کامل اسکن دوربین"""

        return {
            'scan_info': {
                'timestamp': time.time(),
                'scan_type': 'camera_interface',
                'camera_ip': self.camera_ip,
                'camera_type': self.camera_type
            },
            'camera_info': self.camera_info,
            'security_analysis': {
                'issues': self.security_issues,
                'risk_score': self._calculate_risk_score(),
                'recommendations': self._generate_recommendations()
            },
            'summary': {
                'total_issues': len(self.security_issues),
                'critical_issues': len([i for i in self.security_issues if i.get('severity') == 'CRITICAL']),
                'high_issues': len([i for i in self.security_issues if i.get('severity') == 'HIGH']),
                'medium_issues': len([i for i in self.security_issues if i.get('severity') == 'MEDIUM']),
                'low_issues': len([i for i in self.security_issues if i.get('severity') == 'LOW'])
            }
        }

    def _calculate_risk_score(self):
        """محاسبه امتیاز ریسک (0-100)"""

        score = 0

        for issue in self.security_issues:
            severity = issue.get('severity', 'LOW')
            if severity == 'CRITICAL':
                score += 30
            elif severity == 'HIGH':
                score += 20
            elif severity == 'MEDIUM':
                score += 10
            elif severity == 'LOW':
                score += 5

        return min(score, 100)

    def _generate_recommendations(self):
        """تولید پیشنهادات اصلاحی"""

        recommendations = []

        if self._has_default_credentials():
            recommendations.append({
                'priority': 'IMMEDIATE',
                'action': 'Change default credentials',
                'details': 'Replace default username/password with strong credentials'
            })

        if self._has_insecure_protocols():
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Enable encrypted protocols',
                'details': 'Use HTTPS for web interface and RTSPS for video streaming'
            })

        firmware_issues = self._check_firmware_vulnerabilities()
        if firmware_issues:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Update firmware',
                'details': 'Install latest firmware to patch security vulnerabilities'
            })

        if len(recommendations) == 0:
            recommendations.append({
                'priority': 'INFO',
                'action': 'Security looks good',
                'details': 'No critical security issues found'
            })

        return recommendations