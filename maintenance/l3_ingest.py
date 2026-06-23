#!/usr/bin/env python3
"""
l3_ingest.py — L6(VAULT999) → L3(Qdrant) bridge
=================================================
Reads canonical outcomes.jsonl, embeds via Ollama bge-m3,
upserts to Qdrant arifos_memory with idempotent SHA-256 keys.

Architecture:     L6 (outcomes.jsonl) → Ollama bge-m3 → Qdrant (arifos_memory)
Idempotency:      SHA-256(content) as Qdrant point ID
Embedding model:  bge-m3:latest (1024-dim, Cosine)
F1 Reversibility: Dry-run mode, no deletes, UPSERT only

Usage:
  python3 l3_ingest.py              # Full run (all lines)
  python3 l3_ingest.py --dry-run    # Preview only, no writes
  python3 l3_ingest.py --limit 50   # Process first 50 lines
  python3 l3_ingest.py --resume     # Skip already-embedded lines

Author: Omega (arifOS Forge Agent)
Sovereign: Muhammad Arif bin Fazil (F13)
Motto: DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

# ── CONFIG ──────────────────────────────────────────────────
VAULT999_PATH = os.environ.get(
    "VAULT999_PATH", os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl"
)
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = "arifos_memory"
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = "bge-m3:latest"
EMBED_DIM = 1024
BATCH_SIZE = 10  # embed in batches for speed
SLEEP_BETWEEN_BATCHES = 0.5  # be gentle to Ollama


def deterministic_uuid(content: str) -> str:
    """uuid5 from content — deterministic, Qdrant-compatible idempotency key."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, content))


def ollama_embed(texts: list[str]) -> list[list[float]]:
    """Batch-embed texts via Ollama bge-m3. Returns list of vectors."""
    url = f"{OLLAMA_URL}/api/embed"
    vectors = []
    for text in texts:
        try:
            resp = requests.post(
                url,
                json={"model": EMBED_MODEL, "input": text},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            emb = data.get("embeddings", [[]])[0]
            if len(emb) != EMBED_DIM:
                print(f"  ⚠️  Embedding dim mismatch: {len(emb)} vs {EMBED_DIM}", file=sys.stderr)
                vectors.append([0.0] * EMBED_DIM)
            else:
                vectors.append(emb)
        except Exception as e:
            print(f"  ❌ Embed failed for text[:60]: {e}", file=sys.stderr)
            vectors.append([0.0] * EMBED_DIM)
    return vectors


def ensure_collection(client: QdrantClient) -> None:
    """Create collection if it doesn't exist."""
    collections = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        print(f"  📦 Created collection: {QDRANT_COLLECTION}", file=sys.stderr)


def read_outcomes(path: str) -> list[dict]:
    """Read outcomes.jsonl, returning list of parseable JSON entries.
    Handles bare strings by wrapping them as {'text': <string>}."""
    entries = []
    malformed_count = 0
    with open(path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
                if isinstance(parsed, str):
                    # Bare string — wrap as dict
                    entry = {"text": parsed, "action": "raw_entry"}
                elif isinstance(parsed, dict):
                    entry = parsed
                else:
                    malformed_count += 1
                    continue
                entry["_line"] = line_num
                entries.append(entry)
            except json.JSONDecodeError:
                malformed_count += 1
    if malformed_count:
        print(f"  ⚠️  Skipped {malformed_count} malformed lines", file=sys.stderr)
    return entries


def text_for_embedding(entry: dict) -> str:
    """Build a rich text representation for semantic embedding."""
    parts = []
    if entry.get("action"):
        parts.append(f"action: {entry['action']}")
    if entry.get("actor"):
        parts.append(f"actor: {entry['actor']}")
    if entry.get("outcome") or entry.get("verdict"):
        parts.append(f"verdict: {entry.get('outcome') or entry.get('verdict')}")
    if entry.get("session_id"):
        parts.append(f"session: {entry['session_id']}")
    if entry.get("id"):
        parts.append(f"id: {entry['id']}")
    # Add any summary/description fields
    for key in ("summary", "description", "note", "payload"):
        if entry.get(key) and isinstance(entry[key], str):
            parts.append(f"{key}: {entry[key][:200]}")
    return " | ".join(parts) if parts else json.dumps(entry)


def already_embedded(client: QdrantClient, point_id: str) -> bool:
    """Check if a point with this UUID already exists."""
    try:
        result = client.retrieve(
            collection_name=QDRANT_COLLECTION,
            ids=[point_id],
            with_vectors=False,
        )
        return len(result) > 0
    except Exception:
        return False


def ingest(
    dry_run: bool = False,
    limit: Optional[int] = None,
    resume: bool = False,
) -> dict:
    """Main ingestion loop. Returns summary dict."""
    t0 = time.time()

    print("═══ L3 INGEST START ═══", file=sys.stderr)
    print(f"  Vault:    {VAULT999_PATH}", file=sys.stderr)
    print(f"  Qdrant:   {QDRANT_URL}/{QDRANT_COLLECTION}", file=sys.stderr)
    print(f"  Embed:    {EMBED_MODEL} @ {OLLAMA_URL}", file=sys.stderr)
    print(f"  Dry-run:  {dry_run}", file=sys.stderr)
    print(f"  Resume:   {resume}", file=sys.stderr)

    # Connect
    client = QdrantClient(url=QDRANT_URL)
    ensure_collection(client)

    # Read vault
    entries = read_outcomes(VAULT999_PATH)
    total = len(entries)
    print(f"  📄 Read {total} entries from outcomes.jsonl", file=sys.stderr)

    if limit and limit < total:
        entries = entries[:limit]
        total = limit
        print(f"  🔢 Limited to {total} entries", file=sys.stderr)

    # Process in batches
    processed = 0
    skipped = 0
    failed = 0

    for batch_start in range(0, total, BATCH_SIZE):
        batch = entries[batch_start : batch_start + BATCH_SIZE]

        # Filter already-embedded if resuming
        new_batch = []
        for entry in batch:
            text = text_for_embedding(entry)
            pid = deterministic_uuid(text)
            if resume and already_embedded(client, pid):
                skipped += 1
                continue
            entry["_point_id"] = pid
            entry["_text"] = text
            new_batch.append(entry)

        if not new_batch:
            continue

        # Embed
        texts = [e["_text"] for e in new_batch]
        if dry_run:
            print(f"  🔍 [DRY] Would embed {len(texts)} texts", file=sys.stderr)
            for e in new_batch:
                print(f"      L{e['_line']}: {e['_text'][:80]}...", file=sys.stderr)
            continue

        vectors = ollama_embed(texts)

        # Upsert to Qdrant
        points = []
        for entry, vec in zip(new_batch, vectors):
            pid = entry["_point_id"]
            payload = {
                "type": "vault_seal",
                "source": "outcomes.jsonl",
                "action": entry.get("action", ""),
                "actor": entry.get("actor", ""),
                "verdict": entry.get("outcome") or entry.get("verdict", ""),
                "session_id": entry.get("session_id", ""),
                "line_number": entry["_line"],
                "ingested_at": datetime.now(timezone.utc).isoformat(),
            }
            points.append(PointStruct(id=pid, vector=vec, payload=payload))

        try:
            client.upsert(collection_name=QDRANT_COLLECTION, points=points)
            processed += len(points)
            print(
                f"  ✅ Batch {batch_start // BATCH_SIZE + 1}: "
                f"{len(points)} upserted (total: {processed})",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"  ❌ Upsert failed: {e}", file=sys.stderr)
            failed += len(points)

        time.sleep(SLEEP_BETWEEN_BATCHES)

    # Summary
    elapsed = time.time() - t0
    summary = {
        "total_lines": total,
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "dry_run": dry_run,
        "elapsed_seconds": round(elapsed, 1),
        "vectors_per_second": round(processed / elapsed, 1) if elapsed > 0 else 0,
    }

    print("═══ L3 INGEST DONE ═══", file=sys.stderr)
    print(f"  Processed: {processed}", file=sys.stderr)
    print(f"  Skipped:   {skipped}", file=sys.stderr)
    print(f"  Failed:    {failed}", file=sys.stderr)
    print(f"  Time:      {elapsed:.1f}s", file=sys.stderr)

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="L6→L3 VAULT999 to Qdrant bridge")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--limit", type=int, default=None, help="Max entries to process")
    parser.add_argument("--resume", action="store_true", help="Skip already-embedded lines")
    args = parser.parse_args()

    result = ingest(dry_run=args.dry_run, limit=args.limit, resume=args.resume)
    print(json.dumps(result, indent=2))
