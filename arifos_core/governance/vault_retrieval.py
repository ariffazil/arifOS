# arifos_core/vault_retrieval.py
"""
Vault Retrieval (v36Ω) — Cooling Ledger RAG Stub

This module provides a structured interface for retrieving "law" from the
Cooling Ledger (L1) based on the user's query.

Goals:
- Keep it simple and stdlib-only for v36Ω.
- Make it easy to plug in a vector database / embedding model later.
- Return entries in a structured way that zkPC + caged LLMs can consume.

Design:
- RetrievalQuery: describes what the caller wants.
- retrieve_canon_entries(): main entry point.
- Internal helpers for basic keyword/tag/type filtering.

In future:
- This module can be extended to call an external embedding/RAG layer
  while preserving the same function signatures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from arifos_core.governance.ledger_hashing import load_jsonl

# Default path for L1 Cooling Ledger
DEFAULT_LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"


@dataclass
class RetrievalQuery:
    """
    Structured retrieval request for Vault-999 / Cooling Ledger.

    Fields:
        text: The user query or situation description.
        types: Optional list of entry types to restrict to
               (e.g. ["999_SEAL", "zkpc_receipt", "EUREKA"]).
        tags: Optional semantic tags to match (if entries store tags).
        high_stakes: Whether this is a high-stakes query
                     (may be used for ranking/strictness).
        limit: Maximum number of entries to return.
    """
    text: str
    types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    high_stakes: bool = False
    limit: int = 10
    # Optional future knobs (e.g. min_score) can be added here.
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """
    Result from a retrieval operation.

    Fields:
        entries: List of ledger entries (dicts) that matched.
        debug_info: Optional diagnostics about how they were selected.
    """
    entries: List[Dict[str, Any]]
    debug_info: Dict[str, Any]


def _load_ledger(path: Path) -> List[Dict[str, Any]]:
    """
    Load the Cooling Ledger (L1) from disk.

    Returns a list of ledger entry dicts. If the file does not exist,
    returns an empty list.
    """
    if not path.exists():
        return []
    return load_jsonl(str(path))


def _entry_text_blob(entry: Dict[str, Any]) -> str:
    """
    Build a simple text blob for keyword matching.

    We avoid deep recursion; we just concatenate key fields that are
    likely to be relevant for retrieval:
    - id, type, source
    - canon.principle / canon.law / canon.checks
    - receipt fields for zkpc_receipt entries
    """
    parts: List[str] = []

    for key in ("id", "type", "source"):
        val = entry.get(key)
        if isinstance(val, str):
            parts.append(val)

    # If this is a canon-style entry
    canon = entry.get("canon")
    if isinstance(canon, dict):
        for key in ("principle", "law"):
            val = canon.get(key)
            if isinstance(val, str):
                parts.append(val)
        checks = canon.get("checks")
        if isinstance(checks, list):
            parts.extend(str(c) for c in checks)

    # If this is a zkpc_receipt entry
    receipt = entry.get("receipt")
    if isinstance(receipt, dict):
        # We keep it light: use verdict + care_scope + some metrics names.
        verdict = receipt.get("verdict")
        if isinstance(verdict, str):
            parts.append(verdict)

        care_scope = receipt.get("care_scope", {})
        if isinstance(care_scope, dict):
            for k in ("stakeholders", "ethical_risks", "entropy_sources"):
                v = care_scope.get(k)
                if isinstance(v, list):
                    parts.extend(str(x) for x in v)

        metrics = receipt.get("metrics", {})
        if isinstance(metrics, dict):
            # Just include keys for simple text-search right now.
            parts.extend(metrics.keys())

    return " ".join(parts).lower()


def _entry_tags(entry: Dict[str, Any]) -> List[str]:
    """
    Extract tags from a ledger entry if present.

    Convention:
    - We look for `tags` at top-level or inside `canon`.
    """
    tags: List[str] = []
    top_tags = entry.get("tags")
    if isinstance(top_tags, list):
        tags.extend(str(t).lower() for t in top_tags)

    canon = entry.get("canon")
    if isinstance(canon, dict):
        canon_tags = canon.get("tags")
        if isinstance(canon_tags, list):
            tags.extend(str(t).lower() for t in canon_tags)

    return tags


def _simple_keyword_score(text_blob: str, query_text: str) -> int:
    """
    A naive keyword overlap score:
    - Lowercase both,
    - Split query into tokens,
    - Count how many tokens appear in the text blob.

    This is a placeholder until a real embedding/RAG system is wired in.
    """
    if not query_text.strip():
        return 0

    blob = text_blob
    tokens = [tok for tok in query_text.lower().split() if tok]
    score = sum(1 for t in tokens if t in blob)
    return score


def _matches_types(entry: Dict[str, Any], types: Optional[List[str]]) -> bool:
    if not types:
        return True
    etype = entry.get("type")
    return isinstance(etype, str) and etype in types


def _matches_tags(entry: Dict[str, Any], tags: Optional[List[str]]) -> bool:
    if not tags:
        return True
    entry_tags = _entry_tags(entry)
    # Basic "intersection non-empty" check
    query_tags = {t.lower() for t in tags}
    return bool(query_tags.intersection(entry_tags))


def retrieve_canon_entries(
    query: RetrievalQuery,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
) -> RetrievalResult:
    """
    Main retrieval function for Vault-999 / Cooling Ledger.

    v36Ω behaviour (stub):
    - Load all entries from L1 ledger.
    - Filter by `types` and `tags` if provided.
    - Compute a naive keyword score using `query.text` vs entry fields.
    - Sort entries by score (descending) and recency (descending).
    - Truncate to `query.limit`.

    In future:
    - This function can call a vector database / embedding service instead,
      while preserving the same interface.
    """
    entries = _load_ledger(ledger_path)

    scored: List[Tuple[int, Dict[str, Any]]] = []
    for entry in entries:
        if not _matches_types(entry, query.types):
            continue
        if not _matches_tags(entry, query.tags):
            continue

        blob = _entry_text_blob(entry)
        score = _simple_keyword_score(blob, query.text)

        # For now, score 0 entries are allowed but sorted last.
        scored.append((score, entry))

    # Sort by (score desc, timestamp desc if present)
    def sort_key(item: Tuple[int, Dict[str, Any]]) -> Tuple[int, str]:
        score, entry = item
        ts = entry.get("timestamp") or ""
        # We want recent entries to come first if scores tie.
        return (score, ts)

    scored.sort(key=sort_key, reverse=True)

    limited_entries = [e for (s, e) in scored[: max(1, query.limit)]]

    debug_info = {
        "total_entries": len(entries),
        "candidates": len(scored),
        "returned": len(limited_entries),
        "query": {
            "text": query.text,
            "types": query.types,
            "tags": query.tags,
            "high_stakes": query.high_stakes,
            "limit": query.limit,
        },
    }

    return RetrievalResult(entries=limited_entries, debug_info=debug_info)
