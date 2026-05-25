"""
mcp_drift_check — Read-only surface drift detector.

Compares the canonical manifest against the live registered MCP surface.
Does NOT mutate registry by default.

Modes:
    report  = read-only drift report (default)
    warn    = logs drift, does not fail
    strict  = raises on drift (opt-in, gated by ARIFOS_DRIFT_ENFORCEMENT)

PHOENIX-72 gate: drift_detected=false + counts match target.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Default enforcement level from environment
DRIFT_ENFORCEMENT = os.getenv("ARIFOS_DRIFT_ENFORCEMENT", "report")


def _load_manifest() -> dict[str, Any]:
    """Load the canonical tool manifest."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS
    from arifosmcp.runtime.public_surface import DIAGNOSTIC_TOOLS, EXPANDED_45

    return {
        "canonical13": list(CANONICAL_TOOLS.keys()),
        "expanded45": list(EXPANDED_45),
        "diagnostic": list(DIAGNOSTIC_TOOLS),
    }


def _get_live_tools(mcp_server: Any | None = None) -> list[str]:
    """Extract live registered tool names from the MCP server."""
    # If an mcp server instance is passed, use it
    if mcp_server is not None:
        try:
            return sorted(mcp_server._tools.keys())
        except Exception:
            pass
    # Fallback: ask the public registry
    try:
        from arifosmcp.runtime.public_surface import (
            DIAGNOSTIC_TOOLS,
            EXPANDED_45,
        )
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        live = set(_CANONICAL_HANDLERS.keys())
        live.update(EXPANDED_45)
        live.update(DIAGNOSTIC_TOOLS)
        return sorted(live)
    except Exception as e:
        logger.warning(f"Failed to enumerate live tools: {e}")
        return []


def mcp_drift_check(
    mode: str = "report",
    target_manifest: str = "canonical13",
    mcp_server: Any | None = None,
) -> dict[str, Any]:
    """
    Detect drift between manifest and live registered surface.

    Args:
        mode: report | warn | strict
        target_manifest: canonical13 | expanded45 | diagnostic | all
        mcp_server: optional FastMCP instance for live enumeration

    Returns:
        Drift report dict with counts, missing, extra, drift_detected, verdict.
    """
    manifest = _load_manifest()
    allowed: set[str] = set()
    if target_manifest in ("all", "canonical13"):
        allowed.update(manifest["canonical13"])
    if target_manifest in ("all", "expanded45"):
        allowed.update(manifest["expanded45"])
    if target_manifest in ("all", "diagnostic"):
        allowed.update(manifest["diagnostic"])

    live = set(_get_live_tools(mcp_server))
    missing = sorted(allowed - live)
    extra = sorted(live - allowed)
    drift_detected = bool(missing or extra)

    report = {
        "mode": mode,
        "target_manifest": target_manifest,
        "allowed_count": len(allowed),
        "registered_count": len(live),
        "missing": missing,
        "extra": extra,
        "drift_detected": drift_detected,
        "verdict": "SEAL" if not drift_detected else "HOLD",
        "enforcement": DRIFT_ENFORCEMENT,
    }

    if mode == "strict" and drift_detected and DRIFT_ENFORCEMENT == "strict":
        raise RuntimeError(
            f"MCP drift detected: missing={missing}, extra={extra}. "
            f"Set ARIFOS_DRIFT_ENFORCEMENT=report to downgrade to warning."
        )

    if drift_detected:
        logger.warning(
            "mcp_drift_check: drift_detected=true missing=%s extra=%s",
            missing,
            extra,
        )
    else:
        logger.info(
            "mcp_drift_check: drift_detected=false allowed=%d registered=%d",
            len(allowed),
            len(live),
        )

    return report


# ── FastMCP-compatible wrapper ──────────────────────────────────────────────
async def arif_mcp_drift_check(
    mode: str = "report",
    target_manifest: str = "canonical13",
) -> dict[str, Any]:
    """Async wrapper for FastMCP tool registration."""
    return mcp_drift_check(mode=mode, target_manifest=target_manifest)


__all__ = ["mcp_drift_check", "arif_mcp_drift_check"]
