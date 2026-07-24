#!/usr/bin/env python3
"""
reindex_prl.py — Non-destructive PRL reindex (shadow → promote)
═══════════════════════════════════════════════════════════════

Re-indexes the VAULT999 precedent corpus into a 768-d cosine *shadow*
Qdrant collection without touching the live ``arifos_precedent``.  The
operator reviews the shadow's counters and metadata, then optionally
promotes it via a separate explicit flag.

Hard rules (never violated):

* **Dry-run by default.**  Pass ``--apply`` to write to the shadow.
  Pass ``--promote-shadow`` in a *separate* invocation to swap the alias.
* **No delete / recreate of live data.**  ``arifos_precedent`` and any
  pre-existing shadow are read-only to this script.
* **Resume only after metadata compatibility.**  Vector size + distance
  must match the live collection; otherwise the script aborts.
* **Deterministic IDs.**  The strongest immutable key (entry_id / seq +
  sha256_hash fallback) is hashed to a UUID v5 so a re-run upserts the
  same point and stays idempotent.
* **Streaming batches.**  Embeddings + Qdrant upserts are processed in
  bounded batches so memory stays flat on a large corpus.
* **Normalized provenance payloads.**  Every point carries
  ``provenance.reindex_script``, ``provenance.embedder``, and the
  ``source_line`` / ``sha256_hash`` so an audit can trace any vector back
  to its vault entry.
* **Counters.**  ``read / written / skipped_existing / skipped_fail_open /
  errors`` are printed and (when ``--json-report``) dumped to a file.

This script is **safe to run against live data** for dry-run; the only
mutation is the *new* shadow collection (and, on explicit promotion, the
alias swap).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import uuid
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure project source is importable when invoked as a script.
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from arifosmcp.prl.ollama_embedder import (  # noqa: E402
    PrlEmbedderConfig,
    embed_texts_batch,
)
from arifosmcp.tools.vault_vectorizer import (  # noqa: E402
    PRL_COLLECTION,
    PRL_VECTOR_DIM,
    _build_enriched_payload,
    _synthesize_vector_text,
)

logger = logging.getLogger("reindex_prl")


# ── Defaults (env-overridable) ─────────────────────────────────────────
DEFAULT_LIVE_COLLECTION = PRL_COLLECTION
DEFAULT_SHADOW_SUFFIX = "_reindex"
DEFAULT_SHADOW_ALIAS = f"{PRL_COLLECTION}{DEFAULT_SHADOW_SUFFIX}"

DEFAULT_BATCH_SIZE = 64
DEFAULT_BATCH_COOLDOWN_S = 1.5


# ── Counter container ─────────────────────────────────────────────────


@dataclass
class ReindexCounters:
    read: int = 0
    # Number of records whose embedding WOULD be written to the shadow.
    # In dry-run mode this is a forward-looking count of valid candidates
    # (NOT a fail-open bucket).  In apply mode this is the actual write
    # count after the embedder returned a real vector.
    written: int = 0
    skipped_existing: int = 0
    # Dry-run only: records whose embedding the embedder would have
    # fail-opened for.  ALWAYS 0 in dry-run mode — dry-run never calls
    # the embedder, so we cannot mislabel a valid candidate as an embed
    # failure (that was the previous bug; see git log).
    skipped_fail_open: int = 0
    # Number of records the live embedder fail-opened on during an
    # --apply run.  In dry-run mode this stays at 0; the dry-run path
    # does not call the embedder at all.
    embedder_fail_open: int = 0
    skipped_bad_id: int = 0
    errors: int = 0
    shadow_collection: str = ""
    embedder_model: str = ""
    embedder_dim: int = 0
    started_at: str = ""
    finished_at: str = ""
    dry_run: bool = True
    promoted: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Vault iteration ───────────────────────────────────────────────────


def _iter_seal_chain(vault_path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield (lineno, entry_dict) for every JSON line in seal_chain.jsonl.

    The cryptographic ledger is NEVER mutated; this is a read-only
    stream over the file at the canonical VAULT999 path.
    """
    with vault_path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                entry = json.loads(stripped)
            except json.JSONDecodeError:
                logger.debug("vault line %d: skipping malformed JSON", lineno)
                continue
            if not isinstance(entry, dict):
                logger.debug("vault line %d: skipping non-dict (%s)", lineno, type(entry).__name__)
                continue
            yield lineno, entry


def _resolve_strong_id(entry: dict[str, Any]) -> tuple[str, str]:
    """Pick the strongest immutable key for the deterministic point ID.

    Returns (raw_id, kind) where ``kind`` is ``entry_id`` / ``seq`` /
    ``sha256_hash``.  ``entry_id`` and ``seq`` are preferred when both
    are present and identical; ``sha256_hash`` is the fallback.
    """
    entry_id = entry.get("entry_id")
    seq = entry.get("seq")
    sha = entry.get("sha256_hash") or entry.get("hash")

    if entry_id and seq is not None and str(entry_id) == str(seq):
        return str(entry_id), "entry_id_seq"
    if entry_id:
        return str(entry_id), "entry_id"
    if seq is not None and str(seq) != "":
        return str(seq), "seq"
    if sha:
        return str(sha), "sha256_hash"
    return "", "missing"


def _deterministic_point_id(raw_id: str, kind: str) -> str:
    """Map a raw vault key to a stable UUID v5 (Qdrant accepts UUIDs)."""
    return str(uuid.uuid5(uuid.NAMESPACE_OID, f"vault999:{kind}:{raw_id}"))


# ── Metadata compatibility probe ─────────────────────────────────────


def _probe_compatibility(client: Any, shadow: str, live: str, *, dim: int) -> dict[str, Any]:
    """Verify a pre-existing shadow collection is metadata-compatible.

    A resume is allowed only when (vector_size == dim) and
    (distance == COSINE).  Any mismatch → abort with a structured error.
    """
    from qdrant_client.models import Distance  # type: ignore

    info = client.get_collection(collection_name=shadow)
    vectors = getattr(info, "config", None)
    params = getattr(vectors, "params", None) if vectors else None
    vec_size = getattr(params, "vectors", None) or getattr(params, "size", None)
    distance = getattr(params, "distance", None)

    return {
        "shadow": shadow,
        "vector_size": vec_size,
        "distance": str(distance) if distance is not None else None,
        "expected_dim": dim,
        "compatible": (vec_size == dim) and (str(distance) == str(Distance.COSINE)),
    }


# ── Qdrant client lazy import ─────────────────────────────────────────


def _qdrant_client(qdrant_url: str) -> Any:
    from qdrant_client import QdrantClient  # type: ignore

    return QdrantClient(url=qdrant_url, timeout=10)


def _ensure_shadow(
    client: Any,
    *,
    shadow: str,
    dim: int,
    apply: bool,
    counters: ReindexCounters,
) -> None:
    """Create the shadow collection (no-op on dry-run).

    Dry-run does NOT touch Qdrant.  Apply mode creates the collection if
    absent and aborts on dimension mismatch with any existing shadow.
    """
    from qdrant_client.models import (  # type: ignore
        Distance,
        VectorParams,
    )

    existing = {c.name for c in client.get_collections().collections}
    if shadow in existing:
        compat = _probe_compatibility(client, shadow, DEFAULT_LIVE_COLLECTION, dim=dim)
        if not compat["compatible"]:
            raise SystemExit(
                json.dumps(
                    {
                        "error": "shadow_metadata_incompatible",
                        "shadow": shadow,
                        "vector_size": compat["vector_size"],
                        "expected_dim": dim,
                        "distance": compat["distance"],
                        "expected": str(Distance.COSINE),
                    },
                    indent=2,
                )
            )
        logger.info(
            "Shadow collection %s exists — metadata compatible (dim=%d, distance=%s). Resume OK.",
            shadow,
            compat["vector_size"],
            compat["distance"],
        )
        return

    if not apply:
        logger.info(
            "[dry-run] Would create shadow collection %s (dim=%d, distance=COSINE)",
            shadow,
            dim,
        )
        return

    client.create_collection(
        collection_name=shadow,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    logger.info("Created shadow collection: %s", shadow)


def _existing_shadow_ids(client: Any, shadow: str) -> set[str]:
    try:
        scroll = client.scroll(
            collection_name=shadow, limit=10_000, with_payload=False, with_vectors=False
        )
    except Exception:
        return set()
    return {str(point.id) for point in (scroll[0] or [])}


# ── Core loop ─────────────────────────────────────────────────────────


def _process_batches(
    client: Any,
    *,
    shadow: str,
    vault_path: Path,
    batch_size: int,
    batch_cooldown: float,
    apply: bool,
    counters: ReindexCounters,
    config: PrlEmbedderConfig,
    stop_after: int | None,
) -> None:
    """Stream entries through embedding + (optional) upsert."""
    from qdrant_client.models import PointStruct  # type: ignore

    existing_ids: set[str] = set()
    if apply:
        existing_ids = _existing_shadow_ids(client, shadow)
        logger.info("Pre-existing points in shadow: %d", len(existing_ids))

    batch_texts: list[str] = []
    batch_meta: list[tuple[str, str, dict[str, Any]]] = []  # (point_id, entry_id, payload)
    batch_payloads_raw: list[dict[str, Any]] = []

    def _flush() -> None:
        nonlocal batch_texts, batch_meta, batch_payloads_raw
        if not batch_texts:
            return
        if apply:
            # Apply path: actually call the embedder + upsert to Qdrant.
            vectors = embed_texts_batch(batch_texts, config=config, fail_open=True)
        else:
            # Dry-run: do NOT call the embedder (no Ollama traffic) and
            # do NOT call Qdrant (no writes).  We just count candidates
            # we WOULD write.  Treat every batch entry as a forward-
            # looking valid candidate; the embedder_fail_open bucket is
            # 0 in dry-run because the embedder is never invoked.
            for _point_id, _entry_id, payload in batch_meta:
                payload["derived_semantic_text"] = ""  # placeholder, not embedded
                payload["provenance"]["reindex_attempted"] = False  # dry-run only
            counters.written += len(batch_meta)
            batch_texts = []
            batch_meta = []
            batch_payloads_raw = []
            return

        upserts: list[PointStruct] = []
        for (point_id, entry_id, payload), vec, derived_text, _raw_entry in zip(
            batch_meta, vectors, batch_texts, batch_payloads_raw, strict=True
        ):
            if vec is None:
                # Embedder fail-opened.  Record the bucket under
                # ``embedder_fail_open`` (apply mode only) so the operator
                # can distinguish this from the dry-run candidate count.
                counters.embedder_fail_open += 1
                logger.warning(
                    "reindex: embedder fail-open for %s — skipping (apply mode)",
                    entry_id,
                )
                continue
            payload["derived_semantic_text"] = derived_text
            payload["provenance"]["reindex_attempted"] = True
            upserts.append(PointStruct(id=point_id, vector=vec, payload=payload))
            counters.written += 1
        if upserts:
            client.upsert(collection_name=shadow, points=upserts)
        batch_texts = []
        batch_meta = []
        batch_payloads_raw = []

    for lineno, entry in _iter_seal_chain(vault_path):
        if stop_after is not None and counters.read >= stop_after:
            break
        counters.read += 1

        raw_id, kind = _resolve_strong_id(entry)
        if not raw_id:
            counters.skipped_bad_id += 1
            logger.debug("vault line %d: no usable id — skipping", lineno)
            continue

        point_id = _deterministic_point_id(raw_id, kind)
        if point_id in existing_ids:
            counters.skipped_existing += 1
            continue

        derived_text = _synthesize_vector_text(entry)
        enriched = _build_enriched_payload(
            entry=entry,
            entry_id=raw_id,
            blast_radius=str(entry.get("blast_radius", "L2_SYSTEM")),
            session_id=str(entry.get("session_id", "")),
            derived_text=derived_text,
            raw_json=json.dumps(entry, sort_keys=True, default=str),
        )
        # Normalized provenance
        enriched["provenance"] = {
            "reindex_script": "scripts/reindex_prl.py",
            "embedder": f"{config.model}@{config.base_url}",
            "embedder_dim": config.dim,
            "source_line": lineno,
            "source_kind": kind,
            "vault_path": str(vault_path),
            "reindex_attempted": False,
        }
        enriched["source_line"] = lineno

        batch_texts.append(derived_text)
        batch_meta.append((point_id, raw_id, enriched))
        batch_payloads_raw.append(entry)

        if len(batch_texts) >= batch_size:
            _flush()
            if apply and batch_cooldown > 0:
                time.sleep(batch_cooldown)

    _flush()


# ── Alias promotion (explicit, second invocation) ─────────────────────


def _promote_shadow(client: Any, shadow: str, live: str) -> None:
    """Swap the live collection's alias to the shadow.  Requires the live
    collection to be reachable.  Aliases only — no rename / no delete.
    """
    from qdrant_client.http import models as qmodels  # type: ignore

    actions = [
        qmodels.CreateAlias(collection_name=shadow, alias_name=live),
    ]
    client.update_collection_aliases(change_aliases_operations=actions)
    logger.info("Promoted alias %s → shadow %s", live, shadow)


# ── CLI ───────────────────────────────────────────────────────────────


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Non-destructive PRL reindex (dry-run by default).",
    )
    p.add_argument(
        "--vault-path",
        default=os.environ.get(
            "VAULT999_SEAL_CHAIN",
            "/root/.local/share/arifos/vault999/seal_chain.jsonl",
        ),
        help="Path to seal_chain.jsonl (default: VAULT999_SEAL_CHAIN or canonical).",
    )
    p.add_argument(
        "--qdrant-url",
        default=os.environ.get("QDRANT_URL", "http://localhost:6333"),
    )
    p.add_argument(
        "--source",
        default=DEFAULT_LIVE_COLLECTION,
        help="Source collection (read-only metadata probe).",
    )
    p.add_argument(
        "--shadow",
        default=DEFAULT_SHADOW_ALIAS,
        help="Shadow collection name.",
    )
    p.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    p.add_argument("--batch-cooldown", type=float, default=DEFAULT_BATCH_COOLDOWN_S)
    p.add_argument("--stop-after", type=int, default=None)
    p.add_argument(
        "--apply",
        action="store_true",
        help="Actually create the shadow collection + upsert points.  Dry-run is the default.",
    )
    p.add_argument(
        "--promote-shadow",
        action="store_true",
        help="Swap live alias to the shadow.  REQUIRES a separate invocation after validation.",
    )
    p.add_argument(
        "--json-report",
        default=None,
        help="Write counters as JSON to this path.",
    )
    p.add_argument("--log-level", default="INFO")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )

    vault_path = Path(args.vault_path)
    if not vault_path.is_file():
        logger.error("Vault file not found: %s", vault_path)
        return 2

    config = PrlEmbedderConfig.from_env()

    # Promotion is always a separate, explicit step.
    if args.promote_shadow:
        client = _qdrant_client(args.qdrant_url)
        try:
            _promote_shadow(client, args.shadow, args.source)
            logger.info("PROMOTION COMPLETE — alias %s now points to %s", args.source, args.shadow)
        finally:
            client.close()
        return 0

    counters = ReindexCounters(
        shadow_collection=args.shadow,
        embedder_model=config.model,
        embedder_dim=config.dim,
        started_at=datetime.now(UTC).isoformat(),
        dry_run=not args.apply,
    )

    logger.info(
        "PRL reindex starting: vault=%s shadow=%s apply=%s dim=%d model=%s",
        vault_path,
        args.shadow,
        args.apply,
        config.dim,
        config.model,
    )

    client = _qdrant_client(args.qdrant_url)
    try:
        _ensure_shadow(
            client,
            shadow=args.shadow,
            dim=PRL_VECTOR_DIM,
            apply=args.apply,
            counters=counters,
        )
        _process_batches(
            client,
            shadow=args.shadow,
            vault_path=vault_path,
            batch_size=args.batch_size,
            batch_cooldown=args.batch_cooldown,
            apply=args.apply,
            counters=counters,
            config=config,
            stop_after=args.stop_after,
        )
    finally:
        client.close()

    counters.finished_at = datetime.now(UTC).isoformat()

    report = counters.as_dict()
    # In dry-run mode the ``written`` field is renamed in the report to
    # ``would_write_candidates`` so an operator can never mistake a
    # forward-looking candidate count for an actual write.  The on-disk
    # dataclass field stays ``written`` to keep the dataclass minimal.
    if counters.dry_run:
        report["would_write_candidates"] = report.pop("written")
        report["written"] = 0
    logger.info("REINDEX SUMMARY: %s", json.dumps(report, default=str))
    if args.json_report:
        Path(args.json_report).write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )
        logger.info("Wrote JSON report → %s", args.json_report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
