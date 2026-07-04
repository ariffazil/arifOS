from __future__ import annotations

from types import SimpleNamespace

from arifosmcp.resources.surface_map import _build_surface_map
from arifosmcp.runtime.public_surface import public_tool_names_for_mode


class _FakeMCP:
    async def list_resources(self):
        return [
            SimpleNamespace(uri="arifos://mcp/surface-map"),
            SimpleNamespace(uri="skill://shadow-diagnostic"),
            SimpleNamespace(uri="tree777://index"),
        ]

    async def list_resource_templates(self):
        return [
            SimpleNamespace(uriTemplate="source://{hash}"),
            SimpleNamespace(uriTemplate="receipt://web/{id}"),
        ]


def test_surface_map_uses_live_registry_shape() -> None:
    payload = _build_surface_map(_FakeMCP())["arifos_agent_surface_map"]

    assert payload["mcp_tools"] == list(public_tool_names_for_mode(None))
    assert payload["tool_count"] == 9
    assert all(name.startswith("arif_") for name in payload["mcp_tools"])
    assert "arifos_act" not in payload["mcp_tools"]

    assert payload["mcp_resources"] == [
        "arifos://mcp/surface-map",
        "skill://shadow-diagnostic",
        "tree777://index",
    ]
    assert payload["resource_count"] == 3
    assert payload["mcp_resource_templates"] == [
        "receipt://web/{id}",
        "source://{hash}",
    ]
    assert payload["resource_template_count"] == 2
