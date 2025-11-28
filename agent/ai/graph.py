"""
LangGraph Security Workflow

This module defines the main LangGraph workflow that orchestrates
all security agents in the correct order with parallel execution
where possible.

Workflow:
    ┌─────────────────┐
    │   ScanMonitor   │ (Network Discovery)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ DeviceIdentifier│ (Fingerprinting)
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼───┐       ┌─────▼─────┐
│  CVE  │       │  Attack   │  (Parallel Execution)
│Hunter │       │   Path    │
└───┬───┘       └─────┬─────┘
    │                 │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ DebateSynthesis │ (Verification & Report)
    └────────┬────────┘
             │
            END
"""

import os
import time
from typing import Dict, Any, Literal

from langgraph.graph import StateGraph, START, END

import sys
sys.path.insert(0, os.path.dirname(__file__))

from state import SecurityState
from api_keys import get_next_key, GEMINI_MODEL, get_key_manager
from agents.scan_monitor import scan_monitor_node_sync
from agents.device_identifier import device_identifier_node_sync
from agents.cve_hunter import cve_hunter_node_sync
from agents.attack_path import attack_path_node_sync
from agents.debate_synthesis import debate_synthesis_node_sync


def should_continue_to_identification(state: SecurityState) -> Literal["device_identifier", "end"]:
    """Decide if we should continue to device identification."""
    devices = state.get("devices", {})
    if devices:
        return "device_identifier"
    print("[GRAPH] No devices found, ending workflow")
    return "end"


def should_continue_to_analysis(state: SecurityState) -> Literal["parallel_analysis", "end"]:
    """Decide if we should continue to CVE/Attack analysis."""
    identifications = state.get("device_identifications", {})
    if identifications:
        return "parallel_analysis"
    print("[GRAPH] No device identifications, ending workflow")
    return "end"


def create_security_graph() -> StateGraph:
    """
    Create the main security analysis LangGraph workflow.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph with our state schema
    graph = StateGraph(SecurityState)

    # Add nodes for each agent
    graph.add_node("scan_monitor", scan_monitor_node_sync)
    graph.add_node("device_identifier", device_identifier_node_sync)
    graph.add_node("cve_hunter", cve_hunter_node_sync)
    graph.add_node("attack_path", attack_path_node_sync)
    graph.add_node("debate_synthesis", debate_synthesis_node_sync)

    # Define the workflow edges
    # START -> ScanMonitor
    graph.add_edge(START, "scan_monitor")

    # ScanMonitor -> DeviceIdentifier (conditional)
    graph.add_conditional_edges(
        "scan_monitor",
        should_continue_to_identification,
        {
            "device_identifier": "device_identifier",
            "end": END
        }
    )

    # DeviceIdentifier -> Parallel (CVEHunter + AttackPath)
    graph.add_conditional_edges(
        "device_identifier",
        should_continue_to_analysis,
        {
            "parallel_analysis": "cve_hunter",
            "end": END
        }
    )

    # For true parallel execution, we add both edges from device_identifier
    # LangGraph will execute nodes with no dependencies in parallel
    graph.add_edge("device_identifier", "attack_path")

    # Both parallel nodes -> DebateSynthesis
    graph.add_edge("cve_hunter", "debate_synthesis")
    graph.add_edge("attack_path", "debate_synthesis")

    # DebateSynthesis -> END
    graph.add_edge("debate_synthesis", END)

    return graph


def compile_security_graph():
    """Compile the security graph for execution."""
    graph = create_security_graph()
    return graph.compile()


async def run_security_analysis(
    network_range: str,
    api_key: str = None,
    continuous: bool = False,
    scan_interval: int = 300
) -> Dict[str, Any]:
    """
    Run a complete security analysis on the specified network.

    Args:
        network_range: CIDR notation network range (e.g., "192.168.1.0/24")
        api_key: Google Gemini API key (optional - uses rotating keys if not provided)
        continuous: Whether to run in continuous monitoring mode
        scan_interval: Seconds between scans in continuous mode

    Returns:
        Final state with all findings and report
    """
    # Get API key from rotation if not provided
    if not api_key:
        api_key = get_next_key()

    key_manager = get_key_manager()

    print(f"\n{'='*60}")
    print(f"ERISKA AI SECURITY ANALYSIS")
    print(f"{'='*60}")
    print(f"Target Network: {network_range}")
    print(f"Mode: {'Continuous' if continuous else 'Single Scan'}")
    print(f"Model: {GEMINI_MODEL}")
    print(f"API Keys Available: {key_manager.key_count}")
    print(f"{'='*60}\n")

    # Compile the graph
    app = compile_security_graph()

    # Initial state - use rotating key
    initial_state: SecurityState = {
        "network_range": network_range,
        "api_key": get_next_key(),  # Get fresh key for each run
        "devices": {},
        "device_identifications": {},
        "cve_findings": {},
        "attack_paths": [],
        "remediation_steps": [],
        "current_phase": "starting",
        "timing": {}
    }

    iteration = 0
    while True:
        iteration += 1
        scan_start = time.time()

        if continuous:
            print(f"\n[SCAN {iteration}] Starting security scan...")

        # Run the graph
        final_state = None
        async for event in app.astream(initial_state):
            # Track progress
            for node_name, node_output in event.items():
                if node_name != "__end__":
                    phase = node_output.get("current_phase", node_name)
                    print(f"[PROGRESS] Completed: {node_name}")
                final_state = node_output

        scan_elapsed = time.time() - scan_start

        # Print timing summary
        if final_state and "timing" in final_state:
            print(f"\n[TIMING] Total scan time: {scan_elapsed:.1f}s")
            for phase, duration in final_state.get("timing", {}).items():
                print(f"  - {phase}: {duration:.1f}s")

        # If not continuous, exit after first scan
        if not continuous:
            break

        # Wait for next scan interval
        print(f"\n[CONTINUOUS] Next scan in {scan_interval} seconds...")
        import asyncio
        await asyncio.sleep(scan_interval)

        # Update state for next iteration (keep existing device data)
        initial_state = {
            **initial_state,
            "devices": final_state.get("devices", {}),
            "device_identifications": final_state.get("device_identifications", {}),
        }

    return final_state


def run_security_analysis_sync(
    network_range: str,
    api_key: str,
    continuous: bool = False,
    scan_interval: int = 300
) -> Dict[str, Any]:
    """Synchronous wrapper for run_security_analysis."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            run_security_analysis(network_range, api_key, continuous, scan_interval)
        )
    finally:
        loop.close()


# Alternative: Simple sequential execution for debugging
def run_sequential_analysis(network_range: str, api_key: str = None) -> Dict[str, Any]:
    """
    Run analysis sequentially (for debugging).

    This bypasses LangGraph and runs each agent in sequence.
    """
    # Get API key from rotation if not provided
    if not api_key:
        api_key = get_next_key()

    key_manager = get_key_manager()
    print(f"[DEBUG] Running sequential analysis with {key_manager.key_count} API keys available")
    print(f"[DEBUG] Using model: {GEMINI_MODEL}")

    state: SecurityState = {
        "network_range": network_range,
        "api_key": get_next_key(),  # Get fresh rotating key
        "devices": {},
        "device_identifications": {},
        "cve_findings": {},
        "attack_paths": [],
        "remediation_steps": [],
        "current_phase": "starting",
        "timing": {}
    }

    # Step 1: Scan Monitor
    print("\n[STEP 1] Running ScanMonitor...")
    result = scan_monitor_node_sync(state)
    state = {**state, **result}

    if not state.get("devices"):
        print("[DEBUG] No devices found, stopping")
        return state

    # Step 2: Device Identifier
    print("\n[STEP 2] Running DeviceIdentifier...")
    result = device_identifier_node_sync(state)
    state = {**state, **result}

    if not state.get("device_identifications"):
        print("[DEBUG] No identifications, stopping")
        return state

    # Step 3a: CVE Hunter
    print("\n[STEP 3a] Running CVEHunter...")
    cve_result = cve_hunter_node_sync(state)

    # Step 3b: Attack Path (would run in parallel normally)
    print("\n[STEP 3b] Running AttackPathAnalyst...")
    attack_result = attack_path_node_sync(state)

    # Merge parallel results
    state = {
        **state,
        "cve_findings": cve_result.get("cve_findings", {}),
        "attack_paths": attack_result.get("attack_paths", []),
        "timing": {
            **state.get("timing", {}),
            **cve_result.get("timing", {}),
            **attack_result.get("timing", {})
        }
    }

    # Step 4: Debate Synthesis
    print("\n[STEP 4] Running DebateSynthesis...")
    result = debate_synthesis_node_sync(state)
    state = {**state, **result}

    return state


if __name__ == "__main__":
    # Test the graph compilation
    print("Testing LangGraph workflow compilation...")

    try:
        app = compile_security_graph()
        print("✓ Graph compiled successfully!")

        # Print graph structure
        print("\nGraph nodes:")
        for node in ["scan_monitor", "device_identifier", "cve_hunter", "attack_path", "debate_synthesis"]:
            print(f"  - {node}")

        print("\nWorkflow ready for execution.")
        print("Use run_security_analysis() or run_sequential_analysis() to start.")

    except Exception as e:
        print(f"✗ Graph compilation failed: {e}")
        raise
