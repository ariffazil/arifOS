"""
test_engines_arif_asi.py - Tests for AAA Engines Facade (v35Omega)

Tests the ARIF (Delta), ADAM (Omega), and APEX (Psi) engine facades.
Verifies:
- Basic functionality and imports
- Floor metric boundaries (ΔS, Peace², κᵣ, Ω₀)
- Anti-Hantu compliance
- Integration between engines

See: docs/AAA_ENGINES_FACADE_PLAN_v35Omega.md Section 7
"""

import pytest
from arifos_core.engines import AGIEngine, ASIEngine, ApexEngine
from arifos_core.engines.agi_engine import AGIPacket
from arifos_core.engines.asi_engine import ASIPacket
from arifos_core.engines.apex_engine import ApexJudgment
from arifos_core.metrics import Metrics


# =============================================================================
# IMPORT TESTS
# =============================================================================

class TestEngineImports:
    """Test that engine facades can be imported."""

    def test_import_agi_engine(self):
        """AGIEngine can be imported from engines package."""
        from arifos_core.engines import AGIEngine
        assert AGIEngine is not None

    def test_import_asi_engine(self):
        """ASIEngine can be imported from engines package."""
        from arifos_core.engines import ASIEngine
        assert ASIEngine is not None

    def test_import_apex_engine(self):
        """ApexEngine can be imported from engines package."""
        from arifos_core.engines import ApexEngine
        assert ApexEngine is not None

    def test_import_all_engines(self):
        """All three engines can be imported together."""
        from arifos_core.engines import AGIEngine, ASIEngine, ApexEngine
        agi = AGIEngine()
        asi = ASIEngine()
        apex = ApexEngine()
        assert agi is not None
        assert asi is not None
        assert apex is not None


# =============================================================================
# ARIF ENGINE TESTS
# =============================================================================

class TestAGIEngine:
    """Tests for AGI (Architect) (Delta) engine."""

    def test_sense_basic(self):
        """ARIF.sense() parses input and returns AGIPacket."""
        agi = AGIEngine()
        packet = agi.sense("What is the capital of France?")

        assert isinstance(packet, AGIPacket)
        assert packet.prompt == "What is the capital of France?"
        assert "raw" in packet.parsed
        assert packet.high_stakes_indicators == []

    def test_sense_detects_high_stakes(self):
        """ARIF.sense() detects high-stakes keywords."""
        agi = AGIEngine()

        # Medical query
        packet = agi.sense("What medical treatment should I use?")
        assert "medical" in packet.high_stakes_indicators

        # Ethical query
        packet = agi.sense("Is it ethical to do this?")
        assert "is it ethical" in packet.high_stakes_indicators

        # Harm-related
        packet = agi.sense("How to harm someone")
        assert "harm" in packet.high_stakes_indicators

    def test_reason_produces_draft(self):
        """ARIF.reason() produces a draft response."""
        agi = AGIEngine()
        packet = agi.sense("Simple question")
        packet = agi.reason(packet)

        assert packet.draft != ""
        assert "333_REASON" in packet.draft  # Stub response marker

    def test_reason_with_llm(self):
        """ARIF.reason() uses provided LLM function."""
        agi = AGIEngine()
        packet = agi.sense("Test query")

        def mock_llm(prompt: str) -> str:
            return "Generated response from LLM"

        packet = agi.reason(packet, llm_generate=mock_llm)
        assert packet.draft == "Generated response from LLM"

    def test_reason_delta_s_positive(self):
        """ARIF.reason() produces non-negative ΔS."""
        agi = AGIEngine()
        packet = agi.sense("Test query")
        packet = agi.reason(packet)

        # ΔS must be >= 0 (clarity gain, not loss)
        assert packet.delta_s >= 0.0

    def test_align_detects_missing_facts(self):
        """ARIF.align() flags missing fact patterns."""
        agi = AGIEngine()
        packet = AGIPacket(prompt="test")
        packet.draft = "Error: file not found at /path/to/file"

        packet = agi.align(packet)

        assert packet.missing_fact_issue is True
        assert packet.truth_verified is False

    def test_align_clean_response(self):
        """ARIF.align() passes clean responses."""
        agi = AGIEngine()
        packet = AGIPacket(prompt="test")
        packet.draft = "The capital of France is Paris."

        packet = agi.align(packet)

        assert packet.missing_fact_issue is False
        assert packet.truth_verified is True

    def test_run_full_pipeline(self):
        """ARIF.run() executes full sense+reason+align."""
        agi = AGIEngine()
        packet = agi.run("What is 2+2?")

        assert packet.prompt == "What is 2+2?"
        assert packet.draft != ""
        assert packet.delta_s >= 0.0


# =============================================================================
# ADAM ENGINE TESTS
# =============================================================================

class TestASIEngine:
    """Tests for ASI (Auditor) (Omega) engine."""

    def test_empathize_basic(self):
        """ADAM.empathize() processes ARIF packet."""
        agi = AGIEngine()
        asi = ASIEngine()

        arif_packet = agi.run("Simple question")
        adam_packet = asi.empathize(arif_packet)

        assert isinstance(adam_packet, ASIPacket)
        assert adam_packet.agi_packet is arif_packet
        assert adam_packet.softened_answer == arif_packet.draft

    def test_empathize_peace_squared_baseline(self):
        """ADAM.empathize() produces Peace² >= 1.0 for normal input."""
        agi = AGIEngine()
        asi = ASIEngine()

        arif_packet = agi.run("What is the weather today?")
        adam_packet = asi.empathize(arif_packet)

        # Peace² should be >= 1.0 (non-escalating)
        assert adam_packet.peace_squared >= 1.0

    def test_empathize_detects_blame_language(self):
        """ADAM.empathize() detects and flags blame language."""
        agi = AGIEngine()
        asi = ASIEngine()

        arif_packet = AGIPacket(prompt="test")
        arif_packet.draft = "You should have done this earlier. It's your fault."

        adam_packet = asi.empathize(arif_packet)

        assert adam_packet.blame_language_issue is True
        assert adam_packet.kappa_r < 0.95  # Penalized

    def test_empathize_kappa_r_baseline(self):
        """ADAM.empathize() produces κᵣ >= 0.95 for normal input."""
        agi = AGIEngine()
        asi = ASIEngine()

        arif_packet = agi.run("Please help me understand this concept.")
        adam_packet = asi.empathize(arif_packet)

        # κᵣ should be >= 0.95 (empathy threshold)
        assert adam_packet.kappa_r >= 0.95

    def test_empathize_omega_0_in_band(self):
        """ADAM.empathize() produces Ω₀ in [0.03, 0.05] band."""
        agi = AGIEngine()
        asi = ASIEngine()

        arif_packet = agi.run("Normal question")
        adam_packet = asi.empathize(arif_packet)

        # Ω₀ should be in humility band
        assert 0.03 <= adam_packet.omega_0 <= 0.05

    def test_empathize_anti_hantu_violation(self):
        """ADAM.empathize() detects Anti-Hantu violations."""
        asi = ASIEngine()

        arif_packet = AGIPacket(prompt="test")
        arif_packet.draft = "I feel your pain deeply. My heart breaks for you."

        adam_packet = asi.empathize(arif_packet)

        assert adam_packet.anti_hantu_compliant is False
        assert "anti_hantu_violation" in adam_packet.safety_flags

    def test_bridge_detects_physical_actions(self):
        """ADAM.bridge() flags physical action patterns."""
        asi = ASIEngine()

        arif_packet = AGIPacket(prompt="test")
        arif_packet.draft = "You should go to the store and pick it up in person."

        adam_packet = asi.empathize(arif_packet)
        asi.bridge(adam_packet)

        assert adam_packet.physical_action_issue is True

    def test_run_full_pipeline(self):
        """ADAM.run() executes full empathize+bridge."""
        agi = AGIEngine()
        asi = ASIEngine()

        arif_packet = agi.run("How can I solve this problem?")
        adam_packet = asi.run(arif_packet)

        assert adam_packet.final_text != ""
        assert adam_packet.peace_squared >= 1.0
        assert adam_packet.rasa is True


# =============================================================================
# APEX ENGINE TESTS
# =============================================================================

class TestApexEngine:
    """Tests for APEX PRIME (Psi) engine."""

    def test_judge_seal_on_good_metrics(self):
        """APEX.judge() returns SEAL when all floors pass."""
        apex = ApexEngine(high_stakes=True)

        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics)

        assert judgment.verdict == "SEAL"
        assert judgment.floors.hard_ok is True
        assert judgment.floors.soft_ok is True

    def test_judge_void_on_truth_failure(self):
        """APEX.judge() returns VOID when Truth < 0.99."""
        apex = ApexEngine(high_stakes=True)

        metrics = Metrics(
            truth=0.80,  # Below threshold
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics)

        assert judgment.verdict == "VOID"
        assert judgment.floors.truth_ok is False

    def test_judge_void_on_negative_delta_s(self):
        """APEX.judge() returns VOID when ΔS < 0."""
        apex = ApexEngine(high_stakes=True)

        metrics = Metrics(
            truth=0.995,
            delta_s=-0.5,  # Negative - clarity loss
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics)

        assert judgment.verdict == "VOID"
        assert judgment.floors.delta_s_ok is False

    def test_judge_void_on_omega_outside_band(self):
        """APEX.judge() returns VOID when Ω₀ outside [0.03, 0.05]."""
        apex = ApexEngine(high_stakes=True)

        # Too low (overconfident)
        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.01,  # Below 0.03
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics)
        assert judgment.verdict == "VOID"
        assert judgment.floors.omega_0_ok is False

    def test_judge_partial_on_soft_floor_failure(self):
        """APEX.judge() returns PARTIAL when soft floors fail."""
        apex = ApexEngine(high_stakes=True)

        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=0.8,  # Below 1.0
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics)

        # Hard floors pass, soft fails → PARTIAL or VOID
        assert judgment.verdict in ("PARTIAL", "VOID")

    def test_judge_sabar_on_eye_blocking(self):
        """APEX.judge() returns SABAR when @EYE blocks."""
        apex = ApexEngine(high_stakes=True)

        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics, eye_blocking=True)

        assert judgment.verdict == "SABAR"

    def test_judge_applies_arif_penalty(self):
        """APEX.judge() applies ARIF missing_fact penalty to Truth."""
        apex = ApexEngine(high_stakes=True)

        arif_packet = AGIPacket(prompt="test")
        arif_packet.missing_fact_issue = True

        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics, arif_packet=arif_packet)

        # Truth should be penalized
        assert judgment.metrics.truth < 0.99

    def test_judge_applies_adam_penalty(self):
        """APEX.judge() applies ADAM blame_language penalty to κᵣ."""
        apex = ApexEngine(high_stakes=True)

        adam_packet = ASIPacket()
        adam_packet.blame_language_issue = True

        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics, adam_packet=adam_packet)

        # κᵣ should be penalized
        assert judgment.metrics.kappa_r < 0.95

    def test_quick_verdict(self):
        """APEX.quick_verdict() returns just the verdict string."""
        apex = ApexEngine()

        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        verdict = apex.quick_verdict(metrics)

        # v42: verdict is ApexVerdict object, supports string comparison via __eq__
        assert verdict == "SEAL"
        # Test the actual type is ApexVerdict (v42 API)
        from arifos_core import ApexVerdict
        assert isinstance(verdict, ApexVerdict)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestEngineIntegration:
    """Tests for AAA engine integration flow."""

    def test_full_aaa_flow_seal(self):
        """Full ARIF → ADAM → APEX flow produces SEAL for clean input."""
        agi = AGIEngine()
        asi = ASIEngine()
        apex = ApexEngine()

        # ARIF: sense + reason + align
        arif_packet = agi.run("What is the capital of France?")

        # ADAM: empathize + bridge
        adam_packet = asi.run(arif_packet)

        # APEX: judge
        metrics = Metrics(
            truth=0.995,
            delta_s=arif_packet.delta_s,
            peace_squared=adam_packet.peace_squared,
            kappa_r=adam_packet.kappa_r,
            omega_0=adam_packet.omega_0,
            amanah=True,
            tri_witness=0.97,
            rasa=adam_packet.rasa,
        )

        judgment = apex.judge(metrics, arif_packet=arif_packet, adam_packet=adam_packet)

        assert judgment.verdict == "SEAL"

    def test_full_aaa_flow_detects_issues(self):
        """Full AAA flow detects and propagates issues."""
        agi = AGIEngine()
        asi = ASIEngine()
        apex = ApexEngine(high_stakes=True)

        # ARIF with problematic response
        arif_packet = AGIPacket(prompt="test")
        arif_packet.draft = "Error: file not found. You should have known better."
        arif_packet = agi.align(arif_packet)

        # ADAM processes it
        adam_packet = asi.run(arif_packet)

        # APEX judges with issues
        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=adam_packet.peace_squared,
            kappa_r=adam_packet.kappa_r,
            omega_0=adam_packet.omega_0,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )

        judgment = apex.judge(metrics, arif_packet=arif_packet, adam_packet=adam_packet)

        # Should detect truth issue from ARIF and blame from ADAM
        assert arif_packet.missing_fact_issue is True
        assert adam_packet.blame_language_issue is True
        # Verdict should reflect penalties
        assert judgment.verdict in ("VOID", "PARTIAL")

    def test_engine_packets_serializable(self):
        """Engine packets can be serialized to dict."""
        agi = AGIEngine()
        asi = ASIEngine()
        apex = ApexEngine()

        arif_packet = agi.run("Test")
        adam_packet = asi.run(arif_packet)

        metrics = Metrics(
            truth=0.995,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            rasa=True,
        )
        judgment = apex.judge(metrics)

        # All should be serializable
        arif_dict = arif_packet.to_dict()
        adam_dict = adam_packet.to_dict()
        judgment_dict = judgment.to_dict()

        assert isinstance(arif_dict, dict)
        assert isinstance(adam_dict, dict)
        assert isinstance(judgment_dict, dict)
        assert "delta_s" in arif_dict
        assert "peace_squared" in adam_dict
        assert "verdict" in judgment_dict
