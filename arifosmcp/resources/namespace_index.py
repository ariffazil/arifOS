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
import os
import time
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

_SKILL_ROOT = Path(os.environ.get("ARIFOS_SKILL_ROOT", "/root/.agents/skills"))
# (root_mtime, entry_count) -> (built_at, listing). A listing is a directory
# of what the served root actually holds; it is cheap to rebuild but not free
# at 600+ skills, so it is cached against the root's mtime and a 60s ceiling.
_SKILL_LISTING: dict[tuple[float, int], tuple[float, list[dict[str, str]]]] = {}
_SKILL_TTL = 60.0


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _describe(skill_md: Path) -> str:
    """Frontmatter `description:`, else the first H1. Never invented."""
    try:
        for line in skill_md.read_text(errors="replace").splitlines()[:40]:
            s = line.strip()
            if s.startswith("description:"):
                val = s.split(":", 1)[1].strip().strip("'\"")
                if val.startswith(">"):
                    val = val[1:].strip()
                if val:
                    return val
            if s.startswith("# ") and not s.startswith("##"):
                return s[2:].strip()
    except OSError:
        pass
    return ""


def skill_listing(root: Path | None = None) -> list[dict[str, str]]:
    """Every skill the served root exposes, measured at read time.

    A skill is a directory directly holding SKILL.md. Taxonomy containers are
    not skills and are not listed. Names come from the directory, so the
    listing answers `skill://{name}/SKILL.md` exactly.
    """
    root = root or _SKILL_ROOT
    try:
        st = root.stat()
        key = (st.st_mtime, len(os.listdir(root)))
    except OSError:
        return []
    cached = _SKILL_LISTING.get(key)
    if cached and (time.monotonic() - cached[0]) < _SKILL_TTL:
        return cached[1]

    listing: list[dict[str, str]] = []
    try:
        for entry in sorted(os.listdir(root)):
            if entry.startswith((".", "_")):
                continue
            d = root / entry
            skill_md = d / "SKILL.md"
            if not skill_md.is_file():
                continue  # taxonomy container or empty shell
            if os.path.realpath(skill_md).startswith(os.path.realpath(root) + os.sep):
                listing.append(
                    {"name": entry, "uri": f"skill://{entry}/SKILL.md", "description": _describe(skill_md)}
                )
    except OSError:
        pass
    _SKILL_LISTING[key] = (time.monotonic(), listing)
    return listing


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
        """Federation skill directory — the names, measured, never hardcoded."""
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
        # The directory itself: a counts-only index tells a client nothing it
        # can act on — it cannot read a skill it cannot name. Measured from the
        # served root at read time (the 2026-09-19 fix: 428 of 555 mesh skills
        # were unpublished, and the index named none of them).
        skills = skill_listing()
        meta.update(skills=len(skills), skill_root=str(_SKILL_ROOT))
        return json.dumps(
            {
                "_meta": meta,
                "description": "Federation skills directory. Counts measured live.",
                "note": "skill://{name}/SKILL.md for individual skill manifests",
                "skills": skills,
            },
            indent=2,
        )

    registered.append("skill://index")

    return registered


__all__ = ["register_namespace_index"]
