from __future__ import annotations

from arifosmcp.runtime.public_registry import build_mcp_manifest, build_server_json
from arifosmcp.runtime.public_surface import BLOCKED_PUBLIC_PREFIXES, CANONICAL_15


def test_public_manifests_lock_to_canonical15() -> None:
    expected = set(CANONICAL_15)
    server_json = build_server_json()
    manifest_json = build_mcp_manifest()

    assert {tool["name"] for tool in server_json["tools"]} == expected
    assert {tool["name"] for tool in manifest_json["tools"]} == expected


def test_public_manifests_block_internal_prefixes() -> None:
    tool_names = {tool["name"] for tool in build_server_json()["tools"]}

    assert not [name for name in tool_names if name.startswith(BLOCKED_PUBLIC_PREFIXES)]
