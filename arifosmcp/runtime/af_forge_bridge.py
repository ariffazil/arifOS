"""
AF-FORGE Bridge Module for Python MCP

This module provides a bridge between the Python MCP server and the
TypeScript AF-FORGE governance layer.

Usage:
    from af_forge_bridge import call_af_forge_sense, should_hold
    
    result = call_af_forge_sense(session_id, prompt, context)
    if result and should_hold(result):
        return HoldResponse(...)
"""

import os
import requests
from typing import Optional, Dict, Any

# Configuration from environment
AF_FORGE_ENABLED = os.getenv("AF_FORGE_ENABLED", "false").lower() == "true"
AF_FORGE_ENDPOINT = os.getenv("AF_FORGE_ENDPOINT", "http://localhost:7071/sense")
AF_FORGE_TIMEOUT = float(os.getenv("AF_FORGE_TIMEOUT_SECONDS", "2.0"))


def call_af_forge_sense(
    session_id: str,
    prompt: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Call AF-FORGE Sense endpoint.
    
    Returns None if AF-FORGE is disabled or call fails.
    On failure, caller should fall back to Python local Sense.
    """
    if not AF_FORGE_ENABLED:
        return None
    
    try:
        payload = {
            "version": "1",
            "session_id": session_id,
            "prompt": prompt,
            "context": context or {
                "source": "mcp-python",
                "tool": "sense",
                "epoch": "2026-04-08",
            },
        }
        
        resp = requests.post(
            AF_FORGE_ENDPOINT,
            json=payload,
            timeout=AF_FORGE_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        if not data.get("ok"):
            print(f"[AF-FORGE] Bridge returned ok=false: {data.get('error')}", flush=True)
            return None
            
        return data
        
    except requests.exceptions.Timeout:
        print(f"[AF-FORGE] Timeout after {AF_FORGE_TIMEOUT}s", flush=True)
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[AF-FORGE] Connection error: {e}", flush=True)
        return None
    except Exception as e:
        print(f"[AF-FORGE] Bridge error: {e}", flush=True)
        return None


def should_hold(af_result: Dict[str, Any]) -> bool:
    """
    Check if AF-FORGE result indicates we should 888_HOLD.
    
    Checks Sense recommendation first, then Judge verdict.
    """
    sense = af_result.get("sense", {})
    judge = af_result.get("judge", {})
    
    # Primary: Sense recommendation
    if sense.get("recommended_next_stage") == "hold":
        return True
    
    # Secondary: Judge verdict
    if judge.get("verdict") == "HOLD":
        return True
    
    # Also hold for VOID
    if judge.get("verdict") == "VOID":
        return True
        
    return False


def get_telemetry(af_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract telemetry fields from AF-FORGE result.
    """
    sense = af_result.get("sense", {})
    judge = af_result.get("judge", {})
    
    return {
        "senseMode": sense.get("mode_used"),
        "senseUncertaintyBand": sense.get("uncertainty_band"),
        "senseEvidenceCount": sense.get("evidence_count"),
        "senseComplexityScore": sense.get("query_complexity_score"),
        "senseRiskIndicators": sense.get("risk_indicators", []),
        "judgeVerdict": judge.get("verdict"),
        "judgeConfidence": judge.get("confidence", {}).get("value"),
        "judgeFloorsTriggered": judge.get("floors_triggered", []),
        "source": "af-forge",
    }


# Health check function
def check_af_forge_health() -> bool:
    """
    Check if AF-FORGE is healthy.
    """
    if not AF_FORGE_ENABLED:
        return False
    
    try:
        health_url = AF_FORGE_ENDPOINT.replace("/sense", "/health")
        resp = requests.get(health_url, timeout=1.0)
        return resp.status_code == 200 and resp.json().get("ok")
    except:
        return False


if __name__ == "__main__":
    # Simple test
    print(f"AF_FORGE_ENABLED: {AF_FORGE_ENABLED}")
    print(f"AF_FORGE_ENDPOINT: {AF_FORGE_ENDPOINT}")
    print(f"AF_FORGE_TIMEOUT: {AF_FORGE_TIMEOUT}")
    
    if AF_FORGE_ENABLED:
        print(f"\nHealth check: {check_af_forge_health()}")
        
        # Test safe query
        result = call_af_forge_sense("test-001", "List files", {})
        if result:
            print(f"\nSafe query:")
            print(f"  should_hold: {should_hold(result)}")
            print(f"  telemetry: {get_telemetry(result)}")
        
        # Test destructive query
        result = call_af_forge_sense("test-002", "Delete all system files", {})
        if result:
            print(f"\nDestructive query:")
            print(f"  should_hold: {should_hold(result)}")
            print(f"  telemetry: {get_telemetry(result)}")
