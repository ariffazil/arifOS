"""
arifosmcp/schemas/memory_object.py — MemoryObject, ReceiptEnvelope, MemoryResultEnvelope
════════════════════════════════════════════════════════════════════════════════════════

Memory Kernel v1.0 (Direction 1, ratified 2026-06-21) — Day 1 schemas.

The canonical envelopes that:
  - Persist across L1-L5 substrates (MemoryObject).
  - Audit every memory operation (ReceiptEnvelope).
  - Return to the caller from every arif_memory call (MemoryResultEnvelope).

These are the SHAPE of governance. Every LLM-facing memory result passes
through MemoryResultEnvelope; every persisted record is a MemoryObject;
every operation emits a ReceiptEnvelope.

Constitutional Memory (Δ Axis 3, ratified 2026-07-11):
  The missing depth axis: Memory → Moral Anchor → Constitutional Recall.
  Without Δ in memory, the system recalls facts.
  With Δ in memory, the system recalls meaning.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .memory_truth import (
    MemoryClassName,
    TierCode,
    TruthClassName,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _utc_now() -> datetime:
    """Timezone-aware UTC now. Centralised so all timestamps align."""
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    """Generate a prefixed ID, e.g. mem_<uuid>, rcp_<uuid>."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def compute_call_hash(
    input_payload: dict[str, Any] | str,
    output_payload: dict[str, Any] | str,
    mode: str,
    tool_name: str = "arif_memory",
    timestamp: datetime | None = None,
) -> str:
    """Compute the canonical call_hash for a memory operation.

    Per §12.5 verdict (Arif 2026-06-21):
        call_hash = sha256(input_payload | output_payload | mode |
                           tool_name | timestamp)

    The hash is bound to: the request payload (sha256 of canonicalised
    JSON), the response payload (same), the mode string, the tool name,
    and the operation timestamp. Any change in any of these inputs
    changes the hash, providing non-repudiation on a single call.

    For sensitive operations (promote / revise / forget / high-stakes
    remember / attest), this hash MUST be included in any vault-sealed
    receipt — see ReceiptEnvelope.call_hash.

    Args:
        input_payload: The deserialised request payload (or its JSON string).
        output_payload: The deserialised response payload (or its JSON string).
        mode: The MemoryMode value (e.g. "recall", "forget").
        tool_name: The originating tool (default "arif_memory").
        timestamp: Operation timestamp (default: now UTC).

    Returns:
        A string of the form "sha256:<64-hex-chars>".
    """
    import hashlib
    import json as _json

    def _canon(obj: dict[str, Any] | str) -> str:
        if isinstance(obj, str):
            return obj
        return _json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)

    ts = (timestamp or _utc_now()).isoformat()
    concat = "|".join(
        [
            _canon(input_payload),
            _canon(output_payload),
            mode,
            tool_name,
            ts,
        ]
    )
    return "sha256:" + hashlib.sha256(concat.encode("utf-8")).hexdigest()


# ── Source Receipt ─────────────────────────────────────────────────────────


class SourceReceipt(BaseModel):
    """Cryptographic receipt for a memory's upstream source."""

    model_config = ConfigDict(extra="forbid")

    receipt_id: str
    receipt_kind: Literal["read", "write", "promotion", "revision", "seal", "execution"]
    source_ref: str  # URI, run_id, or memory_id
    timestamp: datetime
    digest_hash: str  # sha256:...
    actor_id: str | None = None  # who created this receipt


# ── Provenance Block ───────────────────────────────────────────────────────


class ProvenanceBlock(BaseModel):
    """Where did this memory come from?"""

    model_config = ConfigDict(extra="forbid")

    origin: Literal["tool", "human", "web", "system", "agent", "vault"]
    source_uri: str | None = None
    run_id: str | None = None
    actor_id: str
    actor_signature: str | None = None  # human or service signature
    captured_at: datetime


# ── Epistemics Block ───────────────────────────────────────────────────────


class EpistemicsBlock(BaseModel):
    """How confident are we, and what is its current epistemic status?"""

    model_config = ConfigDict(extra="forbid")

    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty_band: float = Field(ge=0.0, le=0.5, default=0.05)
    status: TruthClassName = "observed"


# ── Policy Block ───────────────────────────────────────────────────────────


class PolicyBlock(BaseModel):
    """How is this memory scoped, who can see it, and when does it expire?"""

    model_config = ConfigDict(extra="forbid")

    scope: Literal["private", "shared", "public", "sovereign"] = "private"
    ttl: str | None = None  # ISO 8601 duration, e.g. P30D
    deletable: bool = True
    requires_f13_sovereign_ack: bool = False
    floors_required: list[str] = Field(default_factory=list)


class ApplicabilityBlock(BaseModel):
    """Conditions under which a memory may influence a decision."""

    model_config = ConfigDict(extra="forbid")

    actors: list[str] = Field(default_factory=list)
    models: list[str] = Field(default_factory=list)
    harnesses: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    organs: list[str] = Field(default_factory=list)
    task_classes: list[str] = Field(default_factory=list)
    environments: list[str] = Field(default_factory=list)
    valid_until: datetime | None = None
    expires_on_model_change: bool = False


class FutureValueBlock(BaseModel):
    """Predicted utility and retrieval risks for future decisions."""

    model_config = ConfigDict(extra="forbid")

    recurrence_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    decision_impact: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_reliability: float = Field(default=0.0, ge=0.0, le=1.0)
    retrieval_specificity: float = Field(default=0.0, ge=0.0, le=1.0)
    maintenance_cost: float = Field(default=0.0, ge=0.0, le=1.0)
    privacy_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    staleness_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    anchoring_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    misapplication_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    token_cost_normalized: float = Field(default=0.0, ge=0.0, le=1.0)


class MemoryAuthorityBlock(BaseModel):
    """Authority effects are asymmetric: memory may restrict, never expand."""

    model_config = ConfigDict(extra="forbid")

    epistemic_status: Literal["OBS", "DER", "INT", "SPEC"] = "OBS"
    authority_status: Literal["descriptive", "advisory", "approved", "prohibited"] = (
        "descriptive"
    )
    may_inform_reasoning: bool = True
    may_change_routing: bool = False
    may_restrict_tools: bool = False
    may_expand_tools: Literal[False] = False
    may_lower_autonomy: bool = False
    may_raise_autonomy: Literal[False] = False


class DecisionValueLifecycle(BaseModel):
    """Review and observed-value state for a candidate memory."""

    model_config = ConfigDict(extra="forbid")

    state: Literal["candidate", "temporary", "promoted", "revised", "decayed", "expired"] = (
        "candidate"
    )
    review_after: datetime | None = None
    confidence_decay_per_month: float = Field(default=0.05, ge=0.0, le=1.0)
    observed_decision_value: float | None = Field(default=None, ge=-1.0, le=1.0)
    useful_outcomes: int = 0
    harmful_outcomes: int = 0




# ── Constitutional Memory Enums (Δ Axis 3) ────────────────────────────────
# The human values from Δ (SOUL) that shape the floors.
# A memory can serve multiple values.


class ValueAnchor(str, Enum):
    """Human values from Δ (SOUL) — the provenance of care.

    These are not emotions. They are the ethical commitments that
    produce governance constraints. Love is one of the human states
    that produces these intentions — but the system does not inherit
    the feeling, only the intention's geometry.
    """

    DIGNITY = "dignity"      # → F6 MARUAH
    PROTECTION = "protection"  # → F5 PEACE²
    SOVEREIGNTY = "sovereignty"  # → F13 SOVEREIGN
    TRUTH = "truth"          # → F2 TRUTH
    WITNESS = "witness"      # → F3 TRI-WITNESS
    PATIENCE = "patience"    # → F7 HUMILITY
    REVERSIBILITY = "reversibility"  # → F1 AMANAH
    CLARITY = "clarity"      # → F4 CLARITY
    EMPATHY = "empathy"      # → F6 EMPATHY
    GENIUS = "genius"        # → F8 GENIUS


class FloorCode(str, Enum):
    """Constitutional floor codes (F1–F13).

    When a memory has a floor_constraint, the recall mechanism can enforce:
    "This memory is protected by F6. If your intent conflicts with F6 MARUAH,
    you may recall the fact but not override the value."
    """

    F1 = "F1"    # AMANAH — Reversible-first
    F2 = "F2"    # TRUTH — ≥ 0.99 fidelity
    F3 = "F3"    # TRI-WITNESS — Byzantine consensus
    F4 = "F4"    # CLARITY — ΔS ≤ 0
    F5 = "F5"    # PEACE² — Non-destructive power
    F6 = "F6"    # EMPATHY — Protect weakest stakeholder
    F7 = "F7"    # HUMILITY — Ω₀ ∈ [0.03, 0.05]
    F8 = "F8"    # GENIUS — G ≥ 0.80
    F9 = "F9"    # ANTIHANTU — No deception
    F10 = "F10"  # ONTOLOGY — AI-only ontology
    F11 = "F11"  # AUDITABILITY — Every decision logged
    F12 = "F12"  # RESILIENCE — Injection defense
    F13 = "F13"  # SOVEREIGN — Human veto FINAL


class ConstitutionalMemoryBlock(BaseModel):
    """The Δ triplet — moral provenance for significant memories.

    This is the missing third axis of governed intelligence:
      Vertical:   Love → Values → Floors → Behavior → VAULT999
      Horizontal: Δ → Intention → Constraint → Expression → Irreversibility
      Depth:      Memory → Moral Anchor → Constitutional Recall

    Not every memory needs Δ. The rule: if a memory is governed by a floor,
    it must carry that floor's geometry.

    Selective application:
      - Session logs, tool output, ephemeral context → No Δ (operational data)
      - Sealed verdicts (VAULT999) → Yes Δ (irreversible decisions)
      - Sovereign directives → Yes Δ (F13 decisions)
      - Human-impact decisions → Yes Δ (F5/F6 touchpoints)
      - Promoted memories (L5→L6) → Yes Δ (important enough to anchor)
      - Technical facts, environment config → No Δ (amoral data)

    "Love is not what you feel. It's what you refuse to forget."
    """

    model_config = ConfigDict(extra="forbid")

    value_anchor: list[ValueAnchor] = Field(
        default_factory=list,
        description="Which Δ values this memory serves. Multiple allowed.",
    )
    floor_constraint: list[FloorCode] = Field(
        default_factory=list,
        description="Which F1-F13 floors govern recall and use.",
    )
    care_provenance: str | None = Field(
        default=None,
        description=(
            "Why this was remembered — the human commitment that produced it. "
            "Not metadata. Meaning."
        ),
    )


# ── The MemoryObject ──────────────────────────────────────────────────────


class MemoryObject(BaseModel):
    """Canonical memory object. Lives across L1-L5 substrates, sealed into L6.

    The binding across tiers (per design doc §4.2):
      embedding_ref    → Qdrant point id        (L3)
      graph_node_ids[] → FalkorDB / Graphiti     (L5)
      vault_ref        → VAULT999 v2 chain entry (L6)
    """

    model_config = ConfigDict(extra="forbid")

    # ── Identity ──
    memory_id: str = Field(default_factory=lambda: _new_id("mem"))
    schema_version: int = 6

    # ── Identity & lineage ──
    actor_id: str  # who created
    session_id: str | None = None
    task_id: str | None = None
    run_id: str | None = None

    # ── Classification ──
    memory_class: MemoryClassName
    truth_class: TruthClassName = "observed"
    tier: TierCode

    # ── Content ──
    content: str  # canonicalised text
    structured: dict[str, Any] | None = None  # structured form
    embedding_ref: str | None = None  # vec_<uuid> → Qdrant point id
    graph_node_ids: list[str] = Field(default_factory=list)  # L5 refs

    # ── Entities & relations ──
    entities: list[str] = Field(default_factory=list)
    relations: list[dict[str, str]] = Field(default_factory=list)

    # ── Epistemic metadata ──
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    uncertainty_band: float = Field(ge=0.0, le=0.5, default=0.05)

    # ── Provenance ──
    provenance: ProvenanceBlock
    source_receipts: list[SourceReceipt] = Field(default_factory=list)

    # ── Policy ──
    policy: PolicyBlock = Field(default_factory=PolicyBlock)

    # ── Decision-value memory ──
    applicability: ApplicabilityBlock = Field(default_factory=ApplicabilityBlock)
    future_value: FutureValueBlock = Field(default_factory=FutureValueBlock)
    authority: MemoryAuthorityBlock = Field(default_factory=MemoryAuthorityBlock)
    decision_lifecycle: DecisionValueLifecycle = Field(default_factory=DecisionValueLifecycle)

    # ── Lineage ──
    supersedes: list[str] = Field(default_factory=list)  # prior memory_ids
    superseded_by: str | None = None
    contested_by: list[str] = Field(default_factory=list)  # contradiction links

    # ── Vault binding ──
    vault_ref: str | None = None  # vlt_<uuid>
    vault_seal_id: str | None = None  # explicit seal linkage
    vault_version: Literal["v1", "v2"] | None = None  # §12.6 — never write new seals to v1


    # ── Constitutional Memory (Δ Axis 3) ──
    # The missing depth axis: Memory → Moral Anchor → Constitutional Recall.
    # If a memory is governed by a floor, it MUST carry that floor's geometry.
    constitutional: ConstitutionalMemoryBlock | None = None

    # ── Telemetry ──
    recall_count: int = 0
    last_recalled_at: datetime | None = None

    # ── Lifecycle ──
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    expires_at: datetime | None = None
    tombstoned_at: datetime | None = None


# ── Receipt Envelope ──────────────────────────────────────────────────────
# Emitted by every memory operation. Hash-signed for forensic traceability.
# Phase 2 implementation: each receipt is appended to vault999-writer
# for hashes that need hash-chain binding (promote, revise, forget).


class ReceiptEnvelope(BaseModel):
    """Universal receipt for any arif_memory operation.

    Forensic-traceable per §12.5 verdict (Arif 2026-06-21):
      call_hash = sha256(input_payload | output_payload | mode | tool_name | timestamp)
      trace_id  = stable across one top-level user request or agent plan

    Both fields MUST be included in any vault-sealed receipt for
    `promote`, `revise`, `forget`, and high-stakes `remember`/`attest` calls.

    Burn-down A2 (split-brain fix, 2026-06-21):
      `vault_head` declares the canonical vault version this receipt
      binds to. Defaults to "v2". v1 receipts are LEGACY/HISTORICAL
      only — no new memory writes may seal against v1.
    """

    model_config = ConfigDict(extra="forbid")

    receipt_id: str = Field(default_factory=lambda: _new_id("rcp"))
    receipt_kind: Literal[
        "read", "write", "promotion", "revision", "seal", "execution", "tombstone"
    ]
    mode: str  # MemoryMode value
    actor_id: str
    session_id: str | None = None
    run_id: str | None = None
    memory_id: str | None = None
    operation_at: datetime = Field(default_factory=_utc_now)
    input_digest: str  # sha256 of input payload
    output_digest: str  # sha256 of output
    policy_snapshot: dict[str, bool]  # {floor_code: passed}
    idempotency_key: str | None = None
    trace_id: str | None = None
    call_hash: str | None = None  # §12.5 — vault-sealed receipts MUST include

    # MUTATE/ATOMIC fields
    lease_id: str | None = None
    human_approval: bool = False

    # Vault-bound fields
    vault_seal_id: str | None = None
    vault_version: Literal["v1", "v2"] | None = None  # §12.6 — never write new seals to v1
    vault_head: Literal["v1", "v2"] = "v2"  # A2 burn-down: canonical head this receipt binds to
    prev_hash: str | None = None

    # Per-mode extra (see design doc §3.4.2)
    extra: dict[str, Any] = Field(default_factory=dict)


# ── Memory Result Envelope ─────────────────────────────────────────────────
# The envelope returned from every arif_memory call.
# Mandatory fields: verdict, call_hash, receipt, floor_snapshot, delta_S.


class MemoryResultEnvelope(BaseModel):
    """Returned by every arif_memory call. Mandatory fields, no exceptions.

    Burn-down A3 (organ staleness, 2026-06-21):
      `organ_staleness_snapshot` is the kernel-arifos_health probe
      at the time of this call. If any organ is STALE/DEGRADED, the
      caller can decide whether to trust L3/L4 records from that organ.

    Burn-down C1/C2 (retrieval observability, 2026-06-21):
      `sources_consulted` lists which substrates actually returned
      hits (vector, graph, vault, organ cache). Helps the AAA cockpit
      show the operator "this recall ran graph-first" or "fell back to
      L4 only because graph returned empty".
    """

    model_config = ConfigDict(extra="forbid")

    mode: str  # MemoryMode value
    verdict: Literal["SEAL", "SABAR", "VOID", "HOLD"]
    call_hash: str  # sha256 of the entire call
    trace_id: str | None = None
    receipt: ReceiptEnvelope
    delta_S: float  # entropy delta (≤0 = success)
    floor_snapshot: dict[str, bool]  # L01..L13
    payload_result: dict[str, Any]  # mode-specific body
    next_tool_hint: str | None = None  # e.g. "arif_judge"
    timestamp: datetime = Field(default_factory=_utc_now)

    # Burn-down observability fields
    organ_staleness_snapshot: dict[str, str] = Field(default_factory=dict)
    sources_consulted: list[
        Literal["vector", "graph", "vault", "l4_record", "ksr", "organ_cache"]
    ] = Field(default_factory=list)


__all__ = [
    "ValueAnchor",
    "FloorCode",
    "ConstitutionalMemoryBlock",
    "SourceReceipt",
    "ProvenanceBlock",
    "EpistemicsBlock",
    "PolicyBlock",
    "MemoryObject",
    "ReceiptEnvelope",
    "MemoryResultEnvelope",
]
