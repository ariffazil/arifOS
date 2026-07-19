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
from pathlib import Path
from typing import Any

# Path Y dedup (2026-07-19): import constants from single source of truth
from arifosmcp.runtime.quote_constants import APEX_ORGANS, PERMITTED_STAGES

logger = logging.getLogger(__name__)

# ── Registry paths (unified → tool_quote → quote_registry_v2 → philosophy_atlas) ─
# Per audit 2026-07-19: chain the loaders so the canonical injection path
# actually has a source. unified_quotes_registry.json and tool_quote_registry.json
# were archived in /root/.backups/2026-07-04-registry-unification/ but never
# copied to runtime. quote_registry_v2.json IS in runtime. Without this chain,
# philosophy_anchor is empty in every tool response.
#
# NOTE: this file lives at arifosmcp/runtime/philosophy_registry.py.
# The data directory is arifosmcp/data/ — parents[1], not parents[2].
# The previous parents[2] path was a bug; data files at /opt/arifos/app/data/
# never existed. This commit corrects the path.
_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_REGISTRY_PATH = _DATA_DIR / "unified_quotes_registry.json"
_FALLBACK_PATH = _DATA_DIR / "tool_quote_registry.json"
_V2_REGISTRY_PATH = _DATA_DIR / "quote_registry_v2.json"
_ATLAS_PATH = _DATA_DIR / "philosophy_atlas.json"

# APEX_ORGANS and PERMITTED_STAGES imported at top from quote_constants

FORBIDDEN_STAGE_VERDICT = {
    "verdict": "FORBIDDEN_STAGE",
    "verdict_code": "STAGE_BINDING_VIOLATION",
    "reason": (
        "Quotes are resources, not tools. Permitted only at "
        "555_HEART (reflection) and 999_RECEIPT (receipt). "
        "Hard-gate enforced 2026-07-19 per ASI 💃 audit."
    ),
}

# Per-tool anchor cache (fixes session-state leak for stateful tools)
# Key: (session_id_hash, tool_name, response_fingerprint) → anchor dict
# Cleared on session expiry. Bounded LRU.
_ANCHOR_CACHE: dict[str, dict] = {}
_ANCHOR_CACHE_MAX = 256


def compute_apex_fingerprint(quote: dict, verdict_context: dict | None = None) -> dict:
    """APEX G + C_dark fingerprint — thin adapter to canonical impl.

    Path Y dedup (2026-07-19): canonical implementation lives in
    arifosmcp.runtime.quote_registry. This adapter maps verdict_context
    → intended_use for backward compatibility.

    Multiplicative G across 7 organs — zero anywhere collapses consensus.
    C_dark captures shadow governance risk (Pillar VI).
    """
    from arifosmcp.runtime.quote_registry import (
        compute_apex_fingerprint as _canonical,
    )

    # Map verdict_context → intended_use
    intended_use = "REFLECTION"
    if verdict_context is not None and isinstance(verdict_context, dict):
        intended_use = verdict_context.get("intended_use", "REFLECTION")
    return _canonical(quote, intended_use=intended_use, verdict_context=verdict_context)


def stage_gate(stage: str | None, intended_use: str = "REFLECTION") -> dict | None:
    """Hard stage gate. Returns None if allowed, FORBIDDEN_STAGE dict if not.

    Quotes are resources, not tools. Permitted only at 555_HEART (reflection)
    and 999_RECEIPT (receipt). All other stages get FORBIDDEN_STAGE verdict.
    """
    if stage is None:
        return None  # OBSERVE_ONLY test path — no stage assertion possible
    if stage in PERMITTED_STAGES:
        return None
    return {**FORBIDDEN_STAGE_VERDICT, "requested_stage": stage, "intended_use": intended_use}


def cache_anchor(
    session_id: str | None, tool_name: str, response_payload: dict, anchor: dict
) -> None:
    """Cache anchor by session+tool to survive mid-pipeline state mutation.

    Fixes the session-state leak where anchor injection happens AFTER state
    mutation, causing subsequent tool calls to clobber the anchor.
    """
    if not isinstance(anchor, dict) or not anchor.get("text"):
        return
    sid_key = (session_id or "global")[:16]
    # Use payload's status as fingerprint (cheap, stable per response)
    fp = response_payload.get("status") or response_payload.get("verdict") or "?"
    key = f"{sid_key}|{tool_name}|{fp}"
    if len(_ANCHOR_CACHE) >= _ANCHOR_CACHE_MAX:
        # Drop oldest 10% (FIFO — no LRUCache dependency)
        for k in list(_ANCHOR_CACHE.keys())[: _ANCHOR_CACHE_MAX // 10]:
            _ANCHOR_CACHE.pop(k, None)
    _ANCHOR_CACHE[key] = anchor


def get_cached_anchor(
    session_id: str | None, tool_name: str, response_payload: dict
) -> dict | None:
    """Retrieve a previously cached anchor for this session+tool."""
    sid_key = (session_id or "global")[:16]
    fp = response_payload.get("status") or response_payload.get("verdict") or "?"
    return _ANCHOR_CACHE.get(f"{sid_key}|{tool_name}|{fp}")


_REGISTRY_CACHE: dict[str, Any] | None = None
_V2_REGISTRY_CACHE: dict[str, Any] | None = None

# ── Tool → stage map (Layer D wiring, 2026-07-19) ───────────────────────────
# Maps MCP tool name → the metabolic stage it runs at. Only tools that fire
# at 555_HEART or 999_RECEIPT may carry a quote. Other stages return {} from
# inject_philosophy — the tool still works, the quote just doesn't ride along.
#
# Stage rationale (per AGENTS.md §0 — 11-step EUREKA flow):
#   000_INIT   — boot, no quote
#   111_OBSERVE — gather evidence, no quote
#   333_THINK  — draft change, no quote
#   444_ROUTE  — route intent, no quote
#   555_HEART  — reflection / wisdom moment, quote allowed
#   666_JUDGE  — verdict, no quote (must stay clean)
#   777_FORGE  — execute, no quote
#   888_AUDIT  — audit, no quote
#   999_RECEIPT — close, quote allowed (closing resonance)
_TOOL_STAGE_MAP: dict[str, str] = {
    "arif_init": "000_INIT",  # boot — no quote
    "arif_observe": "111_OBSERVE",  # observe — no quote
    "arif_think": "333_THINK",  # think — no quote
    "arif_route": "444_ROUTE",  # route — no quote
    "arif_memory": "555_HEART",  # memory = heart, reflection — quote allowed
    "arif_judge": "666_JUDGE",  # judge — no quote (verdict must be clean)
    "arif_forge": "777_FORGE",  # forge — no quote (execution, not contemplation)
    "arif_seal": "999_RECEIPT",  # seal = receipt — quote allowed (closing resonance)
    # Aliases
    "arif_session_init": "000_INIT",
    "arif_sense_observe": "111_OBSERVE",
    "arif_kernel_route": "444_ROUTE",
    "arif_kernel_attest": "666_JUDGE",
    "arif_canary": "000_INIT",
    "arif_triage": "000_INIT",
    "arif_fetch": "111_OBSERVE",
    "arif_critique": "333_THINK",
    "arif_compose": "777_FORGE",
}


# ── Tool → quote_id mapping (2026-07-19 unification) ─────────────────────────
# Each canonical tool gets a curated quote from quote_registry_v2.json.
# IDs verified against the runtime registry on 2026-07-19.
_TOOL_QUOTE_MAP: dict[str, str] = {
    "arif_init": "INIT_Q_001",  # Lao Tzu: "A journey of a thousand miles begins with a single step."
    "arif_observe": "SENSE_Q_002",  # Feynman: "The first principle is that you must not fool yourself…"
    "arif_think": "INIT_Q_004",  # Socrates: "The only true wisdom is in knowing you know nothing."
    "arif_route": "COUNCIL_GOV_01",  # Bacon: "Nature, to be commanded, must be obeyed."
    "arif_judge": "COUNCIL_GOV_02",  # Madison: "If men were angels, no government would be necessary."
    "arif_forge": "COUNCIL_GOV_04",  # Popper: knowledge finite, ignorance infinite
    "arif_seal": "COUNCIL_GOV_05",  # Wiener: the purpose put into the machine is the purpose we really desire
    "arif_memory": "COUNCIL_PAR_05",  # Al-Ghazali: Knowledge without action is worthless
}
# Aliases for legacy / aliased tool names
_TOOL_ALIAS_MAP: dict[str, str] = {
    "arif_session_init": "arif_init",
    "arif_sense_observe": "arif_observe",
    "arif_kernel_route": "arif_route",
    "arif_kernel_attest": "arif_judge",
    "arif_canary": "arif_init",
    "arif_triage": "arif_init",
    "arif_fetch": "arif_observe",
    "arif_critique": "arif_think",
    "arif_compose": "arif_forge",
}

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


def _load_v2_registry() -> dict[str, Any]:
    """Load quote_registry_v2.json with caching.

    Per audit 2026-07-19: this is the CANONICAL runtime registry because
    unified_quotes_registry.json and tool_quote_registry.json are not in
    runtime. The flat-quotes array schema is v3.0-compatible.
    """
    global _V2_REGISTRY_CACHE
    if _V2_REGISTRY_CACHE is not None:
        return _V2_REGISTRY_CACHE
    if not _V2_REGISTRY_PATH.exists():
        logger.debug("quote_registry_v2.json missing")
        _V2_REGISTRY_CACHE = {}
        return _V2_REGISTRY_CACHE
    try:
        raw = json.loads(_V2_REGISTRY_PATH.read_text())
        # Build a flat v3.0-style quotes array from v2 records
        quotes = []
        by_id = {}
        for q in raw.get("quotes", []):
            adapted = _adapt_v2_quote_to_v3(q)
            if adapted:
                quotes.append(adapted)
                by_id[adapted["id"]] = adapted
        _V2_REGISTRY_CACHE = {
            "quotes": quotes,
            "by_id": by_id,
            "source": "quote_registry_v2.json",
            "version": raw.get("_metadata", {}).get("version", "2.0.0"),
        }
        logger.info("Loaded quote_registry_v2.json (%s quotes)", len(quotes))
    except Exception as exc:
        logger.warning("Failed to load quote_registry_v2.json: %s", exc)
        _V2_REGISTRY_CACHE = {}
    return _V2_REGISTRY_CACHE


def _adapt_v2_quote_to_v3(v2: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a quote_registry_v2.json entry to v3.0 unified schema.

    Maps:
      text            → quote
      attribution.speaker → author
      classification.tags → symbolic_tags
      status.council  → source
      status.reviewer → source_status
      category        → category
    """
    if not isinstance(v2, dict):
        return None
    attribution = v2.get("attribution", {}) or {}
    classification = v2.get("classification", {}) or {}
    status = v2.get("status", {}) or {}
    text = v2.get("text") or v2.get("quote")
    if not text:
        return None
    speaker = attribution.get("speaker") or attribution.get("author") or "arifOS"
    work = attribution.get("work") or ""
    council = status.get("council") or ""
    author_str = f"{speaker}, {work}" if work else speaker
    return {
        "id": v2.get("id", ""),
        "text": text,
        "quote": text,
        "author": author_str,
        "speaker": speaker,
        "source": council or "quote_registry_v2",
        "source_status": status.get("reviewer", "PENDING") if status.get("reviewed") else "PENDING",
        "symbolic_tags": classification.get("tags", []) or [],
        "dimension_scores": {},
        "dims": [],
        "category": v2.get("category", "generated_reflection"),
        "rigor": 1.0 if attribution.get("attribution_confidence", 0) >= 0.9 else 0.7,
        "tradition": classification.get("tradition", []) or [],
        "arifos_floors": classification.get("arifos_floors", []) or [],
        "dark_modes": classification.get("dark_modes", []) or [],
        "_trigger": "always",
    }


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
    # Resolve aliases first
    canonical_tool = _TOOL_ALIAS_MAP.get(tool_name, tool_name)

    # Resolve context keywords
    if context_keywords is None and context:
        context_keywords = resolve_context(context)

    # ── v3.0 unified: flat quotes array (dimension-indexed) ──
    registry = _load_registry()
    if registry:
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

    # ── v2 fallback (2026-07-19 unification) — quote_registry_v2.json ──
    # Per audit: this is the registry actually present in runtime. Map tool
    # → curated quote, fall back to match_score selection across all quotes.
    v2 = _load_v2_registry()
    if v2 and v2.get("by_id"):
        # 1) Curated per-tool mapping wins
        curated_id = _TOOL_QUOTE_MAP.get(canonical_tool)
        if curated_id and curated_id in v2["by_id"]:
            return _format_quote(v2["by_id"][curated_id], context_keywords)
        # 2) Fall back to highest-scoring quote across all 99 entries
        if v2.get("quotes"):
            return _pick_best_quote(v2["quotes"], context_keywords)

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


# ═══════════════════════════════════════════════════════════════════════════════
# INJECT PHILOSOPHY + SELECT PHILOSOPHY STATE
# ═══════════════════════════════════════════════════════════════════════════════


def inject_philosophy(envelope: Any) -> dict[str, Any]:
    """
    Inject philosophical quote into output envelope as metadata.

    QUOTES ARE NON-CONTAMINATING METADATA. They ride in the philosophical_anchor
    envelope for human resonance. They NEVER enter reasoning, logic, 888_JUDGE
    deliberation, or VAULT999 sealing criteria.

    Wired path (Layer A + B + D, 2026-07-19):
      1. Determine the caller's stage (Tool → Stage map)
      2. Call canonical resolver wisdom_quote_resolve (enforces stage binding)
      3. Attach APEX fingerprint (Layer A), canon_status (Layer C),
         wisdom_contract (Layer B namespace URI), deploy_warrant (Layer B)
      4. Return envelope-ready dict — NEVER enters verdict logic

    Args:
        envelope: The output envelope (must have .tool_name and .context attributes)

    Returns:
        Dict with quote + APEX fingerprint + wisdom_contract, or empty dict.
        Returns empty if stage is forbidden (Layer D enforcement).
    """
    # Lazy import to avoid circular: quote_registry → philosophy_registry → resources
    try:
        from arifosmcp.runtime.quote_registry import (
            PERMITTED_STAGES,
            QuoteStageError,
            wisdom_quote_resolve,
        )
    except Exception as exc:
        logger.debug(f"quote_registry import failed: {exc}")
        return {}

    try:
        tool_name = getattr(envelope, "tool_name", "")
        context = getattr(envelope, "context", "")

        # Map tool → stage. Only tools at 555/999 may carry a quote.
        stage = _TOOL_STAGE_MAP.get(tool_name, "")
        if stage not in PERMITTED_STAGES:
            # Forbidden stage — do not inject, do not raise
            # (the tool still works; quote is metadata, not required)
            return {}

        # Resolve context tags. Try tool-curated mapping first (deterministic),
        # then fall back to dimension-derived tags.
        canonical_tool = _TOOL_ALIAS_MAP.get(tool_name, tool_name)
        curated_id = _TOOL_QUOTE_MAP.get(canonical_tool)

        # Use canonical resolver. If curated_id is set, use it via context_tags
        # by also passing tool_name as a hint (resolvers handle tag match).
        # Otherwise fall back to dimension expansion.
        context_tags = resolve_context(context) if context else ["high_uncertainty"]
        # Always include the tool name as a hint to bias matching
        if canonical_tool and canonical_tool not in context_tags:
            context_tags = [canonical_tool] + context_tags

        # Call the canonical resolver (Layer A + B + C + D all enforced)
        try:
            result = wisdom_quote_resolve(
                context_tags=context_tags,
                intended_use="REFLECTION",
                stage=stage,
                enforce_stage_binding=True,
                maximum_quotes=1,
            )
        except QuoteStageError:
            return {}  # silently skip — stage binding rejected

        # If curated_id exists but resolver didn't pick it, override by
        # force-loading from the registry and computing its contract.
        if (not result.quote or result.quote.quote_id != curated_id) and curated_id:
            from arifosmcp.runtime.quote_registry import load_registry

            reg = load_registry()
            for q in reg.get("quotes", []):
                if q.get("id") == curated_id:
                    from arifosmcp.runtime.quote_registry import (
                        QuoteResult,
                        build_federation_contract,
                        compute_apex_fingerprint,
                        compute_canon_status,
                    )

                    fp = compute_apex_fingerprint(q, intended_use="REFLECTION")
                    attr = q.get("attribution", {})
                    classification = q.get("classification", {})
                    text = q.get("text", "")
                    if isinstance(text, dict):
                        text = text.get("canonical", text.get("normalized", ""))
                    qres = QuoteResult(
                        quote_id=curated_id,
                        text=text,
                        speaker=attr.get("speaker", "Unknown"),
                        source_class=attr.get("source_class", ""),
                        attribution_confidence=attr.get("attribution_confidence", 0.0),
                        tradition=classification.get("tradition", []),
                        tags=classification.get("tags", []),
                        arifos_floors=classification.get("arifos_floors", []),
                        dark_modes=classification.get("dark_modes", []),
                        permitted_uses=q.get("usage", {}).get("permitted", []),
                        disputed=attr.get("source_class") == "DISPUTED_ATTRIBUTION",
                        is_doctrine=attr.get("source_class") == "ARIFOS_DOCTRINE",
                    )
                    result = type(result)(
                        quote=qres,
                        selection_reason=f"curated tool quote ({canonical_tool} → {curated_id})",
                        apex_fingerprint=fp,
                        canon_status=compute_canon_status(q),
                        deploy_warrant=fp["deploy_warrant"],
                        wisdom_contract=build_federation_contract(
                            q, quote_kind="quote", intended_use="REFLECTION"
                        ),
                    )
                    break

        if not result.quote:
            return {}

        q = result.quote
        return {
            # ── Layer A: APEX fingerprint ──
            "quote": q.text,
            "author": q.speaker,
            "namespace_uri": result.wisdom_contract.get("namespace_uri")
            if result.wisdom_contract
            else None,
            "canon_status": result.canon_status,  # Layer C
            "deploy_warrant": result.deploy_warrant,  # Layer B
            "apex_fingerprint": result.apex_fingerprint,  # Layer A
            "wisdom_contract": result.wisdom_contract,  # Layer B namespace
            "provenance_warning": result.provenance_warning,
            "metadata_only": True,
            "injection_stage": stage,
            "curated_for_tool": canonical_tool,
        }
    except Exception as exc:
        logger.debug(f"Philosophy injection failed: {exc}")
        return {}


def select_philosophy_state(
    confidence: float = 0.88,
    dS: float = 0.0,
    intervention: float = 0.5,
    session_id: str = "global",
    locks: list[str] | None = None,
) -> dict[str, Any]:
    """
    Select philosophy state based on confidence, entropy, and Gödel locks.

    Returns a dict with at least 'confidence_cap' — the maximum confidence
    the reasoning engine may claim, given current epistemic conditions.

    Called by sensing_protocol._derive_intelligence_state() at line 1901.

    Philosophy:
      - F7 HUMILITY: confidence can never exceed 0.90 (base cap)
      - Gödel locks reduce the cap further (structural incompleteness)
      - High entropy (dS) reduces the cap (uncertain environment)
      - Intervention level modifies exploration posture
    """
    locks = locks or []

    # Base cap: F7 HUMILITY — never claim 1.0 confidence
    cap = 0.90

    # Gödel lock penalties
    lock_penalties = {
        "G1": 0.15,  # Incompleteness — grounding gap
        "G2": 0.10,  # Contradiction
        "G3": 0.10,  # Self-reference
        "G4": 0.05,  # Undecidability
        "V1": 0.20,  # Void — no evidence at all
        "V2": 0.15,  # Void — hallucination risk
    }
    for lock in locks:
        penalty = lock_penalties.get(lock, 0.05)
        cap -= penalty

    # Entropy penalty — high dS means uncertain environment
    if dS > 0.7:
        cap -= 0.10
    elif dS > 0.5:
        cap -= 0.05

    # Floor: never below 0.30 (still allow some signal through)
    cap = max(0.30, min(cap, 0.90))

    return {
        "confidence_cap": cap,
        "locks_active": locks,
        "entropy_dS": dS,
        "intervention": intervention,
        "session_id": session_id,
        "base_cap": 0.90,
        "lock_penalty_total": sum(lock_penalties.get(l, 0.05) for l in locks),
    }


__all__ = [
    "SYMBOLIC_TAGS",
    "CONTEXT_DIMENSION_MAP",
    "APEX_ORGANS",
    "PERMITTED_STAGES",
    "compute_apex_fingerprint",
    "stage_gate",
    "cache_anchor",
    "get_cached_anchor",
    "compute_match_score",
    "resolve_context",
    "lookup_tool_quote",
    "get_tool_quote_for_envelope",
    "resolve_symbolic_tag",
    "tags_to_meaning",
    "inject_philosophy",
    "select_philosophy_state",
    "resolve_quote",
    "federation_uri",
]


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED RESOLVE — Layer A + Layer B + reflection/receipt modes (2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════════
# This is the ONE canonical resolution path. Replaces direct calls to:
#   - quote_registry.wisdom_quote_resolve  (legacy 555/999 stage-bound path)
#   - philosophy_registry.get_tool_quote_for_envelope (current 8-tool path)
#   - wisdom_quotes.CIVILIZATIONAL_CANON  (legacy hardcoded path)
#   - tools.py:_WISDOM_QUOTES  (legacy hardcoded dict)
# All entry points delegate here. Stage binding is hard-enforced.

VALID_USES = frozenset({"REFLECTION", "RECEIPT", "EDUCATION", "RED_TEAM"})
GLOBAL_FORBIDDEN_USES = frozenset({"factual_evidence", "verdict_authority"})


def resolve_quote(
    *,
    quote_id: str | None = None,
    tool_name: str | None = None,
    context: str = "",
    intended_use: str = "REFLECTION",
    stage: str | None = None,
    exclude_disputed: bool = False,
    tradition: str | None = None,
    verdict_context: dict | None = None,
) -> dict[str, Any]:
    """Unified quote resolution — THE ONE path.

    Args:
        quote_id: Direct lookup by id (highest priority)
        tool_name: Lookup by tool (curated mapping)
        context: Free-text context for match_score
        intended_use: REFLECTION / RECEIPT / EDUCATION / RED_TEAM
        stage: 555_HEART / 999_RECEIPT / None. Hard gate enforced when set.
        exclude_disputed: Filter out DISPUTED_ATTRIBUTION entries
        tradition: Filter by tradition (greek_philosophy, malay, etc.)
        verdict_context: Optional verdict context for APEX fingerprint scoring

    Returns:
        {
            "ok": True/False,
            "verdict": "OK" | "FORBIDDEN_STAGE" | "NO_MATCH",
            "quote": {...envelope...} | None,
            "apex_fingerprint": {...} | None,
            "stage_check": {"requested": stage, "permitted": bool},
            "federation_uri": str,
        }
    """
    # ── Stage gate (hard enforcement) ──────────────────────────────────────
    stage_check = {
        "requested": stage,
        "permitted": stage is None or stage in PERMITTED_STAGES,
    }
    if stage is not None and stage not in PERMITTED_STAGES:
        return {
            "ok": False,
            "verdict": "FORBIDDEN_STAGE",
            "verdict_code": "STAGE_BINDING_VIOLATION",
            "quote": None,
            "apex_fingerprint": None,
            "stage_check": stage_check,
            "federation_uri": federation_uri(quote_id or tool_name or "unknown"),
            "reason": FORBIDDEN_STAGE_VERDICT["reason"],
            "requested_stage": stage,
            "intended_use": intended_use,
        }

    # ── Validate intended_use ─────────────────────────────────────────────
    if intended_use not in VALID_USES:
        return {
            "ok": False,
            "verdict": "INVALID_USE",
            "quote": None,
            "apex_fingerprint": None,
            "stage_check": stage_check,
            "federation_uri": federation_uri(quote_id or tool_name or "unknown"),
            "reason": f"intended_use must be one of {sorted(VALID_USES)}",
        }

    # ── Lookup by id (highest priority) ──────────────────────────────────
    raw_quote = None
    if quote_id:
        v2 = _load_v2_registry()
        if v2 and quote_id in v2.get("by_id", {}):
            raw_quote = v2["by_id"][quote_id]
        else:
            # Check unified/tool registries if v2 misses
            for reg in (_load_registry(),):
                if reg and quote_id in {q.get("id"): q for q in reg.get("quotes", [])}:
                    raw_quote = {q.get("id"): q for q in reg.get("quotes", [])}[quote_id]
                    break

    # ── Lookup by tool (curated) ─────────────────────────────────────────
    if raw_quote is None and tool_name:
        canonical_tool = _TOOL_ALIAS_MAP.get(tool_name, tool_name)
        v2 = _load_v2_registry()
        if v2 and v2.get("by_id"):
            curated_id = _TOOL_QUOTE_MAP.get(canonical_tool)
            if curated_id and curated_id in v2["by_id"]:
                raw_quote = v2["by_id"][curated_id]
        if raw_quote is None:
            # Fallback: legacy registry lookup
            legacy = lookup_tool_quote(tool_name, context)
            if legacy:
                raw_quote = legacy

    # ── Filter & format ──────────────────────────────────────────────────
    if raw_quote is None:
        return {
            "ok": False,
            "verdict": "NO_MATCH",
            "quote": None,
            "apex_fingerprint": None,
            "stage_check": stage_check,
            "federation_uri": federation_uri(quote_id or tool_name or "unknown"),
            "reason": "No quote found for the given criteria",
        }

    # Apply filters
    if exclude_disputed:
        attr = raw_quote.get("attribution", {}) or {}
        if attr.get("source_class") == "DISPUTED_ATTRIBUTION":
            return {
                "ok": False,
                "verdict": "NO_MATCH",
                "quote": None,
                "apex_fingerprint": None,
                "stage_check": stage_check,
                "federation_uri": federation_uri(quote_id or tool_name or "unknown"),
                "reason": "DISPUTED_ATTRIBUTION excluded by caller",
            }
    if tradition:
        classification = raw_quote.get("classification", {}) or {}
        if tradition not in (classification.get("tradition") or []):
            return {
                "ok": False,
                "verdict": "NO_MATCH",
                "quote": None,
                "apex_fingerprint": None,
                "stage_check": stage_check,
                "federation_uri": federation_uri(quote_id or tool_name or "unknown"),
                "reason": f"tradition={tradition} not in {classification.get('tradition')}",
            }

    # Check usage permission
    usage = raw_quote.get("usage", {}) or {}
    permitted_uses = set(usage.get("permitted") or [])
    if intended_use not in permitted_uses:
        return {
            "ok": False,
            "verdict": "FORBIDDEN_USE",
            "quote": None,
            "apex_fingerprint": None,
            "stage_check": stage_check,
            "federation_uri": federation_uri(quote_id or tool_name or "unknown"),
            "reason": f"intended_use={intended_use} not permitted for this quote",
        }

    # Format the quote
    formatted = _format_quote(raw_quote, None)
    apex = compute_apex_fingerprint(raw_quote, verdict_context)

    return {
        "ok": True,
        "verdict": "OK",
        "quote": formatted,
        "apex_fingerprint": apex,
        "stage_check": stage_check,
        "federation_uri": federation_uri(formatted.get("quote_id", "?")),
    }


def federation_uri(quote_id: str) -> str:
    """Layer B — federation contract URI scheme (ASI 💃 audit 2026-07-19).

    arifos://wisdom/quotes/{id}
    arifos://wisdom/fingerprint/{id}
    arifos://wisdom/canon-status/{id}
    """
    if not quote_id or quote_id == "?":
        return "arifos://wisdom/quotes/unknown"
    return f"arifos://wisdom/quotes/{quote_id}"


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE OLD DUAL-PATH CODE (2026-07-19 unification)
# ═══════════════════════════════════════════════════════════════════════════════
