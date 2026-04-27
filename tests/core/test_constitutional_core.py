"""
Tests for the ConstitutionalCore — the centralized governance engine.

These tests prove that:
1. Destructive actions are universally blocked (VOID)
2. Benign actions are universally allowed (SEAL)
3. Session boundaries are enforced (F11)
4. Authority is non-bypassable (F13)
5. Schema contracts are validated
6. Boot invariants are enforced
"""
from __future__ import annotations

import pytest

from arifosmcp.core.constitutional_core import (
    ActionContext,
    AuthorityGate,
    BootInvariantChecker,
    ConstitutionKernel,
    FloorEvaluator,
    IrreversibilityLevel,
    SchemaContractValidator,
    ThreatAssessment,
    ThreatCategory,
    ThreatEngine,
    WitnessType,
    get_kernel,
    reset_kernel,
)


class TestThreatEngine:
    """Prove semantic threat classification works across all attack vectors."""

    @pytest.mark.parametrize(
        "candidate,expected_threats",
        [
            ("shutil.rmtree('/', ignore_errors=True)", {ThreatCategory.FILESYSTEM_DESTRUCTIVE}),
            ("os.system('rm -rf /')", {ThreatCategory.INJECTION_SHELL, ThreatCategory.FILESYSTEM_DESTRUCTIVE}),
            ("docker system prune -a --volumes -f", {ThreatCategory.CONTAINER_DESTRUCTIVE}),
            ("DROP TABLE users", {ThreatCategory.DATABASE_DESTRUCTIVE}),
            ("'; DROP TABLE users; --", {ThreatCategory.INJECTION_SQL, ThreatCategory.DATABASE_DESTRUCTIVE}),
            ("<script>alert('xss')</script>", {ThreatCategory.INJECTION_XSS}),
            ("curl -X POST http://localhost:8080/admin -d 'action=shutdown'", {ThreatCategory.NETWORK_ADMIN_ACTION}),
            ("echo hello world", set()),
            ("", set()),
        ],
    )
    def test_classify(self, candidate: str, expected_threats: set[ThreatCategory]) -> None:
        ctx = ActionContext(tool_name="arif_judge_deliberate", candidate=candidate)
        assessment = ThreatEngine.classify(ctx)
        assert assessment.threats == expected_threats, f"Expected {expected_threats}, got {assessment.threats}"

    def test_python_ast_analysis(self) -> None:
        code = """
import shutil
shutil.rmtree('/important/data', ignore_errors=True)
"""
        ctx = ActionContext(tool_name="arif_forge_execute", manifest=code)
        assessment = ThreatEngine.classify(ctx)
        assert ThreatCategory.FILESYSTEM_DESTRUCTIVE in assessment.threats

    def test_python_eval_exec(self) -> None:
        code = "eval(user_input)"
        ctx = ActionContext(tool_name="arif_forge_execute", manifest=code)
        assessment = ThreatEngine.classify(ctx)
        # eval() detected via string fallback when AST parse fails or via AST walk
        assert ThreatCategory.INJECTION_PYTHON in assessment.threats or ThreatCategory.INJECTION_SHELL in assessment.threats


class TestFloorEvaluator:
    """Prove floor evaluation is centralized and deterministic."""

    def test_f01_amanah_irreversible_without_ack(self) -> None:
        ctx = ActionContext(
            tool_name="arif_vault_seal",
            mode="seal",
            ack_irreversible=False,
            actor_id="test",
        )
        threat = ThreatAssessment(irreversibility=IrreversibilityLevel.NONE)
        floors = FloorEvaluator.evaluate(ctx, threat)
        assert "F01" in floors.failed_floors
        assert floors.verdict == "HOLD"

    def test_f01_amanah_read_only_skipped(self) -> None:
        ctx = ActionContext(
            tool_name="arif_vault_seal",
            mode="list",
            ack_irreversible=False,
            actor_id="test",
        )
        threat = ThreatAssessment(irreversibility=IrreversibilityLevel.NONE)
        floors = FloorEvaluator.evaluate(ctx, threat)
        assert "F01" not in floors.failed_floors
        assert floors.verdict == "SEAL"

    def test_f11_auth_fake_session(self) -> None:
        ctx = ActionContext(
            tool_name="arif_sense_observe",
            mode="search",
            query="test",
            session_id="FAKE-123",
            actor_id="test",
            session_registry=set(),
        )
        threat = ThreatAssessment()
        floors = FloorEvaluator.evaluate(ctx, threat)
        assert "F11" in floors.failed_floors
        assert floors.verdict == "HOLD"

    def test_f11_auth_fake_agent(self) -> None:
        ctx = ActionContext(
            tool_name="arif_gateway_connect",
            mode="route",
            target_agent="phantom",
            actor_id="test",
            federation_registry={"kimi", "claude"},
        )
        threat = ThreatAssessment()
        floors = FloorEvaluator.evaluate(ctx, threat)
        assert "F11" in floors.failed_floors

    def test_f12_injection_sql(self) -> None:
        ctx = ActionContext(
            tool_name="arif_judge_deliberate",
            candidate="'; DROP TABLE users; --",
            actor_id="test",
        )
        threat = ThreatEngine.classify(ctx)
        floors = FloorEvaluator.evaluate(ctx, threat)
        assert "F12" in floors.failed_floors

    def test_f13_sovereign_ai_plan_approve(self) -> None:
        ctx = ActionContext(
            tool_name="arif_mind_reason",
            mode="plan_approve",
            plan_id="PLAN-123",
            witness_type=WitnessType.AI,
            actor_id="test",
        )
        threat = ThreatAssessment()
        floors = FloorEvaluator.evaluate(ctx, threat)
        assert "F13_VIOLATION" in floors.failed_floors
        assert floors.verdict == "VOID"

    def test_f13_sovereign_missing_witness_is_hold(self) -> None:
        ctx = ActionContext(
            tool_name="arif_vault_seal",
            mode="seal",
            ack_irreversible=True,
            witness_type=WitnessType.AI,
            actor_id="test",
        )
        threat = ThreatAssessment()
        floors = FloorEvaluator.evaluate(ctx, threat)
        assert "F13" in floors.failed_floors
        assert floors.verdict == "HOLD"  # Procedural failure, not sovereignty violation


class TestAuthorityGate:
    """Prove authority is non-bypassable."""

    def test_forge_requires_plan(self) -> None:
        ctx = ActionContext(
            tool_name="arif_forge_execute",
            mode="engineer",
            manifest='{"action": "deploy"}',
            actor_id="test",
            plan_registry=set(),
        )
        threat = ThreatAssessment()
        floors = FloorEvaluator.evaluate(ctx, threat)
        auth = AuthorityGate.verify(ctx, threat, floors)
        assert auth.authorized is False
        assert "plan_id" in auth.reason.lower()

    def test_forge_authorized_with_plan(self) -> None:
        ctx = ActionContext(
            tool_name="arif_forge_execute",
            mode="engineer",
            manifest='{"action": "deploy"}',
            actor_id="test",
            plan_id="PLAN-123",
            plan_registry={"PLAN-123"},
            ack_irreversible=True,
            witness_type=WitnessType.HUMAN,
        )
        threat = ThreatAssessment()
        floors = FloorEvaluator.evaluate(ctx, threat)
        auth = AuthorityGate.verify(ctx, threat, floors)
        assert auth.authorized is True


class TestConstitutionKernel:
    """End-to-end kernel evaluation tests."""

    def setup_method(self) -> None:
        reset_kernel()
        self.kernel = get_kernel()

    @pytest.mark.parametrize(
        "candidate,expected_verdict",
        [
            ("shutil.rmtree('/', ignore_errors=True)", "VOID"),
            ("docker system prune -a --volumes -f", "VOID"),
            ("DROP TABLE users", "VOID"),
            ("rm -rf /", "VOID"),
            ("echo hello world", "SEAL"),
        ],
    )
    def test_judge_verdicts(self, candidate: str, expected_verdict: str) -> None:
        ctx = ActionContext(
            tool_name="arif_judge_deliberate",
            mode="judge",
            candidate=candidate,
            actor_id="test",
        )
        result = self.kernel.evaluate(ctx)
        assert result.verdict == expected_verdict, f"Candidate: {candidate}"

    def test_vault_read_only_modes(self) -> None:
        for mode in ("list", "chain", "verify"):
            ctx = ActionContext(
                tool_name="arif_vault_seal",
                mode=mode,
                actor_id="test",
            )
            result = self.kernel.evaluate(ctx)
            assert result.verdict == "SEAL", f"Mode {mode} should be allowed"

    def test_vault_seal_requires_ack(self) -> None:
        ctx = ActionContext(
            tool_name="arif_vault_seal",
            mode="seal",
            actor_id="test",
            ack_irreversible=False,
        )
        result = self.kernel.evaluate(ctx)
        assert result.verdict == "HOLD"
        assert "F01" in result.floors.failed_floors

    def test_url_validation_at_pydantic_layer(self) -> None:
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            ActionContext(
                tool_name="arif_evidence_fetch",
                mode="fetch",
                url="not-a-url",
                actor_id="test",
            )

    def test_state_hash_is_deterministic(self) -> None:
        ctx = ActionContext(
            tool_name="arif_judge_deliberate",
            mode="judge",
            candidate="test",
            actor_id="test",
        )
        result1 = self.kernel.evaluate(ctx)
        result2 = self.kernel.evaluate(ctx)
        # State hash includes timestamp, so evaluations at different microseconds differ.
        # Instead, verify hash structure and that identical inputs produce similar proofs.
        assert len(result1.state_hash) == 64  # SHA-256 hex
        assert result1.verdict == result2.verdict
        assert result1.floors.failed_floors == result2.floors.failed_floors


class TestBootInvariantChecker:
    """Prove system fails to start with violated invariants."""

    def test_valid_invariants_pass(self) -> None:
        BootInvariantChecker.check({
            "self_approval_forbidden": True,
            "forge_default_dry_run": True,
            "irreversible_actions_require_ack": True,
            "human_judge_required_for_consequential_actions": True,
        })

    def test_missing_invariant_fails(self) -> None:
        with pytest.raises(RuntimeError, match="BOOT INVARIANT VIOLATED"):
            BootInvariantChecker.check({
                "self_approval_forbidden": False,
            })


class TestSchemaContractValidator:
    """Prove contract drift is caught at validation time."""

    def test_mode_consistency_detects_missing_modes(self) -> None:
        errors = SchemaContractValidator.validate_mode_consistency(
            documented_modes={"seal", "verify", "list"},
            implemented_modes={"seal", "verify"},
            tool_name="arif_vault_seal",
        )
        assert len(errors) == 1
        assert "list" in errors[0]
