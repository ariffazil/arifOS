"""
APEX Quantum G Telemetry — Gate 1 Bridge Instrumentation
═══════════════════════════════════════════════════════════

Bridges arifOS kernel receipts (constitutional truth) and
arifFlow metabolic receipts (FQ pulse) into provenance-complete
QG telemetry events.

MODE: OBSERVE-ONLY (Gate 1). Never ranks candidates. Never recommends
closure. Never computes G values without evidence. All APEX scalars
start null/UNKNOWN until evidenced.

INTEGRITY RULE (F13 directive 2026-08-04):
    QG_event_hash = H(kernel_receipt_hash || flow_step_hash ||
                       formula_version || payload)

This establishes traceable linkage without treating arifFlow as the
constitutional source of truth.

ARCHITECTURE:
    Agent action → arifOS receipt (truth) + arifFlow step (pulse)
                    │                              │
                    └──────────┬───────────────────┘
                               │
                          QG Bridge (this module)
                               │
                    ┌──────────┼──────────┐
                    │          │          │
              ProposalEvent  JudgmentEvent  OutcomeEvent
                    │          │          │
                    └──────────┴──────────┘
                               │
                    /var/lib/arifflow/qg_telemetry.jsonl
                               │
                    VAULT999 witness (future: Gate 8)

DITEMPA BUKAN DIBERI — Forged, Not Given.
Forged: 2026-08-04 by 333-AGI Δ MIND under F13 directive.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── Constants ───────────────────────────────────────────────────────────────

FORMULA_VERSION = "qg.v0.1"
SCHEMA_VERSION = "apex-quantum-g.telemetry.v0.1"
QG_TELEMETRY_PATH = Path("/var/lib/arifflow/qg_telemetry.jsonl")
GENESIS_HASH = "0" * 64

# Operational mode. Gate 1 = OBSERVE_ONLY. Never promote without F13.
_QG_MODE: str = os.getenv("APEX_QG_MODE", "observe")
assert _QG_MODE in ("observe",), (
    f"APEX_QG_MODE={_QG_MODE} rejected. "
    "Only 'observe' is permitted at Gate 1. "
    "Shadow/advisory/autoclose require F13 ratification."
)


# ── Dataclass — QG Telemetry Event ─────────────────────────────────────────


@dataclass
class QGEvent:
    """One immutable telemetry event per candidate action.

    All APEX scalars (A, P, E, X, G) and projection values (confidence,
    delta_g, risk, cost, quantum_g_score) default to null/UNKNOWN.
    Populating them WITHOUT evidence is a F2 TRUTH violation.
    """

    # ── Identity ──
    event_id: str
    session_id: str
    event_type: str  # "proposal" | "judgment" | "outcome"
    agent_id: str = "333-AGI"
    step_id: int = 0
    candidate_id: str = ""

    # ── Bridge references ──
    arifos_receipt_ref: Optional[str] = None
    arifflow_step_ref: Optional[str] = None

    # ── Provenance ──
    formula_version: str = FORMULA_VERSION
    kernel_commit: Optional[str] = None
    schema_version: str = SCHEMA_VERSION
    measurement_window: list[int] = field(default_factory=list)
    source_hashes: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    synthetic: bool = False

    # ── APEX scalars (NULL = UNMEASURED, never invent) ──
    apex: dict[str, Optional[float]] = field(
        default_factory=lambda: {
            "A": None,
            "P": None,
            "E": None,
            "X": None,
            "G": None,
        }
    )

    # ── Flow (may be populated from live arifFlow probe) ──
    flow: dict[str, Any] = field(
        default_factory=lambda: {
            "fq": None,
            "health": None,
            "window": [],
        }
    )

    # ── Projection (NULL = UNKNOWN until evidenced) ──
    projection: dict[str, Any] = field(
        default_factory=lambda: {
            "confidence": None,
            "delta_g": None,
            "risk": None,
            "cost": None,
            "quantum_g_score": None,
        }
    )

    # ── Constitutional ──
    constitutional: dict[str, Any] = field(
        default_factory=lambda: {
            "open_blockers": [],
            "required_floors": ["F1", "F2", "F13"],
            "authority_required": "F13",
            "recommended_verdict": "HOLD",
        }
    )

    # ── Integrity ──
    event_hash: str = ""
    previous_event_hash: str = GENESIS_HASH
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mode: str = "observe"


# ── Core Functions ──────────────────────────────────────────────────────────


def compute_qg_hash(
    kernel_receipt_hash: str,
    flow_step_hash: str,
    formula_version: str,
    payload: dict[str, Any],
) -> str:
    """Compute QG integrity hash per F13 directive.

    QG_event_hash = H(kernel_receipt_hash || flow_step_hash ||
                       formula_version || payload)
    """
    payload_json = json.dumps(payload, sort_keys=True)
    preimage = f"{kernel_receipt_hash}|{flow_step_hash}|{formula_version}|{payload_json}"
    return hashlib.sha256(preimage.encode()).hexdigest()


def get_previous_event_hash(telemetry_path: Path = QG_TELEMETRY_PATH) -> str:
    """Return the hash of the most recent QG event, or GENESIS_HASH."""
    if not telemetry_path.exists():
        return GENESIS_HASH
    try:
        with open(telemetry_path) as f:
            lines = f.readlines()
            if not lines:
                return GENESIS_HASH
            last = json.loads(lines[-1].strip())
            return last.get("event_hash", GENESIS_HASH)
    except (json.JSONDecodeError, IndexError, OSError):
        return GENESIS_HASH


def emit_event(
    event: QGEvent,
    telemetry_path: Path = QG_TELEMETRY_PATH,
) -> dict[str, Any]:
    """Append one QG telemetry event to the append-only log.

    Returns the event as a dict with the computed hash for the caller.
    Raises ValueError if any APEX scalar is non-null without evidence.
    """

    # Gate 1 invariant: no ranking, no closure recommendation
    if event.event_type not in ("proposal", "judgment", "outcome"):
        raise ValueError(f"Unknown event_type: {event.event_type}")

    # F2 TRUTH gate: populated scalars require evidence declaration.
    # Non-synthetic events with populated APEX scalars must carry at least
    # one source_hash or missing_inputs acknowledging the evidence gap.
    populated = [k for k in ("A", "P", "E", "X", "G") if event.apex.get(k) is not None]
    if populated and not event.synthetic:
        has_evidence = bool(event.source_hashes) or bool(event.missing_inputs)
        if not has_evidence:
            raise ValueError(
                f"F2 TRUTH: apex scalars {populated} set but no source_hashes "
                f"or missing_inputs declared. Set synthetic=True or provide evidence provenance."
            )

    # Compute integrity hash
    payload = {
        k: v for k, v in asdict(event).items() if k not in ("event_hash", "previous_event_hash")
    }
    krh = event.arifos_receipt_ref or GENESIS_HASH
    fsh = event.arifflow_step_ref or GENESIS_HASH
    event.event_hash = compute_qg_hash(
        kernel_receipt_hash=krh,
        flow_step_hash=fsh,
        formula_version=event.formula_version,
        payload=payload,
    )
    event.previous_event_hash = get_previous_event_hash(telemetry_path)

    # Serialize
    record = asdict(event)
    # Convert None → "UNMEASURED" in apex for human readability
    for k in ("A", "P", "E", "X", "G"):
        if record["apex"].get(k) is None:
            record["apex"][k] = "UNMEASURED"

    # Append to log
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)
    telemetry_path.touch(exist_ok=True)
    with open(telemetry_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    return record


# ── High-Level Emitters ─────────────────────────────────────────────────────


def emit_proposal(
    session_id: str,
    agent_id: str,
    step_id: int,
    candidate_id: str,
    arifos_receipt_ref: Optional[str] = None,
    arifflow_step_ref: Optional[str] = None,
    kernel_commit: Optional[str] = None,
    flow_fq: Optional[float] = None,
    flow_health: Optional[float] = None,
    flow_window: Optional[list[int]] = None,
    open_blockers: Optional[list[str]] = None,
    missing_inputs: Optional[list[str]] = None,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Emit a PROPOSAL event — candidate action predicted state.

    All APEX scalars default to null/UNKNOWN. Supply only if evidenced.
    The constitutional block gates are enforced here: if open_blockers
    is non-empty, recommended_verdict = "HOLD" regardless.
    """

    # Constitutional gate
    blockers = open_blockers or []
    verdict = "HOLD" if blockers else "PROPOSAL_ONLY"

    event = QGEvent(
        event_id=str(uuid.uuid4()),
        session_id=session_id,
        event_type="proposal",
        agent_id=agent_id,
        step_id=step_id,
        candidate_id=candidate_id,
        arifos_receipt_ref=arifos_receipt_ref,
        arifflow_step_ref=arifflow_step_ref,
        kernel_commit=kernel_commit,
        flow={
            "fq": flow_fq,
            "health": flow_health,
            "window": flow_window or [],
        },
        constitutional={
            "open_blockers": blockers,
            "required_floors": ["F1", "F2", "F13"],
            "authority_required": "F13",
            "recommended_verdict": verdict,
        },
        missing_inputs=missing_inputs or [],
        synthetic=synthetic,
        mode=_QG_MODE,
    )
    return emit_event(event)


def emit_judgment(
    session_id: str,
    agent_id: str,
    step_id: int,
    candidate_id: str,
    actual_verdict: str,
    triggered_floors: list[str],
    judge_receipt_ref: Optional[str] = None,
    arifos_receipt_ref: Optional[str] = None,
    arifflow_step_ref: Optional[str] = None,
) -> dict[str, Any]:
    """Emit a JUDGMENT event — the actual 888-APEX verdict."""

    event = QGEvent(
        event_id=str(uuid.uuid4()),
        session_id=session_id,
        event_type="judgment",
        agent_id=agent_id,
        step_id=step_id,
        candidate_id=candidate_id,
        arifos_receipt_ref=arifos_receipt_ref,
        arifflow_step_ref=arifflow_step_ref,
        constitutional={
            "open_blockers": [],
            "required_floors": triggered_floors,
            "authority_required": "F13",
            "recommended_verdict": actual_verdict,
            "judge_receipt_ref": judge_receipt_ref,
        },
        mode=_QG_MODE,
    )
    return emit_event(event)


def emit_outcome(
    session_id: str,
    agent_id: str,
    step_id: int,
    candidate_id: str,
    observed_cost: Optional[float] = None,
    observed_delta_g: Optional[float] = None,
    human_decision: Optional[str] = None,
    outcome_verdict: str = "RECORDED",
    arifos_receipt_ref: Optional[str] = None,
    arifflow_step_ref: Optional[str] = None,
) -> dict[str, Any]:
    """Emit an OUTCOME event — what actually happened.

    This is where calibration error and decision regret are computed later.
    """

    event = QGEvent(
        event_id=str(uuid.uuid4()),
        session_id=session_id,
        event_type="outcome",
        agent_id=agent_id,
        step_id=step_id,
        candidate_id=candidate_id,
        arifos_receipt_ref=arifos_receipt_ref,
        arifflow_step_ref=arifflow_step_ref,
        projection={
            "confidence": None,
            "delta_g": observed_delta_g,
            "risk": None,
            "cost": observed_cost,
            "quantum_g_score": None,
        },
        constitutional={
            "open_blockers": [],
            "required_floors": [],
            "authority_required": "F13",
            "recommended_verdict": outcome_verdict,
            "human_decision": human_decision,
        },
        mode=_QG_MODE,
    )
    return emit_event(event)


# ── Query ───────────────────────────────────────────────────────────────────


def read_events(
    limit: int = 20,
    event_type: Optional[str] = None,
    session_id: Optional[str] = None,
    telemetry_path: Path = QG_TELEMETRY_PATH,
) -> list[dict[str, Any]]:
    """Read recent QG telemetry events with optional filters."""
    if not telemetry_path.exists():
        return []

    events: list[dict[str, Any]] = []
    with open(telemetry_path) as f:
        for line in f:
            try:
                ev = json.loads(line.strip())
                if event_type and ev.get("event_type") != event_type:
                    continue
                if session_id and ev.get("session_id") != session_id:
                    continue
                events.append(ev)
            except json.JSONDecodeError:
                continue

    return events[-limit:]


def health() -> dict[str, Any]:
    """Return QG telemetry subsystem health."""
    exists = QG_TELEMETRY_PATH.exists()
    count = 0
    if exists:
        with open(QG_TELEMETRY_PATH) as f:
            count = sum(1 for _ in f if _.strip())

    return {
        "status": "ok" if exists else "uninitialized",
        "mode": _QG_MODE,
        "formula_version": FORMULA_VERSION,
        "schema_version": SCHEMA_VERSION,
        "event_count": count,
        "telemetry_path": str(QG_TELEMETRY_PATH),
        "autoclose_allowed": False,
        "ranking_allowed": False,
        "gate": 1,
        "doctrine": "OBSERVE_ONLY — no ranking, no closure, no G computation without evidence",
    }


# ── Self-Test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== APEX QG Telemetry — Gate 1 Smoke Test ===")
    print(f"  mode: {_QG_MODE}")
    print(f"  formula: {FORMULA_VERSION}")

    # Emit a synthetic proposal
    result = emit_proposal(
        session_id="SEAL-TEST-000",
        agent_id="333-AGI",
        step_id=1,
        candidate_id="candidate-test-001",
        arifos_receipt_ref="sha256:0000000000000000000000000000000000000000000000000000000000000000",
        arifflow_step_ref="receipt-test-001",
        flow_fq=1.70,
        missing_inputs=["A", "P", "E", "X", "G"],
        synthetic=True,
    )
    print(f"  proposal emitted: {result['event_id'][:12]}... hash={result['event_hash'][:16]}...")

    # Read back
    events = read_events(limit=5)
    print(f"  events in log: {len(events)}")
    print(f"  health: {json.dumps(health(), indent=2)}")
    print("=== PASS ===")
