"""
arifOS Namespace Index — Canonical Surface Directory
════════════════════════════════════════════════════

A live pointer to the current namespace surface.
The canonical surface is the live resources/list — this is a directory,
not a migration archaeology map.

ZEN (2026-09-02, F13 'audit this and zen all'): counts are COMPUTED LIVE
from the registry at read time. Never hardcoded. The previous static
`count: 30, drift: "aligned"` drifted from reality (35 live resources)
while claiming alignment — a self-report is not a witness.

DITEMPA BUKAN DIBERI — The map serves the territory, not the reverse.
"""

from __future__ import annotations

import json
import time
from typing import Any

from fastmcp import FastMCP


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


async def _list_prompts(mcp: FastMCP) -> list[Any]:
    try:
        return list(await mcp.list_prompts(run_middleware=False))
    except TypeError:
        return list(await mcp.list_prompts())


async def _list_resources(mcp: FastMCP) -> list[Any]:
    try:
        return list(await mcp.list_resources(run_middleware=False))
    except TypeError:
        return list(await mcp.list_resources())


async def _list_tools(mcp: FastMCP) -> list[Any]:
    try:
        return list(await mcp.list_tools(run_middleware=False))
    except TypeError:
        return list(await mcp.list_tools())


def register_namespace_index(mcp: FastMCP) -> list[str]:
    """Register arifos://index — canonical namespace directory (live-counted)."""

    @mcp.resource(
        "arifos://index",
        name="arifOS Namespace Index",
        mime_type="application/json",
        description="Canonical resource directory — counts computed live from the registry at read time.",
    )
    async def namespace_index() -> str:
        """Live directory pointer — measured, never hardcoded."""
        meta: dict[str, Any] = {
            "chambers": ["IDENTITY", "LAW", "STATE", "MIND", "DEEP"],
            "cap": 33,
            "counting": "live_registry",
            "generated_at": _now_iso(),
        }
        try:
            resources = await _list_resources(mcp)
            prompts = await _list_prompts(mcp)
            tools = await _list_tools(mcp)
            uris = [str(getattr(r, "uri", "") or "") for r in resources]
            meta.update(
                count=len(uris),
                arifos=sum(1 for u in uris if u.startswith("arifos://")),
                prompts=len(prompts),
                tools=len(tools),
            )
        except Exception as exc:
            meta.update(
                count=None,
                arifos=None,
                prompts=None,
                tools=None,
                note=f"registry unavailable ({type(exc).__name__}) — use resources/list",
            )
        return json.dumps(
            {
                "_meta": meta,
                "description": (
                    "Resource directory in 5 chambers. Counts measured live from the "
                    "registry. Governed hooks: prompts/list. Kernel verbs: tools/list. "
                    "This index is the map; resources/list is the territory."
                ),
            },
            indent=2,
        )

    registered = ["arifos://index"]

    # ── skill://index — federation skills pointer ──────────────────────
    @mcp.resource(
        "skill://index",
        name="Federation Skill Index",
        mime_type="application/json",
        description="Federation skill directory — counts computed live. Use skill://{name}/SKILL.md.",
    )
    async def skill_index() -> str:
        """Federation skill directory pointer — measured, never hardcoded."""
        meta: dict[str, Any] = {
            "generated_at": _now_iso(),
            "counting": "live_registry",
        }
        try:
            prompts = await _list_prompts(mcp)
            resources = await _list_resources(mcp)
            meta.update(
                prompts=len(prompts),
                resources=len(resources),
                hooks=[str(p.name) for p in prompts],
            )
        except Exception as exc:
            meta.update(
                prompts=None,
                resources=None,
                note=f"registry unavailable ({type(exc).__name__}) — use prompts/list",
            )
        return json.dumps(
            {
                "_meta": meta,
                "description": "Federation skills directory. Counts measured live.",
                "note": "skill://{name}/SKILL.md for individual skill manifests",
            },
            indent=2,
        )

    registered.append("skill://index")

    return registered


__all__ = ["register_namespace_index"]
