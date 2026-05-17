"""
core/uncertainty_engine.py — Real-time uncertainty quantification engine.

Computes lexical entropy, claim density, and calibrated confidence
from evidence and text rather than returning static zeros.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from typing import Any


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
        unique_domains.add(match.group(1).lower() if match else str(src).lower())
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


def calculate_uncertainty(
    evidence: Any = None,
    *,
    evidence_count: int | None = None,
    evidence_relevance: float | None = None,
    reasoning_consistency: float | None = None,
    knowledge_gaps: Sequence[str] | None = None,
    model_logits_confidence: float | None = None,
) -> dict[str, float]:
    """Calculate auditable uncertainty metrics for legacy and structured callers."""
    if any(
        value is not None
        for value in (
            evidence_count,
            evidence_relevance,
            reasoning_consistency,
            knowledge_gaps,
            model_logits_confidence,
        )
    ):
        count = max(0, evidence_count or 0)
        relevance = max(
            0.0, min(1.0, evidence_relevance if evidence_relevance is not None else 0.5)
        )
        consistency = max(
            0.0,
            min(1.0, reasoning_consistency if reasoning_consistency is not None else 0.5),
        )
        gaps = len(knowledge_gaps or [])
        logits = max(
            0.0,
            min(
                1.0,
                model_logits_confidence if model_logits_confidence is not None else 0.5,
            ),
        )
        safety_omega = round(
            max(
                0.0,
                min(
                    1.0,
                    0.55 * (1.0 - relevance)
                    + 0.25 * (1.0 - consistency)
                    + 0.10 * (1.0 - logits)
                    + 0.10 * min(1.0, gaps / max(1, count + 1)),
                ),
            ),
            4,
        )
        return {
            "uncertainty": safety_omega,
            "safety_omega": safety_omega,
            "confidence": round(1.0 - safety_omega, 4),
            "entropy": round(max(0.0, min(1.0, gaps / max(1, count + 1))), 4),
            "claim_density": round(relevance, 4),
            "source_diversity": round(min(1.0, count / 3 if count else 0.0), 4),
        }

    if isinstance(evidence, dict):
        result = UncertaintyEngine().evaluate(
            content=evidence.get("content", ""),
            context=evidence,
        )
    else:
        result = UncertaintyEngine().evaluate(content=str(evidence or ""))
    return {
        **result,
        "safety_omega": result["uncertainty"],
    }


__all__ = ["UncertaintyEngine", "calculate_uncertainty"]
