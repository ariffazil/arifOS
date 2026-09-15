"""
Trace propagation acceptance tests — P0-B Wave 1 (2026-09-16).

Acceptance matrix (scoped SLO — designated governed path):
- Root mint at trusted ingress: UUID trace_id/span_id, parent_span_id = null
- Nested governed calls: children inherit trace_id, link parent
- Async tasks: context propagates by copy-on-create
- Receiver: invalid IDs rejected VISIBLY (never silently replaced)
- Local backend: survives NATS-down without NameError (silent-loss fix)
"""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

import pytest

from arifosmcp.arifos_observability.trace_context import current, span


def _uuid(value) -> UUID:
    return UUID(str(value))


def test_root_span_mints_uuids_and_null_parent():
    with span("arif_judge") as ctx:
        assert _uuid(ctx.trace_id)
        assert _uuid(ctx.span_id)
        assert ctx.parent_span_id is None
    assert current() is None  # resets on exit


def test_nested_child_inherits_trace_and_links_parent():
    with span("arif_init") as root:
        with span("arif_route") as child:
            assert child.trace_id == root.trace_id
            assert child.parent_span_id == root.span_id
            assert child.span_id != root.span_id
        # after child exits, ambient returns to root
        assert current().span_id == root.span_id


def test_sibling_spans_share_trace_and_distinct_ids():
    with span("arif_observe") as outer:
        with span("geox_basin") as s1:
            pass
        with span("wealth_primitive") as s2:
            pass
        assert s1.trace_id == s2.trace_id == outer.trace_id
        assert s1.span_id != s2.span_id
        assert s1.parent_span_id == s2.parent_span_id == outer.span_id


def test_async_task_propagates_context():
    captured = {}

    async def inner():
        ctx = current()
        captured["ctx"] = ctx

    with span("arif_forge") as root:
        asyncio.run(inner())
        assert captured["ctx"].trace_id == root.trace_id


def test_act_sid_is_metadata_not_trace_identity():
    with span("arif_init", act_sid="SEAL-56bfeed611c648dc") as ctx:
        assert ctx.act_sid == "SEAL-56bfeed611c648dc"
        assert str(ctx.trace_id).startswith("SEAL-") is False


def test_invalid_trace_id_rejected_visibly(caplog):
    from arifosmcp.runtime.telemetry import trace_tool_call

    with caplog.at_level(logging.WARNING, logger="arifos.telemetry"):
        trace_tool_call(
            tool_name="unit_test",
            arguments={},
            result={"status": "OK"},
            session_id=None,
            actor_id="333-AGI",
            latency_ms=1.0,
            trace_id="trace_1758000000000_notauuid",  # the P0-B mint format
            span_id=None,
            parent_span_id=None,
        )
    assert "trace_context_rejected" in caplog.text


def test_local_backend_survives_nats_down(monkeypatch):
    """The hoisted parse must never NameError the local path (P0-A disease)."""
    import arifosmcp.runtime.telemetry as tel

    monkeypatch.setattr(tel, "_get_nats", lambda: None)
    monkeypatch.setattr(tel, "_get_langfuse", lambda: None)
    monkeypatch.setattr(tel, "_get_local_backend", lambda: None)

    t = tel.Telemetry()
    # Must not raise — previously NameError'd when NATS was down and
    # _trace/_span/_parent were only initialized inside the NATS branch.
    t.record_tool_call(
        tool="unit_test",
        verdict="OK",
        latency=1.0,
        session_id=None,
        actor_id="333-AGI",
        trace_id="11111111-2222-3333-4444-555555555555",
        span_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    )


def test_dispatcher_module_imports_clean():
    """The dispatcher + wiring imports resolve at runtime (LSP noise ≠ reality)."""
    import arifosmcp.arifos_otel_wiring  # noqa: F401
    import arifosmcp.runtime.telemetry  # noqa: F401

    from arifosmcp.arifos_otel_wiring import tool_span  # noqa: F401

    assert callable(tool_span)
