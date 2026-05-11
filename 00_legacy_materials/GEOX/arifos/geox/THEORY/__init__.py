"""
GEOX THEORY Layer — Theory of Anomalous Contrast (ToAC)
DITEMPA BUKAN DIBERI

The constitutional foundation of GEOX. Defines the core mathematical
and philosophical framework distinguishing physical signal from
visual perception.
"""

from .contrast_taxonomy import (
    SourceDomain,
    VisualTransform,
    PhysicalProxy,
    ConfidenceClass,
    ContrastTaxonomy,
    TRANSFORM_CATALOG,
)

from .contrast_governance import (
    ContrastVerdict,
    HOLDTrigger,
    GovernancePolicy,
    assess_conflation_risk,
    POLICY_SEISMIC,
    POLICY_MEDICAL,
    POLICY_GENERIC,
)

from .contrast_theory import (
    ConflationRisk,
    ContrastDomain,
    ContrastCanon,
    ContrastStack,
    SignalAudit,
    AnomalousContrastTheory,
    ToACCore,
)

# Constants (defined here for convenience)
GEOX_SEAL = "SEAL"
GEOX_SABAR = "SABAR"
GEOX_PARTIAL = "PARTIAL"
GEOX_REVIEW = "REVIEW"
GEOX_HOLD = "HOLD"
GEOX_BLOCK = "GEOX_BLOCK"
GEOX_VOID = "VOID"


# Placeholder for check_floor_compliance - to be implemented
# For now, return empty list (no violations)
def check_floor_compliance(data, confidence=None, provenance=None):
    """Check constitutional floor compliance."""
    violations = []
    # F7 Humility check
    if confidence is not None:
        if not (0.03 <= confidence <= 0.15):
            violations.append("F7_humility")
    # F9 Anti-Hantu check
    if provenance is None or not provenance.get("verified", False):
        violations.append("F9_provenance")
    return violations


__all__ = [
    # Taxonomy
    "SourceDomain",
    "VisualTransform",
    "PhysicalProxy",
    "ConfidenceClass",
    "ContrastTaxonomy",
    "TRANSFORM_CATALOG",
    # Governance
    "ContrastVerdict",
    "HOLDTrigger",
    "GovernancePolicy",
    "assess_conflation_risk",
    "POLICY_SEISMIC",
    "POLICY_MEDICAL",
    "POLICY_GENERIC",
    "check_floor_compliance",
    # Theory
    "ConflationRisk",
    "ContrastDomain",
    "ContrastCanon",
    "ContrastStack",
    "SignalAudit",
    "AnomalousContrastTheory",
    "ToACCore",
    # Constants
    "GEOX_SEAL",
    "GEOX_SABAR",
    "GEOX_PARTIAL",
    "GEOX_REVIEW",
    "GEOX_HOLD",
    "GEOX_BLOCK",
    "GEOX_VOID",
]
