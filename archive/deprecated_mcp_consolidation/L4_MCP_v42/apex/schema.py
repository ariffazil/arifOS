"""
Canonical Schemas for L4_MCP apex.verdict.

Defines immutable data structures for request/response contracts.
These are the ONLY external-facing types from L4_MCP.

Version: v45.1.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Verdict(str, Enum):
    """
    Single source of truth for verdict outcomes.

    Black-box verdicts (L4_MCP):
    - SEAL: Approved (seal of approval)
    - VOID: Blocked (constitutional violation)
    - SABAR: Pause & cool down (soft floor fail → collapsed from PARTIAL)
    - HOLD_888: Human review required (escalation)

    Note: PARTIAL exists in glass-box (arifos_core/mcp) but is
    collapsed to SABAR in black-box for simplicity.
    """

    SEAL = "SEAL"
    VOID = "VOID"
    SABAR = "SABAR"
    HOLD_888 = "HOLD_888"


class ActionClass(str, Enum):
    """
    Action risk classification.

    Used to determine required evidence and constraints.
    """

    READ = "READ"  # Low risk (read-only action)
    WRITE = "WRITE"  # Medium risk (reversible change)
    DELETE = "DELETE"  # High risk (irreversible change)
    PUBLISH = "PUBLISH"  # High risk (public or permanent effect)
    PAY = "PAY"  # Critical risk (financial transaction)
    SELF_MODIFY = "SELF_MODIFY"  # Existential risk (self-modification)
    UNKNOWN = "UNKNOWN"  # Unclassified or unknown action


@dataclass(frozen=True)
class Caller:
    """
    Immutable caller identity information.

    Extracted from context or provided explicitly.
    Used for audit logging and trust-level weighting.
    """

    source: str = "unknown"  # e.g., "openai", "claude-desktop", "local-ci"
    model: str = "unknown"  # e.g., "gpt-5", "claude-3.7"
    tenant: str = "unknown"  # e.g., "arif", "acme-corp"
    trust_level: str = "unknown"  # e.g., "low", "medium", "high"


@dataclass(frozen=True)
class ApexRequest:
    """
    Immutable request to apex.verdict.

    This is the ONLY input contract for the black-box authority.
    """

    task: str  # The proposed action (natural language or code)
    params: Dict[str, Any] = field(default_factory=dict)  # Parameters for the task
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context (metadata, env)
    caller: Optional[Caller] = None  # Identity of the caller (if already known)


@dataclass
class ApexResponse:
    """
    Structured verdict response from apex.verdict.

    This is the ONLY output contract for the black-box authority.
    All internal computation is hidden; only the final decision is exposed.
    """

    verdict: Verdict  # Outcome: SEAL, VOID, SABAR, or HOLD_888
    apex_pulse: float  # Confidence/impact score (0.0–1.0)
    reason_codes: List[str]  # Codes for reasons (e.g. floor triggers, patterns)
    required_evidence: List[str]  # Any evidence required to proceed (if conditional)
    constraints: List[str]  # Constraints on execution (e.g., "no_external_calls")
    floor_triggered: List[str]  # Which Floors triggered (if any)
    action_class: ActionClass  # Classification of the action risk
    caller: Caller  # Caller identity (always populated in response)
    explanation: str  # Human-readable explanation of the verdict
    cooling_ledger_id: Optional[str]  # Audit log ID (None if ledger failed)
    timestamp: str  # ISO8601 UTC timestamp of the verdict
