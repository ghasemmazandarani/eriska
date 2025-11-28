"""
Scan Monitor Agent

This agent is responsible for continuous network monitoring and device discovery.
It scans the network, identifies new devices, and tracks changes.
"""

import time
from datetime import datetime
from typing import Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.state import SecurityState, DeviceInfo
from ai.prompts.system_prompts import SCAN_MONITOR_PROMPT
from ai.tools.scanner_tools import scan_network, scan_ports, get_network_info


def create_scan_monitor_agent(api_key: str, model: str = "gemini-2.5-pro"):
    """Create the Scan Monitor LLM agent."""
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=4096
    )
    return llm


async def scan_monitor_node(state: SecurityState) -> Dict[str, Any]:
    """
    Scan Monitor node for the LangGraph workflow.

    This node:
    1. Scans the network to discover devices
    2. Scans ports on each discovered device
    3. Tracks new vs. existing devices
    4. Updates state with scan results
    """
    start_time = time.time()

    network_range = state.get("network_range")
    api_key = state.get("api_key")
    existing_devices = state.get("devices", {})

    # Get network info if range not specified
    if not network_range:
        net_info = get_network_info.invoke({})
        if net_info.get("success"):
            network_range = net_info["network_range"]
        else:
            return {
                "errors": [f"Failed to get network info: {net_info.get('error')}"],
                "current_phase": "scan_failed"
            }

    print(f"\n[SCAN_MONITOR] Scanning network: {network_range}")

    # Perform network scan
    scan_result = scan_network.invoke({"network_range": network_range})

    if not scan_result.get("success"):
        return {
            "errors": [f"Network scan failed: {scan_result.get('error')}"],
            "current_phase": "scan_failed"
        }

    discovered_devices = scan_result.get("devices", {})
    print(f"[SCAN_MONITOR] Discovered {len(discovered_devices)} devices")

    # Track new devices
    new_device_ips = []
    changed_device_ips = []

    # Scan ports on each device and build device info
    devices: Dict[str, DeviceInfo] = {}

    for ip, device_data in discovered_devices.items():
        print(f"[SCAN_MONITOR] Scanning ports on {ip}...")

        # Scan ports
        port_result = scan_ports.invoke({"target_ip": ip})
        open_ports = port_result.get("open_ports", []) if port_result.get("success") else []

        # Build device info
        device_info = DeviceInfo(
            ip=ip,
            mac=device_data.get("mac", ""),
            vendor=device_data.get("vendor", "Unknown"),
            device_type="unknown",  # Will be filled by DeviceIdentifier
            ports=open_ports,
            fingerprints={},
            first_seen=device_data.get("first_seen", time.time()),
            last_seen=time.time()
        )

        devices[ip] = device_info

        # Check if this is a new device
        if ip not in existing_devices:
            new_device_ips.append(ip)
            print(f"[SCAN_MONITOR] NEW DEVICE: {ip} ({device_info['mac']})")
        else:
            # Check for changes (different ports)
            old_ports = set(existing_devices[ip].get("ports", []))
            new_ports = set(open_ports)
            if old_ports != new_ports:
                changed_device_ips.append(ip)
                print(f"[SCAN_MONITOR] CHANGED: {ip} - ports changed")

    # Calculate timing
    elapsed = time.time() - start_time

    # Generate summary using LLM if we have an API key
    summary = ""
    if api_key and (new_device_ips or devices):
        try:
            llm = create_scan_monitor_agent(api_key)
            summary_prompt = f"""Briefly summarize this network scan result (2-3 sentences):
- Network: {network_range}
- Total devices: {len(devices)}
- New devices: {len(new_device_ips)}
- Changed devices: {len(changed_device_ips)}

Devices found:
"""
            for ip, info in devices.items():
                ports_str = ", ".join(map(str, info.get("ports", []))) or "none"
                summary_prompt += f"- {ip} ({info.get('mac', 'unknown')}) - Ports: {ports_str}\n"

            response = llm.invoke([
                SystemMessage(content="You are a network security analyst. Be concise."),
                HumanMessage(content=summary_prompt)
            ])
            summary = response.content
            print(f"\n[SCAN_MONITOR] Summary: {summary}")
        except Exception as e:
            print(f"[SCAN_MONITOR] Could not generate summary: {e}")

    return {
        "devices": devices,
        "new_devices": new_device_ips,
        "changed_devices": changed_device_ips,
        "network_range": network_range,
        "scan_timestamp": datetime.now().isoformat(),
        "current_phase": "scanned",
        "timing": {"scan_monitor": elapsed}
    }


# Synchronous version for simpler testing
def scan_monitor_node_sync(state: SecurityState) -> Dict[str, Any]:
    """Synchronous version of scan_monitor_node."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(scan_monitor_node(state))
    finally:
        loop.close()
