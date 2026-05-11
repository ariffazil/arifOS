"""
tests/runtime/test_geox_qc_pipeline.py — GeoX Confidence & QC Pipeline Tests
"""

from __future__ import annotations

import math
import pytest

from arifosmcp.runtime.geox_bridge import (
    compute_confidence_bands,
    validate_physics_constraint,
    qc_verify_claim,
)


class TestConfidenceBands:
    """F07 HUMILITY + F09 ANTIHANTU: Statistical confidence from geoscience series."""

    def test_basic_p10_p50_p90(self):
        values = [2.1, 2.3, 2.5, 2.7, 2.9, 3.1, 3.3, 3.5, 3.7, 3.9]
        bands = compute_confidence_bands(values)
        assert bands["p10"] == pytest.approx(2.1, 0.01)
        assert bands["p50"] == pytest.approx(3.1, 0.01)
        assert bands["p90"] == pytest.approx(3.7, 0.01)
        assert bands["n"] == 10

    def test_insufficient_data_returns_none(self):
        bands = compute_confidence_bands([2.5])
        assert bands["p10"] is None
        assert bands["p50"] is None
        assert bands["p90"] is None
        assert bands["n"] == 1

    def test_ignores_nonfinite_values(self):
        values = [2.1, float("inf"), 2.5, float("nan"), 2.9]
        bands = compute_confidence_bands(values)
        assert bands["n"] == 3
        assert bands["p50"] == pytest.approx(2.5, 0.01)

    def test_statistics_accuracy(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        bands = compute_confidence_bands(values)
        assert bands["mean"] == pytest.approx(3.0, 0.01)
        assert bands["stdev"] == pytest.approx(math.sqrt(2.5), 0.01)


class TestPhysicsConstraint:
    """F09 ANTIHANTU: GeoX computations must respect Earth physics bounds."""

    def test_density_valid(self):
        r = validate_physics_constraint({"rhob": 2.45}, "density")
        assert r["valid"] is True
        assert r["key"] == "rhob"

    def test_density_too_low(self):
        r = validate_physics_constraint({"rhob": 1.5}, "density")
        assert r["valid"] is False
        assert "Physics-9 violation" in r["error"]

    def test_density_too_high(self):
        r = validate_physics_constraint({"rhob": 3.0}, "density")
        assert r["valid"] is False

    def test_velocity_valid(self):
        r = validate_physics_constraint({"vp": 3000}, "velocity")
        assert r["valid"] is True

    def test_velocity_boundary(self):
        r = validate_physics_constraint({"vp": 1500}, "velocity")
        assert r["valid"] is True
        r2 = validate_physics_constraint({"vp": 1499}, "velocity")
        assert r2["valid"] is False

    def test_porosity_valid(self):
        r = validate_physics_constraint({"phi": 0.25}, "porosity")
        assert r["valid"] is True

    def test_porosity_negative(self):
        r = validate_physics_constraint({"phi": -0.05}, "porosity")
        assert r["valid"] is False

    def test_missing_key(self):
        r = validate_physics_constraint({}, "density")
        assert r["valid"] is False
        assert "Missing key" in r["error"]

    def test_unknown_constraint(self):
        r = validate_physics_constraint({"x": 1}, "temperature")
        assert r["valid"] is False
        assert "Unknown constraint_type" in r["error"]

    def test_non_numeric_value(self):
        r = validate_physics_constraint({"rhob": "heavy"}, "density")
        assert r["valid"] is False


class TestQcVerifyClaim:
    """F02 TRUTH + F03 WITNESS + F07 HUMILITY + F09 ANTIHANTU: Claim state machine."""

    def _base_claim(self, overrides: dict | None = None) -> dict:
        c = {
            "claim_state": "INGESTED",
            "evidence_refs": ["ref1", "ref2", "ref3"],
            "confidence": "HIGH",
            "physics_check": {"valid": True},
            "primary_result": {"value": 2.45},
        }
        if overrides:
            c.update(overrides)
        return c

    def test_happy_path_qc_verified(self):
        claim = self._base_claim()
        result = qc_verify_claim(claim)
        assert result["claim_state"] == "QC_VERIFIED"
        assert result["previous_state"] == "INGESTED"
        assert result["verdict"] == "SEAL"
        assert result["issues"] == []

    def test_insufficient_evidence_refs(self):
        claim = self._base_claim({"evidence_refs": ["ref1"]})
        result = qc_verify_claim(claim, required_evidence_refs=3)
        assert result["claim_state"] == "QC_HOLD"
        assert result["verdict"] == "VOID"
        assert any("F03 WITNESS" in i for i in result["issues"])

    def test_low_confidence(self):
        claim = self._base_claim({"confidence": "LOW"})
        result = qc_verify_claim(claim, min_confidence="MEDIUM")
        assert result["claim_state"] == "QC_HOLD"
        assert any("F07 HUMILITY" in i for i in result["issues"])

    def test_physics_failure(self):
        claim = self._base_claim({"physics_check": {"valid": False, "error": "rhob out of range"}})
        result = qc_verify_claim(claim)
        assert result["claim_state"] == "QC_HOLD"
        assert any("F09 ANTIHANTU" in i for i in result["issues"])

    def test_missing_primary_result(self):
        claim = self._base_claim({"primary_result": None})
        result = qc_verify_claim(claim)
        assert result["claim_state"] == "QC_HOLD"
        assert any("F02 TRUTH" in i for i in result["issues"])

    def test_multiple_issues(self):
        claim = self._base_claim(
            {
                "evidence_refs": [],
                "confidence": "LOW",
                "physics_check": {"valid": False, "error": "bad"},
                "primary_result": None,
            }
        )
        result = qc_verify_claim(claim)
        assert result["claim_state"] == "QC_HOLD"
        assert len(result["issues"]) == 4
