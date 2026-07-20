"""
arifosmcp/tools/vault_vectorizer.py — PRL Phase 1: Vector Index for VAULT999

Precedent Retrieval Layer: Every seal becomes a 1024-dim vector in Qdrant.
Payload-filtered by blast_radius for compartmentalised precedent matching.

Collection: arifos_precedent (COSINE distance, 1024-dim BGE-M3 compatible)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import time
from datetime import UTC, datetime
from typing import Any

from arifosmcp.intelligence.embeddings import embed

logger = logging.getLogger(__name__)

PRL_COLLECTION = "arifos_precedent"
PRL_VECTOR_DIM = 1024

_QDRANT_CLIENT: Any = None


def _get_qdrant() -> Any:
    """Return QdrantClient or None if unreachable.  Lazy init with health check."""
    global _QDRANT_CLIENT
    if _QDRANT_CLIENT is not None:
        return _QDRANT_CLIENT
    try:
        from qdrant_client import QdrantClient  # noqa: PLC0415

        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        client = QdrantClient(url=qdrant_url, timeout=5)
        client.get_collections()
        _QDRANT_CLIENT = client
        return client
    except Exception as exc:
        logger.debug("Qdrant unreachable for PRL: %s", exc)
        return None


def _ensure_collection() -> bool:
    """Create arifos_precedent collection if absent.  Returns True if ready."""
    client = _get_qdrant()
    if client is None:
        return False
    try:
        from qdrant_client.models import Distance, VectorParams  # noqa: PLC0415

        existing = {c.name for c in client.get_collections().collections}
        if PRL_COLLECTION not in existing:
            client.create_collection(
                collection_name=PRL_COLLECTION,
                vectors_config=VectorParams(
                    size=PRL_VECTOR_DIM,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(
                "Created Qdrant PRL collection: %s (%d-dim COSINE)",
                PRL_COLLECTION,
                PRL_VECTOR_DIM,
            )
        return True
    except Exception as exc:
        logger.error("Failed to ensure PRL collection: %s", exc)
        return False


def vectorize_seal(
    entry_id: str,
    payload_text: str,
    blast_radius: str = "L2_SYSTEM",
    session_id: str | None = None,
) -> bool:
    """Embed a seal payload and store it in the Qdrant precedent index.

    Called as a post-seal hook from vault.py after every successful arif_seal.
    Non-fatal — seal already succeeded; index failure is logged but does not
    block the seal.

    Args:
        entry_id: VAULT999 entry ID for this seal
        payload_text: Human-readable seal payload (judged content)
        blast_radius: PRL consequence tier (L1_LOCAL | L2_SYSTEM | L3_CRITICAL)
        session_id: Governing session ID

    Returns:
        True if vector was stored, False if Qdrant was unreachable
    """
    if not _ensure_collection():
        logger.warning("PRL: Qdrant unavailable — seal %s not indexed", entry_id)
        return False

    client = _get_qdrant()
    if client is None:
        return False

    try:
        from qdrant_client.models import PointStruct  # noqa: PLC0415

        # Build semantic summary for embedding
        summary_text = f"[ENTRY_ID:{entry_id}] [BLAST_RADIUS:{blast_radius}] {payload_text[:500]}"
        vector = embed(summary_text, dim=PRL_VECTOR_DIM)
        timestamp = datetime.now(UTC).isoformat()

        client.upsert(
            collection_name=PRL_COLLECTION,
            points=[
                PointStruct(
                    id=entry_id,
                    vector=vector,
                    payload={
                        "entry_id": entry_id,
                        "blast_radius": blast_radius,
                        "session_id": session_id or "",
                        "timestamp": timestamp,
                        "payload_summary": payload_text[:500],
                    },
                )
            ],
        )
        logger.info(
            "PRL: vectorized seal %s (blast_radius=%s, %d chars)",
            entry_id,
            blast_radius,
            len(payload_text),
        )
        return True
    except Exception as exc:
        logger.error("PRL: vectorize_seal failed for %s: %s", entry_id, exc)
        return False


def _embed_with_retry(text: str, dim: int, max_retries: int = 4) -> list[float]:
    """Embed text with exponential backoff retry for Ollama timeouts.

    Handles 408 (Timeout) and 503 (Service Unavailable) from local Ollama.
    Exponential backoff: 2s → 4s → 8s → 16s.

    Args:
        text: Text to embed.
        dim: Target vector dimension.
        max_retries: Maximum retry attempts (default 4).

    Returns:
        Vector as list[float].

    Raises:
        RuntimeError if all retries exhausted.
    """
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return embed(text, dim=dim)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                wait = 2 ** (attempt + 1)  # 2, 4, 8, 16 seconds
                logger.warning(
                    "PRL embed retry %d/%d after %.1fs: %s",
                    attempt + 1,
                    max_retries,
                    wait,
                    exc,
                )
                time.sleep(wait)
    raise RuntimeError(f"Embed failed after {max_retries} retries: {last_error}")


def _infer_category(action: str, metadata: dict[str, Any] | None = None) -> str:
    """Derive a domain category from the action string using structural heuristics.

    This allows sparse historical seals (which lack explicit category tags)
    to be enriched with meaningful domain classifications for PRL matching.
    """
    meta = metadata or {}
    action_lower = str(action).lower()

    # surface_gate patterns
    if any(kw in action_lower for kw in ("surface_gate", "surface.pin", "surface.lock", "surface_gate.pin")):
        return "security.surface_control"

    # vector / qdrant patterns
    if any(kw in action_lower for kw in ("vector", "qdrant", "embed", "upsert", "index", "collection")):
        return "database.vector_index"

    # EMD / PRL patterns
    if any(kw in action_lower for kw in ("emd", "prl", "gate", "precedent", "encode", "metabolize", "intercept")):
        return "architecture.emd_pipeline"

    # file / forge / mutation patterns
    if any(kw in action_lower for kw in ("file_write", "forge", "mutate", "patch", "commit", "deploy")):
        return "system.code_generation"

    # session / init patterns
    if any(kw in action_lower for kw in ("init", "session", "arif_init", "bootstrap", "handshake")):
        return "governance.session_lifecycle"

    # seal / verdict / judge patterns
    if any(kw in action_lower for kw in ("seal", "judge", "verdict", "hold", "sabar", "void")):
        return "governance.constitutional"

    # geoscience / basin / geological patterns
    if any(kw in action_lower for kw in ("geox", "basin", "seismic", "well", "geolog", "petrophys")):
        return "geoscience.earth_model"

    # capital / wealth patterns
    if any(kw in action_lower for kw in ("wealth", "capital", "npv", "irr", "trade", "portfolio")):
        return "finance.capital_intelligence"

    # Fallback: check metadata for hints
    tool_name = str(meta.get("tool_name", "")).lower()
    if "prl" in tool_name or "gate" in tool_name:
        return "architecture.emd_pipeline"
    if "vector" in tool_name or "qdrant" in tool_name:
        return "database.vector_index"

    return "UNCATEGORIZED"


def _synthesize_vector_text(entry: dict[str, Any]) -> str:
    """Build a semantically dense document for BGE-M3 embedding.

    Extracts signal from seal mechanics WITHOUT modifying the vault ledger.
    The derived text is what gets embedded; the original JSON stays
    in the Qdrant payload for audit.

    Returns a multi-line structured document optimized for cosine matching.
    """
    payload = entry.get("payload", {})
    if isinstance(payload, str):
        try:
            import json as _json
            payload = _json.loads(payload)
        except Exception:
            payload = {}

    # Extract core fields
    action = str(payload.get("action", entry.get("action", entry.get("event", ""))))
    verdict = str(entry.get("verdict", payload.get("verdict", "SEAL")))
    blast_radius = str(entry.get("blast_radius", payload.get("blast_radius", "L2_SYSTEM")))
    actor = str(entry.get("actor", payload.get("actor", entry.get("actor_id", payload.get("actor_id", "")))))
    category = str(entry.get("category", payload.get("category", payload.get("domain", ""))))

    # Metadata — the WHY
    metadata = payload.get("metadata", {})
    if isinstance(metadata, str):
        try:
            import json as _json
            metadata = _json.loads(metadata)
        except Exception:
            metadata = {}

    # Infer category if missing
    if not category or category in ("UNCATEGORIZED", ""):
        category = _infer_category(action, metadata)

    # Extract contextual signals from metadata
    context_parts = []
    for key in ("reason", "query", "tool_name", "target_file", "rule_override", "intent"):
        val = metadata.get(key, entry.get(key, payload.get(key, "")))
        if val and str(val).strip():
            context_parts.append(f"{key}: {str(val)[:200]}")

    # If no metadata context, try top-level reason/description
    if not context_parts:
        reason = str(entry.get("reason", payload.get("reason", payload.get("description", ""))))
        if reason:
            context_parts.append(f"reason: {reason[:300]}")

    context_str = " | ".join(context_parts) if context_parts else "no_context_available"

    # Build the dense semantic document
    dense_text = (
        f"Domain Category: {category}\n"
        f"Execution Action: {action}\n"
        f"Operational Context: {context_str}\n"
        f"Blast Radius Authority: {blast_radius}\n"
        f"Institutional Verdict: {verdict}\n"
        f"Actor: {actor}"
    )
    return dense_text


def _build_enriched_payload(
    entry: dict[str, Any],
    entry_id: str,
    blast_radius: str,
    session_id: str,
    derived_text: str,
    raw_json: str,
) -> dict[str, Any]:
    """Build the enhanced Qdrant payload with derived semantic fields.

    The original seal data is preserved under 'raw_payload'. Derived fields
    (enriched_category, derived_semantic_text, is_derived) allow prl_gate.py
    to inject high-density context into the EMD pipeline.
    """
    payload = entry.get("payload", {})
    if isinstance(payload, str):
        try:
            import json as _json
            payload = _json.loads(payload)
        except Exception:
            payload = {}

    action = str(payload.get("action", entry.get("action", "")))
    category = str(entry.get("category", payload.get("category", "")))
    if not category or category == "UNCATEGORIZED":
        category = _infer_category(action, payload.get("metadata", {}))

    actor = str(entry.get("actor", payload.get("actor", entry.get("actor_id", ""))))
    verdict = str(entry.get("verdict", payload.get("verdict", "SEAL")))
    vault_seq = entry.get("seq", entry.get("entry_id", ""))
    vault_hash = entry.get("sha256_hash", entry.get("hash", ""))

    return {
        "entry_id": entry_id,
        "blast_radius": blast_radius,
        "session_id": session_id or "",
        "timestamp": datetime.now(UTC).isoformat(),
        "payload_summary": raw_json[:500],
        # ── Derived semantic fields (P6 enrichment) ──
        "vault_seq": str(vault_seq),
        "vault_hash": str(vault_hash),
        "raw_verdict": verdict,
        "enriched_category": category,
        "derived_semantic_text": derived_text,
        "actor": actor,
        "is_derived": True,
    }


def backfill_historical(
    vault_dir: str | None = None,
    default_blast_radius: str = "L2_SYSTEM",
    batch_size: int = 10,
    batch_cooldown: float = 3.0,
    show_progress: bool = True,
) -> dict[str, Any]:
    """Read existing VAULT999 entries and index them into the PRL Qdrant collection.

    Processes entries in batches with cooldown between batches to avoid
    overwhelming local Ollama embedding queues.  Uses exponential-backoff
    retry for transient Ollama failures (408/503).

    Safe default blast_radius = L2_SYSTEM for unclassified historical seals.
    Skips entries already in the index (idempotent).

    Args:
        vault_dir: Path to VAULT999 directory.  Defaults to canonical location.
        default_blast_radius: Blast radius to assign to backfilled entries.
        batch_size: Entries to process per batch (default 10).
        batch_cooldown: Seconds to wait between batches (default 3.0).
        show_progress: Print progress to stderr (default True).

    Returns:
        Dict with {indexed, skipped, errors, total, batches, elapsed_s, status}
    """
    if vault_dir is None:
        vault_dir = os.environ.get(
            "VAULT999_PATH",
            "/root/.local/share/arifos/vault999",
        )

    if not _ensure_collection():
        return {
            "indexed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "batches": 0,
            "elapsed_s": 0.0,
            "status": "QDRANT_DOWN",
        }

    client = _get_qdrant()
    if client is None:
        return {
            "indexed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "batches": 0,
            "elapsed_s": 0.0,
            "status": "QDRANT_DOWN",
        }

    import json
    import uuid
    from pathlib import Path

    from qdrant_client.models import PointStruct  # noqa: PLC0415

    vault_path = Path(vault_dir)
    seal_chain_path = vault_path / "seal_chain.jsonl"

    entries: list[dict[str, Any]] = []

    # Read seal_chain.jsonl ONLY (canonical sealed entries).
    # outcomes.jsonl is the legacy format — skip to avoid format divergence.
    for source_path in (seal_chain_path,):
        if not source_path.exists():
            continue
        try:
            with open(source_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if isinstance(entry, dict):
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as exc:
            logger.warning("PRL backfill: failed to read %s: %s", source_path, exc)

    if not entries:
        return {
            "indexed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "batches": 0,
            "elapsed_s": 0.0,
            "status": "NO_ENTRIES",
        }

    # Get existing point IDs to skip already-indexed entries
    try:
        existing_ids: set[str] = set()
        scroll_result = client.scroll(
            collection_name=PRL_COLLECTION,
            limit=10_000,
            with_payload=False,
            with_vectors=False,
        )
        for point in scroll_result[0] or []:
            existing_ids.add(str(point.id))
    except Exception:
        existing_ids = set()

    indexed = 0
    skipped = 0
    errors = 0

    start_time = time.monotonic()

    # Process entries in batches to avoid overwhelming local Ollama
    total_entries = len(entries)
    batch_count = (total_entries + batch_size - 1) // batch_size

    for batch_idx in range(batch_count):
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + batch_size, total_entries)
        batch_entries = entries[batch_start:batch_end]

        if show_progress:
            print(
                f"\r[PRL BACKFILL] batch {batch_idx + 1}/{batch_count} "
                f"({batch_start + 1}-{batch_end} of {total_entries}) "
                f"| indexed={indexed} skipped={skipped} errors={errors}",
                end="",
                flush=True,
            )

        for entry in batch_entries:
            raw_id = entry.get("entry_id", entry.get("seq", ""))
            if raw_id is None or raw_id == "":
                errors += 1
                continue

            # Qdrant requires UUIDs or unsigned ints.  Convert int seqs
            # to deterministic UUIDs so the same VAULT999 entry always
            # maps to the same Qdrant point.
            entry_id = str(raw_id)
            try:
                qdrant_point_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"vault999:{entry_id}"))
            except Exception:
                errors += 1
                continue

            if qdrant_point_id in existing_ids:
                skipped += 1
                continue

            payload_text = json.dumps(entry, sort_keys=True, default=str)
            derived_text = _synthesize_vector_text(entry)
            enriched_payload = _build_enriched_payload(
                entry, entry_id, default_blast_radius,
                str(entry.get("session_id", "")), derived_text, payload_text,
            )
            try:
                # Embed the DERIVED SEMANTIC DOCUMENT, not the raw JSON
                vector = _embed_with_retry(derived_text, dim=PRL_VECTOR_DIM)

                timestamp = datetime.now(UTC).isoformat()
                client.upsert(
                    collection_name=PRL_COLLECTION,
                    points=[
                        PointStruct(
                            id=qdrant_point_id,
                            vector=vector,
                            payload=enriched_payload,
                        )
                    ],
                )
                indexed += 1
                existing_ids.add(qdrant_point_id)
            except Exception as exc:
                logger.error("PRL backfill: failed for %s: %s", entry_id, exc)
                errors += 1

        # Cooldown between batches — lets Ollama queue clear
        if batch_idx < batch_count - 1:
            time.sleep(batch_cooldown)

    elapsed = time.monotonic() - start_time

    if show_progress:
        print()  # newline after progress line
        print(
            f"[PRL BACKFILL] DONE: {indexed} indexed, {skipped} skipped, "
            f"{errors} errors of {total_entries} total "
            f"in {elapsed:.1f}s ({batch_count} batches)"
        )

    return {
        "indexed": indexed,
        "skipped": skipped,
        "errors": errors,
        "total": total_entries,
        "batches": batch_count,
        "elapsed_s": round(elapsed, 1),
        "status": "OK" if errors == 0 else "PARTIAL",
    }


def prl_post_seal_hook(
    entry_id: str,
    payload: str,
    blast_radius: str = "L2_SYSTEM",
    session_id: str | None = None,
) -> bool:
    """Post-seal hook: vectorize the seal payload into the PRL index.

    Called from vault.py after every successful arif_seal.
    Non-fatal — seal already succeeded.
    """
    return vectorize_seal(
        entry_id=entry_id,
        payload_text=payload,
        blast_radius=blast_radius,
        session_id=session_id,
    )


__all__ = [
    "vectorize_seal",
    "backfill_historical",
    "prl_post_seal_hook",
    "PRL_COLLECTION",
]
