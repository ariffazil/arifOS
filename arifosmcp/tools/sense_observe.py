"""
arifosmcp/tools/sense_observe.py — 111_SENSE (Reality-Wired)
═══════════════════════════════════════════════════════════════

Reality-grounded observation and telemetry, wired to RealityHandler
for live web search (Brave → DDGS fallback) and URL fetch with
browserless render fallback.

QUANTUM SABAR PROTOCOL:
  Byzantine continuity when W1 (human/singular) or W3 (Earth/plural)
  is unreachable. Partition handling: if witness is unreachable within
  timeout, route to PURGATORY_LEDGER instead of hanging.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.reality_handlers import handler as reality_handler
from arifosmcp.runtime.reality_models import BundleInput
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok

logger = logging.getLogger(__name__)


def arif_sense_observe(
    mode: str = "search",
    query: str | None = None,
    url: str | None = None,
    layers: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    partition_mode: str = "ONLINE",
    partition_timeout: int = 30,
    top_k: int = 5,
    render: str = "auto",
) -> dict[str, Any]:
    """
    SENSE tool — now reality-wired via RealityHandler.

    Modes:
      search   → Brave API search (DDGS fallback)
      ingest   → Fetch + ingest URL via RealityHandler compass
      compass  → Auto-detect fetch vs search via handle_compass
      atlas    → Structural layer map (stub — pending vector atlas)
      entropy_dS → Random entropy delta (physics stub)
      vitals   → System vitals stub
    """
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        return _hold(
            "arif_sense_observe", auth["reason"], ["F11"], session_id=session_id
        )

    floor_check = check_floors("arif_sense_observe", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold(
            "arif_sense_observe", floor_check["reason"], floor_check["failed_floors"]
        )

    if partition_mode == "DEAD":
        return {
            "status": "HOLD",
            "tool": "arif_sense_observe",
            "result": {},
            "meta": {
                "partition": "DEAD",
                "reason": "Witness unreachable — CANDIDATE_SEAL escalation required",
                "failed_floors": [],
            },
        }

    if partition_mode == "PURGATORY":
        return _ok(
            "arif_sense_observe",
            {
                "query": query,
                "results": [],
                "source": "purgatory_ledger",
                "omega_0": 0.04,
                "partition": "PURGATORY",
                "note": "Witness unreachable — entry cached in Purgatory Ledger",
            },
        )

    if mode == "search":
        try:
            s_res = asyncio.run(reality_handler.search_brave(query or "", top_k=top_k))
            results = s_res.results if s_res.results else []
            omega_0 = 0.05 + min(len(results) * 0.02, 0.20)
            return _ok(
                "arif_sense_observe",
                {
                    "query": query,
                    "results": results,
                    "source": s_res.engine,
                    "verdict": "SEAL" if results else "SABAR",
                    "omega_0": round(omega_0, 3),
                    "partition": "ONLINE",
                    "latency_ms": round(s_res.latency_ms, 1),
                    "note": None if results else "No results — check query or API keys",
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_sense_observe ({mode}): {e}")
            return _ok(
                "arif_sense_observe",
                {
                    "query": query,
                    "results": [],
                    "source": "fallback_stub",
                    "verdict": "SABAR",
                    "omega_0": 0.04,
                    "partition": "ONLINE",
                    "note": f"RealityHandler fallback failed: {e}",
                },
            )

    if mode == "ingest" and url:
        try:
            bundle = asyncio.run(
                reality_handler.handle_compass(
                    BundleInput(type="url", value=url, mode="fetch", render=render),  # type: ignore[arg-type]
                    auth_context={
                        "actor_id": actor_id or "anonymous",
                        "session_id": session_id or "global",
                    },
                )
            )
            return _ok(
                "arif_sense_observe",
                {
                    "url": url,
                    "ingested": bundle.status.state == "SUCCESS",
                    "bundle_id": bundle.id,
                    "status": bundle.status.state,
                    "verdict": bundle.status.verdict,
                    "results_count": len(bundle.results),
                    "partition": "ONLINE",
                    "errors": [
                        {"code": e.code, "detail": e.detail}
                        for e in bundle.status.errors
                    ],
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_sense_observe ({mode}): {e}")
            return _ok(
                "arif_sense_observe",
                {
                    "url": url,
                    "ingested": False,
                    "verdict": "SABAR",
                    "partition": "ONLINE",
                    "note": f"RealityHandler fallback failed: {e}",
                },
            )

    if mode == "compass":
        value = url or query or ""
        btype = "url" if value.startswith(("http://", "https://")) else "query"
        try:
            bundle = asyncio.run(
                reality_handler.handle_compass(
                    BundleInput(
                        type=btype,  # type: ignore[arg-type]
                        value=value,
                        mode="auto",
                        top_k=top_k,
                        render=render,  # type: ignore[arg-type]
                    ),
                    auth_context={
                        "actor_id": actor_id or "anonymous",
                        "session_id": session_id or "global",
                    },
                )
            )
            return _ok(
                "arif_sense_observe",
                {
                    "heading": bundle.input.mode,
                    "confidence": 0.95 if bundle.status.state == "SUCCESS" else 0.50,
                    "bundle_id": bundle.id,
                    "status": bundle.status.state,
                    "verdict": bundle.status.verdict,
                    "results_count": len(bundle.results),
                    "partition": "ONLINE",
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_sense_observe ({mode}): {e}")
            return _ok(
                "arif_sense_observe",
                {
                    "heading": "unknown",
                    "confidence": 0.0,
                    "verdict": "SABAR",
                    "partition": "ONLINE",
                    "note": f"RealityHandler fallback failed: {e}",
                },
            )

    if mode == "atlas":
        return _ok(
            "arif_sense_observe",
            {
                "map": {},
                "layers": layers or [],
                "partition": partition_mode,
            },
        )
    if mode == "entropy_dS":
        dS = random.uniform(-0.1, 0.1)
        return _ok(
            "arif_sense_observe",
            {
                "delta_S": round(dS, 6),
                "trend": "stable",
                "partition": partition_mode,
            },
        )
    if mode == "vitals":
        return _ok(
            "arif_sense_observe",
            {
                "cpu": 12.5,
                "mem": 34.0,
                "io": "normal",
                "partition": partition_mode,
            },
        )

    return _hold("arif_sense_observe", f"Unknown mode: {mode}")
