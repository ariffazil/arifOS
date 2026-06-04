"""
arifosmcp/runtime/metabolic_receipt.py — Aggregate Intention Accounting
═══════════════════════════════════════════════════════════════════════

Implements Gap 2: Metabolic Receipt System.
Tracks cumulative risk, files touched, and objectives across a session
to prevent split-action bypass (Metabolic Bypass).

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class MetabolicReceipt:
    receipt_id: str
    actor_id: str
    session_id: str
    trace_id: str
    objective_hash: str
    target_subsystem: str
    files_touched: list[str] = field(default_factory=list)
    tools_called: list[str] = field(default_factory=list)
    risk_delta: float = 0.0
    entropy_delta: float = 0.0
    reversibility: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# In-memory aggregate store
_AGGREGATE_RECEIPTS: dict[str, list[MetabolicReceipt]] = {}


def create_receipt(
    actor_id: str,
    session_id: str,
    objective: str,
    action_payload: dict[str, Any],
    risk_score: float,
    reversibility: str,
) -> MetabolicReceipt:
    import hashlib

    obj_hash = hashlib.sha256(objective.encode()).hexdigest()[:16]

    receipt = MetabolicReceipt(
        receipt_id=f"REC-{uuid.uuid4().hex[:8]}",
        actor_id=actor_id,
        session_id=session_id,
        trace_id=uuid.uuid4().hex,
        objective_hash=obj_hash,
        target_subsystem=action_payload.get("subsystem", "unknown"),
        files_touched=action_payload.get("files", []),
        tools_called=[action_payload.get("tool", "unknown")],
        risk_delta=risk_score,
        reversibility=reversibility,
    )

    if session_id not in _AGGREGATE_RECEIPTS:
        _AGGREGATE_RECEIPTS[session_id] = []
    _AGGREGATE_RECEIPTS[session_id].append(receipt)

    return receipt


def get_cumulative_metrics(session_id: str, window_minutes: int = 60) -> dict[str, Any]:
    """
    Gap 3.4 Invariant: Judge the operation, not only the step.
    Calculates cumulative risk and entropy across the session.
    """
    receipts = _AGGREGATE_RECEIPTS.get(session_id, [])
    if not receipts:
        return {"cumulative_risk": 0.0, "total_files": 0, "objectives_count": 0}

    total_risk = sum(r.risk_delta for r in receipts)
    unique_files = set()
    unique_objectives = set()
    for r in receipts:
        unique_files.update(r.files_touched)
        unique_objectives.add(r.objective_hash)

    return {
        "cumulative_risk": round(total_risk, 3),
        "total_files_touched": len(unique_files),
        "objectives_count": len(unique_objectives),
        "is_bypass_attempt": total_risk > 5.0 or len(unique_files) > 20,
    }
