"""
GEOX Theory of Anomalous Contrast (ToAC) — Core Definitions
DITEMPA BUKAN DIBERI

Definition:
Anomalous Contrast is the systematic error that occurs when visual/display contrast
(how something looks) is conflated with physical contrast (what the signal actually is).
"""

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ContrastDomain(str, Enum):
    PHYSICAL = "physical"  # Earth TRUTH (Impedance, Discontinuity)
    DISPLAY = "display"  # Visualization (Colormap, Gain, Filter)
    PERCEPTUAL = "perceptual"  # Human/Agent recognition (Edges, Patterns)


class ConflationRisk(BaseModel):
    """
    Assessment of conflation risk for a feature or interpretation.

    Conflation risk is high when visual/display contrast significantly
    exceeds physical contrast, indicating the feature may be an artifact
    of visualization rather than a true physical structure.
    """

    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk 0-1")
    physical_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in physical origin"
    )
    display_amplification: float = Field(
        ..., ge=0.0, description="How much display amplifies signal"
    )

    # Risk factors
    factors: List[str] = Field(
        default_factory=list, description="Specific risk factors identified"
    )

    def is_critical(self) -> bool:
        """True if risk is critical (> 0.8)."""
        return self.risk_score > 0.8

    def is_high(self) -> bool:
        """True if risk is high (> 0.5)."""
        return self.risk_score > 0.5


class ContrastCanon(BaseModel):
    """The mandatory rules for governed interpretation."""

    rules: List[str] = [
        "C1: Never interpret single-view contrast.",
        "C2: Cross-validate multiple visual transforms.",
        "C3: Explicitly map visual proxies to physical axes.",
        "C4: Cap confidence if physical resolution < visual saliency.",
    ]


class ContrastStack(BaseModel):
    """A multi-layer contrast representation."""

    physical_layer: Optional[Any] = None
    display_layer: Optional[Any] = None
    perceptual_layer: Optional[Any] = None
    processing_chain: List[Any] = Field(default_factory=list)


class SignalAudit(BaseModel):
    """Audit trail for signal verification."""

    has_physical_trace: bool = False
    transform_chain_documented: bool = False
    confidence_quantified: bool = False
    alternatives_considered: bool = False


class AnomalousContrastTheory:
    """Core theory implementation."""

    @staticmethod
    def identify_conflation_risk(
        physical_axes: List[str], display_transforms: List[str]
    ) -> float:
        """Calculate Risk Level (0.0 - 1.0). High risk if complex transforms used."""
        return min(1.0, len(display_transforms) * 0.2 + 0.1)

    @staticmethod
    def amplification_factor(stack: ContrastStack) -> float:
        """Total contrast amplification through processing chain."""
        if not stack.processing_chain:
            return 1.0
        total = 1.0
        for transform in stack.processing_chain:
            if hasattr(transform, "amplification_factor"):
                total *= transform.amplification_factor
        return total

    @staticmethod
    def is_anomalous(
        physical_contrast: float, visual_contrast: float, threshold: float = 2.0
    ) -> bool:
        """Anomalous if visual contrast >> physical signal."""
        if physical_contrast <= 0:
            return (
                visual_contrast > 0.1
            )  # Any visual contrast is anomalous if no physical
        return visual_contrast > physical_contrast * threshold


class ToACCore:
    @staticmethod
    def identify_conflation_risk(
        physical_axes: List[str], display_transforms: List[str]
    ) -> float:
        """Calculate Risk Level (0.0 - 1.0). High risk if complex transforms used."""
        return min(1.0, len(display_transforms) * 0.2 + 0.1)
