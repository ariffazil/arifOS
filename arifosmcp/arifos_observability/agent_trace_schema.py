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

from pydantic import BaseModel, Field


class AgentTraceSpan(BaseModel):
    """Typed schema for an arifOS agent trace span."""

    span_id: str
    trace_id: str
    name: str
    actor_id: str
    action_class: str  # OBSERVE | ANALYZE | MUTATE | GOVERNED | SEAL
    tool: str
    session_id: str | None = None
    lease_id: str | None = None
    verdict: str | None = None  # SEAL | SABAR | HOLD | VOID
    input_hash: str | None = None
    output_hash: str | None = None
    entropy_delta: float | None = None
    start_time_ns: int
    end_time_ns: int | None = None
    attributes: dict = Field(default_factory=dict)
    error: str | None = None


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
