"""
envelope.py — CallEnvelope: the contract between SDK and kernel.

The envelope is what every prethink / pretool / posttool / seal
call carries. It's the same shape across all 4 guards.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from arifos.intent import Intent


class CallEnvelope(BaseModel):
    """
    The transport envelope for every SDK ↔ kernel call.

    Same shape across prethink, pretool, posttool, seal. This is
    the lingua franca — agents cannot invent their own shape,
    cannot drift, cannot hide behind partial implementations.
    """

    intent: Intent
    trace_id: str | None = None
    parent_lease_id: str | None = None
    tool_name: str | None = None
    tool_args: dict[str, Any] = Field(default_factory=dict)
    tool_result: Any = None
    taint: str = "UNTRUSTED"  # UNTRUSTED | TRUSTED | VERIFIED
    confidence: float | None = None
    source: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    def to_kernel_payload(self) -> dict[str, Any]:
        """Serialise for transport to arifOS MCP."""
        return {
            "intent": self.intent.model_dump(mode="json"),
            "trace_id": self.trace_id,
            "parent_lease_id": self.parent_lease_id,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "taint": self.taint,
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata,
        }
