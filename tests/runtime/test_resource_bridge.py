"""Resource bridge for tools-only clients (2026-10-17).

ChatGPT connectors expose tools only. `arif_observe(mode="fetch", url="arifos://…")`
must serve the same canon text that `resources/read` would return, without
adding a ninth tool or expanding the sovereign 8-verb facade.
"""

from __future__ import annotations

import sys
import types

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

from arifosmcp.runtime.tools import (
    _arif_sense_observe,
    _read_mcp_resource_text,
)


def _fake_server_with(uri: str, text: str) -> types.SimpleNamespace:
    mcp = FastMCP("resource-bridge-probe")
    mcp.add_resource(
        TextResource(uri=uri, name="probe-resource", text=text, description="probe")
    )
    return types.SimpleNamespace(mcp=mcp)


def test_static_resource_bridge(monkeypatch):
    monkeypatch.setitem(
        sys.modules, "arifosmcp.server", _fake_server_with("arifos://probe", "hello-canon")
    )
    out = _read_mcp_resource_text("arifos://probe")
    assert out["content"] == "hello-canon"
    assert out["source"] == "mcp_resource_registry"


def test_unknown_resource_is_explicit(monkeypatch):
    monkeypatch.setitem(
        sys.modules, "arifosmcp.server", _fake_server_with("arifos://probe", "x")
    )
    out = _read_mcp_resource_text("arifos://missing")
    assert "UNKNOWN_RESOURCE" in out["error"]


def test_fetch_mode_serves_resource(monkeypatch):
    monkeypatch.setitem(
        sys.modules, "arifosmcp.server", _fake_server_with("arifos://probe", "canon-body")
    )
    out = _arif_sense_observe(mode="fetch", url="arifos://probe")
    # _ok envelope carries the payload; the text must be present verbatim.
    assert "canon-body" in str(out)


def test_fetch_mode_still_rejects_bad_scheme(monkeypatch):
    monkeypatch.setitem(
        sys.modules, "arifosmcp.server", _fake_server_with("arifos://probe", "x")
    )
    out = _arif_sense_observe(mode="fetch", url="not-a-url")
    # Falls through to the ingest path, which fails explicitly.
    assert "ingested" in str(out) or "error" in str(out).lower()


def test_dynamic_resource_bridge(monkeypatch):
    mcp = FastMCP("dynamic-resource-probe")

    @mcp.resource("arifos://dynamic")
    def dynamic() -> str:
        return "dyn-body"

    monkeypatch.setitem(sys.modules, "arifosmcp.server", types.SimpleNamespace(mcp=mcp))
    out = _read_mcp_resource_text("arifos://dynamic")
    assert out["content"] == "dyn-body"
