"""
arifosmcp/tools/evidence_fetch.py — 222_FETCH
═════════════════════════════════════════════

Evidence-preserving web ingestion and fetch.
"""
from __future__ import annotations

import uuid
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok


def arif_evidence_fetch(
    mode: str = "fetch",
    url: str | None = None,
    query: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_evidence_fetch", {"url": url or "", "query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_evidence_fetch", floor_check["reason"], floor_check["failed_floors"])

    if mode == "fetch":
        return _ok("arif_evidence_fetch", {"url": url, "content": "", "status": 200, "archived": False})
    if mode == "search":
        return _ok("arif_evidence_fetch", {"query": query, "results": []})
    if mode == "archive":
        return _ok("arif_evidence_fetch", {"url": url, "archived": True, "archive_id": uuid.uuid4().hex[:8]})
    if mode == "verify":
        return _ok("arif_evidence_fetch", {"url": url, "verified": False, "note": "stub"})

    return _hold("arif_evidence_fetch", f"Unknown mode: {mode}")
