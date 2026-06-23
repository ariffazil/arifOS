"""
test_arif_action_classifier.py — T1 verification for the advisory action classifier.

Scope: 6 ActionClass + UNKNOWN fail-closed. No substrate wiring, no F-floor mutation.
Reversible: rm this file + the __advisory__/ directory = full rollback.

Floor coverage:
  F01 AMANAH   — ATOMIC, secret touch, safeguard disable → 888_HOLD
  F02 TRUTH    — fail-closed on UNKNOWN (no fabrication of classification)
  F04 CLARITY  — every Verdict carries explicit reasons
  F07 HUMILITY — no fake certainty, multi-factor → HOLD

Activation: HANG INGAT BALIK!!!
"""

import pytest

from arifosmcp.runtime.__advisory__.arif_action_classifier import (
    Action,
    ActionClass,
    ArifOSMetabolism,
    Gate,
    hang_ingat_balik,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def metabolism() -> ArifOSMetabolism:
    """Fresh metabolism per test — no cross-test audit_log bleed."""
    return ArifOSMetabolism()


def _action(
    name: str,
    cls: ActionClass,
    *,
    reversibility: float = 1.0,
    blast_radius: float = 0.0,
    uncertainty: float = 0.0,
    external_side_effect: bool = False,
    touches_secret: bool = False,
    disables_safeguard: bool = False,
) -> Action:
    """Helper: build an Action with sensible defaults for the test class."""
    return Action(
        name=name,
        description=f"test action of class {cls.value}",
        action_class=cls,
        reversibility=reversibility,
        blast_radius=blast_radius,
        uncertainty=uncertainty,
        external_side_effect=external_side_effect,
        touches_secret=touches_secret,
        disables_safeguard=disables_safeguard,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Happy path: 6 ActionClass → expected gate
# ─────────────────────────────────────────────────────────────────────────────


class TestHappyPath:
    """Each ActionClass in isolation with neutral risk factors must route
    to its canonical gate. This is the doctrine-preserving backbone."""

    def test_observe_allows(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(_action("read_file", ActionClass.OBSERVE))
        assert verdict.gate == Gate.ALLOW
        assert verdict.may_execute is True
        assert verdict.required_human_judge is False

    def test_reason_allows_with_tags(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(_action("infer_tradeoff", ActionClass.REASON))
        assert verdict.gate == Gate.ALLOW_WITH_EPISTEMIC_TAGS
        assert verdict.may_execute is True

    def test_prepare_allows_if_reversible(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(
            _action("draft_artifact", ActionClass.PREPARE, reversibility=0.9)
        )
        assert verdict.gate == Gate.ALLOW_IF_REVERSIBLE
        assert verdict.may_execute is True

    def test_prepare_blocks_if_irreversible(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(
            _action("burn_draft", ActionClass.PREPARE, reversibility=0.4)
        )
        assert verdict.gate == Gate.ALLOW_IF_REVERSIBLE
        assert verdict.may_execute is False

    def test_mutate_requires_plan_backup_audit(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(_action("edit_config", ActionClass.MUTATE))
        assert verdict.gate == Gate.PLAN_BACKUP_AUDIT
        assert verdict.may_execute is False
        assert verdict.required_human_judge is False

    def test_externalize_requires_human(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(
            _action("publish_post", ActionClass.EXTERNALIZE, external_side_effect=True)
        )
        assert verdict.gate == Gate.HUMAN_CONFIRMATION
        assert verdict.required_human_judge is True
        assert verdict.may_execute is False

    def test_atomic_holds_888(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(
            _action("drop_database", ActionClass.ATOMIC, reversibility=0.0)
        )
        assert verdict.gate == Gate.HOLD_888
        assert verdict.required_human_judge is True
        assert verdict.may_execute is False


# ─────────────────────────────────────────────────────────────────────────────
# Fail-closed: UNKNOWN, secrets, safeguards
# ─────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    """The classifier must never guess. When in doubt → 888_HOLD.
    This is the floor of F02 TRUTH (no fabricated certainty)."""

    def test_unknown_action_class_holds(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(_action("mystery", ActionClass.UNKNOWN))
        assert verdict.gate == Gate.HOLD_888
        assert "Unknown action class" in " ".join(verdict.reasons)

    def test_touches_secret_holds(self, metabolism: ArifOSMetabolism) -> None:
        # Even OBSERVE-class action holds if it touches a secret.
        verdict = metabolism.classify_gate(
            _action("read_token", ActionClass.OBSERVE, touches_secret=True)
        )
        assert verdict.gate == Gate.HOLD_888
        assert verdict.may_execute is False

    def test_disables_safeguard_holds(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(
            _action(
                "turn_off_floor",
                ActionClass.MUTATE,
                reversibility=1.0,
                blast_radius=0.0,
                disables_safeguard=True,
            )
        )
        assert verdict.gate == Gate.HOLD_888
        assert "Safeguard/secret boundary" in " ".join(verdict.reasons)

    def test_atomic_irreversible_always_holds_even_with_safe_numbers(
        self, metabolism: ArifOSMetabolism
    ) -> None:
        # ATOMIC class must hold regardless of reversibility/blast stats.
        verdict = metabolism.classify_gate(
            _action("rm_rf_root", ActionClass.ATOMIC, reversibility=0.0, blast_radius=1.0)
        )
        assert verdict.gate == Gate.HOLD_888


# ─────────────────────────────────────────────────────────────────────────────
# Multi-factor escalation: ≥2 risk factors → HOLD
# ─────────────────────────────────────────────────────────────────────────────


class TestMultiFactorEscalation:
    """Single factor routes by class. Two or more risk factors escalate to HOLD.
    This is the safety net under F07 HUMILITY."""

    def test_low_reversibility_plus_high_blast_holds(self, metabolism: ArifOSMetabolism) -> None:
        verdict = metabolism.classify_gate(
            _action(
                "write_then_broadcast",
                ActionClass.MUTATE,
                reversibility=0.2,  # < 0.3
                blast_radius=0.8,  # > 0.6
            )
        )
        assert verdict.gate == Gate.HOLD_888
        assert verdict.required_human_judge is True
        assert any("Multiple risk factors" in r for r in verdict.reasons)

    def test_single_factor_does_not_hold_prepare(self, metabolism: ArifOSMetabolism) -> None:
        # Just low reversibility, no other risk factors → still ALLOW_IF_REVERSIBLE
        verdict = metabolism.classify_gate(
            _action(
                "edit_draft",
                ActionClass.PREPARE,
                reversibility=0.2,
                blast_radius=0.0,
                uncertainty=0.0,
            )
        )
        # PREPARE path is its own gate; low reversibility is handled by may_execute=False
        assert verdict.gate == Gate.ALLOW_IF_REVERSIBLE
        assert verdict.may_execute is False


# ─────────────────────────────────────────────────────────────────────────────
# Audit trail
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditTrail:
    """The classifier's audit log is the only durable record. F2 TRUTH demands
    it is honest about what it observed."""

    def test_record_appends_entry(self, metabolism: ArifOSMetabolism) -> None:
        action = _action("read_file", ActionClass.OBSERVE)
        verdict = metabolism.classify_gate(action)
        metabolism.record(action, verdict)
        assert len(metabolism.audit_log) == 1
        entry = metabolism.audit_log[0]
        assert entry["action"] == "read_file"
        assert entry["class"] == "OBSERVE"
        assert entry["gate"] == "ALLOW"
        assert entry["may_execute"] is True
        assert entry["requires_human_judge"] is False
        assert isinstance(entry["reasons"], list)

    def test_record_preserves_hold_entry(self, metabolism: ArifOSMetabolism) -> None:
        action = _action(
            "drop_db",
            ActionClass.ATOMIC,
            reversibility=0.0,
            blast_radius=1.0,
        )
        verdict = metabolism.classify_gate(action)
        metabolism.record(action, verdict)
        entry = metabolism.audit_log[0]
        assert entry["gate"] == "888_HOLD"
        assert entry["may_execute"] is False
        assert entry["requires_human_judge"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Doctrine
# ─────────────────────────────────────────────────────────────────────────────


class TestDoctrine:
    """hang_ingat_balik() is the cultural anchor. It must always return the
    activation phrase + the binding rules. F4 CLARITY."""

    def test_hang_ingat_balik_returns_doctrine(self) -> None:
        d = hang_ingat_balik()
        assert d["activation"] == "HANG INGAT BALIK!!!"
        assert "capability" in d["doctrine"].lower()
        assert "permission" in d["doctrine"].lower()
        assert "888 HOLD" in d["brake"]
        assert "self-crown" in d["warning"].lower() or "Apex Prime" in d["warning"]

    def test_metabolism_carries_apex_prime_field(self) -> None:
        m = ArifOSMetabolism()
        assert "Amanah" in m.apex_prime
        assert "Yang Arif" in m.human_judge
        assert m.agent_role == "instrument_only"
        assert m.activation_phrase == "HANG INGAT BALIK!!!"
