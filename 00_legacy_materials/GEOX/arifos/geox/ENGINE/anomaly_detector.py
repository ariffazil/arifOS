"""
Anomaly Detector — Automatic Detection of Conflation Errors
DITEMPA BUKAN DIBERI

The AnomalyDetector identifies when features in ContrastSpace likely
represent visual artifacts rather than physical signal. It uses the
Theory of Anomalous Contrast to flag suspicious features.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class ConflationAlert:
    """
    Alert for a detected conflation anomaly.

    A conflation alert includes:
      - The type of anomaly detected
      - Confidence in the detection
      - Recommended action
      - Explanation for human review
    """

    alert_id: str
    feature_id: str

    # Detection metadata
    alert_type: str  # "anomalous_contrast", "circular_reference", "unknown_transform"
    confidence: float  # 0-1 confidence in this alert

    # The anomaly score that triggered this alert
    anomalous_score: float
    threshold: float

    # Recommendation
    recommendation: str

    # Human-readable explanation
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "feature_id": self.feature_id,
            "alert_type": self.alert_type,
            "confidence": round(self.confidence, 3),
            "anomalous_score": round(self.anomalous_score, 3),
            "threshold": self.threshold,
            "recommendation": self.recommendation,
            "explanation": self.explanation,
        }


class AnomalyDetector:
    """
    Detects conflation anomalies in ContrastSpace.

    Uses multiple detection strategies:
      1. Anomalous contrast ratio (display >> physical)
      2. Circular references in transform chains
      3. Unknown transform types
      4. Population-level statistics
    """

    # Default thresholds
    DEFAULT_ANOMALY_THRESHOLD = 2.0  # display > 2x physical
    DEFAULT_CONFIDENCE_THRESHOLD = 0.7

    def __init__(
        self,
        anomaly_threshold: float = DEFAULT_ANOMALY_THRESHOLD,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ):
        self.anomaly_threshold = anomaly_threshold
        self.confidence_threshold = confidence_threshold
        self._alert_counter = 0

    def _next_alert_id(self) -> str:
        """Generate sequential alert IDs."""
        self._alert_counter += 1
        return f"GEOX-ALT-{self._alert_counter:04d}"

    def check_anomalous_contrast(
        self,
        feature_id: str,
        physical_component: float,
        display_component: float,
        perceptual_component: float | None = None,
    ) -> ConflationAlert | None:
        """
        Check if a feature exhibits anomalous contrast.

        Returns ConflationAlert if anomalous, None otherwise.
        """
        # Calculate anomalous score
        epsilon = 0.01
        score = display_component / (physical_component + epsilon)

        if score <= self.anomaly_threshold:
            return None

        # Calculate confidence based on how far above threshold
        # and how high perceptual component is
        confidence = min(0.5 + (score - self.anomaly_threshold) * 0.2, 0.95)
        if perceptual_component is not None:
            confidence = min(confidence + perceptual_component * 0.1, 0.95)

        # Determine recommendation
        if score > 5.0:
            recommendation = (
                "REJECT — Feature likely represents display artifact, not physical signal"
            )
        elif score > 3.0:
            recommendation = (
                "REVIEW REQUIRED — High anomalous contrast. Verify against raw data before use"
            )
        else:
            recommendation = "FLAG — Moderate anomaly. Document transform chain for audit"

        # Build explanation
        explanation = (
            f"Display contrast ({display_component:.2f}) is {score:.1f}x higher than "
            f"physical signal ({physical_component:.2f}). This indicates the feature "
            f"may be an artifact of visualization (colormap, gain, filtering) rather "
            f"than a true subsurface structure. "
        )

        if perceptual_component and perceptual_component > 0.5:
            explanation += (
                f"Additionally, perceptual contrast is high ({perceptual_component:.2f}), "
                f"suggesting the display is designed to attract human attention, "
                f"which increases risk of misinterpretation."
            )

        return ConflationAlert(
            alert_id=self._next_alert_id(),
            feature_id=feature_id,
            alert_type="anomalous_contrast",
            confidence=confidence,
            anomalous_score=score,
            threshold=self.anomaly_threshold,
            recommendation=recommendation,
            explanation=explanation,
        )

    def check_circular_reference(
        self,
        feature_id: str,
        transform_chain: list[str],
    ) -> ConflationAlert | None:
        """
        Check if a transform chain contains circular references.

        A circular reference is when the same transform type appears
        multiple times in ways that create feedback loops.
        """
        # Simple check: same transform appears multiple times
        seen = set()
        duplicates = []
        for t in transform_chain:
            if t in seen:
                duplicates.append(t)
            seen.add(t)

        if not duplicates:
            return None

        return ConflationAlert(
            alert_id=self._next_alert_id(),
            feature_id=feature_id,
            alert_type="circular_reference",
            confidence=0.9,
            anomalous_score=float(len(duplicates)),
            threshold=1.0,
            recommendation="REVIEW — Duplicate transforms in chain may indicate processing error",
            explanation=f"Transform(s) {duplicates} appear multiple times in chain: {transform_chain}. "
            "This may create feedback loops that amplify artifacts.",
        )

    def check_population_anomaly(
        self,
        feature_ids: list[str],
        anomalous_scores: list[float],
    ) -> ConflationAlert | None:
        """
        Check if a population of features has unusual anomalous score distribution.

        This detects systematic issues in processing pipelines.
        """
        if len(anomalous_scores) < 10:
            return None  # Not enough data

        scores = np.array(anomalous_scores)
        mean_score = np.mean(scores)
        std_score = np.std(scores)

        # Flag if mean anomalous score is high
        if mean_score < self.anomaly_threshold:
            return None

        return ConflationAlert(
            alert_id=self._next_alert_id(),
            feature_id=f"POPULATION:{len(feature_ids)}_features",
            alert_type="population_bias",
            confidence=min(mean_score / 5.0, 0.9),
            anomalous_score=float(mean_score),
            threshold=self.anomaly_threshold,
            recommendation="SYSTEM REVIEW — Population shows systematic high anomalous scores. Review processing pipeline",
            explanation=f"Population of {len(feature_ids)} features has mean anomalous score of {mean_score:.2f} "
            f"(±{std_score:.2f}). This suggests the processing pipeline may systematically "
            f"amplify display contrast beyond physical signal.",
        )

    def generate_summary(
        self,
        alerts: list[ConflationAlert],
    ) -> dict[str, Any]:
        """Generate summary statistics for a collection of alerts."""
        if not alerts:
            return {
                "alert_count": 0,
                "overall_verdict": "SEAL",
                "risk_level": "LOW",
            }

        by_type: dict[str, int] = {}
        high_confidence = 0
        max_score = 0.0

        for alert in alerts:
            by_type[alert.alert_type] = by_type.get(alert.alert_type, 0) + 1
            if alert.confidence > self.confidence_threshold:
                high_confidence += 1
            max_score = max(max_score, alert.anomalous_score)

        # Determine overall verdict
        if high_confidence > len(alerts) * 0.5:
            verdict = "VOID"
            risk = "CRITICAL"
        elif max_score > 5.0:
            verdict = "HOLD"
            risk = "HIGH"
        elif high_confidence > 0:
            verdict = "REVIEW"
            risk = "MEDIUM"
        else:
            verdict = "PARTIAL"
            risk = "LOW"

        return {
            "alert_count": len(alerts),
            "high_confidence_alerts": high_confidence,
            "by_type": by_type,
            "max_anomalous_score": round(max_score, 2),
            "overall_verdict": verdict,
            "risk_level": risk,
            "alerts": [a.to_dict() for a in alerts],
        }
