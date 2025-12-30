"""
Trinity module for arifOS v45 - GitForge/GitQC/GitSeal + Response Validation.

Implements the three-stage governance gate for code changes:
- /gitforge: State mapping and entropy prediction
- /gitQC: Constitutional quality control (F1-F9 validation)
- /gitseal: Human authority gate + release bundle creation

PLUS: Real-time response validation for AI outputs.

See: L1_THEORY/canon/03_runtime/FORGING_PROTOCOL_v45.md
"""

from .forge import ForgeReport, analyze_branch
from .qc import QCReport, validate_changes
from .seal import SealDecision, execute_seal
from .housekeeper import HousekeeperProposal, propose_docs

# v45.0.1: Response Validation (machine-enforced floor checks)
from arifos_core.enforcement.response_validator import (
    FloorReport,
    validate_response,
)

__all__ = [
    # Git Governance
    "ForgeReport",
    "analyze_branch",
    "QCReport",
    "validate_changes",
    "SealDecision",
    "execute_seal",
    "HousekeeperProposal",
    "propose_docs",
    # Response Validation
    "FloorReport",
    "validate_response",
]
