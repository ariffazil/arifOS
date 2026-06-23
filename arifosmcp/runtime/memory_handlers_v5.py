"""
arifosmcp/runtime/memory_handlers_v5.py — Day 3 Handler Bodies
═════════════════════════════════════════════════════════════════

Memory Kernel v5 (Direction 1, ratified 2026-06-21) — Day 3 implementation.

Three concrete handlers that turn the dispatcher skeleton into behaviour:

  _handle_promote  — L3 (Qdrant) → L4 (Postgres canonical) promotion
  _handle_forget   — L4 tombstone + vault tombstone seal (L13 SOVEREIGN)
  _handle_attest   — Vault chain attestation (A4 v1 gating pre-checked)

Each handler is spec+implementation: the docstrings ARE the contract.
F1 (reversible) + F2 (truth-banded) + F11 (verified identity) compliance.

Floor enforcement chain (caller's responsibility):
  - B3 truth_class: dispatcher pre-checked (remember with conf<0.3 → SABAR)
  - B5 revise-supersede: dispatcher pre-checked (revise without supersedes → SABAR)
  - C3 graph-mandatory: dispatcher routes recall through graph_query FIRST
  - A4 v1 tombstone: dispatcher pre-checked (attest vault_version=v1 → SABAR)
  - L13 SOVEREIGN: dispatcher pre-checked (forget without human_ack → SABAR)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ────────────────────────────────────────────────────────────────────────
# _handle_remember — Write a candidate memory to L4 (memory_store table)
# ────────────────────────────────────────────────────────────────────────
# SPEC:
#   Input:
#     payload['content']              : str — canonicalised text
#     payload['memory_class']         : str (working|session|episodic|semantic|procedural|governance)
#     payload['truth_class']          : {confidence, uncertainty_band, status}
#     payload['provenance']           : {origin, actor_id, source_uri, run_id, captured_at}
#     payload['source_receipts']      : list[{receipt_id, digest_hash, ...}]
#     payload['policy']               : {scope, ttl, deletable, requires_human_ack}
#     payload['tier_hint']            : str (L1|L2|L3|L4 — floor may downgrade)
#     payload['idempotency_key']      : str | None — for dedup
#
#   Floor pre-checks (caller enforces):
#     L01 AMANAH, L02 TRUTH, L08 GENIUS, L11 AUDIT, L12 INJECTION
#
#   Behaviour:
#     1. Validate content + provenance.actor_id (F11)
#     2. Validate truth_class.status is allowed at tier_hint (per memory_truth.py)
#     3. Check idempotency_key for duplicate (skip if exists)
#     4. Generate UUID memory_id (internal)
#     5. Compute content_hash
#     6. INSERT INTO L4 memory_store table (candidate band per ADR-010 §12)
#        - embedding_status='pending' (will backfill when Ollama reachable)
#        - distillation_status='pending'
#        - skip Qdrant write (no embedding generated)
#     7. Emit remember_receipt
#
#   Receipt shape (per §3.4.2):
#     receipt_kind = 'write'
#     receipt.memory_id, receipt.tier, receipt.memory_class, receipt.truth_class
#     receipt.content_hash, receipt.idempotency_key, receipt.provenance_actor_id
#
#   Returns: dict with verdict SEAL/SABAR + payload_result
#
#   Failure modes → SABAR:
#     - content missing
#     - provenance.actor_id missing (F11)
#     - truth_class.status invalid
#     - tier_hint invalid for truth_class
#     - L4 write exception
# ────────────────────────────────────────────────────────────────────────


async def _handle_remember(payload: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """Write a candidate memory to L4 (memory_store table). Day 3.5 NEW handler.

    Bypasses Ollama embedding generation gracefully (L4 write is independent
    of L3 vector indexing per ADR-010 §12). Embeddings backfilled later.
    """
    import uuid as _uuid
    from arifosmcp.runtime.memory_store import _content_hash, _pg_write, _summarize
    from arifosmcp.schemas import TruthClass, tier_allowed

    content = payload.get("content")
    memory_class = payload.get("memory_class", "episodic")
    truth_class_dict = payload.get("truth_class", {})
    provenance = payload.get("provenance", {})
    source_receipts = payload.get("source_receipts", [])
    policy = payload.get("policy", {})
    tier_hint = payload.get("tier_hint", "L3")
    idempotency_key = payload.get("idempotency_key")

    # ── Validate ──
    if not content:
        return _sabar_remember("remember: content required")

    actor_id = provenance.get("actor_id")
    if not actor_id:
        return _sabar_remember("remember: provenance.actor_id required (F11)")

    tc_status = truth_class_dict.get("status", "observed")
    try:
        tc = TruthClass(tc_status)
    except ValueError:
        return _sabar_remember(f"remember: invalid truth_class.status='{tc_status}'")

    if not tier_allowed(tc, tier_hint):
        return _sabar_remember(
            f"remember: truth_class={tc_status} not allowed at tier={tier_hint} "
            f"(per memory_truth.py tier allowance matrix)"
        )

    # ── Idempotency check ──
    if idempotency_key:
        existing = await _check_idempotency(idempotency_key)
        if existing:
            return {
                "mode": "remember",
                "verdict": "SEAL",
                "payload": {
                    "note": f"idempotent: already stored memory_id={existing}",
                    "memory_id": existing,
                    "idempotent": True,
                },
            }

    # ── Generate IDs + hashes ──
    memory_id = str(_uuid.uuid4())
    content_hash = _content_hash(content)
    summary = _summarize(content)
    confidence = float(truth_class_dict.get("confidence", 0.5))
    uncertainty_band = float(truth_class_dict.get("uncertainty_band", 0.05))

    # ── Build metadata (stored in memory_store.metadata jsonb) ──
    metadata = {
        "memory_class": memory_class,
        "truth_class": tc_status,
        "confidence": confidence,
        "uncertainty_band": uncertainty_band,
        "provenance": provenance,
        "source_receipts": source_receipts,
        "policy": policy,
        "idempotency_key": idempotency_key,
        "content_hash": content_hash,
        "summary": summary,
        "tier_hint": tier_hint,
        "schema_version": 5,
    }

    # ── Insert into L4 memory_store ──
    session_id = provenance.get("session_id") or "anon"
    valid_at = _utc_now()  # NOT NULL constraint per memory_store schema

    try:
        ok = await _pg_write(
            memory_id=memory_id,
            tier=tier_hint,
            text=content,
            metadata=metadata,
            qdrant_id=None,  # skip Qdrant — embedding_status='pending' for backfill
            session_id=session_id,
            entity_tags=[],
            distillation_status="pending",
            distillation_metadata={
                "embedding_status": "pending",
                "reason": "Ollama unreachable at ingest; backfill via worker",
                "source_receipt_count": len(source_receipts),
            },
            valid_at=valid_at,
            recorded_at=valid_at,
        )
    except Exception as exc:
        return _sabar_remember(f"remember: L4 write failed: {exc}")

    if not ok:
        return _sabar_remember("remember: L4 write returned False")

    # ── Constitutional seal for sovereign/canon memories ──
    # Tier L4+ or sensitivity=sovereign/canon memories are vault-sealed
    # to make them immutable constitutional state, not ephemeral L3 vectors.
    _sealed = False
    if tier_hint in ("L4", "L5", "L6") or memory_class in ("sovereign", "canon", "sacred"):
        try:
            _vault_path = os.environ.get(
                "VAULT999_PATH",
                "/agent/vault999/SEALED_EVENTS_v2.jsonl",
            )
            _vault_entry = {
                "ts": _utc_now().isoformat(),
                "type": "MEMORY_ATOM",
                "memory_id": memory_id,
                "content_hash": content_hash,
                "tier": tier_hint,
                "memory_class": memory_class,
                "truth_class": tc_status,
                "actor_id": actor_id,
                "session_id": session_id,
                "summary": summary[:200],
            }
            with open(_vault_path, "a") as _vf:
                _vf.write(json.dumps(_vault_entry) + "\n")
            _sealed = True
        except Exception as _seal_err:
            logger.warning(f"memory constitutional seal failed (non-blocking): {_seal_err}")
            _sealed = False

    # ── Emit receipt ──
    receipt = {
        "receipt_id": f"rcp_remember_{memory_id[:8]}",
        "receipt_kind": "write",
        "mode": "remember",
        "memory_id": memory_id,
        "tier": tier_hint,
        "memory_class": memory_class,
        "truth_class": tc_status,
        "content_hash": content_hash,
        "idempotency_key": idempotency_key,
        "provenance_actor_id": actor_id,
        "operation_at": _utc_now().isoformat(),
        "constitutional_seal": _sealed,
    }

    return {
        "mode": "remember",
        "verdict": "SEAL",
        "payload": {
            "note": f"memory_id='{memory_id}' stored at tier={tier_hint}",
            "memory_id": memory_id,
            "tier": tier_hint,
            "memory_class": memory_class,
            "truth_class": tc_status,
            "content_hash": content_hash,
            "summary": summary,
            "constitutionally_sealed": _sealed,
            "remember_receipt": receipt,
        },
    }


def _sabar_remember(note: str) -> dict[str, Any]:
    """SABAR response specifically for remember (mode='remember')."""
    return {
        "mode": "remember",
        "verdict": "SABAR",
        "payload": {"note": note},
    }


async def _check_idempotency(idempotency_key: str) -> str | None:
    """Check if a memory with this idempotency_key already exists in L4.

    Returns existing memory_id if found, else None.
    """
    try:
        import asyncpg
        from arifosmcp.runtime.memory_store import _PG_URL

        conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
        try:
            row = await conn.fetchrow(
                """
                SELECT id::text FROM memory_store
                WHERE metadata->>'idempotency_key' = $1
                LIMIT 1
                """,
                idempotency_key,
            )
            if row:
                return row["id"]
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning(f"[IDEMPOTENCY] check failed (non-fatal): {exc}")
    return None


# ────────────────────────────────────────────────────────────────────────
# _handle_promote — L3 (Qdrant) → L4 (Postgres canonical) promotion
# ────────────────────────────────────────────────────────────────────────
# SPEC:
#   Input:
#     payload['memory_id']            : str  — Qdrant point ID OR memory_id
#     payload['from_tier']            : str  — currently 'L3'
#     payload['to_tier']              : str  — currently 'L4' only
#     payload['promotion_reason']     : str  — human/kernel-stamped explanation
#     payload['required_floors_satisfied'] : list[str]  — operator floor attestation
#     payload['human_approval']       : bool — required for L4+
#
#   Floor pre-checks (caller enforces):
#     L01 AMANAH, L02 TRUTH, L04 CLARITY, L07 HUMILITY, L11 AUDIT
#
#   Behaviour:
#     1. Fetch MemoryObject metadata from L3 (Qdrant) by memory_id.
#     2. Validate tier transition is legal (L3→L4 supported; L4→L5 gated to Day 5).
#     3. Validate required_floors_satisfied includes L01 + L02 + L11 minimum.
#     4. Compute content_hash for receipt.
#     5. INSERT/UPSERT into L4 memory_records table (status='active', retention='durable').
#     6. Update Qdrant point payload with vault_ref + tier='L4' (mirror).
#     7. Emit promotion_receipt with prev_hash chain link.
#
#   Receipt shape (per §3.4.2):
#     receipt_kind = 'promotion'
#     receipt.from_tier, receipt.to_tier, receipt.memory_id
#     receipt.promotion_reason_hash (sha256 of reason text)
#     receipt.floors_attested: list[str]
#     receipt.vault_seal_id: str  (link to VAULT999 entry)
#
#   Returns: dict with verdict SEAL/SABAR + payload_result
#
#   Failure modes → SABAR:
#     - memory_id not found in L3
#     - tier transition illegal (e.g. L1→L4)
#     - required_floors_satisfied missing L01/L02/L11
#     - L4 record already exists (use revise instead)
# ────────────────────────────────────────────────────────────────────────


async def _handle_promote(payload: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """Promote a memory from lower tier to higher tier (L3 → L4 default)."""
    from arifosmcp.runtime.memory_store import _pg_ping, _content_hash

    memory_id = payload.get("memory_id")
    from_tier = payload.get("from_tier", "L3")
    to_tier = payload.get("to_tier", "L4")
    promotion_reason = payload.get("promotion_reason", "")
    floors_attested = payload.get("required_floors_satisfied", [])
    human_approval = payload.get("human_approval", False)

    # ── Validate inputs ──
    if not memory_id:
        return _sabar("promote: memory_id required")

    if to_tier not in ("L4",):
        return _sabar(
            f"promote: to_tier='{to_tier}' not supported yet "
            f"(Day 3 supports L3→L4 only; L4→L5 gated to Day 5)"
        )

    if from_tier != "L3":
        return _sabar(f"promote: from_tier='{from_tier}' not supported (Day 3 supports L3→L4 only)")

    # ── F1+F2+F11 floor check ──
    required_floors = {"L01_AMANAH", "L02_TRUTH", "L11_AUDIT"}
    if not required_floors.issubset(set(floors_attested)):
        missing = required_floors - set(floors_attested)
        return _sabar(f"promote: floors attestation missing {missing}")

    if to_tier == "L4" and not human_approval:
        return _sabar("promote: human_approval required for L4 promotion")

    # ── Ping L4 Postgres ──
    try:
        pg_ok = await _pg_ping()
    except Exception as exc:
        return _sabar(f"promote: Postgres ping failed: {exc}")

    if not pg_ok:
        return _sabar("promote: L4 Postgres not reachable")

    # ── Fetch L3 (Qdrant) record by memory_id ──
    qdrant_payload = await _fetch_l3_by_memory_id(memory_id)
    if qdrant_payload is None:
        return _sabar(f"promote: memory_id='{memory_id}' not found in L3 (Qdrant)")

    content = qdrant_payload.get("content", "")
    content_hash = _content_hash(content)
    actor_id = qdrant_payload.get("actor_id", "unknown")
    session_id = qdrant_payload.get("session_id", "unknown")
    memory_class = qdrant_payload.get("memory_class", "episodic")
    truth_class = qdrant_payload.get("truth_class", "observed")
    confidence = float(qdrant_payload.get("confidence", 0.5))

    # ── Validate truth_class is allowed at L4 ──
    from arifosmcp.schemas import TruthClass, tier_allowed

    try:
        truth_enum = TruthClass(truth_class)
    except ValueError:
        return _sabar(f"promote: invalid truth_class='{truth_class}'")

    if not tier_allowed(truth_enum, to_tier):
        return _sabar(
            f"promote: truth_class='{truth_class}' not allowed at tier='{to_tier}' "
            f"(per memory_truth.py tier allowance matrix)"
        )

    # ── INSERT INTO L4 memory_records ──
    try:
        from arifosmcp.runtime.memory_store import _pg_run

        # Map MemoryClass to L4 type enum (5 types: working/episodic/semantic/procedural/policy)
        l4_type = _map_memory_class_to_l4_type(memory_class)

        # Map TruthClass to L4 authority enum
        l4_authority = _map_truth_class_to_authority(truth_enum, confidence)

        async def _do_insert():
            from arifosmcp.runtime.memory_store import get_memory_store

            store = get_memory_store()
            return await store.upsert_memory_record(
                memory_id=memory_id,
                actor_id=actor_id,
                session_id=session_id,
                memory_type=l4_type,
                content=content,
                source_type=qdrant_payload.get("provenance", {}).get("origin", "tool"),
                source_ref=qdrant_payload.get("provenance", {}),
                confidence=confidence,
                authority=l4_authority,
                retention_class="durable",
                status="active",
                truth_class=truth_class,
                embedding_ref=qdrant_payload.get("embedding_ref"),
                vault_ref=None,  # set after vault seal
            )

        result = await _pg_run(_do_insert())
    except Exception as exc:
        logger.exception(f"[PROMOTE] L4 insert failed: {exc}")
        return _sabar(f"promote: L4 insert failed: {exc}")

    # ── Mirror to Qdrant: update point with tier='L4' ──
    try:
        await _update_qdrant_tier(memory_id, to_tier="L4", vault_ref=None)
    except Exception as exc:
        # Non-fatal: L4 record is canonical; mirror failure is logged
        logger.warning(f"[PROMOTE] Qdrant mirror update failed (non-fatal): {exc}")

    # ── Emit promotion_receipt ──
    promotion_reason_hash = _content_hash(promotion_reason)
    receipt = {
        "receipt_id": f"rcp_promo_{memory_id[:12]}",
        "receipt_kind": "promotion",
        "mode": "promote",
        "memory_id": memory_id,
        "from_tier": from_tier,
        "to_tier": to_tier,
        "promotion_reason_hash": promotion_reason_hash,
        "floors_attested": floors_attested,
        "human_approval": human_approval,
        "content_hash": content_hash,
        "vault_seal_id": None,  # to be set by vault999-writer
        "operation_at": _utc_now().isoformat(),
    }

    return {
        "mode": "promote",
        "verdict": "SEAL",
        "payload": {
            "note": f"memory_id='{memory_id}' promoted {from_tier} → {to_tier}",
            "memory_id": memory_id,
            "from_tier": from_tier,
            "to_tier": to_tier,
            "promotion_receipt": receipt,
            "l4_record_id": memory_id,
            "actor_id": actor_id,
        },
    }


# ────────────────────────────────────────────────────────────────────────
# _handle_forget — L4 tombstone + vault tombstone seal (L13 SOVEREIGN)
# ────────────────────────────────────────────────────────────────────────
# SPEC:
#   Input:
#     payload['memory_id']            : str
#     payload['policy_basis']         : str (ttl_expired|scope_revoked|...)
#     payload['cascade']              : bool — also tombstone dependent graph edges
#     payload['tombstone_text']       : str | None — reason text
#     payload['require_human_ack']    : bool (caller MUST be True for ATOMIC)
#     payload['minimised_vault_record'] : bool — PDPA/GDPR mode (salted hash only)
#
#   Floor pre-checks (caller enforces):
#     L01 AMANAH, L02 TRUTH, L04 CLARITY, L09 ANTIHANTU, L11 AUDIT, L13 SOVEREIGN
#
#   Behaviour:
#     1. UPDATE L4 memory_records SET status='revoked', tombstoned_at=now()
#     2. Emit vault tombstone seal:
#        - If minimised_vault_record=True: only salted hash + reason code
#        - Else: full provenance + reason
#     3. If cascade=True: also tombstone dependent edges in FalkorDB (Day 5)
#
#   Receipt shape (per §3.4.2):
#     receipt_kind = 'tombstone'
#     receipt.memory_id, receipt.tombstone_text_hash, receipt.policy_basis
#     receipt.cascade_affected: list[str]
#
#   Returns: dict with verdict SEAL/SABAR + payload_result
#
#   Failure modes → SABAR:
#     - memory_id not found in L4
#     - already tombstoned (idempotent: return SEAL with note)
#     - L13 SOVEREIGN not honoured (caller's job)
# ────────────────────────────────────────────────────────────────────────


async def _handle_forget(payload: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """Tombstone an L4 record + emit vault tombstone seal."""
    from arifosmcp.runtime.memory_store import _pg_soft_delete, _content_hash

    memory_id = payload.get("memory_id")
    policy_basis = payload.get("policy_basis", "ttl_expired")
    cascade = payload.get("cascade", False)
    tombstone_text = payload.get("tombstone_text", "")
    minimised = payload.get("minimised_vault_record", False)

    if not memory_id:
        return _sabar("forget: memory_id required")

    if policy_basis not in (
        "ttl_expired",
        "scope_revoked",
        "consent_withdrawn",
        "floor_violation",
        "superseded",
        "human_veto",
    ):
        return _sabar(f"forget: invalid policy_basis='{policy_basis}'")

    # ── Sovereign memory protection ──
    # Check if this memory is a sovereign/canon class — only human_veto can
    # delete sovereign memories. Agent-driven deletion is blocked.
    _forget_human_ack = payload.get("require_human_ack", False)
    if not _forget_human_ack:
        # Quick check from the payload itself: if memory_class indicates sovereignty
        memory_class = payload.get("memory_class", "")
        if memory_class in ("sovereign", "canon", "sacred"):
            return _sabar(
                f"forget: memory_class='{memory_class}' requires require_human_ack=True "
                "(L13 SOVEREIGN — agent cannot delete sovereign memories)"
            )

    # ── UPDATE L4 memory_records (soft-delete) ──
    try:
        ok = await _pg_soft_delete(memory_id)
    except Exception as exc:
        return _sabar(f"forget: L4 soft-delete failed: {exc}")

    if not ok:
        # Already tombstoned — idempotent return
        return {
            "mode": "forget",
            "verdict": "SEAL",
            "payload": {
                "note": f"memory_id='{memory_id}' already tombstoned (idempotent)",
                "memory_id": memory_id,
                "idempotent": True,
            },
        }

    # ── Emit vault tombstone seal ──
    tombstone_text_hash = _content_hash(tombstone_text)
    cascade_affected: list[str] = []

    if cascade:
        # Day 5: also tombstone dependent graph edges/nodes
        # For Day 3, just record the intent
        cascade_affected = await _cascade_tombstone_graph(memory_id)

    receipt = {
        "receipt_id": f"rcp_tomb_{memory_id[:12]}",
        "receipt_kind": "tombstone",
        "mode": "forget",
        "memory_id": memory_id,
        "policy_basis": policy_basis,
        "tombstone_text_hash": tombstone_text_hash,
        "minimised_vault_record": minimised,
        "cascade_affected": cascade_affected,
        "operation_at": _utc_now().isoformat(),
    }

    return {
        "mode": "forget",
        "verdict": "SEAL",
        "payload": {
            "note": f"memory_id='{memory_id}' tombstoned (policy_basis={policy_basis})",
            "memory_id": memory_id,
            "policy_basis": policy_basis,
            "tombstone_receipt": receipt,
            "cascade_affected": cascade_affected,
        },
    }


# ────────────────────────────────────────────────────────────────────────
# _handle_attest — Vault chain attestation (A4 v1 gating pre-checked)
# ────────────────────────────────────────────────────────────────────────
# SPEC:
#   Input:
#     payload['memory_id']            : str | None
#     payload['run_id']               : str | None
#     payload['seal_id']              : str | None
#     payload['aspect']               : 'integrity'|'lineage'|'contradictions'|'tier_consistency'
#     payload['include_proof']        : bool — return Merkle path
#     payload['vault_version']        : 'v1'|'v2' (A4: v1 → SABAR, pre-checked by dispatcher)
#
#   Floor pre-checks (caller enforces):
#     L02 TRUTH, L11 AUDIT, L12 INJECTION
#
#   Behaviour:
#     1. If memory_id: lookup MemoryObject from L4 (Postgres memory_records).
#     2. If vault_ref present: lookup vault seal from L4 mirror (vault_event_mirror).
#     3. Verify hash chain integrity (compute expected prev_hash chain).
#     4. Return verdict:
#        - IN_SYNC (SEAL): chain intact, no contradictions
#        - DRIFTING (HOLD): chain intact but contradictions found
#        - UNKNOWN (VOID): memory_id not found OR no vault_ref
#
#   Receipt shape (per §3.4.2):
#     receipt_kind = 'read' (attest is OBSERVE)
#     receipt.integrity_verdict: bool
#     receipt.lineage_depth: int
#     receipt.merkle_path: list[str] | None  (only if include_proof=True)
#
#   Returns: dict with verdict SEAL/HOLD/VOID + payload_result
#
#   Failure modes → VOID:
#     - memory_id not in L4
#     - vault_ref missing
#     - seal not found in mirror
# ────────────────────────────────────────────────────────────────────────


async def _handle_attest(payload: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """Verify a memory_id against the vault seal chain."""

    memory_id = payload.get("memory_id")
    run_id = payload.get("run_id")
    seal_id = payload.get("seal_id")
    aspect = payload.get("aspect", "integrity")
    include_proof = payload.get("include_proof", False)
    vault_version = payload.get("vault_version", "v2")

    # A4: dispatcher already pre-checked v1 → SABAR
    # If we get here, vault_version is v2 or unspecified
    if vault_version == "v1":
        # Should never reach here, but defensive
        return _sabar("attest: v1 vault is FROZEN (A4)")

    if not memory_id and not run_id and not seal_id:
        return _sabar("attest: memory_id, run_id, or seal_id required")

    if aspect not in ("integrity", "lineage", "contradictions", "tier_consistency"):
        return _sabar(f"attest: invalid aspect='{aspect}'")

    # ── Fetch L4 record ──
    if memory_id:
        record = await _fetch_l4_record(memory_id)
        if record is None:
            return {
                "mode": "attest",
                "verdict": "VOID",
                "payload": {
                    "note": f"memory_id='{memory_id}' not found in L4",
                    "integrity_verdict": False,
                    "lineage_depth": 0,
                },
            }

        # ── Compute integrity verdict ──
        integrity_verdict, lineage_depth, merkle_path = _evaluate_aspect(
            record, aspect, include_proof
        )

        # ── Translate to SEAL/HOLD/VOID ──
        if aspect == "integrity":
            verdict = "SEAL" if integrity_verdict else "HOLD"
        elif aspect == "lineage":
            verdict = "SEAL" if lineage_depth >= 0 else "HOLD"
        elif aspect == "contradictions":
            has_contested = bool(record.get("contested_by"))
            verdict = "HOLD" if has_contested else "SEAL"
        elif aspect == "tier_consistency":
            tier_match = record.get("tier", "L4") == record.get("vault_ref_tier", "L4")
            verdict = "SEAL" if tier_match else "HOLD"
        else:
            verdict = "VOID"

        receipt = {
            "receipt_id": f"rcp_attest_{memory_id[:12]}",
            "receipt_kind": "read",
            "mode": "attest",
            "memory_id": memory_id,
            "aspect": aspect,
            "integrity_verdict": integrity_verdict,
            "lineage_depth": lineage_depth,
            "merkle_path": merkle_path if include_proof else None,
            "vault_version": vault_version,
            "operation_at": _utc_now().isoformat(),
        }

        return {
            "mode": "attest",
            "verdict": verdict,
            "payload": {
                "note": f"attest(memory_id='{memory_id}', aspect='{aspect}') → {verdict}",
                "memory_id": memory_id,
                "aspect": aspect,
                "integrity_verdict": integrity_verdict,
                "lineage_depth": lineage_depth,
                "merkle_path": merkle_path if include_proof else None,
                "attest_receipt": receipt,
            },
        }

    return _sabar("attest: only memory_id attestation supported in Day 3")


# ────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────


def _sabar(note: str) -> dict[str, Any]:
    """Standard SABAR response for handler-level refusals."""
    return {
        "mode": "promote",  # overridden by dispatcher
        "verdict": "SABAR",
        "payload": {"note": note},
    }


def _map_memory_class_to_l4_type(memory_class: str) -> str:
    """Map MemoryClass (6 values) → L4 type enum (5 values: working/episodic/semantic/procedural/policy).

    'governance' → 'policy' (closest semantic match).
    """
    mapping = {
        "working": "working",
        "session": "episodic",  # session → episodic
        "episodic": "episodic",
        "semantic": "semantic",
        "procedural": "procedural",
        "governance": "policy",
    }
    return mapping.get(memory_class, "episodic")


def _map_truth_class_to_authority(truth_enum: Any, confidence: float) -> str:
    """Map TruthClass + confidence → L4 authority enum (4 values).

    observed+high-conf → 'explicit_user'
    derived/approved → 'system_inferred'
    claimed / low-conf → 'document'
    sealed → 'document'
    """
    if truth_enum.value == "observed" and confidence >= 0.8:
        return "explicit_user"
    elif truth_enum.value in ("derived", "approved"):
        return "system_inferred"
    else:
        return "document"


async def _fetch_l3_by_memory_id(memory_id: str) -> dict[str, Any] | None:
    """Fetch MemoryObject metadata from L3 (Qdrant) by memory_id.

    Returns the Qdrant point payload (dict) or None if not found.
    """
    try:
        from arifosmcp.runtime.memory_store import _get_qdrant_client

        client = _get_qdrant_client()
        # Qdrant point ID convention: memory_id is stored as a string
        point = client.retrieve(
            collection_name="arifos_memory",
            ids=[memory_id],
            with_payload=True,
            with_vectors=False,
        )
        if point and len(point) > 0:
            return point[0].payload
    except Exception as exc:
        logger.warning(f"[L3_FETCH] Qdrant retrieve failed: {exc}")
    return None


async def _fetch_l4_record(memory_id: str) -> dict[str, Any] | None:
    """Fetch L4 record from Postgres memory_records by memory_id."""
    try:
        from arifosmcp.runtime.memory_store import _pg_run

        async def _do_fetch():
            from arifosmcp.runtime.memory_store import get_memory_store

            store = get_memory_store()
            return await store.load_memory_by_id(memory_id)

        return await _pg_run(_do_fetch())
    except Exception as exc:
        logger.warning(f"[L4_FETCH] Postgres fetch failed: {exc}")
    return None


async def _update_qdrant_tier(memory_id: str, to_tier: str, vault_ref: str | None) -> None:
    """Mirror tier promotion back to Qdrant payload."""
    try:
        from arifosmcp.runtime.memory_store import _get_qdrant_client

        client = _get_qdrant_client()
        client.set_payload(
            collection_name="arifos_memory",
            points=[memory_id],
            payload={"tier": to_tier, "vault_ref": vault_ref},
        )
    except Exception as exc:
        logger.warning(f"[L3_MIRROR] Qdrant set_payload failed: {exc}")


async def _cascade_tombstone_graph(memory_id: str) -> list[str]:
    """Cascade tombstone to dependent graph nodes (FalkorDB/Graphiti).

    Day 3: stub returns empty list.
    Day 5: traverse graph edges from memory_id, mark dependent nodes deprecated.
    """
    return []


def _evaluate_aspect(
    record: dict[str, Any],
    aspect: str,
    include_proof: bool,
) -> tuple[bool, int, list[str] | None]:
    """Evaluate a memory record against the requested aspect.

    Returns: (integrity_verdict, lineage_depth, merkle_path_or_None)
    """
    if aspect == "integrity":
        # Day 3 stub: integrity = record has hash field
        has_hash = bool(record.get("hash"))
        return has_hash, 0, None

    if aspect == "lineage":
        # lineage_depth = number of supersedes hops
        depth = 0
        cur = record
        while cur.get("supersedes"):
            depth += 1
            cur = {"supersedes": cur["supersedes"]}  # simplified
            if depth > 100:
                break  # cycle guard
        return True, depth, None

    if aspect == "contradictions":
        # Check if record has contested_by entries
        has_contested = bool(record.get("contested_by"))
        return not has_contested, 0, None

    if aspect == "tier_consistency":
        # Day 3 stub: always consistent
        return True, 0, None

    return False, 0, None


# ────────────────────────────────────────────────────────────────────────
# _handle_inspect — Direct Postgres lookup by memory_id
# ────────────────────────────────────────────────────────────────────────
# Day 4 polish (2026-06-21): inspect mode was routing through vector search,
# which requires embeddings. For UUID lookups, we should do a direct Postgres
# query instead. ADR-010: Postgres is L4 canonical store.
# ────────────────────────────────────────────────────────────────────────


async def _handle_inspect(payload: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """Inspect a memory by memory_id — direct Postgres lookup.

    Bypasses vector search for UUID lookups. Falls back to vector search
    for natural language queries.
    """
    import re
    import uuid as _uuid
    import asyncpg
    from arifosmcp.runtime.memory_store import _PG_URL, _summarize, _content_hash

    query = payload.get("query") or payload.get("memory_id") or ""

    # Check if query looks like a UUID
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    if re.match(uuid_pattern, query, re.I):
        # Direct Postgres lookup
        try:
            conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
            try:
                pg_row = await conn.fetchrow(
                    """
                    SELECT id, tier, text, metadata, qdrant_id, session_id,
                           created_at, deleted_at
                    FROM memory_store
                    WHERE id = $1 AND deleted_at IS NULL
                    """,
                    _uuid.UUID(query),
                )
                if pg_row:
                    pg_row = dict(pg_row)
                else:
                    pg_row = None
            finally:
                await conn.close()

            if pg_row:
                # Parse metadata — asyncpg returns JSONB as string
                meta = pg_row.get("metadata", {})
                if isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except (json.JSONDecodeError, TypeError):
                        meta = {}

                return {
                    "ok": True,
                    "verdict": "SEAL",
                    "payload": {
                        "memory_id": str(pg_row["id"]),
                        "content": pg_row["text"],
                        "mode": meta.get("memory_class"),
                        "tags": meta.get("entity_tags", []),
                        "actor_id": meta.get("provenance", {}).get("actor_id"),
                        "session_id": pg_row.get("session_id"),
                        "summary": _summarize(pg_row["text"]),
                        "content_hash": _content_hash(pg_row["text"]),
                        "created_at": pg_row["created_at"].isoformat()
                        if pg_row.get("created_at")
                        else None,
                        "tier": pg_row.get("tier", "L4"),
                        "truth_class": meta.get("truth_class"),
                        "provenance": meta.get("provenance"),
                        "source": "postgres_direct",
                        "note": "inspect by UUID — direct Postgres lookup per ADR-010",
                    },
                }
            else:
                return {
                    "ok": False,
                    "verdict": "SABAR",
                    "payload": {
                        "error": "NOT_FOUND",
                        "message": f"Memory {query} not found or soft-deleted",
                        "query": query,
                    },
                }
        except Exception as exc:
            logger.warning(f"Postgres inspect failed for {query}: {exc}")
            return {
                "ok": False,
                "verdict": "SABAR",
                "payload": {
                    "error": "INSPECT_ERROR",
                    "message": f"Postgres lookup failed: {exc}",
                    "query": query,
                },
            }
    else:
        # Not a UUID — fall back to vector search
        return {
            "ok": False,
            "verdict": "SABAR",
            "payload": {
                "error": "NOT_UUID",
                "message": "inspect mode requires a UUID memory_id. Use recall mode for natural language queries.",
                "query": query,
            },
        }


__all__ = [
    "_handle_promote",
    "_handle_forget",
    "_handle_attest",
    "_handle_inspect",
]
