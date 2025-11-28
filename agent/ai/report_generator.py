"""
Human-Readable Security Report Generator

Generates professional, well-structured security reports in Markdown format
that can be easily converted to PDF or HTML.
"""

import json
from datetime import datetime
from typing import Dict, Any, List


def generate_executive_summary(report_data: Dict) -> str:
    """Generate executive summary section."""
    summary = report_data.get('final_report', {}).get('summary', {})

    risk_score = summary.get('overall_risk_score', 0)
    risk_level = summary.get('risk_level', 'UNKNOWN')
    total_devices = summary.get('total_devices', 0)
    total_cves = summary.get('total_cves', 0)
    critical_cves = summary.get('critical_cves', 0)

    # Risk level descriptions
    risk_descriptions = {
        'CRITICAL': 'The network is at immediate risk of compromise. Critical vulnerabilities exist that could allow attackers to gain full control of network devices.',
        'HIGH': 'The network has significant security weaknesses. Multiple high-severity vulnerabilities were identified that require urgent attention.',
        'MEDIUM': 'The network has moderate security concerns. Several vulnerabilities were found that should be addressed in a timely manner.',
        'LOW': 'The network has minor security issues. A few low-severity findings were identified for consideration.'
    }

    return f"""
## Executive Summary

**Assessment Date:** {datetime.now().strftime('%B %d, %Y at %H:%M')}

**Overall Risk Score:** {risk_score}/100 ({risk_level})

{risk_descriptions.get(risk_level, 'Unable to determine risk level.')}

### Key Metrics
| Metric | Value |
|--------|-------|
| Devices Scanned | {total_devices} |
| Total Vulnerabilities | {total_cves} |
| Critical Severity | {critical_cves} |
| High Severity | {summary.get('high_cves', 0)} |

"""


def generate_risk_gauge(score: int) -> str:
    """Generate ASCII risk gauge."""
    filled = score // 5
    empty = 20 - filled

    if score >= 80:
        indicator = "CRITICAL"
    elif score >= 60:
        indicator = "HIGH"
    elif score >= 40:
        indicator = "MEDIUM"
    else:
        indicator = "LOW"

    gauge = f"""
```
Risk Score: {score}/100 [{indicator}]
[{'=' * filled}{'-' * empty}]
 0        25        50        75       100
 LOW      MEDIUM    HIGH      CRITICAL
```
"""
    return gauge


def generate_device_inventory(report_data: Dict) -> str:
    """Generate device inventory section."""
    devices = report_data.get('devices', {})
    identifications = report_data.get('device_identifications', {})

    if not devices:
        return "\n## Device Inventory\n\nNo devices were discovered during the scan.\n"

    output = "\n## Device Inventory\n\n"
    output += f"A total of **{len(devices)} devices** were discovered on the network.\n\n"

    # Group by device type
    by_type = {}
    for ip, device in identifications.items():
        dtype = device.get('device_type', 'unknown')
        if dtype not in by_type:
            by_type[dtype] = []
        by_type[dtype].append({**device, 'ip': ip})

    output += "### Devices by Type\n\n"
    output += "| Type | Count | IPs |\n"
    output += "|------|-------|-----|\n"

    for dtype, devices_list in by_type.items():
        ips = ', '.join([d['ip'] for d in devices_list[:3]])
        if len(devices_list) > 3:
            ips += f" (+{len(devices_list) - 3} more)"
        output += f"| {dtype.title()} | {len(devices_list)} | {ips} |\n"

    output += "\n### Device Details\n\n"

    for ip, device in identifications.items():
        vendor = device.get('vendor', 'Unknown')
        dtype = device.get('device_type', 'Unknown')
        risk_score = device.get('risk_score', 0)

        risk_badge = ""
        if risk_score >= 70:
            risk_badge = " **[HIGH RISK]**"
        elif risk_score >= 40:
            risk_badge = " *[MEDIUM RISK]*"

        output += f"#### {ip} - {vendor} ({dtype.title()}){risk_badge}\n\n"

        # Show risk indicators if any
        indicators = device.get('risk_indicators', [])
        if indicators:
            output += "**Risk Indicators:**\n"
            for indicator in indicators:
                output += f"- {indicator}\n"
            output += "\n"

    return output


def generate_vulnerability_findings(report_data: Dict) -> str:
    """Generate vulnerability findings section."""
    cve_findings = report_data.get('cve_findings', {})

    if not cve_findings:
        return "\n## Vulnerability Assessment\n\nNo vulnerabilities were identified during this scan.\n"

    # Count and categorize
    all_cves = []
    for ip, cves in cve_findings.items():
        for cve in cves:
            cve['device_ip'] = ip
            all_cves.append(cve)

    critical = [c for c in all_cves if c.get('severity') == 'CRITICAL']
    high = [c for c in all_cves if c.get('severity') == 'HIGH']
    medium = [c for c in all_cves if c.get('severity') == 'MEDIUM']

    output = "\n## Vulnerability Assessment\n\n"
    output += f"The scan identified **{len(all_cves)} vulnerabilities** across {len(cve_findings)} devices.\n\n"

    output += "### Severity Distribution\n\n"
    output += "| Severity | Count | Percentage |\n"
    output += "|----------|-------|------------|\n"

    total = len(all_cves)
    if total > 0:
        output += f"| CRITICAL | {len(critical)} | {len(critical)*100//total}% |\n"
        output += f"| HIGH | {len(high)} | {len(high)*100//total}% |\n"
        output += f"| MEDIUM | {len(medium)} | {len(medium)*100//total}% |\n"

    # Critical vulnerabilities detail
    if critical:
        output += "\n### Critical Vulnerabilities (Immediate Action Required)\n\n"

        # Sort by CVSS
        critical.sort(key=lambda x: x.get('cvss_score', 0), reverse=True)

        for i, cve in enumerate(critical[:10], 1):  # Top 10
            cve_id = cve.get('cve_id', 'Unknown')
            cvss = cve.get('cvss_score', 0)
            desc = cve.get('description', '')[:200]
            device = cve.get('device_ip', 'Unknown')
            confidence = cve.get('confidence', 0.5)

            conf_label = "HIGH" if confidence > 0.7 else "MEDIUM" if confidence > 0.4 else "LOW"

            output += f"#### {i}. {cve_id} (CVSS: {cvss})\n\n"
            output += f"**Affected Device:** {device}\n\n"
            output += f"**Confidence:** {conf_label} ({confidence:.0%})\n\n"
            output += f"**Description:** {desc}...\n\n"
            output += "---\n\n"

    # High vulnerabilities summary
    if high:
        output += "\n### High Severity Vulnerabilities\n\n"
        output += "| CVE ID | Device | CVSS | Description |\n"
        output += "|--------|--------|------|-------------|\n"

        for cve in high[:10]:
            cve_id = cve.get('cve_id', 'Unknown')
            cvss = cve.get('cvss_score', 0)
            desc = cve.get('description', '')[:60] + '...'
            device = cve.get('device_ip', 'Unknown')
            output += f"| {cve_id} | {device} | {cvss} | {desc} |\n"

    return output


def generate_attack_scenarios(report_data: Dict) -> str:
    """Generate attack scenarios section."""
    attack_paths = report_data.get('attack_paths', [])

    if not attack_paths:
        return "\n## Attack Scenarios\n\nNo specific attack paths were modeled for this network.\n"

    output = "\n## Attack Scenarios\n\n"
    output += "The following attack scenarios describe how an adversary could potentially compromise the network.\n\n"

    for i, path in enumerate(attack_paths, 1):
        name = path.get('name', f'Attack Path {i}')
        description = path.get('description', '')
        entry = path.get('entry_point', 'Unknown')
        complexity = path.get('total_complexity', 'MEDIUM')
        likelihood = path.get('likelihood', 0.5)
        impact = path.get('impact', '')

        output += f"### Scenario {i}: {name}\n\n"
        output += f"**Entry Point:** {entry}\n\n"
        output += f"**Complexity:** {complexity}\n\n"
        output += f"**Likelihood:** {likelihood:.0%}\n\n"
        output += f"**Description:** {description}\n\n"

        steps = path.get('steps', [])
        if steps:
            output += "**Attack Steps:**\n\n"
            for step in steps:
                step_num = step.get('step_number', 0)
                action = step.get('action', '')
                output += f"{step_num}. {action}\n"
            output += "\n"

        if impact:
            output += f"**Impact:** {impact}\n\n"

        output += "---\n\n"

    return output


def generate_remediation_plan(report_data: Dict) -> str:
    """Generate remediation plan section."""
    remediation = report_data.get('remediation_steps', [])
    final_report = report_data.get('final_report', {})

    output = "\n## Remediation Plan\n\n"
    output += "The following actions are recommended to address the identified vulnerabilities, listed in priority order.\n\n"

    if not remediation:
        # Fall back to final_report remediation
        remediation = final_report.get('remediation_priority', [])

    if not remediation:
        output += "No specific remediation steps were generated.\n"
        return output

    # Group by urgency
    critical_actions = []
    high_actions = []
    medium_actions = []

    for step in remediation:
        priority = step.get('priority', 99)
        if priority <= 2:
            critical_actions.append(step)
        elif priority <= 5:
            high_actions.append(step)
        else:
            medium_actions.append(step)

    if critical_actions:
        output += "### Immediate Actions (Within 24 Hours)\n\n"
        for step in critical_actions:
            action = step.get('action', '')
            target = step.get('target_device', step.get('target', ''))
            cve = step.get('cve_addressed', '')
            impact = step.get('estimated_impact', '')

            output += f"- [ ] **{action}**\n"
            output += f"  - Target: {target}\n"
            if cve:
                output += f"  - Addresses: {cve}\n"
            if impact:
                output += f"  - Impact: {impact}\n"
            output += "\n"

    if high_actions:
        output += "### Short-Term Actions (Within 1 Week)\n\n"
        for step in high_actions:
            action = step.get('action', '')
            target = step.get('target_device', step.get('target', ''))

            output += f"- [ ] **{action}**\n"
            output += f"  - Target: {target}\n\n"

    if medium_actions:
        output += "### Medium-Term Actions (Within 1 Month)\n\n"
        for step in medium_actions:
            action = step.get('action', '')
            output += f"- [ ] {action}\n"

    return output


def generate_technical_appendix(report_data: Dict) -> str:
    """Generate technical appendix with raw data."""
    output = "\n## Technical Appendix\n\n"

    # Scan information
    scan_info = report_data.get('scan_info', {})
    output += "### Scan Information\n\n"
    output += f"- **Network Range:** {scan_info.get('network', 'N/A')}\n"
    output += f"- **Scan Timestamp:** {scan_info.get('timestamp', 'N/A')}\n"
    output += f"- **AI Model:** {scan_info.get('model', 'N/A')}\n\n"

    # Timing information
    timing = report_data.get('timing', {})
    if timing:
        output += "### Scan Timing\n\n"
        output += "| Phase | Duration |\n"
        output += "|-------|----------|\n"
        for phase, duration in timing.items():
            if isinstance(duration, (int, float)):
                output += f"| {phase.replace('_', ' ').title()} | {duration:.1f}s |\n"

    return output


def generate_full_report(report_data: Dict) -> str:
    """Generate the complete security report."""

    # Get summary for header
    summary = report_data.get('final_report', {}).get('summary', {})
    risk_level = summary.get('risk_level', 'UNKNOWN')
    risk_score = summary.get('overall_risk_score', 0)

    # Build the report
    report = f"""# Network Security Assessment Report

---

**Classification:** CONFIDENTIAL
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Assessment Type:** Automated IoT Security Scan
**Tool:** Eriska AI Security Scanner

---

{generate_risk_gauge(risk_score)}

{generate_executive_summary(report_data)}

{generate_device_inventory(report_data)}

{generate_vulnerability_findings(report_data)}

{generate_attack_scenarios(report_data)}

{generate_remediation_plan(report_data)}

{generate_technical_appendix(report_data)}

---

## Disclaimer

This report was generated by an automated security scanning tool. While the tool uses
AI-powered analysis and comprehensive vulnerability databases, findings should be verified
by qualified security professionals before taking action on critical systems.

**Confidence Levels:**
- **HIGH**: Strong evidence supports this finding
- **MEDIUM**: Likely accurate but may need verification
- **LOW**: Possible finding, requires manual confirmation

---

*Report generated by Eriska AI Security Scanner*
*Model: gemini-2.5-pro | Database: 209,350 CVEs | 38,432 OUI entries*
"""

    return report


def save_report(report_data: Dict, output_path: str = None) -> str:
    """Generate and save the report to a file."""
    report = generate_full_report(report_data)

    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'security_report_{timestamp}.md'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {output_path}")
    return output_path


def generate_html_report(report_data: Dict) -> str:
    """Generate HTML version of the report."""
    md_report = generate_full_report(report_data)

    # Simple markdown to HTML conversion
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Assessment Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .report {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px; margin-top: 30px; }}
        h3 {{ color: #34495e; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .critical {{ color: #e74c3c; font-weight: bold; }}
        .high {{ color: #e67e22; font-weight: bold; }}
        .medium {{ color: #f39c12; }}
        .low {{ color: #27ae60; }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{ background: #ecf0f1; padding: 2px 6px; border-radius: 3px; }}
        .risk-gauge {{
            background: linear-gradient(to right, #27ae60 0%, #f39c12 50%, #e74c3c 100%);
            height: 30px;
            border-radius: 15px;
            position: relative;
            margin: 20px 0;
        }}
        .disclaimer {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="report">
        <pre style="white-space: pre-wrap;">{md_report}</pre>
    </div>
</body>
</html>"""

    return html


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        "scan_info": {"network": "192.168.1.0/24", "timestamp": 1234567890, "model": "gemini-2.5-pro"},
        "devices": {"192.168.1.1": {"ip": "192.168.1.1", "mac": "00:11:22:33:44:55"}},
        "device_identifications": {
            "192.168.1.1": {"vendor": "TP-Link", "device_type": "router", "risk_score": 65}
        },
        "cve_findings": {
            "192.168.1.1": [
                {"cve_id": "CVE-2021-12345", "cvss_score": 9.8, "severity": "CRITICAL",
                 "description": "Test vulnerability", "confidence": 0.8}
            ]
        },
        "final_report": {
            "summary": {
                "total_devices": 1, "total_cves": 1, "critical_cves": 1,
                "high_cves": 0, "overall_risk_score": 75, "risk_level": "HIGH"
            }
        },
        "remediation_steps": [
            {"priority": 1, "action": "Update firmware", "target_device": "192.168.1.1",
             "cve_addressed": "CVE-2021-12345"}
        ]
    }

    report = generate_full_report(sample_data)
    print(report)
