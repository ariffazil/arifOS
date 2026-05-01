"""
arifos/geox/governance/indices.py — Operational Governance Indices

Codifies the 'Fast, Cheap, Safe' trilemma into computable metrics
based on arifOS mechanical constraints (Tokens, Latency, Energy).
"""

from typing import Any


def calculate_indices(kernel_state: dict[str, Any]) -> dict[str, float]:
    """
    Computes the Governance Grammar indices from raw arifOS telemetry.

    Args:
        kernel_state: The dict returned by GovernanceKernel.get_current_state()

    Returns:
        {
            "pay_index": 0.0-1.0,
            "wait_index": 0.0-1.0,
            "no_risk_threshold": 0.0-1.0,
            "apex_readiness": 0.0-1.0
        }
    """
    telemetry = kernel_state.get("telemetry", {})
    witness = kernel_state.get("witness", {})

    # Raw inputs
    omega = telemetry.get("uncertainty_score", 0.0)
    reversibility = telemetry.get("peace2", 1.0)
    current_energy = telemetry.get("psi_le", 1.0)
    genius = telemetry.get("confidence", 0.0)
    stability = telemetry.get("temporal_stability", 1.0)
    shadow = witness.get("shadow", 0.0)

    # 1. Pay Index: Spend capital when irreversibility is low and budget exists
    pay_index = (reversibility) * (current_energy)

    # 2. Wait Index: Wait when uncertainty is high but metabolic flux isn't maxed
    wait_index = omega * (1.0 - min(1.0, telemetry.get("metabolic_flux", 0.0) / 1000.0))

    # 3. No-Risk Threshold: The limit of the 'Forbidden Zone'
    no_risk_threshold = 1.0 - ((1.0 - reversibility) * 0.7 + shadow * 0.3)

    # 4. Apex Readiness: Composite of confidence and temporal grounding
    apex_readiness = genius * stability

    return {
        "pay_index": round(max(0.0, min(1.0, pay_index)), 4),
        "wait_index": round(max(0.0, min(1.0, wait_index)), 4),
        "no_risk_threshold": round(max(0.0, min(1.0, no_risk_threshold)), 4),
        "apex_readiness": round(max(0.0, min(1.0, apex_readiness)), 4),
    }

def get_verdict_advice(indices: dict[str, float]) -> str:
    """Provides qualitative advice based on indices."""
    if indices["apex_readiness"] > 0.9:
        return "APEX_READY: Proceed with full autonomy."

    if indices["pay_index"] > 0.8 and indices["wait_index"] < 0.3:
        return "SOVEREIGN_FAST: Safe to spend budget for speed."

    if indices["wait_index"] > 0.6:
        return "ANCESTRAL_SAFE: Holding for more information recommended."

    if indices["no_risk_threshold"] < 0.4:
        return "HAZARD_DETECTED: Critical irreversibility. 888_HOLD enforced."

    return "STABLE: Standard operational parameters."
