from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from arifosmcp.runtime.public_surface import BLOCKED_PUBLIC_PREFIXES


def _load_root_server_module():
    server_path = Path(__file__).resolve().parents[2] / "server.py"
    spec = importlib.util.spec_from_file_location("root_server", server_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_http_discovery_surfaces_match_canonical15() -> None:
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    tools_response = client.get("/tools")
    well_known_response = client.get("/.well-known/mcp/server.json")

    assert tools_response.status_code == 200
    assert well_known_response.status_code == 200

    tools_payload = tools_response.json()
    well_known_payload = well_known_response.json()

    assert tools_payload["count"] == 15
    assert len(tools_payload["tools"]) == 15
    assert len(well_known_payload["tools"]) == 15
    assert {
        tool["name"] for tool in tools_payload["tools"]
    } == {
        tool["name"] for tool in well_known_payload["tools"]
    }


def test_http_discovery_blocks_internal_prefixes() -> None:
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)
    payload = client.get("/tools").json()

    names = [tool["name"] for tool in payload["tools"]]
    assert not [name for name in names if name.startswith(BLOCKED_PUBLIC_PREFIXES)]
