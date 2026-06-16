"""
Agent Trace Schema — Typed schema for agent-specific trace attributes.

Every arifOS tool call span carries:
- arifos.actor_id
- arifos.action_class
- arifos.tool
- arifos.session_id
- arifos.lease_id
- arifos.verdict
- arifos.input_hash
- arifos.output_hash
- arifos.entropy_delta
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field


class AgentTraceSpan(BaseModel):
    """Typed schema for an arifOS agent trace span."""

    span_id: str
    trace_id: str
    name: str
    actor_id: str
    action_class: str  # OBSERVE | ANALYZE | MUTATE | GOVERNED | SEAL
    tool: str
    session_id: Optional[str] = None
    lease_id: Optional[str] = None
    verdict: Optional[str] = None  # SEAL | SABAR | HOLD | VOID
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    entropy_delta: Optional[float] = None
    start_time_ns: int
    end_time_ns: Optional[int] = None
    attributes: dict = Field(default_factory=dict)
    error: Optional[str] = None


class AgentTraceSchema:
    """Pydantic-based schema validator for agent trace spans."""

    @staticmethod
    def validate(span: dict) -> AgentTraceSpan:
        return AgentTraceSpan(**span)

    @staticmethod
    def attributes() -> list[str]:
        """List of canonical arifOS attribute names."""
        return [
            "arifos.actor_id",
            "arifos.action_class",
            "arifos.tool",
            "arifos.session_id",
            "arifos.lease_id",
            "arifos.verdict",
            "arifos.input_hash",
            "arifos.output_hash",
            "arifos.entropy_delta",
            "arifos.floor_compliance",
            "arifos.epoch",
        ]
