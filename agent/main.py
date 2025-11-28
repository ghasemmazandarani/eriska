import argparse
import sys
import time
import os
from utils.logger import log
from utils.network import get_default_interface, get_local_ip, get_network_range
from core.discovery import DiscoveryEngine
from core.fingerprint import FingerprintEngine
from core.analysis import RiskAnalyzer
from core.credentials import CredentialTester
from core.router_scanner import RouterScanner
from core.camera_scanner import CameraScanner


def banner():
    print(r"""
    ███████╗██████╗ ██╗███████╗██╗  ██╗ █████╗
    ██╔════╝██╔══██╗██║██╔════╝██║ ██╔╝██╔══██╗
    █████╗  ██████╔╝██║███████╗█████╔╝ ███████║
    ██╔══╝  ██╔══██╗██║╚════██║██╔═██╗ ██╔══██║
    ███████╗██║  ██║██║███████║██║  ██╗██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
          IoT Security Agent - v0.2.0
    """)


from utils.reporter import Reporter

def run_router_mode(args):
    """اجرای حالت اسکن از طریق روتر"""
    reporter = Reporter()

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
        save_router_report(report)

        # 6. Upload Report
        reporter.upload_report(report, scan_type="router")

        # 7. Print summary
        print_router_summary(report)

        log.info("✅ Router interface scan completed successfully!")

    except KeyboardInterrupt:
        log.warning("⚠️ Scan interrupted by user")
    except Exception as e:
        log.error(f"❌ Router scan failed: {e}")


def run_network_scan(args):
    """اجرای حالت اسکن شبکه (active/passive)"""
    reporter = Reporter()

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
    log.info(f"Target Network: {target_network}")

    # 2. Start Discovery Engine
    discovery = DiscoveryEngine(iface)

    def save_report():
        """ذخیره گزارش اسکن شبکه"""
        import json

        timestamp = int(time.time())

        # JSON Report
        json_file = f"scan_report_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(discovery.found_devices, f, indent=2)
        
        # Upload Report
        reporter.upload_report(discovery.found_devices, scan_type="network")

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
                            data['vendor'] = onvif_data['info']

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

            # 3. Deep Probing
            ssdp_data = fp_engine.probe_ssdp(ip)
            if ssdp_data['is_upnp']:
                data['fingerprints']['ssdp'] = ssdp_data
                if ssdp_data.get('model'):
                    data['model'] = ssdp_data['model']
                if ssdp_data.get('info'):
                    data['vendor'] = ssdp_data['info']

            snmp_data = fp_engine.probe_snmp(ip)
            if snmp_data['is_snmp']:
                data['fingerprints']['snmp'] = snmp_data
                if snmp_data.get('info'):
                    data['os_info'] = snmp_data['info']

            # 4. Risk Analysis
            score, issues = risk_analyzer.analyze(data)
            data['risk_score'] = score
            data['risk_issues'] = issues

            log.info(f"Finished analysis for {ip} ({data['vendor']}) - Risk: {score}/100")

        save_report()


def save_router_report(report):
    """ذخیره گزارش اسکن روتر"""

    import json

    timestamp = int(time.time())

    # JSON Report
    json_file = f"router_scan_report_{timestamp}.json"
    with open(json_file, "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # HTML Report
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


def run_camera_mode(args):
    """اجرای حالت اسکن از طریق دوربین"""
    reporter = Reporter()

    try:
        # Create camera scanner instance
        camera_scanner = CameraScanner(
            camera_ip=args.camera_ip,
            username=args.camera_user,
            password=args.camera_pass,
            camera_type=args.camera_type
        )

        log.info("🎥 Starting Camera Interface Security Scan")

        # 1. Authenticate with camera
        if not camera_scanner.authenticate():
            log.error("❌ Failed to authenticate with camera")
            return

        # 2. Get camera information
        camera_info = camera_scanner.get_camera_info()
        log.info(f"📷 Camera: {camera_info.get('type', 'Unknown')} {camera_info.get('model', '')}")

        # 3. Analyze camera security
        security_issues = camera_scanner.analyze_camera_security()

        # 4. Generate comprehensive report
        report = camera_scanner.generate_report()

        # 5. Save reports
        save_camera_report(report)

        # 6. Upload Report
        reporter.upload_report(report, scan_type="camera")

        # 7. Print summary
        print_camera_summary(report)

        log.info("✅ Camera interface scan completed successfully!")

    except KeyboardInterrupt:
        log.warning("⚠️ Scan interrupted by user")
    except Exception as e:
        log.error(f"❌ Camera scan failed: {e}")


def save_camera_report(report):
    """ذخیره گزارش اسکن دوربین"""

    import json

    timestamp = int(time.time())

    # JSON Report
    json_file = f"camera_scan_report_{timestamp}.json"
    with open(json_file, "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # HTML Report
    html_file = f"camera_scan_report_{timestamp}.html"

    camera = report['camera_info']
    analysis = report['security_analysis']

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <title>Eriska Camera Security Report</title>
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
            .camera-info {{ background: #e8f4fd; border: 1px solid #bee5eb; }}
            .issue {{ margin-bottom: 15px; padding: 15px; border-radius: 5px; }}
            .critical {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
            .high {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
            .medium {{ background: #d1ecf1; border: 1px solid #bee5eb; }}
            .low {{ background: #d4edda; border: 1px solid #c3e6cb; }}
            .risk-meter {{
                width: 100%;
                height: 30px;
                border-radius: 15px;
                background: linear-gradient(to right, #28a745, #ffc107, #dc3545);
                position: relative;
            }}
            .risk-marker {{
                position: absolute;
                top: -10px;
                transform: translateX(-50%);
                background: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎥 Eriska Camera Security Report</h1>
            <p style="text-align: center; color: #666;">
                Target: {report['scan_info']['camera_ip']} |
                Time: {time.ctime(report['scan_info']['timestamp'])}
            </p>

            <!-- Camera Information -->
            <div class="card camera-info">
                <h2>📷 اطلاعات دوربین</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div><strong>IP Address:</strong> {camera.get('ip', 'Unknown')}</div>
                    <div><strong>Type:</strong> {camera.get('type', 'Unknown')}</div>
                    <div><strong>Model:</strong> {camera.get('model', 'Unknown')}</div>
                    <div><strong>Firmware:</strong> {camera.get('firmware', 'Unknown')}</div>
                    <div><strong>MAC Address:</strong> {camera.get('mac', 'Unknown')}</div>
                    <div><strong>Serial Number:</strong> {camera.get('serial', 'Unknown')}</div>
                </div>
            </div>

            <!-- Security Analysis -->
            <div class="card">
                <h2>🔒 تحلیل امنیتی</h2>

                <div style="margin-bottom: 30px;">
                    <h3>امتیاز ریسک: <span style="font-size: 2em; color: {'#dc3545' if analysis['risk_score'] >= 70 else '#ffc107' if analysis['risk_score'] >= 40 else '#28a745'}">{analysis['risk_score']}/100</span></h3>

                    <div class="risk-meter">
                        <div class="risk-marker" style="left: {analysis['risk_score']}%;">
                            {analysis['risk_score']}
                        </div>
                    </div>
                </div>

                <h3>مسائل امنیتی ({len(analysis['issues'])})</h3>
    """

    # Add security issues
    for issue in analysis['issues']:
        severity_class = issue['severity'].lower()
        html_content += f"""
                <div class="issue {severity_class}">
                    <strong style="color: #dc3545; font-size: 1.1em;">
                        {issue['severity']}: {issue['type']}
                    </strong>
                    <p style="margin: 5px 0;">{issue['description']}</p>
                    <p style="margin: 5px 0;"><strong>پیشنهاد:</strong> {issue['recommendation']}</p>
                </div>
        """

    # Add recommendations
    html_content += """
                <h3>پیشنهادات اصلاحی</h3>
                <ul style="list-style: none; padding: 0;">
    """

    for rec in analysis['recommendations']:
        html_content += f"""
                    <li style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <strong style="color: #007bff;">{rec['priority']}:</strong> {rec['action']}
                        <br><small style="color: #666;">{rec['details']}</small>
                    </li>
        """

    html_content += """
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

    with open(html_file, "w", encoding='utf-8') as f:
        f.write(html_content)

    log.info(f"📄 Reports saved: {json_file}, {html_file}")


def run_ai_mode(args):
    """اجرای حالت AI با LangGraph multi-agent workflow"""
    from dotenv import load_dotenv

    # Load environment variables
    env_file = os.path.join(os.path.dirname(__file__), '..', 'test.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)

    # Get API key
    api_key = args.api_key or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        # Try to get from GEMINI_API_KEYS (comma-separated)
        keys = os.environ.get('GEMINI_API_KEYS', '')
        if keys:
            api_key = keys.split(',')[0].strip()

    if not api_key:
        log.critical("AI mode requires Gemini API key. Use --api-key or set GEMINI_API_KEY environment variable")
        sys.exit(1)

    # Determine network range
    if args.target:
        network_range = args.target
    else:
        iface = args.iface or get_default_interface()
        if not iface:
            log.critical("Could not determine network interface. Use --target to specify network range.")
            sys.exit(1)
        local_ip = get_local_ip(iface)
        if not local_ip:
            log.critical(f"Could not get IP address for interface {iface}.")
            sys.exit(1)
        network_range = get_network_range(local_ip, "255.255.255.0")

    log.info("🤖 Starting AI-Powered Security Analysis")
    log.info(f"Target Network: {network_range}")
    log.info(f"Mode: {'Continuous Monitoring' if args.continuous else 'Single Scan'}")

    try:
        # Import AI module
        from ai.graph import run_security_analysis_sync, run_sequential_analysis

        if args.debug:
            log.info("Running in debug mode (sequential execution)")
            final_state = run_sequential_analysis(network_range, api_key)
        else:
            final_state = run_security_analysis_sync(
                network_range=network_range,
                api_key=api_key,
                continuous=args.continuous,
                scan_interval=args.interval
            )

        # Save AI report
        if final_state and final_state.get('final_report'):
            save_ai_report(final_state)

        log.info("✅ AI Security Analysis completed!")

    except ImportError as e:
        log.error(f"Failed to import AI module: {e}")
        log.error("Make sure all dependencies are installed: pip install langgraph langchain-google-genai")
        sys.exit(1)
    except KeyboardInterrupt:
        log.warning("⚠️ Scan interrupted by user")
    except Exception as e:
        log.error(f"❌ AI analysis failed: {e}")
        import traceback
        traceback.print_exc()


def save_ai_report(state):
    """ذخیره گزارش AI"""
    import json

    timestamp = int(time.time())
    report = state.get('final_report', {})

    # JSON Report
    json_file = f"ai_security_report_{timestamp}.json"
    with open(json_file, "w", encoding='utf-8') as f:
        json.dump({
            'report': report,
            'devices': state.get('devices', {}),
            'device_identifications': state.get('device_identifications', {}),
            'cve_findings': state.get('cve_findings', {}),
            'attack_paths': state.get('attack_paths', []),
            'remediation_steps': state.get('remediation_steps', []),
            'timing': state.get('timing', {})
        }, f, indent=2, ensure_ascii=False, default=str)

    # HTML Report
    html_file = f"ai_security_report_{timestamp}.html"
    summary = report.get('summary', {})

    risk_color = '#dc3545' if summary.get('risk_level') == 'CRITICAL' else \
                 '#fd7e14' if summary.get('risk_level') == 'HIGH' else \
                 '#ffc107' if summary.get('risk_level') == 'MEDIUM' else '#28a745'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Eriska AI Security Report</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #1a1a2e;
                color: #eee;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{
                text-align: center;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .header h1 {{ margin: 0; font-size: 2.5em; }}
            .header p {{ margin: 10px 0 0; opacity: 0.9; }}
            .card {{
                background: #16213e;
                padding: 25px;
                margin-bottom: 20px;
                border-radius: 12px;
                border: 1px solid #0f3460;
            }}
            .card h2 {{
                margin-top: 0;
                color: #e94560;
                border-bottom: 2px solid #0f3460;
                padding-bottom: 10px;
            }}
            .risk-score {{
                font-size: 4em;
                font-weight: bold;
                color: {risk_color};
                text-align: center;
            }}
            .risk-level {{
                text-align: center;
                font-size: 1.5em;
                color: {risk_color};
                margin-bottom: 20px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .stat {{
                background: #0f3460;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #e94560; }}
            .stat-label {{ color: #aaa; margin-top: 5px; }}
            .risk-item {{
                background: #0f3460;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #e94560;
            }}
            .remediation {{
                background: #0f3460;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }}
            .priority {{ color: #ffc107; font-weight: bold; }}
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
            }}
            .critical {{ background: #dc3545; }}
            .high {{ background: #fd7e14; }}
            .medium {{ background: #ffc107; color: #000; }}
            .low {{ background: #28a745; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Eriska AI Security Report</h1>
                <p>Powered by Multi-Agent LangGraph Analysis</p>
                <p>Generated: {time.ctime()}</p>
            </div>

            <div class="card">
                <h2>📊 Risk Assessment</h2>
                <div class="risk-score">{summary.get('overall_risk_score', 0)}/100</div>
                <div class="risk-level">{summary.get('risk_level', 'UNKNOWN')} RISK</div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{summary.get('total_devices', 0)}</div>
                        <div class="stat-label">Devices Scanned</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{summary.get('total_cves', 0)}</div>
                        <div class="stat-label">CVEs Found</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{summary.get('critical_cves', 0)}</div>
                        <div class="stat-label">Critical CVEs</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{summary.get('attack_paths', 0)}</div>
                        <div class="stat-label">Attack Paths</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>⚠️ Top Risks</h2>
    """

    for risk in report.get('top_risks', []):
        severity_class = risk.get('severity', 'medium').lower()
        html_content += f"""
                <div class="risk-item">
                    <strong>{risk.get('device', 'Unknown')}</strong>
                    <span class="badge {severity_class}">{risk.get('severity', 'UNKNOWN')}</span>
                    <br>
                    <span style="color: #aaa;">{risk.get('cve', 'N/A')} - CVSS: {risk.get('cvss', 'N/A')}</span>
                </div>
        """

    html_content += """
            </div>

            <div class="card">
                <h2>🔧 Priority Remediation</h2>
    """

    for step in report.get('remediation_priority', []):
        html_content += f"""
                <div class="remediation">
                    <span class="priority">#{step.get('priority', '?')}</span>
                    <strong>{step.get('action', 'Unknown action')}</strong>
                    <br>
                    <span style="color: #aaa;">Target: {step.get('target', 'N/A')} | Impact: {step.get('impact', 'N/A')}</span>
                </div>
        """

    html_content += """
            </div>
        </div>
    </body>
    </html>
    """

    with open(html_file, "w", encoding='utf-8') as f:
        f.write(html_content)

    log.info(f"📄 AI Reports saved: {json_file}, {html_file}")


def print_camera_summary(report):
    """چاپ خلاصه نتایج اسکن دوربین"""

    print(f"\n{'='*60}")
    print(f"🎥 CAMERA INTERFACE SECURITY SCAN RESULTS")
    print(f"{'='*60}")

    # Camera info
    camera = report['camera_info']
    print(f"\n📷 Camera Information:")
    print(f"   IP: {camera.get('ip', 'Unknown')}")
    print(f"   Type: {camera.get('type', 'Unknown')}")
    print(f"   Model: {camera.get('model', 'Unknown')}")
    print(f"   Firmware: {camera.get('firmware', 'Unknown')}")

    # Security analysis
    analysis = report['security_analysis']
    print(f"\n🔒 Security Analysis:")
    print(f"   Risk Score: {analysis['risk_score']}/100")
    print(f"   Total Issues: {len(analysis['issues'])}")

    # Security issues
    if analysis['issues']:
        print(f"\n⚠️  Security Issues:")
        for issue in analysis['issues']:
            severity_emoji = "🔴" if issue['severity'] == 'CRITICAL' else "🟡" if issue['severity'] == 'HIGH' else "🟠"
            print(f"   {severity_emoji} {issue['severity']}: {issue['type']}")
            print(f"      {issue['description']}")

    print(f"{'='*60}")


def main():
    banner()

    parser = argparse.ArgumentParser(description="Eriska IoT Security Agent")
    parser.add_argument("--mode", choices=["active", "passive", "router", "camera", "ai"], default="active", help="Scan mode")
    parser.add_argument("--iface", help="Network interface to use")
    parser.add_argument("--test-creds", action="store_true", help="Test default credentials (Aggressive)")
    parser.add_argument("--connect", help="Connect agent to dashboard using a connection token")

    # Router mode specific arguments
    parser.add_argument("--router-ip", help="Router IP address (required for router mode)")
    parser.add_argument("--router-user", default="admin", help="Router username (default: admin)")
    parser.add_argument("--router-pass", help="Router password (required for router mode)")
    parser.add_argument("--router-type", choices=["tp-link", "d-link", "asus", "netgear", "auto"], default="auto", help="Router type (default: auto-detect)")

    # Camera mode specific arguments
    parser.add_argument("--camera-ip", help="Camera IP address (required for camera mode)")
    parser.add_argument("--camera-user", default="admin", help="Camera username (default: admin)")
    parser.add_argument("--camera-pass", help="Camera password (required for camera mode)")
    parser.add_argument("--camera-type", choices=["hikvision", "dahua", "axis", "auto"], default="auto", help="Camera type (default: auto-detect)")

    # AI mode specific arguments
    parser.add_argument("--api-key", help="Gemini API key for AI mode (or set GEMINI_API_KEY env var)")
    parser.add_argument("--target", help="Target network range in CIDR notation (e.g., 192.168.1.0/24)")
    parser.add_argument("--continuous", action="store_true", help="Enable continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=300, help="Scan interval in seconds for continuous mode (default: 300)")
    parser.add_argument("--debug", action="store_true", help="Run AI in debug mode (sequential execution)")

    args = parser.parse_args()

    # Handle connection
    if args.connect:
        reporter = Reporter()
        if reporter.connect(args.connect):
            sys.exit(0)
        else:
            sys.exit(1)

    # Validate router mode arguments
    if args.mode == "router":
        if not args.router_ip or not args.router_pass:
            log.critical("Router mode requires --router-ip and --router-pass arguments")
            sys.exit(1)

        log.info("🚀 Starting Router Interface Mode")
        log.info(f"Target Router: {args.router_ip}")
        log.info(f"Router Username: {args.router_user}")

        return run_router_mode(args)

    # Validate camera mode arguments
    if args.mode == "camera":
        if not args.camera_ip or not args.camera_pass:
            log.critical("Camera mode requires --camera-ip and --camera-pass arguments")
            sys.exit(1)

        log.info("🎥 Starting Camera Interface Mode")
        log.info(f"Target Camera: {args.camera_ip}")
        log.info(f"Camera Username: {args.camera_user}")

        return run_camera_mode(args)

    # AI mode - LangGraph multi-agent security analysis
    if args.mode == "ai":
        log.info("🤖 Starting AI-Powered Security Analysis Mode")
        return run_ai_mode(args)

    # For active/passive modes - run network scan
    return run_network_scan(args)


if __name__ == "__main__":
    main()