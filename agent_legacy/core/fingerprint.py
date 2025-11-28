import requests
import mmh3
import codecs
import socket
from utils.logger import log

class FingerprintEngine:
    def __init__(self):
        # Simple OUI DB for MVP (In real world, load from file)
        self.oui_db = {
            "10:12:FB": "Hikvision",
            "C0:56:E3": "Moxa",
            "00:40:8C": "Axis",
            "E0:50:8B": "Dahua",
            "B8:27:EB": "Raspberry Pi",
            "DC:A6:32": "Raspberry Pi",
            "00:11:32": "Synology"
        }
        
        # Known Bad Headers / Vulnerable Signatures
        self.risk_signatures = {
            "Boa/0.94": 8.0, # Vulnerable
            "RomPager": 7.0, # Vulnerable
            "Hikvision-Webs": 5.0, # Common target
            "App-webs/": 5.0
        }
        
        self.port_services = {
            445: "Microsoft-DS (SMB)",
            139: "NetBIOS Session",
            3389: "Microsoft RDP",
            22: "SSH",
            23: "Telnet",
            53: "DNS",
            1883: "MQTT",
            554: "RTSP"
        }

    def guess_service(self, port):
        return self.port_services.get(port, "Unknown")

    def lookup_oui(self, mac):
        if not mac: return "Unknown"
        
        # 1. Local DB Check
        prefix_colon = mac.upper()[:8]
        vendor = self.oui_db.get(prefix_colon)
        if vendor:
            return vendor
            
        # 2. Online Lookup (Fallback)
        try:
            # Using macvendors.co API (Free, no key)
            r = requests.get(f"https://macvendors.co/api/{mac}", timeout=2)
            if r.status_code == 200:
                data = r.json()
                if 'result' in data and 'company' in data['result']:
                    return data['result']['company']
        except:
            pass
            
        return "Unknown"

    def probe_http(self, ip, port, use_ssl=False):
        protocol = "https" if use_ssl else "http"
        url = f"{protocol}://{ip}:{port}"
        data = {
            "server": None,
            "title": None,
            "realm": None,
            "favicon_hash": None,
            "risk_score": 0
        }
        
        try:
            # 1. Get Headers & Title
            r = requests.get(url, timeout=3, verify=False)
            data["server"] = r.headers.get("Server")
            data["realm"] = r.headers.get("WWW-Authenticate")
            
            if r.text:
                start = r.text.find("<title>")
                end = r.text.find("</title>")
                if start != -1 and end != -1:
                    data["title"] = r.text[start+7:end].strip()

            # 2. Favicon Hash
            favicon_url = f"{url}/favicon.ico"
            r_fav = requests.get(favicon_url, timeout=2, verify=False)
            if r_fav.status_code == 200:
                favicon = codecs.encode(r_fav.content, "base64")
                data["favicon_hash"] = mmh3.hash(r_fav.content)

            # 3. Risk Analysis
            if data["server"]:
                for sig, score in self.risk_signatures.items():
                    if sig in data["server"]:
                        data["risk_score"] = max(data["risk_score"], score)
            
            if data["realm"] and ("admin" in data["realm"].lower() or "default" in data["realm"].lower()):
                data["risk_score"] = max(data["risk_score"], 4.0)

        except Exception as e:
            # log.debug(f"HTTP Probe failed for {ip}:{port}: {e}")
            pass
            
        return data

    def probe_rtsp(self, ip, port=554):
        data = {"banner": None, "auth_needed": False}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((ip, port))
            s.send(b"DESCRIBE rtsp://{ip}:{port}/ RTSP/1.0\r\nCSeq: 1\r\n\r\n")
            response = s.recv(1024).decode(errors='ignore')
            
            if "RTSP/1.0 401" in response:
                data["auth_needed"] = True
            elif "RTSP/1.0 200" in response:
                data["auth_needed"] = False # High Risk!
                
            for line in response.split("\r\n"):
                if line.startswith("Server:"):
                    data["banner"] = line.split(":", 1)[1].strip()
                    
        except Exception:
            pass
        finally:
            s.close()
        return data

    def probe_onvif(self, ip, port=80):
        """
        Sends a raw SOAP probe to detect ONVIF services.
        """
        data = {"is_onvif": False, "info": None}
        # SOAP Probe for GetDeviceInformation
        soap_payload = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
  <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>
  </s:Body>
</s:Envelope>"""
        
        try:
            url = f"http://{ip}:{port}/onvif/device_service"
            r = requests.post(url, data=soap_payload, headers={'Content-Type': 'application/soap+xml'}, timeout=2)
            
            if r.status_code == 200 and "GetDeviceInformationResponse" in r.text:
                data["is_onvif"] = True
                # Extract Model/Manufacturer simply
                if "Manufacturer" in r.text:
                    start = r.text.find("Manufacturer") + 13
                    end = r.text.find("</", start)
                    data["info"] = r.text[start:end].split(">")[-1] # Handle namespace tags
        except:
            pass
            
        return data

    def probe_snmp(self, ip, port=161):
        """
        Sends a raw SNMP v1 GetRequest for sysDescr (1.3.6.1.2.1.1.1.0).
        """
        data = {"is_snmp": False, "info": None}
        
        # SNMP v1 GetRequest Packet Construction (Hardcoded for sysDescr)
        # Community: public
        # OID: 1.3.6.1.2.1.1.1.0 (sysDescr)
        packet = (
            b'\x30\x26'             # Sequence (38 bytes)
            b'\x02\x01\x00'         # Version: 0 (v1)
            b'\x04\x06\x70\x75\x62\x6c\x69\x63' # Community: public
            b'\xa0\x19'             # GetRequest
            b'\x02\x04\x00\x00\x00\x01' # Request ID
            b'\x02\x01\x00'         # Error Status: 0
            b'\x02\x01\x00'         # Error Index: 0
            b'\x30\x0b'             # VarBindList
            b'\x30\x09'             # VarBind
            b'\x06\x05\x2b\x06\x01\x02\x01' # Object Name (Prefix 1.3.6.1.2.1)
            b'\x05\x00'             # Null Value
        )
        # Note: The above packet is a simplified example. 
        # A more robust raw packet for sysDescr (1.3.6.1.2.1.1.1.0):
        # 30 29 02 01 00 04 06 70 75 62 6c 69 63 a0 1c 02 04 12 34 56 78 02 01 00 02 01 00 30 0e 30 0c 06 08 2b 06 01 02 01 01 01 00 05 00
        packet = bytes.fromhex("302902010004067075626c6963a01c020412345678020100020100300e300c06082b060102010101000500")

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        try:
            s.sendto(packet, (ip, port))
            response, _ = s.recvfrom(1024)
            if response:
                data["is_snmp"] = True
                # Parse response roughly to find the string
                # SNMP strings are usually at the end
                try:
                    # Skip header junk, look for printable ascii
                    text = response.decode(errors='ignore')
                    # Clean up non-printable chars
                    clean_text = "".join([c for c in text if c.isprintable()])
                    # Usually contains "Linux", "Huawei", "Cisco", etc.
                    # Heuristic extraction:
                    if "public" in clean_text:
                        info_part = clean_text.split("public")[-1]
                        data["info"] = info_part.strip()
                except:
                    pass
        except:
            pass
        finally:
            s.close()
            
        return data

    def probe_ssdp(self, ip):
        """
        Sends a unicast SSDP M-SEARCH packet to detect UPnP devices.
        """
        data = {"is_upnp": False, "info": None, "model": None}
        
        msg = (
            'M-SEARCH * HTTP/1.1\r\n'
            'HOST: 239.255.255.250:1900\r\n'
            'MAN: "ssdp:discover"\r\n'
            'MX: 1\r\n'
            'ST: ssdp:all\r\n'
            '\r\n'
        ).encode()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.5)
        try:
            # Send unicast to the target IP (not multicast, to be polite/directed)
            s.sendto(msg, (ip, 1900))
            response, _ = s.recvfrom(2048)
            
            if response:
                data["is_upnp"] = True
                resp_text = response.decode(errors='ignore')
                
                # Extract Location URL
                location = None
                for line in resp_text.split('\r\n'):
                    if line.upper().startswith('LOCATION:'):
                        location = line.split(':', 1)[1].strip()
                        break
                
                if location:
                    # Fetch XML description
                    try:
                        r = requests.get(location, timeout=2)
                        if r.status_code == 200:
                            xml = r.text
                            # Simple XML parsing
                            if "<modelName>" in xml:
                                data["model"] = xml.split("<modelName>")[1].split("</modelName>")[0]
                            if "<manufacturer>" in xml:
                                data["info"] = xml.split("<manufacturer>")[1].split("</manufacturer>")[0]
                    except:
                        pass
        except:
            pass
        finally:
            s.close()
            
        return data
