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
AF_FORGE_API_VERSION = "0.1.0"
MIN_COMPATIBLE_AF_FORGE = "0.1.0"

_contract_checked = False
_contract_valid = False
_contract_failure_reason: Optional[str] = None


def _check_contract() -> bool:
    """Validate runtime contract against AF-FORGE /contract endpoint."""
    global _contract_checked, _contract_valid, _contract_failure_reason
    if _contract_checked:
        return _contract_valid

    if not AF_FORGE_ENABLED:
        _contract_checked = True
        _contract_valid = False
        _contract_failure_reason = "AF_FORGE_DISABLED"
        return False

    try:
        contract_url = AF_FORGE_ENDPOINT.replace("/sense", "/contract")
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

        if af_min_client != "unknown" and AF_FORGE_API_VERSION < af_min_client:
            _contract_failure_reason = f"version_incompatible:client={AF_FORGE_API_VERSION} requires_af>={af_min_client}"
            _contract_checked = True
            _contract_valid = False
            print(f"[AF-FORGE] CONTRACT MISMATCH: client v{AF_FORGE_API_VERSION} < AF-FORGE min {af_min_client}", flush=True)
            return False

        if af_api_version != "unknown" and af_api_version < MIN_COMPATIBLE_AF_FORGE:
            _contract_failure_reason = f"version_incompatible:af={af_api_version} < required={MIN_COMPATIBLE_AF_FORGE}"
            _contract_checked = True
            _contract_valid = False
            print(f"[AF-FORGE] CONTRACT MISMATCH: AF-FORGE v{af_api_version} < required {MIN_COMPATIBLE_AF_FORGE}", flush=True)
            return False

        _contract_checked = True
        _contract_valid = True
        _contract_failure_reason = None
        return True

    except Exception as e:
        _contract_failure_reason = f"contract_check_error:{e}"
        _contract_checked = True
        _contract_valid = False
        print(f"[AF-FORGE] Contract check error: {e}", flush=True)
        return False


def get_contract_status() -> Dict[str, Any]:
    """Return current contract validation status."""
    return {
        "checked": _contract_checked,
        "valid": _contract_valid,
        "reason": _contract_failure_reason,
        "client_version": AF_FORGE_API_VERSION,
        "min_compatible_af_forge": MIN_COMPATIBLE_AF_FORGE,
    }


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

    if not _check_contract():
        print(f"[AF-FORGE] Bridge call blocked by contract failure: {_contract_failure_reason}", flush=True)
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
                "reason": f"AF-FORGE bridge contract failure: {_contract_failure_reason}",
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
                "source": "af-forge",
                "version": AF_FORGE_API_VERSION,
                "epoch": "2026-04-15",
                "contract_failure": _contract_failure_reason,
            },
        }
    
    try:
        payload = {
            "version": AF_FORGE_API_VERSION,
            "session_id": session_id,
            "prompt": prompt,
            "context": context or {
                "source": "mcp-python",
                "tool": "sense",
                "epoch": "2026-04-15",
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
