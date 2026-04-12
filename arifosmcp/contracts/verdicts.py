"""
arifosmcp/contracts/verdicts.py — Canonical Governance Verdicts (Audit Fix 2, 3)

Rule 2: One state name = one meaning. 
Rule 5: Symbolic philosophy compiles into plain structs.
"""

from enum import Enum
from pydantic import BaseModel, Field

class ExecutionStatus(str, Enum):
    """Mechanical status of the tool execution (Fix 2)."""
    SUCCESS = "SUCCESS"      # Tool ran to completion
    ERROR = "ERROR"          # Runtime error (exception, crash)
    TIMEOUT = "TIMEOUT"      # Execution exceeded deadline
    DRY_RUN = "DRY_RUN"      # Simulated execution
    PARTIAL = "PARTIAL"      # Partial execution

class GovernanceStatus(str, Enum):
    """Constitutional verdict (Fix 2, Audit Critical Fix 3)."""
    APPROVED = "APPROVED"    # Maps from SEAL
    PARTIAL = "PARTIAL"      # Limited approval
    PAUSE = "PAUSE"          # Maps from SABAR
    HOLD = "HOLD"            # Awaiting human (F13)
    VOID = "VOID"            # Forbidden/Blocked
    PROVISIONAL = "PROVISIONAL" # Preliminary approval

class ArtifactStatus(str, Enum):
    """State of the output artifact (Audit Fix 4)."""
    USABLE = "USABLE"           # Complete, can be used downstream
    PARTIAL = "PARTIAL"         # Incomplete but usable
    STAGED = "STAGED"           # Prepared but not yet committed
    REJECTED = "REJECTED"       # Failed validation
    EMPTY = "EMPTY"             # No output produced
    SEALED = "SEALED"           # Immutably committed

class ContinuationStatus(str, Enum):
    """Orchestration direction (Fix 3)."""
    READY = "READY"
    HOLD = "HOLD"
    BLOCKED = "BLOCKED"
    CLARIFY_FIRST = "CLARIFY_FIRST"

class VerdictDetail(BaseModel):
    """Audit Fix 2: Structured Verdict Envelope v2.0."""
    code: GovernanceStatus
    reason_code: str
    message: str
    floors_checked: list[str] = Field(default_factory=list)
    floors_failed: list[str] = Field(default_factory=list)
