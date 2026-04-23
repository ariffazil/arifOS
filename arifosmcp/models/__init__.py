"""arifosmcp.models - Constitutional data models."""

# Core metabolic models
from .cycle3e import Cycle3E, MetabolicPhase

# MGI (Machine -> Governance -> Intelligence)
from .mgi import MGIEnvelope, MGIBaseResponse
MGI = MGIEnvelope
GovernanceInterface = MGIBaseResponse

# Verdict models (v2.0 canonical)
from .verdicts import SealType, VerdictState, FloorName, VerdictResult

__all__ = [
    "SealType",
    "VerdictState",
    "FloorName",
    "VerdictResult",
    "Cycle3E",
    "MetabolicPhase",
    "MGI",
    "MGIEnvelope",
    "MGIBaseResponse",
    "GovernanceInterface",
]
