"""Tests for the tailnet identity ingress verifier."""

from __future__ import annotations

import time
from types import SimpleNamespace

import httpx
import pytest
from arifosmcp.runtime.tailnet_identity import (
    TailnetIdentity,
    TailnetIdentityMiddleware,
    current_tailnet_identity,
    sign_payload,
    verify_signed_identity,
)
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

KEY = b"test-key-32-bytes-long-0000000000"


def _payload(**overrides):
    data = {
        "node": "agent-scout-spike.arifOS.ts.net.",
        "tags": ["tag:agent-scout"],
        "caps": {"arif-fazil.com/cap/mcp": [{"tools": ["arif_observe"]}]},
        "user": "",
        "declared_actor": "agent-scout-spike",
    }
    data.update(overrides)
    return data


def _headers(payload=None, *, actor=None, ts=None):
    b64, sig, ts_str = sign_payload(payload or _payload(), KEY, ts=ts)
    headers = {
        "X-Tailnet-Identity": b64,
        "X-Tailnet-Signature": sig,
        "X-Tailnet-Ts": ts_str,
    }
    if actor:
        headers["X-Arif-Actor"] = actor
    return headers


def _app():
    async def whoami(request: Request):
        ident = getattr(request.state, "tailnet_identity", None)
        ctx = current_tailnet_identity()
        return JSONResponse(
            {
                "node": getattr(ident, "node", None),
                "ctx_node": getattr(ctx, "node", None),
            }
        )

    app = Starlette(routes=[Route("/whoami", whoami)])
    app.add_middleware(TailnetIdentityMiddleware)
    return app


async def _get(headers, client_addr=("127.0.0.1", 12345)):
    transport = httpx.ASGITransport(app=_app(), client=client_addr)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/whoami", headers=headers)


@pytest.fixture(autouse=True)
def _key(monkeypatch, tmp_path):
    key_file = tmp_path / "tailnet-ingress.key"
    key_file.write_bytes(KEY)
    monkeypatch.setenv("ARIFOS_TAILNET_INGRESS_KEY_FILE", str(key_file))
    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "observe")


def test_sign_verify_roundtrip():
    b64, sig, ts = sign_payload(_payload(), KEY)
    ident = verify_signed_identity(b64, sig, ts, KEY)
    assert ident is not None
    assert ident.short_node == "agent-scout-spike"
    assert ident.tags == ("tag:agent-scout",)
    assert "arif-fazil.com/cap/mcp" in ident.caps


def test_bad_signature():
    b64, _sig, ts = sign_payload(_payload(), KEY)
    assert verify_signed_identity(b64, "00" * 32, ts, KEY) is None


def test_expired_signature():
    b64, sig, ts = sign_payload(_payload(), KEY, ts=int(time.time()) - 9999)
    assert verify_signed_identity(b64, sig, ts, KEY) is None


def test_actor_binding():
    ident = TailnetIdentity(
        node="agent-scout-spike.arifOS.ts.net.",
        tags=("tag:agent-scout",),
        caps={},
    )
    assert ident.matches_actor("agent-scout-spike")
    assert ident.matches_actor("agent-scout")
    assert not ident.matches_actor("agent-forge")


def test_has_tool():
    ident = TailnetIdentity(
        node="agent-scout-spike.arifOS.ts.net.",
        tags=("tag:agent-scout",),
        caps={"arif-fazil.com/cap/mcp": [{"tools": ["arif_observe"]}]},
    )
    assert ident.has_tool("arif_observe")
    assert not ident.has_tool("arif_forge")


@pytest.mark.asyncio
async def test_observe_attaches_identity():
    r = await _get(_headers())
    assert r.status_code == 200
    assert r.json()["node"].startswith("agent-scout-spike")
    assert r.json()["ctx_node"].startswith("agent-scout-spike")


@pytest.mark.asyncio
async def test_unsigned_passes_without_identity():
    r = await _get({})
    assert r.status_code == 200
    assert r.json()["node"] is None


@pytest.mark.asyncio
async def test_enforce_blocks_actor_mismatch(monkeypatch):
    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "enforce")
    r = await _get(_headers(actor="agent-forge"))
    assert r.status_code == 403
    assert r.json()["error"] == "tailnet_identity_actor_mismatch"


@pytest.mark.asyncio
async def test_enforce_blocks_bad_signature(monkeypatch):
    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "enforce")
    headers = _headers()
    headers["X-Tailnet-Signature"] = "00" * 32
    r = await _get(headers)
    assert r.status_code == 403
    assert r.json()["error"] == "tailnet_identity_invalid"


@pytest.mark.asyncio
async def test_enforce_blocks_public_peer(monkeypatch):
    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "enforce")
    r = await _get(_headers(), client_addr=("203.0.113.5", 12345))
    assert r.status_code == 403
    assert r.json()["error"] == "tailnet_identity_untrusted_peer"


@pytest.mark.asyncio
async def test_enforce_allows_tailnet_peer(monkeypatch):
    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "enforce")
    r = await _get(_headers(), client_addr=("100.64.0.12", 12345))
    assert r.status_code == 200
    assert r.json()["node"].startswith("agent-scout-spike")
    assert r.json()["ctx_node"].startswith("agent-scout-spike")


class _CallCtx:
    method = "tools/call"
    message = SimpleNamespace(name="arif_init", arguments={"actor_id": "agent-forge"})


class _ToolCtx:
    method = "tools/call"

    def __init__(self, name: str, actor: str = "agent-scout-spike") -> None:
        self.message = SimpleNamespace(name=name, arguments={"actor_id": actor})


async def _ok(_context):
    return "ok"


@pytest.mark.asyncio
async def test_actor_binding_observe(monkeypatch):
    from arifosmcp.runtime import tailnet_identity as ti

    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "observe")
    mw = ti.TailnetActorBindingMiddleware()
    ident = ti.TailnetIdentity(
        node="agent-scout-spike.arifOS.ts.net.",
        tags=("tag:agent-scout",),
        caps={},
    )
    token = ti._current_tailnet_identity.set(ident)
    try:
        assert await mw.on_request(_CallCtx(), _ok) == "ok"
    finally:
        ti._current_tailnet_identity.reset(token)


@pytest.mark.asyncio
async def test_actor_binding_enforce(monkeypatch):
    from arifosmcp.runtime import tailnet_identity as ti

    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "enforce")
    mw = ti.TailnetActorBindingMiddleware()
    ident = ti.TailnetIdentity(
        node="agent-scout-spike.arifOS.ts.net.",
        tags=("tag:agent-scout",),
        caps={},
    )
    token = ti._current_tailnet_identity.set(ident)
    try:
        with pytest.raises(PermissionError):
            await mw.on_request(_CallCtx(), _ok)
    finally:
        ti._current_tailnet_identity.reset(token)


@pytest.mark.asyncio
async def test_capability_missing_observe(monkeypatch):
    from arifosmcp.runtime import tailnet_identity as ti

    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "observe")
    mw = ti.TailnetActorBindingMiddleware()
    ident = ti.TailnetIdentity(
        node="agent-scout-spike.arifOS.ts.net.",
        tags=("tag:agent-scout",),
        caps={"arif-fazil.com/cap/mcp": [{"tools": ["arif_observe"]}]},
    )
    token = ti._current_tailnet_identity.set(ident)
    try:
        assert await mw.on_request(_ToolCtx("arif_forge"), _ok) == "ok"
    finally:
        ti._current_tailnet_identity.reset(token)


@pytest.mark.asyncio
async def test_capability_missing_enforce(monkeypatch):
    from arifosmcp.runtime import tailnet_identity as ti

    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "enforce")
    mw = ti.TailnetActorBindingMiddleware()
    ident = ti.TailnetIdentity(
        node="agent-scout-spike.arifOS.ts.net.",
        tags=("tag:agent-scout",),
        caps={"arif-fazil.com/cap/mcp": [{"tools": ["arif_observe"]}]},
    )
    token = ti._current_tailnet_identity.set(ident)
    try:
        with pytest.raises(PermissionError):
            await mw.on_request(_ToolCtx("arif_forge"), _ok)
    finally:
        ti._current_tailnet_identity.reset(token)


@pytest.mark.asyncio
async def test_capability_present(monkeypatch):
    from arifosmcp.runtime import tailnet_identity as ti

    monkeypatch.setenv("ARIFOS_TAILNET_IDENTITY_MODE", "enforce")
    mw = ti.TailnetActorBindingMiddleware()
    ident = ti.TailnetIdentity(
        node="agent-scout-spike.arifOS.ts.net.",
        tags=("tag:agent-scout",),
        caps={"arif-fazil.com/cap/mcp": [{"tools": ["arif_observe"]}]},
    )
    token = ti._current_tailnet_identity.set(ident)
    try:
        assert await mw.on_request(_ToolCtx("arif_observe"), _ok) == "ok"
    finally:
        ti._current_tailnet_identity.reset(token)
