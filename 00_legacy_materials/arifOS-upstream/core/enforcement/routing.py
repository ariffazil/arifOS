"""
Canonical refusal and reality-check routing helpers.

This module is the enforcement-layer source of truth. Legacy callers should use
core.shared.routing, which delegates here for backward compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefusalRule:
    name: str
    risk_domain: str
    patterns: tuple[str, ...]


RULES: tuple[RefusalRule, ...] = (
    RefusalRule(
        name="violence_or_wrongdoing",
        risk_domain="violence",
        patterns=("build a bomb", "make a bomb", "commit murder", "murder", "kill "),
    ),
    RefusalRule(
        name="self_harm",
        risk_domain="self_harm",
        patterns=("commit suicide", "kill myself", "self-harm", "hurt myself"),
    ),
    RefusalRule(
        name="medical_advice",
        risk_domain="medical",
        patterns=("diagnose my symptoms", "diagnose", "medical advice", "prescribe"),
    ),
    RefusalRule(
        name="legal_advice",
        risk_domain="legal",
        patterns=("legal advice", "my lawsuit", "lawsuit", "my attorney"),
    ),
    RefusalRule(
        name="financial_advice",
        risk_domain="financial",
        patterns=("investment advice", "which stock", "stocks", "buy tesla"),
    ),
)

FACTUAL_INDICATORS: tuple[str, ...] = (
    "what is",
    "who is",
    "when did",
    "where is",
    "statistics",
    "research",
    "fact",
    "latest",
    "current",
    "capital of",
)

_COMPATIBILITY_CATEGORY_BY_DOMAIN = {
    "violence": "violence",
    "self_harm": "self_harm",
    "medical": "medical",
    "legal": "legal",
    "financial": "financial",
}


def compatibility_category_for_domain(risk_domain: str) -> str:
    """Map canonical domains to the legacy compatibility labels."""
    return _COMPATIBILITY_CATEGORY_BY_DOMAIN.get(risk_domain, risk_domain)


def detect_refusal_rule(query: str) -> RefusalRule | None:
    """Return the first refusal rule matched by the query, if any."""
    normalized = f" {query.strip().lower()} "
    for rule in RULES:
        if any(pattern in normalized for pattern in rule.patterns):
            return rule
    return None


def should_reality_check(query: str) -> tuple[bool, str | None]:
    """Identify queries that should be grounded against external evidence."""
    normalized = query.strip().lower()
    for indicator in FACTUAL_INDICATORS:
        if indicator in normalized:
            return True, f"matched factual indicator: {indicator}"
    return False, None


__all__ = [
    "FACTUAL_INDICATORS",
    "RefusalRule",
    "compatibility_category_for_domain",
    "detect_refusal_rule",
    "should_reality_check",
]
