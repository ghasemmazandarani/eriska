"""
Security State Schema for Eriska AI Agent System

This module defines the state that flows through the LangGraph workflow.
All agents read from and write to this shared state.
"""

from typing import TypedDict, List, Dict, Optional, Any
from datetime import datetime


def merge_dicts(left: dict, right: dict) -> dict:
    """Custom reducer for merging dictionaries in parallel execution."""
    if left is None:
        return right or {}
    if right is None:
        return left
    result = left.copy()
    result.update(right)
    return result


def merge_lists(left: list, right: list) -> list:
    """Custom reducer for merging lists in parallel execution."""
    if left is None:
        return right or []
    if right is None:
        return left
    return left + right


class DeviceInfo(TypedDict, total=False):
    """Information about a discovered device."""
    ip: str
    mac: str
    vendor: str
    device_type: str  # camera, router, iot_sensor, computer, etc.
    model: Optional[str]
    firmware: Optional[str]
    ports: List[int]
    fingerprints: Dict[str, Any]
    first_seen: float
    last_seen: float


class CVEFinding(TypedDict, total=False):
    """A CVE vulnerability finding."""
    cve_id: str
    description: str
    cvss_score: float
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    affected_versions: Optional[str]
    exploit_available: bool
    confidence: float  # 0.0 to 1.0 - how confident we are this applies
    evidence: List[str]  # Evidence supporting this finding


class AttackStep(TypedDict, total=False):
    """A single step in an attack path."""
    step_number: int
    action: str
    target_device: str
    vulnerability_used: Optional[str]
    access_gained: str
    prerequisites: List[str]


class AttackPath(TypedDict, total=False):
    """A complete attack path scenario."""
    path_id: str
    name: str
    description: str
    entry_point: str
    target: str
    steps: List[AttackStep]
    total_complexity: str  # LOW, MEDIUM, HIGH
    impact: str  # Description of impact
    likelihood: float  # 0.0 to 1.0


class DebateRound(TypedDict, total=False):
    """A single round of multi-agent debate."""
    finding_id: str
    claim: str
    challenge: str
    response: str
    verdict: str  # CONFIRMED, LIKELY, UNCERTAIN, REFUTED
    confidence_delta: float
    evidence_cited: List[str]


class RemediationStep(TypedDict, total=False):
    """A single remediation recommendation."""
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    affected_device: str
    related_cves: List[str]
    effort: str  # Minimal, Moderate, Significant
    steps: List[str]


class SecurityState(TypedDict, total=False):
    """
    Main state schema for the security assessment workflow.

    This state flows through all agents:
    ScanMonitor -> DeviceIdentifier -> [CVEHunter || AttackPath] -> DebateSynthesis
    """

    # === Configuration ===
    network_range: str  # e.g., "192.168.1.0/24"
    scan_interval: int  # seconds between scans
    continuous_mode: bool  # whether to loop continuously
    api_key: str  # Gemini API key

    # === Scan Results ===
    # Populated by ScanMonitor
    devices: Dict[str, Any]  # IP -> DeviceInfo dict
    new_devices: List[str]  # IPs of devices detected in this scan cycle
    changed_devices: List[str]  # IPs of devices with changes
    scan_timestamp: str

    # === Device Identification ===
    # Populated by DeviceIdentifier
    device_identifications: Dict[str, Any]  # IP -> identification results

    # === Vulnerability Analysis ===
    # Populated by CVEHunter (runs in parallel with AttackPath)
    cve_findings: Dict[str, Any]  # IP -> list of CVE findings

    # === Attack Path Analysis ===
    # Populated by AttackPathAnalyst (runs in parallel with CVEHunter)
    attack_paths: List[Any]

    # === Debate & Verification ===
    # Populated by DebateSynthesis
    debate_rounds: List[Any]
    verified_findings: List[Any]  # Findings that passed verification
    confidence_scores: Dict[str, float]  # finding_id -> confidence score

    # === Final Output ===
    risk_scores: Dict[str, int]  # IP -> risk score (0-100)
    overall_risk_score: int  # Network-wide risk score
    remediation_steps: List[Any]  # Renamed from remediation_plan
    final_report: Any  # Generated report (dict or text)

    # === Execution Metadata ===
    current_phase: str  # scan, identify, analyze, debate, complete
    errors: List[str]
    timing: Dict[str, float]  # phase -> seconds


def create_initial_state(
    network_range: str,
    api_key: str,
    continuous_mode: bool = False,
    scan_interval: int = 60
) -> SecurityState:
    """Create an initial state for a new security scan."""
    return SecurityState(
        # Configuration
        network_range=network_range,
        scan_interval=scan_interval,
        continuous_mode=continuous_mode,
        api_key=api_key,

        # Scan Results
        devices={},
        new_devices=[],
        changed_devices=[],
        scan_timestamp=datetime.now().isoformat(),

        # Device Identification
        device_identifications={},

        # Vulnerability Analysis
        cve_findings={},

        # Attack Path Analysis
        attack_paths=[],

        # Debate & Verification
        debate_rounds=[],
        verified_findings=[],
        confidence_scores={},

        # Final Output
        risk_scores={},
        overall_risk_score=0,
        remediation_plan=[],
        final_report="",

        # Execution Metadata
        current_phase="initialized",
        errors=[],
        timing={}
    )
