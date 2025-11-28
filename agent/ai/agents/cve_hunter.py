"""
CVE Hunter Agent

This agent searches for known vulnerabilities (CVEs) that affect the
identified devices. It correlates device fingerprints with the CVE database.
"""

import time
import json
from typing import Dict, Any, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.state import SecurityState, CVEFinding
from ai.prompts.system_prompts import CVE_HUNTER_PROMPT
from ai.tools.rag_tools import search_cve_by_device, get_remediation
from ai.api_keys import GEMINI_MODEL, get_next_key


def create_cve_hunter_agent(api_key: str, model: str = GEMINI_MODEL):
    """Create the CVE Hunter LLM agent."""
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=8192
    )
    return llm


async def cve_hunter_node(state: SecurityState) -> Dict[str, Any]:
    """
    CVE Hunter node for the LangGraph workflow.

    This node runs IN PARALLEL with AttackPathAnalyst.

    This node:
    1. For each identified device, searches for relevant CVEs
    2. Matches CVEs to device versions/firmware
    3. Prioritizes findings by severity
    4. Notes exploit availability
    """
    start_time = time.time()

    device_identifications = state.get("device_identifications", {})
    api_key = state.get("api_key")

    if not device_identifications:
        return {
            "cve_findings": {},
            "current_phase": "no_identifications",
            "timing": {"cve_hunter": 0}
        }

    print(f"\n[CVE_HUNTER] Searching CVEs for {len(device_identifications)} devices...")

    cve_findings: Dict[str, List[CVEFinding]] = {}
    all_cve_ids = []

    for ip, identification in device_identifications.items():
        vendor = identification.get("vendor", "Unknown")
        device_type = identification.get("device_type", "unknown")
        model = identification.get("model")
        firmware = identification.get("firmware")

        if vendor == "Unknown":
            print(f"[CVE_HUNTER] Skipping {ip} - vendor unknown")
            continue

        print(f"[CVE_HUNTER] Searching CVEs for {ip}: {vendor} {device_type}")

        # Search CVE database
        cve_result_str = search_cve_by_device.invoke({
            "vendor": vendor,
            "product": model,
            "firmware_version": firmware,
            "min_cvss": 0.0  # Get all CVEs, we'll filter later
        })

        try:
            cve_result = json.loads(cve_result_str)

            if cve_result.get("success") and cve_result.get("cves"):
                device_cves = []

                for cve_data in cve_result["cves"]:
                    cve_id = cve_data.get("cve_id", "")
                    cvss = cve_data.get("cvss_score", 0.0)

                    # Determine severity
                    severity = "LOW"
                    if cvss >= 9.0:
                        severity = "CRITICAL"
                    elif cvss >= 7.0:
                        severity = "HIGH"
                    elif cvss >= 4.0:
                        severity = "MEDIUM"

                    # Build finding
                    finding = CVEFinding(
                        cve_id=cve_id,
                        description=cve_data.get("description", ""),
                        cvss_score=cvss,
                        severity=severity,
                        affected_versions=cve_data.get("affected_versions"),
                        exploit_available=cve_data.get("exploit_available", False),
                        confidence=0.7 if model else 0.5,  # Higher if we know the model
                        evidence=[f"Vendor match: {vendor}", f"Device type: {device_type}"]
                    )

                    device_cves.append(finding)
                    all_cve_ids.append(cve_id)

                    # Print findings
                    exploit_tag = "[EXPLOIT]" if finding["exploit_available"] else ""
                    print(f"[CVE_HUNTER] Found: {cve_id} ({severity} {cvss}) {exploit_tag}")

                # Sort by CVSS score
                device_cves.sort(key=lambda x: x.get("cvss_score", 0), reverse=True)
                cve_findings[ip] = device_cves

            else:
                print(f"[CVE_HUNTER] No CVEs found for {vendor}")

        except json.JSONDecodeError:
            print(f"[CVE_HUNTER] Failed to parse CVE results for {ip}")
        except Exception as e:
            print(f"[CVE_HUNTER] Error searching CVEs for {ip}: {e}")

    # Generate analysis using LLM
    if api_key and cve_findings:
        try:
            llm = create_cve_hunter_agent(api_key)

            # Build CVE summary for LLM
            critical_cves = []
            high_cves = []

            for ip, findings in cve_findings.items():
                for f in findings:
                    cve_info = {
                        "device_ip": ip,
                        "cve_id": f.get("cve_id"),
                        "cvss": f.get("cvss_score"),
                        "description": f.get("description", "")[:200],
                        "exploit_available": f.get("exploit_available", False)
                    }
                    if f.get("severity") == "CRITICAL":
                        critical_cves.append(cve_info)
                    elif f.get("severity") == "HIGH":
                        high_cves.append(cve_info)

            analysis_prompt = f"""Analyze these CVE findings:

CRITICAL CVEs ({len(critical_cves)}):
{json.dumps(critical_cves, indent=2) if critical_cves else "None"}

HIGH CVEs ({len(high_cves)}):
{json.dumps(high_cves[:5], indent=2) if high_cves else "None"}

Total unique CVEs found: {len(set(all_cve_ids))}
Devices affected: {len(cve_findings)}

Provide:
1. Summary of most critical vulnerabilities (2-3 sentences)
2. Which devices are most at risk
3. Priority order for remediation
"""

            response = llm.invoke([
                SystemMessage(content=CVE_HUNTER_PROMPT),
                HumanMessage(content=analysis_prompt)
            ])
            print(f"\n[CVE_HUNTER] Analysis:\n{response.content}")

        except Exception as e:
            print(f"[CVE_HUNTER] Could not generate analysis: {e}")

    elapsed = time.time() - start_time

    # Summary stats
    total_cves = sum(len(findings) for findings in cve_findings.values())
    critical_count = sum(
        1 for findings in cve_findings.values()
        for f in findings if f.get("severity") == "CRITICAL"
    )

    print(f"\n[CVE_HUNTER] Complete: {total_cves} CVEs found ({critical_count} CRITICAL)")

    return {
        "cve_findings": cve_findings,
        "timing": {"cve_hunter": elapsed}
    }


def cve_hunter_node_sync(state: SecurityState) -> Dict[str, Any]:
    """Synchronous version of cve_hunter_node."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(cve_hunter_node(state))
    finally:
        loop.close()
