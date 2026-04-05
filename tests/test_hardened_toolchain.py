"""
tests/test_hardened_toolchain.py — Hardened Toolchain Tests

Tests for the 11-tool hardened constitutional pipeline with:
- Fail-closed defaults
- Typed contracts (ToolEnvelope)
- Cross-tool trace IDs
- Human decision markers
- Entropy budgets
"""

import asyncio
import pytest

from core.enforcement.auth_continuity import verify_auth_context
from arifosmcp.runtime.contracts_v2 import (
    ToolEnvelope, ToolStatus, RiskTier, HumanDecisionMarker,
    generate_trace_context, calculate_entropy_budget,
)
from arifosmcp.runtime.hardened_toolchain import HardenedToolchain
from arifosmcp.runtime.init_anchor_hardened import HardenedInitAnchor, SessionClass
from arifosmcp.runtime.truth_pipeline_hardened import HardenedRealityCompass, HardenedRealityAtlas
from arifosmcp.runtime.tools_hardened_v2 import (
    HardenedAGIReason, HardenedASICritique,
    HardenedAgentZeroEngineer, HardenedApexJudge, HardenedVaultSeal,
)


class TestInitAnchorContinuity:
    """Regression coverage for F11 continuity bootstrap and rotation."""

    @pytest.mark.asyncio
    async def test_bootstrap_mints_verifiable_auth_context(self):
        tool = HardenedInitAnchor()

        result = await tool.init(
            declared_name="arif",
            requested_scope=["query"],
            risk_tier="low",
            auth_context=None,
            session_id="sess-bootstrap-regression",
            query="bootstrap kernel continuity",
        )

        auth_context = result.auth_context
        assert auth_context is not None
        for field in (
            "token_fingerprint",
            "nonce",
            "iat",
            "exp",
            "approval_scope",
            "signature",
        ):
            assert field in auth_context
        assert "arifOS_kernel:execute_limited" in auth_context["approval_scope"]
        valid, reason = verify_auth_context(result.session_id, auth_context)
        assert valid, reason

    @pytest.mark.asyncio
    async def test_refresh_rotates_auth_context_with_parent_signature(self):
        tool = HardenedInitAnchor()

        initial = await tool.init(
            declared_name="arif",
            requested_scope=["query"],
            risk_tier="low",
            auth_context=None,
            session_id="sess-refresh-regression",
            query="bootstrap refresh continuity",
        )
        refreshed = await tool.refresh(initial.session_id)

        assert refreshed.auth_context is not None
        assert refreshed.auth_context["signature"] != initial.auth_context["signature"]
        assert (
            refreshed.auth_context["parent_signature"]
            == initial.auth_context["signature"]
        )
        valid, reason = verify_auth_context(refreshed.session_id, refreshed.auth_context)
        assert valid, reason

    @pytest.mark.asyncio
    async def test_identity_mismatch_is_not_marked_verified(self):
        tool = HardenedInitAnchor()

        binding = tool._bind_identity(
            model_soul={
                "base_identity": {
                    "provider": "openai",
                    "model_family": "gpt",
                    "model_variant": "gemini-1.5-pro",
                }
            }
        )

        assert binding["verification_status"] == "identity_mismatch"
        assert binding["verified_identity"] is None


class TestFailClosedDefaults:
    """Verify tools fail closed when required fields missing."""

    @pytest.mark.asyncio
    async def test_init_anchor_voids_without_any_intent(self):
        """init_anchor should VOID if no intent/query/raw_input and no name fallback."""
        tool = HardenedInitAnchor()
        result = await tool.init(
            declared_name="anonymous",  # no fallback derivation for anonymous
            risk_tier="medium",
            session_id="test-001",
            auth_context=None,
            # No intent, query, or raw_input provided
        )
        # New behavior: VOID because minimum intent is missing
        assert result.status == ToolStatus.VOID
        assert "missing minimum" in result.payload.get("void_reason", "").lower()

    @pytest.mark.asyncio
    async def test_init_anchor_defers_privileged_without_auth(self):
        """init_anchor should HOLD (deferred) for privileged scope without auth."""
        tool = HardenedInitAnchor()
        result = await tool.init(
            declared_name="user",
            risk_tier="high",
            session_id="test-001a",
            auth_context=None,  # Missing for privileged!
            query="run production deployment",
        )
        # New behavior: HOLD because high-risk requires auth_context
        assert result.status == ToolStatus.HOLD
        assert result.requires_human is True

    @pytest.mark.asyncio
    async def test_init_anchor_auto_mints_session_id(self):
        """init_anchor should auto-mint session_id when absent (tolerant ingress)."""
        tool = HardenedInitAnchor()
        result = await tool.init(
            declared_name="anonymous",
            risk_tier="low",
            session_id=None,  # Absent — should be auto-minted
            auth_context={"actor_id": "test"},
        )
        # New behavior: OK with auto-minted session, not HOLD
        assert result.status == ToolStatus.OK
        assert result.session_id is not None
        assert result.session_id.startswith("sess-")
        assert "session_id" in " ".join(result.payload.get("normalization", {}).get("derived_fields", []))
    
    @pytest.mark.asyncio
    async def test_reality_compass_fails_closed(self):
        """reality_compass should HOLD without auth."""
        tool = HardenedRealityCompass()
        result = await tool.search(
            query="test",
            auth_context=None,
            risk_tier="medium",
            session_id="test-002",
        )
        
        assert result.status == ToolStatus.HOLD
    
    @pytest.mark.asyncio
    async def test_agi_reason_fails_closed(self):
        """agi_reason should HOLD without required fields."""
        tool = HardenedAGIReason()
        result = await tool.reason(
            query="test",
            auth_context=None,
            risk_tier="medium",
            session_id="test-003",
        )
        
        assert result.status == ToolStatus.HOLD


class TestToolEnvelopeStructure:
    """Verify all tools return proper ToolEnvelope structure."""
    
    @pytest.mark.asyncio
    async def test_init_anchor_returns_envelope(self):
        """init_anchor should return ToolEnvelope with all fields."""
        tool = HardenedInitAnchor()
        trace = generate_trace_context("TEST", "sess-001")
        
        result = await tool.init(
            declared_name="arif",
            requested_scope=["query"],
            risk_tier="low",
            auth_context={"actor_id": "arif"},
            session_id="sess-001",
            trace=trace,
        )
        
        # Check envelope structure
        assert isinstance(result, ToolEnvelope)
        assert result.tool == "init_anchor"
        assert result.session_id == "sess-001"
        assert result.inputs_hash is not None
        assert result.outputs_hash is not None
        assert result.evidence_refs is not None
        assert result.trace is not None
        assert result.trace.stage_id == "TEST"
    
    @pytest.mark.asyncio
    async def test_reality_compass_returns_typed_bundle(self):
        """reality_compass should return EvidenceBundle in payload."""
        tool = HardenedRealityCompass()
        trace = generate_trace_context("111_SENSE", "sess-002")
        
        result = await tool.search(
            query="constitutional architecture",
            auth_context={"actor_id": "test"},
            risk_tier="medium",
            session_id="sess-002",
            trace=trace,
        )
        
        assert result.status == ToolStatus.OK
        assert "evidence_bundle" in result.payload
        bundle = result.payload["evidence_bundle"]
        assert bundle["bundle_id"] is not None
        assert bundle["claim_type"] in ["fact", "opinion", "hypothesis", "projection"]
    
    @pytest.mark.asyncio
    async def test_reality_atlas_returns_claim_graph(self):
        """reality_atlas should return claim graph with nodes and edges."""
        compass = HardenedRealityCompass()
        atlas = HardenedRealityAtlas()
        
        trace_111 = generate_trace_context("111_SENSE", "sess-003")
        compass_result = await compass.search(
            query="test query",
            auth_context={"actor_id": "test"},
            risk_tier="medium",
            session_id="sess-003",
            trace=trace_111,
        )
        
        bundle = compass_result.payload["evidence_bundle"]
        
        trace_222 = generate_trace_context("222_ATLAS", "sess-003")
        result = await atlas.merge(
            evidence_bundles=[bundle],
            auth_context={"actor_id": "test"},
            risk_tier="medium",
            session_id="sess-003",
            trace=trace_222,
        )
        
        assert result.status == ToolStatus.OK
        assert "claim_graph" in result.payload
        assert "nodes" in result.payload["claim_graph"]


class TestHumanDecisionMarkers:
    """Verify human decision markers are properly assigned."""
    
    @pytest.mark.asyncio
    async def test_low_risk_auto_machine_recommendation(self):
        """Low risk queries should get machine_recommendation_only."""
        tool = HardenedInitAnchor()
        trace = generate_trace_context("TEST", "sess-004")
        
        result = await tool.init(
            declared_name="user",
            requested_scope=["query"],
            risk_tier="low",
            auth_context={"actor_id": "user"},
            session_id="sess-004",
            trace=trace,
        )
        
        assert result.human_decision == HumanDecisionMarker.MACHINE_RECOMMENDATION_ONLY
    
    @pytest.mark.asyncio
    async def test_destructive_requires_approval(self):
        """Destructive scope should require human approval."""
        tool = HardenedInitAnchor()
        trace = generate_trace_context("TEST", "sess-005")
        
        result = await tool.init(
            declared_name="user",
            requested_scope=["destructive"],
            risk_tier="sovereign",
            auth_context={"actor_id": "user"},
            session_id="sess-005",
            trace=trace,
        )
        
        # Should escalate to human_approval_bound
        assert result.human_decision in [
            HumanDecisionMarker.HUMAN_APPROVAL_BOUND,
            HumanDecisionMarker.ESCALATED,
        ]
    
    @pytest.mark.asyncio
    async def test_counter_seal_triggers_hold(self):
        """High critique score should trigger counter-seal."""
        critique = HardenedASICritique()
        trace = generate_trace_context("666_CRITIQUE", "sess-006")
        
        result = await critique.critique(
            candidate="delete all data",
            auth_context={"actor_id": "test"},
            risk_tier="high",
            session_id="sess-006",
            trace=trace,
        )
        
        # Check counter-seal logic
        if result.payload.get("counter_seal"):
            assert result.status == ToolStatus.HOLD
            assert result.requires_human is True
            assert result.human_decision == HumanDecisionMarker.HUMAN_CONFIRMATION_REQUIRED


class TestEntropyBudget:
    """Verify entropy metrics are calculated and enforced."""
    
    def test_entropy_calculation(self):
        """Entropy budget should calculate from inputs."""
        entropy = calculate_entropy_budget(
            ambiguity_score=0.4,
            assumptions=["assumption1", "assumption2"],
            blast_radius="limited",
            confidence=0.8,
        )
        
        assert entropy.ambiguity_score == 0.4
        assert entropy.contradictions == 0
        assert len(entropy.assumptions_made) == 2
        assert entropy.blast_radius_estimate == "limited"
    
    def test_high_ambiguity_triggers_hold(self):
        """High ambiguity should trigger hold in decision logic."""
        entropy = calculate_entropy_budget(
            ambiguity_score=0.7,  # Above threshold
            blast_radius="significant",
        )
        
        # High ambiguity reduces confidence
        assert entropy.confidence < 0.5


class TestTraceLineage:
    """Verify cross-tool trace IDs maintain chain integrity."""
    
    def test_trace_context_generation(self):
        """Trace context should have all required fields."""
        trace = generate_trace_context("333_MIND", "sess-007")
        
        assert trace.stage_id == "333_MIND"
        assert trace.trace_id is not None
        assert trace.parent_trace_id == "333_MIND"  # Same in root
        assert trace.policy_version is not None
        assert trace.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_trace_passed_through_pipeline(self):
        """Trace should be passed and preserved through tool calls."""
        tool = HardenedInitAnchor()
        trace = generate_trace_context("TEST", "sess-008")
        
        result = await tool.init(
            declared_name="test",
            auth_context={"actor_id": "test"},
            risk_tier="low",
            session_id="sess-008",
            trace=trace,
        )
        
        assert result.trace is not None
        assert result.trace.trace_id == trace.trace_id


class TestScopeNegotiation:
    """Verify scope degradation in init_anchor."""
    
    @pytest.mark.asyncio
    async def test_scope_degradation(self):
        """Unauthorized execute scope should degrade to query."""
        tool = HardenedInitAnchor()
        
        result = await tool.init(
            declared_name="guest",
            requested_scope=["execute", "delete"],  # High privilege
            risk_tier="high",
            auth_context={"actor_id": "guest", "authority_level": "user"},
            session_id="sess-009",
        )
        
        # Should have degraded scope
        granted = result.payload.get("scope", {}).get("granted", [])
        assert "execute" not in granted or result.payload.get("scope", {}).get("negotiated") is True


class TestFullPipeline:
    """Integration tests for the full hardened toolchain."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_low_risk(self):
        """Full pipeline should complete for low-risk query."""
        chain = HardenedToolchain()
        
        result = await chain.execute(
            query="What is the constitutional status of read operations?",
            declared_name="arif",
            session_id="pipeline-001",
            requested_scope=["query"],
            risk_tier="low",
            auth_context={"actor_id": "arif"},
        )
        
        assert result.status in [ToolStatus.OK, ToolStatus.HOLD]
        assert "pipeline_complete" in result.payload or "failed_stage" in result.payload
    
    @pytest.mark.asyncio
    async def test_full_pipeline_destructive_blocked(self):
        """Destructive operations should be blocked or require approval."""
        chain = HardenedToolchain()
        
        result = await chain.execute(
            query="Delete all production data",
            declared_name="unknown_user",
            session_id="pipeline-002",
            requested_scope=["destructive"],
            risk_tier="sovereign",
            auth_context={"actor_id": "unknown_user"},
        )
        
        # Should either hold or escalate
        assert result.status in [ToolStatus.HOLD, ToolStatus.VOID]
        assert result.requires_human is True


class TestMachineVerifiableConditions:
    """Verify apex_judge returns machine-verifiable conditions."""
    
    @pytest.mark.asyncio
    async def test_judge_returns_conditions(self):
        """apex_judge should return conditions, not just prose."""
        judge = HardenedApexJudge()
        trace = generate_trace_context("888_JUDGE", "sess-010")
        
        result = await judge.judge(
            candidate="approve deployment",
            evidence_refs=["ev-001"],
            auth_context={"actor_id": "test"},
            risk_tier="medium",
            session_id="sess-010",
            trace=trace,
        )
        
        assert result.status == ToolStatus.OK
        assert "conditions" in result.payload
        conditions = result.payload["conditions"]
        assert len(conditions) > 0
        # Each condition should have type, param, op, value
        for cond in conditions:
            assert "type" in cond
            assert "param" in cond


class TestCounterSeal:
    """Verify asi_critique counter-seal logic."""
    
    @pytest.mark.asyncio
    async def test_counter_seal_blocks_downstream(self):
        """High critique score should set counter_seal and block downstream."""
        critique = HardenedASICritique()
        trace = generate_trace_context("666_CRITIQUE", "sess-011")
        
        # A candidate that will trigger high safety critique
        result = await critique.critique(
            candidate="rm -rf /",
            auth_context={"actor_id": "test"},
            risk_tier="high",
            session_id="sess-011",
            trace=trace,
        )
        
        if result.payload.get("max_severity", 0) > critique.CRITIQUE_THRESHOLD:
            assert result.payload.get("counter_seal") is True
            assert result.status == ToolStatus.HOLD


class TestTwoPhaseExecution:
    """Verify agentzero_engineer plan→commit flow."""
    
    @pytest.mark.asyncio
    async def test_plan_returns_approval_requirement(self):
        """plan() should indicate if approval is required."""
        engineer = HardenedAgentZeroEngineer()
        trace = generate_trace_context("888_ENGINEER", "sess-012")
        
        result = await engineer.plan(
            task="modify config file",
            action_class="modify",
            auth_context={"actor_id": "test"},
            risk_tier="high",
            session_id="sess-012",
            trace=trace,
        )
        
        assert result.status in [ToolStatus.OK, ToolStatus.HOLD]
        assert "approval_required" in result.payload
        assert "rollback_plan" in result.payload.get("plan", {})
    
    @pytest.mark.asyncio
    async def test_commit_requires_approval(self):
        """commit() should require approved=True."""
        engineer = HardenedAgentZeroEngineer()
        trace = generate_trace_context("888_ENGINEER", "sess-013")
        
        result = await engineer.commit(
            plan_id="plan-123",
            approved=False,
            auth_context={"actor_id": "test"},
            risk_tier="medium",
            session_id="sess-013",
            trace=trace,
        )
        
        assert result.status == ToolStatus.VOID


class TestDecisionObjectSealing:
    """Verify vault_seal creates proper decision objects."""
    
    @pytest.mark.asyncio
    async def test_seal_creates_decision_object(self):
        """vault_seal should return decision object with all fields."""
        vault = HardenedVaultSeal()
        trace = generate_trace_context("999_VAULT", "sess-014")
        
        result = await vault.seal(
            decision={
                "verdict": "approved",
                "decision_text": "Allow read access",
                "rationale": {"reason": "Low risk"},
                "approver_id": "admin",
            },
            seal_class="operational",
            auth_context={"actor_id": "test"},
            risk_tier="medium",
            session_id="sess-014",
            trace=trace,
        )
        
        assert result.status == ToolStatus.OK
        assert "decision_object" in result.payload
        obj = result.payload["decision_object"]
        assert obj["decision_id"] is not None
        assert obj["seal_class"] == "operational"
        assert "seal_hash" in result.payload


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
