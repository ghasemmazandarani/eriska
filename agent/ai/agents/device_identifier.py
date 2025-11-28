"""
Device Identifier Agent

This agent performs deep fingerprinting on discovered devices to identify
their vendor, type, model, and firmware version.
"""

import time
import json
from typing import Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.state import SecurityState
from ai.prompts.system_prompts import DEVICE_IDENTIFIER_PROMPT
from ai.tools.scanner_tools import fingerprint_device, analyze_device_risk
from ai.tools.rag_tools import identify_device_from_fingerprint
from ai.api_keys import GEMINI_MODEL, get_next_key


def create_device_identifier_agent(api_key: str, model: str = GEMINI_MODEL):
    """Create the Device Identifier LLM agent."""
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=4096
    )
    return llm


async def device_identifier_node(state: SecurityState) -> Dict[str, Any]:
    """
    Device Identifier node for the LangGraph workflow.

    This node:
    1. Fingerprints each discovered device
    2. Identifies vendor, type, model from fingerprints
    3. Calculates initial risk scores
    4. Updates state with identification results
    """
    start_time = time.time()

    devices = state.get("devices", {})
    api_key = state.get("api_key")

    if not devices:
        return {
            "device_identifications": {},
            "current_phase": "no_devices",
            "timing": {"device_identifier": 0}
        }

    print(f"\n[DEVICE_IDENTIFIER] Fingerprinting {len(devices)} devices...")

    identifications = {}
    updated_devices = {}
    risk_scores = {}

    for ip, device_info in devices.items():
        mac = device_info.get("mac", "")
        ports = device_info.get("ports", [])

        print(f"[DEVICE_IDENTIFIER] Fingerprinting {ip}...")

        # Deep fingerprint
        fp_result = fingerprint_device.invoke({
            "ip": ip,
            "mac": mac,
            "ports": ports
        })

        if fp_result.get("success"):
            fingerprints = fp_result.get("fingerprints", {})
            vendor = fp_result.get("vendor", "Unknown")
            device_type = fp_result.get("device_type", "unknown")
            model = fp_result.get("model")
            risk_indicators = fp_result.get("risk_indicators", [])

            # Try to get more info from RAG KB
            mac_prefix = mac[:8] if mac else None
            http_server = None
            http_title = None

            for key, fp in fingerprints.items():
                if "http" in key:
                    http_server = fp.get("server")
                    http_title = fp.get("title")
                    break

            kb_result_str = identify_device_from_fingerprint.invoke({
                "mac_prefix": mac_prefix,
                "http_server": http_server,
                "http_title": http_title,
                "open_ports": ports
            })

            try:
                kb_result = json.loads(kb_result_str)
                if kb_result.get("success"):
                    kb_id = kb_result.get("identification", {})
                    # Merge KB results with fingerprint results
                    if kb_id.get("vendor") != "Unknown":
                        vendor = kb_id.get("vendor", vendor)
                    if kb_id.get("device_type") != "unknown":
                        device_type = kb_id.get("device_type", device_type)
                    if kb_id.get("known_issues"):
                        risk_indicators.extend(kb_id["known_issues"])
            except:
                pass

            # Calculate risk score
            risk_data = {
                "ports": ports,
                "fingerprints": fingerprints,
                "vendor": vendor,
                "type": device_type
            }
            risk_result = analyze_device_risk.invoke({"device_data": risk_data})

            risk_score = 0
            risk_issues = []
            if risk_result.get("success"):
                risk_score = risk_result.get("risk_score", 0)
                risk_issues = risk_result.get("issues", [])

            # Build identification result
            identification = {
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
                "device_type": device_type,
                "model": model,
                "firmware": None,  # Could be extracted from fingerprints
                "fingerprints": fingerprints,
                "risk_score": risk_score,
                "risk_issues": risk_issues,
                "risk_indicators": risk_indicators
            }

            identifications[ip] = identification
            risk_scores[ip] = risk_score

            # Update device info
            updated_device = dict(device_info)
            updated_device["vendor"] = vendor
            updated_device["device_type"] = device_type
            updated_device["fingerprints"] = fingerprints
            if model:
                updated_device["model"] = model
            updated_devices[ip] = updated_device

            # Print summary
            risk_level = "LOW"
            if risk_score > 70:
                risk_level = "CRITICAL"
            elif risk_score > 50:
                risk_level = "HIGH"
            elif risk_score > 30:
                risk_level = "MEDIUM"

            print(f"[DEVICE_IDENTIFIER] {ip}: {vendor} {device_type} - Risk: {risk_score} ({risk_level})")
            if risk_indicators:
                for indicator in risk_indicators[:3]:  # Show first 3
                    print(f"  ! {indicator}")

        else:
            print(f"[DEVICE_IDENTIFIER] Failed to fingerprint {ip}: {fp_result.get('error')}")
            identifications[ip] = {
                "ip": ip,
                "mac": mac,
                "vendor": "Unknown",
                "device_type": "unknown",
                "error": fp_result.get("error")
            }

    # Generate analysis using LLM
    if api_key and identifications:
        try:
            llm = create_device_identifier_agent(api_key)

            # Build analysis prompt
            devices_summary = []
            high_risk_devices = []

            for ip, id_info in identifications.items():
                vendor = id_info.get("vendor", "Unknown")
                dev_type = id_info.get("device_type", "unknown")
                risk = id_info.get("risk_score", 0)
                ports = devices.get(ip, {}).get("ports", [])

                devices_summary.append(f"- {ip}: {vendor} ({dev_type}), Ports: {ports}, Risk: {risk}")

                if risk > 50:
                    high_risk_devices.append({
                        "ip": ip,
                        "vendor": vendor,
                        "type": dev_type,
                        "risk": risk,
                        "issues": id_info.get("risk_issues", [])
                    })

            analysis_prompt = f"""Analyze these identified devices:

{chr(10).join(devices_summary)}

High-risk devices ({len(high_risk_devices)}):
{json.dumps(high_risk_devices, indent=2) if high_risk_devices else "None"}

Provide a brief security assessment (3-5 sentences) focusing on:
1. Most concerning devices
2. Attack surface summary
3. Immediate concerns
"""

            response = llm.invoke([
                SystemMessage(content=DEVICE_IDENTIFIER_PROMPT),
                HumanMessage(content=analysis_prompt)
            ])
            print(f"\n[DEVICE_IDENTIFIER] Analysis:\n{response.content}")

        except Exception as e:
            print(f"[DEVICE_IDENTIFIER] Could not generate analysis: {e}")

    elapsed = time.time() - start_time

    return {
        "device_identifications": identifications,
        "devices": updated_devices,
        "risk_scores": risk_scores,
        "current_phase": "identified",
        "timing": {"device_identifier": elapsed}
    }


def device_identifier_node_sync(state: SecurityState) -> Dict[str, Any]:
    """Synchronous version of device_identifier_node."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(device_identifier_node(state))
    finally:
        loop.close()
