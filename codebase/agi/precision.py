"""
PRECISION PHYSICS (v53) - Critical Gap 1 Fix

Implements precision weighting (π = 1/σ²) for optimal belief updating.
Replaces homogeneous confidence with heterogeneous precision.

Formula: F = ΔS + Ω₀·π⁻¹  (not just F = ΔS + Ω₀)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone


@dataclass
class PrecisionEstimate:
    """
    Precision π = 1/σ² (inverse variance)
    Higher precision = more trustworthy evidence
    """
    pi_likelihood: float  # π_L: Data reliability (source variance)
    pi_prior: float       # π_P: Model confidence
    kalman_gain: float    # weight = π_L / (π_P + π_L)
    
    def __post_init__(self):
        # Ensure non-zero to avoid division by zero
        self.pi_likelihood = max(self.pi_likelihood, 0.01)
        self.pi_prior = max(self.pi_prior, 0.01)


class PrecisionWeighter:
    """
    Kalman-style precision weighting for belief updates.
    
    Key insight: Not all evidence is equal.
    - High precision (low variance): Trust more
    - Low precision (high variance): Trust less
    """
    
    @staticmethod
    def estimate_source_variance(sources: List[str]) -> float:
        """
        Compute variance from source agreement.
        
        Multiple agreeing sources → low variance → high precision
        Conflicting sources → high variance → low precision
        """
        if not sources:
            return 1.0  # Maximum uncertainty
        
        # Unique sources
        unique = len(set(sources))
        total = len(sources)
        
        # Agreement ratio
        agreement = unique / total
        
        # Variance decreases with agreement
        return agreement * 0.5 + 0.1  # Range: 0.1 - 0.6
    
    @staticmethod
    def estimate_temporal_variance(timestamps: List[datetime]) -> float:
        """
        Compute variance from temporal consistency.
        
        Recent + consistent timestamps → low variance
        Stale or scattered timestamps → high variance
        """
        if not timestamps or len(timestamps) < 2:
            return 0.3  # Moderate uncertainty
        
        now = datetime.now(timezone.utc)
        ages = [(now - ts).total_seconds() for ts in timestamps]
        
        # Mean age
        mean_age = sum(ages) / len(ages)
        
        # Variance in ages
        variance_ages = sum((a - mean_age) ** 2 for a in ages) / len(ages)
        
        # Normalize: older and more scattered = higher variance
        return min(1.0, (mean_age / 3600 + variance_ages / 1000) / 10)
    
    @staticmethod
    def estimate_semantic_variance(embeddings: List[List[float]]) -> float:
        """
        Compute variance from semantic coherence.
        
        Similar embeddings (cosine similarity) → low variance
        Dissimilar embeddings → high variance
        """
        if not embeddings or len(embeddings) < 2:
            return 0.3
        
        # Compute pairwise cosine similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = cosine_similarity(embeddings[i], embeddings[j])
                similarities.append(sim)
        
        if not similarities:
            return 0.3
        
        # Variance = 1 - mean similarity
        mean_sim = sum(similarities) / len(similarities)
        return 1.0 - mean_sim
    
    def estimate_precision(
        self,
        sources: List[str],
        timestamps: List[datetime],
        embeddings: Optional[List[List[float]]] = None
    ) -> PrecisionEstimate:
        """
        Full precision estimation from evidence metadata.
        """
        # Component variances
        var_source = self.estimate_source_variance(sources)
        var_temporal = self.estimate_temporal_variance(timestamps)
        var_semantic = self.estimate_semantic_variance(embeddings) if embeddings else 0.3

        # Total variance (sum of independent variances)
        var_total = var_source + var_temporal + var_semantic

        # Precision = inverse variance (pi = 1/sigma^2)
        pi_L = 1.0 / (var_total + 0.01)  # epsilon regularization

        # Default prior precision (can be updated from hypothesis)
        pi_P = 1.0  # Neutral prior

        # Kalman gain
        K = pi_L / (pi_P + pi_L)

        return PrecisionEstimate(
            pi_likelihood=pi_L,
            pi_prior=pi_P,
            kalman_gain=K
        )
    
    def update_belief(
        self,
        current_confidence: float,
        evidence_confidence: float,
        precision: PrecisionEstimate
    ) -> float:
        """
        Kalman-style belief update with precision weighting.
        
        new_belief = old_belief + K × (observation - old_belief)
        """
        K = precision.kalman_gain
        
        # Prediction error
        error = evidence_confidence - current_confidence
        
        # Weighted update
        new_confidence = current_confidence + K * error
        
        # Clamp to valid range
        return max(0.0, min(1.0, new_confidence))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot / (norm_a * norm_b)


# Global precision weighter
_precision_weighter = PrecisionWeighter()


def estimate_precision(
    sources: List[str],
    timestamps: List[datetime],
    embeddings: Optional[List[List[float]]] = None
) -> PrecisionEstimate:
    """Convenience function for precision estimation."""
    return _precision_weighter.estimate_precision(sources, timestamps, embeddings)


def update_belief_with_precision(
    current_confidence: float,
    evidence_confidence: float,
    precision: PrecisionEstimate
) -> float:
    """Convenience function for precision-weighted belief update."""
    return _precision_weighter.update_belief(
        current_confidence, evidence_confidence, precision
    )


__all__ = [
    "PrecisionEstimate",
    "PrecisionWeighter",
    "estimate_precision",
    "update_belief_with_precision",
    "cosine_similarity"
]
