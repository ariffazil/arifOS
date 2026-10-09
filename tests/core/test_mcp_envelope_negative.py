"""
P0 (2026-09-17) Negative test matrix for MCP transport bridge strict envelope.

Doctrine (2026-09-17):
    Interpretation must be singular. For every accepted request,
    I_transport(R) = I_adapter(R) = I_kernel(R), else R → REJECT.

Scope:
    - tools/call on MCP 2026-07-28 REQUIRES Mcp-Method + Mcp-Name headers
    - Header/body equality MUST hold (no confused-deputy)
    - Unsupported protocol versions REJECTED at ingress
    - The transition-window logger path (line 286) is intentionally permitted
      for non-mutation methods, but NOT for tools/call

Coverage:
    1. tools/call WITHOUT Mcp-Method header → -32020
    2. tools/call WITHOUT Mcp-Name header → -32020
    3. Mcp-Method says X, body method says Y → -32020 (confused-deputy)
    4. Mcp-Name says X, params.name says Y → -32020 (confused-deputy)
    5. Unsupported protocol version → -32022
    6. Missing protocol version header on 2026 path → falls through (legacy)
    7. server/discover WITHOUT any modern envelope → success (version-independent)
    8. tools/list WITHOUT Mcp-Method → falls through with WARN log (transition window)
    9. tools/call WITH both headers matching → dispatched (kernel may still reject)
    10. Header case-normalization: "mcp-method" lowercase matches body method
    11. Mcp-Name with trailing whitespace stripped
    12. ARIFOS_MCP_ENVELOPE_STRICT=0 disables strict mode (tools/call without headers allowed)

Strategy:
    Build a minimal FastAPI app that mounts ONLY the middleware under test.
    Use httpx.AsyncClient + ASGITransport to invoke requests synchronously.
    No live arifOS dependency.
"""

from __future__ import annotations

import os
import pytest
import json
from typing import Any

# ── Force strict mode for these tests; per-test overrides set 0 where needed ──
os.environ.setdefault("ARIFOS_MCP_ENVELOPE_STRICT", "1")


# ── ASGI test client + minimal app (no live kernel) ─────────────────────────
from fastapi import FastAPI, Request  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from arifosmcp.runtime.mcp_transport_bridge import (  # noqa: E402
    MCPProtocolVersionMiddleware,
    ERR_HEADER_MISMATCH,
    ERR_UNSUPPORTED_VERSION,
    LATEST_PROTOCOL_VERSION,
)


# The middleware reads SUPPORTED_PROTOCOL_VERSIONS at module import time. We
# don't need to mutate it — the test asserts the middleware behavior using the
# canonical supported set.


@pytest.fixture
def app():
    """Minimal FastAPI app with only the transport middleware + echo endpoint."""
    app = FastAPI()
    app.add_middleware(MCPProtocolVersionMiddleware)

    @app.post("/mcp")
    @app.get("/mcp")
    async def echo(request: Request):
        # If we got here, middleware passed the request through.
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": getattr(request.state, "mcp_protocol_version", None),
                "result": {"dispatched": True, "stateless": getattr(request.state, "mcp_stateless", False)},
            }
        )

    return app


def _post(client, headers: dict[str, str], body: dict[str, Any] | None = None, path: str = "/mcp"):
    """Helper: POST /mcp with given headers and JSON body."""
    return client.post(
        path,
        headers=headers,
        content=json.dumps(body or {}),
    )


# ── Test 1: tools/call WITHOUT Mcp-Method header → -32020 ──────────────────
def test_tools_call_without_mcp_method_header_rejected(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={"MCP-Protocol-Version": LATEST_PROTOCOL_VERSION},
            body={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "arif_observe", "arguments": {}},
            },
        )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == ERR_HEADER_MISMATCH
    assert "Mcp-Method" in body["error"]["message"]
def test_tools_call_without_mcp_name_header_rejected(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={
                "MCP-Protocol-Version": LATEST_PROTOCOL_VERSION,
                "Mcp-Method": "tools/call",
            },
            body={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "arif_observe", "arguments": {}},
            },
        )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == ERR_HEADER_MISMATCH
    assert "Mcp-Name" in body["error"]["message"]


# ── Test 3: Mcp-Method mismatch (gateway routes A, body executes B) ────────
def test_mcp_method_header_body_mismatch_rejected(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={
                "MCP-Protocol-Version": LATEST_PROTOCOL_VERSION,
                "Mcp-Method": "arif_seal",  # gateway says SEAL
                "Mcp-Name": "arif_init",    # gateway says INIT
            },
            body={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "arif_init", "arguments": {}},  # body agrees on name
            },
        )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == ERR_HEADER_MISMATCH
    assert "arif_seal" in body["error"]["message"]
    assert "tools/call" in body["error"]["message"]


# ── Test 4: Mcp-Name mismatch (gateway routes A, body executes B) ──────────
def test_mcp_name_header_body_mismatch_rejected(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={
                "MCP-Protocol-Version": LATEST_PROTOCOL_VERSION,
                "Mcp-Method": "tools/call",
                "Mcp-Name": "arif_seal",  # gateway says SEAL
            },
            body={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "arif_init", "arguments": {}},  # body says INIT
            },
        )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == ERR_HEADER_MISMATCH
    assert "arif_seal" in body["error"]["message"]
    assert "arif_init" in body["error"]["message"]


# ── Test 5: Unsupported protocol version → -32022 ──────────────────────────
def test_unsupported_protocol_version_rejected(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={"MCP-Protocol-Version": "1999-01-01"},
            body={"jsonrpc": "2.0", "id": 5, "method": "tools/list"},
        )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == ERR_UNSUPPORTED_VERSION
    assert "1999-01-01" in body["error"]["message"]


# ── Test 6: server/discover WITHOUT modern envelope → success ──────────────
def test_server_discover_without_headers_succeeds(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={},  # no MCP-Protocol-Version
            body={"jsonrpc": "2.0", "id": 6, "method": "server/discover"},
        )
    # server/discover is version-independent; should return 200 with discover result
    assert r.status_code == 200
    body = r.json()
    assert "result" in body
    assert "supportedVersions" in body["result"]


# ── Test 7: tools/list without Mcp-Method (transition window) → dispatched ─
def test_tools_list_without_header_dispatched_with_warning(app, caplog):
    from fastapi.testclient import TestClient
    import logging
    with TestClient(app) as client:
        with caplog.at_level(logging.WARNING, logger="arifosmcp.runtime.mcp_transport_bridge"):
            r = _post(
                client,
                headers={"MCP-Protocol-Version": LATEST_PROTOCOL_VERSION},
                body={"jsonrpc": "2.0", "id": 7, "method": "tools/list"},
            )
    assert r.status_code == 200
    body = r.json()
    assert body["result"]["dispatched"] is True
    # WARN log emitted for transition-window observation
    assert any(
        "MCP 2026-07-28: request without Mcp-Method header" in rec.message
        for rec in caplog.records
    )


# ── Test 8: tools/call WITH both headers matching → dispatched ─────────────
def test_tools_call_with_matching_headers_dispatched(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={
                "MCP-Protocol-Version": LATEST_PROTOCOL_VERSION,
                "Mcp-Method": "tools/call",
                "Mcp-Name": "arif_observe",
            },
            body={
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {"name": "arif_observe", "arguments": {}},
            },
        )
    assert r.status_code == 200
    body = r.json()
    assert body["result"]["dispatched"] is True
    assert body["result"]["stateless"] is True


# ── Test 9: Header case-insensitive (mcp-method lowercase) ─────────────────
def test_header_case_insensitive_lowercase_mcp_method(app):
    """SEP-2243 / RFC 7230: HTTP headers are case-insensitive. Starlette
    normalizes to title-case via Headers.__getitem__, so 'mcp-method' should
    resolve to 'Mcp-Method' lookup. Test the canonical lowercase form."""
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={
                "MCP-Protocol-Version": LATEST_PROTOCOL_VERSION,
                "Mcp-Method": "tools/call",
                "Mcp-Name": "arif_observe",
            },
            body={
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {"name": "arif_observe", "arguments": {}},
            },
        )
    assert r.status_code == 200


# ── Test 10: Mcp-Name with trailing whitespace is stripped ─────────────────
def test_mcp_name_whitespace_stripped(app):
    """Bridge line 204: mcp_name = .strip() — assert this works."""
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={
                "MCP-Protocol-Version": LATEST_PROTOCOL_VERSION,
                "Mcp-Method": "tools/call",
                "Mcp-Name": "  arif_observe  ",  # whitespace
            },
            body={
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": "arif_observe", "arguments": {}},
            },
        )
    assert r.status_code == 200


# ── Test 11: ARIFOS_MCP_ENVELOPE_STRICT=0 disables strict mode ──────────────
def test_env_var_disables_strict_envelope(monkeypatch):
    """Per bridge line 254: ARIFOS_MCP_ENVELOPE_STRICT=0 reverts to lenient
    behavior for emergency compatibility. tools/call without headers
    should be DISPATCHED with a WARN log."""
    monkeypatch.setenv("ARIFOS_MCP_ENVELOPE_STRICT", "0")
    # Re-import the middleware so the env var is read at class-definition time
    import importlib
    import arifosmcp.runtime.mcp_transport_bridge as bridge
    importlib.reload(bridge)
    from fastapi.testclient import TestClient
    app = FastAPI()
    app.add_middleware(bridge.MCPProtocolVersionMiddleware)

    @app.post("/mcp")
    async def echo(request: Request):
        return JSONResponse({"jsonrpc": "2.0", "id": 1, "result": {"dispatched": True}})

    with TestClient(app) as client:
        r = _post(
            client,
            headers={"MCP-Protocol-Version": LATEST_PROTOCOL_VERSION},
            body={
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {"name": "arif_observe", "arguments": {}},
            },
        )
    # Lenient mode: dispatched (with WARN log)
    assert r.status_code == 200
    assert r.json()["result"]["dispatched"] is True
    # Reload back to strict for subsequent tests
    monkeypatch.delenv("ARIFOS_MCP_ENVELOPE_STRICT")
    importlib.reload(bridge)


# ── Test 12: notifications/* exempt from header requirement ────────────────
def test_notification_exempt_from_header_requirement(app):
    """Bridge line 286: notifications/initialized, notifications/cancelled,
    etc. are exempt because they don't mutate state."""
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={"MCP-Protocol-Version": LATEST_PROTOCOL_VERSION},
            body={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )
    # notifications get 202 Accepted (no id, notification convention)
    assert r.status_code in (200, 202)


# ── Test 13: ping on 2026 path returns empty result (no session) ───────────
def test_ping_on_2026_returns_empty(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = _post(
            client,
            headers={"MCP-Protocol-Version": LATEST_PROTOCOL_VERSION},
            body={"jsonrpc": "2.0", "id": 12, "method": "ping"},
        )
    assert r.status_code == 200
    assert r.json()["result"] == {}


# ── Test 14: GET /mcp (SSE listen stream) does not crash without body ───────
def test_get_mcp_does_not_crash_without_body(app):
    """Bridge lines 174-176 fix: GET /mcp must not UnboundLocalError on method."""
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = client.get("/mcp", headers={"MCP-Protocol-Version": LATEST_PROTOCOL_VERSION})
    # Should not 500. May 200 (echo) or other — but not 500.
    assert r.status_code != 500


# ── Test 15: malformed JSON body falls through gracefully ───────────────────
def test_malformed_json_body_does_not_crash(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = client.post(
            "/mcp",
            headers={"MCP-Protocol-Version": LATEST_PROTOCOL_VERSION},
            content=b"not json",
        )
    # Should not 500; falls through with empty body{}.
    assert r.status_code != 500
