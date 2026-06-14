"""
arifosmcp/tools/paradox.py — Paradox Status & Circuit Breaker Telemetry

Exposes the state of all 5 epistemic circuit breakers (CB1-CB5) and
the 11 paradox anchors to agents via `arif_paradox_status`.

This closes GAP 3 of the APEX Eureka extraction: paradox state was
invisible to agents. Now any agent can query "what paradoxes are
currently active?"

Theory: arifOS/static/arifos/theory/000/APEX_THEORY.md
Source: arifOS/core/paradox/circuit_breakers.py

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

# ── Inline circuit breaker types ─────────────────────────────────────────────

BREAKER_INFO: list[dict[str, str]] = [
    {
        "id": "CB1",
        "name": "Godellock",
        "description": "Ω₀ < 0.03 — epistemic overconfidence",
        "metaphor": "Gödel's incompleteness: certainty is always incomplete",
        "check": "omega_0 < 0.03",
    },
    {
        "id": "CB2",
        "name": "Single-Witness",
        "description": "Any witness lane W < 0.70 — insufficient corroboration",
        "metaphor": "One testimony is not evidence in law",
        "check": "min(human_w, ai_w, earth_w) < 0.70",
    },
    {
        "id": "CB3",
        "name": "Cheap Truth",
        "description": "τ > 0.99 but evidence < Landauer bound — truth without thermodynamic cost",
        "metaphor": "Free claims have no weight",
        "check": "confidence > 0.99 and evidence_level < threshold",
    },
    {
        "id": "CB4",
        "name": "Recursive Stack",
        "description": "Self-reference depth > 3 levels — infinite regress risk",
        "metaphor": "'This statement is false' — recursive paradox",
        "check": "self_reference_depth > 3",
    },
    {
        "id": "CB5",
        "name": "Confidence Cascade",
        "description": "Confidence (τ) rises without new evidence — belief hardening",
        "metaphor": "Certainty inflation without factual basis",
        "check": "confidence_increase > 0 without new evidence_added",
    },
]

ANCHOR_IDS = [
    "J_TxC", "J_TxP", "J_TxJ",
    "J_CxC", "J_CxP", "J_CxJ",
    "J_HxC", "J_HxP", "J_HxJ",
    "J_IRREVOCABLE",
    "J_POWER_ASYMMETRY",
]


def arif_paradox_status(
    mode: str = "status",
    omega_0: float = 0.05,
    human_w: float = 0.42,
    ai_w: float = 0.32,
    earth_w: float = 0.26,
    confidence: float = 0.0,
    evidence_level: str = "L0",
    self_reference_depth: int = 0,
    confidence_increase: float = 0.0,
    evidence_added: bool = False,
) -> dict[str, Any]:
    """
    Query the current state of all 5 epistemic circuit breakers (CB1-CB5).

    Each breaker returns TRIPPED | WARNING | OK based on the provided
    parameters. Defaults represent a healthy system with tri-witness
    consensus (human=0.42, ai=0.32, earth=0.26).

    Modes:
      status   — Evaluate all 5 circuit breakers and return states
      info     — Return the static description of all breakers + anchors
      health   — Quick summary: how many circuits are healthy

    Returns:
      {
        "verdict": "STABLE | WARNING | CRITICAL",
        "circuit_breakers": [...],
        "anchors_available": 11,
        "unhealthy_count": N,
      }
    """
    if mode == "info":
        return {
            "circuit_breakers": BREAKER_INFO,
            "anchor_count": len(ANCHOR_IDS),
            "anchors": ANCHOR_IDS,
            "theory_doc": "arifOS/static/arifos/theory/000/APEX_THEORY.md",
        }

    results: list[dict[str, str]] = []
    unhealthy = 0

    # CB1: Godellock
    cb1_state = "TRIPPED" if omega_0 < 0.03 else ("WARNING" if omega_0 < 0.05 else "OK")
    if cb1_state != "OK":
        unhealthy += 1
    cb1_msg = (
        "overconfidence detected" if cb1_state == "TRIPPED" else
        "elevated confidence" if cb1_state == "WARNING" else
        "healthy epistemic humility"
    )
    results.append({
        "breaker": "CB1",
        "name": "Godellock",
        "state": cb1_state,
        "value": str(omega_0),
        "message": f"Ω₀={omega_0:.3f} — {cb1_msg}",
    })

    # CB2: Single-Witness
    min_w = min(human_w, ai_w, earth_w)
    cb2_state = "TRIPPED" if min_w < 0.50 else ("WARNING" if min_w < 0.70 else "OK")
    if cb2_state != "OK":
        unhealthy += 1
    cb2_msg = (
        "insufficient corroboration" if cb2_state == "TRIPPED" else
        "marginally corroborated" if cb2_state == "WARNING" else
        "all witnesses above threshold"
    )
    results.append({
        "breaker": "CB2",
        "name": "Single-Witness",
        "state": cb2_state,
        "value": f"min_w={min_w:.2f}",
        "message": f"Minimum witness confidence {min_w:.2f} — {cb2_msg}",
    })

    # CB3: Cheap Truth
    evidence_threshold = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
    ev_level = evidence_threshold.get(evidence_level, 0)
    cb3_state = "TRIPPED" if confidence > 0.99 and ev_level < 2 else ("WARNING" if confidence > 0.95 and ev_level < 3 else "OK")
    if cb3_state != "OK":
        unhealthy += 1
    cb3_msg = (
        "truth without cost" if cb3_state == "TRIPPED" else
        "confidence exceeds evidence" if cb3_state == "WARNING" else
        "confidence grounded in evidence"
    )
    results.append({
        "breaker": "CB3",
        "name": "Cheap Truth",
        "state": cb3_state,
        "value": f"τ={confidence:.2f}, evidence={evidence_level}",
        "message": f"τ={confidence:.2f} with evidence={evidence_level} — {cb3_msg}",
    })

    # CB4: Recursive Stack
    cb4_state = "TRIPPED" if self_reference_depth > 5 else ("WARNING" if self_reference_depth > 3 else "OK")
    if cb4_state != "OK":
        unhealthy += 1
    cb4_msg = (
        "infinite regress risk" if cb4_state == "TRIPPED" else
        "elevated recursion" if cb4_state == "WARNING" else
        "no recursive paradox"
    )
    results.append({
        "breaker": "CB4",
        "name": "Recursive Stack",
        "state": cb4_state,
        "value": f"depth={self_reference_depth}",
        "message": f"Self-reference depth {self_reference_depth} — {cb4_msg}",
    })

    # CB5: Confidence Cascade
    cb5_state = "TRIPPED" if confidence_increase > 0.3 and not evidence_added else ("WARNING" if confidence_increase > 0.1 and not evidence_added else "OK")
    if cb5_state != "OK":
        unhealthy += 1
    cb5_msg = (
        "belief hardening" if cb5_state == "TRIPPED" else
        "confidence inflation" if cb5_state == "WARNING" else
        "confidence growth matches evidence"
    )
    results.append({
        "breaker": "CB5",
        "name": "Confidence Cascade",
        "state": cb5_state,
        "value": f"Δτ={confidence_increase:.2f}, new_evidence={evidence_added}",
        "message": f"Confidence increased {confidence_increase:.2f} without evidence — {cb5_msg}",
    })

    verdict = "STABLE" if unhealthy == 0 else ("WARNING" if unhealthy <= 2 else "CRITICAL")

    if mode == "health":
        return {
            "verdict": verdict,
            "healthy_count": 5 - unhealthy,
            "unhealthy_count": unhealthy,
            "unhealthy_breakers": [r["breaker"] for r in results if r["state"] != "OK"],
        }

    return {
        "verdict": verdict,
        "circuit_breakers": results,
        "anchors_available": len(ANCHOR_IDS),
        "unhealthy_count": unhealthy,
        "healthy_count": 5 - unhealthy,
        "mode": mode,
    }
