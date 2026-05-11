"""
Contrast Taxonomy — Source → Transform → Proxy → Confidence
DITEMPA BUKAN DIBERI

Universal classification system for contrast in any interpretation domain.

Every contrast feature can be traced through:
  SOURCE: Where did the signal originate?
  TRANSFORM: What display operations were applied?
  PROXY: What visual feature is being used as evidence?
  CONFIDENCE: How certain are we of the physical→visual mapping?
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Literal


class SourceDomain(Enum):
    """
    The origin domain of a contrast signal.

    This is the FIRST question in ToAC: Where did this come from?
    """

    EARTH = auto()  # Seismic: actual rock properties
    SENSOR = auto()  # Raw instrument measurement
    SIMULATION = auto()  # Modeled/predicted data
    SYNTHETIC = auto()  # Artificial test data
    UNKNOWN = auto()  # Provenance unclear

    def is_physical(self) -> bool:
        """True if source is physical reality (not simulated/unknown)."""
        return self in (SourceDomain.EARTH, SourceDomain.SENSOR)


class ClaimTag(Enum):
    """
    Non-negotiable claim classification for all GEOX assertions.

    Ensures that every claim made by the system is explicitly categorized
    by its epistemic status.

    CLAIMS: Fact-based, verified against physical models (F2 Truth).
    PLAUSIBLE: Follows logical trends but lacks high-res calibration.
    HYPOTHESIS: Speculative, based on visual similarity (High Conflation Risk).
    UNKNOWN: Data gap or model failure.
    """

    CLAIM = auto()
    PLAUSIBLE = auto()
    HYPOTHESIS = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class VisualTransform:
    """
    A display/visualization operation applied to data.

    Every transform carries an anomalous risk — the possibility that
    it creates features not present in the physical source.
    """

    name: str
    category: Literal[
        "colormap",  # Color scale changes
        "intensity",  # Brightness/contrast adjustments
        "filter",  # Convolution, smoothing, sharpening
        "edge_detect",  # Sobel, Canny, etc.
        "histogram",  # Histogram equalization, CLAHE
        "geometric",  # Resizing, warping
    ]
    parameters: dict[str, Any] = field(default_factory=dict)

    # Risk that this transform creates artifacts
    artifact_risk: Literal["low", "medium", "high", "critical"] = "medium"

    # Physical quantities this transform can obscure or create
    affects_quantities: list[str] = field(default_factory=list)

    @property
    def risk_score(self) -> float:
        """Numeric risk score (0.0 - 1.0)."""
        scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        return scores.get(self.artifact_risk, 0.5)


# Standard transforms catalog
TRANSFORM_CATALOG = {
    "grayscale": VisualTransform("grayscale", "colormap", artifact_risk="low"),
    "inverted": VisualTransform("inverted", "colormap", artifact_risk="low"),
    "seismic_colormap": VisualTransform(
        "seismic_colormap", "colormap", artifact_risk="medium"
    ),
    "rainbow": VisualTransform(
        "rainbow", "colormap", artifact_risk="high"
    ),  # Perceptually non-uniform
    "linear_stretch": VisualTransform(
        "linear_stretch", "intensity", artifact_risk="low"
    ),
    "gamma_0.8": VisualTransform("gamma_0.8", "intensity", {"gamma": 0.8}, "medium"),
    "gamma_1.2": VisualTransform("gamma_1.2", "intensity", {"gamma": 1.2}, "medium"),
    "gaussian_smooth": VisualTransform(
        "gaussian_smooth", "filter", {"kernel": "gaussian"}, "low"
    ),
    "sharpen": VisualTransform("sharpen", "filter", artifact_risk="high"),
    "median_filter": VisualTransform("median_filter", "filter", artifact_risk="low"),
    "sobel": VisualTransform(
        "sobel",
        "edge_detect",
        artifact_risk="high",
        affects_quantities=["discontinuity", "gradient"],
    ),
    "canny": VisualTransform(
        "canny",
        "edge_detect",
        artifact_risk="high",
        affects_quantities=["edge", "boundary"],
    ),
    "histogram_eq": VisualTransform(
        "histogram_eq", "histogram", artifact_risk="medium"
    ),
    "CLAHE": VisualTransform(
        "CLAHE",
        "histogram",
        {"adaptive": True},
        "critical",
        affects_quantities=["local_contrast", "texture"],
    ),
    "resize": VisualTransform("resize", "geometric", artifact_risk="medium"),
    "reproject": VisualTransform("reproject", "geometric", artifact_risk="high"),
}


@dataclass(frozen=True)
class PhysicalProxy:
    """
    A visual feature used as stand-in (proxy) for a physical quantity.

    The SECOND question in ToAC: What visual feature is being interpreted?

    Examples:
      - A dark line in seismic (visual) → fault (physical)
      - A bright spot in MRI (visual) → tumor (physical)
      - A color change in satellite (visual) → mineral deposit (physical)
    """

    visual_feature: str
    claimed_physical_quantity: str
    proxy_validity: Literal["direct", "indirect", "speculative", "unverified"]

    # How reliably does the visual feature indicate the physical quantity?
    reliability: float  # 0.0 - 1.0

    # Alternative physical quantities that could produce same visual feature
    alternative_interpretations: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not (0.0 <= self.reliability <= 1.0):
            raise ValueError("reliability must be in [0, 1]")

    @property
    def is_high_risk(self) -> bool:
        """True if proxy validity is speculative or unverified."""
        return self.proxy_validity in ("speculative", "unverified")

    @property
    def requires_confirmation(self) -> bool:
        """True if alternative interpretations exist."""
        return len(self.alternative_interpretations) > 0


@dataclass
class ConfidenceClass:
    """
    F7 Humility: Confidence classification with constitutional bounds.

    Confidence must be in [0.03, 0.15] unless explicitly overridden.
    This prevents both overconfidence and false humility.
    """

    # Core confidence value (F7 constitutional band)
    value: float  # 0.03 - 0.15 for normal operations

    # Classification of what this confidence refers to
    confidence_type: Literal[
        "detection",  # "Something is here"
        "classification",  # "This is a fault"
        "measurement",  # "Dip is 45 degrees"
        "prediction",  # "This trend continues"
    ]

    # Justification for confidence level
    justification: str

    # Whether this is outside normal F7 band
    f7_override: bool = False
    override_reason: str = ""

    def __post_init__(self):
        if not self.f7_override:
            if not (0.03 <= self.value <= 0.15):
                raise ValueError(
                    f"Confidence {self.value} outside F7 band [0.03, 0.15]. "
                    f"Set f7_override=True with justification if necessary."
                )

    @property
    def is_constitutional(self) -> bool:
        """True if confidence is within F7 humility band."""
        return 0.03 <= self.value <= 0.15

    @property
    def confidence_label(self) -> str:
        """Human-readable confidence label."""
        if self.value < 0.05:
            return "very_low"
        elif self.value < 0.08:
            return "low"
        elif self.value < 0.12:
            return "moderate"
        else:
            return "elevated"


@dataclass
class ContrastTaxonomy:
    """
    Complete taxonomy for a contrast feature.

    Every feature in GEOX must have a full taxonomy:
      SOURCE → TRANSFORM → PROXY → CONFIDENCE

    This creates the audit trail needed to detect anomalous contrast.
    """

    # Source: Where did the signal originate?
    source: SourceDomain
    source_details: dict[str, Any] = field(default_factory=dict)

    # Transform chain: What display operations were applied?
    transforms: list[VisualTransform] = field(default_factory=list)

    # Proxy: What visual feature is being interpreted?
    proxy: PhysicalProxy | None = None

    # Confidence: How certain is the interpretation?
    confidence: ConfidenceClass | None = None

    # Domain context
    domain: Literal["seismic", "medical", "satellite", "generic"] = "generic"

    def add_transform(self, transform: VisualTransform) -> ContrastTaxonomy:
        """Add a transform to the chain (returns new instance)."""
        new_transforms = self.transforms + [transform]
        return ContrastTaxonomy(
            source=self.source,
            source_details=self.source_details,
            transforms=new_transforms,
            proxy=self.proxy,
            confidence=self.confidence,
            domain=self.domain,
        )

    @property
    def cumulative_artifact_risk(self) -> float:
        """Combined artifact risk from all transforms."""
        if not self.transforms:
            return 0.0

        # Risk compounds non-linearly
        risks = [t.risk_score for t in self.transforms]
        cumulative = 1.0
        for r in risks:
            cumulative *= 1 - r
        return 1 - cumulative

    @property
    def is_governed(self) -> bool:
        """True if this taxonomy meets minimum governance requirements."""
        return (
            self.source != SourceDomain.UNKNOWN
            and self.proxy is not None
            and self.confidence is not None
            and (self.confidence.is_constitutional or self.confidence.f7_override)
        )

    @property
    def anomalous_risk_score(self) -> float:
        """
        Overall anomalous contrast risk score (0.0 - 1.0).

        High when:
        - Source is unknown or synthetic
        - Many high-risk transforms applied
        - Proxy is speculative
        - Confidence is outside F7 band
        """
        score = 0.0

        # Source risk
        if self.source == SourceDomain.UNKNOWN:
            score += 0.3
        elif self.source == SourceDomain.SYNTHETIC:
            score += 0.2
        elif not self.source.is_physical():
            score += 0.1

        # Transform risk
        score += self.cumulative_artifact_risk * 0.4

        # Proxy risk
        if self.proxy:
            if self.proxy.is_high_risk:
                score += 0.2
            if self.proxy.requires_confirmation:
                score += 0.1
        else:
            score += 0.3  # No proxy defined

        # Confidence risk
        if self.confidence:
            if (
                not self.confidence.is_constitutional
                and not self.confidence.f7_override
            ):
                score += 0.2
        else:
            score += 0.2  # No confidence declared

        return min(1.0, score)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "source": self.source.name,
            "source_details": self.source_details,
            "transforms": [
                {
                    "name": t.name,
                    "category": t.category,
                    "artifact_risk": t.artifact_risk,
                }
                for t in self.transforms
            ],
            "proxy": (
                {
                    "visual_feature": self.proxy.visual_feature,
                    "claimed_physical": self.proxy.claimed_physical_quantity,
                    "validity": self.proxy.proxy_validity,
                    "reliability": self.proxy.reliability,
                }
                if self.proxy
                else None
            ),
            "confidence": (
                {
                    "value": self.confidence.value,
                    "type": self.confidence.confidence_type,
                    "label": self.confidence.confidence_label,
                }
                if self.confidence
                else None
            ),
            "domain": self.domain,
            "anomalous_risk_score": self.anomalous_risk_score,
        }
