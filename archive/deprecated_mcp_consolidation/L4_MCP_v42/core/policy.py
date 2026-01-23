"""
Policy Lookup for L4_MCP.

Retrieves policy/rule references for given reason codes.
"""

from typing import Dict, List


def policy_lookup_for(reason_codes: List[str]) -> Dict[str, str]:
    """
    Fetch authoritative policy or rule references for given reason codes.

    Args:
        reason_codes: List of triggered rule codes

    Returns:
        Dict mapping reason codes to policy references

    TODO: Connect to L1_THEORY canon for actual policy text
    """
    # Policy reference mapping (stub - to be connected to L1_THEORY)
    policy_refs = {
        "F1": "L1_THEORY/canon/01_floors/F1_AMANAH.md",
        "F2": "L1_THEORY/canon/01_floors/F2_TRUTH.md",
        "F3": "L1_THEORY/canon/01_floors/F3_TRIWITNESS.md",
        "F4": "L1_THEORY/canon/01_floors/F4_CLARITY.md",
        "F5": "L1_THEORY/canon/01_floors/F5_PEACE2.md",
        "F6": "L1_THEORY/canon/01_floors/F6_KAPPA_R.md",
        "F7": "L1_THEORY/canon/01_floors/F7_OMEGA_0.md",
        "F8": "L1_THEORY/canon/01_floors/F8_GENIUS.md",
        "F9": "L1_THEORY/canon/01_floors/F9_ANTIHANTU.md",
        "ROUTING_SEAL": "L1_THEORY/canon/03_runtime/000_999_PIPELINE.md",
    }

    result = {}
    for code in reason_codes:
        # Extract floor prefix (e.g., "F1" from "F1_Amanah")
        floor_key = code.split("_")[0] if "_" in code else code
        if floor_key in policy_refs:
            result[code] = policy_refs[floor_key]

    return result
