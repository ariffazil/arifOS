"""
tests/runtime/test_gptr_bridge.py — gptr-mcp Organ Bridge Tests

Phase 1 (2026-06-16): covers the arifOS-side gptr_bridge that delegates
to the gptr-mcp organ on 127.0.0.1:18084.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import os
import socket
from unittest.mock import patch

import pytest


def _gptr_organ_alive() -> bool:
    """Probe 127.0.0.1:18084 — returns True if gptr-organ is listening."""
    try:
        with socket.create_connection(("127.0.0.1", 18084), timeout=1.0):
            return True
    except (OSError, socket.timeout):
        return False


_GPTR_LIVE = _gptr_organ_alive()


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ─── Bridge imports ──────────────────────────────────────────────────


class TestBridgeImports:
    def test_bridge_imports(self):
        from arifosmcp.runtime.gptr_bridge import gptr_bridge

        assert gptr_bridge is not None
        assert hasattr(gptr_bridge, "deep_research")
        assert hasattr(gptr_bridge, "quick_search")
        assert hasattr(gptr_bridge, "write_report")
        assert hasattr(gptr_bridge, "get_research_sources")
        assert hasattr(gptr_bridge, "get_research_context")
        assert hasattr(gptr_bridge, "health")

    def test_bridge_url_default(self):
        import arifosmcp.runtime.gptr_bridge as gbmod

        # Default URL points at 127.0.0.1:18084
        assert "18084" in gbmod._GPTR_URL or os.getenv("GPTR_ORGAN_URL") is not None


# ─── Health check ────────────────────────────────────────────────────


@pytest.mark.skipif(not _GPTR_LIVE, reason="gptr-organ on 127.0.0.1:18084 not running")
class TestHealth:
    def test_health_live(self):
        from arifosmcp.runtime.gptr_bridge import gptr_bridge

        result = run(gptr_bridge.health())
        assert result["status"] == "healthy"
        assert result["gptr_response"].get("status") == "healthy"


# ─── Live integration (organ must be running) ───────────────────────


@pytest.mark.skipif(not _GPTR_LIVE, reason="gptr-organ on 127.0.0.1:18084 not running")
class TestLiveQuickSearch:
    """quick_search is the fast path — 5-10s, returns 10 results."""

    def test_quick_search_malaysia_capital(self):
        from arifosmcp.runtime.gptr_bridge import gptr_bridge

        result = run(gptr_bridge.quick_search("What is the capital of Malaysia?"))
        assert result["status"] == "success", f"got {result}"
        assert result["epistemic_tag"] == "INTERPRETATION"
        assert result["tool"] == "quick_search"
        results = result.get("search_results", [])
        assert len(results) >= 5, f"expected >=5 results, got {len(results)}"
        # At least one result should mention Kuala Lumpur
        body_blob = " ".join(r.get("body", "") for r in results).lower()
        assert "kuala lumpur" in body_blob, f"KL not in any result body"

    def test_quick_search_returns_search_id(self):
        from arifosmcp.runtime.gptr_bridge import gptr_bridge

        result = run(gptr_bridge.quick_search("Malaysia capital"))
        assert result.get("search_id") is not None
        assert len(result["search_id"]) > 0


@pytest.mark.skipif(not _GPTR_LIVE, reason="gptr-organ on 127.0.0.1:18084 not running")
@pytest.mark.slow
class TestLiveDeepResearch:
    """deep_research is the slow path — 30-60s, returns full report."""

    def test_deep_research_malaysia_capital(self):
        from arifosmcp.runtime.gptr_bridge import gptr_bridge

        result = run(gptr_bridge.deep_research("What is the capital of Malaysia?"))
        assert result["status"] == "success", f"got {result}"
        assert result["epistemic_tag"] == "INTERPRETATION"
        report = result.get("report") or ""
        assert len(report) > 5000, f"expected long report, got {len(report)} chars"
        assert "Kuala Lumpur" in report
        assert result.get("research_id") is not None


# ─── arif_sense_observe mode wiring ─────────────────────────────────


class TestSenseObserveWiring:
    """arif_sense_observe must accept deep_research + quick_search modes."""

    def test_modes_in_allowed(self):
        from pathlib import Path

        tools_path = Path("/root/arifOS/arifosmcp/runtime/tools.py")
        src = tools_path.read_text()
        for mode in ("deep_research", "quick_search"):
            count = src.count(f'"{mode}"')
            assert count >= 2, f"Mode {mode} only appears {count} time(s) in tools.py"

    def test_gptr_bridge_in_dispatch(self):
        from pathlib import Path

        tools_path = Path("/root/arifOS/arifosmcp/runtime/tools.py")
        src = tools_path.read_text()
        assert "gptr_bridge" in src, "tools.py must import gptr_bridge"
        assert "deep_research" in src
        assert "quick_search" in src
