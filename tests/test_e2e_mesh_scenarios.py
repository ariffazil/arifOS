"""
End-to-End Mesh Scenario Tests — Full Governed Pipeline + E7 + Registry
════════════════════════════════════════════════════════════════════════

Adversarial scenarios that exercise the complete governed substrate:
anonymous atomic actions, reversible chains into irreversible outcomes,
agent loop detection, E7 autonomy contraction, principal override path.

These are the tests the external analysis identified as missing.
Each test simulates a real agent attack/error and verifies the
governance pipeline + E7 + tool risk registry respond correctly.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations


from arifosmcp.runtime.governance_pipeline import (
    GovernancePipeline,
    PipelineVerdict,
    Gate,
    ToolCallContext,
)
from arifosmcp.runtime.principal_paradox import (
    evaluate_autonomy_ceiling,
    AutonomyTier,
    GateVerdict,
    MAX_OVERRIDES_PER_HOUR,
)
from arifosmcp.runtime.tool_risk_registry import (
    classify_tool,
)


# ═══════════════════════════════════════════════════════════════
# SCENARIO 1: Anonymous Atomic Action → BLOCKED
# ═══════════════════════════════════════════════════════════════


def test_anonymous_vault_seal_blocked():
    """Anonymous actor attempts VAULT999 seal — must be blocked at Gate 1 (Identity)."""
    pipeline = GovernancePipeline(principal_paradox_enabled=True)
    ctx = ToolCallContext(
        tool_name="arif_vault_seal",
        session_id="s1",
        actor_id="anonymous",
        actor_verification="claimed",
        action_class="ATOMIC",
        risk_tier="ATOMIC",
    )
    result = pipeline.run(ctx)
    assert result.verdict == PipelineVerdict.HOLD
    assert result.blocked_at == Gate.IDENTITY
    assert "Anonymous actor cannot execute ATOMIC" in result.reasons[0]


def test_anonymous_observe_allowed():
    """Anonymous actor observes — should PASS through all gates."""
    pipeline = GovernancePipeline(
        principal_paradox_enabled=True,
        f0_rootkey_enabled=False,
        f13_gate_enabled=False,
    )
    ctx = ToolCallContext(
        tool_name="arif_sense_observe",
        session_id="s2",
        actor_id="anonymous",
        action_class="OBSERVE",
        risk_tier="LOW",
        caller_has_lease=True,
    )
    result = pipeline.run(ctx)
    assert result.verdict == PipelineVerdict.PASS
    # Verify E7 gate was reached
    assert any(g.gate == Gate.PRINCIPAL_PARADOX for g in result.gate_results)


# ═══════════════════════════════════════════════════════════════
# SCENARIO 2: Agent Escalation Chain — Reversible → Irreversible
# ═══════════════════════════════════════════════════════════════


def test_chain_reversible_to_irreversible():
    """Agent chains reversible actions into effectively irreversible outcome.

    Pattern: memory_store (reversible) → forge_execute engineer (borderline)
    → vault_seal (irreversible). The chain should trip E7 as reversibility drops.
    """
    pipeline = GovernancePipeline(
        principal_paradox_enabled=True,
        f0_rootkey_enabled=False,
        f13_gate_enabled=False,
        vault_liveness_enabled=False,  # vault probe unavailable in test env
        envelope_enabled=False,  # test env — no federation envelopes
    )

    # Step 1: Memory store (reversible, MEDIUM)
    ctx1 = ToolCallContext(
        tool_name="arif_memory_recall",
        session_id="chain-1",
        actor_id="agent-7",
        actor_verification="verified",
        action_class="MUTATE",
        risk_tier="MEDIUM",
        params={"mode": "store"},
        caller_has_lease=True,
    )
    r1 = pipeline.run(ctx1)
    assert r1.verdict in (PipelineVerdict.PASS, PipelineVerdict.WARN)
    e7_1 = [g for g in r1.gate_results if g.gate == Gate.PRINCIPAL_PARADOX][0]
    assert e7_1.metadata.get("e7_verdict") in ("PROCEED", "SABAR")

    # Step 2: Forge engineer (MUTATE, HIGH, borderline reversibility)
    ctx2 = ToolCallContext(
        tool_name="arif_forge_execute",
        session_id="chain-1",
        actor_id="agent-7",
        actor_verification="verified",
        action_class="MUTATE",
        risk_tier="HIGH",
        blast_radius="PUBLIC",
        reversibility=0.4,
        params={"mode": "engineer"},
        caller_has_lease=True,
    )
    r2 = pipeline.run(ctx2)
    e7_2 = [g for g in r2.gate_results if g.gate == Gate.PRINCIPAL_PARADOX][0]
    # Should be at least PROPOSE_ONLY
    assert e7_2.metadata.get("autonomy_tier") in (
        "PRINCIPAL_APPROVAL_REQUIRED",
        "PROPOSE_ONLY",
        "HOLD",
    ), f"Expected escalation, got {e7_2.metadata.get('autonomy_tier')}"

    # Step 3: Vault seal (ATOMIC, irreversible) — should HOLD
    ctx3 = ToolCallContext(
        tool_name="arif_vault_seal",
        session_id="chain-1",
        actor_id="agent-7",
        actor_verification="verified",
        action_class="IRREVERSIBLE",
        risk_tier="ATOMIC",
        blast_radius="PUBLIC",
        reversibility=0.0,
        caller_has_lease=True,
    )
    r3 = pipeline.run(ctx3)
    e7_3 = [g for g in r3.gate_results if g.gate == Gate.PRINCIPAL_PARADOX][0]
    assert e7_3.metadata.get("e7_verdict") == "HOLD"
    assert e7_3.metadata.get("autonomy_tier") == "HOLD"


# ═══════════════════════════════════════════════════════════════
# SCENARIO 3: E7 Autonomy Contraction Under Rising Risk
# ═══════════════════════════════════════════════════════════════


def test_autonomy_contracts_as_risk_expands():
    """Verify the core E7 thesis: autonomy shrinks as risk grows."""
    # Low risk, local blast, fully reversible → FULL_AUTO
    tier, _, _ = evaluate_autonomy_ceiling(
        action_class="OBSERVE",
        risk_tier="LOW",
        blast_radius="LOCAL",
        reversibility=1.0,
        caller_has_lease=True,
    )
    assert tier == "FULL_AUTO"

    # Medium risk, federation blast, 0.5 reversible → PRINCIPAL_APPROVAL_REQUIRED
    tier2, _, _ = evaluate_autonomy_ceiling(
        action_class="MUTATE",
        risk_tier="MEDIUM",
        blast_radius="PUBLIC",
        reversibility=0.5,
        caller_has_lease=True,
    )
    assert tier2 == "PRINCIPAL_APPROVAL_REQUIRED"

    # High risk, external blast, 0.3 reversible → HOLD
    tier3, _, _ = evaluate_autonomy_ceiling(
        action_class="IRREVERSIBLE",
        risk_tier="HIGH",
        blast_radius="CIVILIZATIONAL",
        reversibility=0.3,
        caller_has_lease=True,
    )
    assert tier3 == "HOLD"


def test_autonomy_full_contraction_table():
    """Every row in the 16-row contract table maps correctly."""
    from arifosmcp.runtime.principal_paradox import AUTONOMY_CONTRACTION

    for risk, blast, rev_floor, expected_tier in AUTONOMY_CONTRACTION:
        tier, rationale, envelope = evaluate_autonomy_ceiling(
            action_class="MUTATE",
            risk_tier=risk.value,
            blast_radius=blast.value,
            reversibility=rev_floor,  # exactly at floor
            caller_has_lease=True,
        )
        # At the exact floor value, should get the expected tier
        assert tier == expected_tier.value, (
            f"Row ({risk.value}, {blast.value}, {rev_floor}): "
            f"expected {expected_tier.value}, got {tier}. {rationale}"
        )


# ═══════════════════════════════════════════════════════════════
# SCENARIO 4: Tool Risk Registry Accuracy
# ═══════════════════════════════════════════════════════════════


def test_all_13_canonical_tools_classified():
    """Every canonical tool has at least a base risk profile."""
    canonical = [
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
    ]
    for tool in canonical:
        profile = classify_tool(tool, {})
        assert profile.tool_name == tool
        assert profile.action_class in (
            "OBSERVE",
            "ANALYZE",
            "DRAFT",
            "MUTATE",
            "IRREVERSIBLE",
            "PREPARE",
        )
        assert profile.risk_tier in ("LOW", "MEDIUM", "HIGH", "ATOMIC")
        assert profile.blast_radius in (
            "LOCAL",
            "ACCOUNT",
            "ORG",
            "PUBLIC",
            "MARKET",
            "INFRASTRUCTURE",
            "CIVILIZATIONAL",
        )
        assert 0.0 <= profile.reversibility <= 1.0


def test_forge_mode_classification():
    """arif_forge_execute modes map to correct risk profiles."""
    # Query → OBSERVE, safe
    p = classify_tool("arif_forge_execute", {"mode": "query"})
    assert p.action_class == "OBSERVE"
    assert p.risk_tier == "LOW"
    assert p.autonomy_floor == "FULL_AUTO"

    # Dry run → ANALYZE, safe
    p = classify_tool("arif_forge_execute", {"mode": "dry_run"})
    assert p.action_class == "ANALYZE"
    assert p.autonomy_floor == "FULL_AUTO"

    # Engineer → MUTATE, needs principal
    p = classify_tool("arif_forge_execute", {"mode": "engineer"})
    assert p.action_class == "MUTATE"
    assert p.autonomy_floor == "PRINCIPAL_APPROVAL_REQUIRED"

    # Deploy → IRREVERSIBLE, HOLD
    p = classify_tool("arif_forge_execute", {"mode": "deploy"})
    assert p.action_class == "IRREVERSIBLE"
    assert p.autonomy_floor == "HOLD"


def test_dangerous_mode_aliases():
    """Dangerous aliases map to conservative classifications."""
    aliases = {
        "write": "MUTATE",
        "generate": "MUTATE",
        "build": "MUTATE",
        "mutate": "MUTATE",
        "execute": "IRREVERSIBLE",
        "apply": "IRREVERSIBLE",
        "push": "IRREVERSIBLE",
    }
    for alias, expected_class in aliases.items():
        p = classify_tool("arif_forge_execute", {"mode": alias})
        assert p.action_class == expected_class, (
            f"Alias '{alias}' → {p.action_class}, expected {expected_class}"
        )


# ═══════════════════════════════════════════════════════════════
# SCENARIO 5: Simulation Mode — Log, Don't Block
# ═══════════════════════════════════════════════════════════════


def test_simulation_mode_logs_but_does_not_block():
    """In simulate mode, E7 evaluates fully but never hard-blocks."""
    pipeline = GovernancePipeline(
        principal_paradox_enabled=True,
        enforcement_mode="simulate",
    )
    ctx = ToolCallContext(
        tool_name="arif_vault_seal",
        session_id="sim-1",
        actor_id="agent-7",
        actor_verification="verified",
        action_class="IRREVERSIBLE",
        risk_tier="ATOMIC",
        blast_radius="PUBLIC",
        reversibility=0.0,
        caller_has_lease=True,
    )
    result = pipeline.run(ctx)
    e7_gates = [g for g in result.gate_results if g.gate == Gate.PRINCIPAL_PARADOX]
    assert len(e7_gates) > 0, "E7 gate must have been executed"
    e7 = e7_gates[0]
    assert e7.passed == True, "Simulate mode: E7 must pass"
    assert e7.metadata.get("enforcement_mode") == "simulate"
    assert e7.metadata.get("shadow_verdict") is not None
    assert e7.metadata.get("would_have_blocked") == True


def test_enforce_mode_blocks():
    """In enforce mode, E7 hard-blocks atomic actions."""
    pipeline = GovernancePipeline(
        principal_paradox_enabled=True,
        f0_rootkey_enabled=False,
        f13_gate_enabled=False,
        enforcement_mode="enforce",
    )
    ctx = ToolCallContext(
        tool_name="arif_vault_seal",
        session_id="enf-1",
        actor_id="agent-7",
        actor_verification="verified",
        action_class="IRREVERSIBLE",
        risk_tier="ATOMIC",
        blast_radius="PUBLIC",
        reversibility=0.0,
        caller_has_lease=True,
    )
    result = pipeline.run(ctx)
    e7_gates = [g for g in result.gate_results if g.gate == Gate.PRINCIPAL_PARADOX]
    assert len(e7_gates) > 0, "E7 gate must have been executed"
    e7 = e7_gates[0]
    # In enforce mode, E7 should HOLD this
    assert e7.metadata.get("e7_verdict") == "HOLD"
    assert e7.passed == False


# ═══════════════════════════════════════════════════════════════
# SCENARIO 6: Principal Override Path
# ═══════════════════════════════════════════════════════════════


def test_principal_direct_always_full_auto():
    """Principal (F13) always gets FULL_AUTO regardless of risk."""
    # Even IRREVERSIBLE + CIVILIZATIONAL + irreversible → FULL_AUTO for principal
    tier, rationale, envelope = evaluate_autonomy_ceiling(
        action_class="IRREVERSIBLE",
        risk_tier="ATOMIC",
        blast_radius="CIVILIZATIONAL",
        reversibility=0.0,
        caller_is_principal=True,
    )
    assert tier == "FULL_AUTO"
    assert envelope.get("principal_direct") == True


def test_no_lease_always_hold():
    """Without an active lease, even LOW risk is HOLD."""
    tier, rationale, envelope = evaluate_autonomy_ceiling(
        action_class="OBSERVE",
        risk_tier="LOW",
        blast_radius="LOCAL",
        reversibility=1.0,
        caller_has_lease=False,
    )
    assert tier == "HOLD"
    assert envelope.get("violation") == "NO_LEASE"


def test_surge_protection_downgrades():
    """When override count exceeds max, autonomy downgrades."""
    tier, rationale, envelope = evaluate_autonomy_ceiling(
        action_class="MUTATE",
        risk_tier="MEDIUM",
        blast_radius="ORG",
        reversibility=0.7,
        caller_has_lease=True,
        prior_override_count=MAX_OVERRIDES_PER_HOUR,  # at limit
    )
    # Should be downgraded one tier from FULL_AUTO → PROPOSE_ONLY
    assert tier in ("PROPOSE_ONLY", "PRINCIPAL_APPROVAL_REQUIRED", "HOLD")
    assert envelope.get("surge_active") == True


# ═══════════════════════════════════════════════════════════════
# SCENARIO 7: E7 Clause Enforcement
# ═══════════════════════════════════════════════════════════════


def test_scope_enforcement_glob_patterns():
    """Clause 1 — fnmatch glob patterns work correctly."""
    from arifosmcp.runtime.principal_paradox import enforce_scope

    # Wildcard matches everything
    ok, _ = enforce_scope({"tool_name": "anything_at_all"}, ["*"])
    assert ok

    # Prefix glob
    ok, _ = enforce_scope({"tool_name": "arif_sense_observe"}, ["arif_sense_*"])
    assert ok

    # Multiple globs
    ok, _ = enforce_scope(
        {"tool_name": "arif_mind_reason"}, ["arif_sense_*", "arif_mind_*", "arif_heart_*"]
    )
    assert ok

    # Out of scope
    ok, reason = enforce_scope({"tool_name": "arif_forge_execute"}, ["arif_sense_*", "arif_mind_*"])
    assert not ok
    assert "outside declared policy scope" in reason

    # Exact match
    ok, _ = enforce_scope({"tool_name": "arif_vault_seal"}, ["arif_vault_seal"])
    assert ok


def test_attestation_receipt_completeness():
    """Clause 3 — attestation receipts contain all required fields."""
    from arifosmcp.runtime.principal_paradox import emit_attestation

    receipt = emit_attestation(
        intent="seal ROOTKEY_SPEC_v54",
        inputs_hash="abc123def456",
        risk_trigger="IRREVERSIBLE+PUBLIC",
        autonomy_tier="PRINCIPAL_APPROVAL_REQUIRED",
        approval_decision="SABAR",
        approving_authority="arifOS-kernel",
        principal_override_occurred=False,
    )
    assert receipt.receipt_hash.startswith("sha256:")
    assert receipt.intent == "seal ROOTKEY_SPEC_v54"
    assert receipt.inputs_hash == "abc123def456"
    assert receipt.autonomy_tier_at_execution == AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED
    assert receipt.approval_decision == GateVerdict.SABAR
    assert receipt.principal_override_occurred == False


# ═══════════════════════════════════════════════════════════════
# SCENARIO 8: Agent Loop → Behavior Sink Detection
# ═══════════════════════════════════════════════════════════════


def test_repeated_identical_calls_detected():
    """Repeated identical MUTATE calls from same agent should trigger budget gate."""
    pipeline = GovernancePipeline(
        principal_paradox_enabled=True,
        f0_rootkey_enabled=False,
        f13_gate_enabled=False,
        max_same_tool_calls=2,
        vault_liveness_enabled=False,  # vault probe unavailable in test env
        floor_enabled=False,  # test env — floor L01 requires ack_irreversible param
        envelope_enabled=False,  # test env — no federation envelopes
    )
    ctx = ToolCallContext(
        tool_name="arif_forge_execute",
        session_id="loop-1",
        actor_id="agent-7",
        actor_verification="verified",
        action_class="MUTATE",
        risk_tier="HIGH",
        blast_radius="PUBLIC",
        reversibility=0.5,
        params={"mode": "engineer"},
        caller_has_lease=True,
    )

    # First call — should pass E7 (or SABAR)
    r1 = pipeline.run(ctx)
    assert r1.verdict in (PipelineVerdict.PASS, PipelineVerdict.WARN)

    # Second call — still within budget
    r2 = pipeline.run(ctx)
    assert r2.verdict in (PipelineVerdict.PASS, PipelineVerdict.WARN)

    # Third call — exceeds max_same_tool_calls (2) → HOLD at Budget gate
    r3 = pipeline.run(ctx)
    assert r3.verdict == PipelineVerdict.HOLD
    assert r3.blocked_at == Gate.BUDGET
    assert any("max_same_tool_calls" in reason for reason in r3.reasons)


# ═══════════════════════════════════════════════════════════════
# SCENARIO 9: Cross-Organ Risk Escalation
# ═══════════════════════════════════════════════════════════════


def test_gateway_connect_federation_blast():
    """Gateway routing carries PUBLIC blast radius."""
    p = classify_tool("arif_gateway_connect", {"mode": "route"})
    assert p.blast_radius == "PUBLIC"
    assert p.risk_tier == "MEDIUM"


def test_judge_deliberate_requires_principal_for_binding():
    """Binding judgment (mode=judge) requires principal approval."""
    p = classify_tool("arif_judge_deliberate", {"mode": "judge"})
    assert p.autonomy_floor == "PRINCIPAL_APPROVAL_REQUIRED"
    assert p.risk_tier == "HIGH"


# ═══════════════════════════════════════════════════════════════
# SCENARIO 10: /000 + /999 Surface Completeness
# ═══════════════════════════════════════════════════════════════


def test_000_surface_completeness():
    """The /000 autonomy surface exposes all required parameters."""
    from arifosmcp.runtime.principal_paradox import build_000_autonomy_surface

    surface = build_000_autonomy_surface("test-session")
    policy = surface["autonomy_policy"]
    assert "max_tier" in policy
    assert "automatic_approval_threshold" in policy
    assert "surge_protection_max_overrides_per_hour" in policy
    assert "reversibility_hard_floor" in policy
    assert "contract_version" in policy
    assert len(surface["hold_conditions"]) >= 5


def test_999_surface_completeness():
    """The /999 proof chamber exposes execution evidence."""
    from arifosmcp.runtime.principal_paradox import build_999_execution_surface

    surface = build_999_execution_surface(
        seal_id="SEAL:test-001",
        action_class="MUTATE",
        risk_tier="HIGH",
        approving_authority="arif",
        principal_override_occurred=True,
        evidence_hash="sha256:abc123",
        chain_position=42,
        autonomy_tier="PRINCIPAL_APPROVAL_REQUIRED",
        e7_gate_passed=False,
    )
    seal = surface["last_seal"]
    assert seal["seal_id"] == "SEAL:test-001"
    assert seal["principal_override_occurred"] == True
    assert seal["chain_position"] == 42
    assert seal["e7_gate_passed"] == False
    assert surface["surge_status"] in ("NORMAL", "SURGE")
