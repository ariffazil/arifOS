"""
arifos — Band 1 Cognition-Firewall SDK for the arifOS kernel.

DITEMPA BUKAN DIBERI — Forged, not given.

The `arifos` namespace is the new SDK surface inside the existing
`arifOS` PyPI distribution. It sits BESIDE `arifosmcp/` (the existing
MCP/server namespace), NOT replacing it.

- `arifosmcp` = the kernel as a service (port 8088, MCP, VAULT999, F1-F13)
- `arifos`    = the kernel as a client library (Band 1 cognition firewall)

Public surface (per the corrected architecture):

    from arifos import Kernel, prethink, pretool, seal
    from arifos import Decision, ActionClass, CognitionLane
    from arifos.adapters.openai import ArifKernel
    from arifos.exceptions import ArifHold, ArifDenied, ArifSealMissing

Optional install:
    pip install arifos              # core (just this file's contents)
    pip install "arifos[openai]"    # + OpenAI Agents SDK adapter
"""

from arifos.actor import Actor
from arifos.decision import (
    ActionClass,
    CognitionLane,
    Decision,
    FloorVerdict,
    RiskEnvelope,
)
from arifos.envelope import CallEnvelope
from arifos.exceptions import (
    ArifDenied,
    ArifGovernanceError,
    ArifHold,
    ArifSealMissing,
)
from arifos.floors import (
    check_f1_reversibility,
    check_f11_audit,
    check_f13_sovereign,
    check_f2_truth,
    check_f7_humility,
)
from arifos.intent import Intent
from arifos.kernel import Kernel
from arifos.lease import Lease
from arifos.risk import (
    BlastRadius,
    Reversibility,
    classify_blast_radius,
    classify_reversibility,
)
from arifos.seal import seal
from arifos.guards import prethink, pretool, posttool

__version__ = "0.1.0"
__all__ = [
    "Actor",
    "ActionClass",
    "ArifDenied",
    "ArifGovernanceError",
    "ArifHold",
    "ArifSealMissing",
    "BlastRadius",
    "CallEnvelope",
    "CognitionLane",
    "Decision",
    "FloorVerdict",
    "Intent",
    "Kernel",
    "Lease",
    "Reversibility",
    "RiskEnvelope",
    "check_f1_reversibility",
    "check_f11_audit",
    "check_f13_sovereign",
    "check_f2_truth",
    "check_f7_humility",
    "classify_blast_radius",
    "classify_reversibility",
    "posttool",
    "prethink",
    "pretool",
    "seal",
]
