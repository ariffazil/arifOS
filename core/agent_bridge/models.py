"""Pydantic models for cross-agent telemetry.

These shapes are published to NATS JetStream and consumed by arifOS
for ingestion into L3 (Qdrant) and L5 (Graphiti).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AgentTelemetry(BaseModel):
    """One telemetry event: what an agent did, how it went, what it learned."""

    agent_id: str = Field(
        ...,
        description="Canonical agent name: kimi | claude | codex | copilot | aider | continue | gemini",
    )
    session_id: str = Field(..., description="Federation session identifier")
    task_hash: str = Field(..., description="SHA-256 of the normalized task intent")
    intent: str = Field(..., description="Human-readable summary of the task")
    tools_used: list[str] = Field(default_factory=list, description="MCP tools invoked")
    outcome: str = Field(default="UNKNOWN", description="SEAL | HOLD | STOP | ERROR | DEFER")
    errors: list[str] = Field(default_factory=list, description="Error messages, if any")
    learnings: list[str] = Field(
        default_factory=list, description="Actionable insights for other agents"
    )
    duration_ms: int = Field(default=0, description="Wall-clock time spent")
    token_estimate: int = Field(default=0, description="Approximate tokens consumed")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Extra context (repo, branch, files touched)"
    )

    def to_nats_subject(self) -> str:
        """Routing subject for NATS publication."""
        return f"agent.memory.{self.agent_id}"
