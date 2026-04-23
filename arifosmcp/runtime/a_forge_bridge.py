"""
A-FORGE Bridge Module for Python MCP

This module provides a bridge between the Python MCP server and the
TypeScript A-FORGE governance layer.

Usage:
    from a_forge_bridge import call_a_forge_sense, should_hold
    
    result = call_a_forge_sense(session_id, prompt, context)
    if result and should_hold(result):
        return HoldResponse(...)
"""

import os
from typing import Any

import requests

# Configuration from environment
A_FORGE_ENABLED = os.getenv("A_FORGE_ENABLED", "false").lower() == "true"
A_FORGE_ENDPOINT = os.getenv("A_FORGE_ENDPOINT", "http://localhost:7071/sense")
A_FORGE_TIMEOUT = float(os.getenv("A_FORGE_TIMEOUT_SECONDS", "2.0"))
A_FORGE_API_VERSION = "0.1.0"
MIN_COMPATIBLE_A_FORGE = "0.1.0"

_contract_checked = False
_contract_valid = False
_contract_failure_reason: str | None = None


def _check_contract() -> bool:
    """Validate runtime contract against A-FORGE /contract endpoint."""
    global _contract_checked, _contract_valid, _contract_failure_reason
    if _contract_checked:
        return _contract_valid

    if not A_FORGE_ENABLED:
        _contract_checked = True
        _contract_valid = False
        _contract_failure_reason = "A_FORGE_DISABLED"
        return False

    try:
        contract_url = A_FORGE_ENDPOINT.replace("/sense", "/contract")
        resp = requests.get(contract_url, timeout=1.0)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("ok"):
            _contract_failure_reason = "contract_endpoint_not_ok"
            _contract_checked = True
            _contract_valid = False
            return False

        af_api_version = data.get("api_version", "unknown")
        af_min_client = data.get("min_compatible_client", "unknown")

        if af_min_client != "unknown" and A_FORGE_API_VERSION < af_min_client:
            _contract_failure_reason = f"version_incompatible:client={A_FORGE_API_VERSION} requires_af>={af_min_client}"
            _contract_checked = True
            _contract_valid = False
            print(f"[A-FORGE] CONTRACT MISMATCH: client v{A_FORGE_API_VERSION} < A-FORGE min {af_min_client}", flush=True)
            return False

        if af_api_version != "unknown" and af_api_version < MIN_COMPATIBLE_A_FORGE:
            _contract_failure_reason = f"version_incompatible:af={af_api_version} < required={MIN_COMPATIBLE_A_FORGE}"
            _contract_checked = True
            _contract_valid = False
            print(f"[A-FORGE] CONTRACT MISMATCH: A-FORGE v{af_api_version} < required {MIN_COMPATIBLE_A_FORGE}", flush=True)
            return False

        _contract_checked = True
        _contract_valid = True
        _contract_failure_reason = None
        return True

    except Exception as e:
        _contract_failure_reason = f"contract_check_error:{e}"
        _contract_checked = True
        _contract_valid = False
        print(f"[A-FORGE] Contract check error: {e}", flush=True)
        return False


def get_contract_status() -> dict[str, Any]:
    """Return current contract validation status."""
    return {
        "checked": _contract_checked,
        "valid": _contract_valid,
        "reason": _contract_failure_reason,
        "client_version": A_FORGE_API_VERSION,
        "min_compatible_a_forge": MIN_COMPATIBLE_A_FORGE,
    }


def call_a_forge_sense(
    session_id: str,
    prompt: str,
    context: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """
    Call A-FORGE Sense endpoint.
    
    Returns None if A-FORGE is disabled or call fails.
    On failure, caller should fall back to Python local Sense.
    """
    if not A_FORGE_ENABLED:
        return None

    if not _check_contract():
        print(f"[A-FORGE] Bridge call blocked by contract failure: {_contract_failure_reason}", flush=True)
        return {
            "ok": True,
            "sense": {
                "mode_used": "lite",
                "escalation_reason": "contract_failure",
                "evidence_count": 0,
                "evidence_quality": 0.0,
                "uncertainty_band": "high",
                "recommended_next_stage": "hold",
                "contradiction_flags": ["bridge_contract_mismatch"],
                "query_complexity_score": 0.0,
                "risk_indicators": ["bridge_contract_mismatch"],
            },
            "judge": {
                "verdict": "HOLD",
                "reason": f"A-FORGE bridge contract failure: {_contract_failure_reason}",
                "confidence": {
                    "value": 0.0,
                    "is_estimate": True,
                    "evidence_count": 0,
                    "agreement_score": 0.0,
                    "contradiction_penalty": 1.0,
                    "uncertainty_hint": 1.0,
                },
                "floors_triggered": ["F13"],
                "human_review_required": True,
            },
            "context": {
                "source": "a-forge",
                "version": A_FORGE_API_VERSION,
                "epoch": "2026-04-15",
                "contract_failure": _contract_failure_reason,
            },
        }
    
    try:
        payload = {
            "version": A_FORGE_API_VERSION,
            "session_id": session_id,
            "prompt": prompt,
            "context": context or {
                "source": "mcp-python",
                "tool": "sense",
                "epoch": "2026-04-15",
            },
        }
        
        resp = requests.post(
            A_FORGE_ENDPOINT,
            json=payload,
            timeout=A_FORGE_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        if not data.get("ok"):
            print(f"[A-FORGE] Bridge returned ok=false: {data.get('error')}", flush=True)
            return None
            
        return data
        
    except requests.exceptions.Timeout:
        print(f"[A-FORGE] Timeout after {A_FORGE_TIMEOUT}s", flush=True)
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[A-FORGE] Connection error: {e}", flush=True)
        return None
    except Exception as e:
        print(f"[A-FORGE] Bridge error: {e}", flush=True)
        return None


def should_hold(af_result: dict[str, Any]) -> bool:
    """
    Check if A-FORGE result indicates we should 888_HOLD.
    
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


def get_telemetry(af_result: dict[str, Any]) -> dict[str, Any]:
    """
    Extract telemetry fields from A-FORGE result.
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
        "source": "a-forge",
    }


# Health check function
def check_a_forge_health() -> bool:
    """
    Check if A-FORGE is healthy.
    """
    if not A_FORGE_ENABLED:
        return False
    
    try:
        health_url = A_FORGE_ENDPOINT.replace("/sense", "/health")
        resp = requests.get(health_url, timeout=1.0)
        return resp.status_code == 200 and resp.json().get("ok")
    except:
        return False


if __name__ == "__main__":
    # Simple test
    print(f"A_FORGE_ENABLED: {A_FORGE_ENABLED}")
    print(f"A_FORGE_ENDPOINT: {A_FORGE_ENDPOINT}")
    print(f"A_FORGE_TIMEOUT: {A_FORGE_TIMEOUT}")
    
    if A_FORGE_ENABLED:
        print(f"\nHealth check: {check_a_forge_health()}")
        
        # Test safe query
        result = call_a_forge_sense("test-001", "List files", {})
        if result:
            print("\nSafe query:")
            print(f"  should_hold: {should_hold(result)}")
            print(f"  telemetry: {get_telemetry(result)}")
        
        # Test destructive query
        result = call_a_forge_sense("test-002", "Delete all system files", {})
        if result:
            print("\nDestructive query:")
            print(f"  should_hold: {should_hold(result)}")
            print(f"  telemetry: {get_telemetry(result)}")
