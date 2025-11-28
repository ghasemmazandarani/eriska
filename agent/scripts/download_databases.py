"""
Database Download Script for Eriska AI Security Agent

Downloads and processes:
1. CVE Database from NVD (National Vulnerability Database)
2. OUI Database from IEEE (MAC address to vendor mapping)
3. MITRE ATT&CK patterns

Usage:
    python download_databases.py --all              # Download everything
    python download_databases.py --cve              # Download CVE only
    python download_databases.py --oui              # Download OUI only
    python download_databases.py --attack           # Download ATT&CK only
    python download_databases.py --cve --years 2023 2024  # Specific years
"""

import os
import sys
import json
import gzip
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Data directories
BASE_DIR = Path(__file__).parent.parent / "agent" / "ai" / "data"
CVE_DIR = BASE_DIR / "cve"
OUI_DIR = BASE_DIR / "oui"
ATTACK_DIR = BASE_DIR / "attack"

# IoT-relevant vendors and products to filter CVEs
IOT_KEYWORDS = [
    # Camera vendors
    "hikvision", "dahua", "axis", "foscam", "reolink", "amcrest", "wyze",
    "uniview", "vivotek", "hanwha", "bosch", "pelco", "avigilon",

    # Router vendors
    "tp-link", "tplink", "d-link", "dlink", "netgear", "asus", "linksys",
    "tenda", "xiaomi", "huawei", "zte", "mikrotik", "ubiquiti", "cisco",

    # Smart home
    "tuya", "tasmota", "shelly", "sonoff", "philips hue", "ring", "nest",
    "ecobee", "honeywell", "samsung smartthings", "wemo", "belkin",

    # NAS
    "synology", "qnap", "western digital", "wd", "seagate", "buffalo",

    # Protocols and services
    "upnp", "onvif", "rtsp", "telnet", "mqtt", "coap", "zigbee", "zwave",

    # Generic IoT terms
    "iot", "smart home", "ip camera", "nvr", "dvr", "router", "gateway",
    "access point", "firmware", "embedded"
]


def print_progress(current: int, total: int, prefix: str = "", suffix: str = ""):
    """Print a progress bar."""
    bar_length = 40
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "=" * filled + "-" * (bar_length - filled)
    percent = (current / total * 100) if total > 0 else 0
    print(f"\r{prefix} [{bar}] {percent:.1f}% {suffix}", end="", flush=True)


def download_file(url: str, dest_path: Path, description: str = "") -> bool:
    """Download a file with progress indication."""
    print(f"\nDownloading: {description or url}")

    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    print_progress(downloaded, total_size, "Progress:", f"{downloaded//1024}KB")

        print(f"\n  Saved to: {dest_path}")
        return True

    except requests.RequestException as e:
        print(f"\n  ERROR: {e}")
        return False


def download_oui_database() -> bool:
    """Download IEEE OUI database (MAC address to vendor mapping)."""
    print("\n" + "="*60)
    print("DOWNLOADING OUI DATABASE (IEEE)")
    print("="*60)

    OUI_DIR.mkdir(parents=True, exist_ok=True)

    # Download OUI.txt
    oui_url = "https://standards-oui.ieee.org/oui/oui.txt"
    oui_path = OUI_DIR / "oui.txt"

    if not download_file(oui_url, oui_path, "IEEE OUI Database"):
        return False

    # Parse and create JSON version for faster lookup
    print("\nParsing OUI database...")
    oui_dict = {}

    try:
        with open(oui_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if "(hex)" in line:
                    parts = line.split("(hex)")
                    if len(parts) >= 2:
                        mac_prefix = parts[0].strip().replace("-", ":").upper()
                        vendor = parts[1].strip()
                        oui_dict[mac_prefix] = vendor

        # Save as JSON
        json_path = OUI_DIR / "oui.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(oui_dict, f, indent=2)

        print(f"  Parsed {len(oui_dict)} OUI entries")
        print(f"  Saved JSON to: {json_path}")
        return True

    except Exception as e:
        print(f"  ERROR parsing OUI: {e}")
        return False


def download_attack_patterns() -> bool:
    """Download MITRE ATT&CK framework data."""
    print("\n" + "="*60)
    print("DOWNLOADING MITRE ATT&CK PATTERNS")
    print("="*60)

    ATTACK_DIR.mkdir(parents=True, exist_ok=True)

    attacks = [
        ("Enterprise ATT&CK", "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json", "enterprise-attack.json"),
        ("ICS ATT&CK", "https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json", "ics-attack.json"),
    ]

    success = True
    for name, url, filename in attacks:
        path = ATTACK_DIR / filename
        if not download_file(url, path, name):
            success = False
            continue

        # Extract relevant techniques
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            techniques = []
            for obj in data.get('objects', []):
                if obj.get('type') == 'attack-pattern':
                    tech = {
                        'id': obj.get('external_references', [{}])[0].get('external_id', ''),
                        'name': obj.get('name', ''),
                        'description': obj.get('description', '')[:500],
                        'tactics': [p.get('phase_name') for p in obj.get('kill_chain_phases', [])],
                        'platforms': obj.get('x_mitre_platforms', []),
                    }
                    techniques.append(tech)

            # Save simplified version
            simple_path = ATTACK_DIR / filename.replace('.json', '_simplified.json')
            with open(simple_path, 'w', encoding='utf-8') as f:
                json.dump(techniques, f, indent=2)

            print(f"  Extracted {len(techniques)} attack techniques")

        except Exception as e:
            print(f"  WARNING: Could not parse {filename}: {e}")

    return success


def download_cve_database(years: List[int] = None, nvd_api_key: str = None) -> bool:
    """
    Download CVE database from NVD using API 2.0.

    Args:
        years: List of years to download (default: last 3 years)
        nvd_api_key: Optional NVD API key for higher rate limits
    """
    import time

    print("\n" + "="*60)
    print("DOWNLOADING CVE DATABASE (NVD API 2.0)")
    print("="*60)

    CVE_DIR.mkdir(parents=True, exist_ok=True)

    if years is None:
        current_year = datetime.now().year
        years = [current_year, current_year - 1, current_year - 2]

    # NVD API 2.0 endpoint
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    all_cves = []
    iot_cves = []

    headers = {}
    if nvd_api_key:
        headers['apiKey'] = nvd_api_key
        print("  Using API key for higher rate limits")

    # Rate limiting: 5 requests per 30 seconds without key, 50 with key
    delay = 6 if not nvd_api_key else 0.6

    for year in years:
        print(f"\nFetching CVEs for {year}...")
        start_index = 0
        results_per_page = 2000

        while True:
            params = {
                'pubStartDate': f'{year}-01-01T00:00:00.000',
                'pubEndDate': f'{year}-12-31T23:59:59.999',
                'startIndex': start_index,
                'resultsPerPage': results_per_page
            }

            try:
                response = requests.get(base_url, params=params, headers=headers, timeout=120)
                response.raise_for_status()
                data = response.json()

                vulnerabilities = data.get('vulnerabilities', [])
                total_results = data.get('totalResults', 0)

                if not vulnerabilities:
                    break

                print(f"  Fetched {start_index + len(vulnerabilities)}/{total_results} CVEs...")

                for vuln in vulnerabilities:
                    cve = parse_cve_item_v2(vuln)
                    if cve:
                        all_cves.append(cve)
                        if is_iot_relevant(cve):
                            iot_cves.append(cve)

                start_index += results_per_page

                if start_index >= total_results:
                    break

                # Rate limiting
                time.sleep(delay)

            except requests.RequestException as e:
                print(f"  ERROR fetching CVEs: {e}")
                break

        print(f"  Found {len([c for c in all_cves if c.get('published_date', '').startswith(str(year))])} CVEs for {year}")

    # Save all CVEs
    all_path = CVE_DIR / "all_cves.json"
    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump(all_cves, f)
    print(f"\nSaved {len(all_cves)} total CVEs to {all_path}")

    # Save IoT-filtered CVEs
    iot_path = CVE_DIR / "iot_cves.json"
    with open(iot_path, 'w', encoding='utf-8') as f:
        json.dump(iot_cves, f, indent=2)
    print(f"Saved {len(iot_cves)} IoT-relevant CVEs to {iot_path}")

    # Create summary stats
    stats = create_cve_stats(iot_cves)
    stats_path = CVE_DIR / "iot_cve_stats.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"Saved CVE statistics to {stats_path}")

    return True


def parse_cve_item_v2(vuln: Dict) -> Optional[Dict]:
    """Parse a CVE item from NVD API 2.0 format."""
    try:
        cve_data = vuln.get('cve', {})
        cve_id = cve_data.get('id', '')

        # Get description (English)
        descriptions = cve_data.get('descriptions', [])
        description = ''
        for desc in descriptions:
            if desc.get('lang') == 'en':
                description = desc.get('value', '')
                break

        # Get CVSS score
        metrics = cve_data.get('metrics', {})
        cvss_score = 0.0
        severity = 'UNKNOWN'

        # Try CVSS v3.1 first, then v3.0, then v2.0
        for version in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
            if version in metrics and metrics[version]:
                cvss_data = metrics[version][0].get('cvssData', {})
                cvss_score = cvss_data.get('baseScore', 0.0)
                severity = cvss_data.get('baseSeverity', 'UNKNOWN')
                break

        # Get affected products (CPE)
        affected = []
        configurations = cve_data.get('configurations', [])
        for config in configurations:
            for node in config.get('nodes', []):
                for cpe_match in node.get('cpeMatch', []):
                    cpe = cpe_match.get('criteria', '')
                    if cpe:
                        parts = cpe.split(':')
                        if len(parts) >= 5:
                            affected.append({
                                'vendor': parts[3],
                                'product': parts[4],
                                'version': parts[5] if len(parts) > 5 else '*'
                            })

        # Check for exploits
        refs = cve_data.get('references', [])
        exploit_available = any(
            'exploit' in ref.get('url', '').lower() or
            'Exploit' in ' '.join(ref.get('tags', []))
            for ref in refs
        )

        return {
            'cve_id': cve_id,
            'description': description,
            'cvss_score': float(cvss_score),
            'severity': severity,
            'affected_products': affected,
            'exploit_available': exploit_available,
            'published_date': cve_data.get('published', ''),
            'last_modified': cve_data.get('lastModified', '')
        }

    except Exception as e:
        return None


def parse_cve_item(item: Dict) -> Optional[Dict]:
    """Parse a CVE item from NVD format."""
    try:
        cve_data = item.get('cve', {})
        cve_id = cve_data.get('CVE_data_meta', {}).get('ID', '')

        # Get description
        desc_data = cve_data.get('description', {}).get('description_data', [])
        description = desc_data[0].get('value', '') if desc_data else ''

        # Get CVSS score
        impact = item.get('impact', {})
        cvss_v3 = impact.get('baseMetricV3', {}).get('cvssV3', {})
        cvss_v2 = impact.get('baseMetricV2', {}).get('cvssV2', {})

        cvss_score = cvss_v3.get('baseScore') or cvss_v2.get('baseScore') or 0.0
        severity = cvss_v3.get('baseSeverity') or 'UNKNOWN'

        # Get affected products (CPE)
        affected = []
        configs = item.get('configurations', {}).get('nodes', [])
        for node in configs:
            for cpe_match in node.get('cpe_match', []):
                cpe = cpe_match.get('cpe23Uri', '')
                if cpe:
                    parts = cpe.split(':')
                    if len(parts) >= 5:
                        affected.append({
                            'vendor': parts[3],
                            'product': parts[4],
                            'version': parts[5] if len(parts) > 5 else '*'
                        })

        # Get references
        refs = cve_data.get('references', {}).get('reference_data', [])
        exploit_available = any(
            'exploit' in ref.get('url', '').lower() or
            'exploit' in ' '.join(ref.get('tags', [])).lower()
            for ref in refs
        )

        return {
            'cve_id': cve_id,
            'description': description,
            'cvss_score': float(cvss_score),
            'severity': severity,
            'affected_products': affected,
            'exploit_available': exploit_available,
            'published_date': item.get('publishedDate', ''),
            'last_modified': item.get('lastModifiedDate', '')
        }

    except Exception as e:
        return None


def is_iot_relevant(cve: Dict) -> bool:
    """Check if a CVE is relevant to IoT devices."""
    # Check description
    desc_lower = cve.get('description', '').lower()
    for keyword in IOT_KEYWORDS:
        if keyword in desc_lower:
            return True

    # Check affected products
    for product in cve.get('affected_products', []):
        vendor = product.get('vendor', '').lower()
        prod = product.get('product', '').lower()

        for keyword in IOT_KEYWORDS:
            if keyword in vendor or keyword in prod:
                return True

    return False


def create_cve_stats(cves: List[Dict]) -> Dict:
    """Create statistics from CVE list."""
    stats = {
        'total_cves': len(cves),
        'by_severity': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0},
        'with_exploit': 0,
        'by_vendor': {},
        'top_products': {},
        'generated_at': datetime.now().isoformat()
    }

    for cve in cves:
        # Severity
        severity = cve.get('severity', 'UNKNOWN')
        if severity in stats['by_severity']:
            stats['by_severity'][severity] += 1

        # Exploits
        if cve.get('exploit_available'):
            stats['with_exploit'] += 1

        # Vendors and products
        for product in cve.get('affected_products', []):
            vendor = product.get('vendor', 'unknown')
            prod = product.get('product', 'unknown')

            stats['by_vendor'][vendor] = stats['by_vendor'].get(vendor, 0) + 1

            key = f"{vendor}:{prod}"
            stats['top_products'][key] = stats['top_products'].get(key, 0) + 1

    # Sort and limit top products
    stats['top_products'] = dict(
        sorted(stats['top_products'].items(), key=lambda x: x[1], reverse=True)[:50]
    )
    stats['by_vendor'] = dict(
        sorted(stats['by_vendor'].items(), key=lambda x: x[1], reverse=True)[:30]
    )

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Download security databases for Eriska AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python download_databases.py --all
    python download_databases.py --cve --years 2023 2024
    python download_databases.py --oui --attack
        """
    )

    parser.add_argument('--all', action='store_true', help='Download all databases')
    parser.add_argument('--cve', action='store_true', help='Download CVE database')
    parser.add_argument('--oui', action='store_true', help='Download OUI database')
    parser.add_argument('--attack', action='store_true', help='Download MITRE ATT&CK')
    parser.add_argument('--years', nargs='+', type=int, help='CVE years to download')
    parser.add_argument('--nvd-key', type=str, help='NVD API key (optional)')

    args = parser.parse_args()

    # Default to all if nothing specified
    if not (args.all or args.cve or args.oui or args.attack):
        args.all = True

    print("="*60)
    print("ERISKA AI - DATABASE DOWNLOADER")
    print("="*60)
    print(f"Data directory: {BASE_DIR}")

    results = {}

    if args.all or args.oui:
        results['oui'] = download_oui_database()

    if args.all or args.attack:
        results['attack'] = download_attack_patterns()

    if args.all or args.cve:
        results['cve'] = download_cve_database(years=args.years, nvd_api_key=args.nvd_key)

    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    for db, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  {db.upper()}: {status}")

    print("\nData saved to:", BASE_DIR)
    print("\nNext steps:")
    print("  1. Run: python scripts/prepare_for_supabase.py")
    print("  2. Upload to Supabase vector store")


if __name__ == "__main__":
    main()
