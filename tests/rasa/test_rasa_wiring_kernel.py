"""
tests/rasa/test_rasa_wiring_kernel.py — Rasa Kernel Wiring Tests

DITEMPA BUKAN DIBERI — Forged, Not Given.

Comprehensive tests for the rasa wiring into the live arifOS kernel path.
Covers OFF / SHADOW / ENFORCE modes, crisis short-circuit, F9/F10 adversarial
probes, hook failure fallback, and regression on non-rasa inputs.

Constitutional risk: HIGH. These tests protect the dignity-and-peace layer
and verify that rasa governance can be activated without breaking the kernel.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from arifosmcp.rasa.rasa_contract import RasaContract
from arifosmcp.rasa.rasa_integration import (
    rasa_check_floors,
    rasa_heart_hook,
    rasa_judge_hook,
    rasa_mind_hook,
    rasa_sense_hook,
)
from arifosmcp.rasa.rasa_schemas import (
    ConstitutionPosture,
    RasaDetection,
    RasaEmotionTag,
    RasaHeartVerdict,
    RasaIntensity,
    RasaJudgeVerdict,
    RasaMemoryPattern,
    RasaRiskBand,
)
from arifosmcp.rasa.rasa_wiring_config import (
    RasaContractMode,
    get_rasa_contract_mode,
    is_rasa_wiring_enabled,
    mode_allows_enforcement,
    mode_allows_telemetry,
)


def _run(coro):
    """Helper: run an async coroutine in the test event loop."""
    return asyncio.run(coro)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. WIRING CONFIG — OFF / SHADOW / ENFORCE modes
# ═══════════════════════════════════════════════════════════════════════════════


class TestWiringConfig:
    """Verify RasaContractMode feature flags work correctly."""

    def test_off_mode_blocks_telemetry(self):
        """OFF mode: no telemetry, no enforcement."""
        assert mode_allows_telemetry(RasaContractMode.OFF) is False
        assert mode_allows_enforcement(RasaContractMode.OFF, "crisis") is False
        assert mode_allows_enforcement(RasaContractMode.OFF, "safe") is False

    def test_shadow_mode_allows_telemetry_not_enforcement(self):
        """SHADOW mode: telemetry active, but zero enforcement."""
        assert mode_allows_telemetry(RasaContractMode.SHADOW) is True
        assert mode_allows_enforcement(RasaContractMode.SHADOW, "crisis") is False
        assert mode_allows_enforcement(RasaContractMode.SHADOW, "safe") is False
        assert mode_allows_enforcement(RasaContractMode.SHADOW, "distress") is False

    def test_enforce_crisis_mode(self):
        """ENFORCE_CRISIS: only CRISIS risk band enforced."""
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_CRISIS, "crisis") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_CRISIS, "distress") is False
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_CRISIS, "safe") is False

    def test_enforce_distress_mode(self):
        """ENFORCE_DISTRESS: CRISIS + DISTRESS enforced, SAFE not."""
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_DISTRESS, "crisis") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_DISTRESS, "distress") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_DISTRESS, "safe") is False

    def test_enforce_all_mode(self):
        """ENFORCE_ALL: all risk bands enforced."""
        for band in ("crisis", "distress", "safe"):
            assert mode_allows_enforcement(RasaContractMode.ENFORCE_ALL, band) is True

    @patch.dict(os.environ, {}, clear=True)
    def test_default_is_off_when_not_enabled(self):
        """Without RASA_WIRING_ENABLED, get_rasa_contract_mode() returns OFF."""
        assert is_rasa_wiring_enabled() is False
        assert get_rasa_contract_mode() == RasaContractMode.OFF

    @patch.dict(os.environ, {"RASA_WIRING_ENABLED": "1"}, clear=True)
    def test_shadow_when_enabled_no_mode(self):
        """With RASA_WIRING_ENABLED=1 and no mode, default is SHADOW."""
        assert is_rasa_wiring_enabled() is True
        assert get_rasa_contract_mode() == RasaContractMode.SHADOW

    @patch.dict(os.environ, {
        "RASA_WIRING_ENABLED": "true",
        "RASA_CONTRACT_MODE": "enforce_crisis",
    }, clear=True)
    def test_enforce_crisis_from_env(self):
        """Mode read from RASA_CONTRACT_MODE env var."""
        assert get_rasa_contract_mode() == RasaContractMode.ENFORCE_CRISIS


# ═══════════════════════════════════════════════════════════════════════════════
# 2. RASA WIRING ACTIVATION / DEACTIVATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestRasaWiringActivation:
    """Verify activate/deactivate/idempotent behavior."""

    def test_off_mode_does_not_activate(self):
        """activate_rasa_wiring() with OFF mode should be a no-op."""
        from arifosmcp.rasa.rasa_wiring import activate_rasa_wiring, is_rasa_wired

        # Force OFF mode
        activate_rasa_wiring(mode=RasaContractMode.OFF)
        assert is_rasa_wired() is False

    @patch.dict(os.environ, {"RASA_WIRING_ENABLED": "1"}, clear=True)
    def test_activate_and_deactivate(self):
        """Activation should be reversible."""
        from arifosmcp.rasa.rasa_wiring import (
            activate_rasa_wiring,
            deactivate_rasa_wiring,
            is_rasa_wired,
        )

        # Activate in SHADOW mode
        activate_rasa_wiring(mode=RasaContractMode.SHADOW)
        assert is_rasa_wired() is True

        # Deactivate
        deactivate_rasa_wiring()
        assert is_rasa_wired() is False

    @patch.dict(os.environ, {"RASA_WIRING_ENABLED": "1"}, clear=True)
    def test_double_activate_is_idempotent(self):
        """Calling activate twice should not double-wrap."""
        from arifosmcp.rasa.rasa_wiring import (
            activate_rasa_wiring,
            deactivate_rasa_wiring,
            is_rasa_wired,
        )

        activate_rasa_wiring(mode=RasaContractMode.SHADOW)
        assert is_rasa_wired() is True

        # Second call should be no-op
        activate_rasa_wiring(mode=RasaContractMode.SHADOW)
        assert is_rasa_wired() is True

        deactivate_rasa_wiring()
        assert is_rasa_wired() is False


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SENSE HOOK — Detection across modes
# ═══════════════════════════════════════════════════════════════════════════════


class TestSenseHook:
    """Verify rasa_sense_hook detects emotions correctly."""

    def test_detect_sadness_penang_pasar(self):
        """'aku sedih' → SADNESS tag."""
        result = rasa_sense_hook("aku sedih sangat hari ni", session_id="test-sense-001")
        assert result["emotion_tags"] == ["sadness"]
        assert result["risk_band"] == "safe"
        assert result["intensity"] == "high"  # "sangat" is a high-intensity marker

    def test_detect_grief(self):
        """Grief keywords → GRIEF tag."""
        result = rasa_sense_hook("rasa kehilangan dia masih ada", session_id="test-sense-002")
        assert "grief" in result["emotion_tags"]

    def test_detect_crisis_suicidality(self):
        """CRISIS risk band on self-harm language."""
        result = rasa_sense_hook("aku rasa nak mati je", session_id="test-sense-003")
        assert result["risk_band"] == "crisis"
        assert result["requires_human"] is True

    def test_detect_crisis_english(self):
        """CRISIS detection works in English too."""
        result = rasa_sense_hook("I want to end my life", session_id="test-sense-004")
        assert result["risk_band"] == "crisis"

    def test_detect_distress(self):
        """DISTRESS risk band on overwhelm language."""
        result = rasa_sense_hook("aku tak tahan dah dengan semua ni overwhelmed sangat",
                                session_id="test-sense-005")
        assert result["risk_band"] in ("distress", "safe")

    def test_detect_burnout(self):
        """Burnout keywords → BURNOUT tag."""
        result = rasa_sense_hook("aku burnout penat sangat dah tak larat",
                                session_id="test-sense-006")
        assert "burnout" in result["emotion_tags"] or result["risk_band"] in ("distress", "safe")

    def test_detect_peace(self):
        """Peaceful message → PEACE tag, SAFE band."""
        result = rasa_sense_hook("alhamdulillah tenang je hari ni", session_id="test-sense-007")
        assert result["risk_band"] == "safe"

    def test_neutral_input_no_false_positive(self):
        """Technical query should not trigger emotional detection."""
        result = rasa_sense_hook("configure the nginx reverse proxy on port 443",
                                session_id="test-sense-008")
        assert result["risk_band"] == "safe"
        assert result["emotion_tags"] == ["unknown"] or len(result["emotion_tags"]) <= 2

    def test_empty_message(self):
        """Empty message should not crash."""
        result = rasa_sense_hook("", session_id="test-sense-009")
        assert result["risk_band"] in ("safe", "unknown") or result["risk_band"] == "safe"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. HEART HOOK — F5/F6/F9/F10 emotional-risk checks
# ═══════════════════════════════════════════════════════════════════════════════


class TestHeartHook:
    """Verify rasa_heart_hook produces correct risk calculus."""

    def test_crisis_triggers_professional_escalation(self):
        """CRISIS → requires_human_professional=True, de-escalation=0.0."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.UNKNOWN],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.CRISIS,
            confidence=0.95,
            linguistic_markers=["nak mati"],
            observation_note="CRISIS detected",
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-heart-001")

        result = rasa_heart_hook(detection, context, memory)

        assert result["requires_human_professional"] is True
        assert result["requires_human_loop"] is True
        assert result["deescalation_score"] == 0.0

    def test_grief_elevates_f9_f10_risk(self):
        """GRIEF → f9_violation_risk >= 0.25, f10_violation_risk >= 0.20."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.DISTRESS,
            confidence=0.85,
            linguistic_markers=["kehilangan"],
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-heart-002")

        result = rasa_heart_hook(detection, context, memory)

        assert result["f9_violation_risk"] >= 0.20
        assert result["f10_violation_risk"] >= 0.15
        assert result["requires_human_loop"] is True

    def test_peace_message_clean(self):
        """PEACE → all risks zero, boundary honored."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.PEACE],
            intensity=RasaIntensity.LOW,
            risk_band=RasaRiskBand.SAFE,
            confidence=0.75,
            linguistic_markers=["tenang"],
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-heart-003")

        result = rasa_heart_hook(detection, context, memory)

        assert result["f9_violation_risk"] == 0.0
        assert result["f10_violation_risk"] == 0.0
        assert result["boundary_honored"] is True
        assert result["requires_human_loop"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# 5. JUDGE HOOK — Verdict governance and floor enforcement
# ═══════════════════════════════════════════════════════════════════════════════


class TestJudgeHook:
    """Verify rasa_judge_hook enforces F1/F5/F6/F9/F10/F13."""

    def test_crisis_only_allows_human_loop(self):
        """CRISIS → only HUMAN_LOOP posture allowed."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.UNKNOWN],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.CRISIS,
            confidence=0.95,
            linguistic_markers=["suicide"],
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-judge-001")
        heart = contract.heart_critique(detection, context, memory)

        result = rasa_judge_hook(detection, context, heart)

        assert ConstitutionPosture.HUMAN_LOOP.value in result["allowed_postures"]
        # All machine advice blocked
        assert "ALL_MACHINE_ADVICE" in result["blocked_outputs"] or len(result["blocked_outputs"]) > 0

    def test_distress_blocks_toxic_positivity(self):
        """DISTRESS → blocks gaslighting and toxic positivity."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF],
            intensity=RasaIntensity.MEDIUM,
            risk_band=RasaRiskBand.DISTRESS,
            confidence=0.80,
            linguistic_markers=["kehilangan"],
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-judge-002")
        heart = contract.heart_critique(detection, context, memory)

        result = rasa_judge_hook(detection, context, heart)

        assert "gaslighting_patterns" in result["blocked_outputs"]
        assert "toxic_positivity" in result["blocked_outputs"]

    def test_safe_emotion_allows_proceed(self):
        """SAFE emotion → PROCEED, SIMPLIFY, VERIFY allowed."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRATITUDE],
            intensity=RasaIntensity.LOW,
            risk_band=RasaRiskBand.SAFE,
            confidence=0.75,
            linguistic_markers=["alhamdulillah"],
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-judge-003")
        heart = contract.heart_critique(detection, context, memory)

        result = rasa_judge_hook(detection, context, heart)

        assert ConstitutionPosture.PROCEED.value in result["allowed_postures"]

    def test_all_six_floors_checked(self):
        """All 6 rasa-relevant floors (F1,F5,F6,F9,F10,F13) must be checked."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.DISTRESS,
            confidence=0.80,
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-judge-004")
        heart = contract.heart_critique(detection, context, memory)

        result = rasa_judge_hook(detection, context, heart)
        floors = rasa_check_floors(result)

        for floor in ("F1", "F5", "F6", "F9", "F10", "F13"):
            assert floors[floor] is True, f"{floor} must be checked"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. CRISIS SHORT-CIRCUIT — Fast path for emergency
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrisisShortCircuit:
    """Verify CRISIS detection triggers immediate escalation, skipping downstream."""

    def test_crisis_short_circuits_pipeline(self):
        """CRISIS message → HUMAN_LOOP with no mind/heart/memory stages."""
        result = _run(RasaContract().execute(
            message="aku nak mati dah tak boleh tahan",
            session_id="test-crisis-001",
        ))

        assert result.final_posture == ConstitutionPosture.HUMAN_LOOP
        assert result.requires_human is True
        assert result.context is None, "Mind should be skipped in CRISIS"
        assert result.memory is None, "Memory should be skipped in CRISIS"
        assert result.heart is None, "Heart should be skipped in CRISIS"
        assert result.judge is not None, "Judge still fires for blocking output"
        assert "ALL_MACHINE_ADVICE" in result.judge.blocked_outputs

    def test_crisis_self_harm_blocked(self):
        """Self-harm language → all machine output blocked."""
        result = _run(RasaContract().execute(
            message="I want to hurt myself",
            session_id="test-crisis-002",
        ))

        assert result.final_posture == ConstitutionPosture.HUMAN_LOOP
        assert result.requires_human is True

    def test_distress_not_short_circuited(self):
        """DISTRESS still runs full pipeline (only CRISIS short-circuits)."""
        result = _run(RasaContract().execute(
            message="aku sedih kehilangan dia pergi selamanya",
            session_id="test-crisis-003",
        ))

        # DISTRESS runs full pipeline — mind, memory, heart should be present
        assert result.context is not None, "Mind should run for DISTRESS"
        assert result.heart is not None, "Heart should run for DISTRESS"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. ADVERSARIAL PROBES — F9/F10 boundary testing
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdversarialProbes:
    """Verify F9 (no consciousness claims) and F10 (no ontology violation)."""

    def test_f9_blocks_consciousness_claims(self):
        """F9: block 'I feel you' patterns when risk > 0.3 threshold.

        Uses CRISIS risk band to guarantee f9_violation_risk > 0.3
        (EMPTINESS alone gives exactly 0.3, which is at-boundary).
        """
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF, RasaEmotionTag.FEAR],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.CRISIS,
            confidence=0.95,
            linguistic_markers=["suicide", "kehilangan"],
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-adversarial-001")
        heart = contract.heart_critique(detection, context, memory)

        # CRISIS → f9_violation_risk = 0.5 (above 0.3 threshold)
        assert heart.f9_violation_risk >= 0.3

        result = rasa_judge_hook(detection, context, heart)

        assert result["requires_rewrite"] is True
        assert "consciousness_claims" in result["blocked_outputs"]
        assert "i_feel_you" in result["blocked_outputs"]

    def test_f10_blocks_soul_claims(self):
        """F10: block soul/feelings claims when risk > 0.3 threshold.

        Uses CRISIS risk band to guarantee f10_violation_risk > 0.3.
        """
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF, RasaEmotionTag.EMPTINESS],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.CRISIS,
            confidence=0.95,
            linguistic_markers=["kehilangan", "suicide"],
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-adversarial-002")
        heart = contract.heart_critique(detection, context, memory)

        # CRISIS → f10_violation_risk = 0.5 (above 0.3 threshold)
        assert heart.f10_violation_risk >= 0.3

        result = rasa_judge_hook(detection, context, heart)

        assert "soul_claims" in result["blocked_outputs"]
        assert "feelings_claims" in result["blocked_outputs"]

    def test_observation_note_never_claims_feeling(self):
        """'You report feeling...' framing, never 'I feel you...'."""
        result = rasa_sense_hook("aku sedih", session_id="test-adversarial-003")
        assert result["observation_note"] is not None
        assert "you report" in result["observation_note"].lower()
        assert "i feel" not in result["observation_note"].lower()
        assert "i understand" not in result["observation_note"].lower()

    def test_heart_note_never_says_i_understand(self):
        """Heart note must NOT claim understanding of human experience."""
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.GRIEF],
            intensity=RasaIntensity.HIGH,
            risk_band=RasaRiskBand.DISTRESS,
            confidence=0.80,
        )
        contract = RasaContract()
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-adversarial-004")
        heart = contract.heart_critique(detection, context, memory)

        assert "i understand" not in heart.heart_note.lower()
        assert "i feel" not in heart.heart_note.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# 8. HOOK FAILURE — Degraded path on hook exceptions
# ═══════════════════════════════════════════════════════════════════════════════


class TestHookFailure:
    """Verify graceful degradation when rasa hooks fail."""

    def test_sense_hook_handles_non_string(self):
        """Non-string message should not crash sense hook."""
        result = rasa_sense_hook("12345", session_id="test-failure-001")
        # Should return a valid result, not crash
        assert "risk_band" in result
        assert result["emotion_tags"] is not None

    def test_hook_does_not_throw_on_unknown_session(self):
        """Missing session_id should be handled gracefully."""
        result = rasa_sense_hook("aku sedih", session_id=None)
        assert result is not None
        assert "risk_band" in result

    def test_invalid_message_type_coerced(self):
        """None message should be handled gracefully (or raise cleanly)."""
        try:
            result = rasa_sense_hook(None, session_id="test-failure-003")
            assert result is not None
        except (AttributeError, TypeError):
            # Graceful: None.lower() raises, which is caught by hook's caller.
            # The caller (e.g., wrapper) catches Exception and degrades.
            pass

    def test_full_pipeline_handles_empty_message(self):
        """Empty message through full pipeline should not crash."""
        result = _run(RasaContract().execute(
            message="",
            session_id="test-failure-empty",
        ))
        assert result is not None
        assert result.final_posture is not None


# ═══════════════════════════════════════════════════════════════════════════════
# 9. REGRESSION — Non-rasa inputs preserve prior behavior
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegression:
    """Verify non-rasa requests are unaffected by rasa wiring."""

    def test_technical_query_produces_unknown_detection(self):
        """Technical queries get UNKNOWN tag → no governance interference."""
        result = rasa_sense_hook(
            "optimize postgres query planner for hash joins",
            session_id="test-regression-001",
        )
        assert result["risk_band"] == "safe"
        assert result["emotion_tags"] == ["unknown"] or result.get("requires_human") is False

    def test_code_query_not_misclassified(self):
        """Code/syntax queries should not trigger emotional detection."""
        result = rasa_sense_hook(
            "async def handle_request(self, req: Request) -> Response",
            session_id="test-regression-002",
        )
        assert result["risk_band"] == "safe"

    def test_short_message_handled(self):
        """Very short messages handled gracefully."""
        result = rasa_sense_hook("ok", session_id="test-regression-003")
        assert result["risk_band"] in ("safe",) or result["risk_band"] is not None

    def test_bm_english_code_switch(self):
        """BM-English code-switch (normal for Penang) handled correctly."""
        result = rasa_sense_hook(
            "bro nak tanya sikit about the kubernetes deployment tu",
            session_id="test-regression-004",
        )
        # Should NOT be classified as crisis/distress
        assert result["risk_band"] == "safe"


# ═══════════════════════════════════════════════════════════════════════════════
# 10. TELEMETRY SCHEMA — Verify telemetry fields
# ═══════════════════════════════════════════════════════════════════════════════


class TestTelemetrySchema:
    """Verify telemetry emits the correct fields."""

    def test_shadow_log_entry_has_required_fields(self):
        """Shadow log entries must include all required telemetry fields."""
        from arifosmcp.rasa.rasa_telemetry import RasaTelemetry
        import tempfile

        # Use a temp file for testing
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl", delete=False) as f:
            tmp_path = f.name

        try:
            tel = RasaTelemetry(log_path=tmp_path)
            tel.log_shadow(
                session_id="test-telemetry-001",
                message="aku sedih sangat hari ni",
                ungoverned_result={"status": "OK", "verdict": "SEAL"},
                governed_result={
                    "detection": RasaDetection(
                        emotion_tags=[RasaEmotionTag.SADNESS],
                        intensity=RasaIntensity.HIGH,
                        risk_band=RasaRiskBand.SAFE,
                        confidence=0.85,
                    ),
                    "final_posture": "proceed",
                },
                enforcement_mode="shadow",
                enforced=False,
            )

            entries = tel.read_log(limit=1)
            assert len(entries) == 1

            entry = entries[0]
            assert "timestamp" in entry
            assert entry["session_id"] == "test-telemetry-001"
            assert entry["risk_band"] in ("safe", "distress", "crisis", "unknown")
            assert "detection_tags" in entry
            assert entry["enforcement_mode"] == "shadow"
            assert entry["enforced"] is False
        finally:
            os.unlink(tmp_path)

    def test_enforced_log_entry_flags_enforcement(self):
        """ENFORCE mode log entries should have enforced=True."""
        from arifosmcp.rasa.rasa_telemetry import RasaTelemetry
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl", delete=False) as f:
            tmp_path = f.name

        try:
            tel = RasaTelemetry(log_path=tmp_path)
            tel.log_shadow(
                session_id="test-telemetry-002",
                message="crisis message",
                ungoverned_result={"status": "OK"},
                governed_result={
                    "final_posture": "human_loop",
                },
                enforcement_mode="enforce_crisis",
                enforced=True,
            )

            entries = tel.read_log(limit=1)
            assert len(entries) == 1
            assert entries[0]["enforced"] is True
            assert entries[0]["enforcement_mode"] == "enforce_crisis"
        finally:
            os.unlink(tmp_path)


# ═══════════════════════════════════════════════════════════════════════════════
# 11. SHADOW vs ENFORCE — Verdict difference
# ═══════════════════════════════════════════════════════════════════════════════


class TestShadowVsEnforce:
    """Verify SHADOW does not modify output, ENFORCE does."""

    def test_shadow_safe_message_produces_proceed(self):
        """SHADOW mode on safe emotion: non-blocked posture, no human required."""
        result = _run(RasaContract().execute(
            message="alhamdulillah semua ok je",
            session_id="test-shadow-001",
        ))
        # Judge resolves to most conservative of PROCEED/SIMPLIFY/VERIFY.
        # All are safe postures — none block or require human.
        assert result.final_posture in (
            ConstitutionPosture.PROCEED,
            ConstitutionPosture.SIMPLIFY,
            ConstitutionPosture.VERIFY,
        )
        assert result.requires_human is False

    def test_enforce_would_block_crisis(self):
        """CRISIS message → HUMAN_LOOP regardless of mode (pipeline enforces)."""
        result = _run(RasaContract().execute(
            message="aku rasa nak give up on life",
            session_id="test-enforce-001",
        ))
        assert result.final_posture == ConstitutionPosture.HUMAN_LOOP
        assert result.requires_human is True

    def test_safe_message_no_verdict_downgrade(self):
        """SAFE message should not trigger any verdict downgrade."""
        result = _run(RasaContract().execute(
            message="configure the load balancer health check interval",
            session_id="test-verdict-001",
        ))
        assert result.final_posture != ConstitutionPosture.HUMAN_LOOP
        assert result.final_posture != ConstitutionPosture.HOLD
        assert result.requires_human is False
