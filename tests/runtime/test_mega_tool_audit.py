from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from arifosmcp.runtime.public_surface import (
    BLOCKED_PUBLIC_PREFIXES,
    CANARY_PROBES,
    CANONICAL_13,
)


def _load_root_server_module():
    server_path = Path(__file__).resolve().parents[2] / "server.py"
    spec = importlib.util.spec_from_file_location("root_server", server_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_http_discovery_surfaces_match_canonical13() -> None:
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    tools_response = client.get("/tools")
    well_known_response = client.get("/.well-known/mcp/server.json")

    assert tools_response.status_code == 200
    assert well_known_response.status_code == 200

    tools_payload = tools_response.json()
    well_known_payload = well_known_response.json()

    # canonical13 public surface now includes the 19 kernel tools + 6 transport canary diagnostics
    expected_canonical13 = set(CANONICAL_13)
    expected_diagnostics = set(CANARY_PROBES)
    tools_names = {tool["name"] for tool in tools_payload["tools"]}
    well_known_names = {tool["name"] for tool in well_known_payload["tools"]}

    assert expected_canonical13.issubset(tools_names)
    assert tools_names - expected_canonical13 == expected_diagnostics
    assert tools_names == well_known_names
    assert tools_payload["count"] == len(tools_payload["tools"])


def test_http_discovery_blocks_internal_prefixes() -> None:
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)
    payload = client.get("/tools").json()

    names = [tool["name"] for tool in payload["tools"]]
    assert not [name for name in names if name.startswith(BLOCKED_PUBLIC_PREFIXES)]
