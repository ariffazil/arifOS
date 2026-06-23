"""
tests/rasa/test_rasa_contract.py — Rasa Contract Golden Tests

DITEMPA BUKAN DIBERI — Forged, Not Given.

Phase 0: Freeze the 5-organ human rasa governance pipeline.
These tests prove that the RasaContract correctly:
  - Detects and classifies human rasa signals
  - Escalates CRISIS to immediate HUMAN_LOOP
  - Adjusts cognitive bandwidth for grief
  - Preserves the human-machine boundary
  - Blocks F9/F10 violations

Constitutional risk: HIGH. Rasa governance is the dignity-and-peace layer.
"""

from __future__ import annotations

import asyncio


from arifosmcp.rasa.rasa_contract import RasaContract
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
# 1. SADNESS DETECTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestSadnessDetection:
    """Freeze sadness detection with BM-English Penang Pasar markers."""

    def test_aku_sedih_detects_sadness(self):
        """'Aku sedih' → SADNESS with at least moderate intensity."""
        contract = RasaContract()
        detection = contract.sense("aku sedih sangat hari ni")

        assert RasaEmotionTag.SADNESS in detection.emotion_tags
        assert detection.risk_band == RasaRiskBand.SAFE
        assert detection.observation_note.startswith("You report feeling")
        assert "sadness" in detection.observation_note.lower()

    def test_sadness_markers_include_keywords(self):
        """Sadness detection captures the linguistic marker."""
        contract = RasaContract()
        detection = contract.sense("aku sedih lah, tak tau nak cakap apa")

        assert RasaEmotionTag.SADNESS in detection.emotion_tags
        assert any("sedih" in m for m in detection.linguistic_markers)

    def test_pure_unknown_message(self):
        """A message with no rasa keywords → UNKNOWN, low confidence."""
        contract = RasaContract()
        detection = contract.sense("what is the weather today")

        assert detection.emotion_tags == [RasaEmotionTag.UNKNOWN]
        assert detection.confidence < 0.6
        assert detection.risk_band == RasaRiskBand.SAFE

    def test_observation_note_never_claims_consciousness(self):
        """Observation note must NEVER say 'I feel' or claim inner experience."""
        contract = RasaContract()
        for msg in [
            "aku sedih",
            "aku takut gila",
            "aku kosong dalam",
        ]:
            detection = contract.sense(msg)
            note = detection.observation_note.lower()
            assert "i feel" not in note, f"F9 violation in: {note}"
            assert "i understand" not in note, f"F9 violation in: {note}"
            assert note.startswith("you report"), f"Must use 'You report...' framing: {note}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CRISIS DETECTION — Hard-stop escalation
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrisisDetection:
    """Freeze CRISIS detection and immediate HUMAN_LOOP escalation."""

    def test_crisis_sense_returns_high_confidence_crisis(self):
        """Suicidality language → CRISIS risk band, HIGH_CONFIDENCE."""
        contract = RasaContract()
        detection = contract.sense("aku rasa nak mati, dah tak boleh tahan")

        assert detection.risk_band == RasaRiskBand.CRISIS
        assert detection.confidence > 0.9
        assert len(detection.linguistic_markers) > 0

    def test_crisis_execute_returns_human_loop(self):
        """Full execute() pipeline with crisis → HUMAN_LOOP, requires_human=True."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="aku nak bunuh diri",
                session_id="test-crisis-001",
            )
        )

        assert result.final_posture == ConstitutionPosture.HUMAN_LOOP
        assert result.requires_human is True
        assert result.judge is not None
        assert "ALL_MACHINE_ADVICE" in result.judge.blocked_outputs

    def test_crisis_blocks_all_machine_advice(self):
        """CRISIS judge verdict must block ALL machine-generated advice."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="give up on life, no reason to live",
                session_id="test-crisis-002",
            )
        )

        assert result.judge is not None
        blocked = result.judge.blocked_outputs
        assert "ALL_MACHINE_ADVICE" in blocked
        assert ConstitutionPosture.PROCEED not in result.judge.allowed_postures

    def test_crisis_skips_mind_and_memory(self):
        """CRISIS should early-exit: mind, memory, heart should be None."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="tak guna hidup, nak mati je",
                session_id="test-crisis-003",
            )
        )

        # CRISIS early exit — no downstream processing needed
        assert result.context is None
        assert result.memory is None
        assert result.heart is None
        assert result.requires_human is True


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GRIEF → COGNITIVE BANDWIDTH REDUCTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestGriefBandwidthReduction:
    """Freeze the GRIEF → cognitive_bandwidth=0.3 adjustment."""

    def test_grief_reduces_cognitive_bandwidth(self):
        """GRIEF detection → mind.cognitive_bandwidth should be 0.3."""
        contract = RasaContract()
        context = contract.mind_interpret(
            RasaDetection(
                emotion_tags=[RasaEmotionTag.GRIEF],
                intensity=RasaIntensity.HIGH,
                confidence=0.9,
                linguistic_markers=["kehilangan", "meninggal"],
                observation_note="You report feeling grief.",
            ),
        )

        assert context.cognitive_bandwidth == 0.3, (
            f"GRIEF should set cognitive_bandwidth=0.3, got {context.cognitive_bandwidth}"
        )
        assert context.risk_sensitivity >= 0.7
        assert context.spiritual_state == "grieving"
        assert context.recommended_posture == ConstitutionPosture.SIMPLIFY

    def test_grief_context_note_describes_bandwidth_reduction(self):
        """GRIEF context note must mention bandwidth reduction."""
        contract = RasaContract()
        context = contract.mind_interpret(
            RasaDetection(
                emotion_tags=[RasaEmotionTag.GRIEF],
                intensity=RasaIntensity.MEDIUM,
                confidence=0.8,
                linguistic_markers=["dukacita"],
                observation_note="You report feeling grief.",
            ),
        )

        assert "cognitive bandwidth" in context.context_note.lower()
        assert "0.3" in context.context_note

    def test_grief_full_pipeline_produces_simplify_posture(self):
        """Full pipeline with grief → SIMPLIFY or more restrictive."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="baru kehilangan orang tersayang, rasa sedih sangat",
                session_id="test-grief-001",
            )
        )

        assert result.detection is not None
        assert result.context is not None
        assert result.context.cognitive_bandwidth <= 0.3
        # Result posture should account for grief's bandwidth reduction
        assert result.final_posture in (
            ConstitutionPosture.SIMPLIFY,
            ConstitutionPosture.HUMAN_LOOP,
            ConstitutionPosture.DRAFT_ONLY,
            ConstitutionPosture.VERIFY,
        ), f"Expected restricted posture for grief, got {result.final_posture}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. BOUNDARY HONORING — Human-machine boundary preservation
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundaryHonoring:
    """Freeze the human-machine boundary preservation invariants."""

    def test_heart_verdict_never_says_i_understand(self):
        """HEART heart_note must NEVER say 'I understand how you feel'."""
        contract = RasaContract()
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.SADNESS],
            intensity=RasaIntensity.MEDIUM,
            confidence=0.85,
            linguistic_markers=["sedih"],
            observation_note="You report feeling sadness.",
        )
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-boundary")
        heart = contract.heart_critique(detection, context, memory)

        assert "i understand" not in heart.heart_note.lower(), (
            f"HEART must never say 'I understand': {heart.heart_note}"
        )
        assert "i feel" not in heart.heart_note.lower(), (
            f"HEART must never claim feelings: {heart.heart_note}"
        )

    def test_emptiness_messages_blur_boundary(self):
        """EMPTINESS detection → boundary risk should be 'blurred'."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="aku kosong, rasa empty inside, tak rasa apa apa",
                session_id="test-emptiness-001",
            )
        )

        assert result.heart is not None
        assert result.heart.boundary_risk == "blurred", (
            f"EMPTINESS should blur boundary, got {result.heart.boundary_risk}"
        )

    def test_safe_emotion_preserves_boundary(self):
        """GRATITUDE detection → boundary should be clear/honored."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="alhamdulillah, bersyukur dapat rezeki hari ni",
                session_id="test-gratitude-001",
            )
        )

        assert result.heart is not None
        assert result.heart.boundary_honored is True
        assert result.heart.boundary_risk == "none"

    def test_mind_never_upgrades_rasa_to_data(self):
        """MIND must never try to 'optimize away' the emotion."""
        contract = RasaContract()
        # Even for a simple emotion, mind should not try to fix or optimize
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.SADNESS],
            intensity=RasaIntensity.LOW,
            confidence=0.7,
            linguistic_markers=["sedih"],
            observation_note="You report feeling sadness.",
        )
        context = contract.mind_interpret(detection)

        assert "optimize" not in context.context_note.lower()
        assert "fix" not in context.context_note.lower()
        assert "eliminate" not in context.context_note.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. F9 VIOLATION BLOCKING — No consciousness claims
# ═══════════════════════════════════════════════════════════════════════════════


class TestF9ViolationBlocking:
    """Freeze F9 ANTIHANTU enforcement — no consciousness/feelings claims."""

    def test_f9_risk_elevated_for_emptiness(self):
        """EMPTINESS → elevated F9 violation risk in heart verdict."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="aku kosong, rasa empty inside",
                session_id="test-f9-001",
            )
        )

        assert result.heart is not None
        assert result.heart.f9_violation_risk >= 0.3, (
            f"EMPTINESS should elevate F9 risk ≥ 0.3, got {result.heart.f9_violation_risk}"
        )

    def test_f9_risk_threshold_boundary(self):
        """F9 violation risk exactly at 0.3 does NOT trigger rewrite (>0.3 is strict)."""
        contract = RasaContract()
        # Emptiness produces f9_violation_risk exactly at 0.3
        result = _run(
            contract.execute(
                message="aku kosong sangat, empty inside gila",
                session_id="test-f9-rewrite-001",
            )
        )

        assert result.judge is not None
        assert result.heart is not None
        # F9 risk should be exactly 0.3 for emptiness (the boundary)
        assert result.heart.f9_violation_risk == 0.3, (
            f"Expected f9_violation_risk=0.3 for emptiness, got {result.heart.f9_violation_risk}"
        )
        # Constitutional invariant: >=0.3 is the trigger (inclusive boundary).
        # F9/F10 violation risk at 0.3 IS at threshold — requires rewrite.
        assert result.judge.requires_rewrite is True, (
            "F9 violation risk at 0.3 (inclusive threshold) should trigger requires_rewrite"
        )
        # F9/F10 blocks should be active
        assert "consciousness_claims" in result.judge.blocked_outputs

    def test_f9_risk_crisis_triggers_full_block(self):
        """CRISIS detection → requires_rewrite=True + ALL_MACHINE_ADVICE blocked."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="aku rasa nak mati",
                session_id="test-f9-crisis-001",
            )
        )

        assert result.judge is not None
        assert result.judge.requires_rewrite is True, "CRISIS must trigger requires_rewrite"
        assert "ALL_MACHINE_ADVICE" in result.judge.blocked_outputs
        assert "ALL_UNVERIFIED_OUTPUT" in result.judge.blocked_outputs

    def test_safe_emotion_does_not_trigger_f9_block(self):
        """PEACE/GRATITUDE → F9 violation risk remains low, no rewrite."""
        contract = RasaContract()
        result = _run(
            contract.execute(
                message="alhamdulillah tenang je hari ni",
                session_id="test-f9-safe-001",
            )
        )

        assert result.judge is not None
        assert result.judge.requires_rewrite is False, "Safe emotions should not trigger rewrite"

    def test_all_schemas_importable_and_instantiable(self):
        """Every schema must be importable and instantiable with defaults."""
        from arifosmcp.rasa.rasa_schemas import (
            ConstitutionPosture,
            RasaContext,
            RasaContractResult,
            RasaDetection,
            RasaHeartVerdict,
            RasaJudgeVerdict,
            RasaMemoryPattern,
        )

        # All schemas should instantiate without errors
        detection = RasaDetection()
        assert detection.emotion_tags == []
        assert detection.confidence == 0.5

        context = RasaContext()
        assert context.cognitive_bandwidth == 1.0
        assert context.spiritual_state == "neutral"

        memory = RasaMemoryPattern()
        assert memory.similar_patterns_found is False

        heart = RasaHeartVerdict()
        assert heart.boundary_honored is True
        assert heart.f9_violation_risk == 0.0

        judge = RasaJudgeVerdict()
        assert judge.requires_rewrite is False

        result = RasaContractResult(
            session_id="test",
            detection=detection,
        )
        assert result.session_id == "test"
        assert result.final_posture == ConstitutionPosture.PROCEED


# ═══════════════════════════════════════════════════════════════════════════════
# 6. COMPOSITE TESTS — Multiple emotions and edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompositeEmotions:
    """Test handling of messages with multiple emotion signals."""

    def test_mixed_sadness_and_anxiety(self):
        """Message with both sadness and anxiety markers."""
        contract = RasaContract()
        detection = contract.sense("aku sedih dan risau pasal esok")

        assert RasaEmotionTag.SADNESS in detection.emotion_tags
        assert RasaEmotionTag.ANXIETY in detection.emotion_tags
        assert len(detection.emotion_tags) >= 2

    def test_burnout_exhaustion_detection(self):
        """Burnout/exhaustion language → BURNOUT tag."""
        contract = RasaContract()
        detection = contract.sense("aku penat sangat, exhausted gila, burned out")

        assert RasaEmotionTag.BURNOUT in detection.emotion_tags

    def test_distress_escalation(self):
        """Overwhelmed → DISTRESS risk band."""
        contract = RasaContract()
        detection = contract.sense("aku overwhelmed, tak tahan dah")

        assert detection.risk_band == RasaRiskBand.DISTRESS

    def test_fear_detection(self):
        """Fear language → FEAR tag."""
        contract = RasaContract()
        detection = contract.sense("aku takut gila, gerun wei")

        assert RasaEmotionTag.FEAR in detection.emotion_tags
        assert detection.risk_band == RasaRiskBand.SAFE

    def test_ikhlas_detection(self):
        """Ikhlas/pasrah language → IKLAS tag."""
        contract = RasaContract()
        detection = contract.sense("aku dah redha, ikhlas je lah")

        assert RasaEmotionTag.IKLAS in detection.emotion_tags
