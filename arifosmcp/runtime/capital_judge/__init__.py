"""
PR5 — Capital Judge Orchestrator.

Audit-4 mandates a single orchestrator implementing the state machine:

  RECEIVED
   → AUTHENTICATED     (token + capability + audience verified)
   → VALIDATED         (schema match)
   → COMPUTED          (COMPUTATION receipt emitted)
   → JUDGED            (JUDGMENT receipt: PROCEED · HOLD · DENY)
   → HUMAN_HOLD | RATIFIED   (if ratification_required)
   → SEALED            (chain appended)
   → EXECUTED          (only via A-FORGE)

The orchestrator refuses any path that drops COMPUTATION straight to
EXECUTION. WEALTH QUALIFY NEVER auto-executes.
"""

from .state_machine import (
    State,
    TransitionError,
    CapitalCase,
    Receipt,
    StateMachine,
)
from .receipt import (
    ComputationReceipt,
    JudgmentReceipt,
    HumanRatificationReceipt,
    ExecutionReceipt,
)
from .orchestrator import CapitalJudgeOrchestrator

__all__ = [
    "State",
    "TransitionError",
    "CapitalCase",
    "Receipt",
    "StateMachine",
    "ComputationReceipt",
    "JudgmentReceipt",
    "HumanRatificationReceipt",
    "ExecutionReceipt",
    "CapitalJudgeOrchestrator",
]
