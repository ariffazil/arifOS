"""
arifosmcp/intelligence/tools/vector_bridge.py — INGEST Bridge (114_INGEST)
═══════════════════════════════════════════════════════════════════════════════

SEALTRIWITNESS Phase 2: Real vector auto-sync bridge.

Bridges EvidenceBundle from reality_handlers (SENSE) to memory_store (555_MEMORY).

Architecture:
    RealityHandler.handle_compass() creates EvidenceBundle
        ↓ (fire-and-forget asyncio.create_task)
        ↓ auto_sync_bundle(bundle, session_id, actor_id)
        ↓ this bridge
        ↓ ingest_evidence_bundle(bundle, dry_run=True)
        ↓ memory_store.store() [dual-write: Qdrant + Postgres]
        ↓ IngestResult returned

Governing rules:
    No observation without receipt.  (F2 TRUTH)
    No receipt without bundle.      (F3 WITNESS)
    No bundle without optional ingest. (F1 AMANAH)
    No ingest without idempotency.   (data integrity)
    No permanent write in dry_run.   (F1 reversibility)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime

from arifosmcp.schemas.evidence_bundle import (
    CanonicalEvidenceBundle,
    IngestResult,
    IngestStatus,
)

logger = logging.getLogger(__name__)

# ── Optional dependency guard ────────────────────────────────────────────────

MEMORY_STORE_AVAILABLE = False
_memory_store = None

try:
    from arifosmcp.runtime.memory_store import store as _store_fn

    _memory_store = _store_fn
    MEMORY_STORE_AVAILABLE = True
except ImportError:
    MEMORY_STORE_AVAILABLE = False
    _memory_store = None


# ── Idempotency check ────────────────────────────────────────────────────────


def _check_idempotency(idempotency_key: str | None) -> tuple[bool, str | None]:
    """
    Check if a bundle with this idempotency key was already ingested.

    Returns (already_exists, existing_memory_id).

    NOTE: Full idempotency dedup requires a Postgres lookup. This is a
    lightweight in-memory check stub. For production, query the
    memory_store.pg_connection directly with:
        SELECT memory_id FROM memory_store WHERE metadata_->>'idempotency_key' = $1

    Returns (False, None) when idempotency_key is None or
    MEMORY_STORE_AVAILABLE is False.
    """
    if not idempotency_key or not MEMORY_STORE_AVAILABLE:
        return False, None

    # Lazy import to avoid circular dependency at import time
    try:
        import json as _json
        from pathlib import Path as _Path

        index_file = _Path.home() / ".arifOS" / "memory" / ".qdrant_index.json"
        if not index_file.exists():
            return False, None

        idx = _json.loads(index_file.read_text())
        for memory_id, record in idx.items():
            meta = record.get("metadata", {})
            if meta.get("idempotency_key") == idempotency_key:
                return True, memory_id
        return False, None
    except Exception:
        # If index read fails, do not block ingestion — proceed with write
        return False, None


# ── Core ingest function ────────────────────────────────────────────────────


async def ingest_evidence_bundle(
    bundle: CanonicalEvidenceBundle,
    *,
    dry_run: bool = True,
    tier: str = "session",
    authorized: bool = False,
    session_verified: bool = False,
    sovereign_ack: bool = False,
) -> IngestResult:
    """
    Persist an EvidenceBundle to memory (Qdrant + Postgres dual-write).

    Authorization gates (ALL must be True for permanent write):
        dry_run=False  AND
        authorized=True  AND
        session_verified=True  AND
        sovereign_ack=True

    Args:
        bundle: CanonicalEvidenceBundle to persist.
        dry_run: If True, simulate write without permanent storage. Default True.
                 Set to False only after explicit authorization.
        tier: Memory tier to use. Options: sacred, canon, session, ephemeral.
              Default: session (24h TTL).
        authorized: Caller explicitly authorized the write. Default False.
        session_verified: Session is verified (not anonymous/global). Default False.
        sovereign_ack: Human sovereign acknowledged the write. Default False.

    Returns:
        IngestResult with status, memory_id, backend write results, auth fields.

    Governing principle:
        No permanent write unless ALL authorization gates are True.
    """
    result = IngestResult(
        bundle_id=bundle.bundle_id,
        dry_run=dry_run,
        authorized=authorized,
        session_verified=session_verified,
        sovereign_ack=sovereign_ack,
        idempotency_key=bundle.idempotency_key,
        timestamp_utc=datetime.now(UTC).isoformat(),
    )

    # ── Authorization gate check ────────────────────────────────────────
    auth_gates_met = not dry_run and authorized and session_verified and sovereign_ack
    if not auth_gates_met and not dry_run:
        # Permanent write requested but not all gates are True
        result.status = IngestStatus.BLOCKED_AUTH_REQUIRED
        reasons = []
        if dry_run:
            reasons.append("dry_run=True")
        if not authorized:
            reasons.append("authorized=False")
        if not session_verified:
            reasons.append("session_verified=False")
        if not sovereign_ack:
            reasons.append("sovereign_ack=False")
        result.blocked_reason = "; ".join(reasons)
        sys.stderr.write(
            f"[vector_bridge] BLOCK_AUTH bundle {bundle.bundle_id} — {result.blocked_reason}\n"
        )
        return result

    # ── Empty bundle guard ───────────────────────────────────────────────
    if not bundle.query and not bundle.claims:
        sys.stderr.write(
            f"[vector_bridge] SKIP empty bundle {bundle.bundle_id} — no query, no claims\n"
        )
        result.status = IngestStatus.SKIPPED
        return result

    # ── Ensure idempotency key ─────────────────────────────────────────
    bundle.ensure_idempotency_key()
    key_for_log = (bundle.idempotency_key or "")[:8] if bundle.idempotency_key else "none"
    result.idempotency_key = bundle.idempotency_key

    # ── Idempotency pre-check ──────────────────────────────────────────
    already_exists, existing_memory_id = _check_idempotency(bundle.idempotency_key)
    if already_exists:
        sys.stderr.write(
            f"[vector_bridge] SKIP idempotent bundle {bundle.bundle_id} "
            f"(key={key_for_log}..., memory_id={existing_memory_id})\n"
        )
        result.status = IngestStatus.SKIPPED
        result.memory_id = existing_memory_id
        return result

    # ── Memory store write ─────────────────────────────────────────────
    if not MEMORY_STORE_AVAILABLE or _memory_store is None:
        result.status = IngestStatus.FAILED
        result.error = "memory_store unavailable"
        sys.stderr.write(
            f"[vector_bridge] FAIL bundle {bundle.bundle_id} — memory_store not importable\n"
        )
        return result

    if dry_run:
        sys.stderr.write(
            f"[vector_bridge] DRY_RUN bundle {bundle.bundle_id} "
            f"(key={key_for_log}..., session={bundle.session_id})\n"
        )
        result.status = IngestStatus.SKIPPED
        result.bundle_id = bundle.bundle_id
        # Still return what WOULD be written
        return result

    # ── Real write ─────────────────────────────────────────────────────
    try:
        memory_content = bundle.to_memory_content()

        # _memory_store is guaranteed non-None here (MEMORY_STORE_AVAILABLE check above)
        store_result = _memory_store(  # type: ignore[operator]
            content=memory_content,
            mode="evidence_ingest",
            tags=["evidence", "sense", bundle.provider, bundle.evidence_level.value],
            actor_id=bundle.actor_id,
            session_id=bundle.session_id,
            summary=f"[{bundle.evidence_level.value}] {bundle.query[:120]}",
            tier=tier,
        )

        result.memory_id = store_result.get("memory_id")
        result.qdrant_written = store_result.get("backends", {}).get("qdrant", False)
        result.postgres_written = store_result.get("backends", {}).get("postgres", False)
        result.status = result.compute_status()

        # Phase 2: Recall verification — prove the bundle can be retrieved
        if result.memory_id and result.status in (
            IngestStatus.SUCCESS,
            IngestStatus.PARTIAL_SUCCESS,
        ):
            result.recall_verified = await _verify_recall(result.memory_id, bundle.bundle_id)

        sys.stderr.write(
            f"[vector_bridge] WROTE bundle {bundle.bundle_id} "
            f"→ memory_id={result.memory_id} "
            f"qdrant={result.qdrant_written} "
            f"pg={result.postgres_written} "
            f"recall={result.recall_verified}\n"
        )

    except Exception as exc:
        logger.error("Ingest failed for bundle %s: %s", bundle.bundle_id, exc)
        result.status = IngestStatus.FAILED
        result.error = str(exc)
        result.backend_errors = {"memory_store": str(exc)}
        sys.stderr.write(f"[vector_bridge] FAIL bundle {bundle.bundle_id}: {exc}\n")

    return result


async def _verify_recall(memory_id: str, bundle_id: str) -> bool:
    """
    Phase 2: Verify a written bundle can be recalled by memory_id.

    Returns True if recall succeeds, False otherwise.
    Best-effort — recall failure does NOT fail the ingest, but IS recorded.
    """
    try:
        from arifosmcp.runtime.memory_store import recall as _recall_fn

        recalled = _recall_fn(memory_id)
        if recalled and recalled.get("memory_id") == memory_id:
            sys.stderr.write(
                f"[vector_bridge] RECALL_OK memory_id={memory_id} bundle_id={bundle_id}\n"
            )
            return True
        sys.stderr.write(
            f"[vector_bridge] RECALL_MISMATCH memory_id={memory_id} bundle_id={bundle_id}\n"
        )
        return False
    except Exception as exc:
        sys.stderr.write(
            f"[vector_bridge] RECALL_FAIL memory_id={memory_id} bundle_id={bundle_id}: {exc}\n"
        )
        return False


# ── Legacy auto_sync_bundle interface (called from reality_handlers) ─────────


async def auto_sync_bundle(
    bundle,
    *,
    session_id: str | None = None,
    actor_id: str | None = None,
    dry_run: bool = True,
    authorized: bool = False,
    session_verified: bool = False,
    sovereign_ack: bool = False,
) -> IngestResult:
    """
    Bridge from RealityHandler.handle_compass() to ingest_evidence_bundle().

    This is the function imported by reality_handlers.py:
        from ..intelligence.tools.vector_bridge import auto_sync_bundle

    Authorization gates (ALL must be True for permanent write):
        dry_run=False  AND
        authorized=True  AND
        session_verified=True  AND
        sovereign_ack=True

    Args:
        bundle: EvidenceBundle from reality_models.py (runtime/reality_models.py)
        session_id: Session context — overrides bundle.session_id if provided.
        actor_id: Actor context — overrides bundle.actor_id if provided.
        dry_run: If True, no permanent write. Default True (F1 reversibility).
        authorized: Caller explicitly authorized the write. Default False.
        session_verified: Session is verified (not anonymous/global). Default False.
        sovereign_ack: Human sovereign acknowledged the write. Default False.

    Returns:
        IngestResult describing what was (or would be) written.
    """
    # ── Coerce runtime/reality_models EvidenceBundle → CanonicalEvidenceBundle
    if isinstance(bundle, CanonicalEvidenceBundle):
        canonical = bundle
    else:
        # Runtime EvidenceBundle from reality_models.py — adapt fields
        from arifosmcp.runtime.reality_models import Actor

        actor_obj = getattr(bundle, "actor", None)
        bundle_input = getattr(bundle, "input", None)
        bundle_status = getattr(bundle, "status", None)
        bundle_provenance = getattr(bundle, "provenance", {})

        # Extract errors as string list from BundleStatus.errors
        error_strings: list[str] = []
        if bundle_status is not None:
            status_errors = getattr(bundle_status, "errors", []) or []
            error_strings = [
                getattr(e, "code", str(e)) if hasattr(e, "code") else str(e) for e in status_errors
            ]

        canonical = CanonicalEvidenceBundle(
            bundle_id=getattr(bundle, "id", f"eb-{session_id or 'unknown'[:8]}"),
            session_id=session_id
            or (getattr(actor_obj, "actor_id", None) if isinstance(actor_obj, Actor) else None)
            or "global",
            actor_id=actor_id or "anonymous",
            query=(getattr(bundle_input, "value", "") if bundle_input is not None else ""),
            mode=(
                getattr(bundle_input, "mode", "search") if bundle_input is not None else "search"
            ),
            provider=(
                bundle_provenance.get("engine", "unknown")
                if isinstance(bundle_provenance, dict)
                else "unknown"
            ),
            void_flags=error_strings,
        )

    # Override session/actor if explicitly provided
    if session_id:
        canonical.session_id = session_id
    if actor_id:
        canonical.actor_id = actor_id

    # ── Phase 3: Extract entities + relations from search results ───────────────
    # Only extract when we have real search results (not when already Canonical)
    if not isinstance(bundle, CanonicalEvidenceBundle):
        bundle_results = getattr(bundle, "results", None) or []
        if bundle_results:
            try:
                # Lazy import to avoid circular dependency
                from arifosmcp.intelligence.tools.relate_bridge import extract_graph

                entities, relations = await extract_graph(
                    bundle_results=bundle_results,
                    query=canonical.query,
                    session_id=canonical.session_id,
                )
                if entities:
                    canonical.entities = entities
                    sys.stderr.write(
                        f"[vector_bridge] RELATE extracted {len(entities)} entities, "
                        f"{len(relations)} relations for bundle {canonical.bundle_id}\n"
                    )
                if relations:
                    canonical.relations = relations
            except Exception as rel_err:
                # Non-fatal: entity extraction failure should not block ingest
                sys.stderr.write(
                    f"[vector_bridge] RELATE extraction failed (non-fatal): {rel_err}\n"
                )

    canonical.ensure_idempotency_key()

    return await ingest_evidence_bundle(
        canonical,
        dry_run=dry_run,
        authorized=authorized,
        session_verified=session_verified,
        sovereign_ack=sovereign_ack,
    )
