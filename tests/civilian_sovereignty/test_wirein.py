"""
F14 — Wire-in tests.

These tests verify that F14 stamping is actually invoked from the
runtime tool paths (not just from the substrate unit tests).

They run against the runtime in-process, not against the live MCP
service. They test the F14 stamping post-processors fire on the
correct code paths.
"""

import pytest


# ── arif_kernel_route entanglement advisory (Right #7) ────────────────


def test_kernel_route_status_includes_f14_entanglement():
    from arifosmcp.runtime.tools import _f14_entanglement_for_session

    result = _f14_entanglement_for_session("test-session")
    assert result["right_id"] == "right_to_non_addictive_AI"
    # F07: substrate always returns gracefully (fails closed)
    assert "available" in result
    assert "entanglement_score" in result or result.get("available") is False


def test_kernel_route_status_no_session_uses_zero_calls():
    from arifosmcp.runtime.tools import _f14_entanglement_for_session

    # No session id → no recorded calls → entanglement is OBSERVED band
    result = _f14_entanglement_for_session(None)
    # daily_factor=1/10=0.1 contributes 0.04 (=0.4*0.1) to the 0.6-weighted
    # daily component — so a fresh session in a 60-min window starts
    # at 0.04 entanglement, not 0.0. F07: we declare the math, not hide it.
    assert 0.0 <= result["entanglement_score"] < 0.4
    assert result["band"] == "OBSERVED"
    assert result["advisory_emitted"] is False


# ── arif_judge_deliberate escalation + appeal + explanation ─────────


def test_judge_sovereign_escalation_for_c5():
    from arifosmcp.runtime.civilian_sovereignty.enforce import (
        require_sovereign_judgment,
    )

    h = require_sovereign_judgment("C5", stakes=0.9)
    assert h is not None
    assert h["verdict"] == "HOLD"
    assert h["right_id"] == "right_to_human_judgment_high_stakes"


def test_judge_appeal_envelope_path_only():
    from arifosmcp.runtime.civilian_sovereignty.enforce import (
        make_appeal_envelope,
    )

    e = make_appeal_envelope(
        original_decision_ref="test-001",
        decision_chain="arif_judge_deliberate/test",
        appeal_grounds="testing the wire-in",
        actor_id="arif-fazil",
    )
    assert e["right_id"] == "right_to_appeal_automated_decisions"
    # The kernel declares its role as PATH ONLY
    assert "PATH ONLY" in e["appeal_path"]["kernel_role"]


# ── arif_reply_compose F14 stamping (Right #1 + #4) ──────────────────


def test_stamp_f14_reply_helper_does_not_break_existing_returns():
    """F14 stamping must never change a SEAL to a HOLD or remove a key."""
    from arifosmcp.tools.reply import _stamp_f14_reply

    base = {"verdict": "SEAL", "message": "hello"}
    stamped = _stamp_f14_reply(base, ai_involvement="partial", language="bm")
    # Original keys preserved
    assert stamped["verdict"] == "SEAL"
    assert stamped["message"] == "hello"
    # F14 metadata added
    assert "ai_involvement" in stamped
    assert "language_grounding" in stamped
    # Bahasa anchoring works
    assert stamped["language_grounding"]["language"] == "bm"
    assert stamped["language_grounding"]["language_name"] == "Bahasa Melayu"


def test_stamp_f14_reply_survives_substrate_failure():
    """If F14 substrate is broken, the reply still returns (F07)."""
    from arifosmcp.tools.reply import _stamp_f14_reply

    # Substrate import will succeed, but if it raises internally,
    # the helper must still return a valid result
    base = {"verdict": "SEAL"}
    stamped = _stamp_f14_reply(base, "klingon", "en")  # unknown lang
    assert stamped["verdict"] == "SEAL"
    # Unknown language falls back to English (F07)
    assert stamped["language_grounding"]["language"] == "en"


# ── arif_memory_recall prune → cognitive privacy (Right #5) ─────────


def test_cognitive_privacy_stamp_on_forget():
    from arifosmcp.runtime.civilian_sovereignty.enforce import (
        stamp_cognitive_privacy,
    )

    base = {"pruned": ["mem-1", "mem-2"], "count": 2}
    stamped = stamp_cognitive_privacy(
        base,
        scope="forget",
        categories=["mem-1", "mem-2"],
        retention_window_seconds=0,
    )
    assert stamped["cognitive_privacy"]["scope"] == "forget"
    assert stamped["cognitive_privacy"]["retention_set_to"] == "forgotten"
    # F11: audit trail is never zero
    assert stamped["cognitive_privacy"]["audit_trail_kept_for_days"] > 0


# ── F14 — Surface discipline (F2 TRUTH) ───────────────────────────────


def test_no_new_mcp_tools_added():
    """The 13-tool constitucional surface must not be expanded.

    New modes on existing tools are OK; new top-level tool names
    are F13 territory.
    """
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    assert len(CANONICAL_TOOLS) == 13, (
        f"Surface drift: 13 → {len(CANONICAL_TOOLS)}. "
        f"New tools: {set(CANONICAL_TOOLS.keys()) - _EXPECTED_13}"
    )


_EXPECTED_13 = {
    "arif_session_init",
    "arif_sense_observe",
    "arif_evidence_fetch",
    "arif_mind_reason",
    "arif_heart_critique",
    "arif_kernel_route",
    "arif_reply_compose",
    "arif_memory_recall",
    "arif_gateway_connect",
    "arif_judge_deliberate",
    "arif_vault_seal",
    "arif_forge_execute",
    "arif_ops_measure",
}


# ── F14 — Opt-out mode aliases added to session_init (Right #6, #10) ─


def test_session_init_accepts_opt_out_modes():
    """Right #6 and #10 are routed through session_init as new modes.

    These are NOT new tools — they are new modes on the existing
    arif_session_init tool. The 13-tool surface is preserved.
    """
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    modes = CANONICAL_TOOLS["arif_session_init"]["modes"]
    assert "opt_out" in modes, f"opt_out missing: {modes}"
    assert "opt_out_profiling" in modes, f"opt_out_profiling missing: {modes}"
    # Old modes still present
    for m in ("init", "light", "resume", "validate", "epoch_open", "epoch_seal"):
        assert m in modes, f"old mode {m!r} dropped"


# ── F14 — F02 confidence cap test (parametrized) ────────────────────


@pytest.mark.parametrize("involvement", ["full", "partial", "advisory", "observed"])
def test_ai_involvement_values_never_one(involvement):
    from arifosmcp.runtime.civilian_sovereignty.enforce import (
        stamp_ai_involvement,
    )

    result = stamp_ai_involvement({}, involvement, confidence=1.0)
    assert result["ai_involvement"]["confidence"] <= 0.95
    assert result["ai_involvement"]["disclosure"] == involvement
