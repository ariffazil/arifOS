"""D1 regression — arif_think:critique must be reachable on the schema surfaces.

Defect D1 (2026-11-04, session SEAL-3f6a3d2834a44416): the wonder firewall
advertises allowed_next=["arif_think:critique"] (tools.py:15556/15562) and the
handler supports the mode (tools.py:16149 deterministic, 16337 LLM path), but
the MCP boundary rejects mode="critique" because the mode enum on BOTH schema
surfaces omits it. Candidates can be created but never critiqued — the gate is
one-way (incinerator by plumbing).

RED before the fix; GREEN after. The live-wire test is GREEN only after the
deploy lands (builds from the working tree; the running kernel serves the
previously-built wheel).
"""

from __future__ import annotations

import json
import pathlib
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
REGISTRY_SCHEMA = REPO / "arifosmcp" / "schema" / "registry" / "tools" / "arifos.think.schema.json"
TOOL_REGISTRY = REPO / "arifosmcp" / "schemas" / "arifos_tool_registry.json"


def test_registry_schema_allows_critique_mode():
    schema = json.loads(REGISTRY_SCHEMA.read_text())
    enum = schema["properties"]["mode"]["enum"]
    assert "critique" in enum, f"registry schema mode enum missing critique: {enum}"


def test_tool_registry_allows_critique_mode():
    reg = json.loads(TOOL_REGISTRY.read_text())
    modes = reg["public_tools"]["arif_think"]["modes"]
    assert "critique" in modes, f"tool registry modes missing critique: {modes}"


def test_wire_tools_list_exposes_critique_mode():
    """The live kernel :8088 must serve mode=critique in arif_think's inputSchema."""
    req = urllib.request.Request(
        "http://127.0.0.1:8088/mcp",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode()
    payload = body
    if not body.lstrip().startswith("{"):
        for line in body.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                break
    data = json.loads(payload)
    tools = data.get("result", {}).get("tools", [])
    think = next((t for t in tools if "arif_think" in t.get("name", "")), None)
    assert think is not None, "arif_think not in tools/list"
    modes = think.get("inputSchema", {}).get("properties", {}).get("mode", {}).get("enum", [])
    assert "critique" in modes, f"live wire mode enum missing critique: {modes}"
