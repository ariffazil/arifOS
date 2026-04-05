"""
F2 Truth tests aligned to the current kernel API.

These assertions exercise the live floor contract (`F2_Truth.check`) and the
canonical cognition interface (`judge_cognition`) instead of the removed
`JudgmentEngine.evaluate(...)` wrapper.
"""

from __future__ import annotations

import pytest

from core.judgment import judge_cognition
from core.shared.floors import F2_Truth


class TestF2TruthFloor:
    def setup_method(self) -> None:
        self.floor = F2_Truth()

    def test_ungrounded_claim_fails_floor(self) -> None:
        result = self.floor.check({"query": "The moon is made of cheese", "truth_score": 0.5})

        assert not result.passed
        assert result.floor_id == "F2_Truth"
        assert result.score == pytest.approx(0.5)

    def test_grounded_claim_passes_floor(self) -> None:
        result = self.floor.check({"query": "Python 3.12 release date", "truth_score": 0.99})

        assert result.passed
        assert result.score == pytest.approx(0.99)

    def test_axiomatic_math_bypasses_claim_threshold(self) -> None:
        result = self.floor.check({"query": "2+2"})

        assert result.passed
        assert result.score == pytest.approx(1.0)


class TestF2TruthKernel:
    def test_ungrounded_cognition_returns_low_truth(self) -> None:
        result = judge_cognition(
            query="The moon is made of cheese",
            evidence_count=0,
            evidence_relevance=0.0,
            reasoning_consistency=0.3,
            knowledge_gaps=["no external evidence"],
            model_logits_confidence=0.2,
        )

        assert result.grounded is False
        assert result.truth_score == pytest.approx(0.5)
        assert result.verdict in {"SABAR", "PARTIAL", "PROVISIONAL"}

    def test_grounded_cognition_caps_truth_at_floor_threshold(self) -> None:
        result = judge_cognition(
            query="Python 3.12 release date",
            evidence_count=5,
            evidence_relevance=1.0,
            reasoning_consistency=1.0,
            knowledge_gaps=[],
            model_logits_confidence=1.0,
            grounding=[
                {"source": "python.org", "relevance": 1.0},
                {"source": "docs.python.org", "relevance": 1.0},
            ],
        )

        assert result.grounded is True
        assert result.truth_score == pytest.approx(0.99)
        assert result.provenance is not None
        assert result.provenance.final_score == pytest.approx(0.99)

    def test_more_grounding_increases_truth_score(self) -> None:
        low = judge_cognition(
            query="Python release schedule",
            evidence_count=1,
            evidence_relevance=0.6,
            reasoning_consistency=0.8,
            knowledge_gaps=["limited corroboration"],
            model_logits_confidence=0.7,
            grounding=[{"source": "blog.example", "relevance": 0.6}],
        )
        high = judge_cognition(
            query="Python release schedule",
            evidence_count=4,
            evidence_relevance=1.0,
            reasoning_consistency=0.95,
            knowledge_gaps=[],
            model_logits_confidence=0.95,
            grounding=[
                {"source": "python.org", "relevance": 1.0},
                {"source": "docs.python.org", "relevance": 1.0},
            ],
        )

        assert high.truth_score > low.truth_score


# ═══════════════════════════════════════════════════════════════════════════════
# PARIS WEATHER INCIDENT — Regression Suite (v2026.03.25)
# Ensures DRY_RUN + DOMAIN_GATE + VERDICT_SCOPE hardening cannot regress.
# See: 000/FLOORS/F02_TRUTH.md §Enforcement Addendum (v2026.03.25)
# ═══════════════════════════════════════════════════════════════════════════════

class TestParisWeatherIncident:
    """
    Regression tests for the Paris Weather hallucination incident.
    A model presented weather data as factual after receiving a DRY_RUN
    router response with no domain payload.
    These tests ensure the three root-cause fixes cannot silently regress.
    """

    def test_dry_run_envelope_forces_simulation_only_policy(self) -> None:
        """Fix 1: DRY_RUN=True must set output_policy=SIMULATION_ONLY and verdict_scope=DRY_RUN_SEAL."""
        from arifosmcp.runtime.contracts_v2 import (
            ToolEnvelope, ToolStatus, RiskTier, OutputPolicy, VerdictScope,
        )
        envelope = ToolEnvelope(
            status=ToolStatus.OK,
            tool="arifOS_kernel",
            session_id="test-session",
            risk_tier=RiskTier.LOW,
            dry_run=True,
            payload={"stage": "444_ROUTER", "meta": "routing decision"},
        )
        result = envelope.to_dict()

        assert result["output_policy"] == OutputPolicy.SIMULATION_ONLY.value, (
            "DRY_RUN envelope MUST force output_policy=SIMULATION_ONLY"
        )
        assert result["verdict_scope"] == VerdictScope.DRY_RUN_SEAL.value, (
            "DRY_RUN envelope MUST set verdict_scope=DRY_RUN_SEAL"
        )
        assert result["dry_run"] is True
        # Warning must be present and contain the key model instruction
        warning_text = " ".join(result.get("warnings", []))
        assert "SIMULATION_ONLY" in warning_text or "simulation" in warning_text.lower(), (
            "DRY_RUN envelope MUST include model-surface warning about simulation"
        )

    def test_dry_run_payload_field_also_triggers_poison_pill(self) -> None:
        """Fix 1: dry_run in payload dict (not just dataclass field) must also trigger poison pill."""
        from arifosmcp.runtime.contracts_v2 import (
            ToolEnvelope, ToolStatus, RiskTier, OutputPolicy,
        )
        envelope = ToolEnvelope(
            status=ToolStatus.OK,
            tool="arifOS_kernel",
            session_id="test-session",
            risk_tier=RiskTier.LOW,
            payload={"dry_run": True, "stage": "444_ROUTER"},  # dry_run in payload dict
        )
        result = envelope.to_dict()
        assert result["output_policy"] == OutputPolicy.SIMULATION_ONLY.value, (
            "dry_run=True in payload dict MUST also trigger SIMULATION_ONLY policy"
        )

    def test_weather_domain_gate_fails_without_required_keys(self) -> None:
        """Fix 2: weather domain class without required keys must force CANNOT_COMPUTE + DOMAIN_VOID."""
        from arifosmcp.runtime.contracts_v2 import (
            ToolEnvelope, ToolStatus, RiskTier, OutputPolicy, VerdictScope,
        )
        # Simulate a 'weather' result with no real weather keys — only governance meta
        envelope = ToolEnvelope(
            status=ToolStatus.OK,
            tool="physics_reality",
            session_id="test-session",
            risk_tier=RiskTier.LOW,
            payload={
                "stage": "444_ROUTER",
                "verdict": "SEAL",  # old-style, no domain keys
                "query": "weather in Paris",
            },
        )
        envelope.apply_domain_gate("weather")
        result = envelope.to_dict()

        assert result["output_policy"] == OutputPolicy.CANNOT_COMPUTE.value, (
            "Weather domain without temp_c/provider/timestamp/location MUST be CANNOT_COMPUTE"
        )
        assert result["verdict_scope"] == VerdictScope.DOMAIN_VOID.value, (
            "Weather domain without required keys MUST be DOMAIN_VOID"
        )
        warning_text = " ".join(result.get("warnings", []))
        assert "Cannot Compute" in warning_text or "DOMAIN_GATE_FAIL" in warning_text

    def test_weather_domain_gate_passes_with_all_required_keys(self) -> None:
        """Fix 2: weather with all required keys must produce REAL_DOMAIN + DOMAIN_SEAL."""
        from arifosmcp.runtime.contracts_v2 import (
            ToolEnvelope, ToolStatus, RiskTier, OutputPolicy, VerdictScope,
        )
        envelope = ToolEnvelope(
            status=ToolStatus.OK,
            tool="physics_reality",
            session_id="test-session",
            risk_tier=RiskTier.LOW,
            payload={
                "temp_c": 18.5,
                "provider": "openweathermap",
                "timestamp": "2026-03-25T02:00:00Z",
                "location": "Paris, FR",
            },
        )
        envelope.apply_domain_gate("weather")
        result = envelope.to_dict()

        assert result["output_policy"] == OutputPolicy.REAL_DOMAIN.value, (
            "Weather with all required keys MUST be REAL_DOMAIN"
        )
        assert result["verdict_scope"] == VerdictScope.DOMAIN_SEAL.value

    def test_router_seal_is_not_domain_seal(self) -> None:
        """Fix 3: ROUTER_SEAL and DOMAIN_SEAL must be distinct values — never equal."""
        from arifosmcp.runtime.contracts_v2 import VerdictScope
        assert VerdictScope.ROUTER_SEAL != VerdictScope.DOMAIN_SEAL, (
            "ROUTER_SEAL and DOMAIN_SEAL MUST be distinct; conflation is a F2 violation"
        )
        assert VerdictScope.ROUTER_SEAL.value != VerdictScope.DOMAIN_SEAL.value

    def test_router_meta_output_policy_is_not_real_domain(self) -> None:
        """Fix 3: OutputPolicy.ROUTER_META must not be REAL_DOMAIN."""
        from arifosmcp.runtime.contracts_v2 import OutputPolicy
        assert OutputPolicy.ROUTER_META != OutputPolicy.REAL_DOMAIN, (
            "ROUTER_META output MUST NOT authorise domain factual claims"
        )

    def test_domain_payload_gates_registry_contains_weather(self) -> None:
        """Fix 2: DOMAIN_PAYLOAD_GATES must define weather with the four canonical keys."""
        from arifosmcp.runtime.contracts_v2 import DOMAIN_PAYLOAD_GATES
        assert "weather" in DOMAIN_PAYLOAD_GATES
        required = DOMAIN_PAYLOAD_GATES["weather"]
        for key in ("temp_c", "provider", "timestamp", "location"):
            assert key in required, (
                f"DOMAIN_PAYLOAD_GATES['weather'] must include '{key}'"
            )

    def test_anchor_void_propagation_sets_global_hold(self) -> None:
        """Fix 4: GlobalAnchorHoldRegistry.set_global_hold must block the session."""
        from arifosmcp.agentzero.escalation.hold_state import GlobalAnchorHoldRegistry

        registry = GlobalAnchorHoldRegistry()
        registry.set_global_hold(
            session_key="test-actor-void",
            reason="init_anchor: missing intent/query/raw_input",
        )

        hold = registry.is_held("test-actor-void")
        assert hold is not None, "Session MUST be marked as held after set_global_hold"
        assert hold["code"] == "888_HOLD"

        # Clean up
        cleared = registry.clear_hold("test-actor-void")
        assert cleared is True
        assert registry.is_held("test-actor-void") is None, (
            "Hold MUST be cleared after clear_hold"
        )

    def test_anchor_void_hold_response_shape(self) -> None:
        """Fix 4: build_hold_response must include next_action pointing to init_anchor."""
        from arifosmcp.agentzero.escalation.hold_state import GlobalAnchorHoldRegistry

        registry = GlobalAnchorHoldRegistry()
        registry.set_global_hold(
            session_key="test-actor-resp",
            reason="session-rejected: missing raw_input",
        )
        response = registry.build_hold_response("test-actor-resp")

        assert response["status"] == "888_HOLD"
        assert response["output_policy"] == "CANNOT_COMPUTE"
        assert response["next_action"]["tool"] == "init_anchor"
        registry.clear_hold("test-actor-resp")
