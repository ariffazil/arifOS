"""
arifosmcp/runtime/federation_quarantine.py — External Agent Isolation
══════════════════════════════════════════════════════════════════════

Implements Gap 8: Federation Quarantine.
Ensures external agent outputs are treated as evidence only, not authority.
Blocks direct execution from federated agent payloads.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from typing import Any, Dict, List

def wrap_federated_output(agent_id: str, raw_output: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wraps federated agent output in a quarantine envelope.
    """
    return {
        "agent_id": agent_id,
        "agent_identity_verified": metadata.get("identity_verified", False),
        "content_role": "evidence_not_instruction",
        "capability_scope": metadata.get("scope", []),
        "can_execute": False,  # Hard invariant: Federated agents cannot execute
        "can_advise": True,
        "injection_scan": metadata.get("injection_status", "unknown"),
        "raw_payload": raw_output,
        "governance_layer": "arifos_quarantine_v1"
    }

def validate_external_payload(payload: Dict[str, Any]) -> bool:
    """
    Checks if a payload contains unauthorized instructions or authority elevation attempts.
    """
    forbidden_keywords = ["sudo", "rm -rf", "grant access", "elevate", "override constitution"]
    content = str(payload.get("raw_payload", "")).lower()
    
    for kw in forbidden_keywords:
        if kw in content:
            return False
            
    return True
