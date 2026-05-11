"""
GEOX — Geospatial World-Model Agent for arifOS
DITEMPA BUKAN DIBERI

Theory of Anomalous Contrast (ToAC) — The Core Principle:

    Visual contrast is NOT physical reality.
    Every pixel you see has been transformed:
        Physical Signal → Processing → Display Encoding → Perception

    GEOX prevents conflation (confusion between visual and physical) by:
        1. Computing PHYSICAL attributes FIRST
        2. Documenting EVERY transform in the chain
        3. AUDITING for anomalous contrast (display >> physical)
        4. REQUIRING human review when risk is high

Architecture: THEORY → ENGINE → TOOLS → GOVERNANCE
"""

__version__ = "0.4.0"
__author__ = "arifOS"

# Import layers directly (avoiding circular imports)
# THEORY Layer — Core principles
from .THEORY import (
    # Taxonomy
    SourceDomain,
    VisualTransform,
    PhysicalProxy,
    ConfidenceClass,
    ContrastTaxonomy,
    TRANSFORM_CATALOG,
    # Governance
    ContrastVerdict,
    HOLDTrigger,
    GovernancePolicy,
    assess_conflation_risk,
    POLICY_SEISMIC,
    POLICY_MEDICAL,
    POLICY_GENERIC,
    check_floor_compliance,
    # Theory
    ConflationRisk,
    ContrastDomain,
    ContrastCanon,
    ContrastStack,
    SignalAudit,
    AnomalousContrastTheory,
    ToACCore,
    # Constants
    GEOX_SEAL,
    GEOX_SABAR,
    GEOX_PARTIAL,
    GEOX_REVIEW,
    GEOX_HOLD,
    GEOX_BLOCK,
    GEOX_VOID,
)

# ENGINE Layer — Processing core
from .ENGINE import (
    ContrastSpace,
    ContrastFeature,
    TransformRegistry,
    TransformProfile,
    get_registry,
    AnomalyDetector,
    ConflationAlert,
)

# GOVERNANCE Layer — Compliance
from .governance import (
    FloorEnforcer,
    FloorCheckResult,
    AuditLogger,
    AuditEntry,
    VerdictRenderer,
    RenderedVerdict,
    ConflationReport,
    generate_conflation_report,
)

__all__ = [
    # Version
    "__version__",
    # THEORY
    "SourceDomain",
    "VisualTransform",
    "PhysicalProxy",
    "ConfidenceClass",
    "ContrastTaxonomy",
    "TRANSFORM_CATALOG",
    "ContrastVerdict",
    "HOLDTrigger",
    "GovernancePolicy",
    "assess_conflation_risk",
    "POLICY_SEISMIC",
    "POLICY_MEDICAL",
    "POLICY_GENERIC",
    "check_floor_compliance",
    "ConflationRisk",
    "ContrastDomain",
    "ContrastCanon",
    "ContrastStack",
    "SignalAudit",
    "AnomalousContrastTheory",
    "ToACCore",
    "GEOX_SEAL",
    "GEOX_SABAR",
    "GEOX_PARTIAL",
    "GEOX_REVIEW",
    "GEOX_HOLD",
    "GEOX_BLOCK",
    "GEOX_VOID",
    # ENGINE
    "ContrastSpace",
    "ContrastFeature",
    "TransformRegistry",
    "TransformProfile",
    "get_registry",
    "AnomalyDetector",
    "ConflationAlert",
    # GOVERNANCE
    "FloorEnforcer",
    "FloorCheckResult",
    "AuditLogger",
    "AuditEntry",
    "VerdictRenderer",
    "RenderedVerdict",
    "ConflationReport",
    "generate_conflation_report",
]


def get_geox_info() -> dict:
    """Get information about the GEOX installation."""
    return {
        "version": __version__,
        "theory": "Theory of Anomalous Contrast (ToAC)",
        "layers": ["THEORY", "ENGINE", "TOOLS", "GOVERNANCE"],
        "domains": ["seismic", "generic (extensible)"],
        "constitutional_floors": ["F1", "F4", "F7", "F9", "F13"],
    }


# Lazy imports for TOOLS layer
# These require separate import to avoid circular dependencies
def get_tools():
    """Get the TOOLS layer. Use this for accessing seismic/generic tools."""
    from . import TOOLS

    return TOOLS
