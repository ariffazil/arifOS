"""
arifOS Sovereign Fabric — Trace Context (Wajib Layer 12)
════════════════════════════════════════════════════════

Every action gets a trace_id that follows it through the entire pipeline.
This is the reality replay membrane — you can reconstruct what happened.

OpenTelemetry-compatible trace context, adapted for constitutional governance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ── Trace Context ──────────────────────────────────────────────────────


@dataclass
class TraceContext:
    """
    A trace context that follows an action through the federation.

    Compatible with OpenTelemetry Trace Context format.
    Every MCP tool call, every organ routing, every verdict gets a span.
    """

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:32])
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: Optional[str] = None
    actor_id: str = ""
    session_id: str = ""
    tool_name: str = ""
    action_class: str = ""
    verdict: str = ""  # PROCEED / HOLD / SABAR / VOID
    organ: str = ""  # arifOS / GEOX / WEALTH / WELL / A-FORGE
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = "ok"  # ok / error / hold / void
    attributes: dict[str, Any] = field(default_factory=dict)

    def finish(self, status: str = "ok", verdict: str = "") -> None:
        """Mark span as finished."""
        self.end_time = time.time()
        self.status = status
        if verdict:
            self.verdict = verdict

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Serialize for logging/receipt."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "tool_name": self.tool_name,
            "action_class": self.action_class,
            "verdict": self.verdict,
            "organ": self.organ,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
        }

    def to_w3c_traceparent(self) -> str:
        """
        W3C Trace Context format:
        {version}-{trace-id}-{parent-id}-{trace-flags}
        """
        flags = "01" if self.status == "ok" else "00"
        return f"00-{self.trace_id}-{self.span_id}-{flags}"


# ── Trace Collector ────────────────────────────────────────────────────


class TraceCollector:
    """
    Collects trace spans for the current session.
    Writes to file for persistence and VAULT999 sealing.
    """

    def __init__(self, output_dir: str = "/tmp/arifos-traces"):
        self.spans: list[TraceContext] = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def start_span(
        self,
        tool_name: str,
        actor_id: str = "",
        session_id: str = "",
        action_class: str = "",
        organ: str = "",
        parent_span_id: Optional[str] = None,
        attributes: Optional[dict[str, Any]] = None,
    ) -> TraceContext:
        """Start a new trace span."""
        ctx = TraceContext(
            tool_name=tool_name,
            actor_id=actor_id,
            session_id=session_id,
            action_class=action_class,
            organ=organ,
            parent_span_id=parent_span_id,
            attributes=attributes or {},
        )
        self.spans.append(ctx)
        return ctx

    def finish_span(
        self,
        ctx: TraceContext,
        status: str = "ok",
        verdict: str = "",
    ) -> None:
        """Finish a span and record it."""
        ctx.finish(status=status, verdict=verdict)

    def get_trace(self, trace_id: str) -> list[TraceContext]:
        """Get all spans for a given trace_id."""
        return [s for s in self.spans if s.trace_id == trace_id]

    def flush(self, session_id: str = "") -> str:
        """Write all spans to a JSONL file. Returns file path."""
        filename = f"trace-{session_id or 'session'}-{int(time.time())}.jsonl"
        filepath = self.output_dir / filename
        with open(filepath, "a") as f:
            for span in self.spans:
                f.write(json.dumps(span.to_dict()) + "\n")
        count = len(self.spans)
        self.spans.clear()
        return str(filepath)

    def summary(self) -> dict[str, Any]:
        """Quick summary of collected traces."""
        if not self.spans:
            return {"spans": 0}
        total_ms = sum(s.duration_ms for s in self.spans)
        verdicts = {}
        for s in self.spans:
            v = s.verdict or "pending"
            verdicts[v] = verdicts.get(v, 0) + 1
        return {
            "spans": len(self.spans),
            "total_ms": round(total_ms, 2),
            "verdicts": verdicts,
            "actors": list(set(s.actor_id for s in self.spans if s.actor_id)),
            "organs": list(set(s.organ for s in self.spans if s.organ)),
        }


# ── Singleton Collector ────────────────────────────────────────────────

_collector: Optional[TraceCollector] = None


def get_trace_collector() -> TraceCollector:
    """Get or create the singleton trace collector."""
    global _collector
    if _collector is None:
        _collector = TraceCollector()
    return _collector
