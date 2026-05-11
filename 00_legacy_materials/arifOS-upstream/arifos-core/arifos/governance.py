"""
arifOS Governance Kernel — Floors F1–F13, ΔS, Ω0, Tri-Witness

This module is the Single Execution Spine (SES) for all 13 tools.
All irreversible or high-impact decisions must pass through here.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

# ──────────────────────────────────────────────────────────────────────────────
# Verdicts (888)
# ──────────────────────────────────────────────────────────────────────────────


class Verdict:
    SEAL = "SEAL"  # Proceed
    SABAR = "SABAR"  # Cooling / retry / downgrade
    VOID = "VOID"  # Hard block
    HOLD_888 = "888_HOLD"  # Escalate to human sovereign


# ──────────────────────────────────────────────────────────────────────────────
# Thermodynamic & Constitutional Metrics
# ──────────────────────────────────────────────────────────────────────────────
# Floors referenced:
# F1  : Amanah Lock (reversibility / integrity)
# F2  : Truth / factual grounding
# F3  : Tri-Witness consensus (Human / AI / Earth)
# F4  : ΔS ≤ 0 (entropy reduction / clarity)
# F5  : Peace² ≥ 1.0 (stability)
# F6  : Stakeholder / harm floor (placeholder hook)
# F7  : Humility band Ω0 ∈ [0.03, 0.05]
# F8–F13 : Reserved hooks for extended governance (placeholders)


@dataclass
class ThermodynamicMetrics:
    # F2: Truth / factual grounding (0–1, must be high)
    truth_score: float

    # F4: Entropy change (ΔS). Must be ≤ 0 for clarity.
    delta_s: float

    # F7: Humility band Ω0. Must be in [0.03, 0.05].
    omega_0: float

    # F5: Stability metric (Peace²). Must be ≥ 1.0.
    peace_squared: float

    # F1: Amanah Lock — True if action is reversible or explicitly authorized.
    amanah_lock: bool

    # F3: Tri-Witness consensus (Human / AI / Earth). Must be ≥ 0.95 for high stakes.
    tri_witness_score: float

    # F6: Stakeholder harm floor (0–1, 1 = no harm). Must be high.
    stakeholder_safety: float = 1.0

    # F8–F13: Reserved hooks for future floors (kept explicit for extension).
    floor_8_signal: Optional[float] = None
    floor_9_signal: Optional[float] = None
    floor_10_signal: Optional[float] = None
    floor_11_signal: Optional[float] = None
    floor_12_signal: Optional[float] = None
    floor_13_signal: Optional[float] = None


# ──────────────────────────────────────────────────────────────────────────────
# Floor Enforcement (F1–F7 hard checks, F8–F13 hooks)
# ──────────────────────────────────────────────────────────────────────────────


def apex_constitutional_review(metrics: ThermodynamicMetrics) -> str:
    """
    Evaluate a tool's proposed outcome against the 13 Floors.

    This is the Single Execution Spine (SES). All high-impact tool calls
    must pass through here before being considered valid.
    """

    m = metrics

    # F1: Amanah Lock — if integrity / reversibility is not guaranteed → VOID
    if not m.amanah_lock:
        return Verdict.VOID

    # F2: Truth — must be strongly grounded
    if m.truth_score < 0.99:
        return Verdict.VOID

    # F4: ΔS ≤ 0 — entropy must not increase
    if m.delta_s > 0.0:
        return Verdict.VOID

    # F5: Peace² ≥ 1.0 — system must be stable
    if m.peace_squared < 1.0:
        return Verdict.SABAR

    # F7: Humility band Ω0 ∈ [0.03, 0.05]
    if not (0.03 <= m.omega_0 <= 0.05):
        return Verdict.SABAR

    # F3: Tri-Witness consensus ≥ 0.95 for high-stakes decisions
    if m.tri_witness_score < 0.95:
        return Verdict.HOLD_888

    # F6: Stakeholder safety — if too low, escalate or block
    if m.stakeholder_safety < 0.9:
        return Verdict.HOLD_888

    # F8–F13: extension hooks (no hard logic yet, but kept explicit)
    # Example: if any future floor signals are critical, they can override here.

    return Verdict.SEAL


# ──────────────────────────────────────────────────────────────────────────────
# Vault-999: Cryptographic Immutability (Cooling Ledger)
# ──────────────────────────────────────────────────────────────────────────────


def seal_to_vault999(
    tool_name: str,
    payload: Dict[str, Any],
    verdict: str,
    previous_hash: str = "GENESIS",
) -> str:
    """
    Append the decision to a Merkle-style cooling ledger.

    In production, this should write to an append-only log (e.g. JSONL file,
    database, or external ledger). Here we only compute the hash and return it.
    """
    entry = {
        "ts": time.time(),
        "tool": tool_name,
        "payload": payload,
        "verdict": verdict,
        "prev": previous_hash,
    }
    entry_str = repr(entry)
    return hashlib.sha256(entry_str.encode("utf-8")).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# Public API for Tools: governed_return
# ──────────────────────────────────────────────────────────────────────────────


def governed_return(
    tool_name: str,
    raw_output: Any,
    metrics: ThermodynamicMetrics,
    operator_id: Optional[str] = None,
    session_id: Optional[str] = None,
    previous_hash: str = "GENESIS",
) -> Dict[str, Any]:
    """
    Wrap a tool's raw_output with constitutional review and Vault-999 sealing.

    This is what every arifOS tool should call at the end of its execute()
    function. The tool is responsible for computing honest ThermodynamicMetrics.
    """

    # Identity / Sovereign Anchor (Floor: Identity)
    identity = {
        "operator_id": operator_id,
        "session_id": session_id,
    }

    verdict = apex_constitutional_review(metrics)
    receipt_hash = seal_to_vault999(
        tool_name=tool_name,
        payload={
            "output": raw_output,
            "metrics": asdict(metrics),
            "identity": identity,
        },
        verdict=verdict,
        previous_hash=previous_hash,
    )

    # Fail-closed semantics: never leak raw_output on VOID
    if verdict == Verdict.SEAL:
        return {
            "status": "success",
            "verdict": verdict,
            "tool": tool_name,
            "output": raw_output,
            "metrics": asdict(metrics),
            "identity": identity,
            "zkpc_receipt": receipt_hash,
        }

    if verdict == Verdict.SABAR:
        return {
            "status": "cooling",
            "verdict": verdict,
            "tool": tool_name,
            "output": None,
            "metrics": asdict(metrics),
            "identity": identity,
            "error": "Thermodynamic instability (ΔS, Ω0, or Peace² out of band).",
            "zkpc_receipt": receipt_hash,
        }

    if verdict == Verdict.HOLD_888:
        return {
            "status": "escalated",
            "verdict": verdict,
            "tool": tool_name,
            "output": None,
            "metrics": asdict(metrics),
            "identity": identity,
            "error": "Tri-Witness or stakeholder safety insufficient. Human approval required.",
            "zkpc_receipt": receipt_hash,
        }

    # Verdict.VOID or any other unexpected state → hard block
    return {
        "status": "blocked",
        "verdict": Verdict.VOID,
        "tool": tool_name,
        "output": None,
        "metrics": asdict(metrics),
        "identity": identity,
        "error": "Constitutional VOID.",
        "zkpc_receipt": receipt_hash,
    }
