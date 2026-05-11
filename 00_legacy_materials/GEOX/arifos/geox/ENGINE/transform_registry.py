"""
Transform Registry — Catalog of Visual Transforms with Risk Metadata
DITEMPA BUKAN DIBERI

Maintains a registry of all known visual transforms with their
conflation risk profiles. Used for:

  - Automatic risk assessment during transform selection
  - Matching transforms to data types
  - Warning about high-risk transform chains
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransformProfile:
    """
    Risk profile for a visual transform.

    Every visual transform (colormap, gain, filter, etc.) has:
      - amplification_factor: How much it can increase display contrast
      - distortion_type: What kind of artifacts it can introduce
      - risk_level: LOW, MEDIUM, HIGH based on amplification and distortion
    """

    transform_name: str
    transform_type: str  # "colormap", "gain", "filter", "composite"

    # Risk metrics
    amplification_factor: float = 1.0  # 1.0 = neutral, 10.0 = extreme
    distortion_potential: float = 0.0  # 0.0 = none, 1.0 = severe

    # Description of artifacts
    distortion_type: str = "none"

    # Domain applicability
    applicable_domains: tuple[str, ...] = ()  # "seismic", "medical", "satellite", etc.

    @property
    def risk_level(self) -> str:
        """Categorize risk based on amplification and distortion."""
        score = self.amplification_factor * (1 + self.distortion_potential)
        if score < 1.5:
            return "LOW"
        elif score < 3.0:
            return "MEDIUM"
        else:
            return "HIGH"

    def to_dict(self) -> dict:
        return {
            "name": self.transform_name,
            "type": self.transform_type,
            "amplification": self.amplification_factor,
            "distortion": self.distortion_potential,
            "risk_level": self.risk_level,
        }


class TransformRegistry:
    """
    Registry of visual transforms with their risk profiles.

    Provides lookup and chain risk analysis.
    """

    # Built-in transform profiles
    _BUILTIN_PROFILES: list[TransformProfile] = [
        # Seismic-specific transforms
        TransformProfile(
            "seismic_wiggle",
            "display",
            amplification_factor=1.0,
            distortion_potential=0.0,
            applicable_domains=("seismic",),
        ),
        TransformProfile(
            "seismic_variable_density",
            "colormap",
            amplification_factor=2.0,
            distortion_potential=0.3,
            distortion_type="color_gradient_exaggeration",
            applicable_domains=("seismic",),
        ),
        TransformProfile(
            "seismic_seisview",
            "display",
            amplification_factor=1.5,
            distortion_potential=0.2,
            applicable_domains=("seismic",),
        ),
        TransformProfile(
            "agc_fast",
            "gain",
            amplification_factor=3.0,
            distortion_potential=0.4,
            distortion_type="stratigraphic_leveling",
            applicable_domains=("seismic",),
        ),
        TransformProfile(
            "agc_slow",
            "gain",
            amplification_factor=2.0,
            distortion_potential=0.3,
            applicable_domains=("seismic",),
        ),
        # Generic transforms (all domains)
        TransformProfile(
            "grayscale",
            "colormap",
            amplification_factor=1.0,
            distortion_potential=0.0,
            applicable_domains=("seismic", "medical", "satellite", "generic"),
        ),
        TransformProfile(
            "jet_colormap",
            "colormap",
            amplification_factor=2.5,
            distortion_potential=0.4,
            distortion_type="perceptual_band_edge",
            applicable_domains=("seismic", "medical", "satellite", "generic"),
        ),
        TransformProfile(
            "viridis",
            "colormap",
            amplification_factor=1.2,
            distortion_potential=0.1,
            applicable_domains=("seismic", "medical", "satellite", "generic"),
        ),
        TransformProfile(
            "histogram_equalization",
            "enhancement",
            amplification_factor=2.0,
            distortion_potential=0.3,
            distortion_type="nonlinear_mapping",
            applicable_domains=("seismic", "medical", "satellite", "generic"),
        ),
        TransformProfile(
            "gaussian_blur",
            "filter",
            amplification_factor=0.8,
            distortion_potential=0.2,
            distortion_type="edge_smoothing",
            applicable_domains=("seismic", "medical", "satellite", "generic"),
        ),
        TransformProfile(
            "sharpen",
            "filter",
            amplification_factor=1.8,
            distortion_potential=0.3,
            distortion_type="edge_enhancement",
            applicable_domains=("seismic", "medical", "satellite", "generic"),
        ),
        # High-risk transforms
        TransformProfile(
            "autogain_extreme",
            "gain",
            amplification_factor=10.0,
            distortion_potential=0.8,
            distortion_type="dynamic_range_compression",
            applicable_domains=("seismic", "medical", "satellite"),
        ),
        TransformProfile(
            "ai_upscale",
            "ml_inference",
            amplification_factor=5.0,
            distortion_potential=0.6,
            distortion_type="hallucinated_texture",
            applicable_domains=("seismic", "satellite", "generic"),
        ),
    ]

    def __init__(self):
        self._profiles: dict[str, TransformProfile] = {}
        self._register_builtin()

    def _register_builtin(self) -> None:
        """Register all built-in profiles."""
        for profile in self._BUILTIN_PROFILES:
            self.register(profile)

    def register(self, profile: TransformProfile) -> None:
        """Register a new transform profile."""
        self._profiles[profile.transform_name] = profile

    def get(self, transform_name: str) -> TransformProfile | None:
        """Get profile by name."""
        return self._profiles.get(transform_name)

    def find_for_domain(self, domain: str) -> list[TransformProfile]:
        """Find all transforms applicable to a domain."""
        return [
            p
            for p in self._profiles.values()
            if domain in p.applicable_domains or "generic" in p.applicable_domains
        ]

    def analyze_chain(self, chain: list[str]) -> dict:
        """
        Analyze a chain of transforms for cumulative risk.

        Returns:
          - total_amplification: Product of all amplification factors
          - max_single_amplification: Highest single transform amplification
          - risk_level: LOW/MEDIUM/HIGH based on cumulative risk
          - warnings: List of specific concerns
        """
        profiles = [self.get(t) for t in chain]

        # Handle unknown transforms
        unknown = [t for t, p in zip(chain, profiles) if p is None]
        if unknown:
            return {
                "error": f"Unknown transforms: {unknown}",
                "risk_level": "UNKNOWN",
            }

        profiles = [p for p in profiles if p is not None]

        # Calculate cumulative metrics
        total_amp = 1.0
        max_single = 1.0
        warnings_list = []

        for profile in profiles:
            total_amp *= profile.amplification_factor
            max_single = max(max_single, profile.amplification_factor)

            if profile.amplification_factor > 3.0:
                warnings_list.append(
                    f"{profile.transform_name}: high amplification ({profile.amplification_factor:.1f}x)"
                )

            if profile.distortion_potential > 0.5:
                warnings_list.append(
                    f"{profile.transform_name}: severe distortion potential"
                )

        # Determine overall risk
        if total_amp > 10.0 or max_single > 5.0:
            risk = "HIGH"
        elif total_amp > 3.0 or max_single > 2.5:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "chain": chain,
            "total_amplification": round(total_amp, 2),
            "max_single_amplification": round(max_single, 2),
            "risk_level": risk,
            "warnings": warnings_list,
            "profiles": [p.to_dict() for p in profiles],
        }


# Global registry instance
_global_registry: TransformRegistry | None = None


def get_registry() -> TransformRegistry:
    """Get the global transform registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = TransformRegistry()
    return _global_registry
