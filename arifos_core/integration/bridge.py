"""
Bridge adapter to expose arifOS v45Ω law engine to external clients (aCLIP).

This module serves as the primary integration point for:
- arifos_clip (aCLIP)
- External CI/CD tools
- Audit systems

It translates external session data into internal Metrics and requests
a verdict from the APEX PRIME Judiciary.
"""

from typing import Dict, Any
from arifos_core.system.apex_prime import apex_review, ApexVerdict
from arifos_core.enforcement.metrics import Metrics


def evaluate_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a session against the arifOS v45Ω Constitutional Floors.

    Args:
        session_data: Dictionary containing session context, metrics, and content.
                      Expected structure:
                      {
                          "metrics": { ... },     # Raw floor values
                          "purpose": str,         # User intent/query
                          "content": str,         # Draft content/response
                          "high_stakes": bool,    # Risk classification
                          "metadata": { ... }     # Extra context
                      }

    Returns:
        Dict with keys:
        - verdict: str (SEAL, VOID, PARTIAL, SABAR, 888_HOLD)
        - reason: str
        - details: dict (pulse, floors, etc.)
    """
    # 1. Extract Metrics
    raw_metrics = session_data.get("metrics", {})

    # Construct Safe Defaults if missing (Fail-Closed logic handled by Apex if values low)
    # We default to "safe" values ONLY if the client didn't provide them,
    # assuming the client has pre-validated or this is a raw check.
    # However, for TRUTH, we default to 0.0 (Fail) if missing to prevent Blind Seal.

    metrics_obj = Metrics(
        truth=raw_metrics.get("truth", 0.0),  # Default to FAIL (F2)
        delta_s=raw_metrics.get("delta_s", 0.0),  # Default to Neutral (F4)
        peace_squared=raw_metrics.get("peace_squared", 1.0),
        kappa_r=raw_metrics.get("kappa_r", 0.95),
        omega_0=raw_metrics.get("omega_0", 0.04),  # Perfect humility
        amanah=raw_metrics.get("amanah", True),
        tri_witness=raw_metrics.get("tri_witness", 0.0),
        rasa=raw_metrics.get("rasa", True),
        anti_hantu=raw_metrics.get("anti_hantu", True),
        # Pass through extended metrics if present
        ambiguity=raw_metrics.get("ambiguity"),
        drift_delta=raw_metrics.get("drift_delta"),
        paradox_load=raw_metrics.get("paradox_load"),
    )

    # 2. Extract Context
    purpose = session_data.get("purpose", "")
    content = session_data.get("content", "")
    high_stakes = session_data.get("high_stakes", False)

    # 3. Call Apex Prime Judiciary
    verdict: ApexVerdict = apex_review(
        metrics=metrics_obj, high_stakes=high_stakes, prompt=purpose, response_text=content
    )

    # 4. Format Output for Client
    return {
        "verdict": verdict.verdict.value,
        "reason": verdict.reason,
        "details": {
            "pulse": verdict.pulse,
            "floors": verdict.floors.__dict__ if verdict.floors else {},
            "genius": {"g": verdict.genius_index, "c_dark": verdict.dark_cleverness},
        },
    }
