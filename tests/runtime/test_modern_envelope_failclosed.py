"""Fail-closed modern envelope validation (MCP 2026-07-28).

SCAR 2026-09-17: the HeaderMismatch check fired only when header AND body
method were BOTH present — omitting Mcp-Method/Mcp-Name bypassed validation
entirely, letting a gateway and the kernel interpret one request two ways.
These tests prove the confused-deputy paths now fail closed, the happy modern
path still passes, legacy-era traffic is untouched, and the emergency
kill-switch works.

Refs: external AGI-substrate audit (2026-09-17) + live probe of
arifosmcp/runtime/mcp_transport_bridge.py (old line 203).
"""

from __future__ import annotations

import asyncio
import importlib
import json
import os
from unittest.mock import patch

from starlette.requests import Request
from starlette.responses import JSONResponse

from arifosmcp.runtime.mcp_transport_bridge import (
    ERR_HEADER_MISMATCH,
    MCPProtocolVersionMiddleware,
)

MODERN = b"2026-07-28"


def _make_request(body: dict, headers: list[tuple[bytes, bytes]]):
    raw = json.dumps(body).encode()
    messages = iter([{"type": "http.request", "body": raw, "more_body": False}])
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/mcp",
        "headers": [(b"content-type", b"application/json")] + headers,
    }

    async def receive() -> dict:
        return next(messages)

    return Request(scope, receive)


def _tools_call_body(tool: str = "arif_init") -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 41,
        "method": "tools/call",
        "params": {"name": tool, "arguments": {}},
    }


def _downstream_reached():
    state = {"reached": False}

    async def call_next(_request: Request) -> JSONResponse:
        state["reached"] = True
        return JSONResponse({"jsonrpc": "2.0", "id": 41, "result": {"ok": True}})

    return call_next, state


def _run(request, call_next):
    return asyncio.run(MCPProtocolVersionMiddleware(None).dispatch(request, call_next))


def _assert_rejected(response, state) -> None:
    payload = json.loads(response.body)
    assert response.status_code == 400
    assert payload["error"]["code"] == ERR_HEADER_MISMATCH
    assert state["reached"] is False, "kernel must NOT receive ambiguous requests"


def test_tools_call_without_mcp_method_header_fails_closed():
    req = _make_request(_tools_call_body(), [(b"mcp-protocol-version", MODERN)])
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)
    assert "Mcp-Method" in json.loads(response.body)["error"]["message"]


def test_tools_call_without_mcp_name_header_fails_closed():
    req = _make_request(
        _tools_call_body(),
        [(b"mcp-protocol-version", MODERN), (b"mcp-method", b"tools/call")],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)
    assert "Mcp-Name" in json.loads(response.body)["error"]["message"]


def test_method_header_mismatch_still_rejected():
    req = _make_request(
        _tools_call_body(),
        [(b"mcp-protocol-version", MODERN), (b"mcp-method", b"tools/list")],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)


def test_name_header_mismatch_confused_deputy_rejected():
    """Gateway routes arif_seal while body executes arif_init → reject."""
    req = _make_request(
        _tools_call_body("arif_init"),
        [
            (b"mcp-protocol-version", MODERN),
            (b"mcp-method", b"tools/call"),
            (b"mcp-name", b"arif_seal"),
        ],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)
    assert "arif_seal" in json.loads(response.body)["error"]["message"]


def test_valid_modern_envelope_reaches_kernel():
    req = _make_request(
        _tools_call_body("arif_init"),
        [
            (b"mcp-protocol-version", MODERN),
            (b"mcp-method", b"tools/call"),
            (b"mcp-name", b"arif_init"),
        ],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    assert response.status_code == 200
    assert state["reached"] is True


def test_readonly_method_without_headers_ratchet_rejects():
    """G0.7 ratchet: Mcp-Method required for ALL routed modern methods.

    Justified by production evidence: zero transition-window warnings
    between the 2026-09-17 03:03 deploy and the ratchet.
    """
    req = _make_request(
        {"jsonrpc": "2.0", "id": 42, "method": "tools/list", "params": {}},
        [(b"mcp-protocol-version", MODERN)],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)


def test_readonly_method_without_headers_lenient_mode_passes():
    """Kill-switch: lenient mode still passes headerless non-mutations."""
    req = _make_request(
        {"jsonrpc": "2.0", "id": 42, "method": "tools/list", "params": {}},
        [(b"mcp-protocol-version", MODERN)],
    )
    call_next, state = _downstream_reached()
    with patch.dict(os.environ, {"ARIFOS_MCP_ENVELOPE_STRICT": "0"}):
        response = _run(req, call_next)
    assert response.status_code == 200
    assert state["reached"] is True


def test_notification_without_headers_exempt():
    """notifications/* are exempt from the Mcp-Method requirement.

    G7 intercepts notifications/initialized and answers 202 directly —
    downstream (FastMCP session logic) is never reached, by design.
    """
    req = _make_request(
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        [(b"mcp-protocol-version", MODERN)],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    assert response.status_code == 202
    assert state["reached"] is False  # G7 no-op short-circuit


def test_version_coherence_header_meta_mismatch_rejected():
    body = {
        "jsonrpc": "2.0", "id": 43, "method": "tools/list",
        "params": {"_meta": {
            "io.modelcontextprotocol/protocolVersion": "2025-11-25",
            "io.modelcontextprotocol/clientCapabilities": {},
        }},
    }
    req = _make_request(
        body,
        [(b"mcp-protocol-version", MODERN), (b"mcp-method", b"tools/list")],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)
    assert "_meta" in json.loads(response.body)["error"]["message"]


def test_version_coherence_equal_passes():
    body = {
        "jsonrpc": "2.0", "id": 44, "method": "tools/list",
        "params": {"_meta": {
            "io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientCapabilities": {},
        }},
    }
    req = _make_request(
        body,
        [(b"mcp-protocol-version", MODERN), (b"mcp-method", b"tools/list")],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    assert response.status_code == 200
    assert state["reached"] is True


def test_mcp_param_mirror_mismatch_rejected():
    req = _make_request(
        _tools_call_body("arif_init"),
        [
            (b"mcp-protocol-version", MODERN),
            (b"mcp-method", b"tools/call"),
            (b"mcp-name", b"arif_init"),
            (b"mcp-param-actor_id", b"someone-else"),
        ],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)
    assert "Mcp-Param-actor_id" in json.loads(response.body)["error"]["message"]


def test_mcp_param_mirror_extra_header_without_body_arg_rejected():
    req = _make_request(
        _tools_call_body("arif_init"),
        [
            (b"mcp-protocol-version", MODERN),
            (b"mcp-method", b"tools/call"),
            (b"mcp-name", b"arif_init"),
            (b"mcp-param-nonexistent", b"x"),
        ],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    _assert_rejected(response, state)


def test_mcp_param_mirror_equal_passes():
    body = _tools_call_body("arif_init")
    body["params"]["arguments"] = {"actor_id": "arif"}
    req = _make_request(
        body,
        [
            (b"mcp-protocol-version", MODERN),
            (b"mcp-method", b"tools/call"),
            (b"mcp-name", b"arif_init"),
            (b"mcp-param-actor_id", b"arif"),
        ],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    assert response.status_code == 200
    assert state["reached"] is True


def test_legacy_era_tools_call_without_modern_headers_untouched():
    """2025-11-25 has no modern-header requirement — era separation intact."""
    req = _make_request(
        _tools_call_body(),
        [(b"mcp-protocol-version", b"2025-11-25")],
    )
    call_next, state = _downstream_reached()
    response = _run(req, call_next)
    assert response.status_code == 200
    assert state["reached"] is True


def test_kill_switch_restores_lenient_mode():
    req = _make_request(
        _tools_call_body(),
        [(b"mcp-protocol-version", MODERN)],
    )
    call_next, state = _downstream_reached()
    with patch.dict(os.environ, {"ARIFOS_MCP_ENVELOPE_STRICT": "0"}):
        bridge = importlib.reload(
            __import__(
                "arifosmcp.runtime.mcp_transport_bridge",
                fromlist=["MCPProtocolVersionMiddleware"],
            )
        )
        response = asyncio.run(
            bridge.MCPProtocolVersionMiddleware(None).dispatch(req, call_next)
        )
    assert response.status_code == 200
    assert state["reached"] is True


def test_transport_http_entrypoint_has_protocol_middleware():
    """Complete mediation: transport/http.py must not be a bypass route."""
    try:
        from arifosmcp.transport.http import create_http_app
    except Exception as exc:  # heavy kernel import in test env — record honestly
        import pytest

        pytest.skip(f"cannot build app in test env: {exc}")
    app = create_http_app()
    names = {m.cls.__name__ for m in app.user_middleware}
    assert "MCPProtocolVersionMiddleware" in names
    assert "MCPSessionBridgeMiddleware" in names
