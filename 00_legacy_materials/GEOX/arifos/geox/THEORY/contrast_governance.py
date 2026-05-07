"""
Contrast Governance — Verdict Determination from ToAC
DITEMPA BUKAN DIBERI

Implements constitutional verdict logic based on Theory of Anomalous Contrast.

Verdicts:
  SEAL:    Full physical grounding, low conflation risk
  QUALIFY: Good grounding but with acknowledged limitations
  HOLD:    Elevated conflation risk, requires human review
  BLOCK:   Unacceptable risk, cannot proceed
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from .contrast_taxonomy import ContrastTaxonomy
from .contrast_theory import ConflationRisk


class ContrastVerdict(Enum):
    """
    Constitutional verdicts for contrast-governed interpretation.

    These map to GEOX verdicts but are specific to contrast governance.
    """

    SEAL = auto()  # Full physical grounding
    QUALIFY = auto()  # Good but limited
    HOLD = auto()  # Elevated risk, review required
    BLOCK = auto()  # Cannot proceed

    def to_geox_verdict(self) -> str:
        """Convert to standard GEOX verdict string."""
        mapping = {
            ContrastVerdict.SEAL: "SEAL",
            ContrastVerdict.QUALIFY: "QUALIFY",
            ContrastVerdict.HOLD: "HOLD",
            ContrastVerdict.BLOCK: "GEOX_BLOCK",
        }
        return mapping[self]


@dataclass
class HOLDTrigger:
    """
    A specific condition that triggered a HOLD verdict.

    HOLDs are not failures — they are governance checkpoints that
    require human attention before proceeding.
    """

    trigger_type: str
    description: str
    mitigation: str
    floor_violated: str  # e.g., "F7", "F9"

    def to_dict(self) -> dict[str, str]:
        return {
            "type": self.trigger_type,
            "description": self.description,
            "mitigation": self.mitigation,
            "floor": self.floor_violated,
        }


@dataclass
class GovernancePolicy:
    """
    Policy for determining verdicts from contrast risk assessments.

    Different domains may have different policies, but all derive
    from the same Theory of Anomalous Contrast.
    """

    # Domain this policy applies to
    domain: str

    # Risk thresholds for each verdict
    seal_max_risk: float = 0.2  # Risk must be below this for SEAL
    qualify_max_risk: float = 0.4  # Risk must be below this for QUALIFY
    hold_max_risk: float = 0.7  # Risk must be below this for HOLD
    # Above hold_max_risk = BLOCK

    # Required elements for each verdict level
    seal_requires: list[str] = field(
        default_factory=lambda: ["physical_source", "validated_proxy", "f7_confidence"]
    )
    qualify_requires: list[str] = field(
        default_factory=lambda: ["proxy_defined", "confidence_declared"]
    )

    # Auto-HOLD triggers (always trigger HOLD regardless of risk)
    auto_hold_triggers: list[str] = field(
        default_factory=lambda: [
            "unknown_source",
            "critical_transform_without_validation",
            "confidence_outside_f7",
        ]
    )

    def determine_verdict(
        self,
        taxonomy: ContrastTaxonomy,
        risk: ConflationRisk | None = None,
    ) -> tuple[ContrastVerdict, list[HOLDTrigger]]:
        """
        Determine verdict from taxonomy and risk assessment.

        Returns:
            (verdict, list of HOLD triggers if applicable)
        """
        triggers: list[HOLDTrigger] = []

        # Check auto-HOLD triggers first
        if taxonomy.source.name == "UNKNOWN":
            triggers.append(
                HOLDTrigger(
                    trigger_type="unknown_source",
                    description="Source domain is UNKNOWN — cannot verify physical grounding",
                    mitigation="Provide provenance information or validate with orthogonal data",
                    floor_violated="F9",
                )
            )

        # Check for critical transforms
        critical_transforms = [t for t in taxonomy.transforms if t.artifact_risk == "critical"]
        if critical_transforms and taxonomy.source.name == "UNKNOWN":
            triggers.append(
                HOLDTrigger(
                    trigger_type="critical_transform_without_validation",
                    description=f"Critical transforms applied without physical validation: {[t.name for t in critical_transforms]}",
                    mitigation="Validate features with independent data or reduce transform intensity",
                    floor_violated="F4",
                )
            )

        # Check confidence
        if taxonomy.confidence and not taxonomy.confidence.is_constitutional:
            if not taxonomy.confidence.f7_override:
                triggers.append(
                    HOLDTrigger(
                        trigger_type="confidence_outside_f7",
                        description=f"Confidence {taxonomy.confidence.value} outside constitutional band [0.03, 0.15]",
                        mitigation="Adjust confidence to F7-compliant range or provide override justification",
                        floor_violated="F7",
                    )
                )

        # If any triggers, return HOLD
        if triggers:
            return ContrastVerdict.HOLD, triggers

        # Calculate effective risk
        anomalous_risk = taxonomy.anomalous_risk_score
        if risk:
            # Blend taxonomy risk with assessed risk
            anomalous_risk = max(anomalous_risk, risk.conflation_likelihood)

        # Determine verdict from risk
        if anomalous_risk < self.seal_max_risk:
            # Check if SEAL requirements are met
            if self._meets_seal_requirements(taxonomy):
                return ContrastVerdict.SEAL, []
            else:
                return ContrastVerdict.QUALIFY, []

        elif anomalous_risk < self.qualify_max_risk:
            return ContrastVerdict.QUALIFY, []

        elif anomalous_risk < self.hold_max_risk:
            triggers.append(
                HOLDTrigger(
                    trigger_type="elevated_anomalous_risk",
                    description=f"Anomalous contrast risk {anomalous_risk:.2f} exceeds QUALIFY threshold",
                    mitigation="Add validation data, reduce transforms, or document alternatives",
                    floor_violated="F2",
                )
            )
            return ContrastVerdict.HOLD, triggers

        else:
            # BLOCK — risk too high
            return ContrastVerdict.BLOCK, [
                HOLDTrigger(
                    trigger_type="critical_anomalous_risk",
                    description=f"Anomalous contrast risk {anomalous_risk:.2f} exceeds safe operating threshold",
                    mitigation="Fundamentally re-acquire data with better provenance or abandon interpretation",
                    floor_violated="F9",
                )
            ]

    def _meets_seal_requirements(self, taxonomy: ContrastTaxonomy) -> bool:
        """Check if taxonomy meets all requirements for SEAL verdict."""
        # Must have physical source
        if not taxonomy.source.is_physical():
            return False

        # Must have validated proxy
        if not taxonomy.proxy:
            return False
        if taxonomy.proxy.is_high_risk:
            return False

        # Must have constitutional confidence
        if not taxonomy.confidence:
            return False
        if not taxonomy.confidence.is_constitutional:
            return False

        # Risk must be low
        if taxonomy.anomalous_risk_score > self.seal_max_risk:
            return False

        return True


# Standard policies for each domain

POLICY_SEISMIC = GovernancePolicy(
    domain="seismic",
    seal_max_risk=0.15,  # Very conservative for seismic
    qualify_max_risk=0.35,
    hold_max_risk=0.65,
    auto_hold_triggers=[
        "unknown_source",
        "raster_only_input",  # Image without SEG-Y
        "critical_transform_without_validation",
        "confidence_outside_f7",
        "bond_synthetic_ambiguity",  # Inversion-like structures
    ],
)

POLICY_MEDICAL = GovernancePolicy(
    domain="medical",
    seal_max_risk=0.20,
    qualify_max_risk=0.40,
    hold_max_risk=0.70,
)

POLICY_GENERIC = GovernancePolicy(
    domain="generic",
    seal_max_risk=0.25,
    qualify_max_risk=0.45,
    hold_max_risk=0.75,
)


def assess_conflation_risk(
    taxonomy: ContrastTaxonomy,
    domain: str = "generic",
) -> tuple[ContrastVerdict, list[HOLDTrigger], dict[str, Any]]:
    """
    Main entry point for contrast risk assessment.

    Args:
        taxonomy: Complete contrast taxonomy for the feature
        domain: Which domain policy to apply

    Returns:
        (verdict, hold_triggers, assessment_metadata)
    """
    # Select policy
    policies = {
        "seismic": POLICY_SEISMIC,
        "medical": POLICY_MEDICAL,
        "generic": POLICY_GENERIC,
    }
    policy = policies.get(domain, POLICY_GENERIC)

    # Determine verdict
    verdict, triggers = policy.determine_verdict(taxonomy)

    # Build metadata
    metadata = {
        "domain": domain,
        "policy": policy.domain,
        "anomalous_risk_score": taxonomy.anomalous_risk_score,
        "source_domain": taxonomy.source.name,
        "transform_count": len(taxonomy.transforms),
        "cumulative_artifact_risk": taxonomy.cumulative_artifact_risk,
        "is_governed": taxonomy.is_governed,
    }

    return verdict, triggers, metadata
