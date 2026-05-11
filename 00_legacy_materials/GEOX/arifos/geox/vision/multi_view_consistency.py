"""
MultiViewConsistencyChecker — Cross-View Feature Validation
DITEMPA BUKAN DIBERI

Detects display artifacts by checking feature consistency across contrast views.
"""

from dataclasses import dataclass


@dataclass
class FeatureSignature:
    """Signature for a detected feature."""

    feature_type: str
    location: tuple[int, int] | None
    description_hash: str


class MultiViewConsistencyChecker:
    """
    Check consistency of features across contrast views.

    Theory: Real geological features persist across contrast variations.
    Display artifacts appear/disappear with aggressive enhancement.
    """

    def check_consistency(
        self,
        view_features: list[list[dict]],
        tolerance: float = 0.1,
    ) -> float:
        """
        Calculate cross-view consistency score.

        Args:
            view_features: List of feature lists, one per view
            tolerance: Location tolerance for feature matching

        Returns:
            Consistency score [0.0, 1.0]
        """
        if not view_features or len(view_features) < 2:
            return 0.0

        # Count feature occurrences
        n_views = len(view_features)
        feature_votes: dict[str, int] = {}

        for view in view_features:
            for feature in view:
                sig = self._signature(feature)
                feature_votes[sig] = feature_votes.get(sig, 0) + 1

        if not feature_votes:
            return 0.0

        # Calculate consistency
        scores = []
        for sig, votes in feature_votes.items():
            persistence = votes / n_views
            scores.append(persistence)

        return sum(scores) / len(scores)

    def identify_artifacts(
        self,
        view_features: list[list[dict]],
        threshold: float = 0.5,
    ) -> list[dict]:
        """
        Identify features that are likely display artifacts.

        Features appearing in fewer views than threshold = artifacts.
        """
        if not view_features:
            return []

        n_views = len(view_features)
        artifacts = []

        # Count occurrences
        all_features: dict[str, list] = {}
        for view in view_features:
            for feature in view:
                sig = self._signature(feature)
                if sig not in all_features:
                    all_features[sig] = []
                all_features[sig].append(feature)

        # Identify low-persistence features
        for sig, occurrences in all_features.items():
            persistence = len(occurrences) / n_views
            if persistence < threshold:
                artifacts.append(
                    {
                        "feature": occurrences[0],
                        "persistence": persistence,
                        "votes": len(occurrences),
                        "total_views": n_views,
                    }
                )

        return artifacts

    def _signature(self, feature: dict) -> str:
        """Generate feature signature for comparison."""
        ftype = feature.get("type", "unknown")
        desc = feature.get("description", "")[:30]
        return f"{ftype}:{desc}"
