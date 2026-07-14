"""
test_qqq_validator.py — QQQ Recommendation Discipline Test Suite
═══════════════════════════════════════════════════════════════════════════════
Tests Gate 5b: QQQ validator (validate_qqq + gate_qqq).

QQQ Doctrine v1.0 — operational expression of F2 TRUTH + F4 CLARITY + F7 HUMILITY.

Covers:
  - Intent gating: QQQ triggers only on RECOMMENDATION/DECISION/VERDICT
  - Q1 Qualitative: ≥5 paths, NULL mandatory, INVERSE mandatory
  - Q2 Quantitative: BR, REV, Time, Conf, PA per path
  - Q3 Quantum: precedent, interference, superposition, observer
  - Verdict: recommended_path_id must reference valid path
  - Envelope missing: ENVELOPE_MISSING, not suppression
  - Gate integration: gate_qqq returns structured QQQCheck

FLOOR BIND: F2 TRUTH, F4 CLARITY, F7 HUMILITY
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

import pytest

from arifosmcp.runtime.qqq_validator import (
    QQQCheck,
    QQQVerdict,
    gate_qqq,
    validate_qqq,
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS — minimal valid envelope for testing
# ═══════════════════════════════════════════════════════════════════════════════


def _make_path(
    path_id: str = "P1",
    category: str = "AGGRESSIVE",
    blast_radius: int = 3,
    reversibility: int = 4,
    confidence: float = 0.85,
    prior_art: str = "STRONG",
) -> dict:
    """Create a minimal path dict."""
    return {
        "path_id": path_id,
        "name": f"Path {path_id}",
        "description": f"Description for {path_id}",
        "category": category,
        "blast_radius": blast_radius,
        "reversibility": reversibility,
        "time_cost": "~5min",
        "confidence": confidence,
        "prior_art": prior_art,
    }


def _make_quantum() -> dict:
    """Create a minimal quantum analysis dict."""
    return {
        "precedent_effect": "Probe-first becomes canon",
        "interference_effect": "None for this path",
        "superposition_effect": "All options preserved",
        "observer_effect": "No behavioral shift",
    }


def _make_valid_envelope() -> dict:
    """Create a minimal valid QQQ envelope (5 paths, NULL + INVERSE, quantum)."""
    return {
        "paths": [
            _make_path("P1", "AGGRESSIVE"),
            _make_path("P2", "CONSERVATIVE"),
            _make_path("P3", "LATERAL"),
            _make_path("P4", "NULL", blast_radius=0, reversibility=5, confidence=1.0),
            _make_path("P5", "INVERSE", blast_radius=4, reversibility=2, confidence=0.3, prior_art="NONE"),
        ],
        "quantum": _make_quantum(),
        "recommended_path_id": "P3",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INTENT GATING — QQQ triggers only on RECOMMENDATION/DECISION/VERDICT
# ═══════════════════════════════════════════════════════════════════════════════


class TestIntentGating:
    """QQQ must NOT trigger on non-recommendation intents."""

    def test_observation_not_required(self):
        check = validate_qqq(None, "OBSERVATION")
        assert check.verdict == QQQVerdict.NOT_REQUIRED
        assert check.qqq_required is False

    def test_status_report_not_required(self):
        check = validate_qqq(None, "STATUS_REPORT")
        assert check.verdict == QQQVerdict.NOT_REQUIRED
        assert check.qqq_required is False

    def test_question_not_required(self):
        check = validate_qqq(None, "QUESTION")
        assert check.verdict == QQQVerdict.NOT_REQUIRED
        assert check.qqq_required is False

    def test_recommendation_required(self):
        check = validate_qqq(None, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.ENVELOPE_MISSING
        assert check.qqq_required is True

    def test_decision_required(self):
        check = validate_qqq(None, "DECISION")
        assert check.verdict == QQQVerdict.ENVELOPE_MISSING
        assert check.qqq_required is True

    def test_verdict_required(self):
        check = validate_qqq(None, "VERDICT")
        assert check.verdict == QQQVerdict.ENVELOPE_MISSING
        assert check.qqq_required is True

    def test_unknown_intent_not_required(self):
        check = validate_qqq(None, "UNKNOWN")
        assert check.verdict == QQQVerdict.NOT_REQUIRED


# ═══════════════════════════════════════════════════════════════════════════════
# ENVELOPE MISSING — must surface, never suppress
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnvelopeMissing:
    """When QQQ is required but no envelope provided, must label not suppress."""

    def test_none_envelope(self):
        check = validate_qqq(None, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.ENVELOPE_MISSING
        assert len(check.reasons) > 0
        assert "no envelope provided" in check.reasons[0]

    def test_empty_dict_envelope(self):
        check = validate_qqq({}, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.ENVELOPE_MISSING

    def test_gate_qqq_missing_envelope(self):
        check = gate_qqq(None, "DECISION")
        assert check.verdict == QQQVerdict.ENVELOPE_MISSING
        assert check.metadata["qqq_compliance"] == "INADMISSIBLE-Q1"


# ═══════════════════════════════════════════════════════════════════════════════
# Q1 QUALITATIVE — option space mapping
# ═══════════════════════════════════════════════════════════════════════════════


class TestQ1Qualitative:
    """Q1: ≥5 paths, NULL mandatory, INVERSE mandatory."""

    def test_too_few_paths(self):
        envelope = {
            "paths": [_make_path("P1"), _make_path("P2")],
            "quantum": _make_quantum(),
            "recommended_path_id": "P1",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q1
        assert any("≥5" in r for r in check.reasons)

    def test_missing_null(self):
        envelope = {
            "paths": [
                _make_path("P1", "AGGRESSIVE"),
                _make_path("P2", "CONSERVATIVE"),
                _make_path("P3", "LATERAL"),
                _make_path("P4", "INVERSE"),
                _make_path("P5", "AGGRESSIVE"),
            ],
            "quantum": _make_quantum(),
            "recommended_path_id": "P1",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q1
        assert any("NULL" in r for r in check.reasons)

    def test_missing_inverse(self):
        envelope = {
            "paths": [
                _make_path("P1", "AGGRESSIVE"),
                _make_path("P2", "CONSERVATIVE"),
                _make_path("P3", "LATERAL"),
                _make_path("P4", "NULL"),
                _make_path("P5", "AGGRESSIVE"),
            ],
            "quantum": _make_quantum(),
            "recommended_path_id": "P1",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q1
        assert any("INVERSE" in r for r in check.reasons)

    def test_valid_q1(self):
        envelope = _make_valid_envelope()
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.has_null is True
        assert check.has_inverse is True
        assert check.paths_count == 5

    def test_seven_paths_preferred(self):
        """7 paths is preferred (MAKRUH to have only 5)."""
        envelope = {
            "paths": [
                _make_path("P1", "AGGRESSIVE"),
                _make_path("P2", "CONSERVATIVE"),
                _make_path("P3", "LATERAL"),
                _make_path("P4", "NULL"),
                _make_path("P5", "INVERSE"),
                _make_path("P6", "LATERAL"),
                _make_path("P7", "CONSERVATIVE"),
            ],
            "quantum": _make_quantum(),
            "recommended_path_id": "P3",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.paths_count == 7


# ═══════════════════════════════════════════════════════════════════════════════
# Q2 QUANTITATIVE — measured trade-offs
# ═══════════════════════════════════════════════════════════════════════════════


class TestQ2Quantitative:
    """Q2: BR, REV, Time, Conf, PA per path."""

    def test_missing_metrics(self):
        envelope = {
            "paths": [
                {"path_id": "P1", "category": "AGGRESSIVE"},  # no metrics
                _make_path("P2", "CONSERVATIVE"),
                _make_path("P3", "LATERAL"),
                _make_path("P4", "NULL"),
                _make_path("P5", "INVERSE"),
            ],
            "quantum": _make_quantum(),
            "recommended_path_id": "P2",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q2
        assert any("missing fields" in r for r in check.reasons)

    def test_confidence_out_of_range(self):
        envelope = {
            "paths": [
                _make_path("P1", "AGGRESSIVE", confidence=1.5),  # out of range
                _make_path("P2", "CONSERVATIVE"),
                _make_path("P3", "LATERAL"),
                _make_path("P4", "NULL"),
                _make_path("P5", "INVERSE"),
            ],
            "quantum": _make_quantum(),
            "recommended_path_id": "P2",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q2
        assert any("confidence" in r for r in check.reasons)

    def test_blast_radius_out_of_range(self):
        envelope = {
            "paths": [
                _make_path("P1", "AGGRESSIVE", blast_radius=6),  # out of range
                _make_path("P2", "CONSERVATIVE"),
                _make_path("P3", "LATERAL"),
                _make_path("P4", "NULL"),
                _make_path("P5", "INVERSE"),
            ],
            "quantum": _make_quantum(),
            "recommended_path_id": "P2",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q2

    def test_valid_q2(self):
        envelope = _make_valid_envelope()
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.metrics_complete is True


# ═══════════════════════════════════════════════════════════════════════════════
# Q3 QUANTUM — second-order effects
# ═══════════════════════════════════════════════════════════════════════════════


class TestQ3Quantum:
    """Q3: precedent, interference, superposition, observer."""

    def test_missing_quantum(self):
        envelope = {
            "paths": [
                _make_path("P1"), _make_path("P2"), _make_path("P3"),
                _make_path("P4", "NULL"), _make_path("P5", "INVERSE"),
            ],
            "recommended_path_id": "P1",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q3
        assert any("quantum_analysis missing" in r for r in check.reasons)

    def test_empty_quantum(self):
        envelope = {
            "paths": [
                _make_path("P1"), _make_path("P2"), _make_path("P3"),
                _make_path("P4", "NULL"), _make_path("P5", "INVERSE"),
            ],
            "quantum": {},
            "recommended_path_id": "P1",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q3

    def test_incomplete_quantum(self):
        envelope = {
            "paths": [
                _make_path("P1"), _make_path("P2"), _make_path("P3"),
                _make_path("P4", "NULL"), _make_path("P5", "INVERSE"),
            ],
            "quantum": {
                "precedent_effect": "Probe-first becomes canon",
                "interference_effect": "",  # empty
                "superposition_effect": "All options preserved",
                "observer_effect": "No behavioral shift",
            },
            "recommended_path_id": "P1",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q3
        assert any("interference_effect" in r for r in check.reasons)

    def test_valid_q3(self):
        envelope = _make_valid_envelope()
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.quantum_complete is True


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT — recommended_path_id must reference valid path
# ═══════════════════════════════════════════════════════════════════════════════


class TestVerdict:
    """recommended_path_id must reference a valid path_id."""

    def test_invalid_recommended_path(self):
        envelope = _make_valid_envelope()
        envelope["recommended_path_id"] = "P99"  # doesn't exist
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q1
        assert any("not in path_ids" in r for r in check.reasons)

    def test_valid_recommended_path(self):
        envelope = _make_valid_envelope()
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.recommended_path_valid is True


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETE — valid envelope passes all three Q layers
# ═══════════════════════════════════════════════════════════════════════════════


class TestComplete:
    """Valid envelope must pass all three Q layers."""

    def test_valid_envelope_complete(self):
        envelope = _make_valid_envelope()
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.COMPLETE
        assert check.qqq_required is True
        assert check.paths_count == 5
        assert check.has_null is True
        assert check.has_inverse is True
        assert check.quantum_complete is True
        assert check.metrics_complete is True
        assert check.recommended_path_valid is True
        assert len(check.reasons) == 0

    def test_gate_qqq_complete(self):
        envelope = _make_valid_envelope()
        check = gate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.COMPLETE
        assert check.metadata["qqq_compliance"] == "COMPLETE"

    def test_gate_qqq_inadmissible(self):
        """gate_qqq must map INADMISSIBLE verdicts to compliance string."""
        envelope = {
            "paths": [_make_path("P1")],
            "quantum": _make_quantum(),
            "recommended_path_id": "P1",
        }
        check = gate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict != QQQVerdict.COMPLETE
        assert "INADMISSIBLE" in check.metadata["qqq_compliance"]


# ═══════════════════════════════════════════════════════════════════════════════
# EDGE CASES — boundary conditions
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Boundary conditions and edge cases."""

    def test_exactly_five_paths(self):
        """5 is the minimum — must pass Q1."""
        envelope = _make_valid_envelope()
        assert len(envelope["paths"]) == 5
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.paths_count == 5

    def test_four_paths_fails(self):
        """4 paths is below minimum — must fail Q1."""
        envelope = {
            "paths": [
                _make_path("P1"), _make_path("P2"), _make_path("P3"),
                _make_path("P4", "NULL"),
            ],
            "quantum": _make_quantum(),
            "recommended_path_id": "P1",
        }
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q1

    def test_boundary_confidence_zero(self):
        """Confidence 0.0 is valid boundary."""
        envelope = _make_valid_envelope()
        envelope["paths"][0]["confidence"] = 0.0
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.metrics_complete is True

    def test_boundary_confidence_one(self):
        """Confidence 1.0 is valid boundary."""
        envelope = _make_valid_envelope()
        envelope["paths"][0]["confidence"] = 1.0
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.metrics_complete is True

    def test_boundary_blast_radius_zero(self):
        """BR-0 is valid boundary (no blast)."""
        envelope = _make_valid_envelope()
        envelope["paths"][0]["blast_radius"] = 0
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.metrics_complete is True

    def test_boundary_reversibility_five(self):
        """REV-5 is valid boundary (fully reversible)."""
        envelope = _make_valid_envelope()
        envelope["paths"][0]["reversibility"] = 5
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.metrics_complete is True

    def test_quantum_short_answer_rejected(self):
        """Quantum answers must be ≥5 chars."""
        envelope = _make_valid_envelope()
        envelope["quantum"]["precedent_effect"] = "x"  # too short
        check = validate_qqq(envelope, "RECOMMENDATION")
        assert check.verdict == QQQVerdict.INADMISSIBLE_Q3


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE INTEGRATION — Gate 5b in governance pipeline
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineIntegration:
    """Gate 5b integration with governance pipeline."""

    def test_gate_enum_includes_qqq(self):
        """Gate enum must include QQQ as GATE_5B_QQQ."""
        from arifosmcp.runtime.governance_pipeline import Gate

        assert hasattr(Gate, "QQQ")
        assert Gate.QQQ.value == "GATE_5B_QQQ"

    def test_gate_ordering(self):
        """QQQ gate must be between FLOORS (5) and DRIFT (6)."""
        from arifosmcp.runtime.governance_pipeline import Gate

        gates = list(Gate)
        floors_idx = gates.index(Gate.FLOORS)
        qqq_idx = gates.index(Gate.QQQ)
        drift_idx = gates.index(Gate.DRIFT)

        assert floors_idx < qqq_idx < drift_idx

    def test_qqq_never_blocks(self):
        """QQQ gate must never block — it labels, not suppresses."""
        # Even with no envelope, QQQ returns information, not a block
        check = gate_qqq(None, "RECOMMENDATION")
        # The verdict is ENVELOPE_MISSING, but this is informational
        assert check.verdict == QQQVerdict.ENVELOPE_MISSING
        # The check itself doesn't block — the pipeline decides what to do
        assert check.qqq_required is True
