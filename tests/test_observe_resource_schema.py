"""tests/test_observe_resource_schema.py — C2 acceptance (F13 2026-10-30).

888-APEX finding: arif_observe implemented resource_read/resource_search in code
but the PUBLISHED inputSchema omitted them — tools/list (the only MCP discovery
surface) could not find the migration path. Contract and code diverged; same
failure class as the hand-copied COORDINATION_TOOLS tuple.

Acceptance layers recorded SEPARATELY (per F13 bounded envelope):
  schema published  (this file, wire-visible objects)
  invocation accepted / handler reached (in-process call_tool)
  result correct (resource payload assertions)

Excluded by scope: new capabilities, authority changes, broad test repair.
"""

from __future__ import annotations

import json

import pytest

OLD_MODES = [
    "search",
    "fetch",
    "hybrid_discovery",
    "ingest",
    "compass",
    "atlas",
    "entropy_dS",
    "vitals",
]
NEW_MODES = ["resource_read", "resource_search"]


async def _observe_schema():
    from arifosmcp.server import mcp

    tools = await mcp.list_tools()
    obs = next(t for t in tools if t.name == "arif_observe")
    return obs.parameters  # FastMCP FunctionTool: JSON Schema lives here


@pytest.mark.asyncio
async def test_published_enum_contains_new_modes_and_keeps_old_ones():
    schema = await _observe_schema()
    enum = schema["properties"]["mode"].get("enum", [])
    for m in NEW_MODES:
        assert m in enum, f"{m} implemented but not published (C2 defect persists)"
    for m in OLD_MODES:
        assert m in enum, f"pre-existing mode {m} lost during C2 fix"
    # No unreviewed capability may ride along.
    assert sorted(enum) == sorted(OLD_MODES + NEW_MODES), (
        f"enum drifted beyond reviewed set: {sorted(set(enum) - set(OLD_MODES + NEW_MODES))}"
    )


@pytest.mark.asyncio
async def test_published_schema_exposes_uri_property():
    schema = await _observe_schema()
    props = schema.get("properties", {})
    assert "uri" in props, f"uri not published; properties={sorted(props)}"
    assert "resource" in str(props["uri"].get("description", "")).lower() or props["uri"], (
        "uri property present but empty"
    )


@pytest.mark.asyncio
async def test_invalid_mode_fails_deterministically():
    """A mode outside the published enum must fail deterministically — never crash, never pass."""
    from arifosmcp.server import mcp

    result = await mcp.call_tool(
        "arif_observe", {"mode": "teleport", "query": "x", "actor_id": "probe"}
    )
    is_error = getattr(result, "is_error", getattr(result, "isError", False))
    text = ""
    if getattr(result, "content", None):
        text = str(result.content[0].text)[:400]
    if not is_error:
        # envelope-style deterministic refusal is also acceptable
        assert "teleport" in text or "hold" in text.lower() or "error" in text.lower(), (
            f"invalid mode neither errored nor refused deterministically: {text}"
        )


@pytest.mark.asyncio
async def test_resource_read_invocation_reaches_handler():
    """Layer separation: schema published → invocation accepted → handler reached → result correct."""
    from arifosmcp.server import mcp

    result = await mcp.call_tool(
        "arif_observe",
        {
            "mode": "resource_read",
            "uri": "arifos://vitals",
            "actor_id": "probe",
            "session_id": "probe",
        },
    )
    is_error = getattr(result, "is_error", getattr(result, "isError", False))
    assert not is_error, f"schema-valid resource_read errored: {str(result)[:300]}"
    inner = json.loads(result.content[0].text)
    # canonical normalization renames the tool status to the kernel envelope status
    assert str(inner.get("status", "")).upper() in ("OK", "COMPLETED"), (
        f"outer not ok: {str(inner)[:300]}")
    payload = inner.get("result", inner)
    resource = payload.get("resource", {})
    assert str(resource.get("status", "")).upper() == "OK", "inner bridge not ok"
    assert resource.get("uri") == "arifos://vitals"
    assert len(str(resource.get("content", ""))) > 0, "resource content empty"


@pytest.mark.asyncio
async def test_resource_search_invocation_reaches_handler():
    from arifosmcp.server import mcp

    result = await mcp.call_tool(
        "arif_observe",
        {"mode": "resource_search", "query": "vitals", "actor_id": "probe", "session_id": "probe"},
    )
    is_error = getattr(result, "is_error", getattr(result, "isError", False))
    assert not is_error, f"schema-valid resource_search errored: {str(result)[:300]}"
    inner = json.loads(result.content[0].text)
    payload = inner.get("result", inner)
    resource = payload.get("resource", {})
    assert str(resource.get("status", "")).upper() == "OK"
    assert resource.get("count", 0) >= 1
