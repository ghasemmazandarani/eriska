import threading
import time
import threading
import time
import socket
# from scapy.all import ARP, Ether, srp, sniff (Moved to methods)
from utils.logger import log
from utils.network import get_local_ip
from utils.network import get_local_ip

class DiscoveryEngine:
    def __init__(self, iface):
        self.iface = iface
        self.found_devices = {} # IP -> {mac, vendor, ports}
        self.lock = threading.Lock()
        self.running = False

    def start_passive(self):
        """
        Starts the passive ARP monitor.
        """
        log.info("Starting Passive ARP Monitor...")
        self.running = True
        t = threading.Thread(target=self._passive_sniffer)
        t.daemon = True
        t.start()

    def _passive_sniffer(self):
        from scapy.all import ARP, sniff
        def packet_callback(pkt):
            if not self.running: return False
            if ARP in pkt:
                # ARP Request or Reply
                if pkt[ARP].op in (1, 2): # who-has or is-at
                    src_ip = pkt[ARP].psrc
                    src_mac = pkt[ARP].hwsrc
                    self._add_device(src_ip, src_mac, "Passive")

        try:
            sniff(prn=packet_callback, filter="arp", store=0, iface=self.iface)
        except Exception as e:
            log.error(f"Passive sniffer error: {e}")

    def scan_network(self, network_range):
        """
        Active ARP Scan.
        """
        from scapy.all import ARP, Ether, srp
        log.info(f"Scanning network: {network_range}")
        try:
            # Create ARP Request
            arp = ARP(pdst=network_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp

            # Send and receive
            result = srp(packet, timeout=2, verbose=0, iface=self.iface)[0]

            for sent, received in result:
                self._add_device(received.psrc, received.hwsrc, "Active")
            
            log.info(f"ARP Scan complete. Found {len(self.found_devices)} devices.")
            return self.found_devices
        except Exception as e:
            log.error(f"ARP Scan failed: {e}")
            return {}

    def scan_ports(self, target_ip, ports=[80, 443, 8080, 8081, 8000, 554, 22, 23, 21, 53, 445, 139, 3389, 1883]):
        """
        Multi-threaded TCP Connect Scan.
        """
        open_ports = []
        
        def check_port(ip, port):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5) # Increased timeout slightly
            try:
                result = s.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
            except:
                pass
            finally:
                s.close()

        threads = []
        for port in ports:
            t = threading.Thread(target=check_port, args=(target_ip, port))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
            
        return open_ports

    def _add_device(self, ip, mac, source):
        with self.lock:
            if ip not in self.found_devices:
                log.info(f"[{source}] New Device: {ip} ({mac})")
                self.found_devices[ip] = {
                    "mac": mac,
                    "vendor": "Unknown", # To be filled by Fingerprint
                    "ports": [],
                    "first_seen": time.time()
                }
