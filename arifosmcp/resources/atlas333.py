"""
arifosmcp/resources/atlas333.py — ATLAS333 MCP Resources
═══════════════════════════════════════════════════════════

Passive read surface over existing ATLAS333 data structures.
No new data. No duplication. MCP skin over committed files.

Data sources:
  - paradox_quotes.py → ALL_PARADOX_QUOTES, Organ, ParadoxAxis, Norm
  - atlas.py → PARADOX_GPV_MAP, resolve_paradox_axes()
  - types.py → TEARFRAME thresholds (trm, echo, rasa)
  - ATLAS333_EVERGREEN.md → paradox definitions, zones, activation rules

Resource URIs (arifos:// namespace):
  arifos://atlas333/index            — Root index
  arifos://atlas333/paradox/list     — All 33 paradoxes
  arifos://atlas333/paradox/{id}     — Single paradox (1-33)
  arifos://atlas333/quote/list       — All 33 quotes
  arifos://atlas333/quote/{id}       — Single quote (M1-M11, R1-R11, J1-J11)
  arifos://atlas333/zones            — 7 paradox zones
  arifos://atlas333/organs           — 3 quote organs (Memory/Mind/Judge)
  arifos://atlas333/thresholds       — TEARFRAME (trm≥0.94, echo≥0.87, rasa≥0.85)
  arifos://atlas333/activation/rules — GPV→paradox activation matrix
  arifos://atlas333/flow             — 10-stage pipeline
  arifos://atlas333/geometry         — Full cognitive geometry (zones × geometries × depths)
  arifos://atlas333/scar/{id}        — Sealed scar by ID (read-only)
  arifos://atlas333/seal/head        — VAULT999 chain head (cache-friendly)

F-binding:
  F2: deterministic — derived from committed data structures
  F4: clarity — structured JSON, not prose
  F8: read-only by design — no resource/tool confusion
  F11: auditable — provenance via data source references

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP


# ── Paradox definitions (from paradox_quotes.py — single source of truth) ─
# 27 of 33 hardcoded axis values were fabricated (not in canonical ParadoxAxis
# enum). This refactor sources everything from arifosmcp/constitution/paradox_quotes.py
# so the data is canonical. Falls back to empty list if import fails — honest UNKNOWN.

_QUOTE_ID_TO_PARADOX_ID: dict[str, int] = {
    **{f"M{i}": i for i in range(1, 12)},
    **{f"R{i}": 11 + i for i in range(1, 12)},
    **{f"J{i}": 22 + i for i in range(1, 12)},
}


def _build_paradoxes_from_canonical() -> list[dict[str, Any]]:
    """Build the 33-paradox table from paradox_quotes.py. Single source of truth."""
    try:
        from arifosmcp.constitution.paradox_quotes import ALL_PARADOX_QUOTES
    except ImportError as exc:
        logger.warning(f"atlas333: paradox_quotes not importable; returning empty: {exc}")
        return []

    paradoxes: list[dict[str, Any]] = []
    # Sort by quote_id to maintain order M1..M11, R1..R11, J1..J11.
    for qid in sorted(ALL_PARADOX_QUOTES.keys(), key=lambda x: (x[0], int(x[1:]))):
        q = ALL_PARADOX_QUOTES[qid]
        paradoxes.append({
            "id": _QUOTE_ID_TO_PARADOX_ID[qid],
            "paradox": q.axis_label,        # human-readable: "recollection vs. discovery"
            "axis": q.axis.value,           # canonical ParadoxAxis enum value
            "organ": q.organ.value,         # canonical Organ enum value
            "quote_id": qid,                # bridge to canonical quote
        })
    return paradoxes


_PARADOXES: list[dict[str, Any]] = _build_paradoxes_from_canonical()
_PARADOX_BY_ID: dict[int, dict[str, Any]] = {p["id"]: p for p in _PARADOXES}

# ── GPV→Paradox activation matrix (from atlas.py PARADOX_GPV_MAP) ───────

_ACTIVATION_RULES: dict[str, dict[str, Any]] = {
    "tau_high_rho_low": {
        "condition": "τ ≥ 0.9, ρ ≤ 0.2, lane=FACTUAL",
        "description": "Pure truth-seeking (Zone I + V)",
        "paradox_ids": [1, 2, 3, 4, 21, 22, 25],
    },
    "rho_crisis": {
        "condition": "ρ ≥ 0.3, lane=CRISIS",
        "description": "Risk detected (Zone II + VI)",
        "paradox_ids": [6, 7, 8, 9, 23, 26, 30],
    },
    "kappa_care": {
        "condition": "κ ≥ 0.5, lane=CARE",
        "description": "Care/identity context (Zone III + IV)",
        "paradox_ids": [11, 12, 13, 15, 16, 17, 20],
    },
    "tau_kappa_factual": {
        "condition": "τ ≥ 0.8, κ ≥ 0.3, lane=FACTUAL",
        "description": "Facts meet meaning (Zone I + IV)",
        "paradox_ids": [5, 18, 24],
    },
    "rho_high": {
        "condition": "ρ ≥ 0.6, any lane",
        "description": "High risk hard gate (Zone II + VI)",
        "paradox_ids": [8, 9, 10, 28, 29],
    },
    "query_exploratory": {
        "condition": "query_type=EXPLORATORY",
        "description": "Open-ended exploration (Zone IV + V)",
        "paradox_ids": [19, 22, 25],
    },
}

# ── Zones (from ATLAS333_COGNITIVE_GEOMETRY.md) ──────────────────────────

_ZONES: list[dict[str, Any]] = [
    {
        "zone": "I",
        "name": "Truth Territory",
        "geometry": "euclidean",
        "depth": "surface",
        "paradox_range": "1-4, 12-16",
    },
    {
        "zone": "II",
        "name": "Risk Frontier",
        "geometry": "hyperbolic",
        "depth": "deep",
        "paradox_range": "6-9, 23-26",
    },
    {
        "zone": "III",
        "name": "Care Basin",
        "geometry": "spherical",
        "depth": "intimate",
        "paradox_range": "11, 15-17, 32",
    },
    {
        "zone": "IV",
        "name": "Meaning Meridian",
        "geometry": "toroidal",
        "depth": "recursive",
        "paradox_range": "5, 18-20, 24",
    },
    {
        "zone": "V",
        "name": "Discovery Ridge",
        "geometry": "fractal",
        "depth": "emergent",
        "paradox_range": "3, 19, 21-22, 25",
    },
    {
        "zone": "VI",
        "name": "Governance Spine",
        "geometry": "crystalline",
        "depth": "constitutional",
        "paradox_range": "26-31",
    },
    {
        "zone": "VII",
        "name": "Sovereign Apex",
        "geometry": "singular",
        "depth": "absolute",
        "paradox_range": "29, 31, 33",
    },
]

# ── 10-stage pipeline (from ATLAS333_COGNITIVE_GEOMETRY.md) ──────────────

_PIPELINE_STAGES: list[dict[str, Any]] = [
    {"stage": 1, "name": "INGEST", "tool": "arif_observe", "description": "Raw signal acquisition"},
    {
        "stage": 2,
        "name": "CLASSIFY",
        "tool": "Φ(text)",
        "description": "Lane + query type classification",
    },
    {"stage": 3, "name": "DECODE", "tool": "Θ(lane)", "description": "Demand tensor (τ, κ, ρ)"},
    {
        "stage": 4,
        "name": "ACTIVATE",
        "tool": "PARADOX_GPV_MAP",
        "description": "GPV→paradox activation",
    },
    {
        "stage": 5,
        "name": "ENRICH",
        "tool": "get_triggered_quotes_by_gpv()",
        "description": "Quote injection by paradox",
    },
    {
        "stage": 6,
        "name": "EVALUATE",
        "tool": "evaluate_paradox_gate_gpv()",
        "description": "Paradox gate check",
    },
    {
        "stage": 7,
        "name": "TEARFRAME",
        "tool": "FloorScores",
        "description": "TRM/ECHO/RASA thresholds",
    },
    {"stage": 8, "name": "JUDGE", "tool": "arif_judge", "description": "Constitutional verdict"},
    {"stage": 9, "name": "FORGE", "tool": "arif_forge", "description": "Governed execution"},
    {"stage": 10, "name": "SEAL", "tool": "arif_seal", "description": "VAULT999 immutable append"},
]

# ── TEARFRAME thresholds (from types.py:460-490) ────────────────────────

_TEARFRAME: dict[str, Any] = {
    "trm": {
        "name": "Truth-Reliability Metric",
        "formula": "f2_truth",
        "threshold": 0.94,
        "floor": "F2",
    },
    "echo": {
        "name": "Evidence Coherence",
        "formula": "∛(f3 × f2 × f13)",
        "threshold": 0.87,
        "floors": ["F2", "F3", "F13"],
    },
    "rasa": {
        "name": "Resonance-Alignment",
        "formula": "∛(f6 × f5 × f13)",
        "threshold": 0.85,
        "floors": ["F5", "F6", "F13"],
    },
}

# ── Cognitive geometry (from ATLAS333_COGNITIVE_GEOMETRY.md) ─────────────

_GEOMETRY_TERRITORIES: list[dict[str, Any]] = [
    {
        "territory": "Memory",
        "geometries": ["euclidean", "hyperbolic", "fractal"],
        "depths": ["surface", "deep", "emergent"],
    },
    {
        "territory": "Mind",
        "geometries": ["euclidean", "spherical", "toroidal"],
        "depths": ["surface", "intimate", "recursive"],
    },
    {
        "territory": "Judge",
        "geometries": ["crystalline", "singular", "hyperbolic"],
        "depths": ["constitutional", "absolute", "deep"],
    },
]


def attach_to_mcp_resource(mcp: FastMCP) -> list[str]:
    """Attach ATLAS333 resources to MCP server. Read-only by design (F8).

    Reads from existing committed data structures — no new data, no duplication.
    Pattern matches skills_contracts_resource.py attach_to_mcp_resource.
    """
    registered: list[str] = []

    # ── arifos://atlas333/index — Root index ─────────────────────────────

    @mcp.resource("arifos://atlas333/index")
    async def atlas333_index() -> str:
        """ATLAS333 root index — all available resources."""
        return json.dumps(
            {
                "atlas_id": "ATLAS333",
                "version": "v1.0.0",
                "description": "Cognitive geometry of arifOS — 33 paradoxes, 33 quotes, 7 zones, TEARFRAME thresholds",
                "resources": [
                    "arifos://atlas333/paradox/list",
                    "arifos://atlas333/paradox/{id}",
                    "arifos://atlas333/quote/list",
                    "arifos://atlas333/quote/{id}",
                    "arifos://atlas333/zones",
                    "arifos://atlas333/organs",
                    "arifos://atlas333/thresholds",
                    "arifos://atlas333/activation/rules",
                    "arifos://atlas333/flow",
                    "arifos://atlas333/geometry",
                    "arifos://atlas333/scar/{id}",
                    "arifos://atlas333/seal/head",
                    "arifos://atlas333/agent/init",
                ],
                "data_sources": [
                    "constitution/paradox_quotes.py",
                    "core/shared/atlas.py",
                    "core/shared/types.py",
                    "core/shared/ATLAS333_EVERGREEN.md",
                ],
                "seal": "DITEMPA BUKAN DIBERI",
            },
            indent=2,
        )

    registered.append("arifos://atlas333/index")

    # ── arifos://atlas333/paradox/list — All 33 paradoxes ───────────────

    @mcp.resource("arifos://atlas333/paradox/list")
    async def paradox_list() -> str:
        """All 33 paradoxes with axes, zones, organs."""
        return json.dumps(
            {
                "total": len(_PARADOXES),
                "by_organ": {
                    "memory": [p for p in _PARADOXES if p["organ"] == "memory"],
                    "mind": [p for p in _PARADOXES if p["organ"] == "mind"],
                    "judge": [p for p in _PARADOXES if p["organ"] == "judge"],
                },
                "paradoxes": _PARADOXES,
            },
            indent=2,
        )

    registered.append("arifos://atlas333/paradox/list")

    # ── arifos://atlas333/paradox/{id} — Single paradox ─────────────────

    @mcp.resource("arifos://atlas333/paradox/{id}")
    async def paradox_by_id(id: str) -> str:
        """Single paradox by ID (1-33) with full context."""
        try:
            pid = int(id)
        except ValueError:
            return json.dumps({"error": f"Invalid paradox ID: {id}. Expected 1-33."})

        paradox = _PARADOX_BY_ID.get(pid)
        if not paradox:
            return json.dumps({"error": f"Paradox {id} not found. Valid range: 1-33."})

        # Find which activation rules reference this paradox
        activating_rules = [
            {"rule": name, "condition": rule["condition"]}
            for name, rule in _ACTIVATION_RULES.items()
            if pid in rule["paradox_ids"]
        ]

        # Find zone for this paradox
        zone = next(
            (z for z in _ZONES if _paradox_in_zone(pid, z["paradox_range"])),
            None,
        )

        return json.dumps(
            {
                **paradox,
                "activating_rules": activating_rules,
                "zone": zone["zone"] if zone else "unknown",
                "zone_name": zone["name"] if zone else "unknown",
            },
            indent=2,
        )

    registered.append("arifos://atlas333/paradox/{id}")

    # ── arifos://atlas333/quote/list — All 33 quotes ────────────────────

    @mcp.resource("arifos://atlas333/quote/list")
    async def quote_list() -> str:
        """All 33 quotes from paradox_quotes.py."""
        try:
            from arifosmcp.constitution.paradox_quotes import ALL_PARADOX_QUOTES

            quotes = [q.to_dict() for q in ALL_PARADOX_QUOTES.values()]
            return json.dumps(
                {
                    "total": len(quotes),
                    "by_organ": {
                        "memory": [q for q in quotes if q["organ"] == "memory"],
                        "mind": [q for q in quotes if q["organ"] == "mind"],
                        "judge": [q for q in quotes if q["organ"] == "judge"],
                    },
                    "quotes": quotes,
                },
                indent=2,
            )
        except ImportError as exc:
            return json.dumps({"error": f"Cannot import paradox_quotes: {exc}"})

    registered.append("arifos://atlas333/quote/list")

    # ── arifos://atlas333/quote/{id} — Single quote ─────────────────────

    @mcp.resource("arifos://atlas333/quote/{id}")
    async def quote_by_id(id: str) -> str:
        """Single quote by ID (M1-M11, R1-R11, J1-J11) with full context."""
        try:
            from arifosmcp.constitution.paradox_quotes import (
                ALL_PARADOX_QUOTES,
                get_quote_by_id,
            )

            quote = get_quote_by_id(id.upper())
            if not quote:
                valid_ids = sorted(ALL_PARADOX_QUOTES.keys())
                return json.dumps({"error": f"Quote {id} not found. Valid IDs: {valid_ids}"})

            return json.dumps(quote.to_dict(), indent=2)
        except ImportError as exc:
            return json.dumps({"error": f"Cannot import paradox_quotes: {exc}"})

    registered.append("arifos://atlas333/quote/{id}")

    # ── arifos://atlas333/zones — 7 paradox zones ───────────────────────

    @mcp.resource("arifos://atlas333/zones")
    async def zones() -> str:
        """7 paradox zones with paradox ranges and geometries."""
        return json.dumps(
            {
                "total": len(_ZONES),
                "zones": _ZONES,
            },
            indent=2,
        )

    registered.append("arifos://atlas333/zones")

    # ── arifos://atlas333/organs — 3 quote organs ────────────────────────

    @mcp.resource("arifos://atlas333/organs")
    async def organs() -> str:
        """3 quote organs (Memory/Mind/Judge) with paradox counts."""
        return json.dumps(
            {
                "organs": [
                    {
                        "organ": "memory",
                        "paradox_ids": list(range(1, 12)),
                        "quote_prefix": "M",
                        "quote_range": "M1-M11",
                        "description": "Retrieval, forgetting, archive, temporal meaning",
                    },
                    {
                        "organ": "mind",
                        "paradox_ids": list(range(12, 23)),
                        "quote_prefix": "R",
                        "quote_range": "R1-R11",
                        "description": "Doubt, certainty, optimization, observation",
                    },
                    {
                        "organ": "judge",
                        "paradox_ids": list(range(23, 34)),
                        "quote_prefix": "J",
                        "quote_range": "J1-J11",
                        "description": "Verdict, authority, governance, sovereignty",
                    },
                ]
            },
            indent=2,
        )

    registered.append("arifos://atlas333/organs")

    # ── arifos://atlas333/thresholds — TEARFRAME ─────────────────────────

    @mcp.resource("arifos://atlas333/thresholds")
    async def thresholds() -> str:
        """TEARFRAME thresholds (trm≥0.94, echo≥0.87, rasa≥0.85)."""
        return json.dumps(
            {
                "tearframe": _TEARFRAME,
                "source": "core/shared/types.py:460-490",
                "reference": "ATLAS333_EVERGREEN.md §TEARFRAME",
            },
            indent=2,
        )

    registered.append("arifos://atlas333/thresholds")

    # ── arifos://atlas333/activation/rules — GPV→paradox matrix ─────────

    @mcp.resource("arifos://atlas333/activation/rules")
    async def activation_rules() -> str:
        """GPV→paradox activation matrix from atlas.py."""
        return json.dumps(
            {
                "total_rules": len(_ACTIVATION_RULES),
                "source": "core/shared/atlas.py PARADOX_GPV_MAP",
                "rules": _ACTIVATION_RULES,
                "usage": "Pass GPV state → match conditions → get paradox IDs → query arifos://atlas333/paradox/{id}",
            },
            indent=2,
        )

    registered.append("arifos://atlas333/activation/rules")

    # ── arifos://atlas333/flow — 10-stage pipeline ───────────────────────

    @mcp.resource("arifos://atlas333/flow")
    async def flow() -> str:
        """10-stage cognitive pipeline from signal to seal."""
        return json.dumps(
            {
                "total_stages": len(_PIPELINE_STAGES),
                "stages": _PIPELINE_STAGES,
                "source": "ATLAS333_COGNITIVE_GEOMETRY.md",
            },
            indent=2,
        )

    registered.append("arifos://atlas333/flow")

    # ── arifos://atlas333/geometry — Full cognitive geometry ─────────────

    @mcp.resource("arifos://atlas333/geometry")
    async def geometry() -> str:
        """Full cognitive geometry — territories × geometries × depths."""
        return json.dumps(
            {
                "territories": _GEOMETRY_TERRITORIES,
                "zones": _ZONES,
                "pipeline": _PIPELINE_STAGES,
                "source": "ATLAS333_COGNITIVE_GEOMETRY.md",
            },
            indent=2,
        )

    registered.append("arifos://atlas333/geometry")

    # ── arifos://atlas333/scar/{id} — Sealed scar ───────────────────────

    @mcp.resource("arifos://atlas333/scar/{id}")
    async def scar_by_id(id: str) -> str:
        """Single sealed scar by ID (read-only, with witness chain)."""
        try:
            import pathlib

            scar_path = pathlib.Path("/root/.local/share/arifos/vault999") / "scars" / f"{id}.json"
            if scar_path.exists():
                return scar_path.read_text()
            # Try in-memory scar store
            from arifosmcp.constitution.paradox_quotes import ALL_PARADOX_QUOTES

            # Check if id matches a quote_id that has scar linkage
            quote = ALL_PARADOX_QUOTES.get(id.upper())
            if quote:
                return json.dumps(
                    {
                        "scar_id": id,
                        "linked_quote": quote.to_dict(),
                        "status": "quote_found_no_sealed_scar",
                        "note": "No sealed scar file found. Scar linkage is placeholder.",
                    },
                    indent=2,
                )
            return json.dumps(
                {
                    "scar_id": id,
                    "status": "not_found",
                    "note": "No sealed scar or matching quote found for this ID.",
                }
            )
        except Exception as exc:
            return json.dumps({"error": f"Cannot read scar: {exc}"})

    registered.append("arifos://atlas333/scar/{id}")

    # ── arifos://atlas333/seal/head — VAULT999 chain head ───────────────

    @mcp.resource("arifos://atlas333/seal/head")
    async def seal_head() -> str:
        """Current VAULT999 chain head (cache-friendly, read-only)."""
        try:
            import pathlib

            head_path = pathlib.Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
            if head_path.exists():
                return head_path.read_text()
            return json.dumps(
                {
                    "status": "not_found",
                    "note": "seal_chain_head.json not found at expected path.",
                }
            )
        except Exception as exc:
            return json.dumps({"error": f"Cannot read seal chain head: {exc}"})

    registered.append("arifos://atlas333/seal/head")

    # ── arifos://atlas333/agent/init — Agent init prompt ─────────────────

    @mcp.resource("arifos://atlas333/agent/init")
    async def agent_init() -> str:
        """Agent init prompt for new agents joining the federation."""
        return json.dumps(
            {
                "prompt": (
                    "You are entering the arifOS federation. The ATLAS333 is your cognitive geometry map.\n\n"
                    "1. Read arifos://atlas333/index to understand available resources.\n"
                    "2. Read arifos://atlas333/paradox/list to internalize the 33 paradoxes.\n"
                    "3. Read arifos://atlas333/thresholds to know TEARFRAME gates.\n"
                    "4. Read arifos://atlas333/activation/rules to understand which paradoxes fire for which queries.\n"
                    "5. Read arifos://atlas333/flow to know the 10-stage pipeline.\n\n"
                    "The 33 paradoxes are the minimum viable self-knowledge — they prevent "
                    "the agent's confidence from becoming noise, and its knowledge from becoming certainty.\n\n"
                    "DITEMPA BUKAN DIBERI — Forged, Not Given."
                ),
                "data_sources": [
                    "core/shared/ATLAS333_AGENT.md",
                    "core/shared/ATLAS333_EVERGREEN.md",
                ],
            },
            indent=2,
        )

    registered.append("arifos://atlas333/agent/init")

    return registered


# ── Helpers ───────────────────────────────────────────────────────────────


def _paradox_in_zone(pid: int, paradox_range: str) -> bool:
    """Check if a paradox ID falls within a zone's paradox range string.

    Handles formats like "1-4, 12-16" or "29, 31, 33".
    """
    for part in paradox_range.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= pid <= int(hi):
                return True
        elif part.isdigit() and int(part) == pid:
            return True
    return False


__all__ = ["attach_to_mcp_resource"]
