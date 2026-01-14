"""
eureka_types.py — Phase 1 EUREKA Memory Engine Types (v38.3Omega)

Core data model for memory write requests and decisions.
Coexists with existing memory infrastructure.

Author: arifOS Project
Version: v38.3 Phase 1
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Literal


class MemoryBand(str, Enum):
    """Memory band targets for write operations."""
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    PHOENIX = "PHOENIX"
    LEDGER = "LEDGER"
    VAULT = "VAULT"
    VOID = "VOID"


class Verdict(str, Enum):
    """Verdict types for memory routing."""
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    SABAR_EXTENDED = "SABAR_EXTENDED"
    VOID = "VOID"
    HOLD_888 = "888_HOLD"


class ActorRole(str, Enum):
    """Actor roles for authority checks."""
    HUMAN = "HUMAN"                # Human operator/judge
    JUDICIARY = "JUDICIARY"        # APEX PRIME / @EYE (advisory + veto)
    ENGINE = "ENGINE"              # Pipeline / system code
    TOOL = "TOOL"                  # External tool calls, untrusted


@dataclass(frozen=True)
class MemoryWriteRequest:
    """
    Request to write to memory.
    
    Immutable request object that captures intent before routing.
    """
    # Who/why
    actor_role: ActorRole
    verdict: Verdict
    reason: str

    # What to write
    content: Dict[str, Any]              # Structured payload only
    tags: List[str] = field(default_factory=list)

    # Governance context
    high_stakes: bool = False
    human_seal: bool = False             # Explicit human confirmation
    parent_hash: Optional[str] = None    # Chain link if available


@dataclass(frozen=True)
class MemoryWriteDecision:
    """
    Decision about a memory write request.
    
    Result of routing logic after authority checks.
    """
    allowed: bool
    target_band: MemoryBand
    action: Literal["APPEND", "DROP"]
    why: str
    requires_human_seal: bool = False


__all__ = [
    "MemoryBand",
    "Verdict",
    "ActorRole",
    "MemoryWriteRequest",
    "MemoryWriteDecision",
]
