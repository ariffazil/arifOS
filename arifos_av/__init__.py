"""arifOS AV Governance — constitutional kernel for autonomous vehicles.

The layer that decides whether an action is allowed, who may decide,
and what proof is required before it counts as done.
"""

from .capability import Capability, CapabilityGate, GateVerdict
from .authority import (
    AuthorityEnvelope, AuthorityVoid, Grant, SpeechAct, Tier, require_grant,
)
from .judgment import Evidence, Judge, Verdict, complete
from .receipts import ReceiptLedger
from .handover import (
    BareActRejected, ExplanationRequired, HandoverRequest, HumanSovereign,
)
from .edge_ladder import BoundedLadder, LadderResult
from .kernel import AVGovernanceKernel, DriveAction

__version__ = "0.1.0"
__all__ = [
    "Capability", "CapabilityGate", "GateVerdict",
    "AuthorityEnvelope", "AuthorityVoid", "Grant", "SpeechAct", "Tier",
    "require_grant", "Evidence", "Judge", "Verdict", "complete",
    "ReceiptLedger", "BareActRejected", "ExplanationRequired",
    "HandoverRequest", "HumanSovereign", "BoundedLadder", "LadderResult",
    "AVGovernanceKernel", "DriveAction",
]
