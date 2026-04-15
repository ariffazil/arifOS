"""
arifosmcp/contracts/continuity.py — Canonical Handoff Hashing (Audit Fix 6)

Rule 4: One tool = one contract. 
Rule 7: Enforce stage boundaries in code.
"""

from enum import Enum
from pydantic import BaseModel, Field

class KernelState(str, Enum):
    """The three canonical kernel states (Audit Fix 3)."""
    READY = "READY"       # System ready to accept work
    HOLD = "HOLD"         # Paused, waiting for condition
    BLOCKED = "BLOCKED"   # Cannot proceed, requires intervention

class Stage(str, Enum):
    """Canonical arifOS stages."""
    INIT = "000_INIT"
    SENSE = "111_SENSE"
    PLAN = "222_PLAN"
    MIND = "333_MIND"
    ROUTER = "444_ROUTER"
    MEMORY = "555_MEMORY"
    HEART = "666_HEART"
    FORGE = "777_FORGE"
    JUDGE = "888_JUDGE"
    VAULT = "999_VAULT"

class HandoffSpec(BaseModel):
    """Clean handoff specification (Audit Fix 3)."""
    next_stage: Stage
    required_inputs: list[str] = Field(default_factory=list)
    release_condition: str = "governance_seal"
    estimated_tokens: int = 0

class ContinuityState(BaseModel):
    """Immutable handoff contract (Fix 3/6)."""
    kernel_state: KernelState = KernelState.READY
    current_stage: Stage
    handoff: HandoffSpec | None = None
    
    # Cryptographic proof
    handoff_hash: str | None = None
    continuity_version: int = 1
    session_id: str
    issued_at: float
    expires_at: float | None = None
