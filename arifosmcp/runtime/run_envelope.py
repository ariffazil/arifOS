"""
arifOS Run Envelope — shared transaction context for the governed flow.

Epoch 2 / Item 1 of the Kernel Senescence Reduction plan.
The single object that flows through every stage of one run. Each stage
reads the previous envelope, appends its result, and returns a new
envelope. Earlier history is never rewritten.

Schema (from F13 epoch / audit spec):
    {
      "run_id": "run-...",
      "session_ref": "arifos://session/...",
      "actor_ref": "arifos://identity/...",
      "intent_hash": "sha256:...",
      "trace_id": "...",
      "evidence_refs": [],
      "current_stage": "OBSERVE",
      "stage_history": [],
      "effective_verdict": null,
      "receipt_ref": null
    }

A successful tool call without continuity is not a successful metabolism.
This module is the continuity.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, replace
from typing import Any, Final

# Schema version. Bump when the canonical shape changes.
RUN_STATE_VERSION = 1


# ── The 10-stage flow (audit spec) ────────────────────────────────────────

# Canonical stages in order. The kernel has 8 tools; OBSERVE and FORGE
# each cover one extra stage internally (EVIDENCE and VERIFY_CONSEQUENCE
# respectively), but every stage appears in the run envelope's history.
STAGE_INIT: Final = "INIT"
STAGE_OBSERVE: Final = "OBSERVE"
STAGE_EVIDENCE: Final = "EVIDENCE"
STAGE_THINK: Final = "THINK"
STAGE_ROUTE: Final = "ROUTE"
STAGE_MEMORY: Final = "MEMORY"
STAGE_JUDGE: Final = "JUDGE"
STAGE_FORGE: Final = "FORGE"
STAGE_VERIFY_CONSEQUENCE: Final = "VERIFY_CONSEQUENCE"
STAGE_RECEIPT: Final = "RECEIPT"

CANONICAL_STAGES: Final = (
    STAGE_INIT,
    STAGE_OBSERVE,
    STAGE_EVIDENCE,
    STAGE_THINK,
    STAGE_ROUTE,
    STAGE_MEMORY,
    STAGE_JUDGE,
    STAGE_FORGE,
    STAGE_VERIFY_CONSEQUENCE,
    STAGE_RECEIPT,
)

# Map each canonical tool to the stage(s) it executes.
# arif_observe covers OBSERVE + EVIDENCE (it produces evidence_refs).
# arif_forge covers FORGE + VERIFY_CONSEQUENCE (it verifies before acting).
# arif_seal is the terminal RECEIPT stage.
TOOL_TO_STAGES: Final = {
    "arif_init": (STAGE_INIT,),
    "arif_observe": (STAGE_OBSERVE, STAGE_EVIDENCE),
    "arif_think": (STAGE_THINK,),
    "arif_route": (STAGE_ROUTE,),
    "arif_memory": (STAGE_MEMORY,),
    "arif_judge": (STAGE_JUDGE,),
    "arif_forge": (STAGE_FORGE, STAGE_VERIFY_CONSEQUENCE),
    "arif_seal": (STAGE_RECEIPT,),
}

STAGE_TO_TOOL: Final = {stage: tool for tool, stages in TOOL_TO_STAGES.items() for stage in stages}


# ── Stage record ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StageRecord:
    """One completed stage's contribution to a run.

    Immutable. Appended to RunEnvelope.stage_history.
    """

    stage: str
    tool: str
    started_at: str
    finished_at: str
    outcome: str  # canonical verdict value
    evidence_refs: tuple[str, ...] = ()
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "tool": self.tool,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "outcome": self.outcome,
            "evidence_refs": list(self.evidence_refs),
            "notes": self.notes,
        }


# ── Run envelope ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RunEnvelope:
    """The single object that flows through every stage of one run.

    Frozen. Each stage transition produces a new envelope. Earlier history
    is preserved by construction.
    """

    run_id: str
    session_ref: str  # arifos://session/{id}
    actor_ref: str  # arifos://identity/{id}
    intent_hash: str  # sha256:... of the original intent string
    trace_id: str
    evidence_refs: tuple[str, ...] = ()
    current_stage: str = STAGE_INIT
    stage_history: tuple[StageRecord, ...] = ()
    effective_verdict: str | None = None
    receipt_ref: str | None = None
    state_version: int = RUN_STATE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "session_ref": self.session_ref,
            "actor_ref": self.actor_ref,
            "intent_hash": self.intent_hash,
            "trace_id": self.trace_id,
            "evidence_refs": list(self.evidence_refs),
            "current_stage": self.current_stage,
            "stage_history": [s.to_dict() for s in self.stage_history],
            "effective_verdict": self.effective_verdict,
            "receipt_ref": self.receipt_ref,
        }


# ── Construction ──────────────────────────────────────────────────────────


def _hash_intent(intent: str) -> str:
    """sha256 of the intent string. The intent itself is never stored in
    the envelope — only its hash. The full intent lives in the source
    of the run; the hash binds the run to that source.
    """
    return f"sha256:{hashlib.sha256(intent.encode('utf-8')).hexdigest()}"


def start_run(
    *,
    session_id: str,
    actor_id: str,
    intent: str,
    trace_id: str | None = None,
) -> RunEnvelope:
    """Open a new run. The first stage is INIT.

    Returns the canonical RunEnvelope with no history, no evidence,
    no verdict, no receipt. Subsequent stages mutate by transition.
    """
    return RunEnvelope(
        run_id=f"run-{uuid.uuid4().hex[:16]}",
        session_ref=f"arifos://session/{session_id}",
        actor_ref=f"arifos://identity/{actor_id}",
        intent_hash=_hash_intent(intent),
        trace_id=trace_id or f"trc-{uuid.uuid4().hex[:16]}",
        evidence_refs=(),
        current_stage=STAGE_INIT,
        stage_history=(),
        effective_verdict=None,
        receipt_ref=None,
    )


# ── Transitions ──────────────────────────────────────────────────────────


def add_evidence(envelope: RunEnvelope, evidence_ref: str) -> RunEnvelope:
    """Append an evidence reference. Returns a new envelope.

    Idempotent: duplicate refs are not added twice. The order of unique
    refs is preserved.
    """
    if evidence_ref in envelope.evidence_refs:
        return envelope
    return replace(
        envelope,
        evidence_refs=envelope.evidence_refs + (evidence_ref,),
    )


def record_stage(
    envelope: RunEnvelope,
    *,
    tool: str,
    started_at: str,
    finished_at: str,
    outcome: str,
    evidence_refs: tuple[str, ...] = (),
    notes: str = "",
) -> RunEnvelope:
    """Append a StageRecord to the run. Advances current_stage to the tool's
    highest stage. Returns a new envelope.

    The audit requires: accept the previous envelope, append, preserve
    run_id, preserve actor and session, add evidence by reference, never
    rewrite earlier history. record_stage satisfies all six.
    """
    if tool not in TOOL_TO_STAGES:
        raise ValueError(f"unknown tool: {tool!r}. canonical 8: {sorted(TOOL_TO_STAGES.keys())}")
    stages = TOOL_TO_STAGES[tool]
    # The "current" stage becomes the last stage this tool covers.
    new_current = stages[-1]

    # Append the tool's stages to the history. For single-stage tools,
    # one record. For two-stage tools (observe, forge), one record with
    # the tool and the last stage — the intermediate stage is internal.
    record = StageRecord(
        stage=new_current,
        tool=tool,
        started_at=started_at,
        finished_at=finished_at,
        outcome=outcome,
        evidence_refs=evidence_refs,
        notes=notes,
    )
    new_history = envelope.stage_history + (record,)
    # Append the new evidence refs to the envelope's evidence_refs.
    new_evidence = envelope.evidence_refs
    for ref in evidence_refs:
        if ref not in new_evidence:
            new_evidence = new_evidence + (ref,)
    return replace(
        envelope,
        current_stage=new_current,
        stage_history=new_history,
        evidence_refs=new_evidence,
    )


def set_verdict(
    envelope: RunEnvelope,
    verdict: str,
    *,
    receipt_ref: str | None = None,
) -> RunEnvelope:
    """Set the effective_verdict. Optionally set the receipt_ref.

    The verdict is final only after the JUDGE stage has approved. The
    caller is responsible for sequencing (e.g., call this only after
    record_stage with tool='arif_judge' and outcome in {SEAL, SABAR}).
    """
    return replace(
        envelope,
        effective_verdict=verdict,
        receipt_ref=receipt_ref,
    )


def finalise_receipt(
    envelope: RunEnvelope,
    *,
    receipt_ref: str,
) -> RunEnvelope:
    """Mark the run as sealed. The receipt_ref is now non-null.

    This is a one-way operation. The run is sealed; the envelope is now
    append-only. To inspect history, use stage_history.
    """
    if envelope.effective_verdict is None:
        raise ValueError(
            "cannot finalise receipt: effective_verdict is None. Call set_verdict first."
        )
    return replace(
        envelope,
        current_stage=STAGE_RECEIPT,
        receipt_ref=receipt_ref,
    )


# ── Next-stage guidance ──────────────────────────────────────────────────


def next_stage_for(envelope: RunEnvelope) -> str | None:
    """The lawful next stage for the current envelope.

    Returns None if the run is sealed or in an unknown state. The audit's
    rule: a successful tool call returns one next lawful stage.
    """
    if envelope.receipt_ref is not None:
        return None  # sealed
    if envelope.current_stage not in CANONICAL_STAGES:
        return None
    idx = CANONICAL_STAGES.index(envelope.current_stage)
    if idx + 1 >= len(CANONICAL_STAGES):
        return None
    return CANONICAL_STAGES[idx + 1]


def stages_remaining(envelope: RunEnvelope) -> tuple[str, ...]:
    """Stages still ahead of the current_stage. Empty if sealed."""
    if envelope.current_stage not in CANONICAL_STAGES:
        return ()
    idx = CANONICAL_STAGES.index(envelope.current_stage)
    return CANONICAL_STAGES[idx + 1 :]


def is_sealed(envelope: RunEnvelope) -> bool:
    return envelope.receipt_ref is not None


__all__ = [
    "RUN_STATE_VERSION",
    "STAGE_INIT",
    "STAGE_OBSERVE",
    "STAGE_EVIDENCE",
    "STAGE_THINK",
    "STAGE_ROUTE",
    "STAGE_MEMORY",
    "STAGE_JUDGE",
    "STAGE_FORGE",
    "STAGE_VERIFY_CONSEQUENCE",
    "STAGE_RECEIPT",
    "CANONICAL_STAGES",
    "TOOL_TO_STAGES",
    "STAGE_TO_TOOL",
    "StageRecord",
    "RunEnvelope",
    "start_run",
    "add_evidence",
    "record_stage",
    "set_verdict",
    "finalise_receipt",
    "next_stage_for",
    "stages_remaining",
    "is_sealed",
]
