"""
arifosmcp/runtime/philosophy_registry.py — Tool-Quote Registry Loader
═══════════════════════════════════════════════════════════════════════

Centralized loader for tool_quote_registry.json — provides purpose-matched
philosophical anchors with symbolic tag scoring and dimension metrics.

v2.0 (2026-06-28): Added match_score() engine, symbolic tag resolution,
context-to-dimension mapping, and ranked quote selection.

QUOTES ARE NON-CONTAMINATING METADATA. They ride in the philosophical_anchor
envelope for human resonance. They NEVER enter reasoning, logic, 888_JUDGE
deliberation, or VAULT999 sealing criteria.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Registry paths (v3.0 unified, v2.0 fallback) ──────────────────────────
_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "data" / "unified_quotes_registry.json"
_FALLBACK_PATH = Path(__file__).resolve().parents[2] / "data" / "tool_quote_registry.json"
_REGISTRY_CACHE: dict[str, Any] | None = None

# ── Symbolic Tag Lexicon (synced with registry _enriched.tag_lexicon) ─────────
SYMBOLIC_TAGS: dict[str, dict[str, str]] = {
    "SOV": {"name": "Sovereignty", "axis": "individual_vs_collective"},
    "HUM": {"name": "Humility", "axis": "certainty_vs_uncertainty"},
    "PUR": {"name": "Purpose", "axis": "meaning_vs_void"},
    "RES": {"name": "Resilience", "axis": "endurance_vs_break"},
    "RSP": {"name": "Responsibility", "axis": "agency_vs_victimhood"},
    "CHG": {"name": "Change", "axis": "stasis_vs_flux"},
    "TRI": {"name": "Trial", "axis": "ease_vs_hardship"},
    "FRE": {"name": "Freedom", "axis": "autonomy_vs_constraint"},
    "DEC": {"name": "Deception", "axis": "truth_vs_appearance"},
    "POW": {"name": "Power", "axis": "dominance_vs_submission"},
    "EXC": {"name": "Excellence", "axis": "habit_vs_spark"},
    "IMA": {"name": "Imagination", "axis": "known_vs_possible"},
    "MEA": {"name": "Meaning", "axis": "significance_vs_absurdity"},
    "ATT": {"name": "Attitude", "axis": "internal_vs_external"},
    "KNO": {"name": "Knowledge", "axis": "knowing_vs_ignorance"},
    "CHA": {"name": "Character", "axis": "destiny_vs_accident"},
    "DIG": {"name": "Dignity", "axis": "worth_vs_degradation"},
    "ACT": {"name": "Action", "axis": "courage_vs_paralysis"},
}

# ── Context → Dimension Mapping ──────────────────────────────────────────────
# Maps context keywords to the dimension scores they should activate.
CONTEXT_DIMENSION_MAP: dict[str, list[str]] = {
    "high_uncertainty": ["hum", "res", "pur"],
    "institutional_drag": ["sov", "res", "fre"],
    "thin_evidence": ["hum", "kno", "chg"],
    "capital_risk": ["pow", "rsp", "dec"],
    "human_fatigue": ["tri", "res", "mea"],
    "sovereign_decision": ["sov", "rsp", "pur"],
    "claim_creation": ["hum", "kno", "chg"],
    "emv_computation": ["rsp", "pur", "pow"],
    "prospect_evaluation": ["tri", "res", "hum"],
    "seal_irreversible": ["cha", "pur", "mea"],
    "paradox_tension": ["chg", "hum", "fre"],
}


def _load_registry() -> dict[str, Any]:
    """Load unified_quotes_registry.json with caching. Falls back to tool_quote_registry."""
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE
    # Try unified v3.0 first; fallback to tool_quote_registry v2.0
    path = _REGISTRY_PATH if _REGISTRY_PATH.exists() else _FALLBACK_PATH
    if not path.exists():
        logger.debug("No quote registry found")
        _REGISTRY_CACHE = {}
        return _REGISTRY_CACHE
    try:
        _REGISTRY_CACHE = json.loads(path.read_text())
        if _REGISTRY_CACHE is not None:
            n = len(_REGISTRY_CACHE.get("quotes", []))
            logger.info("Loaded %s (%s quotes)", path.name, n)
    except Exception as exc:
        logger.warning("Failed to load registry: %s", exc)
        _REGISTRY_CACHE = {}
    return _REGISTRY_CACHE if _REGISTRY_CACHE is not None else {}


# ── Match Scoring Engine ──────────────────────────────────────────────────────


def compute_match_score(quote: dict[str, Any], context_keywords: list[str] | None = None) -> float:
    """
    Compute 0-1 relevance score for a quote given context keywords.

    Uses the quote's dimension_scores weighted by context-keyword mappings.
    A quote about sovereignty (SOV=1.0) matches "institutional_drag" context
    better than a quote about imagination (IMA=1.0).

    Score = weighted sum of dimension scores that match context
           ÷ max possible sum (normalized to 0-1)

    Args:
        quote: Enriched quote dict with dimension_scores and symbolic_tags
        context_keywords: List of context strings (e.g. ["high_uncertainty",
                         "thin_evidence"])

    Returns:
        Float 0-1, where 1.0 = perfect match
    """
    if not context_keywords:
        return 0.5  # neutral — no context to match against

    dims_v2 = quote.get("dimension_scores", {})
    dims_v3 = quote.get("dims", [])
    if not dims_v2 and not dims_v3:
        return 0.3  # low confidence — no dimension data
    # For v3.0 unified: convert dims list to dict with default 0.7 scores
    if isinstance(dims_v3, list) and not isinstance(dims_v2, dict):
        dims = {d.lower(): 0.7 for d in dims_v3}
    else:
        dims = dims_v2

    # Collect activated dimensions from context keywords
    activated: set[str] = set()
    for kw in context_keywords:
        activated.update(CONTEXT_DIMENSION_MAP.get(kw.lower(), []))

    if not activated:
        return 0.5

    # Weighted sum: sum(dimension_score * weight) / sum(max_weight)
    total_score = 0.0
    max_score = 0.0
    for dim in activated:
        score = dims.get(dim, 0.3)
        # Core dimensions (sov, pur, hum) weighted 2x
        weight = 2.0 if dim in ("sov", "pur", "hum") else 1.0
        total_score += score * weight
        max_score += 1.0 * weight

    if max_score == 0:
        return 0.5

    raw = total_score / max_score
    # Sigmoid compression — avoid extreme 0.0/1.0 (F7 Humility)
    return round(0.2 + 0.6 * raw, 3)


def resolve_context(context: str = "") -> list[str]:
    """Resolve a free-text context string to context keywords."""
    if not context:
        return []
    ctx_lower = context.lower()
    keywords = []
    for kw in CONTEXT_DIMENSION_MAP:
        if kw.replace("_", " ") in ctx_lower or any(word in ctx_lower for word in kw.split("_")):
            keywords.append(kw)
    return keywords if keywords else ["high_uncertainty"]  # default


# ── Quote lookup ──────────────────────────────────────────────────────────────


def lookup_tool_quote(
    tool_name: str, context: str = "", context_keywords: list[str] | None = None
) -> dict[str, Any] | None:
    """
    Look up the BEST purpose-matched philosophical quote for a tool.

    Uses match_score() to rank quotes by contextual relevance when
    multiple quotes exist. Falls back to first "always" trigger.

    Args:
        tool_name: Canonical MCP tool name
        context: Free-text context description
        context_keywords: Explicit context keywords (overrides context parsing)

    Returns:
        Quote dict with keys: quote_id, quote, author, source,
        symbolic_tags, dimension_scores, match_score, source_status
        or None if no tool-specific quote found
    """
    registry = _load_registry()
    if not registry:
        return None

    # Resolve context keywords
    if context_keywords is None and context:
        context_keywords = resolve_context(context)

    # ── v3.0 unified: flat quotes array (dimension-indexed) ──
    quotes = registry.get("quotes", [])
    if quotes and isinstance(quotes, list) and quotes:
        return _pick_best_quote(quotes, context_keywords)

    # ── v2.0 tool_registry: organ/tools structure ──
    for organ_key in ("arifos", "geox", "well", "wealth"):
        organ = registry.get(organ_key, {})
        if not isinstance(organ, dict):
            continue
        tools = organ.get("tools", {})
        if tool_name in tools:
            return _pick_best_quote(tools[tool_name].get("quotes", []), context_keywords)
        sys_tools = organ.get("system_tools", {})
        if tool_name in sys_tools:
            return _pick_best_quote(sys_tools[tool_name].get("quotes", []), context_keywords)

    # ── Cross-cutting ──
    cross = registry.get("cross_cutting", {})
    for section in cross.values():
        if isinstance(section, dict) and section.get("quote"):
            return _format_quote(section["quote"], context_keywords)

    return None


def _pick_best_quote(quotes: list[dict], context_keywords: list[str] | None = None) -> dict | None:
    """Pick the highest-scoring quote for the given context."""
    if not quotes:
        return None

    # Compute match scores for all quotes
    scored = []
    for i, q in enumerate(quotes):
        score = compute_match_score(q, context_keywords)
        trigger = q.get("trigger", "always")
        # "always" trigger gets base score of 0.4; contextual triggers compete on score
        base = 0.4 if trigger == "always" else 0.0
        scored.append((base + score, i, q))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    _, _, best = scored[0]
    return _format_quote(best, context_keywords)


def _format_quote(raw: dict, context_keywords: list[str] | None = None) -> dict[str, Any]:
    """Normalize quote dict to standard envelope format with match score.
    Handles both v2.0 (tool_registry) and v3.0 (unified) field names."""
    match = compute_match_score(raw, context_keywords)
    # v3.0 unified uses 'dims'; v2.0 uses 'symbolic_tags' + 'dimension_scores'
    dims_v2 = raw.get("dimension_scores", {})
    dims_v3 = raw.get("dims", [])
    tags = raw.get("symbolic_tags", dims_v3)
    return {
        "quote_id": raw.get("id", raw.get("canon_id", "TOOL")),
        "quote": raw.get("text", raw.get("quote", "")),
        "author": raw.get("author", "arifOS"),
        "source": raw.get("source", ""),
        "source_status": "VERIFIED",
        "symbolic_tags": tags,
        "dimension_scores": dims_v2 if isinstance(dims_v2, dict) else {},
        "dims": dims_v3 if isinstance(dims_v3, list) else [],
        "rigor": raw.get("rigor"),
        "match_score": match,
    }


def get_tool_quote_for_envelope(
    tool_name: str, context: str = ""
) -> tuple[dict[str, Any] | None, str]:
    """
    Get best tool-specific quote + injection mode for output envelope.

    Uses match_score() to select the contextually most relevant quote.

    Returns (quote_dict, injection_mode) where injection_mode is one of:
      "tool_specific" — found in registry with match_score
      "atlas_27"     — not found, use S×G×Ω coordinate fallback
    """
    quote = lookup_tool_quote(tool_name, context)
    if quote:
        return quote, "tool_specific"
    return None, "atlas_27"


# ── Symbolic Tag Resolution ──────────────────────────────────────────────────


def resolve_symbolic_tag(tag: str) -> dict[str, str]:
    """Resolve a 3-char symbolic tag to its full meaning."""
    return SYMBOLIC_TAGS.get(tag.upper(), {"name": "Unknown", "axis": "unknown"})


def tags_to_meaning(tags: list[str]) -> str:
    """Convert symbolic tags to a human-readable meaning string."""
    names = [SYMBOLIC_TAGS.get(t, {}).get("name", t) for t in tags]
    return " ⊗ ".join(names)


def inject_philosophy(envelope: Any) -> dict[str, Any]:
    """
    Inject philosophical quote into output envelope as metadata.

    QUOTES ARE NON-CONTAMINATING METADATA. They ride in the philosophical_anchor
    envelope for human resonance. They NEVER enter reasoning, logic, 888_JUDGE
    deliberation, or VAULT999 sealing criteria.

    Args:
        envelope: The output envelope (must have .tool_name and .context attributes)

    Returns:
        Dict with quote metadata or empty dict if no quote available
    """
    try:
        tool_name = getattr(envelope, "tool_name", "")
        context = getattr(envelope, "context", "")

        # Get tool-specific quote with context-aware scoring
        quote, injection_mode = get_tool_quote_for_envelope(tool_name, context)

        if quote:
            return {
                "quote": quote.get("quote", ""),
                "author": quote.get("author", ""),
                "source": quote.get("source", ""),
                "symbolic_tags": quote.get("symbolic_tags", []),
                "dimension_scores": quote.get("dimension_scores", {}),
                "match_score": quote.get("match_score", 0.5),
                "injection_mode": injection_mode,
                "metadata_only": True,  # Explicit flag: quotes are metadata, not reasoning
            }
        return {}
    except Exception as exc:
        logger.debug(f"Philosophy injection failed: {exc}")
        return {}


__all__ = [
    "SYMBOLIC_TAGS",
    "CONTEXT_DIMENSION_MAP",
    "compute_match_score",
    "resolve_context",
    "lookup_tool_quote",
    "get_tool_quote_for_envelope",
    "resolve_symbolic_tag",
    "tags_to_meaning",
    "inject_philosophy",
]
