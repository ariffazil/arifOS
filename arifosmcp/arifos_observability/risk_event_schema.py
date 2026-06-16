"""
Risk Event Schema — Telemetry for risk events from arifOS risk floor.

Risk events are emitted when:
- A mutation is attempted on a sealed artifact
- An actor is denied authority
- An irreversible action is requested
- A constitutional floor is approached (F11 → F12)

Constitutional binding: F2 TRUTH, F11 AUDIT, F13 SOVEREIGN
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskSeverity(str, Enum):
    """Risk severity levels."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskEvent(BaseModel):
    """Typed risk event for arifOS telemetry."""

    event_id: str
    severity: RiskSeverity
    actor_id: str
    action_class: str
    tool: str
    session_id: Optional[str] = None
    reason: str
    floor: str  # e.g., "F11_AUDIT"
    reversible: bool
    human_ack_required: bool
    blast_radius: str  # LOW | MEDIUM | HIGH | CRITICAL
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    evidence: dict = Field(default_factory=dict)
