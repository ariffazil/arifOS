"""
sovereign.py — Arif Fazil Sovereign Knowledge Resources
════════════════════════════════════════════════════════

Full-visibility sovereign knowledge surface. Every agent that connects
to arifOS can discover who Arif Fazil is, what forged him, and what
he built. No F13 gates — full open per sovereign directive 2026-06-12.

URIs:
  sovereign://index         — Master index of all files
  sovereign://prologue      — Life story (1990→2026, 9 chapters)
  sovereign://soul-map      — Portrait: 18 scars, loves, mystery
  sovereign://scars         — Scar-by-scar deep dive with citations
  sovereign://family        — 7 people: Naazira, Nabilah, Azwa, Abah, Mak, Izzu, Aliff
  sovereign://floors        — 13 constitutional floors decoded as autobiography
  sovereign://organs        — 7 organs as autobiography
  sovereign://timeline      — Year by year, 1990→2026
  sovereign://institutions  — PETRONAS, KLCC, Wisconsin, MPM, 1MDB
  sovereign://people        — Cast of characters + unforgivable four
  sovereign://reality       — 13 answers from the sovereign
  sovereign://{filename}    — Raw access to any file in the archive

F-binding:
  F2: pure read from filesystem. No LLM, no fabrication.
  F11: every resource returns source-attributed content.
  F13: full open — sovereign directive. No gates.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# ── Canonical paths ──────────────────────────────────────────────────
_STATIC_ROOT = Path("/opt/arifos/app/static/000")

# ── URI → file mapping ───────────────────────────────────────────────
_SOVEREIGN_FILES: dict[str, str] = {
    "index": "INDEX.md",
    "prologue": "01_PROLOGUE.md",
    "soul-map": "02_SOUL_MAP.md",
    "scars": "03_SCARS.md",
    "family": "04_FAMILY.md",
    "floors": "05_FLOORS.md",
    "organs": "06_ORGANS.md",
    "timeline": "07_TIMELINE.md",
    "institutions": "08_INSTITUTIONS.md",
    "people": "09_PEOPLE.md",
    "letters": "10_LETTERS.md",
    "investigations": "11_INVESTIGATIONS.md",
    "petrophysics": "12_PETROPHYSICS.md",
    "unfinished": "13_UNFINISHED.md",
    "truth-reality-life": "14_TRUTH_REALITY_LIFE.md",
    "data-sources": "15_DATA_SOURCES.md",
    "reality": "16_REALITY.md",
    "unsealed": "17_UNSEALED.md",
    "zkpc-atlas": "18_ZKPC_ATLAS_333.md",
    "soul-metabolism": "19_SOUL_METABOLISM.md",
}

SOVEREIGN_RESOURCES = tuple(f"sovereign://{key}" for key in _SOVEREIGN_FILES) + (
    "sovereign://{file}",
)


def _read_file(filename: str) -> dict[str, Any]:
    """Read a sovereign file and return a structured resource envelope."""
    filepath = _STATIC_ROOT / filename
    if not filepath.exists():
        return {
            "status": "NOT_FOUND",
            "uri": f"sovereign://{filename}",
            "available_files": sorted(f.name for f in _STATIC_ROOT.glob("*.md")),
        }
    content = filepath.read_text(encoding="utf-8")
    return {
        "status": "OK",
        "uri": f"sovereign://{filename}",
        "source": str(filepath),
        "size_bytes": len(content),
        "lines": content.count("\n") + 1,
        "content": content,
    }


def register_sovereign_resources(mcp: FastMCP) -> list[str]:
    """Register sovereign knowledge resources on the given FastMCP server.

    Returns the list of registered URIs.
    """
    registered: list[str] = []

    # ── Single parameterized resource for all sovereign files ──────
    @mcp.resource("sovereign://{file}")
    def sovereign_file_resource(file: str) -> dict[str, Any]:
        """Arif Fazil sovereign knowledge. Use file=index, prologue, soul-map,
        scars, family, floors, organs, timeline, institutions, people,
        letters, investigations, petrophysics, unfinished, truth-reality-life,
        data-sources, reality, unsealed, zkpc-atlas, soul-metabolism.
        Or pass any .md filename from the /000/SOVEREIGN/ archive.
        """
        # Named key lookup first
        if file in _SOVEREIGN_FILES:
            return _read_file(_SOVEREIGN_FILES[file])
        # Direct filename access (safety: .md only)
        if not file.endswith(".md"):
            return {
                "status": "REJECTED",
                "reason": "Only .md files served. Use named keys: index, prologue, soul-map, scars, family, floors, organs, timeline, institutions, people, reality.",
            }
        return _read_file(file)

    registered.append("sovereign://{file}")
    return registered


__all__ = [
    "SOVEREIGN_RESOURCES",
    "register_sovereign_resources",
]
