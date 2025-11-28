"""
Prepare Downloaded Data for Supabase Upload

This script:
1. Loads the downloaded CVE and device data
2. Generates embeddings using OpenAI text-embedding-3-large
3. Formats data for Supabase pgvector upload
4. Optionally uploads directly to Supabase

Usage:
    python prepare_for_supabase.py --generate-embeddings
    python prepare_for_supabase.py --upload
    python prepare_for_supabase.py --generate-embeddings --upload
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / "test.env")
except ImportError:
    pass

# Data directories
BASE_DIR = Path(__file__).parent.parent / "agent" / "ai" / "data"
CVE_DIR = BASE_DIR / "cve"
OUI_DIR = BASE_DIR / "oui"
ATTACK_DIR = BASE_DIR / "attack"
OUTPUT_DIR = BASE_DIR / "supabase_ready"


def get_openai_client():
    """Get OpenAI client for embeddings."""
    try:
        from openai import OpenAI
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        return OpenAI(api_key=api_key)
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")


def get_supabase_client():
    """Get Supabase client."""
    try:
        from supabase import create_client
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_ANON_KEY')
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return create_client(url, key)
    except ImportError:
        raise ImportError("supabase package not installed. Run: pip install supabase")


def generate_embedding(client, text: str, model: str = "text-embedding-3-large") -> List[float]:
    """Generate embedding for text using OpenAI."""
    # Truncate if too long (max ~8000 tokens)
    if len(text) > 30000:
        text = text[:30000]

    response = client.embeddings.create(
        model=model,
        input=text,
        dimensions=3072  # text-embedding-3-large supports custom dimensions
    )
    return response.data[0].embedding


def prepare_cve_documents(limit: int = None) -> List[Dict]:
    """Prepare CVE documents for embedding."""
    print("\nPreparing CVE documents...")

    iot_cve_path = CVE_DIR / "iot_cves.json"
    if not iot_cve_path.exists():
        print(f"  ERROR: {iot_cve_path} not found. Run download_databases.py first.")
        return []

    with open(iot_cve_path, 'r', encoding='utf-8') as f:
        cves = json.load(f)

    if limit:
        cves = cves[:limit]

    documents = []
    for cve in cves:
        # Create searchable text
        affected = ", ".join([
            f"{p['vendor']} {p['product']}"
            for p in cve.get('affected_products', [])[:5]
        ])

        text = f"""CVE ID: {cve['cve_id']}
Severity: {cve['severity']} (CVSS: {cve['cvss_score']})
Affected: {affected}
Exploit Available: {'Yes' if cve.get('exploit_available') else 'No'}
Description: {cve['description']}"""

        doc = {
            'id': cve['cve_id'],
            'type': 'cve',
            'content': text,
            'metadata': {
                'cve_id': cve['cve_id'],
                'cvss_score': cve['cvss_score'],
                'severity': cve['severity'],
                'exploit_available': cve.get('exploit_available', False),
                'affected_products': cve.get('affected_products', [])[:10],
                'published_date': cve.get('published_date', '')
            }
        }
        documents.append(doc)

    print(f"  Prepared {len(documents)} CVE documents")
    return documents


def prepare_attack_documents() -> List[Dict]:
    """Prepare MITRE ATT&CK documents for embedding."""
    print("\nPreparing ATT&CK documents...")

    documents = []

    for filename in ['enterprise-attack_simplified.json', 'ics-attack_simplified.json']:
        path = ATTACK_DIR / filename
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            techniques = json.load(f)

        source = 'enterprise' if 'enterprise' in filename else 'ics'

        for tech in techniques:
            text = f"""MITRE ATT&CK Technique: {tech['id']} - {tech['name']}
Source: {source.upper()}
Tactics: {', '.join(tech.get('tactics', []))}
Platforms: {', '.join(tech.get('platforms', []))}
Description: {tech['description']}"""

            doc = {
                'id': f"attack_{tech['id']}",
                'type': 'attack_pattern',
                'content': text,
                'metadata': {
                    'technique_id': tech['id'],
                    'name': tech['name'],
                    'tactics': tech.get('tactics', []),
                    'platforms': tech.get('platforms', []),
                    'source': source
                }
            }
            documents.append(doc)

    print(f"  Prepared {len(documents)} ATT&CK documents")
    return documents


def prepare_device_documents() -> List[Dict]:
    """Prepare device fingerprint documents for embedding."""
    print("\nPreparing device fingerprint documents...")

    # These are common IoT device patterns for identification
    device_patterns = [
        # Cameras
        {
            'vendor': 'Hikvision',
            'type': 'camera',
            'indicators': ['Hikvision-Webs', 'DNVRS-Webs', 'App-webs', 'ISAPI'],
            'default_ports': [80, 443, 554, 8000],
            'protocols': ['ONVIF', 'RTSP', 'ISAPI'],
            'common_vulns': ['CVE-2021-36260', 'CVE-2017-7921', 'CVE-2014-4878']
        },
        {
            'vendor': 'Dahua',
            'type': 'camera',
            'indicators': ['Dahua', 'DH-', 'XVR', 'IPC-'],
            'default_ports': [80, 443, 554, 37777],
            'protocols': ['ONVIF', 'RTSP', 'Dahua Protocol'],
            'common_vulns': ['CVE-2021-33044', 'CVE-2020-25078', 'CVE-2017-13776']
        },
        {
            'vendor': 'Axis',
            'type': 'camera',
            'indicators': ['AXIS', 'Axis Communications'],
            'default_ports': [80, 443, 554],
            'protocols': ['ONVIF', 'RTSP', 'VAPIX'],
            'common_vulns': ['CVE-2018-10660', 'CVE-2018-10661', 'CVE-2018-10662']
        },

        # Routers
        {
            'vendor': 'TP-Link',
            'type': 'router',
            'indicators': ['TP-LINK', 'tplinkwifi', 'TL-', 'Archer'],
            'default_ports': [80, 443, 22],
            'protocols': ['HTTP', 'UPnP'],
            'common_vulns': ['CVE-2022-30075', 'CVE-2020-35575', 'CVE-2019-7405']
        },
        {
            'vendor': 'Netgear',
            'type': 'router',
            'indicators': ['NETGEAR', 'Nighthawk', 'Orbi'],
            'default_ports': [80, 443],
            'protocols': ['HTTP', 'UPnP', 'SOAP'],
            'common_vulns': ['CVE-2021-45388', 'CVE-2020-26919', 'CVE-2017-6077']
        },
        {
            'vendor': 'D-Link',
            'type': 'router',
            'indicators': ['D-Link', 'DIR-', 'DSL-'],
            'default_ports': [80, 443, 8080],
            'protocols': ['HTTP', 'UPnP', 'HNAP'],
            'common_vulns': ['CVE-2020-25078', 'CVE-2019-17621', 'CVE-2018-10822']
        },
        {
            'vendor': 'ASUS',
            'type': 'router',
            'indicators': ['ASUS', 'RT-', 'ROG'],
            'default_ports': [80, 443, 8443],
            'protocols': ['HTTP', 'AiCloud'],
            'common_vulns': ['CVE-2023-39238', 'CVE-2022-26376', 'CVE-2018-14712']
        },

        # Smart Home
        {
            'vendor': 'Tuya',
            'type': 'smart_device',
            'indicators': ['Tuya', 'Smart Life', 'tuya_uuid'],
            'default_ports': [6668, 80],
            'protocols': ['Tuya Protocol', 'MQTT'],
            'common_vulns': ['CVE-2019-12580']
        },
        {
            'vendor': 'Shelly',
            'type': 'smart_switch',
            'indicators': ['Shelly', 'shelly'],
            'default_ports': [80, 5683],
            'protocols': ['HTTP', 'CoAP', 'MQTT'],
            'common_vulns': []
        },

        # NAS
        {
            'vendor': 'Synology',
            'type': 'nas',
            'indicators': ['Synology', 'DiskStation', 'DSM'],
            'default_ports': [5000, 5001, 80, 443],
            'protocols': ['HTTP', 'WebDAV', 'SMB'],
            'common_vulns': ['CVE-2022-27624', 'CVE-2021-26560', 'CVE-2019-3870']
        },
        {
            'vendor': 'QNAP',
            'type': 'nas',
            'indicators': ['QNAP', 'QTS', 'NAS'],
            'default_ports': [8080, 443, 80],
            'protocols': ['HTTP', 'SMB', 'AFP'],
            'common_vulns': ['CVE-2022-27596', 'CVE-2021-28816', 'CVE-2020-2509']
        }
    ]

    documents = []
    for pattern in device_patterns:
        text = f"""Device: {pattern['vendor']} {pattern['type']}
Vendor: {pattern['vendor']}
Type: {pattern['type']}
Identification Indicators: {', '.join(pattern['indicators'])}
Default Ports: {', '.join(map(str, pattern['default_ports']))}
Protocols: {', '.join(pattern['protocols'])}
Known Vulnerabilities: {', '.join(pattern['common_vulns']) if pattern['common_vulns'] else 'Check CVE database'}"""

        doc = {
            'id': f"device_{pattern['vendor'].lower().replace(' ', '_')}_{pattern['type']}",
            'type': 'device_fingerprint',
            'content': text,
            'metadata': pattern
        }
        documents.append(doc)

    print(f"  Prepared {len(documents)} device fingerprint documents")
    return documents


def generate_embeddings_batch(client, documents: List[Dict], batch_size: int = 100) -> List[Dict]:
    """Generate embeddings for documents in batches."""
    print(f"\nGenerating embeddings for {len(documents)} documents...")

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}...")

        for doc in batch:
            try:
                embedding = generate_embedding(client, doc['content'])
                doc['embedding'] = embedding
            except Exception as e:
                print(f"    ERROR generating embedding for {doc['id']}: {e}")
                doc['embedding'] = None

    # Filter out failed embeddings
    documents = [d for d in documents if d.get('embedding') is not None]
    print(f"  Successfully generated {len(documents)} embeddings")
    return documents


def save_for_supabase(documents: List[Dict], filename: str):
    """Save documents in Supabase-ready format."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f)

    print(f"  Saved to: {output_path}")

    # Also save without embeddings for inspection
    docs_no_embed = [{k: v for k, v in d.items() if k != 'embedding'} for d in documents]
    inspect_path = OUTPUT_DIR / filename.replace('.json', '_inspect.json')
    with open(inspect_path, 'w', encoding='utf-8') as f:
        json.dump(docs_no_embed, f, indent=2)


def upload_to_supabase(documents: List[Dict], table_name: str = "documents"):
    """Upload documents to Supabase."""
    print(f"\nUploading {len(documents)} documents to Supabase table '{table_name}'...")

    client = get_supabase_client()

    # Upload in batches
    batch_size = 50
    uploaded = 0

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]

        # Format for Supabase
        records = []
        for doc in batch:
            record = {
                'content': doc['content'],
                'metadata': doc['metadata'],
                'embedding': doc['embedding']
            }
            records.append(record)

        try:
            result = client.table(table_name).insert(records).execute()
            uploaded += len(batch)
            print(f"  Uploaded {uploaded}/{len(documents)}")
        except Exception as e:
            print(f"  ERROR uploading batch: {e}")

    print(f"  Upload complete: {uploaded} documents")


def main():
    parser = argparse.ArgumentParser(description="Prepare data for Supabase upload")
    parser.add_argument('--generate-embeddings', action='store_true', help='Generate OpenAI embeddings')
    parser.add_argument('--upload', action='store_true', help='Upload to Supabase')
    parser.add_argument('--cve-limit', type=int, default=1000, help='Max CVEs to process (default: 1000)')
    parser.add_argument('--table', type=str, default='documents', help='Supabase table name')

    args = parser.parse_args()

    print("="*60)
    print("ERISKA AI - PREPARE DATA FOR SUPABASE")
    print("="*60)

    # Prepare all documents
    all_documents = []

    cve_docs = prepare_cve_documents(limit=args.cve_limit)
    all_documents.extend(cve_docs)

    attack_docs = prepare_attack_documents()
    all_documents.extend(attack_docs)

    device_docs = prepare_device_documents()
    all_documents.extend(device_docs)

    print(f"\nTotal documents: {len(all_documents)}")

    if args.generate_embeddings:
        print("\n" + "="*60)
        print("GENERATING EMBEDDINGS")
        print("="*60)

        client = get_openai_client()
        all_documents = generate_embeddings_batch(client, all_documents)

        # Save
        save_for_supabase(all_documents, "all_documents.json")
        save_for_supabase([d for d in all_documents if d['type'] == 'cve'], "cve_documents.json")
        save_for_supabase([d for d in all_documents if d['type'] == 'attack_pattern'], "attack_documents.json")
        save_for_supabase([d for d in all_documents if d['type'] == 'device_fingerprint'], "device_documents.json")

    if args.upload:
        print("\n" + "="*60)
        print("UPLOADING TO SUPABASE")
        print("="*60)

        if not all_documents[0].get('embedding'):
            # Load from saved files
            all_path = OUTPUT_DIR / "all_documents.json"
            if all_path.exists():
                with open(all_path, 'r') as f:
                    all_documents = json.load(f)
            else:
                print("ERROR: No embeddings found. Run with --generate-embeddings first.")
                return

        upload_to_supabase(all_documents, args.table)

    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
