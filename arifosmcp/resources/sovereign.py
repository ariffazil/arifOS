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

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# ── Canonical paths ──────────────────────────────────────────────────
_CANDIDATE_ROOTS = [
    Path("/var/www/html/arif/000"),
    Path("/root/arif-fazil.com/sites/arif-fazil.com/public/000"),
    Path("/opt/arifos/static/000"),
    Path("/opt/arifos/app/static/000"),
]


def _resolve_static_root() -> Path:
    for candidate in _CANDIDATE_ROOTS:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return _CANDIDATE_ROOTS[0]


_STATIC_ROOT = _resolve_static_root()

# ── URI → file mapping ───────────────────────────────────────────────
_SOVEREIGN_FILES: dict[str, str] = {
    "index": "INDEX.md",
    "genesis": "genesis-statement.json",
    "claims": "claims.json",
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
    "arifos://000/genesis",
    "arifos://000/claims",
)


def _read_file(filename: str) -> dict[str, Any]:
    """Read a sovereign file and return a structured resource envelope.

    Containment (2026-09-22): ``filename`` arrives from ``sovereign://{file}``
    and may carry ``../`` past the URI segment (fastmcp matches before percent
    decode). Resolve against ``_STATIC_ROOT`` and refuse any escape — the
    extension suffix in the handler is a content-type convention, not a boundary.
    """
    from arifosmcp.runtime.path_guard import contained_path

    try:
        filepath = contained_path(_STATIC_ROOT, filename)
    except ValueError:
        return {
            "status": "REJECTED",
            "uri": f"sovereign://{filename}",
            "reason": "filename escapes the sovereign archive (path containment)",
        }
    if not filepath.exists():
        if filename == "INDEX.md":
            available = sorted(f.name for f in _STATIC_ROOT.iterdir() if not f.name.startswith("."))
            content = (
                f"# arifOS Position Zero (/000) Sovereign Index\n\n"
                f"Canonical archive root: `{_STATIC_ROOT}`\n\n"
                f"Available records:\n"
                + "\n".join(f"- `{f}`" for f in available)
            )
            return {
                "status": "OK",
                "uri": "sovereign://index",
                "source": str(_STATIC_ROOT / "INDEX.md (virtual)"),
                "size_bytes": len(content),
                "lines": content.count("\n") + 1,
                "content": content,
            }
        return {
            "status": "NOT_FOUND",
            "uri": f"sovereign://{filename}",
            "available_files": sorted(f.name for f in _STATIC_ROOT.iterdir() if not f.name.startswith(".")),
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
        """Arif Fazil sovereign knowledge. Use file=index, genesis, claims, prologue,
        soul-map, scars, family, floors, organs, timeline, institutions, people,
        letters, investigations, petrophysics, unfinished, truth-reality-life,
        data-sources, reality, unsealed, zkpc-atlas, soul-metabolism.
        Or pass any filename (.md, .json, .html, .txt, .sig) from the /000 archive.
        """
        # Named key lookup first
        if file in _SOVEREIGN_FILES:
            return _read_file(_SOVEREIGN_FILES[file])
        # Direct filename access (safety: safe extensions only)
        if not file.endswith((".md", ".json", ".html", ".txt", ".sig")):
            return {
                "status": "REJECTED",
                "reason": "Supported extensions: .md, .json, .html, .txt, .sig or named keys (index, genesis, claims, prologue...)",
            }
        return _read_file(file)

    registered.append("sovereign://{file}")

    # ── Canonical arifos://000/* resources ──────────────────────────
    @mcp.resource("arifos://000/genesis")
    def sovereign_000_genesis_resource() -> dict[str, Any]:
        """arifOS Position Zero Genesis Statement (/000) signed by Muhammad Arif bin Fazil."""
        p = _STATIC_ROOT / "genesis-statement.json"
        if p.exists():
            return {
                "status": "OK",
                "uri": "arifos://000/genesis",
                "source": str(p),
                "content": p.read_text(encoding="utf-8"),
            }
        return {"status": "NOT_FOUND", "uri": "arifos://000/genesis"}

    registered.append("arifos://000/genesis")

    @mcp.resource("arifos://000/claims")
    def sovereign_000_claims_resource() -> dict[str, Any]:
        """arifOS Position Zero Attestation Claims (000-CLAIM-001..006, ZKPC dimensions, Gödel Lock)."""
        p = _STATIC_ROOT / "claims.json"
        if p.exists():
            return {
                "status": "OK",
                "uri": "arifos://000/claims",
                "source": str(p),
                "content": p.read_text(encoding="utf-8"),
            }
        return {"status": "NOT_FOUND", "uri": "arifos://000/claims"}

    registered.append("arifos://000/claims")
    return registered


__all__ = [
    "SOVEREIGN_RESOURCES",
    "register_sovereign_resources",
]
