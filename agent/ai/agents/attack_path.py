"""
Attack Path Analyst Agent

This agent constructs realistic attack scenarios showing how an adversary
could compromise the network using the discovered vulnerabilities.
"""

import time
import json
from typing import Dict, Any, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.state import SecurityState, AttackPath, AttackStep
from ai.prompts.system_prompts import ATTACK_PATH_ANALYST_PROMPT
from ai.tools.rag_tools import get_attack_patterns
from ai.api_keys import GEMINI_MODEL


def create_attack_path_agent(api_key: str, model: str = GEMINI_MODEL):
    """Create the Attack Path Analyst LLM agent."""
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.5,  # Slightly higher for creative attack scenarios
        max_output_tokens=8192
    )
    return llm


async def attack_path_node(state: SecurityState) -> Dict[str, Any]:
    """
    Attack Path Analyst node for the LangGraph workflow.

    This node runs IN PARALLEL with CVEHunter.

    This node:
    1. Analyzes network topology and device positions
    2. Identifies potential entry points
    3. Constructs attack paths showing compromise scenarios
    4. Assesses impact of each path
    """
    start_time = time.time()

    device_identifications = state.get("device_identifications", {})
    devices = state.get("devices", {})
    api_key = state.get("api_key")

    if not device_identifications:
        return {
            "attack_paths": [],
            "timing": {"attack_path": 0}
        }

    print(f"\n[ATTACK_PATH] Analyzing attack paths for {len(device_identifications)} devices...")

    # Categorize devices by type and risk
    cameras = []
    routers = []
    iot_devices = []
    high_risk_devices = []

    for ip, identification in device_identifications.items():
        device_type = identification.get("device_type", "unknown")
        risk_score = identification.get("risk_score", 0)
        vendor = identification.get("vendor", "Unknown")
        ports = devices.get(ip, {}).get("ports", [])
        risk_indicators = identification.get("risk_indicators", [])

        device_info = {
            "ip": ip,
            "vendor": vendor,
            "type": device_type,
            "risk_score": risk_score,
            "ports": ports,
            "risk_indicators": risk_indicators
        }

        if device_type == "camera":
            cameras.append(device_info)
        elif device_type == "router":
            routers.append(device_info)
        else:
            iot_devices.append(device_info)

        if risk_score > 50:
            high_risk_devices.append(device_info)

    # Get attack patterns for each device type
    attack_paths: List[AttackPath] = []

    # Generate attack paths for high-risk devices
    for device in high_risk_devices:
        device_type = device.get("type", "unknown")
        ip = device.get("ip")

        # Get relevant attack patterns
        patterns_str = get_attack_patterns.invoke({
            "device_type": device_type,
            "vulnerabilities": [],  # Will be filled from CVE findings later
            "network_position": "internal"
        })

        try:
            patterns_result = json.loads(patterns_str)
            patterns = patterns_result.get("patterns", [])

            for pattern in patterns[:2]:  # Top 2 patterns per device
                # Construct attack path
                steps = []
                for i, step in enumerate(pattern.get("steps", [])):
                    attack_step = AttackStep(
                        step_number=i + 1,
                        action=step,
                        target_device=ip,
                        vulnerability_used=pattern.get("mitre_id"),
                        access_gained="shell" if i == len(pattern.get("steps", [])) - 1 else "partial",
                        prerequisites=[]
                    )
                    steps.append(attack_step)

                attack_path = AttackPath(
                    path_id=f"path_{len(attack_paths) + 1}",
                    name=f"{device['vendor']} {device_type.title()} Compromise",
                    description=pattern.get("description", ""),
                    entry_point=ip,
                    target=ip,
                    steps=steps,
                    total_complexity="MEDIUM" if device.get("risk_score", 0) > 70 else "LOW",
                    impact=f"Full compromise of {device['vendor']} {device_type}",
                    likelihood=min(device.get("risk_score", 50) / 100, 0.9)
                )

                attack_paths.append(attack_path)
                print(f"[ATTACK_PATH] Generated: {attack_path['name']} (Likelihood: {attack_path['likelihood']:.1%})")

        except Exception as e:
            print(f"[ATTACK_PATH] Error generating path for {ip}: {e}")

    # Generate lateral movement paths if we have both cameras and routers
    if cameras and routers:
        # Camera -> Router pivot scenario
        camera = cameras[0]
        router = routers[0]

        lateral_path = AttackPath(
            path_id=f"path_{len(attack_paths) + 1}",
            name="Camera-to-Router Pivot Attack",
            description="Compromise a vulnerable camera and use it to pivot to the router",
            entry_point=camera["ip"],
            target=router["ip"],
            steps=[
                AttackStep(
                    step_number=1,
                    action=f"Exploit vulnerability on camera at {camera['ip']}",
                    target_device=camera["ip"],
                    vulnerability_used="CVE-2021-36260" if "hikvision" in camera.get("vendor", "").lower() else "Unknown",
                    access_gained="shell",
                    prerequisites=["Network access to camera"]
                ),
                AttackStep(
                    step_number=2,
                    action="Enumerate internal network from compromised camera",
                    target_device=camera["ip"],
                    access_gained="network_map",
                    prerequisites=["Camera shell access"]
                ),
                AttackStep(
                    step_number=3,
                    action=f"Attempt to access router admin at {router['ip']}",
                    target_device=router["ip"],
                    vulnerability_used="Default credentials or web exploit",
                    access_gained="admin",
                    prerequisites=["Network map", "Router IP known"]
                ),
                AttackStep(
                    step_number=4,
                    action="Modify DNS or routing rules for traffic interception",
                    target_device=router["ip"],
                    access_gained="mitm",
                    prerequisites=["Router admin access"]
                )
            ],
            total_complexity="HIGH",
            impact="Complete network compromise - traffic interception, credential theft",
            likelihood=0.6
        )

        attack_paths.append(lateral_path)
        print(f"[ATTACK_PATH] Generated: {lateral_path['name']} (Lateral Movement)")

    # Use LLM to generate more sophisticated attack paths
    if api_key and device_identifications:
        try:
            llm = create_attack_path_agent(api_key)

            # Build context for LLM
            network_summary = f"""
Network Analysis:
- Total devices: {len(device_identifications)}
- Cameras: {len(cameras)} ({', '.join([c['ip'] for c in cameras]) if cameras else 'none'})
- Routers: {len(routers)} ({', '.join([r['ip'] for r in routers]) if routers else 'none'})
- Other IoT: {len(iot_devices)}
- High-risk devices: {len(high_risk_devices)}

High-risk device details:
"""
            for device in high_risk_devices[:5]:
                network_summary += f"\n- {device['ip']}: {device['vendor']} {device['type']}"
                network_summary += f"\n  Ports: {device['ports']}"
                network_summary += f"\n  Risk: {device['risk_score']}"
                if device.get('risk_indicators'):
                    network_summary += f"\n  Issues: {device['risk_indicators'][:2]}"

            analysis_prompt = f"""{network_summary}

Based on this network, construct 2-3 realistic attack scenarios that an attacker might use.
For each scenario, describe:
1. Entry point (which device and how)
2. Attack progression (step by step)
3. Ultimate goal/impact
4. Likelihood of success (LOW/MEDIUM/HIGH)

Think like an attacker. Be specific about techniques used.
"""

            response = llm.invoke([
                SystemMessage(content=ATTACK_PATH_ANALYST_PROMPT),
                HumanMessage(content=analysis_prompt)
            ])

            print(f"\n[ATTACK_PATH] LLM Analysis:\n{response.content}")

        except Exception as e:
            print(f"[ATTACK_PATH] Could not generate LLM analysis: {e}")

    elapsed = time.time() - start_time

    # Summary
    print(f"\n[ATTACK_PATH] Complete: {len(attack_paths)} attack paths identified")

    return {
        "attack_paths": attack_paths,
        "timing": {"attack_path": elapsed}
    }


def attack_path_node_sync(state: SecurityState) -> Dict[str, Any]:
    """Synchronous version of attack_path_node."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(attack_path_node(state))
    finally:
        loop.close()
