"""
core/uncertainty_engine.py — Real-time uncertainty quantification engine.

Computes lexical entropy, claim density, and calibrated confidence
from evidence and text rather than returning static zeros.
"""

from __future__ import annotations

import math
import re
from typing import Any, Sequence


def _shannon_entropy(text: str) -> float:
    """Compute normalized Shannon entropy of a string."""
    if not text:
        return 0.0
    counts: dict[str, int] = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    length = len(text)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    # Normalize to [0, 1] assuming max entropy of log2(256)
    return min(1.0, entropy / 8.0)


def _claim_density(text: str) -> float:
    """Estimate density of factual claims per sentence."""
    if not text:
        return 0.0
    sentences = max(1, len(re.split(r"[.!?]+", text)) - 1)
    claim_words = re.findall(
        r"\b(is|are|was|were|will|must|should|always|never|certainly|definitely|prove|fact)\b",
        text,
        re.IGNORECASE,
    )
    return len(claim_words) / sentences


def _source_diversity(sources: Sequence[str]) -> float:
    """Score diversity of evidence sources."""
    if not sources:
        return 0.0
    unique_domains: set[str] = set()
    for src in sources:
        match = re.search(r"https?://(?:www\.)?([^/]+)", str(src))
        unique_domains.add(
            match.group(1).lower() if match else str(src).lower()
        )
    return min(1.0, len(unique_domains) / max(1, len(sources)))


class UncertaintyEngine:
    """Live uncertainty evaluator using entropy and claim heuristics."""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def evaluate(self, content: str, context: dict | None = None) -> dict[str, Any]:
        ctx = context or {}
        text = str(content or "")
        sources = ctx.get("sources", [])
        prior_confidence = ctx.get("prior_confidence", 0.5)

        entropy = _shannon_entropy(text)
        claims = _claim_density(text)
        diversity = _source_diversity(sources)

        uncertainty = (
            0.4 * entropy
            + 0.3 * (1.0 - diversity)
            + 0.2 * min(1.0, claims)
            + 0.1 * (1.0 - prior_confidence)
        )
        uncertainty = round(max(0.0, min(1.0, uncertainty)), 4)
        confidence = round(max(0.0, min(1.0, 1.0 - uncertainty)), 4)

        result = {
            "uncertainty": uncertainty,
            "confidence": confidence,
            "entropy": round(entropy, 4),
            "claim_density": round(claims, 4),
            "source_diversity": round(diversity, 4),
        }
        self._history.append(result)
        return result

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)


def calculate_uncertainty(evidence: Any) -> float:
    """Calculate scalar uncertainty from evidence string or dict."""
    if isinstance(evidence, dict):
        return UncertaintyEngine().evaluate(
            content=evidence.get("content", ""),
            context=evidence,
        )["uncertainty"]
    return UncertaintyEngine().evaluate(content=str(evidence or ""))["uncertainty"]


__all__ = ["UncertaintyEngine", "calculate_uncertainty"]
