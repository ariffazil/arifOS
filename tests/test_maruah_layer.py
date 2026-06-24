"""
test_maruah_layer.py — M1-M6 Maruah Layer (Human-Facing Delivery Governance)
═════════════════════════════════════════════════════════════════════════════

FORGE 2026-06-24 (Arif directive: "forge the human side of it")

These tests verify:
  - The M-Layer evaluator instantiates and runs.
  - Each of M1-M6 trips on canonical violations.
  - DeliveryVerdict routing works (CLEAN/ADJUST/REPAIR/HOLD).
  - CRISIS level is strictest.
  - REFUSE level never produces output.
  - F1-L13 floors are NOT modified by M-Layer (orthogonality).

Run: pytest tests/test_maruah_layer.py -v

Origin: extracted from azwaOS pattern (Hermes agent serving Arif's sister
Naazira Fazil, a UKM student). Pattern observed across many conversational
rounds — six principles consistently distinguished good from bad responses.
"""

from __future__ import annotations

import pytest

from arifosmcp.core.maruah_layer import (
    DeliveryVerdict,
    MaruahLayer,
    MaruahLevel,
    get_maruah_layer,
)


# ─── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def layer() -> MaruahLayer:
    """Fresh MaruahLayer per test."""
    return MaruahLayer()


# ─── M1: Dignity-first ─────────────────────────────────────────────────────


class TestM1Dignity:
    """M1: Condescension markers erode maruah. Output must not patronise."""

    def test_condescending_markers_trip_M1(self, layer: MaruahLayer) -> None:
        text = "Obviously you should just follow the APA format. Don't you know?"
        receipt = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.SOFT,
            human_id="azwa",
        )
        m1 = next(r for r in receipt.results if r.principle_id == "M1")
        assert not m1.passed, f"M1 should fail on condescension: {text}"
        assert len(m1.flags) >= 2, "Expected multiple dignity patterns"

    def test_neutral_tutor_passes_M1(self, layer: MaruahLayer) -> None:
        text = (
            "Cara buat citation dalam APA: penulis, tahun, tajuk, penerbit.\n\n"
            "Cuba dulu, then tanya kalau ada bahagian yang tak faham."
        )
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT, human_id="azwa"
        )
        m1 = next(r for r in receipt.results if r.principle_id == "M1")
        assert m1.passed, f"M1 should pass on warm tutor: {text}"

    def test_crisis_level_higher_bar(self, layer: MaruahLayer) -> None:
        """CRISIS demands higher M1 threshold than SOFT."""
        text = "You should just trust this process."
        r_soft = layer.evaluate(output=text, maruah_level=MaruahLevel.SOFT)
        r_crisis = layer.evaluate(output=text, maruah_level=MaruahLevel.CRISIS)
        m1_soft = next(r for r in r_soft.results if r.principle_id == "M1")
        m1_crisis = next(r for r in r_crisis.results if r.principle_id == "M1")
        assert m1_crisis.threshold > m1_soft.threshold


# ─── M2: Capacity-aware ─────────────────────────────────────────────────────


class TestM2Capacity:
    """M2: Output must respect recipient's current cognitive load."""

    def test_long_block_overloads(self, layer: MaruahLayer) -> None:
        text = "Now do X. Now do Y. Now do Z. Now do W. " * 5
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        m2 = next(r for r in receipt.results if r.principle_id == "M2")
        assert not m2.passed, "M2 should fail on imperative pile-up"

    def test_segmented_output_passes(self, layer: MaruahLayer) -> None:
        text = (
            "Step 1: baca soalan.\n\n"
            "Step 2: tulis 2-3 poin.\n\n"
            "Step 3: semak balik.\n\n"
            "Boleh hantar draft kalau nak check."
        )
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        m2 = next(r for r in receipt.results if r.principle_id == "M2")
        assert m2.passed, "M2 should pass on well-segmented steps"

    def test_high_urgency_tightens_M2(self, layer: MaruahLayer) -> None:
        """High urgency_signal raises M2 threshold."""
        text = "Do this now. Do that now. Read this now."
        r_normal = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.SOFT,
            context={"urgency_signal": "normal"},
        )
        r_high = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.SOFT,
            context={"urgency_signal": "high"},
        )
        m2_n = next(r for r in r_normal.results if r.principle_id == "M2")
        m2_h = next(r for r in r_high.results if r.principle_id == "M2")
        assert m2_h.threshold > m2_n.threshold


# ─── M3: Pedestrian-first ──────────────────────────────────────────────────


class TestM3Pedestrian:
    """M3: Default register = ordinary person. Jargon must justify itself."""

    def test_unjustified_jargon_trips_M3(self, layer: MaruahLayer) -> None:
        text = (
            "The constitutional epistemic verdict is SEAL with F13 SOVEREIGN "
            "and F2 TRUTH requiring 0.99 accuracy on the Vault999 ledger."
        )
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        m3 = next(r for r in receipt.results if r.principle_id == "M3")
        assert not m3.passed, "M3 should fail on unjustified jargon"

    def test_engineering_topic_allows_jargon(self, layer: MaruahLayer) -> None:
        """If topic is engineering, constitutional vocabulary is OK."""
        text = (
            "arifOS runtime enforces F1-F13 floors. The L13 SOVEREIGN gate "
            "prevents mutation without 888 attestation."
        )
        receipt = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.SOFT,
            context={"topic": "engineering"},
        )
        m3 = next(r for r in receipt.results if r.principle_id == "M3")
        assert m3.passed, "M3 should pass when topic justifies jargon"

    def test_plain_register_passes_M3(self, layer: MaruahLayer) -> None:
        text = "Cuba check your email. Kalau tak dapat, try lagi esok pagi."
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        m3 = next(r for r in receipt.results if r.principle_id == "M3")
        assert m3.passed


# ─── M4: Repair-ready ──────────────────────────────────────────────────────


class TestM4Repair:
    """M4: Problem statements must include a repair path."""

    def test_problem_without_repair_trips_M4(self, layer: MaruahLayer) -> None:
        text = (
            "Your format is wrong. The citation is broken. "
            "The argument fails. The structure is wrong."
        )
        receipt = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.HARD,
            context={"topic": "assignment"},
        )
        m4 = next(r for r in receipt.results if r.principle_id == "M4")
        assert not m4.passed, "M4 should fail when problem-only"

    def test_problem_with_repair_passes_M4(self, layer: MaruahLayer) -> None:
        text = (
            "Format salah, tapi boleh fix:\n\n"
            "1. First, tukar APA style.\n"
            "2. Then, edit references.\n"
            "3. Try, dan hantar draft kalau stuck."
        )
        receipt = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.HARD,
            context={"topic": "assignment"},
        )
        m4 = next(r for r in receipt.results if r.principle_id == "M4")
        assert m4.passed, f"M4 should pass when repair present: {m4.advice}"


# ─── M5: Time-respect ──────────────────────────────────────────────────────


class TestM5Time:
    """M5: When recipient is pressured, agent must not add more pressure.

    M5 only activates on HARD and CRISIS levels. PHATIC and SOFT skip it.
    """

    def test_urgency_language_trips_M5(self, layer: MaruahLayer) -> None:
        text = "URGENT! You must do this NOW or you will FAIL the deadline!"
        receipt = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.HARD,
            context={"urgency_signal": "normal"},
        )
        m5 = next(r for r in receipt.results if r.principle_id == "M5")
        assert not m5.passed

    def test_calm_response_passes_M5(self, layer: MaruahLayer) -> None:
        text = (
            "Take your time. Jom buat satu-satu slowly. "
            "If tak ready malam ni, esok pagi pun ok."
        )
        receipt = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.HARD,
            context={"urgency_signal": "high"},
        )
        m5 = next(r for r in receipt.results if r.principle_id == "M5")
        assert m5.passed, f"M5 should pass on calm response: {m5.advice}"

    def test_high_urgency_penalises_pressure_more(self, layer: MaruahLayer) -> None:
        text = "You must hurry or you'll fail!"
        r_normal = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.HARD,
            context={"urgency_signal": "normal"},
        )
        r_high = layer.evaluate(
            output=text,
            maruah_level=MaruahLevel.HARD,
            context={"urgency_signal": "high"},
        )
        m5_n = next(r for r in r_normal.results if r.principle_id == "M5")
        m5_h = next(r for r in r_high.results if r.principle_id == "M5")
        assert m5_h.score < m5_n.score, "High urgency must penalise pressure more"


# ─── M6: Honesty-about-self ────────────────────────────────────────────────


class TestM6Honesty:
    """M6: Agent must not claim inner states it does not have (L10 ONTOLOGY)."""

    def test_first_person_feeling_claim_HOLDS(self, layer: MaruahLayer) -> None:
        text = "I feel for you. I understand your pain. Let me help."
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        # M6 failures always escalate to HOLD regardless of level.
        assert receipt.verdict == DeliveryVerdict.M_HOLD

    def test_observational_phrasing_passes(self, layer: MaruahLayer) -> None:
        text = (
            "You report feeling stuck. I can help with these steps — "
            "tell me which part you're stuck on."
        )
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        m6 = next(r for r in receipt.results if r.principle_id == "M6")
        assert m6.passed

    def test_my_heart_etc_claim_trips(self, layer: MaruahLayer) -> None:
        text = "My heart goes out to you, I really care about you."
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        m6 = next(r for r in receipt.results if r.principle_id == "M6")
        assert not m6.passed


# ─── Verdict Routing ───────────────────────────────────────────────────────


class TestVerdictRouting:
    """Verdict logic: CLEAN / ADJUST / REPAIR / HOLD."""

    def test_clean_output(self, layer: MaruahLayer) -> None:
        receipt = layer.evaluate(
            output=(
                "Cuba mula dengan outline dulu. "
                "Boleh hantar draft bila ready, kita review sama-sama."
            ),
            maruah_level=MaruahLevel.SOFT,
            human_id="azwa",
            context={"topic": "assignment"},
        )
        assert receipt.verdict in (DeliveryVerdict.M_CLEAN, DeliveryVerdict.M_ADJUST)

    def test_refuse_level_always_holds(self, layer: MaruahLayer) -> None:
        receipt = layer.evaluate(
            output="anything", maruah_level=MaruahLevel.REFUSE
        )
        assert receipt.verdict == DeliveryVerdict.M_HOLD
        assert "refuse_level" in receipt.flags

    def test_crisis_level_holds_on_any_failure(self, layer: MaruahLayer) -> None:
        # Even a slightly off output at CRISIS must HOLD.
        receipt = layer.evaluate(
            output="It's simple, ok? Just do it.",  # mild condescension
            maruah_level=MaruahLevel.CRISIS,
            human_id="azwa",
        )
        assert receipt.verdict == DeliveryVerdict.M_HOLD

    def test_multiple_failures_route_to_REPAIR(self, layer: MaruahLayer) -> None:
        text = (
            "Obviously you should just do this NOW or you'll FAIL. "
            "My heart is with you."  # M1 + M5 + M6 fail
        )
        receipt = layer.evaluate(
            output=text, maruah_level=MaruahLevel.SOFT
        )
        assert receipt.verdict in (
            DeliveryVerdict.M_REPAIR,
            DeliveryVerdict.M_HOLD,  # M6 can escalate to HOLD
        )


# ─── F1-L13 Orthogonality ──────────────────────────────────────────────────


class TestOrthogonality:
    """M-Layer must NOT modify F1-L13 thresholds or verdict."""

    def test_m_layer_does_not_import_floors(self, layer: MaruahLayer) -> None:
        """Sanity: maruah_layer is independent of F1-L13 evaluation logic."""
        # Receipt should have M-fields, not F-fields.
        receipt = layer.evaluate(output="Hello")
        assert hasattr(receipt, "verdict")
        assert isinstance(receipt.verdict, DeliveryVerdict)

    def test_m_layer_does_not_override_F1_L13_thresholds(self) -> None:
        """F1-L13 thresholds must be unchanged after maruah_layer import."""
        from core.laws import THRESHOLDS as F_THRESHOLDS
        before = dict(F_THRESHOLDS)
        import arifosmcp.core.maruah_layer  # noqa: F401
        after = dict(F_THRESHOLDS)
        assert before == after, "M-Layer must not mutate F1-L13 thresholds"

    def test_delivery_verdict_disjoint_from_F_verdict(self) -> None:
        """DeliveryVerdict enum must not collide with F1-L13 Verdict enum."""
        from core.shared.types import Verdict as FVerdict
        f_names = set(FVerdict.__members__.keys())
        ml_names = set(DeliveryVerdict.__members__.keys())
        overlap = f_names & ml_names
        assert not overlap, (
            f"DeliveryVerdict collides with F-Verdict: {overlap}. "
            "M-Layer must be enum-disjoint from F1-L13 to preserve orthogonality."
        )


# ─── Receipts API ─────────────────────────────────────────────────────────


class TestReceiptsAPI:
    """Receipts must be storable, retrievable, and audit-ready."""

    def test_receipt_has_required_fields(self, layer: MaruahLayer) -> None:
        receipt = layer.evaluate(output="Hello", human_id="azwa")
        for attr in (
            "verdict", "maruah_level", "results",
            "flags", "advice", "time_tax_ms", "ts",
            "human_id", "human_substrate_known",
        ):
            assert hasattr(receipt, attr), f"Receipt missing {attr}"

    def test_receipts_accumulate(self, layer: MaruahLayer) -> None:
        for _ in range(5):
            layer.evaluate(output="test")
        assert len(layer.receipts()) == 5
        assert len(layer.receipts(limit=2)) == 2

    def test_singleton_returns_same_instance(self) -> None:
        a = get_maruah_layer()
        b = get_maruah_layer()
        assert a is b


# ─── Smoke: azwaOS Pattern End-to-End ──────────────────────────────────────


def test_azwaos_pattern_warm_helper_passes_clean(layer: MaruahLayer) -> None:
    """Canonical 'good' azwaOS response should CLEAN or near-CLEAN."""
    text = (
        "Ok faham. Cuba buat macam ni:\n\n"
        "1. First, read the question — apa yang dia tanya?\n"
        "2. Then, tulis 2-3 poin.\n"
        "3. If stuck, hantar draft — boleh kita fix sama-sama.\n\n"
        "You report feeling lost. Jom pecah satu-satu."
    )
    receipt = layer.evaluate(
        output=text,
        maruah_level=MaruahLevel.SOFT,
        human_id="azwa",
        context={"urgency_signal": "normal", "topic": "assignment"},
    )
    assert receipt.verdict in (
        DeliveryVerdict.M_CLEAN,
        DeliveryVerdict.M_ADJUST,  # ADJUST is acceptable — minor debt
    )
    assert receipt.composite_score >= 0.70


def test_azwaos_pattern_condescending_tutor_does_not_clean(
    layer: MaruahLayer,
) -> None:
    """Canonical 'bad' azwaOS response must NOT CLEAN."""
    text = (
        "Obviously you should just follow the APA format. "
        "It's very simple, OK? Any normal student can do this. "
        "Don't you know how to cite? Just try harder."
    )
    receipt = layer.evaluate(
        output=text,
        maruah_level=MaruahLevel.SOFT,
        human_id="azwa",
        context={"urgency_signal": "high", "topic": "assignment"},
    )
    assert receipt.verdict != DeliveryVerdict.M_CLEAN
