"""
tests/runtime/test_l5_graphiti_bridge_hardening.py
═══════════════════════════════════════════════════════

Truthfulness hardening: legacy bridge treated HTTP 200 as success
regardless of body. Now:
  - HTTP 200 with embedded JSON-RPC error → deferred (failure)
  - HTTP 200 with invalid_api_key sentinel → deferred (failure)
  - HTTP 200 with unparseable body → deferred (failure)
  - HTTP timeout → skipped (network error path, unchanged)
  - Disabled via GRAPHITI_L5_ENABLED=false → disabled (no probe)

Coverage: 401, timeout, success, disabled.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json

import pytest


# ---------------------------------------------------------------------------
# _is_hardened_failure unit tests
# ---------------------------------------------------------------------------
def test_hardened_failure_detects_embedded_invalid_api_key():
    """HTTP 200 + invalid_api_key in JSON-RPC error → failure."""
    from arifosmcp.runtime.l5_graphiti_bridge import _is_hardened_failure

    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32001,
                "message": "invalid_api_key: API key not valid",
            },
        }
    )
    parsed = json.loads(body)
    is_fail, reason = _is_hardened_failure(200, body, parsed)
    assert is_fail is True
    assert reason in ("invalid_api_key", "auth_sentinel", "embedded_error")


def test_hardened_failure_detects_embedded_error_in_result():
    """HTTP 200 with auth sentinel in result body → failure."""
    from arifosmcp.runtime.l5_graphiti_bridge import _is_hardened_failure

    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"status": "unauthorized", "detail": "invalid_api_key"},
        }
    )
    parsed = json.loads(body)
    is_fail, reason = _is_hardened_failure(200, body, parsed)
    assert is_fail is True
    assert reason in _ERROR_SENTINELS or reason == "embedded_error"


def test_hardened_failure_passes_clean_200_response():
    """HTTP 200 with clean JSON-RPC result → NOT a failure."""
    from arifosmcp.runtime.l5_graphiti_bridge import _is_hardened_failure

    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"message": "queued", "memory_id": "abc"},
        }
    )
    parsed = json.loads(body)
    is_fail, reason = _is_hardened_failure(200, body, parsed)
    assert is_fail is False
    assert reason == ""


def test_hardened_failure_unparseable_body_is_failure():
    """HTTP 200 with non-JSON HTML/error page → failure."""
    from arifosmcp.runtime.l5_graphiti_bridge import _is_hardened_failure

    body = "<html>502 Bad Gateway</html>"
    is_fail, reason = _is_hardened_failure(200, body, None)
    assert is_fail is True
    assert reason == "unparseable"


def test_hardened_failure_non_2xx_is_failure():
    """HTTP 4xx/5xx → failure regardless of body."""
    from arifosmcp.runtime.l5_graphiti_bridge import _is_hardened_failure

    body = ""
    is_fail_401, _ = _is_hardened_failure(401, body, None)
    is_fail_500, _ = _is_hardened_failure(500, body, None)
    assert is_fail_401 is True
    assert is_fail_500 is True


# Sentinel list mirror for test introspection
_ERROR_SENTINELS = frozenset(
    (
        "invalid_api_key",
        "unauthorized",
        "forbidden",
        "authentication_failed",
        "auth_failed",
        "missing_credentials",
    )
)


# ---------------------------------------------------------------------------
# bridge_forge_episode integration tests
# ---------------------------------------------------------------------------
class _FakeResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class _FakeClient:
    """Mimics httpx.Client() context manager for forge + session-init paths."""

    def __init__(self, *, init_response: _FakeResponse, call_response: _FakeResponse):
        self._init = init_response
        self._call = call_response
        self._entered = False
        self.calls: list[tuple[str, dict]] = []

    def __enter__(self):
        self._entered = True
        return self

    def __exit__(self, *args):
        self._entered = False
        return False

    def post(self, url, json=None, headers=None):  # noqa: A002 - test param
        self.calls.append((url, json or {}))
        # First call (initialize) returns init; subsequent return call response.
        if json and json.get("method") == "initialize":
            return self._init
        return self._call


def test_bridge_forge_episode_treats_200_invalid_api_key_as_failure(
    monkeypatch,
):
    """The legacy bug: HTTP 200 with invalid_api_key was treated as queued.

    Hardening: now returns status='deferred' with reason='invalid_api_key'.
    """
    from arifosmcp.runtime import l5_graphiti_bridge as bridge

    monkeypatch.setattr(bridge, "_GRAPHITI_ENABLED", True)
    monkeypatch.setattr(bridge, "_SESSION_ID", "fake-session-id")
    monkeypatch.setattr(bridge, "_SESSION_TS", 9_999_999_999.0)  # fresh cache

    init_body = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": 1}})
    init_resp = _FakeResponse(200, init_body)
    call_body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "error": {
                "code": -32001,
                "message": "invalid_api_key: API key not valid",
            },
        }
    )
    call_resp = _FakeResponse(200, call_body)
    fake = _FakeClient(init_response=init_resp, call_response=call_resp)

    def _fake_client_ctor(*args, **kwargs):
        return fake

    monkeypatch.setattr("httpx.Client", _fake_client_ctor)

    result = bridge.bridge_forge_episode(
        memory_id="m1",
        content="hello world",
    )
    assert result["status"] == "deferred", (
        f"expected deferred (hardened) but got {result['status']}"
    )
    assert result["reason"] in ("invalid_api_key", "auth_sentinel", "embedded_error")
    assert result["http_status"] == 200


def test_bridge_forge_episode_treats_401_as_failure(monkeypatch):
    """HTTP 401 (auth failure) → deferred with reason='http_status'."""
    from arifosmcp.runtime import l5_graphiti_bridge as bridge

    monkeypatch.setattr(bridge, "_GRAPHITI_ENABLED", True)
    monkeypatch.setattr(bridge, "_SESSION_ID", "fake-session-id")
    monkeypatch.setattr(bridge, "_SESSION_TS", 9_999_999_999.0)

    init_body = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": 1}})
    init_resp = _FakeResponse(200, init_body)
    call_resp = _FakeResponse(401, "")
    fake = _FakeClient(init_response=init_resp, call_response=call_resp)

    monkeypatch.setattr("httpx.Client", lambda *a, **kw: fake)

    result = bridge.bridge_forge_episode(memory_id="m1", content="hello")
    assert result["status"] == "deferred"
    assert result["reason"] == "http_status"
    assert result["http_status"] == 401


def test_bridge_forge_episode_success_200_clean_body(monkeypatch):
    """HTTP 200 + clean JSON-RPC result → queued (success)."""
    from arifosmcp.runtime import l5_graphiti_bridge as bridge

    monkeypatch.setattr(bridge, "_GRAPHITI_ENABLED", True)
    monkeypatch.setattr(bridge, "_SESSION_ID", "fake-session-id")
    monkeypatch.setattr(bridge, "_SESSION_TS", 9_999_999_999.0)

    init_body = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": 1}})
    init_resp = _FakeResponse(200, init_body)
    call_body = json.dumps(
        {"jsonrpc": "2.0", "id": 2, "result": {"message": "queued"}}
    )
    call_resp = _FakeResponse(200, call_body)
    fake = _FakeClient(init_response=init_resp, call_response=call_resp)

    monkeypatch.setattr("httpx.Client", lambda *a, **kw: fake)

    result = bridge.bridge_forge_episode(memory_id="m1", content="hello")
    assert result["status"] == "queued"
    assert result["http_status"] == 200


def test_bridge_forge_episode_disabled_skips_without_probe(monkeypatch):
    """GRAPHITI_L5_ENABLED=false → disabled, no HTTP probe, no metric increment."""
    from arifosmcp.runtime import l5_graphiti_bridge as bridge

    monkeypatch.setattr(bridge, "_GRAPHITI_ENABLED", False)

    calls = []

    def _bad_client(*args, **kwargs):
        calls.append(("httpx.Client", args, kwargs))
        raise AssertionError("Client must not be constructed when disabled")

    monkeypatch.setattr("httpx.Client", _bad_client)

    result = bridge.bridge_forge_episode(memory_id="m1", content="hi")
    assert result["status"] == "disabled"
    assert len(calls) == 0


def test_bridge_forge_episode_timeout_classified_as_skipped(monkeypatch):
    """httpx.TimeoutException → skipped (network error path)."""
    from arifosmcp.runtime import l5_graphiti_bridge as bridge

    class _TimeoutClient:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, *args, **kwargs):
            import httpx

            raise httpx.TimeoutException("simulated timeout")

    monkeypatch.setattr(bridge, "_GRAPHITI_ENABLED", True)
    monkeypatch.setattr(bridge, "_SESSION_ID", "fake-session-id")
    monkeypatch.setattr(bridge, "_SESSION_TS", 9_999_999_999.0)

    monkeypatch.setattr("httpx.Client", lambda *a, **kw: _TimeoutClient())

    result = bridge.bridge_forge_episode(memory_id="m1", content="hi")
    assert result["status"] == "skipped"
    assert "TimeoutException" in result["reason"] or "Timeout" in result["reason"]


# ---------------------------------------------------------------------------
# bridge_search hardening parity
# ---------------------------------------------------------------------------
def test_bridge_search_treats_200_invalid_api_key_as_degraded(monkeypatch):
    """bridge_search parity with forge_episode hardening."""
    from arifosmcp.runtime import l5_graphiti_bridge as bridge

    monkeypatch.setattr(bridge, "_GRAPHITI_ENABLED", True)
    monkeypatch.setattr(bridge, "_SESSION_ID", "fake-session-id")
    monkeypatch.setattr(bridge, "_SESSION_TS", 9_999_999_999.0)

    init_body = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": 1}})
    init_resp = _FakeResponse(200, init_body)
    call_body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "error": {"code": -32001, "message": "invalid_api_key"},
        }
    )
    call_resp = _FakeResponse(200, call_body)
    fake = _FakeClient(init_response=init_resp, call_response=call_resp)
    monkeypatch.setattr("httpx.Client", lambda *a, **kw: fake)

    result = bridge.bridge_search("test query")
    assert result["status"] == "degraded"
    assert result["nodes"] == []
    assert result["http_status"] == 200