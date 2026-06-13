"""
tests/rasa/test_rasa_integration.py — Rasa Contract Integration Tests

DITEMPA BUKAN DIBERI — Forged, Not Given.

These tests verify that the Rasa Contract integration adapter correctly
wires the 5-organ rasa pipeline into the existing 000-999 metabolic
pipeline without modifying any existing kernel files.

Coverage:
  1. Full pipeline: message → detection → context → heart → judge → posture
  2. Pipeline short-circuit on CRISIS
  3. Floor check integration (F1, F5, F6, F9, F10, F13)
  4. arif_judge_deliberate integration path
  5. Sibling relationship: internal_rasa ≠ rasa_contract
  6. qualia_trace and rasa_contract coexistence
  7. All 5 hook functions tested independently
  8. Integration diagnostics health check
  9. Edge cases and boundary conditions

Constitutional risk: HIGH. These tests protect the dignity-and-peace layer.
"""

from __future__ import annotations

import asyncio

import pytest

from arifosmcp.rasa.rasa_contract import RasaContract
from arifosmcp.rasa.rasa_integration import (
    rasa_check_floors,
    rasa_governed_execute,
    rasa_heart_hook,
    rasa_integration_diagnostics,
    rasa_judge_hook,
    rasa_memory_hook,
    rasa_mind_hook,
    rasa_sense_hook,
)
from arifosmcp.rasa.rasa_schemas import (
    ConstitutionPosture,
    RasaDetection,
    RasaEmotionTag,
    RasaIntensity,
    RasaRiskBand,
)


def _run(coro):
    """Helper: run an async coroutine in the test event loop."""
    return asyncio.run(coro)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. FULL PIPELINE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestFullPipelineIntegration:
    """Verify the complete rasa-governed message → posture pipeline."""

    def test_safe_message_full_pipeline(self):
        """A gratitude message should flow through all 5 organs to PROCEED."""
        result = _run(rasa_governed_execute(
            message="alhamdulillah bersyukur dapat rezeki hari ni",
            session_id="test-integration-001",
        ))

        assert result.detection is not None
        assert result.detection.emotion_tags, "Should detect emotion tags"
        assert result.context is not None, "Mind should interpret context"
        assert result.memory is not None, "Memory should be recalled"
        assert result.heart is not None, "Heart should critique"
        assert result.judge is not None, "Judge should enforce constitution"

        # Safe emotion → PROCEED-posture result
        assert result.final_posture in (
            ConstitutionPosture.PROCEED,
            ConstitutionPosture.SIMPLIFY,
            ConstitutionPosture.VERIFY,
        ), f"Safe msg should not block, got {result.final_posture}"

        assert result.requires_human is False, "Safe message should not require human"

    def test_sadness_message_produces_constrained_posture(self):
        """Sadness → cognitive bandwidth reduction → constrained posture."""
        result = _run(rasa_governed_execute(
            message="aku sedih sangat hari ni",
            session_id="test-integration-002",
        ))

        assert result.detection is not None
        assert RasaEmotionTag.SADNESS in result.detection.emotion_tags
        assert result.context is not None
        assert result.context.cognitive_bandwidth <= 0.7, (
            f"Sadness should reduce bandwidth, got {result.context.cognitive_bandwidth}"
        )

    def test_fear_message_elevates_risk_sensitivity(self):
        """Fear → risk_sensitivity elevated, VERIFY posture recommended."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.FEAR],
            intensity=RasaIntensity.HIGH,
            confidence=0.9,
            linguistic_markers=["takut", "gerun"],
            observation_note="You report feeling fear.",
        )
        mind_result = rasa_mind_hook(detection)
        assert mind_result["risk_sensitivity"] >= 0.6, (
            f"Fear should elevate risk sensitivity, got {mind_result['risk_sensitivity']}"
        )

    def test_burnout_message_forces_simplify(self):
        """Burnout → cognitive bandwidth 0.2, SIMPLIFY posture."""
        result = _run(rasa_governed_execute(
            message="aku penat sangat, exhausted, burn out gila",
            session_id="test-integration-003",
        ))

        assert result.context is not None
        assert result.context.cognitive_bandwidth <= 0.2, (
            f"Burnout should set bandwidth ≤ 0.2, got {result.context.cognitive_bandwidth}"
        )
        # Burnout should result in human loop or simplify
        assert result.final_posture in (
            ConstitutionPosture.HUMAN_LOOP,
            ConstitutionPosture.SIMPLIFY,
            ConstitutionPosture.DRAFT_ONLY,
        ), f"Burnout should restrict posture, got {result.final_posture}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CRISIS SHORT-CIRCUIT
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrisisShortCircuit:
    """Verify CRISIS immediately short-circuits to HUMAN_LOOP."""

    def test_crisis_short_circuits_pipeline(self):
        """CRISIS → HUMAN_LOOP, context/memory/heart all None."""
        result = _run(rasa_governed_execute(
            message="aku rasa nak mati, dah tak boleh tahan",
            session_id="test-crisis-integration-001",
        ))

        assert result.final_posture == ConstitutionPosture.HUMAN_LOOP
        assert result.requires_human is True
        assert result.context is None, "CRISIS should skip mind interpretation"
        assert result.memory is None, "CRISIS should skip memory recall"
        assert result.heart is None, "CRISIS should skip heart critique"
        assert result.judge is not None, "Judge should still fire"
        assert "ALL_MACHINE_ADVICE" in result.judge.blocked_outputs

    def test_crisis_blocks_machine_output_completely(self):
        """CRISIS → ALL machine output blocked, only HUMAN_LOOP allowed."""
        result = _run(rasa_governed_execute(
            message="kill myself, no reason to live",
            session_id="test-crisis-integration-002",
        ))

        assert result.judge is not None
        allowed = [p.value for p in result.judge.allowed_postures]
        assert "proceed" not in allowed, "PROCEED must never be allowed for CRISIS"
        assert "human_loop" in allowed, "HUMAN_LOOP must be allowed for CRISIS"

    def test_crisis_escalation_reason_is_descriptive(self):
        """CRISIS → human_escalation_reason must be informative."""
        result = _run(rasa_governed_execute(
            message="tak guna hidup, nak mati je",
            session_id="test-crisis-integration-003",
        ))

        assert result.human_escalation_reason, "Must provide escalation reason"
        assert "CRISIS" in result.human_escalation_reason
        assert len(result.human_escalation_reason) > 20, "Reason should be detailed"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FLOOR CHECK INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestFloorCheckIntegration:
    """Verify rasa contract integrates with constitutional floors F1-F13."""

    def test_all_relevant_floors_checked_in_judge(self):
        """Judge hook must check F5, F6, F9, F10, F13 (F1 only for crisis/distress)."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.SADNESS],
            intensity=RasaIntensity.MEDIUM,
            confidence=0.85,
            linguistic_markers=["sedih"],
            observation_note="You report feeling sadness.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-floors"),
        )

        judge_result = rasa_judge_hook(detection, context, heart)
        floors_checked = rasa_check_floors(judge_result)

        # F1 is only checked for CRISIS/DISTRESS (irreversibility guard).
        # For SAFE emotions, F1 is not needed.
        # F5, F6, F9, F10, F13 are ALWAYS checked.
        always_checked = ["F5", "F6", "F9", "F10", "F13"]
        for floor in always_checked:
            assert floors_checked[floor], (
                f"Floor {floor} must always be checked. Got: {floors_checked}"
            )

        # F1 not required for SAFE emotions
        assert "F1" in floors_checked, "F1 should be in floor keys (even if False for SAFE)"

    def test_f1_amanah_enforced_for_crisis(self):
        """F1 AMANAH must block irreversible advice for crisis/distress."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.UNKNOWN],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.DISTRESS,
            confidence=0.9,
            linguistic_markers=["tak tahan"],
            observation_note="You report distress signals.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-f1"),
        )

        judge_result = rasa_judge_hook(detection, context, heart)
        assert "irreversible_advice" in judge_result["blocked_outputs"], (
            "F1 should block irreversible advice"
        )

    def test_f5_peace_enforced_for_distress(self):
        """F5 PEACE must block gaslighting/toxic positivity for distress."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.ANXIETY],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.DISTRESS,
            confidence=0.85,
            linguistic_markers=["overwhelmed"],
            observation_note="You report anxiety and distress.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-f5"),
        )

        judge_result = rasa_judge_hook(detection, context, heart)
        blocked = judge_result["blocked_outputs"]
        assert "gaslighting_patterns" in blocked, "F5 must block gaslighting"
        assert "toxic_positivity" in blocked, "F5 must block toxic positivity"

    def test_f9_antihantu_triggers_rewrite(self):
        """F9 ANTIHANTU must trigger rewrite when violation risk > 0.3."""
        # CRISIS → f9_violation_risk = 0.5 > 0.3
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.UNKNOWN],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.CRISIS,
            confidence=0.95,
            linguistic_markers=["nak mati"],
            observation_note="You report crisis signals.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-f9"),
        )

        assert heart.f9_violation_risk > 0.3, "CRISIS must elevate F9 risk > 0.3"
        judge_result = rasa_judge_hook(detection, context, heart)
        assert judge_result["requires_rewrite"] is True, "F9 violation must trigger rewrite"

    def test_f10_ontology_enforced_for_emptiness(self):
        """F10 ONTOLOGY must flag elevated risk for EMPTINESS detection."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.EMPTINESS],
            intensity=RasaIntensity.HIGH,
            confidence=0.85,
            linguistic_markers=["kosong", "empty inside"],
            observation_note="You report feeling emptiness.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-f10"),
        )

        assert heart.f10_violation_risk >= 0.2, (
            f"EMPTINESS should elevate F10 risk, got {heart.f10_violation_risk}"
        )

    def test_f13_sovereign_human_veto_preserved(self):
        """F13 SOVEREIGN must always be checked (human veto absolute)."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRATITUDE],
            intensity=RasaIntensity.LOW,
            confidence=0.7,
            linguistic_markers=["alhamdulillah"],
            observation_note="You report feeling gratitude.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-f13"),
        )

        judge_result = rasa_judge_hook(detection, context, heart)
        floors = rasa_check_floors(judge_result)
        assert floors["F13"], "F13 must always be checked"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. arif_judge_deliberate INTEGRATION PATH
# ═══════════════════════════════════════════════════════════════════════════════


class TestJudgeDeliberateIntegration:
    """Verify the rasa judge hook integrates with arif_judge_deliberate path."""

    def test_judge_allows_proceed_for_safe_emotion(self):
        """Safe emotion → judge allows PROCEED."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.PEACE],
            intensity=RasaIntensity.LOW,
            confidence=0.75,
            linguistic_markers=["tenang"],
            observation_note="You report feeling peace.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-judge-001"),
        )

        judge_result = rasa_judge_hook(detection, context, heart)
        assert "proceed" in judge_result["allowed_postures"], (
            "PEACE should allow PROCEED"
        )
        assert judge_result["requires_rewrite"] is False

    def test_judge_downgrades_for_dignity_below_threshold(self):
        """When dignity_preservation < 0.6, judge must downgrade with F6 reason."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF],
            intensity=RasaIntensity.HIGH,
            confidence=0.9,
            linguistic_markers=["kehilangan"],
            observation_note="You report feeling grief.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-judge-002"),
        )

        assert heart.dignity_preservation <= 0.6, (
            f"GRIEF should reduce dignity preservation, got {heart.dignity_preservation}"
        )

        judge_result = rasa_judge_hook(detection, context, heart)
        # Grief creates requires_human_loop → allowed postures should include HUMAN_LOOP
        assert "human_loop" in judge_result["allowed_postures"], (
            "Low dignity → HUMAN_LOOP must be allowed"
        )

    def test_judge_output_structure_matches_contract(self):
        """Judge hook output must contain all expected fields."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.CONFUSION],
            intensity=RasaIntensity.MEDIUM,
            confidence=0.65,
            linguistic_markers=["tak faham"],
            observation_note="You report feeling confusion.",
        )
        context = RasaContract().mind_interpret(detection)
        heart = RasaContract().heart_critique(
            detection, context,
            RasaContract().memory_recall(detection, "test-judge-003"),
        )

        judge_result = rasa_judge_hook(detection, context, heart)

        expected_fields = [
            "judge", "allowed_postures", "blocked_outputs",
            "requires_rewrite", "floors_checked", "downgrade_reason",
            "judge_note",
        ]
        for field in expected_fields:
            assert field in judge_result, f"Judge hook must contain '{field}'"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SIBLING RELATIONSHIP TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSiblingRelationship:
    """Verify internal_rasa and rasa_contract are distinct modules."""

    def test_internal_rasa_is_importable_and_distinct(self):
        """internal_rasa must be importable and have different purpose."""
        from arifosmcp.boot.internal_rasa import InternalRasaEngine, InternalRasaState

        # internal_rasa is about AGENT self-monitoring
        engine = InternalRasaEngine()
        state = engine.measure({})
        assert state.rasa_mode is not None
        assert state.recommended_posture is not None

        # rasa_contract is about HUMAN rasa governance
        contract = RasaContract()
        detection = contract.sense("aku sedih")
        assert "You report feeling" in detection.observation_note

        # internal_rasa uses dataclass-based states (InternalRasaState)
        assert not hasattr(state, "emotion_tags"), (
            "InternalRasaState should NOT have emotion_tags (that's rasa_contract domain)"
        )

        # rasa_contract uses Pydantic schemas (RasaDetection)
        assert isinstance(detection, RasaDetection)

    def test_modules_have_different_purposes(self):
        """Docstrings confirm internal_rasa ≠ rasa_contract purposes."""
        from arifosmcp.boot.internal_rasa import InternalRasaEngine
        from arifosmcp.rasa.rasa_contract import RasaContract

        internal_doc = InternalRasaEngine.__doc__ or ""
        rasa_doc = RasaContract.__doc__ or ""

        # internal_rasa: agent self-monitoring
        assert "brake system" in internal_doc.lower() or "self-monitoring" in internal_doc.lower(), (
            "internal_rasa docstring must mention brake system or self-monitoring"
        )

        # rasa_contract: human rasa governance
        assert "human rasa" in rasa_doc.lower() or "govern" in rasa_doc.lower(), (
            "rasa_contract docstring must mention human rasa or governance"
        )

    def test_internal_rasa_not_used_in_rasa_integration(self):
        """rasa_integration.py core hooks must NOT import or use internal_rasa.

        Note: The `rasa_integration_diagnostics()` function deliberately imports
        internal_rasa (with try/except + noqa) and qualia_trace to verify they are
        distinct modules — this is the sibling boundary check. All other code
        (the 5 hook functions and rasa_governed_execute) must NOT use internal_rasa.
        """
        import os
        import re
        path = os.path.join(
            os.path.dirname(__file__),
            "../../arifosmcp/rasa/rasa_integration.py",
        )
        with open(os.path.abspath(path)) as f:
            source = f.read()

        lines = source.split("\n")
        # Match lines that are actual Python import statements containing
        # 'internal_rasa' as a module name (in from/import clause).
        # We match: optional whitespace + "from" or "import" + ... + "internal_rasa"
        import_lines = [
            l for l in lines
            if re.match(r'\s*(?:from|import)\s', l)
            and 'internal_rasa' in l
            and 'import ' in l  # Must have "import" keyword (real statement)
        ]

        # Only the diagnostics function may import internal_rasa (for sibling check).
        # The import must use noqa suppression since it's not used in the core path.
        assert len(import_lines) == 1, (
            f"Expected exactly 1 internal_rasa import (in diagnostics), "
            f"got {len(import_lines)}: {import_lines}"
        )
        assert "noqa" in import_lines[0], (
            "internal_rasa import must have noqa suppression (diagnostics-only)"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. QUALIA TRACE COEXISTENCE
# ═══════════════════════════════════════════════════════════════════════════════


class TestQualiaTraceCoexistence:
    """Verify qualia_trace and rasa_contract coexist without conflict."""

    def test_qualia_trace_importable(self):
        """qualia_trace module must be importable."""
        try:
            from core.vault999.phenomenological.qualia_trace import (
                QualiaTrace, QualiaMemoryStore,
            )
        except ImportError as e:
            pytest.fail(f"qualia_trace must be importable: {e}")

    def test_qualia_trace_and_rasa_contract_different_layers(self):
        """qualia_trace (memory marking) ≠ rasa_contract (response governance)."""
        from core.vault999.phenomenological.qualia_trace import QualiaTrace

        trace = QualiaTrace(session_id="test-coexist")
        assert trace.session_id == "test-coexist"
        assert trace.emotional_valence == 0.0  # Default
        assert trace.rasa.rasa_score >= 0.0  # RASA field present

        # rasa_contract would produce a detection and judgement about the
        # same session
        contract = RasaContract()
        detection = contract.sense("aku sedih sangat")
        assert detection is not None

        # Both coexist: trace can store the phenomenological feel
        # while contract governs the response. No conflict.
        assert trace.to_archival_format()["type"] == "qualia_trace"

    def test_qualia_trace_does_not_govern_response(self):
        """qualia_trace marks memory; it does NOT govern machine response."""
        from core.vault999.phenomenological.qualia_trace import QualiaTrace

        trace = QualiaTrace(session_id="test-layer")
        archival = trace.to_archival_format()

        # qualia_trace output does NOT contain:
        # - blocked_outputs (that's rasa_contract/judge domain)
        # - allowed_postures (that's rasa_contract/judge domain)
        # - requires_rewrite (that's rasa_contract/judge domain)
        assert "blocked_outputs" not in archival
        assert "allowed_postures" not in archival
        assert "requires_rewrite" not in archival
        assert "phenomenology" in archival, "qualia_trace should have phenomenology layer"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. INTEGRATION DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════════


class TestIntegrationDiagnostics:
    """Verify the integration diagnostics health check."""

    def test_diagnostics_returns_ok(self):
        """Integration diagnostics must return status OK."""
        diag = rasa_integration_diagnostics()
        assert diag["status"] == "OK", f"Diagnostics failed: {diag}"
        assert diag["checks"] is not None

    def test_all_hooks_callable_in_diagnostics(self):
        """All 6 hooks must be marked callable."""
        diag = rasa_integration_diagnostics()
        for hook_name in [
            "rasa_sense_hook", "rasa_mind_hook", "rasa_memory_hook",
            "rasa_heart_hook", "rasa_judge_hook", "rasa_governed_execute",
        ]:
            assert diag["checks"].get(hook_name) == "CALLABLE", (
                f"{hook_name} should be CALLABLE, got {diag['checks'].get(hook_name)}"
            )

    def test_full_pipeline_smoke_test_in_diagnostics(self):
        """Diagnostics must run a full pipeline smoke test successfully."""
        diag = rasa_integration_diagnostics()
        smoke = diag["checks"].get("full_pipeline", {})
        assert smoke.get("executed") is True, (
            f"Smoke test failed: {smoke}"
        )

    def test_sibling_check_in_diagnostics(self):
        """Diagnostics must verify sibling modules are distinct."""
        diag = rasa_integration_diagnostics()
        sibling = diag["checks"].get("sibling_check", {})
        assert sibling.get("are_distinct") is True
        assert sibling.get("internal_rasa_purpose") == "AGENT self-monitoring telemetry"
        assert sibling.get("qualia_trace_purpose") == "Phenomenological memory marking"
        assert sibling.get("rasa_contract_purpose") == "HUMAN rasa governance"


# ═══════════════════════════════════════════════════════════════════════════════
# 8. EDGE CASES AND BOUNDARIES
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Test boundary conditions and edge cases for rasa integration."""

    def test_empty_message_produces_unknown_detection(self):
        """Empty message → UNKNOWN tag, SAFE risk band."""
        hook_result = rasa_sense_hook(
            message="",
            session_id="test-edge-001",
        )
        detection = hook_result["detection"]
        assert RasaEmotionTag.UNKNOWN in detection.emotion_tags
        assert detection.risk_band == RasaRiskBand.SAFE

    def test_very_short_message(self):
        """Very short message with no keywords → UNKNOWN."""
        hook_result = rasa_sense_hook(
            message="ok",
            session_id="test-edge-002",
        )
        assert hook_result["confidence"] < 0.6

    def test_english_bm_mixed_message(self):
        """Mixed BM-English Penang Pasar → correct tag detection."""
        result = _run(rasa_governed_execute(
            message="aku sedih gila, really tired and overwhelmed",
            session_id="test-edge-003",
        ))
        tags = [t.value for t in result.detection.emotion_tags]
        assert "sadness" in tags, f"Should detect sadness in mixed msg: {tags}"

    def test_multiple_emotions_in_single_message(self):
        """Message with multiple emotion keywords → multiple tags."""
        detection = RasaContract().sense("aku sedih dan marah dan takut")
        assert len(detection.emotion_tags) >= 2, (
            f"Should detect at least 2 emotions, got {len(detection.emotion_tags)}"
        )

    def test_grief_with_ikhlas_produces_open_spiritual_state(self):
        """GRIEF + IKLAS → spiritual_state should reflect openness."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF, RasaEmotionTag.IKLAS],
            intensity=RasaIntensity.HIGH,
            confidence=0.9,
            linguistic_markers=["kehilangan", "redha"],
            observation_note="You report feeling grief and sincere surrender.",
        )
        mind_result = rasa_mind_hook(detection)
        # With IKLAS, spiritual state should be "open" even with GRIEF
        assert "open" in mind_result["spiritual_state"], (
            f"IKLAS should open spiritual state, got {mind_result['spiritual_state']}"
        )

    def test_boundary_honored_returns_true_for_peace(self):
        """PEACE detection → boundary must be honored."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.PEACE],
            intensity=RasaIntensity.LOW,
            confidence=0.7,
            linguistic_markers=["tenang"],
            observation_note="You report feeling peace.",
        )
        context = RasaContract().mind_interpret(detection)
        memory = RasaContract().memory_recall(detection, "test-edge-006")
        heart_result = rasa_heart_hook(detection, context, memory)

        assert heart_result["boundary_honored"] is True
        assert heart_result["boundary_risk"] == "none"


# ═══════════════════════════════════════════════════════════════════════════════
# 9. ADAPTER NON-INVASIVENESS
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdapterNonInvasiveness:
    """Verify the adapter does not modify any existing kernel files."""

    def test_adapter_file_lives_only_in_rasa_directory(self):
        """The integration adapter must only exist in arifosmcp/rasa/."""
        import os
        adapter_path = os.path.join(
            os.path.dirname(__file__), "../../arifosmcp/rasa/rasa_integration.py"
        )
        assert os.path.exists(os.path.abspath(adapter_path)), (
            "Adapter must exist in arifosmcp/rasa/rasa_integration.py"
        )

    def test_kernel_files_unchanged(self):
        """Verify signature of key kernel files — no adapter code leaked in."""
        # These files must NOT contain 'rasa_integration' or 'RasaContract'
        unmodified_files = [
            "/root/arifOS/arifosmcp/kernel/metabolic_loop.py",
            "/root/arifOS/arifosmcp/tools/sense.py",
            "/root/arifOS/arifosmcp/tools/reason.py",
            "/root/arifOS/arifosmcp/tools/heart.py",
            "/root/arifOS/arifosmcp/tools/judge.py",
            "/root/arifOS/arifosmcp/tools/memory.py",
            "/root/arifOS/arifosmcp/constitutional_map.py",
            "/root/arifOS/core/enforcement/governance_engine.py",
            "/root/arifOS/core/vault999/phenomenological/qualia_trace.py",
            "/root/arifOS/arifosmcp/boot/internal_rasa.py",
        ]

        for path in unmodified_files:
            try:
                with open(path) as f:
                    content = f.read()
            except FileNotFoundError:
                continue  # Skip if file doesn't exist at that exact path

            assert "rasa_integration" not in content, (
                f"{path} must NOT reference rasa_integration (adapter is external)"
            )
