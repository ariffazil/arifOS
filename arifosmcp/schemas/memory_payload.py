"""
arifosmcp/schemas/memory_payload.py — Per-Mode Payload Schemas (Discriminated Union)
═══════════════════════════════════════════════════════════════════════════════════

Memory Kernel v1.0 (Direction 1, ratified 2026-06-21) — Day 1 schemas.

Each arif_memory mode has a typed payload schema. The dispatcher uses
the `mode` field to discriminate between payloads at runtime.

Pattern:
  request = MemoryToolRequest(mode=..., payload=RecallPayload(...))
  # OR
  request = MemoryToolRequest.model_validate({
      "mode": "recall",
      "payload": {"query": "..."}
  })

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from .memory_modes import MemoryMode
from .memory_object import EpistemicsBlock, PolicyBlock, ProvenanceBlock, SourceReceipt
from .memory_truth import MemoryClassName, TierCode, TruthClassName


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ── RecallPayload (OBSERVE) ───────────────────────────────────────────────


class RecallPayload(BaseModel):
    """OBSERVE-class. Retrieve memories across vector, graph, vault.

    Burn-down C1 (retrieval path fix, 2026-06-21):
      `graph_first=True` makes the dispatcher run graph traversal
      BEFORE vector search. This makes multi-hop and temporal queries
      first-class rather than vector-only biased.

    Burn-down A3 (organ staleness fix, 2026-06-21):
      `organ_staleness_band` lets the caller declare tolerance for
      stale organ data (e.g., GEOX/WEALTH/WELL last known DEGRADED).
      If unset, dispatcher uses kernel-arifos_health probe.
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["recall"] = "recall"

    query: str | None = None
    embedding_ref: str | None = None
    scope: Literal["all", "session", "actor", "organ", "project"] = "all"
    memory_class: MemoryClassName | None = None
    truth_class: list[TruthClassName] | None = None
    top_k: int = Field(default=10, ge=1, le=100)
    progressive_level: Literal["L0", "L1", "L2", "L3"] = "L1"
    hybrid: bool = True  # vector → graph → vault cascade
    graph_first: bool = True  # C1: graph before vector (default ON)
    include_contested: bool = False
    time_window_hours: int | None = None  # C2: temporal window (recency filter)
    temporal_as_of: datetime | None = None  # C2: "what was true at this time?"
    organ_staleness_band: Literal["strict", "tolerant", "ignore"] = "strict"  # A3


# ── InspectPayload (OBSERVE) ──────────────────────────────────────────────


class InspectPayload(BaseModel):
    """OBSERVE-class. Read a memory object's full state."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["inspect"] = "inspect"

    memory_id: str
    include: list[
        Literal[
            "payload",
            "provenance",
            "epistemics",
            "policy",
            "lineage",
            "contradictions",
            "vault_ref",
            "receipts",
        ]
    ] = Field(default_factory=lambda: ["payload", "provenance", "epistemics"])
    redact_pii: bool = True


# ── AttestPayload (OBSERVE) ───────────────────────────────────────────────


class AttestPayload(BaseModel):
    """OBSERVE-class. Verify a memory_id against vault seal chain."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["attest"] = "attest"

    memory_id: str | None = None
    run_id: str | None = None
    seal_id: str | None = None
    aspect: Literal["integrity", "lineage", "contradictions", "tier_consistency"] = "integrity"
    include_proof: bool = False  # return Merkle path


# ── RememberPayload (MUTATE) ──────────────────────────────────────────────


class RememberPayload(BaseModel):
    """MUTATE-class. Write a candidate memory. Default-deny until validated.

    The `tier_hint` (formerly `tier_target`) is REQUESTED tier only.
    Floors (L02/L04/L07/L11) and 888_JUDGE may DOWNGRADE the actual
    write tier — e.g., an attempted L3 write that fails confidence
    check gets parked at L1 (KSR ephemeral) until approved.

    Field renamed per §12.2 verdict (Arif 2026-06-21) to make the
    downgrade possibility explicit. Promotion to L4+ is ALWAYS a
    separate explicit `promote` call (§12.4 verdict) — never implicit
    via `remember`.
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["remember"] = "remember"

    content: str | None = None
    structured: dict[str, Any] | None = None  # alternative to free text
    memory_class: MemoryClassName = "episodic"
    truth_class: EpistemicsBlock = Field(default_factory=lambda: EpistemicsBlock(confidence=0.5))
    provenance: ProvenanceBlock
    source_receipts: list[SourceReceipt] = Field(default_factory=list)
    policy: PolicyBlock = Field(default_factory=PolicyBlock)
    tier_hint: TierCode = "L3"  # requested; floors may downgrade
    idempotency_key: str | None = None


# ── PromotePayload (MUTATE) ───────────────────────────────────────────────


class PromotePayload(BaseModel):
    """MUTATE-class. Move candidate from lower tier to higher."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["promote"] = "promote"

    memory_id: str
    from_tier: TierCode
    to_tier: TierCode
    promotion_reason: str
    required_floors_satisfied: list[str]  # operator must attest
    human_approval: bool = False  # required for L4+


# ── RevisePayload (MUTATE) ────────────────────────────────────────────────


class RevisePayload(BaseModel):
    """MUTATE-class. Supersede prior memory with corrected version.

    Burn-down B2 (drift fix, 2026-06-21):
      `supersedes_memory_id` MUST be set for `resolution_kind` of
      "supersede" or "merge". The dispatcher enforces this at write
      time — a revise without supersession is a write-without-trace,
      which is exactly how drift accumulates.
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["revise"] = "revise"

    memory_id: str  # the prior memory to revise
    supersedes_memory_id: str | None = None  # B2: required for supersede/merge
    correction_event: str | None = None
    new_content: str | None = None
    new_structured: dict[str, Any] | None = None
    new_truth_class: EpistemicsBlock | None = None
    resolution_kind: Literal["supersede", "merge", "void", "acknowledge"] = "supersede"


# ── ForgetPayload (ATOMIC) ────────────────────────────────────────────────


class ForgetPayload(BaseModel):
    """ATOMIC-class. Soft-delete or revoke.

    IRREVERSIBLE ON RECALL (§12.3 verdict, Arif 2026-06-21):
      Bytes cannot be restored in L1/L2/L3/L4/L5 once tombstoned.

    APPEND-ONLY ON HISTORY:
      Every forget emits a sealed revocation/tombstone entry into the
      vault (L6) that itself is never deleted. Reversal is modelled
      as a NEW MemoryObject + vault entry — never a restoration of
      the original record.

    For extremely sensitive forgets (PDPA/GDPR-class), the vault
    record is MINIMISED: contains only a salted hash + reason code,
    not raw identifiers.

    `require_human_ack=True` is the default for ATOMIC class per
    L13 SOVEREIGN.
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["forget"] = "forget"

    memory_id: str
    policy_basis: Literal[
        "ttl_expired",
        "scope_revoked",
        "consent_withdrawn",
        "floor_violation",
        "superseded",
        "human_veto",
    ] = "ttl_expired"
    cascade: bool = False
    tombstone_text: str | None = None
    require_human_ack: bool = True  # default True for ATOMIC class
    minimised_vault_record: bool = False  # PDPA/GDPR mode: salt + reason only


# ── Discriminated Union ───────────────────────────────────────────────────
# Pydantic v2 native discriminator. The kernel dispatcher matches on `mode`.

MemoryPayload = Annotated[
    Union[
        RecallPayload,
        InspectPayload,
        AttestPayload,
        RememberPayload,
        PromotePayload,
        RevisePayload,
        ForgetPayload,
    ],
    Field(discriminator="mode"),
]


# ── The Full Tool Request Envelope ────────────────────────────────────────


class MemoryToolRequest(BaseModel):
    """The full arif_memory request envelope.

    All incoming tool calls are validated against this schema BEFORE
    the kernel dispatcher routes to the mode-specific handler.

    Example:
        req = MemoryToolRequest(
            mode=MemoryMode.RECALL,
            payload=RecallPayload(query="constitutional floors", top_k=5),
            session_id="sess_abc",
            actor_id="arif",
        )
    """

    model_config = ConfigDict(extra="forbid")

    mode: MemoryMode
    payload: MemoryPayload
    session_id: str | None = None
    actor_id: str
    lease_id: str | None = None  # required for MUTATE/ATOMIC
    human_approval: bool = False  # required for ATOMIC + L4+
    idempotency_key: str | None = None
    trace_id: str | None = None  # shadow-detection forge
    caller_chain: list[str] = Field(default_factory=list)  # origin audit
    timestamp: datetime | None = None


__all__ = [
    "RecallPayload",
    "InspectPayload",
    "AttestPayload",
    "RememberPayload",
    "PromotePayload",
    "RevisePayload",
    "ForgetPayload",
    "MemoryPayload",
    "MemoryToolRequest",
]
