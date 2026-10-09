import json
import pytest
from arifosmcp.transport import AirlockASGIMiddleware as ExportedAirlockASGIMiddleware
from arifosmcp.transport.airlock import (
    AirlockASGIMiddleware,
    process_request,
    record_airlock_result,
    reset_airlock_metrics,
    get_airlock_metrics,
)
from arifosmcp.transport.canonical_envelope import CanonicalEnvelope
from arifosmcp.transport.dialects.streamable_http import streamable_http_adapter
from arifosmcp.transport.errors import TransportFaultCode, build_transport_error_envelope


def test_transport_package_reexports_real_middleware():
    assert ExportedAirlockASGIMiddleware is AirlockASGIMiddleware


def test_streamable_http_canary_tools_do_not_require_session():
    result = streamable_http_adapter(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "arif_ping", "arguments": {}},
        }
    )
    assert result.transport_error is None
    assert result.envelope is not None
    assert result.envelope.tool_name == "arif_ping"
    assert result.envelope.tool_args == {}


def test_unexposed_legacy_name_is_naming_fault_not_session_fault():
    """A name absent from the live public surface must not be answered with a
    session fault. Regression: `arif_session_init` (legacy, still taught by our
    own docs and scripts/init_live_demo.py) returned ARIF_SESSION_NOT_FOUND, so
    an external auditor concluded the kernel had a bootstrap paradox — "init
    requires the session init creates". Measured 2026-10-01.
    """
    for legacy in ("arif_session_init", "session_init", "forge_session_init", "zzz"):
        result = streamable_http_adapter(
            {
                "jsonrpc": "2.0",
                "id": 12,
                "method": "tools/call",
                "params": {"name": legacy, "arguments": {}},
            }
        )
        assert result.transport_error is None, f"{legacy}: naming fault reported as session fault"
        assert result.envelope is not None, f"{legacy}: must fall through to dispatch"
        assert result.envelope.tool_name == legacy


def test_exposed_read_verb_still_requires_session():
    """The naming-fault fix must not un-gate registered verbs."""
    result = streamable_http_adapter(
        {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {"name": "arif_observe", "arguments": {}},
        }
    )
    assert result.transport_error is not None
    assert result.transport_error["error"]["data"]["code"] == "ARIF_SESSION_NOT_FOUND"


def test_session_fault_message_does_not_overclaim_scope():
    """Only read-class verbs are blocked pre-session under partial_enforce, so
    the envelope must not claim a session is needed for "all remote operations".
    """
    result = streamable_http_adapter(
        {
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/call",
            "params": {"name": "arif_observe", "arguments": {}},
        }
    )
    message = result.transport_error["error"]["message"]
    assert "all remote operations" not in message
    assert "arif_init" in message, "must still name the fix"


def test_transport_error_preserves_jsonrpc_id():
    error = build_transport_error_envelope(
        TransportFaultCode.ARIF_SESSION_NOT_FOUND,
        "missing session",
        request_id="rpc-123",
    )
    assert error["jsonrpc"] == "2.0"
    assert error["id"] == "rpc-123"


def test_protocol_mismatch_returns_dict_not_exception():
    """Regression: bare AirlockError in transport_error crashed metrics → MCP 500."""
    result = process_request(
        {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "initialize",
            "protocol_version": "99.99.99",
        }
    )
    assert result.envelope is None
    assert isinstance(result.transport_error, dict)
    assert result.transport_error["id"] == 42
    assert "error" in result.transport_error
    reset_airlock_metrics()
    record_airlock_result(result, mode="shadow")  # must not raise
    metrics = get_airlock_metrics()
    assert metrics["transport_errors"] == 1
    assert metrics["last_error"]["code"] == "ARIF_PROTOCOL_VERSION_MISMATCH"


class MockASGIApp:
    def __init__(self):
        self.scope = None

    async def __call__(self, scope, receive, send):
        self.scope = scope
        # Consume receive
        await receive()
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b'{"jsonrpc": "2.0", "result": {"ok": true}, "id": 1}',
            }
        )


@pytest.mark.anyio
async def test_airlock_middleware_off(monkeypatch):
    monkeypatch.setenv("ARIF_AIRLOCK_MODE", "off")
    app = MockASGIApp()
    middleware = AirlockASGIMiddleware(app)

    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def mock_receive():
        return {
            "type": "http.request",
            "body": b'{"jsonrpc": "2.0", "method": "arif_ping", "params": {}, "id": 1}',
            "more_body": False,
        }

    responses = []

    async def mock_send(message):
        responses.append(message)

    await middleware(scope, mock_receive, mock_send)
    assert app.scope is not None
    assert "airlock_envelope" not in app.scope


@pytest.mark.anyio
async def test_airlock_middleware_shadow(monkeypatch):
    reset_airlock_metrics()
    monkeypatch.setenv("ARIF_AIRLOCK_MODE", "shadow")
    app = MockASGIApp()
    middleware = AirlockASGIMiddleware(app)

    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "headers": [
            (b"content-type", b"application/json"),
            (b"mcp-session-id", b"test-session-123"),
        ],
    }

    async def mock_receive():
        return {
            "type": "http.request",
            "body": b'{"jsonrpc": "2.0", "method": "arif_ping", "params": {}, "id": 1}',
            "more_body": False,
        }

    responses = []

    async def mock_send(message):
        responses.append(message)

    await middleware(scope, mock_receive, mock_send)
    assert app.scope is not None
    assert "airlock_envelope" in app.scope
    env = app.scope["airlock_envelope"]
    assert isinstance(env, CanonicalEnvelope)
    assert env.tool_name == "arif_ping"
    assert env.session_state["transport"]["mcp_session_id"] == "test-session-123"
    metrics = get_airlock_metrics()
    assert metrics["total_requests"] == 1
    assert metrics["normalized_ok"] == 1


@pytest.mark.anyio
async def test_airlock_middleware_enforce_success(monkeypatch):
    monkeypatch.setenv("ARIF_AIRLOCK_MODE", "enforce")
    app = MockASGIApp()
    middleware = AirlockASGIMiddleware(app)

    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "headers": [
            (b"content-type", b"application/json"),
            (b"mcp-session-id", b"enforce-sess"),
        ],
    }

    async def mock_receive():
        return {
            "type": "http.request",
            "body": b'{"jsonrpc": "2.0", "method": "arif_ping", "params": {}, "id": 1}',
            "more_body": False,
        }

    responses = []

    async def mock_send(message):
        responses.append(message)

    await middleware(scope, mock_receive, mock_send)
    assert app.scope is not None
    assert "airlock_envelope" in app.scope
    env = app.scope["airlock_envelope"]
    assert env.tool_name == "arif_ping"
    assert env.session_state["transport"]["mcp_session_id"] == "enforce-sess"


@pytest.mark.anyio
async def test_airlock_middleware_enforce_block(monkeypatch):
    monkeypatch.setenv("ARIF_AIRLOCK_MODE", "enforce")
    app = MockASGIApp()
    middleware = AirlockASGIMiddleware(app)

    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def mock_receive():
        return {
            "type": "http.request",
            "body": b'{"jsonrpc": "2.0", "method": "arif_ping", "dialect": "unknown-dialect", "id": 1}',
            "more_body": False,
        }

    responses = []

    async def mock_send(message):
        responses.append(message)

    await middleware(scope, mock_receive, mock_send)
    assert app.scope is None
    assert len(responses) == 2
    assert responses[0]["type"] == "http.response.start"
    assert responses[0]["status"] == 200

    body = json.loads(responses[1]["body"].decode())
    assert "error" in body
    assert body["error"]["data"]["code"] == "ARIF_TRANSPORT_MISMATCH"
    assert body["id"] == 1


@pytest.mark.anyio
async def test_airlock_middleware_partial_blocks_read_like_errors(monkeypatch):
    reset_airlock_metrics()
    monkeypatch.setenv("ARIF_AIRLOCK_MODE", "partial_enforce")
    app = MockASGIApp()
    middleware = AirlockASGIMiddleware(app)

    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def mock_receive():
        return {
            "type": "http.request",
            "body": b'{"jsonrpc": "2.0", "method": "arif_ping", "dialect": "unknown-dialect", "id": 7}',
            "more_body": False,
        }

    responses = []

    async def mock_send(message):
        responses.append(message)

    await middleware(scope, mock_receive, mock_send)
    assert app.scope is None
    assert (b"x-arifos-airlock", b"partial-block") in responses[0]["headers"]
    body = json.loads(responses[1]["body"].decode())
    assert body["id"] == 7
    metrics = get_airlock_metrics()
    assert metrics["blocked"] == 1
    assert metrics["partial_enforced"] == 1


@pytest.mark.anyio
async def test_airlock_middleware_receive_timeout(monkeypatch):
    import asyncio

    monkeypatch.setenv("ARIF_AIRLOCK_MODE", "shadow")
    monkeypatch.setenv("ARIF_AIRLOCK_RECEIVE_TIMEOUT", "0.05")

    app = MockASGIApp()
    middleware = AirlockASGIMiddleware(app)

    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def mock_receive_stalled():
        await asyncio.sleep(0.5)
        return {"type": "http.request", "body": b"", "more_body": False}

    responses = []

    async def mock_send(message):
        responses.append(message)

    await middleware(scope, mock_receive_stalled, mock_send)
    assert app.scope is None
    assert len(responses) == 2
    assert responses[0]["status"] == 408
    assert (b"x-arifos-airlock", b"timeout") in responses[0]["headers"]


@pytest.mark.anyio
async def test_airlock_middleware_client_disconnect(monkeypatch):
    monkeypatch.setenv("ARIF_AIRLOCK_MODE", "shadow")
    app = MockASGIApp()
    middleware = AirlockASGIMiddleware(app)

    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def mock_receive_disconnect():
        return {"type": "http.disconnect"}

    responses = []

    async def mock_send(message):
        responses.append(message)

    await middleware(scope, mock_receive_disconnect, mock_send)
    assert app.scope is None
    assert len(responses) == 0

