"""MCP initialize protocol negotiation regression tests."""

import asyncio
import json

from starlette.requests import Request
from starlette.responses import JSONResponse

from arifosmcp.runtime.mcp_transport_bridge import (
    INTEROP_PROTOCOL_VERSION,
    MCPProtocolVersionMiddleware,
    _rewrite_initialize_protocol,
    negotiate_initialize_protocol,
)


def test_supported_client_version_is_echoed():
    assert negotiate_initialize_protocol("2025-11-25") == "2025-11-25"
    assert negotiate_initialize_protocol("2025-03-26") == "2025-03-26"
    # BUGFIX (2026-08-11): 2025-06-18 is a real, published MCP spec version —
    # clients sending it (Claude Desktop's connector included) must be echoed
    # back directly, not hard-rejected before reaching any other kernel logic.
    assert negotiate_initialize_protocol("2025-06-18") == "2025-06-18"


def test_unknown_client_version_uses_legacy_interop_version():
    assert negotiate_initialize_protocol("future-version") == INTEROP_PROTOCOL_VERSION


def test_missing_client_version_is_not_rewritten():
    assert negotiate_initialize_protocol(None) is None
    assert negotiate_initialize_protocol("") is None


def test_initialize_response_rewrites_only_protocol_version():
    response = JSONResponse(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2026-07-28",
                "serverInfo": {"name": "ARIFOS MCP"},
            },
        },
        headers={"Mcp-Session-Id": "session-1"},
    )

    rewritten = _rewrite_initialize_protocol(response, "2025-11-25")
    payload = json.loads(rewritten.body)

    assert payload["result"]["protocolVersion"] == "2025-11-25"
    assert payload["result"]["serverInfo"] == {"name": "ARIFOS MCP"}
    assert rewritten.headers["Mcp-Session-Id"] == "session-1"


def test_middleware_rewrites_legacy_initialize_response():
    async def run() -> None:
        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "initialize",
                "params": {"protocolVersion": "2025-11-25"},
            }
        ).encode()
        messages = iter([{"type": "http.request", "body": body, "more_body": False}])
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/mcp",
            "headers": [(b"content-type", b"application/json")],
        }
        async def receive() -> dict:
            return next(messages)

        request = Request(scope, receive)

        async def call_next(_request: Request) -> JSONResponse:
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "result": {"protocolVersion": "2026-07-28"},
                }
            )

        response = await MCPProtocolVersionMiddleware(None).dispatch(request, call_next)
        assert json.loads(response.body)["result"]["protocolVersion"] == "2025-11-25"

    asyncio.run(run())
