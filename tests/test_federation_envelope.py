"""
tests/test_federation_envelope.py — Workstream 9: Kernel-to-Organ Bridge Repair
════════════════════════════════════════════════════════════════════════════════

Tests the ``federation_envelope`` module for:
  1. Envelope construction with full identity/authority/governance context
  2. Injection into call arguments without dropping existing identity
  3. DEGRADED_CLAIM structure (what, where, evidence, usable, next)
  4. Direct-vs-bridged parity comparison (bridge rule 5)
  5. Response finalization with hash and provenance

Bridge rules tested:
  R1: No authority upgrade across the bridge
  R2: No identity substitution
  R3: No dropping the governing session
  R4: No organ result as kernel evidence without provenance
  R5: Direct and bridged calls with same payload must be comparable
  R6: DEGRADED_CLAIM must name what, where, evidence, usable, next

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from arifosmcp.federation.federation_envelope import (
    FEDERATION_ENVELOPE_VERSION,
    build_degraded_claim,
    build_federation_envelope,
    check_bridge_parity,
    compute_request_hash,
    compute_response_hash,
    finalize_response_envelope,
    inject_envelope_into_call_args,
    attach_degraded_claim,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Envelope construction
# ═══════════════════════════════════════════════════════════════════════════════


def test_envelope_construction_minimal():
    """Bridge rule R2/R3: minimal envelope must carry identity and session."""
    env = build_federation_envelope(
        actor_id="test-agent",
        session_id="sess-minimal-001",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
    )
    assert env["__federation_envelope_version"] == FEDERATION_ENVELOPE_VERSION
    assert env["caller"]["actor_id"] == "test-agent"
    assert env["caller"]["identity_verified"] is False
    assert env["session"]["session_id"] == "sess-minimal-001"
    assert env["session"]["authority"] == "OBSERVE_ONLY"
    assert env["request"]["target_organ"] == "WELL"
    assert env["request"]["target_tool"] == "well_health_check"
    assert env["request"]["request_hash"] is not None
    assert len(env["governance"]["trace_id"]) > 0
    # R3: session_id must not be dropped
    assert env["session"]["session_id"] != ""


def test_envelope_construction_full():
    """Full envelope with authority, scope, and governance context."""
    env = build_federation_envelope(
        actor_id="ariffazil",
        identity_verified=True,
        authority_state={
            "identity": {
                "claimed_actor_id": "ariffazil",
                "sovereign_identity": "ARIF_FAZIL",
                "claim_recognized": True,
                "cryptographically_verified": True,
                "verification_method": "signature",
                "verification_reason": "f13_sovereign",
            },
            "constitutional_role": {"role": "SOVEREIGN", "source": "identity_registry"},
            "runtime_grant": {
                "level": "FULL",
                "source": "session_capability_token",
                "allowed_verbs": [
                    "arif_init",
                    "arif_observe",
                    "arif_think",
                    "arif_route",
                    "arif_forge",
                    "arif_judge",
                    "arif_seal",
                ],
                "mutation_allowed": True,
                "seal_allowed": True,
                "expires_at": "2026-07-13T00:00:00Z",
            },
            "session": {"bound": True, "session_id": "sess-full-001", "actor_bound": True},
            "effective_action_authority": {
                "authorized": True,
                "reason_code": "authorized",
            },
        },
        session_id="sess-full-001",
        session_token="sct_v1.eyJhY3RvciI6ImFyaWZmYXppbCJ9.mock",
        authority="FULL",
        allowed_scope=[
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_forge",
            "arif_judge",
            "arif_seal",
        ],
        intent="test full envelope propagation",
        source_tool="arif_route",
        target_organ="GEOX",
        target_tool="geox_basin_profile",
        evidence_layer="L4",
        reversibility="reversible",
        constitutional_chain_id="cc-full-001",
        trace_id="trace-full-001",
    )

    # R1: No authority upgrade across the bridge
    assert env["session"]["authority"] == "FULL"
    assert env["caller"]["identity_verified"] is True
    assert env["caller"]["authority_state"]["runtime_grant"]["level"] == "FULL"

    # Request context
    assert env["request"]["intent"] == "test full envelope propagation"
    assert env["request"]["source_tool"] == "arif_route"
    assert env["request"]["target_organ"] == "GEOX"
    assert env["request"]["request_hash"] is not None

    # Governance context
    assert env["governance"]["evidence_layer"] == "L4"
    assert env["governance"]["reversibility"] == "reversible"
    assert env["governance"]["constitutional_chain_id"] == "cc-full-001"
    assert env["governance"]["trace_id"] == "trace-full-001"


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Inject into call args
# ═══════════════════════════════════════════════════════════════════════════════


def test_inject_envelope_into_call_args_first():
    """First injection: envelope written fresh with legacy compat fields."""
    env = build_federation_envelope(
        actor_id="test-agent",
        session_id="sess-inject-001",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
    )
    args = inject_envelope_into_call_args({"mode": "health"}, env)
    assert args["_envelope"]["__federation_envelope"] is not None
    assert args["_envelope"]["actor_id"] == "test-agent"
    assert args["_envelope"]["session_id"] == "sess-inject-001"
    assert args["_envelope"]["authority"] == "OBSERVE_ONLY"
    assert args["_envelope"]["evidence_layer"] == "L2"
    # Original call_arg preserved
    assert args.get("mode") == "health"


def test_inject_envelope_into_call_args_merge():
    """Merge preserves previous envelope fields (legacy compat)."""
    env = build_federation_envelope(
        actor_id="test-agent",
        session_id="sess-merge-001",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
    )
    prev_env = {"legacy_field": "old_value", "actor_id": "old-agent"}
    args = inject_envelope_into_call_args({"_envelope": prev_env, "mode": "test"}, env)
    # ws9 field wins
    assert args["_envelope"]["actor_id"] == "test-agent"
    # Legacy compat field preserved
    assert args["_envelope"]["legacy_field"] == "old_value"
    # Federation envelope injected
    assert args["_envelope"]["__federation_envelope"] is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: DEGRADED_CLAIM
# ═══════════════════════════════════════════════════════════════════════════════


def test_build_degraded_claim_minimal():
    """Bridge rule R6: minimal degraded claim."""
    claim = build_degraded_claim()
    assert "degraded_claim" in claim
    dc = claim["degraded_claim"]
    assert dc["what_degraded"] == "unknown degradation"
    assert dc["where_degraded"] == "unknown"
    assert dc["evidence_produced"] is False
    assert dc["result_usable"] is False
    assert dc["next_safe_action"] == "investigate and retry"


def test_build_degraded_claim_full():
    """Bridge rule R6: rich degraded claim with all fields."""
    claim = build_degraded_claim(
        what_degraded="identity_verification_dropped_across_bridge",
        where_degraded="WELL_bridge_dispatch",
        evidence_produced=True,
        result_usable=False,
        next_safe_action="retry_with_explicit_session_id_and_actor_id",
        detail={"bridge_session_id": "sess-001", "bridge_actor_id": None},
    )
    dc = claim["degraded_claim"]
    assert dc["what_degraded"] == "identity_verification_dropped_across_bridge"
    assert dc["where_degraded"] == "WELL_bridge_dispatch"
    assert dc["evidence_produced"] is True
    assert dc["result_usable"] is False
    assert dc["next_safe_action"] == "retry_with_explicit_session_id_and_actor_id"
    assert dc["detail"]["bridge_session_id"] == "sess-001"


def test_attach_degraded_claim_to_response():
    """Attach degraded claim to existing response dict (idempotent)."""
    response = {"status": "error", "result": {}}
    attach_degraded_claim(
        response,
        what_degraded="organ_unreachable",
        where_degraded="GEOX_bridge_dispatch",
        evidence_produced=False,
        result_usable=False,
        next_safe_action="check_geox_health",
    )
    assert "degraded_claim" in response
    assert response["degraded_claim"]["what_degraded"] == "organ_unreachable"

    # Idempotent: second attach does not overwrite
    attach_degraded_claim(
        response,
        what_degraded="SHOULD_NOT_OVERWRITE",
        where_degraded="SHOULD_NOT",
        evidence_produced=True,
        result_usable=True,
        next_safe_action="SHOULD_NOT",
    )
    assert response["degraded_claim"]["what_degraded"] == "organ_unreachable"


# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Response finalization
# ═══════════════════════════════════════════════════════════════════════════════


def test_finalize_response_envelope_clean():
    """Finalize stamps response hash, organ status, provenance."""
    env = build_federation_envelope(
        actor_id="test-agent",
        session_id="sess-resp-001",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
    )
    result = {"status": "healthy", "well_score": 78.0, "bandwidth": "NORMAL"}
    finalized = finalize_response_envelope(
        result,
        env,
        organ_status="healthy",
        provenance="well_mcp_via_bridge",
    )
    # R4: provenance must be present
    assert finalized["response"]["provenance"] == "well_mcp_via_bridge"
    assert finalized["response"]["organ_status"] == "healthy"
    assert finalized["response"]["degradation"] is None
    assert len(finalized["response"]["response_hash"]) == 24
    # Request hash echoed for parity check
    assert finalized["response"]["request_hash"] == env["request"]["request_hash"]
    # Target info echoed
    assert finalized["response"]["target_organ"] == "WELL"
    assert finalized["response"]["target_tool"] == "well_health_check"


def test_finalize_response_envelope_degraded():
    """Finalize with degradation block."""
    env = build_federation_envelope(
        actor_id="test-agent",
        session_id="sess-resp-002",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
    )
    degradation = build_degraded_claim(
        what_degraded="partial_response",
        where_degraded="WELL_health_check",
        evidence_produced=True,
        result_usable=True,
        next_safe_action="evaluate_partial_result",
    )["degraded_claim"]
    result = {"status": "degraded", "well_score": 45.0}
    finalized = finalize_response_envelope(
        result,
        env,
        organ_status="degraded",
        provenance="well_mcp_via_bridge",
        degradation=degradation,
    )
    assert finalized["response"]["organ_status"] == "degraded"
    assert finalized["response"]["degradation"] is not None
    assert finalized["response"]["degradation"]["what_degraded"] == "partial_response"
    assert finalized["response"]["degradation"]["result_usable"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: Hash functions
# ═══════════════════════════════════════════════════════════════════════════════


def test_request_hash_deterministic():
    """Same tool_name + arguments = same hash (bridge rule R5)."""
    h1 = compute_request_hash("well_health_check", {"mode": "health"})
    h2 = compute_request_hash("well_health_check", {"mode": "health"})
    assert h1 == h2

    # Different arguments = different hash
    h3 = compute_request_hash("well_health_check", {"mode": "readiness"})
    assert h1 != h3


def test_response_hash():
    """Response hash is deterministic."""
    h1 = compute_response_hash({"status": "healthy", "score": 78})
    h2 = compute_response_hash({"status": "healthy", "score": 78})
    assert h1 == h2
    h3 = compute_response_hash({"status": "degraded", "score": 45})
    assert h1 != h3


# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: Direct-vs-bridged parity (bridge rule R5)
# ═══════════════════════════════════════════════════════════════════════════════


def test_parity_equal():
    """Bridge rule R5: direct and bridged results with same payload are comparable."""
    direct = {"status": "healthy", "ok": True, "well_score": 78.0}
    bridged = {
        "status": "healthy",
        "ok": True,
        "well_score": 78.0,
        "_envelope_echo": {"actor_id": "test", "session_id": "s1", "response_hash": "abc123"},
    }
    result = check_bridge_parity(direct, bridged)
    assert result["parity"] is True
    assert result["bridged_has_identity"] is True


def test_parity_mismatch():
    """Bridge rule R5: different results are flagged."""
    direct = {"status": "healthy", "ok": True, "well_score": 78.0}
    bridged = {"status": "degraded", "ok": False, "well_score": 45.0}
    result = check_bridge_parity(direct, bridged)
    assert result["parity"] is False
    assert len(result["mismatches"]) > 0


def test_parity_numerical_tolerance():
    """Numerical differences within tolerance are acceptable."""
    direct = {"status": "healthy", "well_score": 78.0}
    bridged = {"status": "healthy", "well_score": 78.05, "_envelope_echo": {"session_id": "s1"}}
    result = check_bridge_parity(direct, bridged, tolerance=0.1)
    assert result["parity"] is True


def test_parity_missing_identity():
    """Bridge rule R2/R3: bridged result missing identity fails parity."""
    direct = {"status": "healthy", "ok": True}
    bridged = {"status": "healthy", "ok": True}
    result = check_bridge_parity(direct, bridged)
    # bridged_has_identity is False because no _envelope_echo
    assert result["bridged_has_identity"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# Test 7: Bridge rules enforcement
# ═══════════════════════════════════════════════════════════════════════════════


def test_bridge_rule_1_no_authority_upgrade():
    """R1: authority_state in envelope must never exceed session authority."""
    env = build_federation_envelope(
        actor_id="anonymous",
        session_id="sess-anon-001",
        authority="OBSERVE_ONLY",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
    )
    # Even with identity_verified=False, the envelope authority is OBSERVE_ONLY
    assert env["session"]["authority"] == "OBSERVE_ONLY"
    # The authority_state must reflect same band
    auth_state = env["caller"]["authority_state"]
    assert auth_state["runtime_grant"]["level"] == "OBSERVE_ONLY"
    assert auth_state["runtime_grant"]["mutation_allowed"] is False


def test_bridge_rule_4_provenance_required():
    """R4: every bridged result must have provenance."""
    env = build_federation_envelope(
        actor_id="test-agent",
        session_id="sess-prov-001",
        source_tool="arif_bridge_connect",
        target_organ="WELL",
        target_tool="well_health_check",
    )
    result = finalize_response_envelope(
        {"status": "healthy"},
        env,
        organ_status="healthy",
        provenance="well_mcp_via_bridge",
    )
    assert result["response"]["provenance"] == "well_mcp_via_bridge"


def test_bridge_rule_6_degraded_claim_structure():
    """R6: DEGRADED_CLAIM must name what, where, evidence, usable, next."""
    dc = build_degraded_claim(
        what_degraded="test degradation",
        where_degraded="test location",
        evidence_produced=True,
        result_usable=False,
        next_safe_action="test action",
    )["degraded_claim"]
    required_fields = {
        "what_degraded",
        "where_degraded",
        "evidence_produced",
        "result_usable",
        "next_safe_action",
    }
    assert required_fields.issubset(dc.keys()), f"Missing fields: {required_fields - dc.keys()}"
    assert dc["what_degraded"] == "test degradation"
    assert dc["where_degraded"] == "test location"
    assert dc["evidence_produced"] is True
    assert dc["result_usable"] is False
    assert dc["next_safe_action"] == "test action"
