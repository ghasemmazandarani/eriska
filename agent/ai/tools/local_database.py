"""
Local Database for IoT Security Scanner

Provides in-memory indexed access to:
- OUI (MAC vendor lookup)
- MITRE ATT&CK patterns
- CVE database (SQLite-backed for fast queries)

OUI and ATT&CK use JSON files (small, fast to load).
CVE uses SQLite database (pre-built, instant queries).
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
from datetime import datetime


class LocalDatabase:
    """Local JSON-based database for IoT security data."""

    _instance = None

    def __new__(cls):
        """Singleton pattern to avoid reloading data."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        # Data storage
        self.oui_db: Dict[str, str] = {}  # MAC prefix -> vendor
        self.attack_db: List[Dict] = []    # ATT&CK techniques
        self.attack_by_tactic: Dict[str, List[Dict]] = defaultdict(list)
        self.attack_by_platform: Dict[str, List[Dict]] = defaultdict(list)

        # CVE indexes for fast lookup
        self.cve_by_vendor: Dict[str, List[Dict]] = defaultdict(list)
        self.cve_by_id: Dict[str, Dict] = {}

        # Data paths
        self.base_dir = Path(__file__).parent.parent / "data"
        self.oui_path = self.base_dir / "oui" / "oui.json"
        self.attack_enterprise_path = self.base_dir / "attack" / "enterprise-attack_simplified.json"
        self.attack_ics_path = self.base_dir / "attack" / "ics-attack_simplified.json"
        self.cve_db_path = self.base_dir / "cve" / "cve_database.db"

        # SQLite connection (lazy loaded)
        self._cve_conn: Optional[sqlite3.Connection] = None

        self._loaded = False

    def load(self, load_cve: bool = True) -> 'LocalDatabase':
        """Load all databases into memory."""
        if self._loaded:
            return self

        print("[LocalDB] Loading databases...")

        self._load_oui()
        self._load_attack()

        cve_count = 0
        if load_cve:
            cve_count = self._connect_cve_db()

        self._loaded = True
        print(f"[LocalDB] Loaded: {len(self.oui_db)} OUI entries, "
              f"{len(self.attack_db)} ATT&CK techniques, "
              f"{cve_count} CVEs available")

        return self

    def _load_oui(self):
        """Load OUI MAC vendor database."""
        if not self.oui_path.exists():
            print(f"[LocalDB] WARNING: OUI database not found at {self.oui_path}")
            return

        with open(self.oui_path, 'r', encoding='utf-8') as f:
            self.oui_db = json.load(f)

        print(f"[LocalDB] Loaded {len(self.oui_db)} OUI entries")

    def _load_attack(self):
        """Load MITRE ATT&CK techniques."""
        for path in [self.attack_enterprise_path, self.attack_ics_path]:
            if not path.exists():
                continue

            source = 'enterprise' if 'enterprise' in path.name else 'ics'

            with open(path, 'r', encoding='utf-8') as f:
                techniques = json.load(f)

            for tech in techniques:
                tech['source'] = source
                self.attack_db.append(tech)

                # Index by tactic
                for tactic in tech.get('tactics', []):
                    self.attack_by_tactic[tactic.lower()].append(tech)

                # Index by platform
                for platform in tech.get('platforms', []):
                    self.attack_by_platform[platform.lower()].append(tech)

        print(f"[LocalDB] Loaded {len(self.attack_db)} ATT&CK techniques")

    def _connect_cve_db(self) -> int:
        """Connect to SQLite CVE database."""
        if not self.cve_db_path.exists():
            print(f"[LocalDB] WARNING: CVE database not found at {self.cve_db_path}")
            print("[LocalDB] Run 'python scripts/build_cve_database.py' to build it")
            return 0

        try:
            self._cve_conn = sqlite3.connect(str(self.cve_db_path))
            self._cve_conn.row_factory = sqlite3.Row

            # Get count
            cursor = self._cve_conn.execute("SELECT COUNT(*) FROM cves")
            count = cursor.fetchone()[0]
            print(f"[LocalDB] Connected to CVE database ({count} entries)")
            return count
        except Exception as e:
            print(f"[LocalDB] ERROR connecting to CVE database: {e}")
            return 0

    def _normalize_vendor(self, vendor: str) -> str:
        """Normalize vendor name for consistent lookup."""
        vendor = vendor.lower().strip()

        # Common normalizations
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
        }

        for pattern, normalized in normalizations.items():
            if pattern in vendor:
                return normalized

        return vendor.split()[0] if vendor else vendor  # Return first word

    # ========== PUBLIC QUERY METHODS ==========

    def lookup_vendor(self, mac_address: str) -> Optional[str]:
        """
        Look up vendor from MAC address.

        Args:
            mac_address: Full MAC or just prefix (e.g., "C4:2F:90" or "C4:2F:90:AB:12:34")

        Returns:
            Vendor name or None if not found
        """
        if not self._loaded:
            self.load()

        # Normalize MAC prefix (first 3 octets)
        mac = mac_address.upper().replace('-', ':').replace('.', ':')
        prefix = ':'.join(mac.split(':')[:3])

        return self.oui_db.get(prefix)

    def search_cve(
        self,
        vendor: str,
        product: Optional[str] = None,
        min_cvss: float = 0.0,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search CVEs by vendor and optional product using SQLite.

        Args:
            vendor: Vendor name to search for
            product: Optional product name filter
            min_cvss: Minimum CVSS score threshold
            max_results: Maximum results to return

        Returns:
            List of matching CVE dictionaries
        """
        if not self._loaded:
            self.load()

        if not self._cve_conn:
            return []

        vendor_normalized = self._normalize_vendor(vendor)

        # Build SQL query
        query = """
            SELECT DISTINCT c.cve_id, c.description, c.cvss_score, c.severity,
                   c.remediation, c.published_date,
                   ap.vendor, ap.product
            FROM cves c
            JOIN affected_products ap ON c.cve_id = ap.cve_id
            WHERE (ap.vendor_normalized LIKE ? OR ap.vendor_normalized LIKE ?)
              AND c.cvss_score >= ?
        """
        params = [f"%{vendor_normalized}%", f"{vendor_normalized}%", min_cvss]

        if product:
            query += " AND ap.product LIKE ?"
            params.append(f"%{product.lower()}%")

        query += " ORDER BY c.cvss_score DESC LIMIT ?"
        params.append(max_results)

        try:
            cursor = self._cve_conn.execute(query, params)
            rows = cursor.fetchall()

            # Convert to dict format
            results = []
            seen_ids = set()
            for row in rows:
                cve_id = row['cve_id']
                if cve_id in seen_ids:
                    continue
                seen_ids.add(cve_id)

                results.append({
                    'cve_id': cve_id,
                    'description': row['description'] or '',
                    'cvss_score': row['cvss_score'] or 0.0,
                    'severity': row['severity'] or 'UNKNOWN',
                    'remediation': row['remediation'] or '',
                    'published_date': row['published_date'] or '',
                    'affected': [{'vendor': row['vendor'], 'product': row['product']}]
                })

            return results

        except Exception as e:
            print(f"[LocalDB] CVE search error: {e}")
            return []

    def get_cve_by_id(self, cve_id: str) -> Optional[Dict]:
        """Get a specific CVE by ID using SQLite."""
        if not self._loaded:
            self.load()

        if not self._cve_conn:
            return None

        try:
            cursor = self._cve_conn.execute(
                "SELECT * FROM cves WHERE cve_id = ?",
                [cve_id.upper()]
            )
            row = cursor.fetchone()
            if not row:
                return None

            # Get affected products
            ap_cursor = self._cve_conn.execute(
                "SELECT vendor, product, version_info FROM affected_products WHERE cve_id = ?",
                [cve_id.upper()]
            )
            affected = []
            for ap_row in ap_cursor.fetchall():
                affected.append({
                    'vendor': ap_row['vendor'],
                    'product': ap_row['product'],
                    'versions': json.loads(ap_row['version_info']) if ap_row['version_info'] else []
                })

            return {
                'cve_id': row['cve_id'],
                'description': row['description'] or '',
                'cvss_score': row['cvss_score'] or 0.0,
                'severity': row['severity'] or 'UNKNOWN',
                'remediation': row['remediation'] or '',
                'published_date': row['published_date'] or '',
                'affected': affected
            }
        except Exception as e:
            print(f"[LocalDB] CVE lookup error: {e}")
            return None

    def get_attack_patterns(
        self,
        device_type: Optional[str] = None,
        tactics: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Get MITRE ATT&CK patterns filtered by criteria.

        Args:
            device_type: Device type for platform inference
            tactics: List of tactics to filter by
            platforms: List of platforms to filter by
            max_results: Maximum results to return

        Returns:
            List of matching ATT&CK technique dictionaries
        """
        if not self._loaded:
            self.load()

        results = []

        # Map device types to platforms
        device_platform_map = {
            'camera': ['linux', 'network'],
            'router': ['linux', 'network'],
            'nas': ['linux', 'windows'],
            'iot_device': ['linux', 'network'],
            'smart_device': ['linux', 'network'],
            'workstation': ['windows', 'linux', 'macos'],
        }

        # Infer platforms from device type
        if device_type and not platforms:
            platforms = device_platform_map.get(device_type.lower(), ['linux', 'network'])

        # Get techniques by platform
        if platforms:
            for platform in platforms:
                results.extend(self.attack_by_platform.get(platform.lower(), []))
        else:
            results = self.attack_db.copy()

        # Filter by tactics
        if tactics:
            tactics_lower = [t.lower() for t in tactics]
            results = [
                tech for tech in results
                if any(t in tactics_lower for t in [x.lower() for x in tech.get('tactics', [])])
            ]

        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for tech in results:
            if tech['id'] not in seen_ids:
                seen_ids.add(tech['id'])
                unique_results.append(tech)

        return unique_results[:max_results]

    def get_iot_attack_patterns(self, network_position: str = 'internal') -> List[Dict]:
        """
        Get attack patterns specifically relevant to IoT devices.

        Args:
            network_position: 'gateway', 'internal', or 'dmz'

        Returns:
            List of relevant ATT&CK techniques with IoT context
        """
        if not self._loaded:
            self.load()

        # IoT-relevant tactics by network position
        position_tactics = {
            'gateway': ['initial-access', 'command-and-control', 'lateral-movement', 'collection'],
            'internal': ['discovery', 'lateral-movement', 'collection', 'impact'],
            'dmz': ['initial-access', 'persistence', 'defense-evasion']
        }

        tactics = position_tactics.get(network_position, position_tactics['internal'])

        results = []
        for tactic in tactics:
            results.extend(self.attack_by_tactic.get(tactic, []))

        # Remove duplicates and limit
        seen_ids = set()
        unique_results = []
        for tech in results:
            if tech['id'] not in seen_ids:
                seen_ids.add(tech['id'])
                unique_results.append(tech)

        return unique_results[:15]

    def search_by_text(
        self,
        query: str,
        search_type: str = 'cve',
        max_results: int = 10
    ) -> List[Dict]:
        """
        Text search across database using SQLite FTS for CVEs.

        Args:
            query: Search text
            search_type: 'cve', 'attack', or 'all'
            max_results: Maximum results

        Returns:
            Matching entries
        """
        if not self._loaded:
            self.load()

        results = []

        # Search CVEs using FTS
        if search_type in ('cve', 'all') and self._cve_conn:
            try:
                cursor = self._cve_conn.execute("""
                    SELECT c.cve_id, c.description, c.cvss_score, c.severity,
                           c.remediation, c.published_date
                    FROM cve_fts fts
                    JOIN cves c ON fts.cve_id = c.cve_id
                    WHERE cve_fts MATCH ?
                    ORDER BY c.cvss_score DESC
                    LIMIT ?
                """, [query, max_results])

                for row in cursor.fetchall():
                    results.append({
                        'type': 'cve',
                        'cve_id': row['cve_id'],
                        'description': row['description'] or '',
                        'cvss_score': row['cvss_score'] or 0.0,
                        'severity': row['severity'] or 'UNKNOWN',
                        'remediation': row['remediation'] or '',
                        'published_date': row['published_date'] or ''
                    })
            except Exception as e:
                print(f"[LocalDB] FTS search error: {e}")

        # Search ATT&CK (in-memory)
        if search_type in ('attack', 'all'):
            query_lower = query.lower()
            query_words = query_lower.split()

            for tech in self.attack_db:
                score = 0
                text = f"{tech.get('name', '')} {tech.get('description', '')}".lower()
                for word in query_words:
                    if word in text:
                        score += 1
                if score > 0:
                    tech_copy = tech.copy()
                    tech_copy['type'] = 'attack'
                    tech_copy['_score'] = score
                    results.append(tech_copy)

            # Sort attack results by score
            results = [r for r in results if r.get('type') == 'cve'] + \
                      sorted([r for r in results if r.get('type') == 'attack'],
                             key=lambda x: x.get('_score', 0), reverse=True)

        return results[:max_results]


# Global singleton instance
_db = None

def get_database() -> LocalDatabase:
    """Get the singleton database instance."""
    global _db
    if _db is None:
        _db = LocalDatabase()
        _db.load()
    return _db
