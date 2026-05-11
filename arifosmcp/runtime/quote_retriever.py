"""
arifosmcp/runtime/quote_retriever.py — Deterministic Quote Retrieval

Retrieves the top-k most relevant approved quotes for a given event,
using structured field matching.  Semantic retrieval (bge-m3) is planned
for Phase 2; this module provides the deterministic foundation.

Rules:
- Never returns quotes with allow_use=false.
- Never returns quotes with source_status="uncertain".
- Never uses random selection or surface-prefix routing as primary logic.
- Ranking is deterministic and auditable.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from .quote_ledger import load_quote_ledger

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# SCORING CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Weights for composite relevance score (higher = more relevant)
_W_DOMAIN_MATCH = 4.0
_W_RISK_MATCH = 3.0
_W_TRIGGER_MATCH = 3.0
_W_THEME_KEYWORD = 2.0
_W_MAPPING_KEYWORD = 1.5
_W_ACTION_BIAS_COMPAT = 1.0
_W_PRIORITY_BOOST = 0.5


def _tokenize(text: str) -> set[str]:
    """Simple tokenization for overlap scoring."""
    return set(text.lower().split())


def _overlap_score(a: set[str], b: set[str]) -> float:
    """Jaccard-like overlap score."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / max(len(a), len(b))


def _risk_level_index(risk: str) -> int:
    """Ordinal rank of risk levels."""
    order = {"low": 0, "medium": 1, "high": 2, "critical": 3, "irreversible": 4}
    return order.get(risk, 1)


def _risk_match_score(quote_risks: list[str], event_risk: str) -> float:
    """Score how well the quote's risk_use covers the event risk level."""
    event_idx = _risk_level_index(event_risk)
    best = max((_risk_level_index(r) for r in quote_risks), default=0)
    # If quote covers at least the event risk, full score
    if best >= event_idx:
        return 1.0
    # Otherwise, partial score based on gap
    gap = event_idx - best
    return max(0.0, 1.0 - gap * 0.3)


def _action_bias_compatible(bias: str, event_risk: str) -> float:
    """Check if action bias is compatible with event risk."""
    if event_risk in ("critical", "irreversible"):
        # High-risk events prefer caution
        if bias in ("refuse", "hold", "request_approval"):
            return 1.0
        if bias == "pause_and_reflect":
            return 0.7
        if bias == "proceed_carefully":
            return 0.3
        return 0.0
    if event_risk == "high":
        if bias in ("request_approval", "pause_and_reflect", "hold"):
            return 1.0
        if bias == "proceed_carefully":
            return 0.7
        if bias == "refuse":
            return 0.4
        return 0.0
    # low / medium risk
    if bias == "proceed_carefully":
        return 1.0
    if bias in ("pause_and_reflect", "request_approval"):
        return 0.8
    if bias == "hold":
        return 0.4
    if bias == "refuse":
        return 0.2
    return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# RETRIEVAL
# ═══════════════════════════════════════════════════════════════════════════════


def retrieve_witnesses(
    event: str,
    domain: str | list[str],
    risk_level: str = "medium",
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Retrieve the top-k most relevant approved quotes for an event.

    Parameters
    ----------
    event:
        Free-text description of the event / situation.
    domain:
        Primary domain(s) of the event, e.g. "ethics" or ["ethics", "governance"].
    risk_level:
        One of low, medium, high, critical, irreversible.
    top_k:
        Maximum number of quotes to return.

    Returns
    -------
    List of quote dicts ordered by descending relevance score.
    """
    ledger = load_quote_ledger()
    event_tokens = _tokenize(event)
    domains = {domain} if isinstance(domain, str) else set(domain)

    scored: list[tuple[float, dict[str, Any]]] = []

    for quote in ledger:
        # Hard filters
        if not quote.get("allow_use", False):
            continue
        if quote.get("source_status") == "uncertain":
            continue

        score = 0.0

        # 1. Domain match (Hard Filter)
        quote_domains = set(quote.get("domain", []))
        domain_overlap = len(domains & quote_domains)
        if domain_overlap == 0:
            continue
        score += _W_DOMAIN_MATCH * domain_overlap

        # 2. Risk level match
        score += _W_RISK_MATCH * _risk_match_score(
            quote.get("risk_use", []), risk_level
        )

        # 3. Trigger conditions match
        triggers = " ".join(quote.get("trigger_conditions", []))
        trigger_tokens = _tokenize(triggers)
        score += _W_TRIGGER_MATCH * _overlap_score(event_tokens, trigger_tokens)

        # 4. Theme keyword overlap
        theme_tokens = _tokenize(quote.get("theme", ""))
        score += _W_THEME_KEYWORD * _overlap_score(event_tokens, theme_tokens)

        # 5. arifos_mapping keyword overlap
        mapping = quote.get("arifos_mapping", {})
        mapping_text = " ".join(str(v) for v in mapping.values())
        mapping_tokens = _tokenize(mapping_text)
        score += _W_MAPPING_KEYWORD * _overlap_score(event_tokens, mapping_tokens)

        # 6. Action bias compatibility
        bias = quote.get("action_bias", "pause_and_reflect")
        score += _W_ACTION_BIAS_COMPAT * _action_bias_compatible(bias, risk_level)

        # 7. Priority boost (higher priority = slightly higher score)
        priority = quote.get("priority", 5)
        score += _W_PRIORITY_BOOST * (priority / 10.0)

        if score > 0:
            scored.append((score, quote))

    # Sort descending by score, break ties deterministically by id
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))

    result = [q for _score, q in scored[:top_k]]
    logger.debug(
        "retrieve_witnesses: event=%r domain=%r risk=%r returned=%d",
        event,
        domain,
        risk_level,
        len(result),
    )
    return result


__all__ = ["retrieve_witnesses"]
