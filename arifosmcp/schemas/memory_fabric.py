"""
arifosmcp/schemas/memory_fabric.py — UNIFIED MEMORY FABRIC (P4)
══════════════════════════════════════════════════════════════

Single API for all memory operations across 4 tiers.
No agent writes directly to VAULT999 — agents emit events,
Memory Fabric decides storage policy.

Tiers:
  L0 KernelEnvelope = current transaction state (ephemeral)
  L1 Working Memory = session/task context (Redis, short TTL)
  L2 Episodic Memory = events, attempts, receipts (Supabase)
  L3 Semantic Memory = concepts, embeddings, graph (Qdrant/FalkorDB)
  L4 Canonical Vault = sealed irreversible records (VAULT999)

Forged: 2026-07-26 under Arif's P4 directive.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from arifosmcp.schemas.authority_context import AuthorityContext
from arifosmcp.schemas.governor import GovernanceDecision, Governor

MemoryTier = Literal["working", "episodic", "semantic", "vault"]

TierPolicy = Literal["ephemeral", "session", "project", "durable", "constitutional"]


@dataclass
class MemoryEvent:
    """An event emitted by an agent. Fabric decides what tier to store in.

    This is the ONE write path. No agent writes directly to any storage backend.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = "unknown"  # tool_result, claim, decision, execution, seal_request
    session_id: str = ""
    actor_id: str = ""
    authority: AuthorityContext | None = None
    title: str = ""
    content: str = ""
    summary: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class StoreReceipt:
    """Confirmation of memory storage."""

    receipt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str = ""
    stored: bool = False
    tier: MemoryTier = "working"
    memory_id: str | None = None
    reason: str = ""
    sealed: bool = False
    seal_ref: str | None = None


class MemoryFabric:
    """Unified 4-tier memory API.

    Usage:
        fabric = MemoryFabric()
        receipt = fabric.store(event)
        results = fabric.recall("query text", tiers=["semantic", "episodic"])
        seal_receipt = fabric.seal(memory_id, authority, governor)
    """

    def store_event(
        self,
        event: MemoryEvent,
        tier: MemoryTier | None = None,
    ) -> StoreReceipt:
        """Store an event. If tier is unspecified, auto-route based on event type.

        Routing rules:
          - tool_result → episodic (L2)
          - claim → semantic (L3) + episodic (L2)
          - decision → episodic (L2)
          - execution → episodic (L2) + semantic if contains claims
          - seal_request → vault (L4) via governor
        """
        if tier:
            return self._store(event, tier)

        # Auto-routing
        if event.event_type == "seal_request":
            return self._store(event, "vault")
        if event.event_type in ("claim", "concept", "knowledge"):
            self._store(event, "episodic")  # Always record the event too
            return self._store(event, "semantic")
        if event.event_type in ("tool_result", "decision", "execution", "session"):
            return self._store(event, "episodic")
        if event.event_type in ("constitutional", "doctrine", "floor"):
            return self._store(event, "semantic")

        return self._store(event, "working")

    def _store(self, event: MemoryEvent, tier: MemoryTier) -> StoreReceipt:
        """Internal store implementation. Currently logs; future: each tier
        routes to the appropriate backend (Redis, Supabase, Qdrant, VAULT999)."""
        # Mock store — in production, this routes to actual backends
        memory_id = f"mem-{tier[:4]}-{str(uuid.uuid4())[:8]}"
        return StoreReceipt(
            event_id=event.event_id,
            stored=True,
            tier=tier,
            memory_id=memory_id,
            reason=f"Stored in {tier} (event_type={event.event_type})",
        )

    def recall(
        self,
        query: str,
        tiers: list[MemoryTier] | None = None,
        limit: int = 10,
        session_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Recall memories matching query across specified tiers.

        tiers=None → search all tiers.
        Currently placeholder; production routes to Redis/Qdrant/Supabase.
        """
        tiers = tiers or ["working", "episodic", "semantic", "vault"]
        results: list[dict[str, Any]] = []
        for tier in tiers:
            results.append(
                {
                    "tier": tier,
                    "query": query,
                    "status": "placeholder",
                    "note": f"Recall from {tier} — backend not yet wired",
                }
            )
        return results[:limit]

    def promote(
        self,
        memory_id: str,
        from_tier: MemoryTier,
        to_tier: MemoryTier,
        authority: AuthorityContext,
        reason: str = "",
    ) -> StoreReceipt:
        """Promote a memory record to a higher tier.

        Working → Episodic: automatic after session
        Episodic → Semantic: requires TRUSTED_AGENT
        Semantic → Vault: requires SOVEREIGN + governor approval
        """
        if not authority.actor_verified:
            return StoreReceipt(
                stored=False,
                memory_id=memory_id,
                reason="Promotion requires verified identity",
            )

        tier_upgrade_map = {
            ("working", "episodic"): "OBSERVER",
            ("episodic", "semantic"): "TRUSTED_AGENT",
            ("semantic", "vault"): "SOVEREIGN",
        }
        required = tier_upgrade_map.get((from_tier, to_tier))

        if required == "SOVEREIGN" and not authority.can_seal():
            return StoreReceipt(
                stored=False,
                memory_id=memory_id,
                reason=f"Promotion {from_tier}→{to_tier} requires SOVEREIGN authority",
            )
        if required == "TRUSTED_AGENT" and not authority.can_judge():
            return StoreReceipt(
                stored=False,
                memory_id=memory_id,
                reason=f"Promotion {from_tier}→{to_tier} requires TRUSTED_AGENT authority",
            )

        new_id = f"mem-{to_tier[:4]}-{memory_id[-12:]}"
        return StoreReceipt(
            stored=True,
            tier=to_tier,
            memory_id=new_id,
            reason=f"Promoted {from_tier}→{to_tier}: {reason}"
            if reason
            else f"Promoted {from_tier}→{to_tier}",
        )

    def seal(
        self,
        memory_id: str,
        authority: AuthorityContext,
        governor: Governor,
        seal_reason: str = "",
    ) -> StoreReceipt:
        """Seal a memory record to VAULT999 (L4).

        Requires:
          1. SOVEREIGN authority (or acknowledged sovereign_required)
          2. Governor approval (GovernanceDecision.verdict == "SEAL")
        """
        if not authority.can_seal():
            return StoreReceipt(
                stored=False,
                memory_id=memory_id,
                reason="Sealing requires SOVEREIGN authority",
            )

        decision = governor.evaluate(
            action_class="IRREVERSIBLE",
            reversibility="NONE",
            authority=authority,
            intent=f"Seal memory {memory_id}: {seal_reason}",
        )

        if decision.verdict != "SEAL":
            return StoreReceipt(
                stored=False,
                memory_id=memory_id,
                reason=f"Governor rejected seal: {decision.verdict} — {decision.reasons}",
            )

        seal_ref = f"seal://vault999/{memory_id}-{str(uuid.uuid4())[:8]}"
        return StoreReceipt(
            stored=True,
            tier="vault",
            memory_id=memory_id,
            sealed=True,
            seal_ref=seal_ref,
            reason=f"Sealed to VAULT999: {seal_reason}" if seal_reason else "Sealed to VAULT999",
        )


# ─── P4 self-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from arifosmcp.schemas.authority_context import AuthorityContext
    from arifosmcp.schemas.governor import Governor

    fabric = MemoryFabric()
    gov = Governor.default()

    # Test 1: Store events
    events = [
        MemoryEvent(event_type="session", title="Session started", actor_id="opencode"),
        MemoryEvent(event_type="tool_result", title="Web search complete", confidence=0.9),
        MemoryEvent(event_type="claim", title="Sabah Basin prospectivity >50%", confidence=0.7),
        MemoryEvent(event_type="seal_request", title="Finalize deployment verdict"),
    ]
    for e in events:
        r = fabric.store_event(e)
        assert r.stored, f"Failed to store {e.event_type}"
        print(f"  ✅ {e.event_type} → {r.tier} ({r.memory_id})")

    # Test 2: Promote
    sov = AuthorityContext(
        actor_id="arif", session_id="s1", authority_level="SOVEREIGN", actor_verified=True
    )
    trusted = AuthorityContext(
        actor_id="forge", session_id="s2", authority_level="TRUSTED_AGENT", actor_verified=True
    )
    anon = AuthorityContext.anonymous("s3")

    p1 = fabric.promote("mem-epis-abc12345", "episodic", "semantic", trusted, "Verified claim")
    assert p1.stored, f"Trusted promote failed: {p1.reason}"
    print(f"  ✅ Working→Episodic: {p1.reason}")

    p2 = fabric.promote("mem-sema-abc12345", "semantic", "vault", anon, "Try to seal")
    assert not p2.stored, "Anon should not promote to vault"
    print(f"  ✅ Anon→Vault blocked: {p2.reason}")

    p3 = fabric.promote("mem-sema-abc12345", "semantic", "vault", sov, "Final decision")
    assert p3.stored
    print(f"  ✅ Sovereign→Vault: {p3.reason}")

    # Test 3: Seal (full governor integration)
    seal_result = fabric.seal("mem-sema-abc12345", sov, gov, "Deployment verdict sealed")
    assert seal_result.stored and seal_result.sealed
    print(f"  ✅ Seal: {seal_result.seal_ref}")

    # Test 4: Anon cannot seal
    seal_fail = fabric.seal("mem-sema-abc12345", anon, gov, "Try seal as anon")
    assert not seal_fail.stored
    print(f"  ✅ Anon seal blocked: {seal_fail.reason}")

    # Test 5: Recall
    recall = fabric.recall("Sabah Basin", tiers=["semantic", "episodic"])
    print(f"  ✅ Recall: {len(recall)} results")

    print(f"\n✅ MemoryFabric: ALL tests PASS")
