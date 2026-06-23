"""
tests/runtime/test_reality_wiring.py
════════════════════════════════════

Verify that arif_sense_observe and arif_evidence_fetch stubs are wired
to RealityHandler, and that canonical runtime handlers fall back to
RealityHandler when primary backends fail.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from arifosmcp.runtime.reality_models import FetchResult, SearchResult


class TestSenseObserveStubWiring:
    """arifosmcp.tools.sense — RealityHandler integration."""

    @patch("arifosmcp.tools.sense.validate_session")
    @patch("arifosmcp.tools.sense.check_laws")
    @patch("arifosmcp.tools.sense.reality_handler")
    def test_search_mode_returns_real_results(self, mock_rh, mock_floors, mock_auth):
        mock_auth.return_value = {"valid": True}
        mock_floors.return_value = {"verdict": "SEAL", "reason": "", "violated_laws": []}
        mock_rh.search_brave = AsyncMock(
            return_value=SearchResult(
                engine="brave",
                query="test query",
                status_code=200,
                results=[
                    {"title": "T1", "url": "https://example.com/1", "description": "D1"},
                    {"title": "T2", "url": "https://example.com/2", "description": "D2"},
                ],
                latency_ms=120.0,
            )
        )

        from arifosmcp.tools.sense import arif_sense_observe

        result = arif_sense_observe(mode="search", query="test query")

        assert result["status"] == "OK"
        assert result["result"]["source"] == "brave"
        assert result["result"]["verdict"] == "SEAL"
        assert len(result["result"]["results"]) == 2
        assert result["result"]["results"][0]["title"] == "T1"
        assert result["result"]["omega_0"] > 0.04  # increased by hit count
        mock_rh.search_brave.assert_awaited_once_with("test query", top_k=5)

    @patch("arifosmcp.tools.sense.validate_session")
    @patch("arifosmcp.tools.sense.check_laws")
    @patch("arifosmcp.tools.sense.reality_handler")
    def test_search_mode_graceful_degradation(self, mock_rh, mock_floors, mock_auth):
        mock_auth.return_value = {"valid": True}
        mock_floors.return_value = {"verdict": "SEAL", "reason": "", "violated_laws": []}
        mock_rh.search_brave = AsyncMock(side_effect=Exception("network down"))

        from arifosmcp.tools.sense import arif_sense_observe

        result = arif_sense_observe(mode="search", query="test query")

        # Graceful fallback — tool never crashes, returns SABAR
        assert result["status"] == "OK"
        assert result["result"]["verdict"] == "SABAR"
        assert result["result"]["results"] == []
        assert result["result"]["partition"] == "ONLINE"

    @patch("arifosmcp.tools.sense.validate_session")
    @patch("arifosmcp.tools.sense.check_laws")
    @patch("arifosmcp.tools.sense.reality_handler")
    def test_ingest_mode_compass(self, mock_rh, mock_floors, mock_auth):
        mock_auth.return_value = {"valid": True}
        mock_floors.return_value = {"verdict": "SEAL", "reason": "", "violated_laws": []}

        mock_bundle = MagicMock()
        mock_bundle.id = "eb-abc123"
        mock_bundle.status.state = "SUCCESS"
        mock_bundle.status.verdict = "SEAL"
        mock_bundle.status.errors = []
        mock_bundle.results = [MagicMock()]
        mock_rh.handle_compass = AsyncMock(return_value=mock_bundle)

        from arifosmcp.tools.sense import arif_sense_observe

        result = arif_sense_observe(
            mode="ingest", url="https://example.com/page", actor_id="u1", session_id="s1"
        )

        assert result["status"] == "OK"
        assert result["result"]["ingested"] is True
        assert result["result"]["bundle_id"] == "eb-abc123"
        assert result["result"]["verdict"] == "SEAL"

    @patch("arifosmcp.tools.sense.validate_session")
    @patch("arifosmcp.tools.sense.check_laws")
    def test_dead_partition(self, mock_floors, mock_auth):
        mock_auth.return_value = {"valid": True}
        mock_floors.return_value = {"verdict": "SEAL", "reason": "", "violated_laws": []}

        from arifosmcp.tools.sense import arif_sense_observe

        result = arif_sense_observe(mode="search", query="x", partition_mode="DEAD")
        assert result["status"] == "HOLD"
        assert result["meta"]["partition"] == "DEAD"


class TestEvidenceStubWiring:
    """arifosmcp.tools.evidence — RealityHandler integration."""

    @patch("urllib.request.urlopen")
    @patch("arifosmcp.tools.evidence.check_laws")
    @patch("arifosmcp.runtime.reality_handlers.handler")
    def test_fetch_mode_returns_content(self, mock_rh, mock_floors, mock_urlopen):
        """When urllib fails, RealityHandler fallback provides content."""
        mock_floors.return_value = {"verdict": "SEAL", "reason": "", "violated_laws": []}
        mock_urlopen.side_effect = Exception("connection refused")
        mock_rh.fetch_url = AsyncMock(
            return_value=FetchResult(
                url="https://example.com",
                status_code=200,
                content_type="text/html",
                content_length=1234,
                raw_content="<html>hello</html>",
                final_url="https://example.com",
                redirects=0,
                render_fallback_used=False,
                latency_ms={"total": 45.0},
            )
        )

        from arifosmcp.tools.evidence import arif_evidence_fetch

        result = asyncio.run(arif_evidence_fetch(mode="fetch", url="https://example.com"))

        assert result["status"] == "OK"
        assert result["result"]["content"] == "hello"
        assert result["result"]["status"] == "200"
        mock_rh.fetch_url.assert_awaited_once_with("https://example.com", render="auto")

    @patch("arifosmcp.runtime.tools.get_evidence_store")
    @patch("arifosmcp.tools.evidence.check_laws")
    @patch("arifosmcp.runtime.reality_handlers.handler.search_brave")
    def test_search_mode_returns_results(self, mock_search_brave, mock_floors, mock_get_store):
        """Search mode falls back to evidence store when reality_handler returns empty."""
        from arifosmcp.runtime.reality_handlers import SearchResult

        mock_search_brave.return_value = SearchResult(
            engine="mock", query="python", results=[], status="mocked_empty"
        )
        mock_floors.return_value = {"verdict": "SEAL", "reason": "", "violated_laws": []}
        mock_store = MagicMock()
        mock_store.search_sources.return_value = [
            {"title": "Py", "url": "https://py.org", "description": "Python"}
        ]
        mock_get_store.return_value = mock_store

        with patch.dict("os.environ", {"QDRANT_URL": "http://localhost:6333"}):
            from arifosmcp.tools.evidence import arif_evidence_fetch

            result = asyncio.run(arif_evidence_fetch(mode="search", query="python"))

        assert result["status"] == "OK"
        assert len(result["result"]["results"]) == 1
        assert result["result"]["results"][0]["title"] == "Py"
        assert result["result"]["search_status"] == "found"

    @patch("urllib.request.urlopen")
    @patch("arifosmcp.tools.evidence.check_laws")
    @patch("arifosmcp.runtime.reality_handlers.handler")
    def test_fetch_graceful_degradation(self, mock_rh, mock_floors, mock_urlopen):
        """When both urllib and RealityHandler fail, result is OK with empty content."""
        mock_floors.return_value = {"verdict": "SEAL", "reason": "", "violated_laws": []}
        mock_urlopen.side_effect = Exception("connection refused")
        mock_rh.fetch_url = AsyncMock(side_effect=Exception("timeout"))

        from arifosmcp.tools.evidence import arif_evidence_fetch

        result = asyncio.run(arif_evidence_fetch(mode="fetch", url="https://example.com"))

        # Graceful fallback — empty content but OK (no crash)
        assert result["status"] == "OK"
        assert result["result"]["content"] == ""
        assert result["result"]["evidence_receipt"]["void"] == ["no_rendered_inspection"]


class TestRuntimeCanonicalFallback:
    """Canonical handlers in runtime/tools.py fall back to RealityHandler."""

    def test_sense_observe_reality_handler_fallback_path_exists(self):
        """Verify the patched code is present in _arif_sense_observe."""
        from arifosmcp.runtime.tools import _arif_sense_observe

        source = _arif_sense_observe.__code__.co_filename
        with open(source) as f:
            code = f.read()
        assert "RealityHandler cascade (Brave → DDGS fallback)" in code
        assert "_rh_handler.search_brave" in code

    def test_evidence_fetch_reality_handler_fallback_path_exists(self):
        """Verify the patched code is present in _arif_evidence_fetch."""
        from arifosmcp.runtime.tools import _arif_evidence_fetch

        source = _arif_evidence_fetch.__code__.co_filename
        with open(source) as f:
            code = f.read()
        assert "RealityHandler fallback (streaming + render)" in code
        assert "_rh_handler.fetch_url" in code
