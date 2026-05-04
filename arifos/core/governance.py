"""
arifOS Governance Kernel — Floors F1–F13, ΔS, Ω0, Tri-Witness

DITEMPA BUKAN DIBERI — Forged, Not Given

SEAL authority is centralized in 888_judge only.
No tool may emit SEAL without 888_judge ratification.
"""

from __future__ import annotations
import hashlib
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from arifos.core.middleware.invariant_enforcement import enforce_invariants
except ImportError:
    enforce_invariants = None  # type: ignore


# ──────────────────────────────────────────────────────────────────────────────
# Constitutional Constants
# ──────────────────────────────────────────────────────────────────────────────

PEACE_SQUARED_FLOOR = 0.80  # F5 cooling floor — below this triggers SABAR
TRI_WITNESS_PARTIAL = 0.33  # One-witness score when Earth/AI bridge fails
TRI_WITNESS_THRESHOLD = 0.95  # High-stakes consensus requirement
STAKEHOLDER_SAFETY_FLOOR = 0.90  # F6 hard floor
F4_ENTROPY_TOLERANCE = 0.02  # Allow small positive ΔS for honest failure recording


# ──────────────────────────────────────────────────────────────────────────────
# Verdicts (888)
# ──────────────────────────────────────────────────────────────────────────────


class Verdict:
    CLAIM_ONLY = "CLAIM_ONLY"  # Tool claims success; guard/invariants must ratify
    PARTIAL = "PARTIAL"  # Proceed with remediation noted
    SABAR = "SABAR"  # Cooling / retry / downgrade
    VOID = "VOID"  # Hard block
    HOLD_888 = "888_HOLD"  # Escalate to human sovereign
    SEAL = "SEAL"  # 888_JUDGE only — do not use elsewhere


# ──────────────────────────────────────────────────────────────────────────────
# Thermodynamic & Constitutional Metrics
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ThermodynamicMetrics:
    truth_score: float  # F2: Truth / factual grounding (0–1, must be high)
    delta_s: float  # F4: Entropy change (ΔS). Must be ≤ 0 for clarity.
    omega_0: float  # F7: Humility band Ω0. Must be in [0.03, 0.05].
    peace_squared: float  # F5: Stability metric (Peace²). Must be ≥ 1.0.
    amanah_lock: bool  # F1: Amanah Lock — True if action is reversible.
    tri_witness_score: float  # F3: Tri-Witness consensus (Human / AI / Earth).
    stakeholder_safety: float = 1.0  # F6: Stakeholder harm floor (0–1, 1 = no harm).
    floor_8_signal: Union[str, float, None] = "not_evaluated"
    floor_9_signal: Union[str, float, None] = "not_evaluated"
    floor_10_signal: Union[str, float, None] = "not_evaluated"
    floor_11_signal: Union[str, float, None] = "not_evaluated"
    floor_12_signal: Union[str, float, None] = "not_evaluated"
    floor_13_signal: Union[str, float, None] = "not_evaluated"


# ──────────────────────────────────────────────────────────────────────────────
# Vault-999: Cryptographic Immutability (Cooling Ledger)
# ──────────────────────────────────────────────────────────────────────────────


def _default_vault999_ledger_path() -> str:
    repo_root = Path(os.getenv("ARIFOS_WORKDIR", Path(__file__).resolve().parents[2]))
    return str(repo_root / "VAULT999" / "SEALED_EVENTS.jsonl")


VAULT999_LEDGER_PATH = os.getenv("ARIFOS_VAULT999_LEDGER", _default_vault999_ledger_path())


def seal_to_vault999(
    tool_name: str, payload: Dict[str, Any], verdict: str, previous_hash: str = "GENESIS"
) -> str:
    entry = {
        "ts": time.time(),
        "tool": tool_name,
        "payload": payload,
        "verdict": verdict,
        "prev": previous_hash,
    }
    entry_str = repr(entry)
    return hashlib.sha256(entry_str.encode("utf-8")).hexdigest()


def append_vault999_event(
    event_type: str,
    payload: Dict[str, Any],
    operator_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    ledger_path = VAULT999_LEDGER_PATH
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)

    previous_hash = "GENESIS"
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, "r", encoding="utf-8") as fh:
                lines = [ln.strip() for ln in fh if ln.strip()]
                if lines:
                    last = json.loads(lines[-1])
                    previous_hash = last.get("chain_hash", last.get("merkle_leaf", "GENESIS"))
        except Exception:
            previous_hash = "GENESIS"

    entry = {
        "ts": time.time(),
        "event_type": event_type,
        "operator_id": operator_id,
        "session_id": session_id,
        "payload": payload,
        "prev_hash": previous_hash,
    }
    entry_str = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    merkle_leaf = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
    chain_hash = hashlib.sha256(f"{previous_hash}:{merkle_leaf}".encode("utf-8")).hexdigest()

    record = {
        **entry,
        "merkle_leaf": merkle_leaf,
        "chain_hash": chain_hash,
    }

    with open(ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    return chain_hash


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

    IMPORTANT: This returns CLAIM_ONLY verdict.
    SEAL authority is exclusively held by 888_judge.
    The constitutional_guard and invariant_enforcement middleware
    will upgrade/downgrade this verdict on the server side.
    """

    identity = {
        "operator_id": operator_id,
        "session_id": session_id,
    }

    invariant_failures: List[str] = []
    if isinstance(raw_output, dict) and enforce_invariants is not None:
        try:
            enriched_output = enforce_invariants(tool_name, raw_output)
            if isinstance(enriched_output, dict):
                raw_output = enriched_output
                failures = enriched_output.get("invariant_failures", [])
                invariant_failures = failures if isinstance(failures, list) else []
            elif isinstance(enriched_output, list):
                invariant_failures = enriched_output
        except Exception:
            invariant_failures = []

    verdict = Verdict.CLAIM_ONLY

    if invariant_failures:
        verdict = Verdict.PARTIAL

    receipt_hash = seal_to_vault999(
        tool_name=tool_name,
        payload={"output": raw_output, "metrics": asdict(metrics), "identity": identity},
        verdict=verdict,
        previous_hash=previous_hash,
    )

    # Include zkpc_receipt in metrics so constitutional_guard's _extract_metrics
    # (which scans nested dicts, not envelope top-level) can find it for F11 AUTH.
    metrics_dict = asdict(metrics)
    metrics_dict["zkpc_receipt"] = receipt_hash

    envelope: Dict[str, Any] = {
        "status": "success",
        "verdict": verdict,
        "tool": tool_name,
        "output": raw_output if verdict in (Verdict.CLAIM_ONLY, Verdict.PARTIAL) else None,
        "raw_output": raw_output,
        "metrics": metrics_dict,
        "identity": identity,
        "zkpc_receipt": receipt_hash,
        "invariant_failures": invariant_failures,
    }

    if verdict == Verdict.CLAIM_ONLY:
        return envelope

    if verdict == Verdict.PARTIAL:
        envelope["status"] = "partial"
        actual_failures = (
            raw_output.get("invariant_failures", []) if isinstance(raw_output, dict) else []
        )
        if actual_failures:
            envelope["error"] = "AGI invariants failed: " + ", ".join(
                str(f) for f in actual_failures
            )
        return envelope

    envelope["status"] = "blocked"
    envelope["verdict"] = Verdict.VOID
    envelope["error"] = "Constitutional VOID."
    return envelope
