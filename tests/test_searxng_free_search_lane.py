"""M365 free-search lane — SearXNG localhost + ladder contract tests.

Directive (Arif 2026-10-29): replace the paid Brave dependency with the
keyless sovereign lane. Cascade contract under test:
    SearXNG(localhost) → Brave (only when a key is configured) → SABAR.
Every path must return an explicit, honest envelope — never a fabricated
success, never an empty payload masquerading as an answer (F2).
"""

import json
import socket
import urllib.request

import pytest

import arifosmcp.runtime.tools as T


class _FakeResp:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _capture_urlopen(payload, seen):
    def _fake(req, timeout=None):
        seen["url"] = getattr(req, "full_url", None) or getattr(req, "url", None)
        seen["timeout"] = timeout
        return _FakeResp(payload)

    return _fake


SEARX_TWO_HITS = {
    "results": [
        {
            "title": "A",
            "url": "https://a.example",
            "content": "snippet a",
            "engine": "bing",
        },
        {
            "title": "B",
            "url": "https://b.example",
            "content": "snippet b",
            "engine": "google",
        },
    ],
    "unresponsive_engines": [["duckduckgo", "CAPTCHA"]],
}


def test_searx_maps_hits_and_pins_engines(monkeypatch):
    seen = {}
    monkeypatch.setattr(
        urllib.request, "urlopen", _capture_urlopen(SEARX_TWO_HITS, seen)
    )
    out = T._searxng_web_search("malaysia ringgit", max_results=5)
    assert out["status"] == "success" and out["verdict"] == "SEAL"
    assert out["result_count"] == 2
    h0 = out["hits"][0]
    assert (
        h0["title"] == "A"
        and h0["link"] == "https://a.example"
        and h0["snippet"] == "snippet a"
    )
    assert h0["engine"] == "bing"
    assert "engines=bing" in seen["url"] and "format=json" in seen["url"]
    assert out["unresponsive_engines"] == [
        {"engine": "duckduckgo", "reason": "CAPTCHA"}
    ]
    assert out["provider"] == "searxng_localhost"


def test_searx_empty_is_sabar_not_success(monkeypatch):
    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        _capture_urlopen({"results": [], "unresponsive_engines": []}, {}),
    )
    out = T._searxng_web_search("nothing here", max_results=3)
    assert out["status"] == "empty"
    assert out["verdict"] == "SABAR"
    assert out["hits"] == []


def test_searx_transport_error_is_explicit(monkeypatch):
    def _boom(req, timeout=None):
        raise socket.timeout("engine took too long")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    out = T._searxng_web_search("q", max_results=3)
    assert out["status"] == "error" and out["verdict"] == "SABAR"
    assert "timeout" in out["error"].lower()


def test_ladder_prefers_searx_and_names_answerer(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", _capture_urlopen(SEARX_TWO_HITS, {}))
    out = T._free_web_search("q", max_results=2)
    assert out["provider"] == "searxng_localhost" and out["result_count"] == 2


def test_ladder_falls_to_brave_only_with_key(monkeypatch):
    empty = {"results": [], "unresponsive_engines": []}
    brave_payload = {
        "web": {
            "results": [{"title": "B", "url": "https://brave/x", "description": "d"}]
        }
    }

    calls = {"n": 0}

    def _fake(req, timeout=None):
        calls["n"] += 1
        return _FakeResp(brave_payload if calls["n"] > 1 else empty)

    monkeypatch.setattr(urllib.request, "urlopen", _fake)
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    out = T._free_web_search("q", max_results=3)
    assert out["verdict"] == "SABAR" and out["hits"] == []
    assert out["provider"] == "searxng_localhost"
    assert calls["n"] == 1, "brave must NOT be called without a configured key"

    calls["n"] = 0
    monkeypatch.setenv("BRAVE_API_KEY", "test-key-not-real")
    out2 = T._free_web_search("q", max_results=3)
    assert out2["hits"] and out2["provider"] == "brave_api"
    assert out2.get("fallback_of") == "searxng_empty_or_error"


def _live_searx():
    try:
        with socket.create_connection(("127.0.0.1", 8080), timeout=2):
            return True
    except Exception:
        return False


# real call — proves the deployed box answers through the sovereign lane
@pytest.mark.skipif(not _live_searx(), reason="localhost SearXNG not reachable")
def test_live_searx_returns_real_results():
    out = T._searxng_web_search("malaysia economy ringgit outlook", max_results=5)
    assert out["status"] == "success", out
    assert out["result_count"] >= 1
    assert all(h["link"].startswith("http") for h in out["hits"])
