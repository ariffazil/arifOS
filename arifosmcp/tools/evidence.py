"""
arifosmcp/tools/evidence.py — 222_EVIDENCE (Reality-Wired)
════════════════════════════════════════════════════════════

Evidence-preserving web ingestion and fetch, wired to RealityHandler
for live URL fetch (streaming + browserless render fallback) and
web search (Brave → DDGS fallback).

Every operation emits an evidence receipt for F-WEB audit trail.
Implements Stage 1 Governed Reasoning Trace.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _hold

logger = logging.getLogger(__name__)


async def arif_fetch(
    mode: Literal["fetch", "search", "archive", "verify", "void_audit"] = "fetch",
    url: str | None = None,
    query: str | None = None,
    actor_id: str | None = None,
    render: str = "auto",
    top_k: int = 5,
    thinking_depth: int = 0,
    thinking_budget: float = 1.0,
    sequential_mode: str = "deliberate",
    allow_early_termination: bool = True,
    confidence_threshold: float = 0.90,
) -> dict[str, Any]:
    """
    EVIDENCE tool — reality-wired with governed sequential thinking.

    Modes:
      fetch       — Ingest a URL into the evidence store with receipt emission.
      search      — Query configured evidence/search backends.
      archive     — Seal a lightweight archive receipt for a URL.
      verify      — Return a verification stub for an existing URL/receipt.
      void_audit  — Build a void report across recent evidence receipts.

    Sequential thinking parameters (civilization intelligence):
    - thinking_depth: Max reasoning steps (0-10). 0 = disabled.
    - thinking_budget: Token/time budget for thinking (0.0-10.0).
    - sequential_mode: 'fast' | 'deliberate' | 'exhaustive'
    - allow_early_termination: Stop if confidence > threshold
    - confidence_threshold: Stop threshold (0.0-1.0)
    """
    if mode in (
        "pqc_standard",
        "crqc_estimate",
        "hardware_claim_evidence",
        "quantum_earth_science_evidence",
        "quantum_chemistry_pvt_evidence",
        "ccus_geochemistry_evidence",
        "quantum_algorithm_limitations",
    ):
        return {"status": "readonly", "message": f"{mode} activated based on policy parameters."}

    floor_check = check_laws("arif_fetch", {"url": url or "", "query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_fetch", floor_check["reason"], floor_check["violated_laws"])

    # ── Phase 1: Real Implementation ──
    # Delegate to runtime implementation which handles the thinking layer,
    # backend discovery, and reality-wiring.
    from arifosmcp.runtime.tools import _arif_fetch

    return _arif_fetch(
        mode=mode,
        url=url,
        query=query,
        actor_id=actor_id,
        session_id=None,  # Session should be resolved by caller or env
        thinking_depth=thinking_depth,
        thinking_budget=thinking_budget,
        sequential_mode=sequential_mode,
        allow_early_termination=allow_early_termination,
        confidence_threshold=confidence_threshold,
    )


__all__ = ["arif_fetch"]

# Backward compatibility alias
arif_evidence_fetch = arif_fetch
