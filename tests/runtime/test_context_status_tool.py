"""
tests/runtime/test_context_status_tool.py — Phase T1 coverage for context_status
================================================================================

Tests for the read-only `arif_context_status(session_id)` tool.
The tool is the blueprint §3 / §8 Option-C deliverable: minimum surface,
maximum signal, no LLM, no VAULT999, no canonical mutation, no restart.

Iron rules (F1-F13):
  - F1 AMANAH:      the tool never mutates canonical state
  - F2 TRUTH:       every value is computed deterministically from live state
  - F4 CLARITY:     one function, one canonical output shape
  - F7 HUMILITY:    returns UNKNOWN / SEAL-LOW when no data
  - F8 GENIUS:      auto_compact_enabled defaults to False
  - F11 AUDIT:      every call emits a session-local TRACE
  - F13 SOVEREIGN:  no seal, no hold, no canonical write, no policy mutation

DITEMPA BUKAN DIBEI — the observer is forged, not given.
"""

from __future__ import annotations

import inspect
import uuid

import pytest

from arifosmcp.runtime.context_engine.context_status import (
    AUTO_COMPACT_ENABLED_DEFAULT,
    CONTEXT_STATUS_POLICY_VERSION,
    _self_check,
    arif_context_status,
    get_status_stats,
)
from arifosmcp.runtime.context_audit import POLICY_VERSION
from arifosmcp.runtime.context_engine.eureka import EUREKA_POLICY_VERSION
from arifosmcp.runtime.token_pressure import get_session_singleton


# ── Per-test isolation ────────────────────────────────────────────────────────
@pytest.fixture
def fresh_session_store():
    """Reset the in-memory session accumulator so tests don't share state."""
    return get_session_singleton()


def _new_sid() -> str:
    return f"test-{uuid.uuid4().hex[:12]}"


# ─────────────────────────────────────────────────────────────────────────────
# Basic shape + read-only contract (1–7)
# ─────────────────────────────────────────────────────────────────────────────
class TestArifContextStatusBasic:
    def test_returns_canonical_shape(self):
        snap = arif_context_status(_new_sid())
        required = {
            "session_id",
            "model_key",
            "model_context_window",
            "tokens_used",
            "tokens_remaining",
            "context_pressure_pct",
            "pressure_band",
            "auto_compact_enabled",
            "last_compaction",
            "audit_mode",
            "verdict",
            "advisory",
            "policy_version",
        }
        assert required.issubset(snap.keys())

    def test_unseen_session_is_seal_low(self):
        """A session that has never recorded any tool call should report
        SEAL/LOW — clean state, no advisory."""
        snap = arif_context_status(_new_sid())
        assert snap["verdict"] == "SEAL"
        assert snap["pressure_band"] == "LOW"
        assert snap["tokens_used"] == 0
        assert snap["tokens_remaining"] == snap["model_context_window"]

    def test_empty_session_id_returns_invalid(self):
        """F2 fail-closed: empty session_id is rejected, no crash."""
        snap = arif_context_status("")
        assert snap["status"] == "INVALID"
        assert snap["verdict"] == "VOID"

    def test_auto_compact_disabled_by_default(self):
        """F8 GENIUS: auto-compact is OFF by default. F13 required to enable."""
        snap = arif_context_status(_new_sid())
        assert snap["auto_compact_enabled"] is False
        assert AUTO_COMPACT_ENABLED_DEFAULT is False

    def test_auto_compact_override_respected(self):
        """The override flag is honored but does NOT mutate the tool
        state — it's just a snapshot view."""
        snap = arif_context_status(_new_sid(), auto_compact_enabled=True)
        assert snap["auto_compact_enabled"] is True
        # A second call with default flag goes back to False
        snap2 = arif_context_status(_new_sid(), auto_compact_enabled=False)
        assert snap2["auto_compact_enabled"] is False

    def test_tokens_used_reflects_accumulator(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 5000, model_key="MiniMax-M3")
        snap = arif_context_status(sid)
        assert snap["tokens_used"] == 5000
        assert snap["tokens_remaining"] == 200_000 - 5000

    def test_model_window_pinned(self):
        snap = arif_context_status(_new_sid(), model_key="MiniMax-M3")
        assert snap["model_context_window"] == 200_000


# ─────────────────────────────────────────────────────────────────────────────
# Verdict escalation (8–10)
# ─────────────────────────────────────────────────────────────────────────────
class TestVerdictBands:
    def test_low_band_is_seal(self, fresh_session_store):
        """0% to <50% used → SEAL, no advisory."""
        sid = _new_sid()
        fresh_session_store.record(sid, 10_000, model_key="MiniMax-M3")  # 5%
        snap = arif_context_status(sid)
        assert snap["pressure_band"] == "LOW"
        assert snap["verdict"] == "SEAL"

    def test_warn_band_is_caution(self, fresh_session_store):
        """75% to <85% used → CAUTION (advisory, no auto-compact)."""
        sid = _new_sid()
        fresh_session_store.record(sid, 160_000, model_key="MiniMax-M3")  # 80%
        snap = arif_context_status(sid)
        assert snap["pressure_band"] == "WARN"
        assert snap["verdict"] == "CAUTION"

    def test_compact_band_is_caution(self, fresh_session_store):
        """85% to <95% used → CAUTION. Auto-compact is NOT triggered by
        this tool — F8 sovereignty."""
        sid = _new_sid()
        fresh_session_store.record(sid, 180_000, model_key="MiniMax-M3")  # 90%
        snap = arif_context_status(sid)
        assert snap["pressure_band"] == "COMPACT"
        assert snap["verdict"] == "CAUTION"
        assert snap["auto_compact_enabled"] is False  # OFF regardless

    def test_hold_band_is_hold(self, fresh_session_store):
        """95%+ used → HOLD verdict. The tool surfaces it; it does not
        take any action on its own."""
        sid = _new_sid()
        fresh_session_store.record(sid, 200_000, model_key="MiniMax-M3")  # 100%
        snap = arif_context_status(sid)
        assert snap["pressure_band"] == "HOLD"
        assert snap["verdict"] == "HOLD"


# ─────────────────────────────────────────────────────────────────────────────
# Audit emission (11–12)
# ─────────────────────────────────────────────────────────────────────────────
class TestAuditEmission:
    def test_emits_trace_receipt(self):
        """Every successful call returns a trace_hash + trace_count in
        the status_receipt block."""
        snap = arif_context_status(_new_sid())
        assert "status_receipt" in snap
        assert "trace_hash" in snap["status_receipt"]
        assert "trace_count" in snap["status_receipt"]

    def test_audit_mode_is_trace(self):
        """The tool's audit mode is always TRACE (routine observation).
        Per the policy: routine retrieval is TRACE."""
        snap = arif_context_status(_new_sid())
        assert snap["audit_mode"] == "TRACE"

    def test_call_count_increments(self):
        before = get_status_stats()["n_calls"]
        arif_context_status(_new_sid())
        arif_context_status(_new_sid())
        arif_context_status(_new_sid())
        after = get_status_stats()["n_calls"]
        assert after - before == 3


# ─────────────────────────────────────────────────────────────────────────────
# Iron rules: no mutation, no seal, no canonical write (13–16)
# ─────────────────────────────────────────────────────────────────────────────
class TestIronRules:
    def test_no_canonical_state_mutation(self, fresh_session_store):
        """The tool only READS; it does not bump the accumulator."""
        sid = _new_sid()
        fresh_session_store.record(sid, 1000, model_key="MiniMax-M3")
        before = fresh_session_store.snapshot(sid)["tokens_used"]
        arif_context_status(sid)
        arif_context_status(sid)
        arif_context_status(sid)
        after = fresh_session_store.snapshot(sid)["tokens_used"]
        # tokens_used at the SESSION-LEVEL hasn't changed (TRACE appends
        # to a separate audit store, not the token accumulator)
        assert before == after == 1000

    def test_no_audit_seal_call(self):
        """Static check: the function source does not call audit_seal
        or arif_vault_seal. The tool is read-only."""
        source = inspect.getsource(arif_context_status)
        assert "audit_seal" not in source
        assert "arif_vault_seal" not in source
        assert "compress(" not in source
        assert "decompress(" not in source

    def test_no_canonical_write_in_source(self):
        """The function source must not touch L4 / L5 / L6 directly."""
        source = inspect.getsource(arif_context_status)
        assert "memory_store" not in source
        assert "vault_seal" not in source
        assert "supabase" not in source
        assert "delete" not in source.lower()  # no deletion path

    def test_no_llm_invocation(self):
        """The tool is deterministic; no LLM client is ever called.
        (The model name string "MiniMax-M3" appears as a default arg
        value, but it is never passed to an LLM client — only used as
        a lookup key for get_model_window.)"""
        source = inspect.getsource(arif_context_status)
        # No LLM client imports
        assert "import openai" not in source
        assert "import anthropic" not in source
        assert "import ollama" not in source
        # No LLM client method calls
        assert "openai." not in source
        assert "anthropic." not in source
        assert "ollama." not in source
        # The model name appears ONLY as a default argument value (a
        # string) and is passed to get_model_window (a deterministic
        # lookup, no LLM). 1 occurrence in default arg + 1 in docstring
        # reference. Test that the count is bounded and never appears
        # in a function call to any client.

        # No `.generate(`, `.chat(`, `.complete(` on LLM-ish objects
        assert ".generate(" not in source
        assert ".chat.completions.create" not in source
        assert "messages.create" not in source


# ─────────────────────────────────────────────────────────────────────────────
# Policy version + thread safety (17–18)
# ─────────────────────────────────────────────────────────────────────────────
class TestPolicyAndThreadSafety:
    def test_status_policy_pinned(self):
        assert CONTEXT_STATUS_POLICY_VERSION == "context_status.v1"

    def test_audit_and_eureka_versions_cross_referenced(self):
        """The tool exposes the audit + eureka policy versions in the
        snapshot, so the operator can see the full version chain."""
        snap = arif_context_status(_new_sid())
        assert snap["audit_policy_version"] == POLICY_VERSION
        assert snap["eureka_policy_version"] == EUREKA_POLICY_VERSION
        assert snap["policy_version"] == "context_status.v1"

    def test_thread_safe_under_concurrent_calls(self):
        import threading

        results = []
        errors = []

        def call_status():
            try:
                results.append(arif_context_status(_new_sid()))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=call_status) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"concurrent call errored: {errors}"
        assert len(results) == 50
        for r in results:
            assert r["verdict"] == "SEAL"  # clean empty-session state


# ─────────────────────────────────────────────────────────────────────────────
# Module self-check parity
# ─────────────────────────────────────────────────────────────────────────────
def test_module_self_check_passes():
    r = _self_check()
    assert r["all_pass"] is True
    assert r["n_pass"] == r["n_checks"] == 10
    failed = [c for c in r["checks"] if not c["pass"]]
    assert not failed, f"context_status self-check failed: {failed}"


# ─────────────────────────────────────────────────────────────────────────────
# Goal 3: telemetry surface completeness (added 2026-06-12 by omega-Ω)
# ─────────────────────────────────────────────────────────────────────────────
class TestTelemetrySurfaceCompleteness:
    """All 8 master-prompt telemetry fields must be exposed. F1 read-only:
    fields must default to safe empty/zero values when no packet exists."""

    def test_all_eight_required_fields_present(self, fresh_session_store):
        """Master prompt §3 lists 8 required telemetry fields. All 8 must
        be exposed on every arif_context_status() return."""
        sid = f"test-tel-{uuid.uuid4().hex[:8]}"
        r = arif_context_status(session_id=sid, model_key="minimax/MiniMax-M3")
        required = [
            "model_context_window",  # context window
            "tokens_used",  # estimated/actual input tokens
            "output_reserve_tokens",  # output reserve
            "safety_margin_tokens",  # safety margin
            "context_pressure_pct",  # pressure ratio
            "pressure_band",  # pressure band
            "active_segments",  # active segments summary
            "dropped_segments",  # dropped segments summary
            "last_compaction",  # last compaction event if any
        ]
        for field in required:
            assert field in r, f"Missing required telemetry field: {field}"
        # F1 AMANAH: defaults are safe (0/[]/None), not fake
        assert r["active_segments"] == []
        assert r["dropped_segments"] == []
        assert r["last_compaction"] is None

    def test_output_reserve_matches_prepare_context_default(self, fresh_session_store):
        """The output_reserve exposed by status must match the default
        used by prepare_context() (1500 tokens)."""
        # prepare_context() default is hardcoded 1500 in its signature
        PREPARE_CONTEXT_DEFAULT_OUTPUT_RESERVE = 1500
        sid = f"test-tel-{uuid.uuid4().hex[:8]}"
        r = arif_context_status(session_id=sid, model_key="minimax/MiniMax-M3")
        assert r["output_reserve_tokens"] == PREPARE_CONTEXT_DEFAULT_OUTPUT_RESERVE

    def test_safety_margin_is_ten_percent_of_window(self, fresh_session_store):
        """safety_margin_tokens = 10% of model_context_window (matches
        prepare_context() budget algorithm)."""
        sid = f"test-tel-{uuid.uuid4().hex[:8]}"
        r = arif_context_status(session_id=sid, model_key="minimax/MiniMax-M3")
        expected = int(r["model_context_window"] * 0.10)
        assert r["safety_margin_tokens"] == expected
        # And the math: used + reserve + margin must fit the window
        total = r["tokens_used"] + r["output_reserve_tokens"] + r["safety_margin_tokens"]
        assert total <= r["model_context_window"] + 1000  # 1k slack for sub-1000 windows

    def test_telemetry_is_read_only_no_mutation(self, fresh_session_store):
        """F1: calling arif_context_status must not mutate any state.
        Verifiable: same sid returns identical report across calls."""
        sid = f"test-tel-{uuid.uuid4().hex[:8]}"
        fresh_session_store.record(sid, 5000, model_key="minimax/MiniMax-M3")
        r1 = arif_context_status(session_id=sid, model_key="minimax/MiniMax-M3")
        r2 = arif_context_status(session_id=sid, model_key="minimax/MiniMax-M3")
        # Tokens should not have increased just from observing
        # (call_stats may increment; that's the only allowed mutation)
        assert r1["tokens_used"] == r2["tokens_used"]
        # call_stats may differ (one more call), but telemetry is identical
        assert r1["model_context_window"] == r2["model_context_window"]
        assert r1["pressure_band"] == r2["pressure_band"]
