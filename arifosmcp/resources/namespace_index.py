"""
arifOS Namespace Index — Canonical Surface Directory
════════════════════════════════════════════════════

A live pointer to the current namespace surface.
The canonical surface is the live resources/list — this is a directory,
not a migration archaeology map.

ZEN (2026-08-08): 30 resources, 5 chambers, ≤33 cap. This file is the
index, not the territory. The territory is live at :8088.

DITEMPA BUKAN DIBERI — The map serves the territory, not the reverse.
"""

from __future__ import annotations

import json
import time
from typing import Any

from fastmcp import FastMCP


def register_namespace_index(mcp: FastMCP) -> list[str]:
    """Register arifos://index — canonical namespace directory."""

    @mcp.resource(
        "arifos://index",
        name="arifOS Namespace Index",
        mime_type="application/json",
        description="Canonical resource directory — 30 resources, 5 chambers (IDENTITY/LAW/STATE/MIND/DEEP).",
    )
    def namespace_index() -> str:
        """Return the canonical namespace index as a live directory pointer."""
        return json.dumps(
            {
                "_meta": {
                    "count": 30,
                    "cap": 33,
                    "chambers": ["IDENTITY", "LAW", "STATE", "MIND", "DEEP"],
                    "prompts": 13,
                    "tools": 8,
                    "drift": "aligned",
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
                "description": (
                    "30 resources in 5 chambers. 13 governed hooks (000-999 ladder + meta). "
                    "8 canonical kernel verbs. Use resources/list + prompts/list for full surface."
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
        description="Federation skill directory — 13 governed hooks + 30 resources. Use skill://{name}/SKILL.md.",
    )
    def skill_index() -> str:
        """Return a federation skill directory pointer matching the 33/13 surface."""
        return json.dumps(
            {
                "_meta": {
                    "prompts": 13,
                    "resources": 30,
                    "hooks": [
                        "000 🌱 IGNITE",
                        "111 🌊 SENSE",
                        "222 🏛 PLAN",
                        "333 🧠 REASON",
                        "444 🧭 DIRECT",
                        "555 🗂 REMEMBER",
                        "666 ⚖ DIGNITY",
                        "777 🔥 FORGE",
                        "888 🔒 JUDGE",
                        "999 💎 SEAL",
                        "🌀 GOVERN",
                        "⚓ INIT",
                        "🔐 CLOSE",
                    ],
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "note": "skill://{name}/SKILL.md for individual skill manifests",
                },
                "description": "13 governed hooks + 30 resources. Federation skills directory.",
            },
            indent=2,
        )

    registered.append("skill://index")

    return registered


__all__ = ["register_namespace_index"]
