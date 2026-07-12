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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

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

PERMITTED_STAGES = frozenset({"555_HEART", "999_RECEIPT"})
FORBIDDEN_STAGES = frozenset(
    {"000_INIT", "111_OBSERVE", "333_THINK", "444_ROUTE", "777_FORGE", "888_AUDIT"}
)

VALID_USES = frozenset({"REFLECTION", "RECEIPT", "EDUCATION", "RED_TEAM"})

# Canonical registry: v2 (zen-witness-doctrine). v1 retained on disk as legacy only.
_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "quote_registry_v2.json"
_registry_cache: Optional[dict] = None


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
    provenance_warning: Optional[str] = None
    disputed: bool = False
    is_doctrine: bool = False


@dataclass
class ResolveResult:
    """Result of a wisdom_quote_resolve call."""

    quote: Optional[QuoteResult] = None
    selection_reason: str = ""
    provenance_warning: Optional[str] = None
    candidates_considered: int = 0

    def to_dict(self) -> dict:
        return {
            "quote": self.quote.__dict__ if self.quote else None,
            "selection_reason": self.selection_reason,
            "provenance_warning": self.provenance_warning,
            "candidates_considered": self.candidates_considered,
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


# ═══════════════════════════════════════════════════════════════════════════════
# RESOLVE
# ═══════════════════════════════════════════════════════════════════════════════


def wisdom_quote_resolve(
    context_tags: list[str],
    intended_use: str,
    traditions_allowed: Optional[list[str]] = None,
    exclude_disputed: bool = True,
    maximum_quotes: int = 1,
    arifos_floors: Optional[list[str]] = None,
    dark_modes: Optional[list[str]] = None,
) -> ResolveResult:
    """Resolve a provenance-qualified quotation for a completed analysis.

    This is the SINGLE canonical quote resolver. All organs use this.
    Quotes are selected AFTER verdict, never before.

    Parameters
    ----------
    context_tags : list[str]
        Tags describing the context (e.g., ["truth", "self_deception", "humility"])
    intended_use : str
        One of: REFLECTION, RECEIPT, EDUCATION, RED_TEAM
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
    ResolveResult with quote, selection_reason, and provenance_warning.
    May return no quote (quote=None) — silence is better than forced wisdom.
    """
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
    )


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
        "tradition": classification.get("tradition", []) if isinstance(classification, dict) else [],
        "arifos_floors": classification.get("arifos_floors", []) if isinstance(classification, dict) else [],
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
    "PROVENANCE_CLASSES",
    "PERMITTED_STAGES",
]
