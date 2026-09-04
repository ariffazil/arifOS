"""
Memory Write Policies — Item 4 of the Organ Forge
═══════════════════════════════════════════════════

L1–L6 stores exist. The missing piece is the WRITE POLICY layer:
  - what gets written,
  - who can write it,
  - when it is compacted,
  - when contradictory memory triggers HOLD.

This module is the in-process policy engine. In production it would
dispatch to L4 (Supabase) for the actual writes; here it returns
policy decisions + a record of what WOULD be written so the calling
organ can persist.

The 6 layers (L1–L6):
  L1 Redis  → ephemeral / "now"            — 60s TTL
  L2 Redis  → session thread               — session TTL
  L3 Qdrant → fuzzy similarity / "feels like"
  L4 Supabase → structured record / official
  L5 Graphiti → relationships / "connected to what"
  L6 VAULT999 → immutable sealed / final truth

The Iron Rule (from arifOS memory architecture):
  Memory does not become truth until it has provenance.
  Truth does not become final until sealed (L6).

DITEMPA BUKAN DIBERI — writes are governed, not given.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4

from arifosmcp.schemas.envelope import EvidenceEnvelope

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# LAYERS
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryLayer(StrEnum):
    L1_EPHEMERAL = "L1"  # Redis, ~60s TTL
    L2_SESSION = "L2"  # Redis, session TTL
    L3_SEMANTIC = "L3"  # Qdrant, fuzzy
    L4_STRUCTURED = "L4"  # Supabase, canonical
    L5_RELATIONAL = "L5"  # Graphiti, edges
    L6_IMMUTABLE = "L6"  # VAULT999, sealed


# Layer-specific default TTLs
LAYER_TTL: dict[MemoryLayer, Optional[timedelta]] = {
    MemoryLayer.L1_EPHEMERAL: timedelta(seconds=60),
    MemoryLayer.L2_SESSION: None,  # session-bound
    MemoryLayer.L3_SEMANTIC: None,  # persistent
    MemoryLayer.L4_STRUCTURED: None,  # persistent
    MemoryLayer.L5_RELATIONAL: None,  # persistent
    MemoryLayer.L6_IMMUTABLE: None,  # forever
}


# ═══════════════════════════════════════════════════════════════════════════════
# WRITE DECISION
# ═══════════════════════════════════════════════════════════════════════════════


class WriteAction(StrEnum):
    WRITE = "WRITE"
    PROMOTE = "PROMOTE"  # L_n → L_{n+1}
    REJECT = "REJECT"
    COMPACT = "COMPACT"
    SEAL = "SEAL"  # L4/L5 → L6
    HOLD = "HOLD"  # contradiction, needs human


@dataclass
class WriteDecision:
    layer: MemoryLayer
    action: WriteAction
    reason: str
    key: str
    payload_summary: str
    actor_id: str
    decided_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ═══════════════════════════════════════════════════════════════════════════════
# POLICY RULES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class WriteRequest:
    """What an organ wants to write."""

    actor_id: str
    actor_type: str  # human | agent | system
    layer: MemoryLayer
    key: str
    payload: Any
    source_envelope: Optional[EvidenceEnvelope] = None
    parent_keys: list[str] = field(default_factory=list)
    session_id: Optional[str] = None
    force: bool = False  # bypass policy (requires sovereign ack downstream)


# Promotion graph: which layers can promote to which
PROMOTION: dict[MemoryLayer, set[MemoryLayer]] = {
    MemoryLayer.L1_EPHEMERAL: {MemoryLayer.L2_SESSION, MemoryLayer.L3_SEMANTIC},
    MemoryLayer.L2_SESSION: {MemoryLayer.L4_STRUCTURED, MemoryLayer.L5_RELATIONAL},
    MemoryLayer.L3_SEMANTIC: {MemoryLayer.L4_STRUCTURED, MemoryLayer.L5_RELATIONAL},
    MemoryLayer.L4_STRUCTURED: {MemoryLayer.L6_IMMUTABLE},
    MemoryLayer.L5_RELATIONAL: {MemoryLayer.L6_IMMUTABLE},
    MemoryLayer.L6_IMMUTABLE: set(),  # terminal
}


# Who can write to which layer
WRITE_AUTHORITY: dict[MemoryLayer, set[str]] = {
    MemoryLayer.L1_EPHEMERAL: {"agent", "system", "human"},
    MemoryLayer.L2_SESSION: {"agent", "system", "human"},
    MemoryLayer.L3_SEMANTIC: {"agent", "system"},
    MemoryLayer.L4_STRUCTURED: {"agent", "system"},  # human only via sovereign path
    MemoryLayer.L5_RELATIONAL: {"agent", "system"},
    MemoryLayer.L6_IMMUTABLE: {"system"},  # only arifOS 999 seal can write L6
}


class PolicyError(Exception):
    """Raised when a write violates the policy."""


# ═══════════════════════════════════════════════════════════════════════════════
# POLICY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryPolicyEngine:
    """The single gate every write passes through.

    In production, the actual store is L4 (Supabase). Here we return
    a WriteDecision + an audit record. The caller (organ code) is
    responsible for the actual write to the store.
    """

    def __init__(self) -> None:
        self._decisions: list[WriteDecision] = []
        # Track keys for promotion logic
        self._keys_by_layer: dict[MemoryLayer, set[str]] = {l: set() for l in MemoryLayer}

    def decide(self, req: WriteRequest) -> WriteDecision:
        # 1. Authority check
        if req.actor_type not in WRITE_AUTHORITY.get(req.layer, set()):
            return self._record(
                req,
                WriteAction.REJECT,
                f"Actor type '{req.actor_type}' cannot write to {req.layer.value}",
            )

        # 2. L6 is write-once via seal
        if req.layer == MemoryLayer.L6_IMMUTABLE:
            if req.actor_type != "system":
                return self._record(
                    req,
                    WriteAction.REJECT,
                    "L6 immutable: only system seal path (arifOS 999) can write",
                )

        # 3. Provenance check (L04 CLARITY): no envelope + non-ephemeral → REJECT
        if (
            req.source_envelope is None
            and req.layer not in (MemoryLayer.L1_EPHEMERAL, MemoryLayer.L2_SESSION)
            and not req.force
        ):
            return self._record(
                req,
                WriteAction.REJECT,
                f"{req.layer.value} write requires source_envelope (provenance)",
            )

        # 4. Quality gate (L02): if envelope present, FACT requires quality ≥ 0.99
        if req.source_envelope is not None:
            tag = req.source_envelope.epistemic_tag.value
            q = req.source_envelope.evidence_quality
            if tag == "FACT" and q < 0.99:
                return self._record(
                    req,
                    WriteAction.HOLD,
                    f"FACT label with quality {q} < 0.99 — needs review",
                )

        # 5. Stale envelope check
        if req.source_envelope is not None and req.source_envelope.is_stale():
            return self._record(
                req,
                WriteAction.HOLD,
                "Source envelope is stale (past expires_at)",
            )

        # 6. Contradiction check: L4/L5 writes with contradicting envelopes → HOLD
        if (
            req.source_envelope is not None
            and req.source_envelope.has_contradictions()
            and req.layer in (MemoryLayer.L4_STRUCTURED, MemoryLayer.L5_RELATIONAL)
        ):
            return self._record(
                req,
                WriteAction.HOLD,
                f"Envelope has {len(req.source_envelope.contradictions)} contradiction(s) — HOLD",
            )

        # 7. Key collision → COMPACT (L3 semantic dedup)
        if req.layer == MemoryLayer.L3_SEMANTIC and req.key in self._keys_by_layer[req.layer]:
            return self._record(
                req,
                WriteAction.COMPACT,
                f"Key {req.key} already in L3 — compact path",
            )

        # 8. Promotion from L4/L5 → L6
        if req.layer in (MemoryLayer.L4_STRUCTURED, MemoryLayer.L5_RELATIONAL):
            # SEAL-eligible writes go through a separate seal() method
            pass

        # Default: WRITE
        action = WriteAction.WRITE
        reason = f"Policy passed for {req.layer.value} write"
        self._keys_by_layer[req.layer].add(req.key)
        return self._record(req, action, reason, payload_summary=_summarize(req.payload))

    def seal_to_L6(self, req: WriteRequest, seal_hash: str) -> WriteDecision:
        """Promote an L4/L5 record to L6 (immutable). Requires seal hash."""
        if req.layer not in (MemoryLayer.L4_STRUCTURED, MemoryLayer.L5_RELATIONAL):
            return self._record(
                req,
                WriteAction.REJECT,
                "Seal requires source in L4 or L5",
            )
        if not seal_hash or len(seal_hash) < 8:
            return self._record(
                req,
                WriteAction.REJECT,
                "Seal hash required (≥ 8 chars) for L6 promotion",
            )
        seal_req = WriteRequest(
            actor_id=req.actor_id,
            actor_type="system",  # override to system
            layer=MemoryLayer.L6_IMMUTABLE,
            key=req.key,
            payload={"source_key": req.key, "source_layer": req.layer.value, "seal_hash": seal_hash},
            session_id=req.session_id,
            force=True,
        )
        return self.decide(seal_req)

    def forget_expired_L1(self) -> list[WriteDecision]:
        """Simulate TTL eviction. In production, Redis does this."""
        # Placeholder: emit a COMPACT decision for every L1 key past TTL.
        # Real impl would query Redis for TTL < 0 keys.
        return []

    def stats(self) -> dict[str, Any]:
        return {
            "decisions_total": len(self._decisions),
            "by_action": {a.value: sum(1 for d in self._decisions if d.action == a) for a in WriteAction},
            "keys_by_layer": {l.value: len(self._keys_by_layer[l]) for l in MemoryLayer},
        }

    def _record(
        self,
        req: WriteRequest,
        action: WriteAction,
        reason: str,
        *,
        payload_summary: str = "",
    ) -> WriteDecision:
        dec = WriteDecision(
            layer=req.layer,
            action=action,
            reason=reason,
            key=req.key,
            payload_summary=payload_summary or _summarize(req.payload),
            actor_id=req.actor_id,
        )
        self._decisions.append(dec)
        logger.info(f"memory_policy: {req.layer.value} {action.value} key={req.key} reason={reason}")
        return dec


def _summarize(payload: Any, max_len: int = 80) -> str:
    s = str(payload)
    if len(s) > max_len:
        s = s[: max_len - 3] + "..."
    return s


# Module-level singleton
_engine: Optional[MemoryPolicyEngine] = None


def get_engine() -> MemoryPolicyEngine:
    global _engine
    if _engine is None:
        _engine = MemoryPolicyEngine()
    return _engine
