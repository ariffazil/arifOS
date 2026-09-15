"""
Ambient trace context — P0-B caller-side propagation (Wave 1, 2026-09-16).

Fixes the measured P0-B failure: distinct(trace_id) ≈ row count and
parent_span_id = 0.00% across 201,495 observations (OBSERVABILITY_GAP_AUDIT
2026-09-15). Root cause: no caller propagated trace identity, and the one
producer that minted used a non-UUID template (``trace_{ms}_{actor}``) that
the UUID-typed receiver silently dropped.

Contract (TRACE_PROPAGATION_SCHEMA.md v1.0 · UUID-only):

- ``trace_id`` / ``span_id`` / ``parent_span_id`` are UUID4s, serialized
  canonically as strings. No prefixed templates anywhere on the canonical path.
- A root observation carries ``parent_span_id = null`` — never a fabricated value.
- Invalid inbound IDs are rejected VISIBLY by the receiver (structured
  warning) — never silently replaced. The silent replacement WAS the P0-B bug.
- The ACT session id (``sid``) is domain metadata, never a trace_id.

Ownership (minimal correct design):

- Root mint: the dispatcher / trusted ingress (``runtime/tools.py`` wraps
  every governed handler in ``span(tool_name)``).
- Children: ``@trace_tool`` decorators and any nested governed call inherit
  ``trace_id``, mint their own ``span_id``, and link ``parent_span_id`` to
  the active span.
- Cross-task: ContextVars propagate into ``asyncio.create_task`` by
  copy-on-create, so spawned governed work stays linked by default.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator, Optional
from uuid import UUID, uuid4

logger = logging.getLogger("arifos.trace")

__all__ = ["TraceContext", "current", "span"]


@dataclass(frozen=True)
class TraceContext:
    """Immutable trace identity for one governed span."""

    trace_id: UUID
    span_id: UUID
    parent_span_id: Optional[UUID] = None
    actor_id: Optional[str] = None
    act_sid: Optional[str] = None  # ACT session id — metadata, NOT trace identity


_active: ContextVar[Optional[TraceContext]] = ContextVar("arifos_active_trace", default=None)


def current() -> Optional[TraceContext]:
    """Active trace context in this task, or None."""
    return _active.get()


@contextmanager
def span(
    tool_name: str,
    actor_id: Optional[str] = None,
    act_sid: Optional[str] = None,
) -> Iterator[TraceContext]:
    """
    Open one governed span.

    - No active context → this span becomes the ROOT: fresh trace_id,
      parent_span_id = None (honest root — the dispatcher owns this boundary).
    - Active context present → CHILD: inherits trace_id, fresh span_id,
      parent_span_id = active span's id.

    Resets on exit so sibling requests never cross-contaminate.
    """
    parent = _active.get()
    if parent is None:
        ctx = TraceContext(
            trace_id=uuid4(),
            span_id=uuid4(),
            parent_span_id=None,
            actor_id=actor_id,
            act_sid=act_sid,
        )
    else:
        ctx = TraceContext(
            trace_id=parent.trace_id,
            span_id=uuid4(),
            parent_span_id=parent.span_id,
            actor_id=actor_id or parent.actor_id,
            act_sid=act_sid or parent.act_sid,
        )
    token = _active.set(ctx)
    try:
        yield ctx
    finally:
        _active.reset(token)
