"""
arifosmcp/runtime/memory_store.py — 555_MEMORY Persistent Storage Layer

FIXES THE HOLE: arif_memory_recall previously returned stub data.
Now: actual JSON file persistence in /root/.arifOS/memory/

Storage schema:
  /root/.arifOS/memory/
    .index.json          — master index: memory_id → {timestamp, tags, mode, summary}
    {memory_id}.json     — individual memory records

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Storage root ──────────────────────────────────────────────────────────────

_MEMORY_DIR = Path(os.getenv("ARIFOS_MEMORY_DIR", "/root/.arifOS/memory"))
_INDEX_FILE = _MEMORY_DIR / ".index.json"

# ── Internal helpers ─────────────────────────────────────────────────────────


def _ensure_dir() -> None:
    _MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not _INDEX_FILE.exists():
        _index_write({})


def _index_read() -> dict[str, dict[str, Any]]:
    try:
        with open(_INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _index_write(idx: dict[str, dict[str, Any]]) -> None:
    with open(_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, default=str)


def _content_hash(content: Any) -> str:
    """Stable SHA-256 hash of content for deduplication."""
    return hashlib.sha256(
        json.dumps(content, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]


# ── Public API ───────────────────────────────────────────────────────────────


def store(
    content: Any,
    mode: str = "unknown",
    tags: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    """
    Persist a memory record.

    Returns: {"stored": True, "memory_id": str, "indexed": bool}
    """
    _ensure_dir()
    memory_id = uuid.uuid4().hex[:12]

    record = {
        "memory_id": memory_id,
        "content": content,
        "mode": mode,
        "tags": tags or [],
        "actor_id": actor_id,
        "session_id": session_id,
        "summary": summary or _summarize(content),
        "content_hash": _content_hash(content),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    record_path = _MEMORY_DIR / f"{memory_id}.json"
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str)

    idx = _index_read()
    idx[memory_id] = {
        "mode": mode,
        "tags": tags or [],
        "summary": record["summary"],
        "content_hash": record["content_hash"],
        "created_at": record["created_at"],
        "session_id": session_id,
    }
    _index_write(idx)

    return {"stored": True, "memory_id": memory_id, "indexed": True}


def recall(
    memory_id: str,
) -> dict[str, Any] | None:
    """Retrieve a single memory by ID. Returns None if not found."""
    _ensure_dir()
    record_path = _MEMORY_DIR / f"{memory_id}.json"
    if not record_path.exists():
        return None
    try:
        with open(record_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def search(
    query: str | None = None,
    tags: list[str] | None = None,
    mode: str | None = None,
    session_id: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Search memories by text query, tags, mode, or session.

    Query matches against summary + tags (case-insensitive).
    Returns up to `limit` records ordered by newest first.
    """
    _ensure_dir()
    idx = _index_read()
    results: list[tuple[float, dict[str, Any]]] = []

    for mid, meta in idx.items():
        # Filter: mode
        if mode and meta.get("mode") != mode:
            continue
        # Filter: session_id
        if session_id and meta.get("session_id") != session_id:
            continue
        # Filter: tags (all must match)
        if tags and not all(t in meta.get("tags", []) for t in tags):
            continue
        # Score: query match
        score = 0.0
        if query:
            q = query.lower()
            if q in (meta.get("summary") or "").lower():
                score += 2.0
            if q in " ".join(meta.get("tags", [])).lower():
                score += 1.0
        else:
            score = 1.0

        if score > 0:
            record = recall(mid)
            if record:
                results.append((score, record))

    # Sort by score desc, then created_at desc
    results.sort(key=lambda x: (x[0], x[1].get("created_at", "")), reverse=True)
    return [r for _, r in results[:limit]]


def prune(
    memory_id: str | None = None,
    before: str | None = None,
    reason: str = "manual",
) -> dict[str, Any]:
    """
    Delete memory records.

    Args:
        memory_id: Delete specific record.
        before: Delete records created before this ISO timestamp.
        reason: Reason for pruning (logged).

    Returns: {"pruned": [memory_ids], "count": int}
    """
    _ensure_dir()
    idx = _index_read()
    pruned: list[str] = []

    to_delete: list[str] = []
    if memory_id:
        to_delete = [memory_id]
    elif before:
        for mid, meta in idx.items():
            created = meta.get("created_at", "")
            if created and created < before:
                to_delete.append(mid)

    for mid in to_delete:
        record_path = _MEMORY_DIR / f"{mid}.json"
        if record_path.exists():
            record_path.unlink()
        if mid in idx:
            del idx[mid]
            pruned.append(mid)

    _index_write(idx)
    return {"pruned": pruned, "count": len(pruned), "reason": reason}


def context_for_session(
    session_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Retrieve all memories for a given session, newest first."""
    return search(session_id=session_id, limit=limit)


def _summarize(content: Any) -> str:
    """Generate a one-line summary from content."""
    if isinstance(content, str):
        return content[:120].strip()
    if isinstance(content, dict):
        # Pull most meaningful key as summary
        for key in ("synthesis", "verdict", "composed", "summary", "output"):
            if key in content and content[key]:
                val = content[key]
                if isinstance(val, str):
                    return f"[{key}] {val}"[:120].strip()
        return f"dict with keys: {', '.join(list(content.keys())[:5])}"
    if isinstance(content, list):
        return f"list of {len(content)} items"
    return str(type(content).__name__)


def stats() -> dict[str, Any]:
    """Return memory store statistics."""
    _ensure_dir()
    idx = _index_read()
    total_size = sum(
        (_MEMORY_DIR / f"{mid}.json").stat().st_size
        for mid in idx
        if (_MEMORY_DIR / f"{mid}.json").exists()
    )
    return {
        "total_records": len(idx),
        "total_bytes": total_size,
        "by_mode": _mode_counts(idx),
        "by_session": _session_counts(idx),
    }


def _mode_counts(idx: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for meta in idx.values():
        m = meta.get("mode", "unknown")
        counts[m] = counts.get(m, 0) + 1
    return counts


def _session_counts(idx: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for meta in idx.values():
        s = meta.get("session_id") or "none"
        counts[s] = counts.get(s, 0) + 1
    return counts


__all__ = ["store", "recall", "search", "prune", "context_for_session", "stats"]
