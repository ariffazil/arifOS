"""
Cross-Organ SCT Propagation — Delegation Escape Fix (Vector #7)

Verifies SCT propagates through cross-organ routing. Before this fix,
session_token was dropped in the transport envelope, causing
GEOX/WEALTH/WELL to default to OBSERVE_ONLY regardless of caller authority.

Invariants:
  1. session_token → appears in transport _envelope + federation envelope
  2. OBSERVE_ONLY session → OBSERVE_ONLY at ALL organs (no escalation)
  3. Agent blocked at arifOS cannot route with laxest organ gate

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest


def _fed_env(**kw) -> dict:
    """Build a federation envelope."""
    from arifosmcp.federation.federation_envelope import build_federation_envelope

    defaults = dict(
        actor_id="test-actor",
        identity_verified=True,
        session_id="SEAL-test",
        session_token=None,
        authority="OBSERVE_ONLY",
        source_tool="arif_route",
        target_organ="GEOX",
        target_tool="test_tool",
        constitutional_chain_id="SEAL-test",
    )
    defaults.update(kw)
    return build_federation_envelope(**defaults)


def _inject(args: dict, envelope: dict) -> dict:
    from arifosmcp.federation.federation_envelope import inject_envelope_into_call_args

    return inject_envelope_into_call_args(args, envelope)


# ── Test 1: SCT embedding ──────────────────────────────────────────────────


class TestSCTEnvelopeEmbedding:
    def test_sct_embedded_in_federation_envelope(self):
        env = _fed_env(session_token="act_v1.eyJhdXRo.abc123")
        assert env["session"]["session_token"] == "act_v1.eyJhdXRo.abc123"

    def test_missing_sct_yields_empty_string_not_crash(self):
        env = _fed_env(session_token=None)
        assert env["session"]["session_token"] == ""

    def test_authority_band_preserved(self):
        env = _fed_env(authority="OBSERVE_ONLY", session_token="act_v1.test")
        assert env["session"]["authority"] == "OBSERVE_ONLY"


# ── Test 2: SCT injection propagation ──────────────────────────────────────


class TestSCTInjectionPropagation:
    def test_sct_carried_through_inject_envelope(self):
        args = _inject({"mode": "test"}, _fed_env(session_token="act_v1.prop"))
        assert args["_envelope"]["session_token"] == "act_v1.prop"

    def test_existing_envelope_preserved_on_injection(self):
        args = _inject(
            {"_envelope": {"prior": "keep", "session_id": "old"}},
            _fed_env(session_token="act_v1.new"),
        )
        e = args["_envelope"]
        assert e["prior"] == "keep"
        assert e["session_token"] == "act_v1.new"
        assert e["session_id"] == "SEAL-test"  # federation wins


# ── Test 3: Authority parity across organs ─────────────────────────────────


class TestCrossOrganAuthorityParity:
    def test_observe_only_to_geox(self):
        env = _fed_env(authority="OBSERVE_ONLY", session_token="act_v1.o")
        assert env["session"]["authority"] == "OBSERVE_ONLY"
        rt = env["caller"]["authority_state"]["runtime_grant"]
        assert rt["mutation_allowed"] is False
        assert rt["seal_allowed"] is False

    def test_observe_only_to_wealth(self):
        env = _fed_env(
            authority="OBSERVE_ONLY",
            session_token="act_v1.w",
            target_organ="WEALTH",
            target_tool="capital_diagnose",
        )
        assert env["session"]["authority"] == "OBSERVE_ONLY"

    def test_observe_only_to_well(self):
        env = _fed_env(
            authority="OBSERVE_ONLY",
            session_token="act_v1.wl",
            target_organ="WELL",
            target_tool="well_classify_substrate",
        )
        assert env["session"]["authority"] == "OBSERVE_ONLY"

    def test_full_session_propagates_full_to_organ(self):
        env = _fed_env(authority="FULL", session_token="act_v1.full")
        assert env["session"]["authority"] == "FULL"


# ── Test 4: No organ gate laxity escape ────────────────────────────────────


class TestNoOrganGateLaxityEscape:
    def test_observe_only_cannot_escalate_via_organ_route(self):
        env = _fed_env(authority="OBSERVE_ONLY", session_token="act_v1.blocked")
        args = _inject({"authority_ceiling": "FULL", "authority_band": "FULL"}, env)
        fed = args["_envelope"]["__federation_envelope"]
        assert fed["session"]["authority"] == "OBSERVE_ONLY", (
            "Agent cannot escalate OBSERVE_ONLY → FULL via organ route"
        )

    def test_caller_arguments_cannot_override_session_authority(self):
        from arifosmcp.federation.federation_envelope import build_federation_envelope

        env = build_federation_envelope(
            actor_id="blocked-agent",
            identity_verified=True,
            session_id="SEAL-blocked",
            session_token="act_v1.blocked",
            authority="OBSERVE_ONLY",
            source_tool="arif_route",
            target_organ="WEALTH",
            target_tool="capital_wisdom",
        )
        assert env["session"]["authority"] == "OBSERVE_ONLY"
        rt = env["caller"]["authority_state"]["runtime_grant"]
        assert rt["level"] == "OBSERVE_ONLY", (
            f"Runtime grant must be OBSERVE_ONLY, got {rt['level']}"
        )
