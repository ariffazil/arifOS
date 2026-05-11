"""
Contrast Space — Unified Representation of All Contrast Types
DITEMPA BUKAN DIBERI

Implements a unified mathematical space where all contrast features
(physical, display, perceptual) can be represented and compared.

This enables detection of anomalous contrast through geometric
operations in contrast space.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..THEORY import ContrastTaxonomy, ContrastVerdict, assess_conflation_risk


@dataclass
class ContrastFeature:
    """
    A feature in Contrast Space.

    Every feature has:
      - coordinates: Position in contrast space (physical, display, perceptual dims)
      - taxonomy: Complete source→transform→proxy→confidence chain
      - uncertainty: Error ellipsoid in contrast space
    """

    feature_id: str
    feature_type: str  # "fault", "horizon", "edge", "blob", etc.

    # Coordinates in 3D contrast space
    # [physical_contrast, display_contrast, perceptual_contrast]
    coordinates: np.ndarray  # Shape: (3,)

    # Full taxonomy
    taxonomy: ContrastTaxonomy

    # Uncertainty (covariance matrix in contrast space)
    uncertainty: np.ndarray = field(default_factory=lambda: np.eye(3) * 0.1)

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.coordinates.shape != (3,):
            raise ValueError("coordinates must be 3D vector [physical, display, perceptual]")
        if self.uncertainty.shape != (3, 3):
            raise ValueError("uncertainty must be 3x3 covariance matrix")

    @property
    def physical_component(self) -> float:
        """Physical contrast magnitude (0-1)."""
        return float(self.coordinates[0])

    @property
    def display_component(self) -> float:
        """Display contrast magnitude (0-1)."""
        return float(self.coordinates[1])

    @property
    def perceptual_component(self) -> float:
        """Perceptual contrast magnitude (0-1)."""
        return float(self.coordinates[2])

    @property
    def anomalous_score(self) -> float:
        """
        Anomalous contrast score: high when display dominates physical.

        Score = display_component / (physical_component + epsilon)
        """
        epsilon = 0.01
        return self.display_component / (self.physical_component + epsilon)

    @property
    def is_anomalous(self) -> bool:
        """True if this feature likely represents anomalous contrast."""
        # Anomalous if display >> physical AND perceptual is high
        return (
            self.display_component > 0.5
            and self.display_component > 2 * self.physical_component
            and self.perceptual_component > 0.3
        )

    def distance_to(self, other: ContrastFeature) -> float:
        """Mahalanobis distance to another feature in contrast space."""
        diff = self.coordinates - other.coordinates
        # Simplified: use Euclidean for now
        return float(np.sqrt(np.sum(diff**2)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "feature_id": self.feature_id,
            "feature_type": self.feature_type,
            "coordinates": self.coordinates.tolist(),
            "physical": self.physical_component,
            "display": self.display_component,
            "perceptual": self.perceptual_component,
            "anomalous_score": self.anomalous_score,
            "is_anomalous": self.is_anomalous,
            "taxonomy": self.taxonomy.to_dict(),
        }


class ContrastSpace:
    """
    A space of contrast features with operations for governance.

    The ContrastSpace maintains a population of ContrastFeatures and
    provides operations to:
      - Detect anomalous features (display >> physical)
      - Cluster features by similarity
      - Validate features against governance policies
    """

    def __init__(self, domain: str = "generic"):
        self.domain = domain
        self.features: dict[str, ContrastFeature] = {}
        self._verdict_cache: dict[str, tuple[ContrastVerdict, dict]] = {}

    def add_feature(self, feature: ContrastFeature) -> None:
        """Add a feature to the contrast space."""
        self.features[feature.feature_id] = feature
        # Clear cache for this feature
        self._verdict_cache.pop(feature.feature_id, None)

    def get_feature(self, feature_id: str) -> ContrastFeature | None:
        """Retrieve a feature by ID."""
        return self.features.get(feature_id)

    def assess_feature(self, feature_id: str) -> dict[str, Any]:
        """
        Full governance assessment of a feature.

        Returns assessment including verdict, risk, and recommendations.
        """
        feature = self.features.get(feature_id)
        if not feature:
            raise ValueError(f"Feature {feature_id} not found in contrast space")

        # Check cache
        if feature_id in self._verdict_cache:
            verdict, metadata = self._verdict_cache[feature_id]
        else:
            # Run full assessment
            verdict, triggers, metadata = assess_conflation_risk(feature.taxonomy, self.domain)
            self._verdict_cache[feature_id] = (verdict, metadata)

        return {
            "feature_id": feature_id,
            "feature_type": feature.feature_type,
            "coordinates": feature.coordinates.tolist(),
            "anomalous_score": feature.anomalous_score,
            "is_anomalous": feature.is_anomalous,
            "verdict": verdict.to_geox_verdict(),
            "triggers": [t.to_dict() for t in metadata.get("triggers", [])],
            "taxonomy": feature.taxonomy.to_dict(),
        }

    def find_anomalous(self, threshold: float = 2.0) -> list[ContrastFeature]:
        """
        Find all features with anomalous contrast ratio above threshold.

        Threshold of 2.0 means display_component > 2 * physical_component.
        """
        return [f for f in self.features.values() if f.anomalous_score > threshold]

    def get_population_stats(self) -> dict[str, Any]:
        """Statistics about the feature population."""
        if not self.features:
            return {"count": 0}

        coords = np.array([f.coordinates for f in self.features.values()])

        return {
            "count": len(self.features),
            "physical_mean": float(coords[:, 0].mean()),
            "display_mean": float(coords[:, 1].mean()),
            "perceptual_mean": float(coords[:, 2].mean()),
            "anomalous_count": len(self.find_anomalous()),
            "anomalous_ratio": len(self.find_anomalous()) / len(self.features),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize entire contrast space."""
        return {
            "domain": self.domain,
            "feature_count": len(self.features),
            "features": {fid: f.to_dict() for fid, f in self.features.items()},
            "population_stats": self.get_population_stats(),
        }
