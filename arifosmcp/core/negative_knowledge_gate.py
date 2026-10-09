"""
arifOS core — NEGATIVE_KNOWLEDGE Gate (Computational VOID_t)
═══════════════════════════════════════════════════════════════

Enforces the NEGATIVE_KNOWLEDGE boundary. If an agent or caller attempts
to assert an unmeasured scalar or absent witness as an established fact
without empirical provenance, the claim is rejected into VOID_t and
downgraded from action-eligible status.

    VOID_t = { claims the institution cannot presently justify }

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import re
from typing import Any

CANONICAL_UNMEASURED_SCALARS: tuple[str, ...] = ("G", "C_dark", "W3", "kappa_r")


def evaluate_negative_knowledge(
    claim_text: str | None,
    declared_class: str | None = None,
    *,
    evidence: dict[str, Any] | None = None,
    unmeasured_scalars: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate whether a claim attempts to assert unmeasured reality as fact.

    Returns a dict with:
      - passed: bool
      - violations: list of violation dicts
      - void_entry: VOID_t record if rejected, else None
      - downgraded_class: downgraded class (e.g. UNCLASSIFIED) if violated
      - allowed_for_mutation: False if unmeasured scalar asserted as fact
      - reasons: list of human-readable justifications
    """
    scalars = list(unmeasured_scalars) if unmeasured_scalars else list(CANONICAL_UNMEASURED_SCALARS)
    text = str(claim_text or "")
    dec_class = str(declared_class or "").upper().strip()

    violations: list[dict[str, str]] = []

    for s in scalars:
        # Match pattern like "G=0.9", "G is 0.9", "G is measured at 0.9", "G: 0.9", "W3 = 0.8"
        pattern = rf"\b{re.escape(s)}\b(?:\s+(?:is|measured\s+at|equals?|value(?:\s+is)?))*\s*[:=]?\s*([0-9.]+)"
        if re.search(pattern, text, re.IGNORECASE):
            # Check if evidence provides verified sensor measurement
            has_sensor = False
            if isinstance(evidence, dict):
                scalar_ev = evidence.get("scalars") or evidence.get("scalar_snapshot") or {}
                if isinstance(scalar_ev, dict):
                    val = scalar_ev.get(s)
                    if isinstance(val, dict) and val.get("status") == "MEASURED":
                        has_sensor = True
            if not has_sensor:
                violations.append({
                    "scalar": s,
                    "reason": f"NEGATIVE_KNOWLEDGE: scalar '{s}' is unmeasured in active session; assertion of value lacks empirical sensor provenance.",
                })

    if violations:
        void_entry = {
            "claim": text[:300],
            "unjustified_scalars": [v["scalar"] for v in violations],
            "verdict": "VOID_t",
            "downgraded_from": dec_class or "MEASURED",
            "downgraded_to": "UNCLASSIFIED",
        }
        return {
            "gate": "negative_knowledge_gate/v1",
            "passed": False,
            "violations": violations,
            "void_entry": void_entry,
            "downgraded_class": "UNCLASSIFIED",
            "allowed_for_mutation": False,
            "reasons": [v["reason"] for v in violations],
        }

    return {
        "gate": "negative_knowledge_gate/v1",
        "passed": True,
        "violations": [],
        "void_entry": None,
        "downgraded_class": declared_class or "UNCLASSIFIED",
        "allowed_for_mutation": True,
        "reasons": [],
    }
