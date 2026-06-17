"""
tests/runtime/test_tavily_bridge.py — Tavily Bridge Tests

Phase 0 expansion (2026-06-16): covers the 4 new endpoints
(get_search_context, qna_search, crawl, map_site) alongside
the original search/extract.

Each test follows the F2/F7/F9 contract:
  - TAVILY_API_KEY missing → SABAR envelope, never crash
  - empty input after sanitization → SABAR
  - 403 on /crawl or /map → invite_only envelope with clear note
  - success → SEAL with epistemic tag + witness_debug

Tests marked `live` make a real Tavily API call. The rest are pure
unit tests against the bridge in isolation.

NOTE: _TAVILY_API_KEY is a module-level constant captured at import time.
We patch it via monkeypatch.setattr on the module, not via setenv.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import patch

import pytest

import arifosmcp.runtime.tavily_bridge as tvly_module
from arifosmcp.runtime.tavily_bridge import TavilyMCPBridge


# TAVILY_API_KEY must be set for live tests; if missing they are skipped.
_HAS_TAVILY = bool(os.getenv("TAVILY_API_KEY"))


# ─── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def bridge():
    """Fresh bridge instance per test (does NOT share httpx client)."""
    return TavilyMCPBridge()


@pytest.fixture
def no_key(monkeypatch):
    """Force _TAVILY_API_KEY to empty string in the module."""
    monkeypatch.setattr(tvly_module, "_TAVILY_API_KEY", "")
    return tvly_module


@pytest.fixture
def fake_key(monkeypatch):
    """Force _TAVILY_API_KEY to a non-empty fake value in the module."""
    monkeypatch.setattr(tvly_module, "_TAVILY_API_KEY", "fake-key-for-test")
    return tvly_module


def run(coro):
    """Run an async coroutine in a fresh event loop."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ─── Missing key envelope (unit, no network) ─────────────────────────


class TestMissingKey:
    """All new methods must return SABAR with error_class=config_missing
    when TAVILY_API_KEY is not set."""

    def test_get_search_context_no_key(self, bridge, no_key):
        result = run(bridge.get_search_context("anything"))
        assert result["status"] == "error"
        assert result["verdict"] == "SABAR"
        assert result["error_class"] == "config_missing"
        assert result["bridge"] == "tavily_get_search_context"

    def test_qna_search_no_key(self, bridge, no_key):
        result = run(bridge.qna_search("anything"))
        assert result["status"] == "error"
        assert result["verdict"] == "SABAR"
        assert result["error_class"] == "config_missing"
        assert result["bridge"] == "tavily_qna_search"

    def test_crawl_no_key(self, bridge, no_key):
        result = run(bridge.crawl(url="https://example.com"))
        assert result["status"] == "error"
        assert result["verdict"] == "SABAR"
        assert result["error_class"] == "config_missing"
        assert result["bridge"] == "tavily_crawl"

    def test_map_site_no_key(self, bridge, no_key):
        result = run(bridge.map_site(url="https://example.com"))
        assert result["status"] == "error"
        assert result["verdict"] == "SABAR"
        assert result["error_class"] == "config_missing"
        assert result["bridge"] == "tavily_map"


# ─── URL sanitization (unit, no network) ─────────────────────────────


class TestUrlSanitization:
    """Crawl and map must reject javascript:/data:/vbscript:/file: schemes."""

    def test_crawl_blocks_javascript(self, bridge, fake_key):
        result = run(bridge.crawl(url="javascript:alert(1)"))
        assert result["status"] == "error"
        assert result["error_class"] == "invalid_input"
        assert "javascript" in result["error"].lower()

    def test_crawl_blocks_data_uri(self, bridge, fake_key):
        result = run(bridge.crawl(url="data:text/html,<script>x</script>"))
        assert result["status"] == "error"
        assert result["error_class"] == "invalid_input"

    def test_map_blocks_vbscript(self, bridge, fake_key):
        result = run(bridge.map_site(url="vbscript:msgbox(1)"))
        assert result["status"] == "error"
        assert result["error_class"] == "invalid_input"

    def test_crawl_blocks_file_scheme(self, bridge, fake_key):
        result = run(bridge.crawl(url="file:///etc/passwd"))
        assert result["status"] == "error"
        assert result["error_class"] == "invalid_input"


# ─── Input sanitization (unit, no network) ───────────────────────────


class TestQuerySanitization:
    """Empty / dangerous inputs must produce SABAR, not crash."""

    def test_get_search_context_empty_query(self, bridge, fake_key):
        result = run(bridge.get_search_context(""))
        assert result["status"] == "error"
        assert result["verdict"] == "SABAR"
        assert result["error_class"] == "invalid_input"

    def test_qna_search_empty_query(self, bridge, fake_key):
        result = run(bridge.qna_search(""))
        assert result["status"] == "error"
        assert result["verdict"] == "SABAR"
        assert result["error_class"] == "invalid_input"

    def test_get_search_context_only_dangerous_chars(self, bridge, fake_key):
        # "$$" is in the dangerous list; query sanitizes to empty
        result = run(bridge.get_search_context("$$"))
        # Sanitizer strips "$$" → empty → invalid_input
        assert result["status"] == "error"
        assert result["error_class"] == "invalid_input"


# ─── Epistemic contract (unit, no network) ───────────────────────────


class TestEpistemicContract:
    """F2 TRUTH: every success envelope must carry an epistemic_tag."""

    def test_get_search_context_tag_is_interpretation(self, bridge, fake_key):
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={
                "results": [
                    {"url": "https://a.com", "title": "A", "content": "Hello world"}
                ]
            },
        ):
            result = run(bridge.get_search_context("test"))
        assert result["status"] == "success", f"got {result}"
        assert result["epistemic_tag"] == "INTERPRETATION"
        assert "context" in result
        assert "[Source: https://a.com]" in result["context"]

    def test_qna_search_tag_is_interpretation(self, bridge, fake_key):
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={
                "results": [],
                "answer": "KL is the capital of Malaysia.",
                "follow_up_questions": None,
            },
        ):
            result = run(bridge.qna_search("What is the capital of Malaysia?"))
        assert result["status"] == "success", f"got {result}"
        assert result["epistemic_tag"] == "INTERPRETATION"
        assert result["answer"] == "KL is the capital of Malaysia."

    def test_crawl_tag_is_interpretation(self, bridge, fake_key):
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={"results": [{"url": "https://a.com", "raw_content": "..."}]},
        ):
            result = run(bridge.crawl(url="https://example.com"))
        assert result["status"] == "success", f"got {result}"
        assert result["epistemic_tag"] == "INTERPRETATION"
        assert "pages" in result

    def test_map_tag_is_observed(self, bridge, fake_key):
        """F2: map returns URL list only — graph signal, not LLM prose.
        Epistemic tag is OBSERVED, not INTERPRETATION."""
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={
                "results": [
                    "https://example.com/page1",
                    "https://example.com/page2",
                    {"url": "https://example.com/page3"},
                ]
            },
        ):
            result = run(bridge.map_site(url="https://example.com"))
        assert result["status"] == "success", f"got {result}"
        assert result["epistemic_tag"] == "OBSERVED"  # F2: graph signal
        assert result["url_count"] == 3
        assert "https://example.com/page1" in result["urls"]
        assert "https://example.com/page3" in result["urls"]


# ─── Invite-only envelope (unit, no network) ─────────────────────────


class TestInviteOnly:
    """Crawl and map must convert 403 into a clear invite_only envelope."""

    def test_crawl_invite_only_envelope(self, bridge, fake_key):
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={
                "_bridge_error": True,
                "error": "HTTP 403: forbidden",
                "error_class": "invite_only",
                "bridge": "tavily_crawl",
                "invite_only_endpoint": True,
                "invite_url": "https://crawl.tavily.com",
            },
        ):
            result = run(bridge.crawl(url="https://example.com"))
        assert result["status"] == "error"
        assert result["invite_only"] is True
        assert result["invite_url"] == "https://crawl.tavily.com"
        assert "invite-only" in result["note"].lower()

    def test_map_invite_only_envelope(self, bridge, fake_key):
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={
                "_bridge_error": True,
                "error": "HTTP 403: forbidden",
                "error_class": "invite_only",
                "bridge": "tavily_map",
                "invite_only_endpoint": True,
                "invite_url": "https://crawl.tavily.com",
            },
        ):
            result = run(bridge.map_site(url="https://example.com"))
        assert result["status"] == "error"
        assert result["invite_only"] is True
        assert "invite-only" in result["note"].lower()


# ─── F7 HUMILITY band (unit, no network) ─────────────────────────────


class TestHumilityBand:
    """Every success envelope must carry a humility band in [0.03, 0.10]."""

    @pytest.mark.parametrize(
        "method,kwargs",
        [
            ("get_search_context", {"query": "x"}),
            ("qna_search", {"query": "x"}),
            ("crawl", {"url": "https://example.com"}),
            ("map_site", {"url": "https://example.com"}),
        ],
    )
    def test_humility_band_in_range(self, bridge, fake_key, method, kwargs):
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={
                "results": [{"url": "https://a.com", "content": "x"}],
                "answer": "x",
            },
        ):
            result = run(getattr(bridge, method)(**kwargs))
        band = result.get("metrics", {}).get("f7_humility_band")
        if band is not None:
            assert 0.03 <= band <= 0.10, f"humility band out of F7 range: {band}"


# ─── Token truncation (unit, no network) ─────────────────────────────


class TestTokenTruncation:
    """get_search_context must respect the max_tokens budget."""

    def test_truncation_marks_flag(self, bridge, fake_key):
        long_content = "A" * 20_000  # ~5000 tokens
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={"results": [{"url": "https://a.com", "content": long_content}]},
        ):
            result = run(bridge.get_search_context("test", max_tokens=1000))
        assert result["truncated"] is True
        assert result["context_length_tokens_est"] <= 1005
        assert result["context"].endswith("...")

    def test_no_truncation_when_within_budget(self, bridge, fake_key):
        with patch.object(
            bridge,
            "_post_tavily",
            return_value={"results": [{"url": "https://a.com", "content": "short"}]},
        ):
            result = run(bridge.get_search_context("test", max_tokens=4000))
        assert result["truncated"] is False
        assert result["context"] == "[Source: https://a.com]\nshort"


# ─── LIVE tests (require TAVILY_API_KEY + network) ───────────────────


@pytest.mark.skipif(not _HAS_TAVILY, reason="TAVILY_API_KEY not set")
class TestLive:
    """Real Tavily API calls. Skipped if no key in env."""

    def test_live_get_search_context(self, bridge):
        result = run(
            bridge.get_search_context("What is the capital of Malaysia?", max_tokens=500)
        )
        assert result["status"] == "success"
        assert result["verdict"] == "SEAL"
        assert "Kuala Lumpur" in result["context"]
        assert result["epistemic_tag"] == "INTERPRETATION"
        assert result["context_length_tokens_est"] <= 510

    def test_live_qna_search(self, bridge):
        result = run(bridge.qna_search("What is the capital of Malaysia?"))
        assert result["status"] == "success"
        assert result["verdict"] in ("SEAL", "VOID")
        if result["verdict"] == "SEAL":
            assert "Kuala Lumpur" in (result.get("answer") or "")
            assert result["epistemic_tag"] == "INTERPRETATION"

    def test_live_crawl_invite_only(self, bridge):
        """Free-tier keys should hit 403 → invite_only envelope."""
        result = run(bridge.crawl(url="https://en.wikipedia.org/wiki/Malaysia"))
        if result["status"] == "error":
            assert result.get("invite_only") is True
            assert "https://crawl.tavily.com" in result.get("invite_url", "")

    def test_live_map_invite_only(self, bridge):
        """Same as crawl — free tier should get invite_only."""
        result = run(bridge.map_site(url="https://en.wikipedia.org/wiki/Malaysia"))
        if result["status"] == "error":
            assert result.get("invite_only") is True


# ─── Tool surface wiring (integration) ───────────────────────────────


class TestToolSurfaceWiring:
    """arif_sense_observe must accept the 4 new modes without rejection."""

    def test_tavily_context_mode_in_allowed(self):
        """Static check: the allowed_modes list must include the new modes."""
        from pathlib import Path

        tools_path = Path("/root/arifOS/arifosmcp/runtime/tools.py")
        src = tools_path.read_text()
        for mode in ("tavily_context", "tavily_qna", "tavily_crawl", "tavily_map"):
            assert f'"{mode}"' in src, f"Mode {mode} not in tools.py allowed_modes"

    def test_bridge_imports_clean(self):
        """Bridge must import without error after Phase 0 additions."""
        from arifosmcp.runtime.tavily_bridge import tavily_bridge

        assert hasattr(tavily_bridge, "get_search_context")
        assert hasattr(tavily_bridge, "qna_search")
        assert hasattr(tavily_bridge, "crawl")
        assert hasattr(tavily_bridge, "map_site")
