"""tests/runtime/test_v2_envelope_strictness.py — 888 ORDER 2026-10-21.

Invariant under test (F13 directive 2026-10-21, item #1):
  The top-level envelope disposition MUST NOT be more lenient than the
  strictest internal component. If any sub-event is HOLD/DEGRADED, or
  blocked_actions carries "claim_success", then:
    - can_claim_success is False
    - output_policy is DOMAIN_HOLD
    - final_verdict reflects the strictest component
  and internal trace states are published SEPARATELY from final_verdict.

Reproduces the contradiction class observed externally 2026-10-21 16:18 MYT
(SABAR + can_claim_success=true + DOMAIN_SEAL + DEGRADED in one payload).

Floors engaged: F2 TRUTH, F3 TRI-WITNESS · DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from arifosmcp.runtime.v2_envelope import (
    _extract_can_claim_success,
    build_v2_envelope,
)


# ── extractor-level invariants ────────────────────────────────────────────


def test_extractor_sabar_explicit_veto():
    """SABAR must be an explicit veto, not a fall-through accident."""
    assert _extract_can_claim_success("SABAR", "COMPLETED", {}) is False


def test_extractor_provisional_explicit_veto():
    assert _extract_can_claim_success("PROVISIONAL", "COMPLETED", {}) is False


def test_extractor_blocked_actions_veto():
    assert (
        _extract_can_claim_success("PROCEED", "COMPLETED", {"blocked_actions": ["claim_success"]})
        is False
    )


def test_extractor_subevent_hold_veto():
    resp = {"sesat_events": [{"verdict": "HOLD", "blocked_actions": ["claim_success"]}]}
    assert _extract_can_claim_success("PROCEED", "COMPLETED", resp) is False


def test_extractor_degraded_substrate_veto():
    resp = {"constitutional_check": {"substrate_state": "DEGRADED"}}
    assert _extract_can_claim_success("PROCEED", "COMPLETED", resp) is False


def test_extractor_clean_proceed_still_true():
    """Clean PROCEED+COMPLETED must keep claiming success (no over-veto)."""
    assert _extract_can_claim_success("PROCEED", "COMPLETED", {}) is True


# ── reducer-level invariants (the exact reported contradiction shape) ─────


def test_envelope_sabar_plus_claim_success_no_contradiction():
    """The externally observed shape: verdict=SABAR + blocked claim_success."""
    resp = {
        "verdict": "SABAR",
        "status": "ok",
        "blocked_actions": ["claim_success"],
        "sesat_events": [{"verdict": "HOLD", "blocked_actions": ["claim_success"]}],
    }
    env = build_v2_envelope("arif_memory", resp)
    assert env["can_claim_success"] is False
    assert env["output_policy"] == "DOMAIN_HOLD"
    assert env["final_verdict"] == "HOLD"


def test_envelope_degraded_state_forbids_lenient_top():
    resp = {
        "status": "ok",
        "constitutional_check": {"substrate_state": "DEGRADED", "hold_required": True},
    }
    env = build_v2_envelope("arif_memory", resp)
    assert env["can_claim_success"] is False
    assert env["output_policy"] == "DOMAIN_HOLD"


def test_envelope_intermediate_states_separated_from_final():
    resp = {"status": "ok", "verdict": "SEAL"}
    env = build_v2_envelope("arif_memory", resp)
    assert "intermediate_trace_states" in env
    assert "final_verdict" in env
    assert env["final_verdict"] == "SEAL"
    # trace states carry the echoes; final carries the authority
    assert "canonical_verdict" in env["intermediate_trace_states"]
    assert "strictness_hits" in env["intermediate_trace_states"]


def test_envelope_handler_preset_true_cannot_survive_strictness():
    """A handler pre-setting can_claim_success=True must not survive (no setdefault hole)."""
    resp = {
        "status": "ok",
        "verdict": "SABAR",
        "can_claim_success": True,
        "blocked_actions": ["claim_success"],
    }
    env = build_v2_envelope("arif_memory", resp)
    assert env["can_claim_success"] is False


def test_collect_strictness_hits_shapes():
    from arifosmcp.runtime.v2_envelope import _collect_strictness_hits

    assert _collect_strictness_hits({}) == []
    hits = _collect_strictness_hits({"blocked_actions": ["claim_success"]})
    assert any("claim_success" in h for h in hits)
    hits = _collect_strictness_hits({"sesat_events": [{"verdict": "DEGRADED"}]})
    assert any("DEGRADED" in h for h in hits)
