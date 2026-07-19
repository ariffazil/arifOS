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
  arifos://atlas333/paradox/list     — All 35 paradoxes
  arifos://atlas333/paradox/{id}     — Single paradox (1-35)
  arifos://atlas333/quote/list       — All 36 quote rows (35 unique paradox IDs)
  arifos://atlas333/quote/{id}       — Single quote (M1-M12, R1-R11, J1-J11, C1-C2)
  arifos://atlas333/zones            — 7 paradox zones
  arifos://atlas333/organs           — 4 quote organs (Memory/Mind/Judge/Contour)
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
import logging
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger("arifosmcp.atlas333")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[ATLAS333_AUDIT] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ── Paradox definitions (from paradox_quotes.py — single source of truth) ─
# Refactored 2026-07-15 from 33 hardcoded entries to canonical import.
# 27 of the original hardcoded axis values were fabricated (not in canonical
# ParadoxAxis enum); this loader sources everything from
# arifosmcp.constitution.paradox_quotes.py so data is canonical.
# Falls back to empty list if import fails — honest UNKNOWN rather than fabrication.

_QUOTE_ID_TO_PARADOX_ID: dict[str, int] = {
    **{f"M{i}": i for i in range(1, 12)},
    "M12": 14,  # Structural anchor for paradox 14 (One↔Many)
    **{f"R{i}": 11 + i for i in range(1, 12)},
    **{f"J{i}": 22 + i for i in range(1, 12)},
    "C1": 34,  # P34: Root Outruns Kernel (2026-07-17)
    "C2": 35,  # P35: Positive ≠ Closed (2026-07-17)
}


# ── Activation rules — derive from core.shared.atlas.PARADOX_GPV_MAP when available ──
# The activation matrix lives once in `core.shared.atlas.PARADOX_GPV_MAP`. We mirror
# only the rule IDs/conditions for documentation and keep a reference back to the
# authoritative source. Falsifiable contract: rule keys here match atlas keys and
# the paradox IDs of each rule agree with `resolve_paradox_axes` for the same input.
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
    "rho_sovereign": {
        "condition": "ρ ≥ 0.8, any lane",
        "description": "Root privilege + irreversibility — P34 Root Outruns Kernel (Zone VII)",
        "paradox_ids": [28, 29, 31, 34],
    },
    "seal_no_defense": {
        "condition": "ρ ≥ 0.5, lane∈{CRISIS,FACTUAL} — P35 Positive≠Closed",
        "description": "SEAL without defensive matrix (Zone VII)",
        "paradox_ids": [30, 33, 35],
    },
}


def _runtime_activation_rules() -> dict[str, list[int]] | None:
    """Derive the activation rules from `core.shared.atlas.PARADOX_GPV_MAP` when present.

    Returns the same shape as `_ACTIVATION_RULES` but with the canonical rule IDs and
    paradox lists from the runtime. Used only for falsification, not for documentation.
    Returns None when the runtime source cannot be imported.
    """
    try:
        from core.shared.atlas import PARADOX_GPV_MAP  # type: ignore
    except Exception:
        return None
    out: dict[str, list[int]] = {}
    for key, value in PARADOX_GPV_MAP.items():
        if isinstance(value, list):
            out[key] = [int(x) for x in value]
    return out


def _build_paradoxes_from_canonical() -> list[dict[str, Any]]:
    """Build 36 canonical quote rows spanning 35 paradox IDs."""
    try:
        from arifosmcp.constitution.paradox_quotes import ALL_PARADOX_QUOTES
    except ImportError as exc:
        logger.warning(f"atlas333: paradox_quotes not importable; returning empty: {exc}")
        return []

    paradoxes: list[dict[str, Any]] = []
    # Sort by quote prefix and numeric index for deterministic resource output.
    for qid in sorted(ALL_PARADOX_QUOTES.keys(), key=lambda x: (x[0], int(x[1:]))):
        q = ALL_PARADOX_QUOTES[qid]
        paradoxes.append(
            {
                "id": _QUOTE_ID_TO_PARADOX_ID[qid],
                "paradox": q.axis_label,  # human-readable: "recollection vs. discovery"
                "axis": q.axis.value,  # canonical ParadoxAxis enum value
                "organ": q.organ.value,  # canonical Organ enum value
                "quote_id": qid,  # bridge to canonical quote
            }
        )
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
    "rho_sovereign": {
        "condition": "ρ ≥ 0.8, any lane",
        "description": "Root privilege + irreversibility — P34 Root Outruns Kernel (Zone VII)",
        "paradox_ids": [28, 29, 31, 34],
    },
    "seal_no_defense": {
        "condition": "ρ ≥ 0.5, lane∈{CRISIS,FACTUAL} — P35 Positive≠Closed",
        "description": "SEAL without defensive matrix (Zone VII)",
        "paradox_ids": [30, 33, 35],
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
        "paradox_range": "29, 31, 33, 34, 35",
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

    ZEN (2026-07-16): Reduced from 15 to 3 MCP-exposed resources.
    RESTORED (2026-07-19): 10 resources re-exposed. Code handlers always
    preserved; MCP surface re-enabled post ATLAS333-BOOT-20260719 audit.
    """
    registered: list[str] = []

    # ── arifos://atlas333/index — Root index (CONSOLIDATED) ───────────────

    @mcp.resource("arifos://atlas333/index")
    async def atlas333_index() -> str:
        """ATLAS333 root index — consolidated cognitive geometry."""
        return json.dumps(
            {
                "atlas_id": "ATLAS333",
                "version": "v1.0.0-zen",
                "description": "Cognitive geometry of arifOS — 33 paradoxes, 33 quotes, 7 zones, TEARFRAME thresholds",
                "resources_mcp": [
                    "arifos://atlas333/index",
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

    # ── arifos://atlas333/scar/{id} — Sealed scar (OPERATIONAL — KEPT) ──

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

    # ── arifos://atlas333/seal/head — VAULT999 chain head (OPERATIONAL — KEPT) ──

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

    # ── RESTORED (2026-07-19): 10 resources re-exposed post-ZEN ──────────
    # Data sources already live in _PARADOXES, _ZONES, _ACTIVATION_RULES,
    # _TEARFRAME, _PIPELINE_STAGES, _GEOMETRY_TERRITORIES.
    # Quotes are dynamically built from paradox_quotes canon (single source).

    @mcp.resource("arifos://atlas333/paradox/list")
    async def paradox_list() -> str:
        """All 33 paradoxes with axes, zones, organs."""
        return json.dumps(_PARADOXES, indent=2)

    registered.append("arifos://atlas333/paradox/list")

    @mcp.resource("arifos://atlas333/paradox/{id}")
    async def paradox_by_id(id: str) -> str:
        """Single paradox by ID (1-33) with full context."""
        try:
            pid = int(id)
            if pid in _PARADOX_BY_ID:
                return json.dumps(_PARADOX_BY_ID[pid], indent=2)
            return json.dumps({"error": f"Paradox {id} not found. Valid: 1-33."})
        except ValueError:
            return json.dumps({"error": f"Invalid paradox ID: {id}"})

    registered.append("arifos://atlas333/paradox/{id}")

    @mcp.resource("arifos://atlas333/zones")
    async def zones() -> str:
        """7 paradox zones with paradox ranges."""
        return json.dumps(_ZONES, indent=2)

    registered.append("arifos://atlas333/zones")

    @mcp.resource("arifos://atlas333/organs")
    async def organs() -> str:
        """3 quote organs (Memory/Mind/Judge)."""
        return json.dumps(
            [
                {"organ": "Memory", "quote_range": "M1-M11", "paradox_range": "1-11"},
                {"organ": "Mind", "quote_range": "R1-R11", "paradox_range": "12-22"},
                {"organ": "Judge", "quote_range": "J1-J11", "paradox_range": "23-33"},
            ],
            indent=2,
        )

    registered.append("arifos://atlas333/organs")

    @mcp.resource("arifos://atlas333/thresholds")
    async def thresholds() -> str:
        """TEARFRAME thresholds (TRM ≥ 0.94, ECHO ≥ 0.87, RASA ≥ 0.85)."""
        return json.dumps(_TEARFRAME, indent=2)

    registered.append("arifos://atlas333/thresholds")

    @mcp.resource("arifos://atlas333/activation/rules")
    async def activation_rules() -> str:
        """GPV→paradox activation matrix (6 canonical patterns)."""
        return json.dumps(_ACTIVATION_RULES, indent=2)

    registered.append("arifos://atlas333/activation/rules")

    @mcp.resource("arifos://atlas333/flow")
    async def flow() -> str:
        """10-stage ATLAS333 intelligence pipeline (INGEST→SEAL)."""
        return json.dumps(_PIPELINE_STAGES, indent=2)

    registered.append("arifos://atlas333/flow")

    @mcp.resource("arifos://atlas333/geometry")
    async def geometry() -> str:
        """Full cognitive geometry map (territories × geometries × depths)."""
        return json.dumps(_GEOMETRY_TERRITORIES, indent=2)

    registered.append("arifos://atlas333/geometry")

    @mcp.resource("arifos://atlas333/quote/list")
    async def quote_list() -> str:
        """All 33 quotes (M1-M11, R1-R11, J1-J11) with author, organ, trigger."""
        try:
            from arifosmcp.constitution.paradox_quotes import ALL_PARADOX_QUOTES

            quotes = []
            for qid in sorted(ALL_PARADOX_QUOTES.keys(), key=lambda x: (x[0], int(x[1:]))):
                q = ALL_PARADOX_QUOTES[qid]
                quotes.append(
                    {
                        "quote_id": qid,
                        "paradox_id": _QUOTE_ID_TO_PARADOX_ID.get(qid),
                        "organ": q.organ.value,
                        "axis": q.axis.value,
                        "axis_label": q.axis_label,
                        "trigger_condition": q.trigger_condition,
                        "norm": q.norm.value,
                    }
                )
            return json.dumps(quotes, indent=2)
        except Exception as exc:
            return json.dumps({"error": f"Cannot build quote list: {exc}"})

    registered.append("arifos://atlas333/quote/list")

    @mcp.resource("arifos://atlas333/quote/{id}")
    async def quote_by_id(id: str) -> str:
        """Single quote by ID (M1-M11, R1-R11, J1-J11) with full context."""
        try:
            from arifosmcp.constitution.paradox_quotes import ALL_PARADOX_QUOTES

            qid = id.upper()
            if qid in ALL_PARADOX_QUOTES:
                q = ALL_PARADOX_QUOTES[qid]
                return json.dumps(
                    {
                        "quote_id": qid,
                        "paradox_id": _QUOTE_ID_TO_PARADOX_ID.get(qid),
                        "organ": q.organ.value,
                        "axis": q.axis.value,
                        "axis_label": q.axis_label,
                        "trigger_condition": q.trigger_condition,
                        "norm": q.norm.value,
                        "full_quote": q.to_dict(),
                    },
                    indent=2,
                )
            return json.dumps({"error": f"Quote {id} not found. Valid: M1-M11, R1-R11, J1-J11."})
        except Exception as exc:
            return json.dumps({"error": f"Cannot read quote: {exc}"})

    registered.append("arifos://atlas333/quote/{id}")

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
