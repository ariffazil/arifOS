"""
arifosmcp/runtime/quote_registry.py — Canonical Quote Registry v1

Loads and governs the provenance-typed wisdom quote registry.
Implements Arif's 2026-07-12 directive:
- 8 provenance classes
- Quotes are resources, not tools
- Only permitted at 555 HEART and 999 RECEIPT
- Verdict invariance: quote must never alter verdict

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path

# Path Y dedup (2026-07-19): import constants from single source of truth
from arifosmcp.runtime.quote_constants import (
    APEX_ORGANS,
    C_DARK_CEILING,
    FORBIDDEN_STAGES,  # noqa: F401 — re-exported for external importers
    G_DEPLOY_THRESHOLD,
    PERMITTED_STAGES,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATION CONTRACT — Layer B (2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Per the federation contract, every quote must carry a stable namespace URI
# so any organ can resolve provenance without depending on a Python import path.
# URI scheme: arifos://wisdom/{doctrine|quote}/{id}
#
# Federation deployment fields:
#   namespace_uri     — canonical pointer (every organ can dereference via /resources)
#   organs_safe       — list of organ ports where this quote may inject
#   cardinality       — one of "single" | "many" | "atlas"
#   injection_target  — envelope field name where quote rides (default "philosophy_anchor")
#   ratify_gate       — what must be true to promote from DRAFT → PROVISIONAL → CANON_SEALED

FEDERATION_NAMESPACE_PREFIX = "arifos://wisdom"
INJECTION_TARGET_FIELD = "philosophy_anchor"  # envelope field name (legacy compat)

# Organs where wisdom injection is safe (federation contract).
# These organs expose the arifos://wisdom/{...} resources and accept philosophy_anchor.
FEDERATION_ORGANS_SAFE = frozenset(
    {
        "arifos:8088",  # kernel — primary resolution
        "aforge:7071",  # forge — execution shell
        "aforge:7072",  # forge — mcp gateway
        "geox:8081",  # geoscience
        "wealth:18082",  # capital
        "well:18083",  # human readiness
        "aaa:3001",  # cockpit / A2A
    }
)


def build_namespace_uri(kind: str, quote_id: str) -> str:
    """Build canonical federation namespace URI for a quote.

    Examples:
        build_namespace_uri("quote", "INIT_Q_001")
        → "arifos://wisdom/quote/INIT_Q_001"
        build_namespace_uri("doctrine", "DOCTRINE_AMANAH")
        → "arifos://wisdom/doctrine/DOCTRINE_AMANAH"

    The URI is the machine-readable identity. Display labels live in
    attribution.display.attribution_label — never in the URI.
    """
    if not quote_id:
        raise ValueError("quote_id required for namespace URI")
    kind_norm = kind.lower().strip()
    if kind_norm not in {"quote", "doctrine", "atlas"}:
        raise ValueError(f"Invalid kind {kind!r}; must be quote|doctrine|atlas")
    return f"{FEDERATION_NAMESPACE_PREFIX}/{kind_norm}/{quote_id}"


def build_federation_contract(
    quote: dict,
    quote_kind: str = "quote",
    intended_use: str = "REFLECTION",
) -> dict:
    """Build the federation contract envelope for a quote.

    Layer B contract fields (all organs must consume):
      namespace_uri     — arifos://wisdom/{kind}/{id}  (canonical pointer)
      quote_id          — local id (init_q_001 etc.)
      quote_kind        — "quote" | "doctrine" | "atlas"
      canon_status      — DRAFT | PROVISIONAL | CANON_SEALED  (Layer C mirror)
      apex_fingerprint  — G, C_dark, organs dict         (Layer A mirror)
      organs_safe       — list of organ:port that may inject this
      cardinality       — "single" | "many" | "atlas"
      injection_target  — envelope field name
      ratify_gate       — promotion conditions (dict)
      deploy_warrant    — bool (from APEX fingerprint)

    Returns a dict that callers may attach to envelope under
    `affordance.wisdom_contract` or top-level `wisdom_contract`.
    """
    qid = _quote_id(quote) if quote_kind != "atlas" else quote.get("atlas_id", "")
    fingerprint = compute_apex_fingerprint(quote, intended_use=intended_use)
    canon = compute_canon_status(quote)

    # ratify_gate — conditions for promotion
    if canon == "DRAFT":
        ratify_gate = {
            "current_tier": "DRAFT",
            "promotion_to": "PROVISIONAL",
            "requires": ["≥3 successful uses", "no F-floor violations"],
            "automatic": False,
        }
    elif canon == "PROVISIONAL":
        ratify_gate = {
            "current_tier": "PROVISIONAL",
            "promotion_to": "CANON_SEALED",
            "requires": ["sovereign signature (F13)", "VAULT999 chain append"],
            "automatic": False,
        }
    else:  # CANON_SEALED
        ratify_gate = {
            "current_tier": "CANON_SEALED",
            "promotion_to": None,
            "requires": [],
            "automatic": False,
        }

    # cardinality — how often this quote may fire
    if quote_kind == "doctrine":
        cardinality = "single"  # doctrine: once per session
    elif quote.get("attribution", {}).get("source_class") == "PROVERB":
        cardinality = "many"  # proverbs: reusable across context
    else:
        cardinality = "single"

    return {
        "namespace_uri": build_namespace_uri(quote_kind, qid),
        "quote_id": qid,
        "quote_kind": quote_kind,
        "canon_status": canon,
        "apex_fingerprint": fingerprint,
        "organs_safe": sorted(FEDERATION_ORGANS_SAFE),
        "cardinality": cardinality,
        "injection_target": INJECTION_TARGET_FIELD,
        "ratify_gate": ratify_gate,
        "deploy_warrant": fingerprint.get("deploy_warrant", False),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# APEX ALIGNMENT — Layer A (2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Seven conservation organs (per APEX canon v1):
#   G = Reality · Governance · Civilization · Execution · Memory · Witness · Meaning
#
# Multiplicative — zero anywhere = collapse. C_dark = shadow term.
# Source of physics: APEX_THEORY canon seal 2026-07-13 (V1 canonical).
#
# Citation rules:
#   G_DEPLOY_THRESHOLD = 0.50 (matches APEX verdict threshold)
#   C_DARK_CEILING = 0.30 (Pillar VI GOVERNED state)
#


class QuoteStageError(Exception):
    """Raised when quote resolution is invoked at a forbidden stage."""


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

PROVENANCE_CLASSES = frozenset(
    {
        "PRIMARY_VERIFIED",
        "SECONDARY_VERIFIED",
        "PARAPHRASE",
        "DISPUTED_ATTRIBUTION",
        "PROVERB",
        "SCRIPTURAL_TRANSLATION",
        "FICTIONAL_VOICE",
        "ARIFOS_DOCTRINE",
    }
)

VALID_USES = frozenset({"REFLECTION", "RECEIPT", "EDUCATION", "RED_TEAM"})

# Canonical registry: v2 (zen-witness-doctrine). v1 retained on disk as legacy only.
_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "quote_registry_v2.json"
# SOT declaration (2026-07-19): schema + contract, regenerated from data.
_REGISTRY_SOT_PATH = Path(__file__).resolve().parent.parent / "data" / "quote_registry_sot.yaml"
_registry_cache: dict | None = None
_registry_sot_cache: dict | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class QuoteResult:
    """A resolved quote with full provenance metadata."""

    quote_id: str
    text: str
    speaker: str
    source_class: str
    attribution_confidence: float
    tradition: list[str]
    tags: list[str]
    arifos_floors: list[str]
    dark_modes: list[str]
    permitted_uses: list[str]
    display_label: str = ""
    provenance_warning: str | None = None
    disputed: bool = False
    is_doctrine: bool = False


@dataclass
class ResolveResult:
    """Result of a wisdom_quote_resolve call.

    Now carries APEX fingerprint (Layer A), canon_status tier (Layer C),
    and deploy_warrant (federation contract). A quote is a witness, not
    an authority — deploy_warrant indicates whether the quote may ride
    along with a verdict without violating F2 TRUTH.
    """

    quote: QuoteResult | None = None
    selection_reason: str = ""
    provenance_warning: str | None = None
    candidates_considered: int = 0
    # Layer A — APEX fingerprint (None if no quote)
    apex_fingerprint: dict | None = None
    # Layer C — canon_status tier
    canon_status: str = "DRAFT"
    # Layer B — federation contract: is this quote safe to deploy with a verdict?
    deploy_warrant: bool = False
    # Layer B — federation namespace contract (URI + organs_safe + ratify_gate)
    wisdom_contract: dict | None = None

    def to_dict(self) -> dict:
        return {
            "quote": self.quote.__dict__ if self.quote else None,
            "selection_reason": self.selection_reason,
            "provenance_warning": self.provenance_warning,
            "candidates_considered": self.candidates_considered,
            "apex_fingerprint": self.apex_fingerprint,
            "canon_status": self.canon_status,
            "deploy_warrant": self.deploy_warrant,
            "wisdom_contract": self.wisdom_contract,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD
# ═══════════════════════════════════════════════════════════════════════════════


def load_registry(force_reload: bool = False) -> dict:
    """Load the canonical quote registry from disk."""
    global _registry_cache
    if _registry_cache is not None and not force_reload:
        return _registry_cache

    if not _REGISTRY_PATH.exists():
        logger.warning("Quote registry not found at %s", _REGISTRY_PATH)
        _registry_cache = {"doctrine": [], "quotes": []}
        return _registry_cache

    with _REGISTRY_PATH.open("r", encoding="utf-8") as fh:
        _registry_cache = json.load(fh)

    logger.info(
        "Loaded quote registry: %d doctrine + %d quotes",
        len(_registry_cache.get("doctrine", [])),
        len(_registry_cache.get("quotes", [])),
    )
    return _registry_cache


def load_registry_sot(force_reload: bool = False) -> dict:
    """Load the quote registry SOT declaration (YAML).

    The SOT (Source of Truth) describes the schema, contract, and injection
    map. The DATA (JSON) holds the actual entries. Both are canonical;
    SOT declares HOW the data flows to MCP tools.

    Returns dict with keys: provenance_classes, stage_policy, apex_policy,
    canon_status, namespace, tool_injection_map, intended_uses, tests, etc.

    Returns {} if SOT file is missing (runtime falls back to legacy behavior).
    """
    global _registry_sot_cache
    if _registry_sot_cache is not None and not force_reload:
        return _registry_sot_cache

    if not _REGISTRY_SOT_PATH.exists():
        logger.debug("Quote registry SOT not found at %s", _REGISTRY_SOT_PATH)
        _registry_sot_cache = {}
        return _registry_sot_cache

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        logger.debug("PyYAML not installed; SOT loader disabled")
        _registry_sot_cache = {}
        return _registry_sot_cache

    try:
        with _REGISTRY_SOT_PATH.open("r", encoding="utf-8") as fh:
            _registry_sot_cache = yaml.safe_load(fh) or {}
        logger.info("Loaded quote registry SOT: %s", _REGISTRY_SOT_PATH.name)
    except Exception as exc:
        logger.warning("Failed to load SOT %s: %s", _REGISTRY_SOT_PATH.name, exc)
        _registry_sot_cache = {}

    return _registry_sot_cache


# ═══════════════════════════════════════════════════════════════════════════════
# RESOLVE
# ═══════════════════════════════════════════════════════════════════════════════


def wisdom_quote_resolve(
    context_tags: list[str],
    intended_use: str,
    stage: str = "555_HEART",  # Layer D: stage is now required positional
    traditions_allowed: list[str] | None = None,
    exclude_disputed: bool = True,
    maximum_quotes: int = 1,
    arifos_floors: list[str] | None = None,
    dark_modes: list[str] | None = None,
    enforce_stage_binding: bool = True,  # Layer D: default ON
) -> ResolveResult:
    """[LEGACY-ENTRY-POINT — 2026-07-19 unification]

    Resolve a provenance-qualified quotation for a completed analysis.

    This is the SINGLE canonical quote resolver. All organs use this.
    Quotes are selected AFTER verdict, never before.

    For NEW code, prefer ``philosophy_registry.resolve_quote()`` — it has
    the unified schema (APEX fingerprint, federation URI, stage gate, and
    tool-curated mapping) and is THE canonical resolution path. This function
    is retained for backward compatibility with existing 555/999 callers.

    Behavior preserved: same algorithm, same field names, same exception type.

    Parameters
    ----------
    context_tags : list[str]
        Tags describing the context (e.g., ["truth", "self_deception", "humility"])
    intended_use : str
        One of: REFLECTION, RECEIPT, EDUCATION, RED_TEAM
    stage : str
        Stage at which the quote is being attached. MUST be in
        PERMITTED_STAGES (555_HEART or 999_RECEIPT). Hard-gated by
        default; raise QuoteStageError otherwise.
    enforce_stage_binding : bool
        If True (default), reject calls from forbidden stages with
        QuoteStageError. If False, soft-warn only (legacy callers).
    traditions_allowed : list[str], optional
        Filter to specific traditions. If None, all traditions allowed.
    exclude_disputed : bool
        If True (default), exclude DISPUTED_ATTRIBUTION quotes.
    maximum_quotes : int
        Maximum quotes to return (0-1). Default 1.
    arifos_floors : list[str], optional
        Filter quotes that map to these constitutional floors.
    dark_modes : list[str], optional
        Filter quotes that address these dark geometry patterns.

    Returns
    -------
    ResolveResult with quote, APEX fingerprint, canon_status, deploy_warrant,
    selection_reason, and provenance_warning. May return no quote (quote=None)
    — silence is better than forced wisdom.
    """
    # ── Layer D: hard stage gate ────────────────────────────────────────────
    if enforce_stage_binding and stage not in PERMITTED_STAGES:
        raise QuoteStageError(
            f"Quote resolution forbidden at stage {stage!r}. "
            f"Permitted stages: {sorted(PERMITTED_STAGES)}. "
            f"Quotes are resources, not tools — only at 555_HEART or 999_RECEIPT."
        )

    if intended_use not in VALID_USES:
        return ResolveResult(
            selection_reason=f"Invalid intended_use: {intended_use}. Must be one of {sorted(VALID_USES)}",
            provenance_warning="QUERY_REJECTED",
        )

    if maximum_quotes == 0:
        return ResolveResult(selection_reason="maximum_quotes=0 — no quote requested")

    registry = load_registry()
    all_quotes = registry.get("quotes", [])
    doctrine = registry.get("doctrine", [])

    candidates: list[tuple[float, dict]] = []

    for q in all_quotes:
        # --- Resolve v2 schema: text is a string, id is quote_id ---
        q_id = q.get("id", q.get("quote_id", ""))
        q_text = q.get("text", "")
        if isinstance(q_text, dict):
            q_text = q_text.get("canonical", q_text.get("normalized", ""))
        attr = q.get("attribution", {})
        source_class = attr.get("source_class", "")

        # Exclude disputed if requested
        if exclude_disputed and source_class == "DISPUTED_ATTRIBUTION":
            continue

        # Exclude fictional voices for RECEIPT use
        if intended_use == "RECEIPT" and source_class == "FICTIONAL_VOICE":
            continue

        # Tradition filter
        if traditions_allowed:
            q_traditions = set(q.get("classification", {}).get("tradition", []))
            if not q_traditions & set(traditions_allowed):
                continue

        # Usage permission check
        permitted = set(q.get("usage", {}).get("permitted", []))
        use_map = {
            "REFLECTION": "reflection",
            "RECEIPT": "receipt",
            "EDUCATION": "educational_explanation",
            "RED_TEAM": "red_team",
        }
        if use_map[intended_use] not in permitted and "reflection" not in permitted:
            continue

        # --- Scoring ---
        score = 0.0
        relevance_signal = 0.0  # Must be >0 for quote to be considered relevant
        classification = q.get("classification", {})
        q_tags = set(classification.get("tags", []))
        q_floors = set(classification.get("arifos_floors", []))
        q_dark = set(classification.get("dark_modes", []))

        # Tag overlap (primary signal)
        context_set = set(t.lower() for t in context_tags)
        tag_overlap = q_tags & context_set
        relevance_signal += len(tag_overlap) * 3.0

        # Floor match
        if arifos_floors:
            floor_set = set(arifos_floors)
            floor_overlap = q_floors & floor_set
            relevance_signal += len(floor_overlap) * 2.0

        # Dark mode match
        if dark_modes:
            dark_set = set(dark_modes)
            dark_overlap = q_dark & dark_set
            relevance_signal += len(dark_overlap) * 2.5

        # Gate: attribution confidence only contributes if there's relevance signal
        if relevance_signal <= 0:
            continue

        score = relevance_signal

        # Attribution confidence boost (only after relevance gate)
        confidence = attr.get("attribution_confidence", 0.5)
        if source_class == "PRIMARY_VERIFIED":
            score += confidence * 2.0
        elif source_class == "SECONDARY_VERIFIED":
            score += confidence * 1.0
        elif source_class in ("PARAPHRASE", "PROVERB"):
            score += confidence * 0.5
        elif source_class == "SCRIPTURAL_TRANSLATION":
            score += confidence * 0.8

        # Avoid fictional voices for serious use
        if source_class == "FICTIONAL_VOICE" and intended_use in ("RECEIPT", "RED_TEAM"):
            score *= 0.3

        if score > 0:
            candidates.append((score, q))

    # Sort descending by score
    candidates.sort(key=lambda x: -x[0])

    # Take top-k
    selected = candidates[:maximum_quotes]

    if not selected:
        return ResolveResult(
            selection_reason="No quote matched the given context tags and filters",
            provenance_warning="NO_MATCH",
            candidates_considered=len(candidates),
        )

    best_score, best_q = selected[0]
    attr = best_q.get("attribution", {})
    classification = best_q.get("classification", {})
    usage = best_q.get("usage", {})
    display = best_q.get("display", {})
    text = best_q.get("text", {})

    source_class = attr.get("source_class", "")
    disputed = source_class == "DISPUTED_ATTRIBUTION"

    # Build provenance warning
    provenance_warning = None
    if disputed:
        provenance_warning = f"DISPUTED_ATTRIBUTION — {attr.get('commonly_attributed_to', 'Unknown')}. Not primary-verified."
    elif source_class == "PARAPHRASE":
        provenance_warning = f"PARAPHRASE — not exact wording. {attr.get('note', '')}"
    elif source_class == "FICTIONAL_VOICE":
        provenance_warning = f"FICTIONAL_VOICE — spoken by {attr.get('speaker', 'a fictional character')}. Literary, not empirical."
    elif source_class == "PROVERB":
        provenance_warning = "PROVERB — traditional saying without single confirmed author."
    elif source_class == "ARIFOS_DOCTRINE":
        provenance_warning = (
            "ARIFOS_DOCTRINE — original constitutional language. Not civilisational witness."
        )

    display_label = display.get("attribution_label", "")
    if not display_label and disputed:
        display_label = f"Commonly attributed to {attr.get('commonly_attributed_to', attr.get('speaker', 'Unknown'))}"
    elif not display_label:
        speaker = attr.get("speaker", "Unknown")
        work = attr.get("work", "")
        display_label = f"{speaker}" + (f", {work}" if work else "")

    # v2: text may be string or dict; id may be 'id' or 'quote_id'
    q_id_final = best_q.get("id", best_q.get("quote_id", ""))
    q_text_final = best_q.get("text", "")
    if isinstance(q_text_final, dict):
        q_text_final = q_text_final.get("canonical", q_text_final.get("normalized", ""))

    quote = QuoteResult(
        quote_id=q_id_final,
        text=q_text_final,
        speaker=attr.get("speaker", "Unknown"),
        source_class=source_class,
        attribution_confidence=attr.get("attribution_confidence", 0.0),
        tradition=classification.get("tradition", []),
        tags=classification.get("tags", []),
        arifos_floors=classification.get("arifos_floors", []),
        dark_modes=classification.get("dark_modes", []),
        permitted_uses=usage.get("permitted", []),
        display_label=display_label,
        provenance_warning=provenance_warning,
        disputed=disputed,
        is_doctrine=(source_class == "ARIFOS_DOCTRINE"),
    )

    return ResolveResult(
        quote=quote,
        selection_reason=f"Matched tags: {set(classification.get('tags', [])) & set(t.lower() for t in context_tags)}. Score: {best_score:.1f}",
        provenance_warning=provenance_warning,
        candidates_considered=len(candidates),
        # Layer A — APEX fingerprint attached to envelope
        apex_fingerprint=compute_apex_fingerprint(best_q, intended_use=intended_use),
        # Layer C — canon_status tier
        canon_status=compute_canon_status(best_q),
        # Layer B — federation contract: GOVERNED shadow state only
        deploy_warrant=compute_apex_fingerprint(best_q, intended_use=intended_use)[
            "deploy_warrant"
        ],
        # Layer B — federation namespace contract (Layer B envelope)
        wisdom_contract=build_federation_contract(
            best_q, quote_kind="quote", intended_use=intended_use
        ),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# APEX FINGERPRINT — Layer A (2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════════


def compute_apex_fingerprint(
    quote: dict,
    intended_use: str = "REFLECTION",
    verdict_context: dict | None = None,
) -> dict:
    """APEX fingerprint for a quote in a deployment context.

    Maps the seven conservation organs to per-organ scores, then computes
    G = ∏ organ_i (multiplicative — zero anywhere = collapse).

    Per-organ scoring rationale:
        Reality      — primary_verified gives full credit; secondary/paraphrase/proverb discounted
        Governance   — 1.0 if 'verdict_authority' is in prohibited (i.e. quote cannot alter verdict)
        Civilization — 1.0 if tradition is non-empty (quote lives in a tradition)
        Execution    — 1.0 if action_bias mapped to a verbs category (quote can guide action)
        Memory       — 1.0 if source_class is durable (PRIMARY/SECONDARY/DOCTRINE); else 0.3
        Witness      — attribution_confidence (the human/AI/external collapse to confidence)
        Meaning      — 1.0 if mapped to at least one constitutional floor

    C_dark = shadow term. Driven by disputed attribution, fictional voice,
    or missing prohibited_use list (= hidden shadow).

    Shadow state per Pillar VI:
        GOVERNED   — G >= 0.50, C_dark < 0.30  (safe to deploy)
        UNCHECKED  — C_dark in [0.30, 0.50]   (deploy with caution)
        HIDDEN     — C_dark > 0.50            (TRUE DEVIL risk — do not deploy)

    Args:
        quote: The quote dict.
        intended_use: Primary use classification (default REFLECTION).
        verdict_context: Optional verdict context dict. If provided,
            mapped to intended_use via context.get("intended_use", intended_use).
            This unifies the quote_registry and philosophy_registry call patterns.
    """
    # If verdict_context provided, map to intended_use (Path Y unification)
    if verdict_context is not None and isinstance(verdict_context, dict):
        intended_use = verdict_context.get("intended_use", intended_use)

    classification = quote.get("classification", {}) or {}
    attr = quote.get("attribution", {}) or {}
    usage = quote.get("usage", {}) or {}

    source_class = attr.get("source_class", "")
    confidence = float(attr.get("attribution_confidence", 0.0))

    # Per-organ G contributions
    organs = {
        "Reality": confidence if source_class == "PRIMARY_VERIFIED" else confidence * 0.6,
        "Governance": 1.0 if "verdict_authority" in usage.get("prohibited", []) else 0.0,
        "Civilization": 1.0 if classification.get("tradition") else 0.0,
        "Execution": 1.0 if classification.get("arifos_floors") else 0.5,
        "Memory": 1.0
        if source_class in ("PRIMARY_VERIFIED", "SECONDARY_VERIFIED", "ARIFOS_DOCTRINE")
        else 0.3,
        "Witness": confidence,
        "Meaning": 1.0 if classification.get("arifos_floors") else 0.0,
    }
    # Multiplicative — APEX canon (zero anywhere = collapse)
    try:
        g_score = math.prod(organs.values())
    except Exception:
        g_score = 0.0

    # C_dark — shadow term (Pillar VI)
    c_dark = 0.0
    if source_class == "DISPUTED_ATTRIBUTION":
        c_dark += (1.0 - confidence) * 0.6
    if source_class == "FICTIONAL_VOICE":
        c_dark += 0.3
    # Missing prohibited_use list = hidden shadow (Pillar VI red flag)
    if not usage.get("prohibited"):
        c_dark += 0.1
    # Fictional voices + RECEIPT/RED_TEAM use = elevated shadow
    if source_class == "FICTIONAL_VOICE" and intended_use in ("RECEIPT", "RED_TEAM"):
        c_dark += 0.2

    # Shadow state
    if c_dark > C_DARK_CEILING + 0.20:  # > 0.50
        shadow_state = "HIDDEN"
        true_devil_risk = True
    elif g_score >= G_DEPLOY_THRESHOLD and c_dark <= C_DARK_CEILING:
        shadow_state = "GOVERNED"
        true_devil_risk = False
    else:
        shadow_state = "UNCHECKED"
        true_devil_risk = False

    return {
        "G": round(g_score, 4),
        "C_dark": round(c_dark, 4),
        "organs": {k: round(v, 4) for k, v in organs.items()},
        "shadow_state": shadow_state,
        "true_devil_risk": true_devil_risk,
        "deploy_warrant": shadow_state == "GOVERNED",
        "thresholds": {
            "G_DEPLOY_THRESHOLD": G_DEPLOY_THRESHOLD,
            "C_DARK_CEILING": C_DARK_CEILING,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CANON STATUS — Layer C (2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════════

# Three-tier ratification ladder. Matches VAULT999 ladder semantics.
CANON_STATUS_TIERS = ("DRAFT", "PROVISIONAL", "CANON_SEALED")
DEFAULT_CANON_STATUS = "DRAFT"

# DRAFT council entries (2026-07-19) — sovereign ratification required to promote.
# See quote_registry_v2.json _metadata.council_v1_note.
_DRAFT_COUNCIL_IDS = frozenset(
    {
        "COUNCIL_GOV_01",
        "COUNCIL_GOV_02",
        "COUNCIL_GOV_03",
        "COUNCIL_GOV_04",
        "COUNCIL_GOV_05",
        "COUNCIL_GOV_07",
        "COUNCIL_PAR_01",
        "COUNCIL_PAR_02",
        "COUNCIL_PAR_03",
        "COUNCIL_PAR_05",
        "COUNCIL_VOID_04",
        "COUNCIL_VOID_05",
        "COUNCIL_VOID_06",
        "COUNCIL_VOID_07",
        "COUNCIL_VOID_08",
        "COUNCIL_VOID_09",
        "COUNCIL_VOID_10",
    }
)


def compute_canon_status(quote: dict) -> str:
    """Determine canon_status tier for a quote.

    Tier ladder:
        DRAFT        — newly forged, not load-bearing (default for everything)
        PROVISIONAL  — ≥3 successful uses, no failures (not auto-promoted; manual)
        CANON_SEALED — appended to VAULT999 chain with sovereign signature

    NOTE: Council layer entries (COUNCIL_*) are FORCED to DRAFT regardless of
    any in-registry hint. Promotion requires sovereign ratification via the
    arif_judge → arif_seal → VAULT999 chain. No automatic promotion.
    """
    qid = quote.get("id") or quote.get("quote_id", "")
    if qid in _DRAFT_COUNCIL_IDS:
        return "DRAFT"

    # Doctrine entries carry their own ratification field
    if quote.get("ratification_status") == "CONSTITUTIONAL":
        return "PROVISIONAL"

    # Check registry metadata for explicit tier override
    reg_status = quote.get("status", {})
    if isinstance(reg_status, dict):
        if reg_status.get("ratification") == "CANON_SEALED":
            return "CANON_SEALED"

    return DEFAULT_CANON_STATUS


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT
# ═══════════════════════════════════════════════════════════════════════════════


def _quote_text(q: dict) -> str:
    """Normalize quote text: v2 stores a string; legacy v1 used {canonical,...}."""
    text = q.get("text", "")
    if isinstance(text, dict):
        return str(text.get("canonical") or text.get("normalized") or "")
    return str(text or "")


def _quote_id(q: dict) -> str:
    return str(q.get("id") or q.get("quote_id") or "")


def _doctrine_ratification(d: dict) -> str:
    """Doctrine v2 uses ratification_status; legacy used status.ratification."""
    if d.get("ratification_status"):
        return str(d["ratification_status"])
    status = d.get("status") or {}
    if isinstance(status, dict) and status.get("ratification"):
        return str(status["ratification"])
    return "UNKNOWN"


def _doctrine_tags(d: dict) -> list:
    if isinstance(d.get("tags"), list):
        return d["tags"]
    classification = d.get("classification") or {}
    if isinstance(classification, dict):
        return classification.get("tags", []) or []
    return []


def audit_quote(text: str, claimed_author: str) -> dict:
    """Audit a quote: return probable class, source status, and confidence.

    This is the audit mode of the resolver.
    """
    registry = load_registry()
    all_quotes = registry.get("quotes", [])
    doctrine = registry.get("doctrine", [])

    text_norm = text.strip().lower()
    author_norm = claimed_author.strip().lower()

    for q in all_quotes:
        q_text = _quote_text(q).strip().lower()
        attr = q.get("attribution") or {}
        q_speaker = str(attr.get("speaker", "")).strip().lower()
        q_commonly = str(attr.get("commonly_attributed_to", "")).strip().lower()

        # Text fuzzy match (simple substring)
        if q_text and (text_norm in q_text or q_text in text_norm):
            # Author match
            if author_norm == q_speaker or author_norm == q_commonly:
                display = q.get("display") or {}
                display_label = ""
                if isinstance(display, dict):
                    display_label = display.get("attribution_label", "") or ""
                return {
                    "found": True,
                    "quote_id": _quote_id(q),
                    "source_class": attr.get("source_class"),
                    "attribution_confidence": attr.get("attribution_confidence"),
                    "required_display_label": display_label,
                    "note": attr.get("note", ""),
                }

    # Check doctrine
    for d in doctrine:
        d_text = str(d.get("text", "")).strip().lower()
        if d_text and (text_norm in d_text or d_text in text_norm):
            return {
                "found": True,
                "doctrine_id": d.get("doctrine_id"),
                "source_class": "ARIFOS_DOCTRINE",
                "attribution_confidence": 1.0,
                "required_display_label": "ARIFOS_DOCTRINE — original constitutional language",
                "ratification": _doctrine_ratification(d),
                "note": "This is arifOS doctrine, not a civilisational quotation.",
            }

    return {
        "found": False,
        "source_class": "UNKNOWN",
        "attribution_confidence": 0.0,
        "required_display_label": "Unverified — not in canonical registry",
        "note": "This quotation is not in the canonical quote registry.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE QUERIES
# ═══════════════════════════════════════════════════════════════════════════════


def get_quotes_by_floor(floor_id: str) -> list[dict]:
    """Return all quotes mapped to a constitutional floor."""
    registry = load_registry()
    result = []
    for q in registry.get("quotes", []):
        floors = q.get("classification", {}).get("arifos_floors", [])
        if floor_id in floors:
            result.append(_summarize_quote(q))
    return result


def get_quotes_by_tradition(tradition: str) -> list[dict]:
    """Return all quotes from a specific tradition."""
    registry = load_registry()
    result = []
    for q in registry.get("quotes", []):
        traditions = q.get("classification", {}).get("tradition", [])
        if tradition.lower() in [t.lower() for t in traditions]:
            result.append(_summarize_quote(q))
    return result


def get_disputed_quotes() -> list[dict]:
    """Return all quotes with disputed attribution."""
    registry = load_registry()
    result = []
    for q in registry.get("quotes", []):
        if q.get("attribution", {}).get("source_class") == "DISPUTED_ATTRIBUTION":
            result.append(_summarize_quote(q))
    return result


def get_doctrine() -> list[dict]:
    """Return all arifOS doctrine entries."""
    registry = load_registry()
    return [
        {
            "doctrine_id": d.get("doctrine_id"),
            "name": d.get("name"),
            "text": d.get("text"),
            "ratification": _doctrine_ratification(d),
            "tags": _doctrine_tags(d),
        }
        for d in registry.get("doctrine", [])
    ]


def get_prohibited_uses() -> list:
    """Return all prohibited use patterns."""
    registry = load_registry()
    prohibited = set()
    for q in registry.get("quotes", []):
        for p in q.get("usage", {}).get("prohibited", []):
            prohibited.add(p)
    return sorted(prohibited)


def _summarize_quote(q: dict) -> dict:
    """Create a safe summary of a quote for resource responses (v1+v2 schema)."""
    attr = q.get("attribution") or {}
    classification = q.get("classification") or {}
    display = q.get("display") or {}
    display_label = ""
    if isinstance(display, dict):
        display_label = display.get("attribution_label", "") or ""
    if not display_label:
        display_label = attr.get("speaker", "") or ""

    return {
        "quote_id": _quote_id(q),
        "text": _quote_text(q),
        "speaker": attr.get("speaker", "Unknown"),
        "source_class": attr.get("source_class", ""),
        "attribution_confidence": attr.get("attribution_confidence", 0.0),
        "display_label": display_label,
        "tradition": classification.get("tradition", [])
        if isinstance(classification, dict)
        else [],
        "arifos_floors": classification.get("arifos_floors", [])
        if isinstance(classification, dict)
        else [],
    }


__all__ = [
    "wisdom_quote_resolve",
    "audit_quote",
    "load_registry",
    "get_quotes_by_floor",
    "get_quotes_by_tradition",
    "get_disputed_quotes",
    "get_doctrine",
    "get_prohibited_uses",
    "QuoteResult",
    "ResolveResult",
    "QuoteStageError",  # Layer D
    "PROVENANCE_CLASSES",
    "PERMITTED_STAGES",
    # Layer A — APEX
    "compute_apex_fingerprint",
    "APEX_ORGANS",
    "G_DEPLOY_THRESHOLD",
    "C_DARK_CEILING",
    # Layer C — canon-status
    "compute_canon_status",
    "CANON_STATUS_TIERS",
    "DEFAULT_CANON_STATUS",
]
