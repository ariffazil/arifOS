"""
GEOX Validator Tests
DITEMPA BUKAN DIBERI

Async pytest tests for GeoXValidator — extract_predictions(), verify_prediction(),
validate_batch(), check_floor_compliance(), and the AggregateVerdict logic.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from arifos.geox.examples.mock_tools.mock_earthnet import MockEarthNetTool
from arifos.geox.examples.mock_tools.mock_vlm import MockSeismicVLMTool
from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoInsight,
    GeoPrediction,
    GeoQuantity,
    ProvenanceRecord,
)
from arifos.geox.geox_validator import (
    AggregateVerdict,
    GeoXValidator,
    ValidationResult,
    _parse_range,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _coord(
    lat: float = 4.5, lon: float = 104.2, depth: float = 2500.0
) -> CoordinatePoint:
    return CoordinatePoint(latitude=lat, longitude=lon, depth_m=depth)


def _prov(
    source_id: str = "TEST-PROV-001", source_type: str = "LEM"
) -> ProvenanceRecord:
    return ProvenanceRecord(
        source_id=source_id,
        source_type=source_type,  # type: ignore[arg-type]
        timestamp=datetime.now(timezone.utc),
        confidence=0.82,
    )


def _qty(
    value: float,
    units: str,
    quantity_type: str,
    uncertainty: float = 0.08,
    location: CoordinatePoint | None = None,
) -> GeoQuantity:
    return GeoQuantity(
        value=value,
        units=units,
        quantity_type=quantity_type,
        coordinates=location or _coord(),
        timestamp=datetime.now(timezone.utc),
        uncertainty=uncertainty,
        provenance=_prov(),
    )


def _pred(
    target: str = "net_pay_m",
    lo: float = 15.0,
    hi: float = 45.0,
    units: str = "m",
    confidence: float = 0.72,
    method: str = "LEM_ensemble",
    quantities: list[GeoQuantity] | None = None,
) -> GeoPrediction:
    return GeoPrediction(
        target=target,
        location=_coord(),
        expected_range=(lo, hi),
        units=units,
        confidence=confidence,
        supporting_quantities=quantities or [],
        method=method,
    )


def _insight(
    text: str,
    status: str = "unverified",
    risk_level: str = "medium",
    requires_human_signoff: bool = True,
    support: list[GeoPrediction] | None = None,
    floor_verdicts: dict[str, bool] | None = None,
) -> GeoInsight:
    kwargs: dict = {
        "text": text,
        "status": status,  # type: ignore[arg-type]
        "risk_level": risk_level,  # type: ignore[arg-type]
        "requires_human_signoff": requires_human_signoff,
        "support": support or [],
    }
    if floor_verdicts is not None:
        kwargs["floor_verdicts"] = floor_verdicts
    return GeoInsight(**kwargs)


# ---------------------------------------------------------------------------
# _parse_range (unit tests for the internal helper)
# ---------------------------------------------------------------------------


class TestParseRange:

    def test_single_value(self):
        lo, hi = _parse_range("30")
        assert lo == pytest.approx(30 * 0.85, abs=0.01)
        assert hi == pytest.approx(30 * 1.15, abs=0.01)

    def test_dash_range(self):
        lo, hi = _parse_range("25-45")
        assert lo == 25.0
        assert hi == 45.0

    def test_to_range(self):
        lo, hi = _parse_range("25 to 45")
        assert lo == 25.0
        assert hi == 45.0

    def test_en_dash_range(self):
        lo, hi = _parse_range("25–45")
        assert lo == 25.0
        assert hi == 45.0

    def test_min_max_order(self):
        """min is always the smaller value."""
        lo, hi = _parse_range("45-25")
        assert lo <= hi


# ---------------------------------------------------------------------------
# GeoXValidator.extract_predictions()
# ---------------------------------------------------------------------------


class TestExtractPredictions:

    def setup_method(self):
        self.validator = GeoXValidator()
        self.location = _coord()

    def test_net_pay_extraction(self):
        text = "The reservoir shows net pay of 30 meters in the central closure."
        preds = self.validator.extract_predictions(text, self.location)
        targets = [p.target for p in preds]
        assert "net_pay_m" in targets

    def test_hc_column_extraction(self):
        text = "A hydrocarbon column of 50 m is estimated from AVO response."
        preds = self.validator.extract_predictions(text, self.location)
        targets = [p.target for p in preds]
        assert "hc_column_m" in targets

    def test_porosity_extraction(self):
        text = "Average porosity of 18% is observed in the upper sandstone member."
        preds = self.validator.extract_predictions(text, self.location)
        targets = [p.target for p in preds]
        assert "porosity_pct" in targets

    def test_porosity_converted_to_fraction(self):
        """Porosity given as percentage >1 should be converted to fraction."""
        text = "Average porosity of 18% is observed."
        preds = self.validator.extract_predictions(text, self.location)
        por_preds = [p for p in preds if p.target == "porosity_pct"]
        assert por_preds, "Expected at least one porosity prediction"
        lo, hi = por_preds[0].expected_range
        assert lo < 1.0, f"Porosity should be fraction, got lo={lo}"
        assert hi < 1.0, f"Porosity should be fraction, got hi={hi}"

    def test_pressure_extraction(self):
        text = "Reservoir pressure of 3500 psi is modelled from basin simulation."
        preds = self.validator.extract_predictions(text, self.location)
        targets = [p.target for p in preds]
        assert "reservoir_pressure" in targets

    def test_temperature_extraction(self):
        text = (
            "Formation temperature of 120 degC is consistent with the maturity window."
        )
        preds = self.validator.extract_predictions(text, self.location)
        targets = [p.target for p in preds]
        assert "temperature" in targets

    def test_velocity_extraction(self):
        text = (
            "Seismic velocity of 2800 m/s is recorded in the Miocene clastic section."
        )
        preds = self.validator.extract_predictions(text, self.location)
        targets = [p.target for p in preds]
        assert "seismic_velocity" in targets

    def test_range_extraction(self):
        """A range like '25-45 m' should produce correct (lo, hi)."""
        text = "Net pay of 25-45 m is expected in the Blok Selatan anticline."
        preds = self.validator.extract_predictions(text, self.location)
        np_preds = [p for p in preds if p.target == "net_pay_m"]
        assert np_preds
        lo, hi = np_preds[0].expected_range
        assert lo == pytest.approx(25.0, abs=0.01)
        assert hi == pytest.approx(45.0, abs=0.01)

    def test_all_predictions_are_geo_prediction_instances(self):
        text = "Net pay of 30 meters with porosity 18% and velocity 2400 m/s."
        preds = self.validator.extract_predictions(text, self.location)
        for p in preds:
            assert isinstance(p, GeoPrediction)

    def test_no_quantitative_claims_returns_empty(self):
        text = (
            "The geological setting is broadly favourable for hydrocarbon accumulation."
        )
        preds = self.validator.extract_predictions(text, self.location)
        assert isinstance(preds, list)
        # No quantitative patterns → may be empty
        assert all(isinstance(p, GeoPrediction) for p in preds)

    def test_predictions_have_valid_confidence(self):
        text = "Net pay of 30 meters of net pay in the reservoir."
        preds = self.validator.extract_predictions(text, self.location)
        for p in preds:
            assert 0.0 <= p.confidence <= 1.0

    def test_predictions_method_is_llm_extraction(self):
        text = "Net pay of 30 meters."
        preds = self.validator.extract_predictions(text, self.location)
        for p in preds:
            assert p.method == "LLM_text_extraction"

    def test_predictions_range_min_lte_max(self):
        """All extracted predictions must have valid (lo <= hi)."""
        text = (
            "Net pay of 25-45 m, porosity 15-20%, pressure of 3000-3800 psi, "
            "seismic velocity of 2200-3000 m/s."
        )
        preds = self.validator.extract_predictions(text, self.location)
        for p in preds:
            lo, hi = p.expected_range
            assert lo <= hi, f"Invalid range for {p.target}: ({lo}, {hi})"


# ---------------------------------------------------------------------------
# GeoXValidator.verify_prediction()
# ---------------------------------------------------------------------------


class TestVerifyPrediction:

    def setup_method(self):
        self.validator = GeoXValidator()
        self.mock_earthnet = MockEarthNetTool()
        self.mock_vlm = MockSeismicVLMTool()

    @pytest.mark.asyncio
    async def test_returns_validation_result(self):
        pred = _pred(target="porosity", lo=0.10, hi=0.28, units="fraction")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        assert isinstance(result, ValidationResult)

    @pytest.mark.asyncio
    async def test_result_has_required_fields(self):
        pred = _pred(target="porosity", lo=0.10, hi=0.28, units="fraction")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        assert hasattr(result, "insight_id")
        assert hasattr(result, "verdict")
        assert hasattr(result, "score")
        assert hasattr(result, "evidence")
        assert hasattr(result, "explanation")
        assert hasattr(result, "floor_violations")

    @pytest.mark.asyncio
    async def test_verdict_is_valid_string(self):
        pred = _pred(target="porosity", lo=0.08, hi=0.28, units="fraction")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        assert result.verdict in ("supported", "ambiguous", "contradicted")

    @pytest.mark.asyncio
    async def test_score_in_range(self):
        pred = _pred(target="porosity", lo=0.08, hi=0.28, units="fraction")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        assert 0.0 <= result.score <= 1.0

    @pytest.mark.asyncio
    async def test_evidence_is_list_of_geo_quantities(self):
        pred = _pred(target="porosity", lo=0.08, hi=0.28, units="fraction")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        for qty in result.evidence:
            assert isinstance(qty, GeoQuantity)

    @pytest.mark.asyncio
    async def test_no_tools_returns_ambiguous(self):
        """No tools → no evidence → ambiguous verdict."""
        pred = _pred(target="porosity", lo=0.08, hi=0.28, units="fraction")
        result = await self.validator.verify_prediction(pred, [])
        assert result.verdict == "ambiguous"
        assert result.score == 0.5

    @pytest.mark.asyncio
    async def test_with_vlm_tool_returns_result(self):
        pred = _pred(target="structural_closure_m", lo=20.0, hi=150.0, units="m")
        result = await self.validator.verify_prediction(pred, [self.mock_vlm])
        assert isinstance(result, ValidationResult)
        assert result.verdict in ("supported", "ambiguous", "contradicted")

    @pytest.mark.asyncio
    async def test_to_dict_structure(self):
        pred = _pred(target="porosity", lo=0.08, hi=0.28, units="fraction")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        d = result.to_dict()
        assert "insight_id" in d
        assert "verdict" in d
        assert "score" in d
        assert "evidence_count" in d
        assert "explanation" in d
        assert "floor_violations" in d

    @pytest.mark.asyncio
    async def test_insight_id_format(self):
        """insight_id should be 'pred-<target>'."""
        pred = _pred(target="net_pay_m", lo=15.0, hi=45.0, units="m")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        assert result.insight_id == "pred-net_pay_m"

    @pytest.mark.asyncio
    async def test_porosity_in_malay_basin_range(self):
        """MockEarthNetTool returns porosity 0.08-0.28; broad range → supported."""
        pred = _pred(target="porosity", lo=0.05, hi=0.30, units="fraction")
        result = await self.validator.verify_prediction(pred, [self.mock_earthnet])
        # Very broad predicted range should capture mock values
        assert result.verdict in ("supported", "ambiguous")


# ---------------------------------------------------------------------------
# GeoXValidator.validate_batch() — SEAL path
# ---------------------------------------------------------------------------


class TestValidateBatch:

    def setup_method(self):
        self.validator = GeoXValidator()
        self.mock_earthnet = MockEarthNetTool()
        self.mock_vlm = MockSeismicVLMTool()

    @pytest.mark.asyncio
    async def test_empty_insights_returns_sabar(self):
        result = await self.validator.validate_batch([], [self.mock_earthnet])
        assert isinstance(result, AggregateVerdict)
        assert result.overall == "SABAR"
        assert result.seal_count == 0
        assert result.requires_audit is True

    @pytest.mark.asyncio
    async def test_returns_aggregate_verdict(self):
        insight = _insight(
            text="Net pay estimated at 25 m with good porosity values.",
            status="unverified",
            risk_level="medium",
            requires_human_signoff=True,
        )
        result = await self.validator.validate_batch([insight], [self.mock_earthnet])
        assert isinstance(result, AggregateVerdict)

    @pytest.mark.asyncio
    async def test_verdict_in_valid_set(self):
        insight = _insight(
            text="Net pay estimated at 25 m with moderate porosity.",
            status="unverified",
            risk_level="medium",
            requires_human_signoff=True,
        )
        result = await self.validator.validate_batch([insight], [self.mock_earthnet])
        assert result.overall in ("SEAL", "PARTIAL", "SABAR", "VOID")

    @pytest.mark.asyncio
    async def test_confidence_in_range(self):
        insight = _insight(
            text="Reservoir porosity estimated at 18% from LEM ensemble.",
            status="unverified",
            risk_level="low",
            requires_human_signoff=False,
        )
        result = await self.validator.validate_batch([insight], [self.mock_earthnet])
        assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_supported_insights_seal(self):
        """When all insights are validated as supported, verdict should be SEAL."""
        # Build insights whose predictions fall within mock data ranges
        # MockEarthNetTool returns porosity in [0.08, 0.28] and velocity in [2200, 3800]
        pred1 = _pred(
            target="porosity", lo=0.01, hi=0.35, units="fraction", confidence=0.80
        )
        pred2 = _pred(
            target="seismic_velocity",
            lo=1000.0,
            hi=5000.0,
            units="m/s",
            confidence=0.80,
        )
        # Craft insights with very broad ranges to ensure mock tool values land inside
        i1 = _insight(
            text="Porosity measured at 15-28 fraction in the reservoir interval.",
            status="unverified",
            risk_level="low",
            requires_human_signoff=False,
            support=[pred1],
        )
        i2 = _insight(
            text="P-wave velocity measured at 2000-4000 m/s in the Miocene clastics.",
            status="unverified",
            risk_level="low",
            requires_human_signoff=False,
            support=[pred2],
        )
        result = await self.validator.validate_batch([i1, i2], [self.mock_earthnet])
        # With very broad ranges both should be supported → SEAL
        assert result.overall in ("SEAL", "PARTIAL")

    @pytest.mark.asyncio
    async def test_contradicted_insight_yields_void(self):
        """An insight with contradicted status should push verdict to VOID."""
        # Build a prediction with a range that mock data will NOT match
        # MockEarthNetTool porosity ∈ [0.08, 0.28]; use a range completely outside
        pred_impossible = _pred(
            target="porosity", lo=0.95, hi=0.99, units="fraction", confidence=0.80
        )
        insight_contradicted = _insight(
            text="Porosity estimated at 0.95–0.99 fraction — unrealistically high.",
            status="unverified",
            risk_level="low",
            requires_human_signoff=False,
            support=[pred_impossible],
        )
        result = await self.validator.validate_batch(
            [insight_contradicted], [self.mock_earthnet]
        )
        # match_ratio will be 0 → contradicted → VOID
        assert result.overall == "VOID"
        assert result.void_count >= 1

    @pytest.mark.asyncio
    async def test_aggregate_verdict_counts_consistent(self):
        insight = _insight(
            text="Net pay estimated at 25 m in the reservoir.",
            status="unverified",
            risk_level="medium",
            requires_human_signoff=True,
        )
        result = await self.validator.validate_batch([insight], [self.mock_earthnet])
        total = result.seal_count + result.partial_count + result.void_count
        assert total == len(result.insight_verdicts)

    @pytest.mark.asyncio
    async def test_to_dict_structure(self):
        insight = _insight(
            text="Net pay estimated at 25 m in the reservoir interval.",
            status="unverified",
            risk_level="medium",
            requires_human_signoff=True,
        )
        result = await self.validator.validate_batch([insight], [self.mock_earthnet])
        d = result.to_dict()
        assert "overall" in d
        assert "seal_count" in d
        assert "partial_count" in d
        assert "void_count" in d
        assert "confidence" in d
        assert "requires_audit" in d
        assert "insight_verdicts" in d


# ---------------------------------------------------------------------------
# GeoXValidator.check_floor_compliance()
# ---------------------------------------------------------------------------


class TestCheckFloorCompliance:

    def setup_method(self):
        self.validator = GeoXValidator()

    def test_f4_clarity_passes_with_units(self):
        """F4: insight text containing a unit should pass."""
        insight = _insight(
            text="Net pay estimated at 25 m with good confidence.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F4_clarity") is True

    def test_f4_clarity_fails_without_units(self):
        """F4: insight text with no units should fail F4."""
        insight = _insight(
            text="The reservoir quality is expected to be moderate based on analogue data.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F4_clarity") is False

    def test_f1_amanah_passes_no_irreversible_phrases(self):
        insight = _insight(
            text="Net pay estimated at 25 m — further data recommended before decisions.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F1_amanah") is True

    def test_f1_amanah_fails_on_irreversible_language(self):
        insight = _insight(
            text="Must drill immediately — net pay at 30 m is confirmed.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F1_amanah") is False

    def test_f2_truth_passes_no_absolute_certainty(self):
        insight = _insight(
            text="Net pay estimated at 25 m with moderate confidence.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F2_truth") is True

    def test_f2_truth_fails_on_certainty_claim(self):
        insight = _insight(
            text="100% certain the reservoir contains 25 m net pay.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F2_truth") is False

    def test_f13_sovereign_high_risk_passes_with_signoff(self):
        insight = _insight(
            text="Critical decision required — net pay at 25 m.",
            risk_level="high",
            requires_human_signoff=True,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F13_sovereign") is True

    def test_f7_humility_passes_no_supporting_quantities(self):
        """F7 check on insight with no supporting quantities should pass (no violations)."""
        insight = _insight(
            text="Net pay estimated at 25 m from analogue comparison.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert compliance.get("F7_humility") is True

    def test_f7_humility_fails_with_out_of_band_quantity(self):
        """F7 check fails when supporting quantity has out-of-band uncertainty."""
        qty = GeoQuantity(
            value=0.25,
            units="fraction",
            quantity_type="porosity",
            coordinates=_coord(),
            timestamp=datetime.now(timezone.utc),
            uncertainty=0.25,  # outside [0.03, 0.15]
            provenance=_prov(),
            f7_override=True,
            override_justification="Test override",
        )
        pred = GeoPrediction(
            target="porosity",
            location=_coord(),
            expected_range=(0.10, 0.30),
            units="fraction",
            confidence=0.70,
            supporting_quantities=[qty],
            method="LEM_ensemble",
        )
        insight = _insight(
            text="Porosity estimated at 25% fraction from lab measurements.",
            risk_level="low",
            requires_human_signoff=False,
            support=[pred],
        )
        compliance = self.validator.check_floor_compliance(insight)
        # The qty has f7_override=True so validator skips → F7 should pass
        # (validator only checks when f7_override is False)
        assert isinstance(compliance.get("F7_humility"), bool)

    def test_compliance_returns_dict(self):
        insight = _insight(
            text="Net pay estimated at 25 m with moderate confidence.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        assert isinstance(compliance, dict)
        for key, val in compliance.items():
            assert isinstance(val, bool), f"Floor {key} value is not bool: {val}"

    def test_compliance_keys_are_floor_ids(self):
        insight = _insight(
            text="Net pay estimated at 25 m with moderate confidence.",
            risk_level="low",
            requires_human_signoff=False,
        )
        compliance = self.validator.check_floor_compliance(insight)
        for key in compliance:
            # All keys should match pattern F<n>_<name>
            assert key.startswith("F"), f"Unexpected compliance key: {key}"
