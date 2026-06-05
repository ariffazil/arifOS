"""Agent Bridge — cross-agent memory bus over NATS JetStream.

Allows Kimi, Claude, Copilot, Codex, Aider, Continue, Gemini
to share telemetry without filesystem collision.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

from agent_bridge.models import AgentTelemetry
from agent_bridge.publisher import TelemetryPublisher
from agent_bridge.consumer import TelemetryConsumer

__all__ = ["AgentTelemetry", "TelemetryPublisher", "TelemetryConsumer"]
