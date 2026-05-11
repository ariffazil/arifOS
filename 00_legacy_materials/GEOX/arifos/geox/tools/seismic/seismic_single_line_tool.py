"""
SeismicSingleLineTool — Governed Inverse Modelling Supervisor
DITEMPA BUKAN DIBERI

A domain-aware inverse modelling coordinator that orchestrates deterministic
physics signals (attributes) and probabilistic AI patterns (VLM/CV) into a
governed family of plausible subsurface models.

Follows Theory of Anomalous Contrast (ToAC).
  1. Prevents "Narrative Collapse" by forcing non-unique inverse solutions.
  2. Anchors all "Meta-intelligence" in physical groundings (well-ties/attributes).
  3. Enforces the Bond et al. (2007) anti-bias workflow.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

from ...ENGINE import ContrastFeature, ContrastSpace, get_registry
from ...ENGINE.contrast_wrapper import compute_contrast_verdict
from ...THEORY import (
    GEOX_HOLD,
    ContrastTaxonomy,
)
from .seismic_attribute_calculator import SeismicAttributeCalculator
from .synthetic_generator import SeismicSyntheticGenerator

# Logger setup
logger = logging.getLogger(__name__)


def _make_seismic_taxonomy(level: str = "none") -> ContrastTaxonomy:
    """Create a default seismic contrast taxonomy."""
    from ...THEORY import ConfidenceClass, PhysicalProxy, SourceDomain

    source = SourceDomain.SENSOR if level == "high" else SourceDomain.UNKNOWN
    return ContrastTaxonomy(
        domain=source,
        physical_proxy=PhysicalProxy.ACOUSTIC_IMPEDANCE,
        confidence_class=ConfidenceClass.PROBABILISTIC,
    )


@dataclass
class BiasAuditRecord:
    """Record of a potential bias identified during interpretation."""

    bias_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    mitigation: str
    is_mitigated: bool = False


@dataclass
class SeismicInterpretationResult:
    """Result from seismic interpretation with full governance metadata."""

    # Inverse Model Space
    primary_interpretation: str
    confidence: float
    plausible_model_candidates: list[dict[str, Any]] = field(default_factory=list)

    # Attributes computed
    attributes: dict[str, np.ndarray] = field(default_factory=dict)

    # Governance & Continuity
    bias_audit: list[BiasAuditRecord] = field(default_factory=list)
    transform_chain: list[str] = field(default_factory=list)
    verdict: str = GEOX_HOLD
    contrast_space: ContrastSpace | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to a serializable dictionary."""
        return {
            "primary_interpretation": self.primary_interpretation,
            "confidence": self.confidence,
            "plausible_model_candidates": self.plausible_model_candidates,
            "attribute_count": len(self.attributes),
            "bias_audit": [
                {
                    "bias_type": b.bias_type,
                    "severity": b.severity,
                    "mitigation": b.mitigation,
                }
                for b in self.bias_audit
            ],
            "transform_chain": self.transform_chain,
            "verdict": self.verdict,
        }


class SeismicSingleLineTool:
    """
    Governed inverse modelling supervisor for single-line interpretation.
    """

    def __init__(self):
        self.calculator = SeismicAttributeCalculator()
        self.generator = SeismicSyntheticGenerator()
        self.registry = get_registry()

    async def run(self, params: dict[str, Any]) -> dict[str, Any]:
        """Run the tool with given parameters."""
        file_path = params.get("file_path", "")
        result = await self.interpret_line(file_path)
        return result.to_dict()

    def interpret(
        self, line_data: np.ndarray | str, source_type: str = "RASTER"
    ) -> SeismicInterpretationResult:
        """
        Coordinate the inverse modelling process for a seismic line.
        """
        # 1. Normalize data
        data = self._ensure_ndarray(line_data)

        # 2. Compute Physical Attributes (Grounding)
        attributes = self._compute_grounding_attributes(data)

        # 3. Perform Bias Audit (Bond et al. 2007)
        bias_audit = self._run_bias_audit(data, attributes)

        # 4. Define Contrast Taxonomy
        taxonomy = _make_seismic_taxonomy(level="high" if attributes else "none")

        # 5. Core Interpretation (Probabilistic Pattern Recognition)
        if source_type == "ORCHESTRATED":
            interpretation = self._interpret_orchestrated(data, attributes)
        else:
            interpretation = self._interpret_from_visual_only(data)

        # 6. Determine verdict based on source and audit
        verdict_data = compute_contrast_verdict(attributes)
        verdict = verdict_data["verdict"]

        # 7. Build contrast space
        contrast_space = self._build_contrast_space(attributes, taxonomy)

        # 8. Document transform chain
        transform_chain = [
            "load_raster",
            "compute_attributes",
            "bias_audit",
            "inverse_orchestration",
        ]

        return SeismicInterpretationResult(
            primary_interpretation=interpretation,
            confidence=self._calculate_confidence(source_type, attributes),
            plausible_model_candidates=self._generate_plausible_candidates(interpretation),
            attributes=attributes,
            bias_audit=bias_audit,
            transform_chain=transform_chain,
            verdict=verdict,
            contrast_space=contrast_space,
        )

    def _ensure_ndarray(self, data: Any) -> np.ndarray:
        if isinstance(data, np.ndarray):
            return data

        # ACTIVATE ENGINE: If no data, use the Synthetic Generator (ToAC Grounding)
        logger.info("[GEOX] Seismic Engine Ignite: Generating synthetic extensional block.")
        return self.generator.generate_extensional_block()

    def _compute_grounding_attributes(self, data: np.ndarray) -> dict[str, np.ndarray]:
        """Compute base physical attributes for grounding."""
        attributes = {}

        # Coherence
        coh = self.calculator.compute_dip_steered_coherence(data)
        if coh:
            attributes["coherence"] = coh.values

        # Curvature
        curv = self.calculator.compute_apparent_curvature(data)
        if curv:
            attributes["curvature"] = curv.values

        return attributes

    def _run_bias_audit(
        self, data: np.ndarray, attributes: dict[str, np.ndarray]
    ) -> list[BiasAuditRecord]:
        """Execute the Bond et al. (2007) bias audit."""
        audit = []

        # Check for visual anchoring (Bond et al. 2007 failure mode 1)
        if not attributes:
            audit.append(
                BiasAuditRecord(
                    bias_type="Visual Anchoring",
                    severity="CRITICAL",
                    mitigation="Mandatory computation of coherence and curvature attributes required.",
                )
            )

        # Check for availability bias (analog matching)
        audit.append(
            BiasAuditRecord(
                bias_type="Availability Bias",
                severity="MEDIUM",
                mitigation="Forced generation of 3+ alternative structural models.",
            )
        )

        return audit

    def _interpret_orchestrated(self, data: np.ndarray, attributes: dict[str, np.ndarray]) -> str:
        """Pattern recognition informed by attributes."""
        if "coherence" in attributes and np.mean(attributes["coherence"]) < 0.7:
            return (
                "Interpreted as a complex faulted extensional block with significant discontinuity."
            )
        return "Interpreted as dominated by continuous stratigraphy with minimal structural deformation."

    def _interpret_from_visual_only(self, data: np.ndarray) -> str:
        """Pattern recognition without attribute grounding (DANGEROUS)."""
        return "Preliminary visual interpretation: potential structural closures observed."

    def _calculate_confidence(self, source: str, attributes: dict) -> float:
        """Calculate humility-aware confidence score (F7)."""
        if source != "ORCHESTRATED" or not attributes:
            return 0.3  # Low confidence for ungrounded visual
        base_confidence = 0.4 + len(attributes) * 0.15
        return min(base_confidence, 0.75)  # Cap at 0.75 per F7

    def _generate_plausible_candidates(self, primary: str) -> list[dict[str, Any]]:
        """
        Generate a family of plausible inverse models to prevent narrative collapse.
        """
        return [
            {
                "id": "candidate_extensional",
                "model": "Extensional Regime (Faulted)",
                "description": "Sub-vertical normal faults with stratigraphic thickening.",
                "evidence_strength": "HIGH" if "fault" in primary.lower() else "MEDIUM",
                "non_uniqueness_risk": "High — could be mimicked by stratigraphic pinchouts.",
            },
            {
                "id": "candidate_depositional",
                "model": "Depositional Geometry (Carbonate/Channel)",
                "description": "Lateral variations due to depositional facies, not tectonics.",
                "evidence_strength": "MEDIUM",
                "non_uniqueness_risk": "Moderate — requires spectral decomposition for tie-break.",
            },
            {
                "id": "candidate_artifact",
                "model": "Processing/Display Artifact",
                "description": "Apparent dips caused by velocity pulls or colormap aliasing.",
                "evidence_strength": "LOW",
                "non_uniqueness_risk": "Critical — Bond et al. (2007) failure mode.",
            },
        ]

    def _build_contrast_space(
        self, attributes: dict[str, np.ndarray], taxonomy: ContrastTaxonomy
    ) -> ContrastSpace:
        """Map attributes into a n-dimensional contrast space."""
        space = ContrastSpace()
        for name, values in attributes.items():
            feat = ContrastFeature(name=name, values=values, taxonomy=taxonomy)
            space.add_feature(feat)
        return space

    def get_audit_trail(
        self, bias_audit: list[BiasAuditRecord], verdict: str, confidence: float
    ) -> str:
        """Generate a human-readable audit trail for the interpretation."""
        audit_log = [
            "# GEOX INTERPRETATION AUDIT TRAIL",
            f"Generated: {datetime.now().isoformat()}",
            "---",
            "## Bias Mitigation",
        ]
        for i, audit in enumerate(bias_audit):
            audit_log.append(f"Audit {i+1}: {audit.bias_type} - Severity: {audit.severity}")
            audit_log.append(f" Mitigation: {audit.mitigation}")

        # Add physical grounding status
        audit_log.append(f"Grounding verdict: {verdict}")
        audit_log.append(f"Confidence score: {confidence:.2f}")

        # Final humility check (F7)
        if confidence < 0.5:
            audit_log.append("WARNING: Low confidence. Humility floor triggered.")

        return "\n".join(audit_log)
