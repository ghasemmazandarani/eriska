import argparse
import sys
import time
from utils.logger import log
from utils.network import get_default_interface, get_local_ip, get_network_range
from core.discovery import DiscoveryEngine
from core.fingerprint import FingerprintEngine
from core.analysis import RiskAnalyzer
from core.router_scanner import RouterScanner

def banner():
    print(r"""
    ███████╗██████╗ ██╗███████╗██╗  ██╗ █████╗ 
    ██╔════╝██╔══██╗██║██╔════╝██║ ██╔╝██╔══██╗
    █████╗  ██████╔╝██║███████╗█████╔╝ ███████║
    ██╔══╝  ██╔══██╗██║╚════██║██╔═██╗ ██╔══██║
    ███████╗██║  ██║██║███████║██║  ██╗██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
          IoT Security Agent - v0.1.0
    """)

def main():
    banner()
    parser = argparse.ArgumentParser(description="Eriska IoT Security Agent")
    parser.add_argument("--mode", choices=["active", "passive", "router"], default="active", help="Scan mode")
    parser.add_argument("--iface", help="Network interface to use")
    parser.add_argument("--test-creds", action="store_true", help="Test default credentials (Aggressive)")

    # Router mode specific arguments
    parser.add_argument("--router-ip", help="Router IP address (required for router mode)")
    parser.add_argument("--router-user", default="admin", help="Router username (default: admin)")
    parser.add_argument("--router-pass", help="Router password (required for router mode)")
    parser.add_argument("--router-type", choices=["tp-link", "d-link", "asus", "netgear", "auto"], default="auto", help="Router type (default: auto-detect)")
    
    args = parser.parse_args()

    # Validate router mode arguments
    if args.mode == "router":
        if not args.router_ip or not args.router_pass:
            log.critical("Router mode requires --router-ip and --router-pass arguments")
            sys.exit(1)

        # Router mode - Skip network setup
        log.info("🚀 Starting Router Interface Mode")
        log.info(f"Target Router: {args.router_ip}")
        log.info(f"Router Username: {args.router_user}")

        return run_router_mode(args)

def run_router_mode(args):
    """اجرای حالت اسکن از طریق روتر"""

    try:
        # Create router scanner instance
        router_scanner = RouterScanner(
            router_ip=args.router_ip,
            username=args.router_user,
            password=args.router_pass,
            router_type=args.router_type
        )

        log.info("🚀 Starting Router Interface Security Scan")

        # 1. Authenticate with router
        if not router_scanner.authenticate():
            log.error("❌ Failed to authenticate with router")
            return

        # 2. Get router information
        router_info = router_scanner.get_router_info()
        log.info(f"📡 Router: {router_info.get('type', 'Unknown')} {router_info.get('model', '')}")

        # 3. Get connected devices
        devices = router_scanner.get_connected_devices()

        # 4. Generate comprehensive report
        report = router_scanner.generate_report()

        # 5. Save reports
        save_router_report(report, devices)

        # 6. Print summary
        print_router_summary(report)

        log.info("✅ Router interface scan completed successfully!")

    except KeyboardInterrupt:
        log.warning("⚠️ Scan interrupted by user")
    except Exception as e:
        log.error(f"❌ Router scan failed: {e}")

def save_router_report(report, devices):
    """ذخیره گزارش اسکن روتر"""

    import json

    timestamp = int(time.time())

    # JSON Report
    json_file = f"router_scan_report_{timestamp}.json"
    with open(json_file, "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # HTML Report (Enhanced for router mode)
    html_file = f"router_scan_report_{timestamp}.html"

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <title>Eriska Router Security Report</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Vazirmatn, Arial, sans-serif;
                margin: 20px;
                background: #f0f2f5;
                direction: rtl;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .high-risk {{ border-left: 5px solid #dc3545; }}
            .med-risk {{ border-left: 5px solid #ffc107; }}
            .low-risk {{ border-left: 5px solid #28a745; }}
            h1 {{ color: #333; text-align: center; }}
            .router-info {{ background: #e8f4fd; border: 1px solid #bee5eb; }}
            .stats {{ display: flex; gap: 20px; justify-content: space-around; }}
            .stat-box {{ text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; border: 1px solid #ddd; text-align: right; }}
            th {{ background: #f8f9fa; }}
            .badge {{
                padding: 5px 10px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            .bg-red {{ background: #dc3545; }}
            .bg-yellow {{ background: #ffc107; color: #212529; }}
            .bg-green {{ background: #28a745; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Eriska Router Security Report</h1>
            <p style="text-align: center; color: #666;">
                Target: {report['scan_info']['router_ip']} |
                Time: {time.ctime(report['scan_info']['timestamp'])}
            </p>

            <!-- Router Information -->
            <div class="card router-info">
                <h2>📡 اطلاعات روتر</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div><strong>IP Address:</strong> {report['router_info'].get('ip', 'Unknown')}</div>
                    <div><strong>Type:</strong> {report['router_info'].get('type', 'Unknown')}</div>
                    <div><strong>Model:</strong> {report['router_info'].get('model', 'Unknown')}</div>
                    <div><strong>Firmware:</strong> {report['router_info'].get('firmware', 'Unknown')}</div>
                </div>
            </div>

            <!-- Statistics -->
            <div class="card">
                <h2>📊 آمار کلی</h2>
                <div class="stats">
                    <div class="stat-box">
                        <div style="font-size: 2em; color: #007bff;">{report['summary']['total_devices']}</div>
                        <div>کل دستگاه‌ها</div>
                    </div>
                    <div class="stat-box">
                        <div style="font-size: 2em; color: #28a745;">{report['summary']['wireless_devices']}</div>
                        <div>دستگاه‌های بی‌سیم</div>
                    </div>
                    <div class="stat-box">
                        <div style="font-size: 2em; color: #17a2b8;">{report['summary']['wired_devices']}</div>
                        <div>دستگاه‌های سیمی</div>
                    </div>
                    <div class="stat-box">
                        <div style="font-size: 2em; color: #dc3545;">{report['summary']['high_risk_devices']}</div>
                        <div>دستگاه‌های پرریسک</div>
                    </div>
                </div>
            </div>

            <!-- Device List -->
            <div class="card">
                <h2>📱 لیست دستگاه‌های متصل</h2>
                <table>
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>MAC Address</th>
                            <th>Hostname</th>
                            <th>Type</th>
                            <th>Connection</th>
                            <th>Vendor</th>
                            <th>Risk Score</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for device in report['devices']:
        risk_score = device.get('risk_score', 0)
        risk_class = "high-risk" if risk_score >= 70 else "med-risk" if risk_score >= 40 else "low-risk"
        badge_color = "bg-red" if risk_score >= 70 else "bg-yellow" if risk_score >= 40 else "bg-green"

        html_content += f"""
                        <tr class="{risk_class}">
                            <td>{device.get('ip', 'Unknown')}</td>
                            <td>{device.get('mac', 'Unknown')}</td>
                            <td>{device.get('hostname', 'Unknown')}</td>
                            <td>{device.get('type', 'Unknown')}</td>
                            <td>{device.get('connection_type', 'Unknown')}</td>
                            <td>{device.get('vendor', 'Unknown')}</td>
                            <td>
                                <span class="badge {badge_color}">
                                    {risk_score}/100
                                </span>
                            </td>
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    with open(html_file, "w", encoding='utf-8') as f:
        f.write(html_content)

    log.info(f"📄 Reports saved: {json_file}, {html_file}")

def print_router_summary(report):
    """چاپ خلاصه نتایج اسکن روتر"""

    print(f"\n{'='*60}")
    print(f"🔍 ROUTER INTERFACE SECURITY SCAN RESULTS")
    print(f"{'='*60}")

    # Router info
    router = report['router_info']
    print(f"\n📡 Router Information:")
    print(f"   IP: {router.get('ip', 'Unknown')}")
    print(f"   Type: {router.get('type', 'Unknown')}")
    print(f"   Model: {router.get('model', 'Unknown')}")
    print(f"   Firmware: {router.get('firmware', 'Unknown')}")

    # Summary
    summary = report['summary']
    print(f"\n📊 Network Summary:")
    print(f"   Total Devices: {summary['total_devices']}")
    print(f"   Wireless Devices: {summary['wireless_devices']}")
    print(f"   Wired Devices: {summary['wired_devices']}")
    print(f"   High Risk Devices: {summary['high_risk_devices']}")

    # High risk devices
    high_risk_devices = [d for d in report['devices'] if d.get('risk_score', 0) >= 70]
    if high_risk_devices:
        print(f"\n⚠️  High Risk Devices:")
        for device in high_risk_devices:
            print(f"   - {device['ip']:<15} {device['mac']:<18} {device.get('hostname', 'Unknown'):<20} (Risk: {device['risk_score']})")

    print(f"{'='*60}")

# Original main function continues for active/passive modes
def run_network_scan(args):
    """اجرای حالت اسکن شبکه (active/passive)"""

    # 1. Setup Network
    iface = args.iface or get_default_interface()
    if not iface:
        log.critical("Could not determine network interface. Exiting.")
        sys.exit(1)

    local_ip = get_local_ip(iface)
    if not local_ip:
        log.critical(f"Could not get IP address for interface {iface}. Exiting.")
        sys.exit(1)

    target_network = get_network_range(local_ip, "255.255.255.0")

    log.info(f"Interface: {iface}")
    log.info(f"Local IP: {local_ip}")
    # 2. Start Engines
    discovery = DiscoveryEngine(iface)
    
    def save_report():
        import json
        timestamp = int(time.time())
        
        # JSON Report
        json_file = f"scan_report_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(discovery.found_devices, f, indent=2)
            
        # HTML Report
        html_file = f"scan_report_{timestamp}.html"
        html_content = f"""
        <html>
        <head>
            <title>Eriska Security Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }}
                .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .high-risk {{ border-left: 5px solid #dc3545; }}
                .med-risk {{ border-left: 5px solid #ffc107; }}
                .low-risk {{ border-left: 5px solid #28a745; }}
                h1 {{ color: #333; }}
                .badge {{ padding: 5px 10px; border-radius: 4px; color: white; font-weight: bold; }}
                .bg-red {{ background: #dc3545; }}
                .bg-yellow {{ background: #ffc107; }}
                .bg-green {{ background: #28a745; }}
            </style>
        </head>
        <body>
            <h1>Eriska Security Scan Report</h1>
            <p>Target: {target_network} | Time: {time.ctime()}</p>
        """
        
        for ip, data in discovery.found_devices.items():
            score = data.get('risk_score', 0)
            risk_class = "high-risk" if score > 70 else "med-risk" if score > 30 else "low-risk"
            badge_color = "bg-red" if score > 70 else "bg-yellow" if score > 30 else "bg-green"
            
            html_content += f"""
            <div class="card {risk_class}">
                <h3>{ip} <span class="badge {badge_color}">Risk: {score}/100</span></h3>
                <p><strong>Vendor:</strong> {data.get('vendor', 'Unknown')}</p>
                <p><strong>MAC:</strong> {data.get('mac', 'Unknown')}</p>
                <p><strong>Ports:</strong> {', '.join(map(str, data.get('ports', [])))}</p>
            """
            
            if data.get('risk_issues'):
                html_content += "<h4>Risk Issues:</h4><ul>"
                for issue in data['risk_issues']:
                    html_content += f"<li style='color: #dc3545'>{issue}</li>"
                html_content += "</ul>"
                
            html_content += "</div>"
            
        html_content += "</body></html>"
        
        with open(html_file, "w") as f:
            f.write(html_content)
            
        log.info(f"Reports saved: {json_file}, {html_file}")

    if args.mode == "passive":
        discovery.start_passive()
        log.info("Passive Listener started. Press Ctrl+C to stop.")
        try:
            last_save = time.time()
            while True:
                time.sleep(1)
                # Auto-save every 60 seconds
                if time.time() - last_save > 60:
                    save_report()
                    last_save = time.time()
                    
        except KeyboardInterrupt:
            log.info("Stopping agent...")
        finally:
            save_report()
    else:
        log.info("Starting Active Discovery...")
        devices = discovery.scan_network(target_network)
        
        # Scan ports for found devices
        for ip, data in devices.items():
            log.info(f"Scanning ports for {ip}...")
            open_ports = discovery.scan_ports(ip)
            if open_ports:
                log.info(f"Open ports on {ip}: {open_ports}")
                data['ports'] = open_ports

        # Fingerprint & Analyze
        log.info("Starting Fingerprinting & Analysis...")
        fp_engine = FingerprintEngine()
        risk_analyzer = RiskAnalyzer()
        
        # Initialize Credential Tester if requested
        cred_tester = None
        if args.test_creds:
            from core.credentials import CredentialTester
            cred_tester = CredentialTester()
            log.warning("⚠️  Credential Testing Enabled (Aggressive Mode)")
        
        for ip, data in devices.items():
            # 1. OUI Lookup
            data['vendor'] = fp_engine.lookup_oui(data['mac'])
            data['fingerprints'] = {}
            
            # 2. Service Probing
            for port in data.get('ports', []):
                if port in [80, 8080, 8000]:
                    # HTTP Probe
                    http_data = fp_engine.probe_http(ip, port)
                    data['fingerprints'][f'http_{port}'] = http_data
                    
                    # Credential Test (HTTP)
                    if cred_tester:
                        is_vuln, user, password = cred_tester.test_http_auth(ip, port)
                        if is_vuln:
                            data['vulnerable_creds'] = {'user': user, 'pass': password, 'port': port}
                    
                    # ONVIF Probe (Try on same port)
                    onvif_data = fp_engine.probe_onvif(ip, port)
                    if onvif_data['is_onvif']:
                        data['fingerprints'][f'onvif_{port}'] = onvif_data
                        data['type'] = "Camera (ONVIF)"
                        if onvif_data.get('info'):
                            data['vendor'] = onvif_data['info'] # Update vendor with specific info
                    
                elif port == 443:
                    https_data = fp_engine.probe_http(ip, port, use_ssl=True)
                    data['fingerprints'][f'https_{port}'] = https_data
                    
                elif port == 554:
                    rtsp_data = fp_engine.probe_rtsp(ip, port)
                    data['fingerprints'][f'rtsp_{port}'] = rtsp_data
                
                else:
                    # Generic Port Mapping
                    service_name = fp_engine.guess_service(port)
                    if service_name != "Unknown":
                        data['fingerprints'][f'tcp_{port}'] = {"service": service_name}

            # 3. Deep Probing (SNMP & SSDP) - Try regardless of ports if we want deep info
            # Or trigger based on open ports (161, 1900) - but SSDP is UDP so port scan might miss it
            
            # SSDP Probe (Good for IoT/Routers)
            ssdp_data = fp_engine.probe_ssdp(ip)
            if ssdp_data['is_upnp']:
                data['fingerprints']['ssdp'] = ssdp_data
                if ssdp_data.get('model'):
                    data['model'] = ssdp_data['model']
                if ssdp_data.get('info'):
                    data['vendor'] = ssdp_data['info']

            # SNMP Probe (Good for Infrastructure)
            snmp_data = fp_engine.probe_snmp(ip)
            if snmp_data['is_snmp']:
                data['fingerprints']['snmp'] = snmp_data
                if snmp_data.get('info'):
                    data['os_info'] = snmp_data['info']

            # 4. Risk Analysis
            score, issues = risk_analyzer.analyze(data)
            data['risk_score'] = score
            data['risk_issues'] = issues

            log.info(f"Finished analysis for {ip} ({data['vendor']}) - Risk: {score}/100 - Issues: {len(issues)}")

        save_report()

if __name__ == "__main__":
    main()

