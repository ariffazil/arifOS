"""
888_HOLD Escalation State Machine

F13 Sovereign Safety Valve
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class EscalationPathway(Enum):
    """Three constitutional escalation pathways."""
    REPLY_CONTINUE = auto()
    OFFER_HANDOVER = auto()
    FORCED_ESCALATION = auto()


class HoldState(Enum):
    """States in the 888_HOLD lifecycle."""
    PENDING = auto()
    APPROVED = auto()
    DENIED = auto()
    TIMEOUT = auto()
    CANCELLED = auto()


@dataclass
class HoldRequest:
    """A request for human approval (888_HOLD)."""
    hold_id: str
    execution_id: str
    agent_id: str
    action_type: str
    pathway: EscalationPathway
    reason: str
    risk_level: str
    floor_violations: list[str] = field(default_factory=list)
    state: HoldState = field(default=HoldState.PENDING)
    human_decision: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: int = 3600


class HoldStateManager:
    """888_HOLD State Machine Manager."""
    
    _registry: ClassVar[dict[str, dict[str, Any]]] = {}
    
    def __init__(self) -> None:
        self.pending_holds: dict[str, HoldRequest] = {}
        self.resolved_holds: dict[str, HoldRequest] = {}
        self.stats: dict[str, int] = {
            "total_escalations": 0,
            "pending_count": 0,
            "approved": 0,
            "denied": 0,
            "timeouts": 0,
        }
    
    async def create_hold(
        self,
        execution_id: str,
        agent_id: str,
        action_type: str,
        reason: str,
        risk_level: str,
        pathway: EscalationPathway,
        floor_violations: list[str] | None = None,
    ) -> HoldRequest:
        """Create a new hold request."""
        import uuid
        hold_id = str(uuid.uuid4())[:8]
        hold = HoldRequest(
            hold_id=hold_id,
            execution_id=execution_id,
            agent_id=agent_id,
            action_type=action_type,
            reason=reason,
            risk_level=risk_level,
            pathway=pathway,
            floor_violations=floor_violations or [],
        )
        self.pending_holds[hold_id] = hold
        self.stats["total_escalations"] += 1
        self.stats["pending_count"] = len(self.pending_holds)
        logger.info(f"[{hold_id}] Created {pathway.name} hold: {reason}")
        return hold
