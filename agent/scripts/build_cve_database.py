"""
Build SQLite database from CVE JSON files.

This script processes all CVE JSON files once and creates a SQLite database
for fast queries. Run this once after downloading CVE data:

    python scripts/build_cve_database.py

The resulting database (cve_database.db) will be ~50-100MB and supports
instant queries by vendor, product, CVSS score, etc.
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def create_database(db_path: Path):
    """Create SQLite database with CVE schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
        -- Main CVE table
        CREATE TABLE IF NOT EXISTS cves (
            cve_id TEXT PRIMARY KEY,
            description TEXT,
            cvss_score REAL DEFAULT 0.0,
            severity TEXT DEFAULT 'UNKNOWN',
            remediation TEXT,
            published_date TEXT,
            created_at TEXT
        );

        -- Affected products table (many-to-many relationship)
        CREATE TABLE IF NOT EXISTS affected_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cve_id TEXT NOT NULL,
            vendor TEXT,
            vendor_normalized TEXT,
            product TEXT,
            version_info TEXT,
            FOREIGN KEY (cve_id) REFERENCES cves(cve_id)
        );

        -- Indexes for fast queries
        CREATE INDEX IF NOT EXISTS idx_cves_cvss ON cves(cvss_score);
        CREATE INDEX IF NOT EXISTS idx_cves_severity ON cves(severity);
        CREATE INDEX IF NOT EXISTS idx_affected_vendor ON affected_products(vendor_normalized);
        CREATE INDEX IF NOT EXISTS idx_affected_product ON affected_products(product);
        CREATE INDEX IF NOT EXISTS idx_affected_cve ON affected_products(cve_id);

        -- Full-text search for descriptions
        CREATE VIRTUAL TABLE IF NOT EXISTS cve_fts USING fts5(
            cve_id,
            description,
            content='cves',
            content_rowid='rowid'
        );

        -- Triggers to keep FTS in sync
        CREATE TRIGGER IF NOT EXISTS cve_fts_insert AFTER INSERT ON cves BEGIN
            INSERT INTO cve_fts(rowid, cve_id, description)
            VALUES (new.rowid, new.cve_id, new.description);
        END;
    """)

    conn.commit()
    return conn


def normalize_vendor(vendor: str) -> str:
    """Normalize vendor name for consistent lookup."""
    vendor = vendor.lower().strip()

    normalizations = {
        'tp-link': 'tplink',
        'd-link': 'dlink',
        'hikvision digital technology': 'hikvision',
        'hangzhou hikvision': 'hikvision',
        'zhejiang dahua': 'dahua',
        'dahua technology': 'dahua',
        'netgear, inc.': 'netgear',
        'asus tek': 'asus',
        'asustek': 'asus',
        'cisco systems': 'cisco',
        'synology inc.': 'synology',
        'qnap systems': 'qnap',
        'western digital': 'wd',
        'pure storage': 'purestorage',
    }

    for pattern, normalized in normalizations.items():
        if pattern in vendor:
            return normalized

    # Return first word for compound names
    return vendor.split()[0] if vendor else vendor


def parse_cve_file(cve_path: Path) -> dict | None:
    """Parse a CVE.org cvelistV5 format file."""
    try:
        with open(cve_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    cve_id = data.get('cveMetadata', {}).get('cveId', '')
    if not cve_id:
        return None

    cna = data.get('containers', {}).get('cna', {})

    # Get affected products
    affected = []
    for item in cna.get('affected', []):
        vendor = item.get('vendor', '').strip()
        product = item.get('product', '').strip()
        if vendor or product:
            affected.append({
                'vendor': vendor,
                'vendor_normalized': normalize_vendor(vendor),
                'product': product,
                'versions': json.dumps(item.get('versions', []))
            })

    # Get description
    description = ''
    for desc in cna.get('descriptions', []):
        if desc.get('lang', '').startswith('en'):
            description = desc.get('value', '')
            break

    # Get CVSS score
    cvss_score = 0.0
    severity = 'UNKNOWN'
    for metric in cna.get('metrics', []):
        cvss = metric.get('cvssV3_1') or metric.get('cvssV3_0') or metric.get('cvssV2_0')
        if cvss:
            cvss_score = cvss.get('baseScore', 0.0)
            severity = cvss.get('baseSeverity', 'UNKNOWN')
            break

    # Get remediation/solutions
    remediation = ''
    for solution in cna.get('solutions', []):
        if solution.get('lang', '').startswith('en'):
            remediation = solution.get('value', '')
            break

    return {
        'cve_id': cve_id,
        'affected': affected,
        'description': description,
        'cvss_score': cvss_score,
        'severity': severity,
        'remediation': remediation,
        'published_date': data.get('cveMetadata', {}).get('datePublished', '')
    }


def build_database(cve_dir: Path, db_path: Path, min_year: int = 2018):
    """Build SQLite database from CVE JSON files."""
    print(f"Building CVE database from {cve_dir}")
    print(f"Output: {db_path}")
    print(f"Minimum year: {min_year}")
    print()

    # Remove existing database
    if db_path.exists():
        db_path.unlink()
        print(f"Removed existing database")

    conn = create_database(db_path)
    cursor = conn.cursor()

    total_files = 0
    processed = 0
    inserted = 0

    # Count total files first
    print("Counting CVE files...")
    year_dirs = [d for d in cve_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    year_dirs = [d for d in year_dirs if int(d.name) >= min_year]

    for year_dir in year_dirs:
        for id_dir in year_dir.iterdir():
            if id_dir.is_dir():
                total_files += len(list(id_dir.glob("CVE-*.json")))

    print(f"Found {total_files} CVE files to process")
    print()

    start_time = datetime.now()

    # Process files
    for year_dir in sorted(year_dirs, reverse=True):
        year = int(year_dir.name)
        year_count = 0

        for id_dir in year_dir.iterdir():
            if not id_dir.is_dir():
                continue

            for cve_file in id_dir.glob("CVE-*.json"):
                processed += 1

                if processed % 10000 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    rate = processed / elapsed if elapsed > 0 else 0
                    eta = (total_files - processed) / rate if rate > 0 else 0
                    print(f"  Progress: {processed}/{total_files} ({processed*100/total_files:.1f}%) - "
                          f"{rate:.0f} files/sec - ETA: {eta:.0f}s")

                cve_data = parse_cve_file(cve_file)
                if not cve_data:
                    continue

                # Insert CVE
                try:
                    cursor.execute("""
                        INSERT INTO cves (cve_id, description, cvss_score, severity,
                                         remediation, published_date, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cve_data['cve_id'],
                        cve_data['description'],
                        cve_data['cvss_score'],
                        cve_data['severity'],
                        cve_data['remediation'],
                        cve_data['published_date'],
                        datetime.now().isoformat()
                    ))

                    # Insert affected products
                    for affected in cve_data['affected']:
                        cursor.execute("""
                            INSERT INTO affected_products
                            (cve_id, vendor, vendor_normalized, product, version_info)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            cve_data['cve_id'],
                            affected['vendor'],
                            affected['vendor_normalized'],
                            affected['product'],
                            affected['versions']
                        ))

                    inserted += 1
                    year_count += 1

                except sqlite3.IntegrityError:
                    # Duplicate CVE ID - skip
                    pass

        print(f"Year {year}: {year_count} CVEs inserted")

        # Commit after each year
        conn.commit()

    # Final stats
    elapsed = (datetime.now() - start_time).total_seconds()
    print()
    print(f"=== Build Complete ===")
    print(f"Total processed: {processed} files")
    print(f"Total inserted: {inserted} CVEs")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Database size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Optimize database
    print("\nOptimizing database...")
    cursor.execute("VACUUM")
    cursor.execute("ANALYZE")
    conn.commit()
    conn.close()

    print(f"Final database size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
    print("\nDone! Database is ready for use.")


def main():
    # Paths
    base_dir = Path(__file__).parent.parent / "agent" / "ai" / "data"
    cve_dir = base_dir / "cve" / "cves"
    db_path = base_dir / "cve" / "cve_database.db"

    if not cve_dir.exists():
        print(f"ERROR: CVE directory not found: {cve_dir}")
        print("Run 'python scripts/download_databases.py --cve' first")
        sys.exit(1)

    # Parse command line args
    min_year = 2018
    if len(sys.argv) > 1:
        try:
            min_year = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [min_year]")
            print(f"  min_year: Minimum CVE year to include (default: 2018)")
            sys.exit(1)

    build_database(cve_dir, db_path, min_year)


if __name__ == "__main__":
    main()
