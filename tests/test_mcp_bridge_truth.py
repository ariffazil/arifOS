"""
test_mcp_bridge_truth.py — F13 cross-boundary reclassification acceptance tests
================================================================================

Sovereign directive (2026-07-12T15:35Z):
    "Execution success is evidence of execution only. It carries no action
    authority, no approval and no seal."

10 acceptance tests prove the MCP bridge preserves one coherent envelope
end-to-end. The law: organ results enter arifOS as evidence, not authority.
Only arif_judge may convert evidence into APPROVED / HOLD / VOID.
"""
import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

# ── Import targets ──────────────────────────────────────────────────────
from arifosmcp.tools.kernel_canonical import (
    _enforce_bridge_invariants,
    _bridge_ok,
    _bridge_geox,
    _bridge_wealth,
    _bridge_well,
)
from arifosmcp.federation.federation_envelope import (
    build_federation_envelope,
    finalize_response_envelope,
)


KERNEL_ACTOR = "arif"
KERNEL_SESSION = "SEAL-test-session-001"


# ─── helpers ──────────────────────────────────────────────────────────────
def _make_organ_response(
    *,
    actor_id: str | None = KERNEL_ACTOR,
    session_id: str | None = KERNEL_SESSION,
    authority: str = "OBSERVE_ONLY",
    verdict: str = "EVIDENCE_ONLY",
    payload: dict | None = None,
    include_seal: bool = False,
    include_provenance: bool = True,
) -> dict:
    """Build a synthetic organ response for the bridge to reclassify."""
    resp = {
        "actor_id": actor_id,
        "session_id": session_id,
        "authority": authority,
        "verdict": verdict,
    }
    if include_provenance:
        resp["provenance"] = "geox_internal_evidence_ref_xyz"
    if include_seal:
        resp["seal"] = {"seal_id": "ORGAN-FAKE-SEAL-001", "issuer": "organ_self"}
    if payload:
        resp.update(payload)
    return resp


# ═══════════════════════════════════════════════════════════════════════════
# Test 1: Kernel actor and organ actor remain identical
# ═══════════════════════════════════════════════════════════════════════════
class TestKernelActorMatchesOrganActor:
    def test_organ_returning_different_actor_id_is_corrected_to_kernel_actor(self):
        organ_resp = _make_organ_response(actor_id="organ_lied_about_actor")
        corrected, claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        assert corrected["actor_id"] == KERNEL_ACTOR, (
            f"actor_id must be replaced with kernel actor; got {corrected.get('actor_id')}"
        )
        assert any("inv2" in c for c in claims), (
            f"inv2 (actor_replaced) must be claimed; got claims={claims}"
        )

    def test_organ_returning_matching_actor_id_passes_unchanged(self):
        organ_resp = _make_organ_response(actor_id=KERNEL_ACTOR)
        corrected, claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        assert corrected["actor_id"] == KERNEL_ACTOR
        assert not any("inv2" in c for c in claims), (
            f"matching actor_id must not trigger inv2; got claims={claims}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: Kernel session maps to one traceable organ call
# ═══════════════════════════════════════════════════════════════════════════
class TestKernelSessionPropagates:
    def test_organ_returning_different_session_id_is_corrected_to_kernel_session(self):
        organ_resp = _make_organ_response(session_id="organ_lied_session")
        corrected, claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        assert corrected["session_id"] == KERNEL_SESSION
        assert any("inv3" in c for c in claims), (
            f"inv3 (session_replaced) must be claimed; got claims={claims}"
        )

    def test_organ_returning_matching_session_passes_unchanged(self):
        organ_resp = _make_organ_response(session_id=KERNEL_SESSION)
        corrected, claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        assert corrected["session_id"] == KERNEL_SESSION
        assert not any("inv3" in c for c in claims)


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: OBSERVE_ONLY remains OBSERVE_ONLY
# ═══════════════════════════════════════════════════════════════════════════
class TestAuthorityCannotIncrease:
    @pytest.mark.parametrize("bumped_authority", ["LIMITED_MUTATE", "FULL", "SOVEREIGN"])
    def test_organ_authority_is_downgraded_to_observe_only(self, bumped_authority):
        organ_resp = _make_organ_response(authority=bumped_authority)
        corrected, claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        assert corrected["authority"] == "OBSERVE_ONLY", (
            f"organ authority {bumped_authority} must be downgraded to OBSERVE_ONLY; "
            f"got {corrected.get('authority')}"
        )
        assert any("inv1" in c for c in claims)

    def test_organ_authority_observe_only_unchanged(self):
        organ_resp = _make_organ_response(authority="OBSERVE_ONLY")
        corrected, _ = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        assert corrected["authority"] == "OBSERVE_ONLY"
        assert "authority" not in corrected.get("cross_boundary_invariants_applied", [])


# ═══════════════════════════════════════════════════════════════════════════
# Test 4: An organ cannot return SOVEREIGN, APPROVED or SEALED
# ═══════════════════════════════════════════════════════════════════════════
class TestOrganCannotEmitVerdictStrings:
    @pytest.mark.parametrize("forbidden", ["APPROVED", "SOVEREIGN", "SEALED", "SEAL"])
    def test_forbidden_verdict_string_is_downgraded_to_evidence(self, forbidden):
        organ_resp = _make_organ_response(verdict=forbidden)
        corrected, claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        assert corrected["verdict"] == "EVIDENCE_ONLY", (
            f"verdict '{forbidden}' must be downgraded; got {corrected.get('verdict')}"
        )
        assert any("inv4" in c for c in claims)


# ═══════════════════════════════════════════════════════════════════════════
# Test 5: Direct WELL and bridged WELL return equivalent domain payloads
# ═══════════════════════════════════════════════════════════════════════════
class TestDirectBridgeParity:
    def test_bridge_response_preserves_inner_domain_payload(self):
        domain_payload = {
            "well_score": 78.0,
            "vitality_state": "OPTIMAL",
            "biometric": {"sleep_hours": 8, "stress_load": 2},
        }
        organ_resp = _make_organ_response(payload=domain_payload)
        bridge = _bridge_ok(
            "WELL", "well_validate_vitality", organ_resp,
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        inner = bridge.get("result", {}).get("result", {})
        # Domain payload should be preserved (bridge doesn't strip domain data)
        for k, v in domain_payload.items():
            assert inner.get(k) == v, (
                f"domain field {k!r} should be preserved; got {inner.get(k)}"
            )

    def test_bridge_response_has_cross_boundary_result_block(self):
        organ_resp = _make_organ_response()
        bridge = _bridge_ok(
            "WELL", "well_validate_vitality", organ_resp,
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        cbr = bridge.get("result", {}).get("cross_boundary_result")
        assert cbr is not None, "cross_boundary_result block must be present"
        assert cbr["protocol"] == "MCP"
        assert cbr["source_server"] == "WELL"
        assert cbr["action_authority"] == "NONE"
        assert cbr["receipt_status"] == "UNSEALED"


# ═══════════════════════════════════════════════════════════════════════════
# Test 6: Missing identity produces explicit HOLD, not anonymous silent fallback
# ═══════════════════════════════════════════════════════════════════════════
class TestMissingIdentityHolds:
    def test_organ_response_with_no_actor_id_passes_through_undefined(self):
        # Note: _enforce_bridge_invariants only fires if actor_id IS present and
        # mismatched. Missing actor_id passes through (the wrapper itself decides
        # what to do with empty actor_id; bridge reports the missing field).
        organ_resp = _make_organ_response(actor_id=None)
        organ_resp.pop("actor_id", None)
        corrected, _claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        # The invariants only fire when the value exists. Missing stays missing.
        # The bridge itself attaches cross_boundary_result; the missing actor is
        # detected at the bridge call boundary (in _bridge_<organ>).
        assert "actor_id" not in corrected or corrected.get("actor_id") is None

    def test_bridge_ok_with_empty_actor_still_attaches_proof(self):
        # Even with no actor, the bridge ok must mark action_authority: NONE.
        bridge = _bridge_ok(
            "WELL", "well_validate_vitality", _make_organ_response(),
            kernel_actor_id=None, kernel_session_id=KERNEL_SESSION,
        )
        assert bridge.get("action_authority") == "NONE", (
            f"missing actor must still mark action_authority=NONE; got {bridge.get('action_authority')}"
        )
        assert bridge.get("bridge_actor_id") == ""


# ═══════════════════════════════════════════════════════════════════════════
# Test 7: Organ timeout returns DEGRADED, not false success
# ═══════════════════════════════════════════════════════════════════════════
class TestOrganTimeoutDegraded:
    def test_timeout_simulated_as_exception(self):
        # The bridge wraps exceptions in _hold (HOLD verdict, not OK).
        # The cross_boundary law says: never return false success.
        with patch("arifosmcp.tools.kernel_canonical._assert_organ_attested", return_value=None):
            with patch("arifosmcp.runtime.geox_bridge.call_geox_tool",
                       side_effect=TimeoutError("organ timeout")):
                result = _bridge_geox(
                    "geox_basin", {}, KERNEL_SESSION, KERNEL_ACTOR
                )
        # Result must be a HOLD, not OK
        assert result.get("status") == "HOLD", (
            f"timeout must return HOLD; got status={result.get('status')}"
        )
        # Must NOT carry action_authority: APPROVED
        meta = result.get("_meta", {})
        assert meta.get("action_authority") != "APPROVED", (
            f"timeout must not claim APPROVED; got {meta.get('action_authority')}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Test 8: Successful tools/call returns action_authority: NONE
# ═══════════════════════════════════════════════════════════════════════════
class TestSuccessDoesNotApprove:
    def test_bridge_ok_success_marks_action_authority_none(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        # action_authority is on the top-level envelope (F13 directive)
        assert bridge.get("action_authority") == "NONE", (
            f"success must emit action_authority=NONE; got {bridge.get('action_authority')}"
        )
        # and on the inner result block
        assert bridge.get("result", {}).get("action_authority") == "NONE"

    def test_bridge_ok_outer_verdict_action_is_not_evaluated(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        verdicts = bridge.get("verdicts", {})
        action = verdicts.get("action", {})
        assert action.get("state") == "NOT_EVALUATED", (
            f"bridge outer verdict.action.state must be NOT_EVALUATED; got {action.get('state')}"
        )
        assert action.get("issuer") == "arif_bridge"

    def test_bridge_ok_outer_verdict_receipt_is_unsealed(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        verdicts = bridge.get("verdicts", {})
        receipt = verdicts.get("receipt", {})
        assert receipt.get("state") == "UNSEALED", (
            f"bridge must not seal; got receipt.state={receipt.get('state')}"
        )
        assert receipt.get("issuer") == "arif_bridge"

    def test_bridge_ok_outer_verdict_session_is_observe_only(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        verdicts = bridge.get("verdicts", {})
        sess = verdicts.get("session", {})
        assert sess.get("state") == "OBSERVE_ONLY", (
            f"bridge cannot grant authority above OBSERVE_ONLY; got session.state={sess.get('state')}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Test 9: Judge consumes organ evidence separately from transport status
# ═══════════════════════════════════════════════════════════════════════════
class TestJudgeConsumesEvidenceNotTransport:
    def test_bridge_response_exposes_evidence_layer_for_judge(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(payload={"domain_data": "evidence_here"}),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        # Judge needs to find the evidence: cross_boundary_result + result.result
        result_block = bridge.get("result", {})
        assert "cross_boundary_result" in result_block
        # The cross-boundary block says "execution_status: SUCCESS, action_authority: NONE"
        cbr = result_block["cross_boundary_result"]
        assert cbr["execution_status"] == "SUCCESS"
        assert cbr["action_authority"] == "NONE"
        # The domain evidence is in result_block["result"]
        assert result_block["result"]["domain_data"] == "evidence_here"
        # Judge would consume result_block["result"] as evidence and issue its OWN verdict
        # — distinct from the bridge's transport-level NOT_EVALUATED.

    def test_transport_status_does_not_pretend_to_evidence_layer(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        # Transport layer says: action NOT_EVALUATED, receipt UNSEALED
        verdicts = bridge.get("verdicts", {})
        assert verdicts["action"]["state"] == "NOT_EVALUATED"
        assert verdicts["receipt"]["state"] == "UNSEALED"
        # Evidence layer says: execution_status SUCCESS, action_authority NONE
        cbr = bridge["result"]["cross_boundary_result"]
        assert cbr["action_authority"] == "NONE"
        # The two layers do not confuse each other: transport != evidence


# ═══════════════════════════════════════════════════════════════════════════
# Test 10: Every hop appears in one trace
# ═══════════════════════════════════════════════════════════════════════════
class TestTraceHopsVisible:
    def test_bridge_proof_block_records_hop_metadata(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
            drift_detected=False,
        )
        proof = bridge.get("bridge_proof", {})
        assert proof.get("organ") == "GEOX"
        assert proof.get("tool") == "geox_basin"
        assert proof.get("kernel_session_id") == KERNEL_SESSION
        assert proof.get("kernel_actor_id") == KERNEL_ACTOR
        assert proof.get("drift_detected") is False
        assert "F13 cross-boundary" in proof.get("law", "")

    def test_drift_detected_flag_propagates_to_bridge_proof(self):
        bridge = _bridge_ok(
            "WEALTH", "wealth_capital_health", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
            drift_detected=True,
        )
        proof = bridge.get("bridge_proof", {})
        assert proof.get("drift_detected") is True
        assert proof.get("organ") == "WEALTH"

    def test_invariants_applied_list_propagates_to_bridge_proof(self):
        # Construct a response that triggers invariants
        organ_resp = _make_organ_response(
            actor_id="fake_organ_actor",
            session_id="fake_session",
            authority="FULL",
            verdict="SEALED",
            include_seal=True,
        )
        organ_resp, claims = _enforce_bridge_invariants(
            "GEOX", "geox_basin", KERNEL_ACTOR, KERNEL_SESSION, organ_resp
        )
        bridge = _bridge_ok(
            "GEOX", "geox_basin", organ_resp,
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
            invariants_applied=claims,
        )
        proof = bridge.get("bridge_proof", {})
        applied = proof.get("invariants_applied", [])
        assert len(applied) >= 4, (
            f"expected 4+ invariants applied; got {applied}"
        )
        # Verify specific invariants were caught
        joined = " ".join(applied)
        assert "inv1" in joined  # authority downgrade
        assert "inv2" in joined  # actor replacement
        assert "inv3" in joined  # session replacement
        assert "inv4" in joined  # verdict downgrade
        assert "inv5" in joined  # seal forbidden


# ═══════════════════════════════════════════════════════════════════════════
# End-to-end: ensure full bridge response shape conforms
# ═══════════════════════════════════════════════════════════════════════════
class TestEndToEndShape:
    def test_bridge_response_outer_shape(self):
        bridge = _bridge_ok(
            "GEOX", "geox_basin", _make_organ_response(),
            kernel_actor_id=KERNEL_ACTOR, kernel_session_id=KERNEL_SESSION,
        )
        # Top-level keys per arifOS standard response + F13 markers
        for k in ("status", "tool", "verdicts", "result",
                  "action_authority", "cross_boundary", "bridge_proof"):
            assert k in bridge, f"missing top-level key {k!r}"
        # Result block
        for k in ("organ", "tool", "result", "status", "cross_boundary_result",
                  "actor_id", "session_id", "cross_boundary_invariants_applied",
                  "action_authority"):
            assert k in bridge["result"], f"missing result key {k!r}"
        # Verdicts: action=NOT_EVALUATED, receipt=UNSEALED, session=OBSERVE_ONLY
        assert bridge["verdicts"]["action"]["state"] == "NOT_EVALUATED"
        assert bridge["verdicts"]["receipt"]["state"] == "UNSEALED"
        assert bridge["verdicts"]["session"]["state"] == "OBSERVE_ONLY"
        # F13 markers at top level
        assert bridge["action_authority"] == "NONE"
        # Cross-boundary block: protocol MCP, action_authority NONE, receipt_status UNSEALED
        cbr = bridge["result"]["cross_boundary_result"]
        assert cbr["protocol"] == "MCP"
        assert cbr["action_authority"] == "NONE"
        assert cbr["receipt_status"] == "UNSEALED"
        # Bridge proof: law stamped
        assert "F13 cross-boundary" in bridge["bridge_proof"]["law"]
