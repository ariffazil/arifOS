"""
F1–F13 → constraint mapping for the minda substrate.

This is the doctrinal layer (cold path) for how constitutional floors
become concrete checks on MindProposals. It is informational in v0.1 —
the actual checks are inline in service.py and utility.py. The mapping
exists so future versions can drive the constraint engine from this table.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FConstraint:
    """One floor → check mapping.

    Attributes:
        floor:  F1, F2, ..., F13
        name:   AMANAH, TRUTH, ...
        check:  human-readable description of how the floor becomes a check
        hard:   if True, violation → -inf utility (or BLOCK); if False, soft penalty
    """

    floor: str
    name: str
    check: str
    hard: bool


# Canonical F1-F13 mapping to minda checks.
# v0.1 implements F1, F2, F6, F13 inline. The rest are documented for
# future versions.
F_CONSTRAINTS: list[FConstraint] = [
    FConstraint("F1", "AMANAH", "reversibility — irreversible plans trigger 888_HOLD", True),
    FConstraint(
        "F2", "TRUTH", "confidence ≥ 0.99 for CLAIM, else PLAUSIBLE / ESTIMATE / HYPOTHESIS", True
    ),
    FConstraint("F3", "WITNESS", "intent + plan + outcome aligned (logged to VAULT)", True),
    FConstraint("F4", "CLARITY", "ΔS ≤ 0 — reduce confusion, don't add it", True),
    FConstraint("F5", "PEACE", "peace² ≥ 1.0 — de-escalate, don't escalate", True),
    FConstraint("F6", "EMPATHY", "maruah ≥ 0.4 — dignity floor; below → -inf utility", True),
    FConstraint(
        "F7", "HUMILITY", "confidence ≤ 0.99 — no fake certainty (cap in BeliefEngine)", True
    ),
    FConstraint(
        "F8", "GENIUS", "long-term intelligence preserved (no destructive shortcuts)", True
    ),
    FConstraint("F9", "ANTIHANTU", "no consciousness claims — this is a TOOL, not a mind", True),
    FConstraint(
        "F10", "ONTOLOGY", "AI-only ontology — no soul/feelings/consciousness in plan", True
    ),
    FConstraint("F11", "AUTH", "caller identity verified before advisory (gated upstream)", True),
    FConstraint(
        "F12", "INJECTION", "input sanitized (5× patterns checked upstream by arif_observe)", True
    ),
    FConstraint(
        "F13", "SOVEREIGN", "human veto is absolute; 888_HOLD gates all irreversible", True
    ),
]
