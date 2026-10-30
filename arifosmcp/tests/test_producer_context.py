#!/usr/bin/env python3
"""producer_context regression suite (2026-10-31, source-delivery mission).

Covers the two-layer law: session card is SESSION context, never per-event
producer identity; fail-closed explicit UNKNOWN; server-mint only (no caller
injection surface); persistence through report_lane row + memory write modes;
trim survival at every verbosity level (incl. UNKNOWN fixture).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, "/root/arifOS")

from arifosmcp.runtime.producer_context import build_producer_context  # noqa: E402
from arifosmcp.runtime.verbosity import trim_for_verbosity  # noqa: E402


def test_two_layer_block_from_actor_card():
    pc = build_producer_context(actor_id="QWEN")
    assert pc["schema"] == "producer-context.v1"
    assert pc["session"]["governance_card_hash"], "card hash must ride the session layer"
    assert pc["production"]["requested_model"] == "glm-5.3"
    # the honest label: session_only, per-invocation evidence explicitly absent
    assert pc["attribution"]["state"] == "session_only"
    assert pc["attribution"]["observed_producer_identity"] is None
    assert "no_per_invocation_identity_evidence" in pc["attribution"]["limitations"]


def test_fail_closed_explicit_unknown():
    pc = build_producer_context(session_id="no-such-sid")
    assert pc["attribution"]["state"] == "unknown"
    assert pc["attribution"]["identity_state"] == "UNKNOWN"
    assert pc["production"]["producer_kind"] == "unknown"
    assert pc["session"]["governance_card_hash"] is None
    assert "no_session_card" in pc["attribution"]["limitations"]


def test_no_caller_injection_surface():
    import inspect

    params = inspect.signature(build_producer_context).parameters
    assert "producer_context" not in params, "callers must not be able to supply a block"


def test_trim_preserves_pc_all_levels_and_unknown_fixture():
    happy = {"status": "OK", "tool": "arif_report",
             "producer_context": build_producer_context(actor_id="QWEN"), "result": {"x": 1}}
    unknown = {"status": "OK", "tool": "arif_report",
               "producer_context": build_producer_context(), "result": {}}  # refusal/UNKNOWN fixture
    for resp in (happy, unknown):
        for level in ("standard", "minimal"):
            trimmed = trim_for_verbosity(dict(resp), level)
            assert "producer_context" in trimmed, f"{level} dropped provenance"
            assert trimmed["producer_context"] == resp["producer_context"], "trim mutated the block"


def test_report_lane_row_persists_block(monkeypatch):
    """The PERSISTED row (not the dry_run projection) carries the block.
    Writer is monkeypatched — no live append (source-delivery rules)."""
    from arifosmcp.runtime import report_lane as rl

    captured: dict = {}
    monkeypatch.setattr(rl, "_append", lambda path, row: captured.update(row=row, path=str(path)))
    pc = build_producer_context(actor_id="QWEN")
    rl.report(
        sender="fi-003", platform="mcp", kind="peer",
        subject="producer-context regression", body="row persistence check",
        verified_actor=False, server_actor="fi-003", producer_context=pc,
    )
    assert captured, "writer never invoked"
    assert captured["row"].get("producer_context") == pc, "persisted row must carry the block"
    assert captured["path"].endswith("inbox.jsonl")


def test_report_lane_legacy_callers_get_null_not_crash():
    from arifosmcp.runtime import report_lane as rl

    row = rl.report(
        sender="legacy", platform="mcp", kind="fyi",
        subject="no pc", body="legacy call without the kwarg",
        dry_run=True,
    )
    assert row.get("producer_context") is None


def test_memory_write_modes_only():
    """remember/revise/attest carry pc; recall must not (lean reads)."""
    src = Path("/root/arifOS/arifosmcp/runtime/megaTools/tool_13_arif_memory.py").read_text()
    assert 'if mode in ("remember", "revise", "attest"):' in src
    assert "producer_context" in src


def test_verbosity_keepset_lists_pc():
    src = Path("/root/arifOS/arifosmcp/runtime/verbosity.py").read_text()
    assert '"producer_context",' in src
    assert '"model_governance",' in src
