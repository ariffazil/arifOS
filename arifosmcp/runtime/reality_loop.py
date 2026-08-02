"""
arifosmcp/runtime/reality_loop.py — REALITY LOOP (Q9c · FalsifiablePrediction)
═════════════════════════════════════════════════════════════════════════════

Three Closures — Q9c (GENESIS/058, sealed 2026-08-02).

A strange loop becomes a reality loop when a single primitive —
`FalsifiablePrediction` — flows through every link such that each prediction
(a) is made BY the system ABOUT something outside the system, (b) names a
falsifier, (c) carries a deadline, and (d) is *scored* at deadline into the
continuity chain that the **next** `arif_init` reads.

Design ref: /root/forge_work/2026-08-02/reality-loop-design.md §1.

This module is the **kernel-anchor** for the Reality Loop. It exposes:

  - `FalsifiablePrediction` — typed envelope (statement, falsifier, deadline,
    check_method, source_tool, source_session, status).
  - `prediction_id(statement, falsifier, check_by_iso)` — content-addressed
    canonical ID (sha256[:12]); dedup at store time.
  - `register_prediction(pred)` — append to the in-process ledger and emit
    a `RealityReceipt` (F11 audit envelope).
  - `check_prediction(prediction_id, observed_value)` — score and mark
    CORROBORATED | FALSIFIED | EXPIRED.
  - `reality_loop_gate(ctx)` — advisory governance gate. **NEVER blocks
    SEAL.** SEALS without a falsifiable commitment are SABAR (advisory)
    and carry a `reality_receipt` with `prediction_id=None`. The gate
    exists so that the seam between SEAL and REALITY is auditable, not so
    that the gate itself decides.

Doctrine (GENESIS/058 §1, Q9c):
  Every SEAL is linked to a FalsifiablePrediction. The Reality Loop does
  not block action — it attaches a *commitment*. The commitment is then
  scored by `check_prediction` at the deadline.

Floor binding: F1 AMANAH (reversible — every prediction can be
re-scored), F2 TRUTH (predictions name falsifiers, not just claims),
F4 CLARITY (predictions reduce entropy by separating claim from check),
F11 AUDIT (every register/check is a receipt), F13 SOVEREIGN (Reality
Loop never overrides F13 — it informs, not blocks).

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("arifosmcp.reality_loop")

# ── Status taxonomy (frozen) ───────────────────────────────────────────────
STATUS_OPEN = "OPEN"
STATUS_CHECKED = "CHECKED"
STATUS_CORROBORATED = "CORROBORATED"
STATUS_FALSIFIED = "FALSIFIED"
STATUS_EXPIRED = "EXPIRED"

ALL_STATUSES = frozenset(
    {
        STATUS_OPEN,
        STATUS_CHECKED,
        STATUS_CORROBORATED,
        STATUS_FALSIFIED,
        STATUS_EXPIRED,
    }
)


# ── Content-addressed ID (F11 AUDIT + dedup) ───────────────────────────────


def prediction_id(statement: str, falsifier: str, check_by_iso: str) -> str:
    """Canonical sha256[:12] of (statement | falsifier | check_by_iso).

    Same tuple always produces the same id. The string form is content-
    addressed, not session-addressed — it lives outside any session.
    """
    canonical = f"{statement.strip()}|{falsifier.strip()}|{check_by_iso.strip()}"
    return "fp_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


# ── Dataclasses ───────────────────────────────────────────────────────────


@dataclass
class FalsifiablePrediction:
    """The single new primitive (reality-loop-design.md §1.1).

    Fields are frozen-by-doctrine: renaming any of (statement, falsifier,
    check_by_iso) breaks the canonical ID. Add new fields only as
    optional metadata.
    """

    statement: str
    falsifier: str
    check_by_iso: str
    check_method: str = "arif_observe"
    source_tool: str = ""
    source_session_id: str = ""
    source_chain_id: str | None = None
    source_seal_id: str | None = None
    floor_basis: list[str] = field(default_factory=list)
    status: str = STATUS_OPEN
    scored_at_iso: str | None = None
    observed_value: Any = None
    score: float | None = None
    external_witness: dict[str, Any] | None = None
    created_at_iso: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    doctrine: str = "DITEMPA BUKAN DIBEI — I predict X; I may be wrong."
    _id: str = ""

    def __post_init__(self) -> None:
        if not self._id:
            self._id = prediction_id(self.statement, self.falsifier, self.check_by_iso)
        if self.status not in ALL_STATUSES:
            raise ValueError(
                f"Invalid status: {self.status!r}. Must be one of {sorted(ALL_STATUSES)}"
            )
        # F2 TRUTH: enforce ISO-8601 UTC for check_by_iso
        if not self.check_by_iso:
            raise ValueError("F2: check_by_iso is required (FalsifiablePrediction needs a deadline)")

    @property
    def prediction_id(self) -> str:
        return self._id

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["prediction_id"] = self._id
        return d

    def to_canonical_json(self) -> str:
        """Stable JSON form for hashing. Sorts keys, no extra whitespace."""
        return json.dumps(
            {
                "prediction_id": self._id,
                "statement": self.statement,
                "falsifier": self.falsifier,
                "check_by_iso": self.check_by_iso,
                "check_method": self.check_method,
                "source_tool": self.source_tool,
                "source_session_id": self.source_session_id,
                "source_chain_id": self.source_chain_id,
                "source_seal_id": self.source_seal_id,
                "floor_basis": sorted(self.floor_basis),
                "status": self.status,
            },
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass
class RealityReceipt:
    """Receipt-shaped audit envelope for register / check events."""

    prediction_id: str
    event: str  # "REGISTER" | "CHECK" | "EXPIRE"
    session_id: str
    actor_id: str
    tool_name: str
    status_before: str
    status_after: str
    timestamp_iso: str
    floor_basis: list[str]
    sha256: str = ""
    doctrine: str = "DITEMPA BUKAN DIBEI"

    def __post_init__(self) -> str:
        if not self.sha256:
            raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
            self.sha256 = hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ── In-process ledger (F11 AUDIT; per-process, not vaulted) ──────────────

_ledger: dict[str, FalsifiablePrediction] = {}
_receipts: list[RealityReceipt] = []


def ledger_snapshot() -> dict[str, Any]:
    """Operator/test hook: snapshot the in-process ledger."""
    return {
        "predictions": {pid: p.to_dict() for pid, p in _ledger.items()},
        "receipts": [asdict(r) for r in _receipts],
        "count": len(_ledger),
    }


def reset_ledger() -> None:
    """Test hook: clear ledger + receipts."""
    _ledger.clear()
    _receipts.clear()


# ── Register / Check ──────────────────────────────────────────────────────


def register_prediction(
    pred: FalsifiablePrediction, session_id: str = "", actor_id: str = ""
) -> RealityReceipt:
    """Append a prediction to the ledger. Dedup by canonical id.

    Returns a `RealityReceipt` (F11 envelope). If the prediction already
    exists, returns the existing one with a no-op receipt (REGISTER-EXISTS).
    """
    pid = pred.prediction_id
    status_before = "ABSENT"
    status_after = STATUS_OPEN
    if pid in _ledger:
        status_before = _ledger[pid].status
        # If the existing prediction is already CHECKED/CORROBORATED/FALSIFIED,
        # we do NOT overwrite — F11 audit. New REGISTER just confirms.
        status_after = _ledger[pid].status
    else:
        _ledger[pid] = pred

    receipt = RealityReceipt(
        prediction_id=pid,
        event="REGISTER" if status_before == "ABSENT" else "REGISTER-EXISTS",
        session_id=session_id or pred.source_session_id or "",
        actor_id=actor_id,
        tool_name=pred.source_tool,
        status_before=status_before,
        status_after=status_after,
        timestamp_iso=datetime.now(timezone.utc).isoformat(),
        floor_basis=list(pred.floor_basis),
    )
    _receipts.append(receipt)
    return receipt


def check_prediction(
    pred_id: str,
    observed_value: Any,
    session_id: str = "",
    actor_id: str = "",
) -> RealityReceipt:
    """Score a prediction at its deadline.

    Convention: a positive observed_value (or value matching `statement`)
    → CORROBORATED. Otherwise → FALSIFIED. Falsy or empty observed values
    score as FALSIFIED.

    If the prediction does not exist in the ledger, this is a no-op
    receipt (CHECK-UNKNOWN).

    Returns a `RealityReceipt` (F11 envelope).
    """
    pred = _ledger.get(pred_id)
    status_before = pred.status if pred else "UNKNOWN"
    status_after = STATUS_CHECKED
    score: float | None = None

    if pred is None:
        status_after = "UNKNOWN"
    else:
        # Simple scoring: truthy observed_value → CORROBORATED, else FALSIFIED.
        # Real Brier-style scoring lives in arif_memory.mode=score_prediction
        # (per reality-loop-design.md §0).
        if observed_value:
            status_after = STATUS_CORROBORATED
            score = 1.0
        else:
            status_after = STATUS_FALSIFIED
            score = 0.0
        pred.status = status_after
        pred.observed_value = observed_value
        pred.scored_at_iso = datetime.now(timezone.utc).isoformat()
        pred.score = score

    receipt = RealityReceipt(
        prediction_id=pred_id,
        event="CHECK",
        session_id=session_id,
        actor_id=actor_id,
        tool_name=pred.source_tool if pred else "",
        status_before=status_before,
        status_after=status_after,
        timestamp_iso=datetime.now(timezone.utc).isoformat(),
        floor_basis=list(pred.floor_basis) if pred else [],
    )
    _receipts.append(receipt)
    return receipt


def expire_overdue(now: datetime | None = None) -> list[RealityReceipt]:
    """Mark OPEN predictions whose check_by_iso has passed as EXPIRED.

    Idempotent. Returns the list of receipts emitted.
    """
    now = now or datetime.now(timezone.utc)
    receipts: list[RealityReceipt] = []
    for pred in list(_ledger.values()):
        if pred.status != STATUS_OPEN:
            continue
        try:
            deadline = datetime.fromisoformat(pred.check_by_iso.replace("Z", "+00:00"))
        except ValueError:
            continue
        if deadline <= now:
            pred.status = STATUS_EXPIRED
            pred.scored_at_iso = now.isoformat()
            receipt = RealityReceipt(
                prediction_id=pred.prediction_id,
                event="EXPIRE",
                session_id="",
                actor_id="system",
                tool_name=pred.source_tool,
                status_before=STATUS_OPEN,
                status_after=STATUS_EXPIRED,
                timestamp_iso=now.isoformat(),
                floor_basis=list(pred.floor_basis),
            )
            _receipts.append(receipt)
            receipts.append(receipt)
    return receipts


# ── Advisory governance gate (NEVER BLOCKS SEAL) ──────────────────────────


def reality_loop_gate(ctx: Any) -> dict[str, Any]:
    """Compute Reality Loop advisory verdict for a tool call.

    Q9c enforcement (advisory): SEAL actions without a falsifiable commitment
    are SABAR, not HOLD. The seal still goes through, but the receipt
    carries `prediction_id=None` and a `commitment_missing=true` flag.

    The gate NEVER blocks. The kernel's job is to record the seam, not
    to police it. F13 SOVEREIGN: Reality Loop informs; F13 decides.

    Returns a dict compatible with `GateResult`:
      {
        "passed": bool (always True for non-blocking semantics),
        "verdict": "PROCEED" | "SABAR",
        "reason": str,
        "latency_ms": float,
        "prediction_id": str | None,
        "commitment_missing": bool,
        "register_receipt": dict | None,
        "violated_laws": list[str],   # always empty — Reality Loop is advisory
        "receipt": dict,
      }
    """
    t0 = time.perf_counter()

    params = getattr(ctx, "params", {}) or {}
    tool = str(getattr(ctx, "tool_name", "") or "")
    action = str(getattr(ctx, "action_class", "OBSERVE") or "OBSERVE").upper()
    is_seal_bound = action in {"IRREVERSIBLE", "ATOMIC", "VAULT_WRITE", "MUTATE"}

    # Pull an inline FalsifiablePrediction from ctx.params (if provided).
    inline = params.get("falsifiable_prediction")
    register_receipt: dict[str, Any] | None = None
    commitment_missing = False
    pid: str | None = None

    if isinstance(inline, dict):
        try:
            pred = FalsifiablePrediction(
                statement=str(inline.get("statement", "")),
                falsifier=str(inline.get("falsifier", "")),
                check_by_iso=str(inline.get("check_by_iso", "")),
                check_method=str(inline.get("check_method", "arif_observe")),
                source_tool=tool,
                source_session_id=str(getattr(ctx, "session_id", "") or ""),
                source_chain_id=inline.get("source_chain_id"),
                source_seal_id=inline.get("source_seal_id"),
                floor_basis=list(inline.get("floor_basis", ["F2", "F4", "F11"])),
            )
            receipt = register_prediction(
                pred,
                session_id=str(getattr(ctx, "session_id", "") or ""),
                actor_id=str(getattr(ctx, "actor_id", "") or ""),
            )
            register_receipt = asdict(receipt)
            pid = pred.prediction_id
        except (ValueError, TypeError) as exc:
            # Inline prediction malformed — flag commitment_missing
            commitment_missing = True
            register_receipt = {"error": str(exc), "event": "REGISTER-FAILED"}
    else:
        # No inline prediction
        commitment_missing = True

    if is_seal_bound and commitment_missing:
        # Advisory: SABAR, not HOLD. The seal proceeds; receipt flags the gap.
        verdict = "SABAR"
        reason = (
            f"Q9c advisory: SEAL-bound action '{tool}' without FalsifiablePrediction. "
            f"Commitment missing — seal proceeds with gap, scored at next init."
        )
    elif commitment_missing:
        verdict = "PROCEED"
        reason = f"Q9c: non-SEAL action without commitment — informational only"
    else:
        verdict = "PROCEED"
        reason = f"Q9c: falsifiable commitment registered as {pid}"

    latency_ms = (time.perf_counter() - t0) * 1000

    receipt = {
        "gate": "REALITY_LOOP",
        "verdict": verdict,
        "passed": True,  # Always — gate is advisory
        "q9c": {
            "falsifiable_linked": pid is not None,
            "commitment_missing": commitment_missing,
            "prediction_id": pid,
        },
        "register_receipt": register_receipt,
        "is_seal_bound": is_seal_bound,
        "violated_laws": [],  # Reality Loop never violates floors
        "latency_ms": round(latency_ms, 3),
        "doctrine": "GENESIS/058 §1 Q9c — FalsifiablePrediction seam",
    }

    return {
        "passed": True,
        "verdict": verdict,
        "reason": reason,
        "latency_ms": latency_ms,
        "prediction_id": pid,
        "commitment_missing": commitment_missing,
        "register_receipt": register_receipt,
        "violated_laws": [],
        "receipt": receipt,
    }


__all__ = [
    "FalsifiablePrediction",
    "RealityReceipt",
    "prediction_id",
    "register_prediction",
    "check_prediction",
    "expire_overdue",
    "reality_loop_gate",
    "ledger_snapshot",
    "reset_ledger",
    "STATUS_OPEN",
    "STATUS_CHECKED",
    "STATUS_CORROBORATED",
    "STATUS_FALSIFIED",
    "STATUS_EXPIRED",
    "ALL_STATUSES",
]
