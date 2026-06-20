"""
arifOS Observability Layer — OpenTelemetry + agent trace primitives.

Per executive verdict: "High-stakes agents need traceability across tool calls,
state transitions, and external actions. OpenTelemetry gives the base telemetry
standard; agent-specific trace schemas should be added on top."

This package provides:
- otel_tracer.py: OTel tracer init + span helpers
- agent_trace_schema.py: Agent-specific trace schema
- risk_event_schema.py: Risk event telemetry (for arifOS risk floor)
"""

from .agent_trace_schema import AgentTraceSchema
from .otel_tracer import OTelTracer, init_tracer
from .risk_event_schema import RiskEvent

__all__ = ["OTelTracer", "init_tracer", "AgentTraceSchema", "RiskEvent"]
