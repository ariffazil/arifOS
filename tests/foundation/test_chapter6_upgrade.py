"""
Tests: Chapter 6 Upgrade — Human Wakefulness Federation

Validates:
  P0: FederationEnvelope v2 (claim_state, tool_scope, host_attestation, expires_at)
  P0: Tightened legacy_wrap (only OBSERVE allowed)
  P1: SovereigntyCheckpoint (four-question ritual)
  P1: requires_sovereignty_checkpoint() gate logic
  P2 Foundation: EpistemicTag placeholder test

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


from arifosmcp.schemas.embodied_tool import ClaimState
from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    AuthorityEnvelope,
    AuthoritySource,
    FederationEnvelope,
    HostAttestation,
    RiskPassport,
    ToolScope,
    wrap_legacy_call,
)
from arifosmcp.schemas.sovereignty_checkpoint import (
    CheckpointAnswer,
    CheckpointStatus,
    SovereigntyCheckpoint,
    SovereigntyCheckpointRequest,
    WakefulnessLevel,
    assess_wakefulness,
    build_sovereignty_checkpoint,
)


# ═══════════════════════════════════════════════════════════════════════════════
# P0 — FederationEnvelope v2 Fields
# ═══════════════════════════════════════════════════════════════════════════════


class TestFederationEnvelopeV2:
    """Tests for the v2 envelope fields from the Chapter 6 upgrade."""

    def test_v2_fields_exist_with_defaults(self):
        """New v2 fields should exist with sensible defaults."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
        )
        assert env.claim_state == ClaimState.UNKNOWN
        assert env.tool_scope == []
        assert env.host_attestation == HostAttestation.UNKNOWN
        assert env.expires_at is None
        assert env.actor_verification == "claimed"
        assert env.sovereignty_checkpoint is None

    def test_v2_fields_can_be_set(self):
        """v2 fields should be explicitly settable."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            claim_state=ClaimState.VERIFIED,
            tool_scope=[ToolScope.READ, ToolScope.WRITE],
            host_attestation=HostAttestation.TRUSTED,
            actor_verification="verified",
        )
        assert env.claim_state == ClaimState.VERIFIED
        assert ToolScope.READ in env.tool_scope
        assert ToolScope.WRITE in env.tool_scope
        assert env.host_attestation == HostAttestation.TRUSTED
        assert env.actor_verification == "verified"

    def test_expires_at_enforced_in_validation(self):
        """Expired envelopes should fail validation."""
        past = datetime.now(UTC) - timedelta(hours=1)
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            expires_at=past,
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "expired" in reason.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# P0 — Tightened Legacy Wrap
# ═══════════════════════════════════════════════════════════════════════════════


class TestTightenedLegacyWrap:
    """v2: LEGACY_WRAP only allows OBSERVE. Everything else → HOLD."""

    def test_legacy_wrap_observe_passes(self):
        """OBSERVE with legacy_wrap should still be allowed (read-only is safe)."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(action_class=ActionClass.OBSERVE),
            legacy_wrap=True,
        )
        ok, reason = env.validate_for_execution()
        assert ok is True, f"OBSERVE should pass, got: {reason}"

    def test_legacy_wrap_prepare_allowed(self):
        """PREPARE with legacy_wrap must be allowed (v2 hotfix 2026-06-05).

        Legacy callers (Claude web / Perplexity) cannot construct a full
        FederationEnvelope. PREPARE-class tools (mind_reason, memory_recall,
        evidence_fetch) are read-only planning tools — blocking them broke
        all connector use. OBSERVE + PREPARE are allowed; MUTATE + ATOMIC
        remain blocked.
        """
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(action_class=ActionClass.PREPARE),
            legacy_wrap=True,
        )
        ok, reason = env.validate_for_execution()
        assert ok is True, f"PREPARE should pass for legacy_wrap, got: {reason}"

    def test_legacy_wrap_mutate_blocked(self):
        """MUTATE with legacy_wrap must be blocked."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(action_class=ActionClass.MUTATE),
            legacy_wrap=True,
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "LEGACY_WRAP" in reason

    def test_legacy_wrap_atomic_blocked(self):
        """ATOMIC with legacy_wrap must be blocked."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(action_class=ActionClass.ATOMIC),
            legacy_wrap=True,
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "LEGACY_WRAP" in reason

    def test_wrap_legacy_call_defaults(self):
        """wrap_legacy_call should set v2 defaults correctly."""
        env = wrap_legacy_call(
            actor_id="arif",
            session_id="s1",
            tool_name="arif_ops_measure",
        )
        assert env.legacy_wrap is True
        assert env.claim_state == ClaimState.UNKNOWN
        assert env.host_attestation == HostAttestation.UNKNOWN
        assert env.actor_verification == "claimed"
        # OBSERVE tools get READ scope
        assert ToolScope.READ in env.tool_scope


# ═══════════════════════════════════════════════════════════════════════════════
# P0 — requires_sovereignty_checkpoint() Gate
# ═══════════════════════════════════════════════════════════════════════════════


class TestRequiresSovereigntyCheckpoint:
    """The gate that decides if a tool needs the four-question ritual."""

    def test_dignity_scope_triggers_checkpoint(self):
        """DIGNITY-scoped tools require a checkpoint."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            tool_scope=[ToolScope.DIGNITY],
        )
        assert env.requires_sovereignty_checkpoint() is True

    def test_vault_scope_triggers_checkpoint(self):
        """VAULT-scoped tools require a checkpoint."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            tool_scope=[ToolScope.VAULT],
        )
        assert env.requires_sovereignty_checkpoint() is True

    def test_memory_scope_triggers_checkpoint(self):
        """MEMORY-scoped tools require a checkpoint."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            tool_scope=[ToolScope.MEMORY],
        )
        assert env.requires_sovereignty_checkpoint() is True

    def test_secret_scope_triggers_checkpoint(self):
        """SECRET-scoped tools require a checkpoint."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            tool_scope=[ToolScope.SECRET],
        )
        assert env.requires_sovereignty_checkpoint() is True

    def test_read_only_does_not_trigger(self):
        """READ-only tools do NOT require a checkpoint."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            tool_scope=[ToolScope.READ],
        )
        assert env.requires_sovereignty_checkpoint() is False

    def test_atomic_action_triggers_regardless_of_scope(self):
        """ATOMIC actions require checkpoint even without sensitive scopes."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(action_class=ActionClass.ATOMIC),
            tool_scope=[ToolScope.READ],
        )
        assert env.requires_sovereignty_checkpoint() is True

    def test_public_external_effect_triggers(self):
        """PUBLIC external effects require a checkpoint."""
        from arifosmcp.schemas.federation_envelope import ExternalEffect

        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(external_effect=ExternalEffect.PUBLIC),
            tool_scope=[ToolScope.READ],
        )
        assert env.requires_sovereignty_checkpoint() is True

    def test_write_scope_alone_does_not_trigger(self):
        """WRITE without sensitive scopes does NOT require a checkpoint."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            tool_scope=[ToolScope.WRITE],
        )
        assert env.requires_sovereignty_checkpoint() is False


# ═══════════════════════════════════════════════════════════════════════════════
# P1 — SovereigntyCheckpoint Schema
# ═══════════════════════════════════════════════════════════════════════════════


class TestSovereigntyCheckpoint:
    """Tests for the four-question wakefulness ritual."""

    def test_build_checkpoint_has_four_questions(self):
        """A fresh checkpoint should have exactly 4 questions."""
        chk = build_sovereignty_checkpoint(
            tool_name="arif_judge_deliberate",
            session_id="test-session",
            actor_id="arif",
            risk_summary={"tier": "T3"},
        )
        assert chk.status == CheckpointStatus.PENDING
        assert len(chk.questions) == 4
        assert {q.question_id for q in chk.questions} == {
            "evidence",
            "uncertainty",
            "responsibility",
            "repair",
        }

    def test_checkpoint_not_complete_initially(self):
        """A fresh checkpoint should not be complete."""
        chk = build_sovereignty_checkpoint(
            tool_name="test",
            session_id="s1",
            actor_id="arif",
            risk_summary={},
        )
        assert chk.is_complete() is False
        assert chk.is_expired() is False

    def test_checkpoint_complete_after_answering_all(self):
        """After answering all four questions, checkpoint should be complete."""
        chk = build_sovereignty_checkpoint(
            tool_name="test",
            session_id="s1",
            actor_id="arif",
            risk_summary={},
        )
        for q in chk.questions:
            chk.answers.append(
                CheckpointAnswer(
                    question_id=q.question_id,
                    answer_text="Test answer for " + q.question_id,
                    answer_depth="considered",
                )
            )
        chk.status = CheckpointStatus.COMPLETED
        assert chk.is_complete() is True
        ok, reason = chk.is_valid()
        assert ok is True, f"Complete checkpoint should be valid: {reason}"

    def test_checkpoint_expired(self):
        """An expired checkpoint should fail validation."""
        chk = build_sovereignty_checkpoint(
            tool_name="test",
            session_id="s1",
            actor_id="arif",
            risk_summary={},
        )
        # Artificially expire it
        chk.expires_at = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
        assert chk.is_expired() is True
        ok, reason = chk.is_valid()
        assert ok is False

    def test_checkpoint_rejected(self):
        """A rejected checkpoint should fail validation."""
        chk = build_sovereignty_checkpoint(
            tool_name="test",
            session_id="s1",
            actor_id="arif",
            risk_summary={},
        )
        chk.status = CheckpointStatus.REJECTED
        ok, reason = chk.is_valid()
        assert ok is False
        assert "rejected" in reason.lower()

    def test_checkpoint_incomplete_fails(self):
        """An incomplete checkpoint should fail validation."""
        chk = build_sovereignty_checkpoint(
            tool_name="test",
            session_id="s1",
            actor_id="arif",
            risk_summary={},
        )
        # Answer only 2 of 4
        for q in chk.questions[:2]:
            chk.answers.append(
                CheckpointAnswer(
                    question_id=q.question_id,
                    answer_text="Partial answer",
                )
            )
        chk.status = CheckpointStatus.COMPLETED  # claimed complete but isn't
        ok, reason = chk.is_valid()
        assert ok is False
        assert "incomplete" in reason.lower()

    def test_checkpoint_request_has_instructions(self):
        """The checkpoint request should guide the agent."""
        chk = build_sovereignty_checkpoint(
            tool_name="test",
            session_id="s1",
            actor_id="arif",
            risk_summary={},
        )
        req = SovereigntyCheckpointRequest(checkpoint=chk)
        assert req.verdict == "888_HOLD"
        assert len(req.instructions) > 0
        assert req.checkpoint == chk

    def test_build_checkpoint_preserves_context(self):
        """Checkpoint should carry tool name, session, actor, and risk."""
        chk = build_sovereignty_checkpoint(
            tool_name="arif_vault_seal",
            session_id="sess-123",
            actor_id="arif-fazil",
            risk_summary={"tier": "T5", "action_class": "ATOMIC"},
            tool_description="Seals to VAULT999",
            evidence_summary="VAULT chain at height 61",
        )
        assert chk.tool_name == "arif_vault_seal"
        assert chk.session_id == "sess-123"
        assert chk.actor_id == "arif-fazil"
        assert chk.risk_summary["tier"] == "T5"
        assert chk.tool_description == "Seals to VAULT999"
        assert "height 61" in chk.evidence_summary


# ═══════════════════════════════════════════════════════════════════════════════
# P1 — Wakefulness Assessment
# ═══════════════════════════════════════════════════════════════════════════════


class TestWakefulnessAssessment:
    """Tests for the AI-classified wakefulness level."""

    def _build_completed_checkpoint(
        self, answers: list[tuple[str, str]], depth: str = "considered"
    ) -> SovereigntyCheckpoint:
        """Helper to build a completed checkpoint with given answers."""
        chk = build_sovereignty_checkpoint(
            tool_name="test",
            session_id="s1",
            actor_id="arif",
            risk_summary={},
        )
        for i, (qid, text) in enumerate(answers):
            chk.answers.append(
                CheckpointAnswer(
                    question_id=qid,
                    answer_text=text,
                    answer_depth=depth,
                )
            )
        chk.status = CheckpointStatus.COMPLETED
        return chk

    def test_deep_answers_detected_as_awake(self):
        """Long, deep answers should classify as AWAKE."""
        long_answer = (
            "This is a very detailed and thoughtful response that carefully considers all aspects of the question. "
            * 5
        )
        chk = self._build_completed_checkpoint(
            [(qid, long_answer) for qid in ["evidence", "uncertainty", "responsibility", "repair"]],
            depth="deep",
        )
        level = assess_wakefulness(chk)
        assert level == WakefulnessLevel.AWAKE, f"Expected AWAKE, got {level}"

    def test_surface_answers_detected_as_distracted(self):
        """Very short, fast answers with some variation → DISTRACTED."""
        chk = self._build_completed_checkpoint(
            [
                ("evidence", "ok"),
                ("uncertainty", "fine"),
                ("responsibility", "yes"),
                ("repair", "revert"),
            ],
            depth="surface",
        )
        level = assess_wakefulness(chk, time_to_complete_seconds=10.0)
        assert level == WakefulnessLevel.DISTRACTED, f"Expected DISTRACTED, got {level}"

    def test_near_identical_answers_detected_as_asleep(self):
        """Near-identical answers should classify as ASLEEP."""
        chk = self._build_completed_checkpoint(
            [(qid, "approved") for qid in ["evidence", "uncertainty", "responsibility", "repair"]],
            depth="surface",
        )
        level = assess_wakefulness(chk, time_to_complete_seconds=5.0)
        assert level == WakefulnessLevel.ASLEEP, f"Expected ASLEEP, got {level}"

    def test_mixed_depth_detected_as_present(self):
        """Mixed depth answers should classify as PRESENT."""
        chk = self._build_completed_checkpoint(
            [
                (
                    "evidence",
                    "I reviewed the logs showing the VAULT chain at height 61, the Prometheus metrics showing all 6 targets up, and the systemd status confirming all 15 services active. The evidence is consistent.",
                ),
                (
                    "uncertainty",
                    "The main uncertainty is runtime drift between build and live — this is a known GHCR artifact, not a real problem. Confidence 0.9.",
                ),
                (
                    "responsibility",
                    "I take responsibility. If the seal breaks the chain, I will repair it.",
                ),
                ("repair", "Rollback via git revert. The action is reversible."),
            ],
            depth="considered",
        )
        level = assess_wakefulness(chk, time_to_complete_seconds=120.0)
        assert level in (WakefulnessLevel.AWAKE, WakefulnessLevel.PRESENT), (
            f"Expected AWAKE or PRESENT, got {level}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# P0 — Actor Verification Gate
# ═══════════════════════════════════════════════════════════════════════════════


class TestActorVerification:
    """v2: actor_verification must be 'verified' for mutating actions unless TOKEN/HUMAN_888."""

    def test_claimed_actor_blocked_for_mutate(self):
        """MUTATE with claimed actor and non-TOKEN authority → HOLD."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.SESSION),
            actor_verification="claimed",
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "verified" in reason.lower()

    def test_verified_actor_allowed_for_mutate(self):
        """MUTATE with verified actor → allowed."""
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
            actor_verification="verified",
            receipts=__import__(
                "arifosmcp.schemas.federation_envelope", fromlist=["ActionReceipts"]
            ).ActionReceipts(observe_receipt_id="obs-1"),
        )
        ok, reason = env.validate_for_execution()
        assert ok is True, f"MUTATE with verified actor should pass: {reason}"
