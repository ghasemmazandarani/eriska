"""
Debate Synthesis Agent

This agent implements a multi-agent debate pattern to verify findings
and generate the final security report with confidence scores.
"""

import time
import json
from typing import Dict, Any, List
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.state import SecurityState, RemediationStep
from ai.prompts.system_prompts import DEBATE_SYNTHESIS_PROMPT
from ai.tools.rag_tools import get_remediation
from ai.api_keys import GEMINI_MODEL


def create_debate_agent(api_key: str, model: str = GEMINI_MODEL, role: str = "analyst"):
    """Create a debate participant LLM agent with specific role."""
    # Adjust temperature based on role
    temp = 0.3 if role == "critic" else 0.5

    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temp,
        max_output_tokens=8192
    )
    return llm


def calculate_risk_score(cve_findings: Dict, attack_paths: List) -> int:
    """Calculate overall network risk score (0-100)."""
    score = 0

    # CVE-based scoring
    for ip, findings in cve_findings.items():
        for finding in findings:
            cvss = finding.get("cvss_score", 0)
            if cvss >= 9.0:
                score += 25  # Critical
            elif cvss >= 7.0:
                score += 15  # High
            elif cvss >= 4.0:
                score += 8   # Medium
            else:
                score += 3   # Low

            # Bonus for exploits available
            if finding.get("exploit_available"):
                score += 10

    # Attack path scoring
    for path in attack_paths:
        likelihood = path.get("likelihood", 0.5)
        complexity = path.get("total_complexity", "MEDIUM")

        if complexity == "LOW":
            score += int(20 * likelihood)
        elif complexity == "MEDIUM":
            score += int(15 * likelihood)
        else:
            score += int(10 * likelihood)

    # Cap at 100
    return min(score, 100)


def generate_remediation_priority(cve_findings: Dict, attack_paths: List) -> List[RemediationStep]:
    """Generate prioritized remediation steps."""
    remediation_steps = []
    priority = 1

    # Collect all critical and high severity CVEs
    critical_findings = []
    high_findings = []

    for ip, findings in cve_findings.items():
        for finding in findings:
            finding_with_ip = {**finding, "device_ip": ip}
            if finding.get("severity") == "CRITICAL":
                critical_findings.append(finding_with_ip)
            elif finding.get("severity") == "HIGH":
                high_findings.append(finding_with_ip)

    # Sort by CVSS score and exploit availability
    critical_findings.sort(
        key=lambda x: (x.get("exploit_available", False), x.get("cvss_score", 0)),
        reverse=True
    )
    high_findings.sort(
        key=lambda x: (x.get("exploit_available", False), x.get("cvss_score", 0)),
        reverse=True
    )

    # Generate remediation for critical findings
    for finding in critical_findings[:5]:  # Top 5 critical
        cve_id = finding.get("cve_id", "Unknown")
        device_ip = finding.get("device_ip")

        # Try to get remediation from RAG
        try:
            remediation_str = get_remediation.invoke({
                "cve_id": cve_id,
                "device_type": "unknown",
                "vendor": "unknown"
            })
            remediation_data = json.loads(remediation_str)
            steps = remediation_data.get("remediation", {}).get("steps", [])
            action = steps[0] if steps else f"Patch {cve_id} immediately"
        except:
            action = f"Patch {cve_id} immediately - check vendor security advisories"

        step = RemediationStep(
            priority=priority,
            action=action,
            target_device=device_ip,
            cve_addressed=cve_id,
            difficulty="HIGH" if finding.get("exploit_available") else "MEDIUM",
            estimated_impact=f"Eliminates CRITICAL vulnerability (CVSS {finding.get('cvss_score', 'N/A')})"
        )
        remediation_steps.append(step)
        priority += 1

    # Generate remediation for high findings
    for finding in high_findings[:3]:  # Top 3 high
        cve_id = finding.get("cve_id", "Unknown")
        device_ip = finding.get("device_ip")

        step = RemediationStep(
            priority=priority,
            action=f"Update firmware to patch {cve_id}",
            target_device=device_ip,
            cve_addressed=cve_id,
            difficulty="MEDIUM",
            estimated_impact=f"Eliminates HIGH vulnerability (CVSS {finding.get('cvss_score', 'N/A')})"
        )
        remediation_steps.append(step)
        priority += 1

    # Add general network hardening if attack paths were found
    if attack_paths:
        step = RemediationStep(
            priority=priority,
            action="Implement network segmentation to isolate IoT devices",
            target_device="network",
            difficulty="MEDIUM",
            estimated_impact="Reduces lateral movement risk across all attack paths"
        )
        remediation_steps.append(step)
        priority += 1

        step = RemediationStep(
            priority=priority,
            action="Change default credentials on all network devices",
            target_device="all",
            difficulty="LOW",
            estimated_impact="Eliminates credential-based attack vectors"
        )
        remediation_steps.append(step)

    return remediation_steps


async def debate_synthesis_node(state: SecurityState) -> Dict[str, Any]:
    """
    Debate Synthesis node for the LangGraph workflow.

    This is the FINAL node that:
    1. Reviews all findings from CVE Hunter and Attack Path Analyst
    2. Runs a multi-agent debate to verify critical findings
    3. Calculates confidence scores
    4. Generates the final security report
    """
    start_time = time.time()

    cve_findings = state.get("cve_findings", {})
    attack_paths = state.get("attack_paths", [])
    device_identifications = state.get("device_identifications", {})
    devices = state.get("devices", {})
    api_key = state.get("api_key")

    print(f"\n[DEBATE] Starting synthesis and verification...")
    print(f"[DEBATE] Inputs: {len(cve_findings)} devices with CVEs, {len(attack_paths)} attack paths")

    # Calculate overall risk score
    overall_risk = calculate_risk_score(cve_findings, attack_paths)
    print(f"[DEBATE] Calculated risk score: {overall_risk}/100")

    # Generate prioritized remediation
    remediation_steps = generate_remediation_priority(cve_findings, attack_paths)
    print(f"[DEBATE] Generated {len(remediation_steps)} remediation steps")

    # Count findings by severity
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for ip, findings in cve_findings.items():
        for finding in findings:
            severity = finding.get("severity", "LOW")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

    # Run multi-agent debate for critical findings verification
    debate_verified = []
    confidence_adjustments = {}

    if api_key and severity_counts["CRITICAL"] > 0:
        print(f"\n[DEBATE] Running verification debate for {severity_counts['CRITICAL']} critical findings...")

        try:
            # Create debate participants
            analyst = create_debate_agent(api_key, role="analyst")
            critic = create_debate_agent(api_key, role="critic")

            # Collect critical findings for debate
            critical_for_debate = []
            for ip, findings in cve_findings.items():
                for finding in findings:
                    if finding.get("severity") == "CRITICAL":
                        critical_for_debate.append({
                            "device_ip": ip,
                            "cve_id": finding.get("cve_id"),
                            "cvss": finding.get("cvss_score"),
                            "description": finding.get("description", "")[:300],
                            "evidence": finding.get("evidence", []),
                            "confidence": finding.get("confidence", 0.5)
                        })

            # Analyst presents findings
            analyst_prompt = f"""Review these CRITICAL CVE findings and explain why each is a valid security concern:

{json.dumps(critical_for_debate[:3], indent=2)}

For each finding, explain:
1. Why this CVE applies to this device
2. What evidence supports this conclusion
3. What the real-world impact would be
"""

            analyst_response = analyst.invoke([
                SystemMessage(content="You are a security analyst. Defend CVE findings with technical evidence."),
                HumanMessage(content=analyst_prompt)
            ])

            # Critic challenges findings
            critic_prompt = f"""A security analyst has identified these critical vulnerabilities:

{analyst_response.content}

As a critical reviewer, challenge these findings:
1. Are there any false positives possible?
2. Is the evidence sufficient?
3. Could the CVE not apply due to version differences or configuration?
4. What additional verification would you recommend?

Be rigorous but fair.
"""

            critic_response = critic.invoke([
                SystemMessage(content="You are a security critic. Challenge findings to ensure accuracy. Be skeptical but not dismissive."),
                HumanMessage(content=critic_prompt)
            ])

            # Final synthesis
            synthesis_prompt = f"""Based on the analyst's findings and critic's review:

ANALYST: {analyst_response.content[:1500]}

CRITIC: {critic_response.content[:1500]}

Provide a final verdict:
1. Which findings are CONFIRMED (high confidence)?
2. Which need FURTHER VERIFICATION?
3. Which might be FALSE POSITIVES?

Output as JSON with structure: {{"confirmed": [...], "needs_verification": [...], "possible_false_positives": [...]}}
"""

            final_response = analyst.invoke([
                SystemMessage(content=DEBATE_SYNTHESIS_PROMPT),
                HumanMessage(content=synthesis_prompt)
            ])

            print(f"[DEBATE] Verification complete")
            print(f"[DEBATE] Result:\n{final_response.content[:500]}...")

            # Try to parse the result
            try:
                # Extract JSON from response
                response_text = final_response.content
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]
                else:
                    json_str = response_text

                verdict = json.loads(json_str)
                debate_verified = verdict.get("confirmed", [])

                # Adjust confidence based on debate
                for cve in verdict.get("confirmed", []):
                    confidence_adjustments[cve] = 0.2  # Boost confidence
                for cve in verdict.get("needs_verification", []):
                    confidence_adjustments[cve] = 0.0  # Keep same
                for cve in verdict.get("possible_false_positives", []):
                    confidence_adjustments[cve] = -0.2  # Reduce confidence

            except json.JSONDecodeError:
                print("[DEBATE] Could not parse debate verdict as JSON")

        except Exception as e:
            print(f"[DEBATE] Debate error: {e}")

    # Build final report
    final_report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_devices": len(devices),
            "devices_identified": len(device_identifications),
            "total_cves": sum(len(f) for f in cve_findings.values()),
            "critical_cves": severity_counts["CRITICAL"],
            "high_cves": severity_counts["HIGH"],
            "attack_paths": len(attack_paths),
            "overall_risk_score": overall_risk,
            "risk_level": "CRITICAL" if overall_risk >= 80 else "HIGH" if overall_risk >= 60 else "MEDIUM" if overall_risk >= 40 else "LOW"
        },
        "top_risks": [],
        "verified_findings": debate_verified,
        "remediation_priority": [
            {
                "priority": step["priority"],
                "action": step["action"],
                "target": step.get("target_device"),
                "impact": step.get("estimated_impact")
            }
            for step in remediation_steps[:5]
        ]
    }

    # Add top risks
    for ip, findings in cve_findings.items():
        for finding in findings[:1]:  # Top finding per device
            if finding.get("severity") in ["CRITICAL", "HIGH"]:
                device_info = device_identifications.get(ip, {})
                final_report["top_risks"].append({
                    "device": f"{device_info.get('vendor', 'Unknown')} at {ip}",
                    "cve": finding.get("cve_id"),
                    "severity": finding.get("severity"),
                    "cvss": finding.get("cvss_score")
                })

    # Sort top risks by CVSS
    final_report["top_risks"].sort(key=lambda x: x.get("cvss", 0), reverse=True)
    final_report["top_risks"] = final_report["top_risks"][:5]  # Top 5

    elapsed = time.time() - start_time

    # Print summary
    print(f"\n{'='*60}")
    print(f"[DEBATE] FINAL SECURITY REPORT")
    print(f"{'='*60}")
    print(f"Risk Score: {overall_risk}/100 ({final_report['summary']['risk_level']})")
    print(f"Devices Scanned: {final_report['summary']['total_devices']}")
    print(f"CVEs Found: {final_report['summary']['total_cves']} ({severity_counts['CRITICAL']} Critical, {severity_counts['HIGH']} High)")
    print(f"Attack Paths: {final_report['summary']['attack_paths']}")
    print(f"\nTop Risks:")
    for risk in final_report["top_risks"][:3]:
        print(f"  - {risk['device']}: {risk['cve']} ({risk['severity']})")
    print(f"\nPriority Remediation:")
    for step in final_report["remediation_priority"][:3]:
        print(f"  {step['priority']}. {step['action']}")
    print(f"{'='*60}")

    return {
        "remediation_steps": remediation_steps,
        "final_report": final_report,
        "current_phase": "complete",
        "timing": {"debate_synthesis": elapsed}
    }


def debate_synthesis_node_sync(state: SecurityState) -> Dict[str, Any]:
    """Synchronous version of debate_synthesis_node."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(debate_synthesis_node(state))
    finally:
        loop.close()
