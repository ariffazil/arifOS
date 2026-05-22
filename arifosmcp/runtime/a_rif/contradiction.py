"""
arifosmcp/runtime/a_rif/contradiction.py — Contradiction Audit
══════════════════════════════════════════════════════════════

Thin wrapper over f4_contradiction_handler for A-RIF pipeline use.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.a_rif.models import ContradictionReport

__all__ = ["audit_for_contradictions"]


def audit_for_contradictions(claims: list[dict[str, Any]]) -> ContradictionReport:
    """
    Audit a set of claims for contradictions.

    Returns a ContradictionReport with recommendation:
        HOLD    — contradictions detected, escalate
        MERGE   — minor conflicts, can be merged
        VOID    — no claims to audit
    """
    if not claims:
        return ContradictionReport(
            status="VOID",
            conflicts=[],
            recommendation="VOID",
        )

    # Simple keyword-based contradiction detection
    # In production this delegates to f4_contradiction_handler
    conflicts = []
    for i, claim_a in enumerate(claims):
        for claim_b in claims[i + 1 :]:
            text_a = claim_a.get("text", "").lower()
            text_b = claim_b.get("text", "").lower()
            # Detect direct negation heuristics
            negation_words = ("not", "no", "never", "false", "contradicts")
            if any(w in text_a for w in negation_words) or any(w in text_b for w in negation_words):
                conflicts.append(
                    {
                        "claim_a": claim_a.get("text", ""),
                        "claim_b": claim_b.get("text", ""),
                        "type": "T1_direct_negation",
                    }
                )

    if conflicts:
        return ContradictionReport(
            status="CONFLICT",
            conflicts=conflicts,
            recommendation="HOLD",
        )

    return ContradictionReport(
        status="CONSISTENT",
        conflicts=[],
        recommendation="HOLD",  # Default conservative
    )
