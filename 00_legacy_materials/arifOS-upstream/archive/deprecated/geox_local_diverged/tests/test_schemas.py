"""
GEOX Schema Tests
DITEMPA BUKAN DIBERI

Full pytest test suite for geox_schemas.py — all Pydantic v2 models,
field validators, model validators, and the export_json_schemas() utility.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoInsight,
    GeoPrediction,
    GeoQuantity,
    GeoRequest,
    GeoResponse,
    ProvenanceRecord,
    export_json_schemas,
)

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_coordinate(
    lat: float = 4.5, lon: float = 104.2, depth: float | None = 2500.0
) -> CoordinatePoint:
    return CoordinatePoint(latitude=lat, longitude=lon, depth_m=depth)


def _make_provenance(
    source_id: str = "WELL-LOG-001", source_type: str = "sensor"
) -> ProvenanceRecord:
    return ProvenanceRecord(
        source_id=source_id,
        source_type=source_type,  # type: ignore[arg-type]
        timestamp=datetime.now(timezone.utc),
        confidence=0.82,
    )


def _make_geo_quantity(
    value: float = 0.18,
    units: str = "fraction",
    quantity_type: str = "porosity",
    uncertainty: float = 0.08,
) -> GeoQuantity:
    return GeoQuantity(
        value=value,
        units=units,
        quantity_type=quantity_type,
        coordinates=_make_coordinate(),
        timestamp=datetime.now(timezone.utc),
        uncertainty=uncertainty,
        provenance=_make_provenance(),
    )


def _make_geo_prediction(
    target: str = "net_pay_m",
    lo: float = 15.0,
    hi: float = 45.0,
    units: str = "m",
    confidence: float = 0.72,
) -> GeoPrediction:
    return GeoPrediction(
        target=target,
        location=_make_coordinate(),
        expected_range=(lo, hi),
        units=units,
        confidence=confidence,
        method="LEM_ensemble",
    )


def _make_geo_insight(
    text: str = "Net pay estimated at 25–45 m with moderate confidence.",
    status: str = "supported",
    risk_level: str = "medium",
    requires_human_signoff: bool = True,
) -> GeoInsight:
    return GeoInsight(
        text=text,
        status=status,  # type: ignore[arg-type]
        risk_level=risk_level,  # type: ignore[arg-type]
        requires_human_signoff=requires_human_signoff,
    )


def _make_geo_request() -> GeoRequest:
    return GeoRequest(
        query="Evaluate HC potential of Blok Selatan anticline in Malay Basin.",
        prospect_name="Blok Selatan",
        location=_make_coordinate(lat=4.5, lon=104.2),
        basin="Malay Basin",
        play_type="structural",
        available_data=["seismic_3d", "well_logs"],
        risk_tolerance="medium",
        requester_id="USER-geo-test-001",
    )


# ---------------------------------------------------------------------------
# CoordinatePoint
# ---------------------------------------------------------------------------


class TestCoordinatePoint:

    def test_valid_creation_basic(self):
        cp = CoordinatePoint(latitude=4.5, longitude=104.2)
        assert cp.latitude == 4.5
        assert cp.longitude == 104.2
        assert cp.depth_m is None
        assert cp.crs == "EPSG:4326"

    def test_valid_creation_with_depth(self):
        cp = CoordinatePoint(latitude=4.5, longitude=104.2, depth_m=2500.0)
        assert cp.depth_m == 2500.0

    def test_valid_creation_custom_crs(self):
        cp = CoordinatePoint(latitude=4.5, longitude=104.2, crs="EPSG:32648")
        assert cp.crs == "EPSG:32648"

    def test_latitude_at_positive_boundary(self):
        cp = CoordinatePoint(latitude=90.0, longitude=0.0)
        assert cp.latitude == 90.0

    def test_latitude_at_negative_boundary(self):
        cp = CoordinatePoint(latitude=-90.0, longitude=0.0)
        assert cp.latitude == -90.0

    def test_longitude_at_positive_boundary(self):
        cp = CoordinatePoint(latitude=0.0, longitude=180.0)
        assert cp.longitude == 180.0

    def test_longitude_at_negative_boundary(self):
        cp = CoordinatePoint(latitude=0.0, longitude=-180.0)
        assert cp.longitude == -180.0

    @pytest.mark.parametrize("bad_lat", [90.001, -90.001, 180.0, -180.0, 999.0])
    def test_latitude_out_of_range_raises(self, bad_lat: float):
        with pytest.raises(ValidationError):
            CoordinatePoint(latitude=bad_lat, longitude=0.0)

    @pytest.mark.parametrize("bad_lon", [180.001, -180.001, 360.0, -270.0, 999.0])
    def test_longitude_out_of_range_raises(self, bad_lon: float):
        with pytest.raises(ValidationError):
            CoordinatePoint(latitude=0.0, longitude=bad_lon)

    def test_depth_extreme_valid(self):
        # Just inside the allowed range
        cp = CoordinatePoint(latitude=0.0, longitude=0.0, depth_m=999999.9)
        assert cp.depth_m == 999999.9

    def test_depth_extreme_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            CoordinatePoint(latitude=0.0, longitude=0.0, depth_m=1_000_001.0)

    def test_negative_depth_allowed(self):
        """Negative depth = above surface (elevation)."""
        cp = CoordinatePoint(latitude=0.0, longitude=0.0, depth_m=-50.0)
        assert cp.depth_m == -50.0

    def test_round_trip(self):
        cp = CoordinatePoint(latitude=4.5, longitude=104.2, depth_m=2500.0, crs="EPSG:4326")
        data = cp.model_dump()
        restored = CoordinatePoint(**data)
        assert restored.latitude == cp.latitude
        assert restored.longitude == cp.longitude
        assert restored.depth_m == cp.depth_m
        assert restored.crs == cp.crs


# ---------------------------------------------------------------------------
# ProvenanceRecord
# ---------------------------------------------------------------------------


class TestProvenanceRecord:

    @pytest.mark.parametrize(
        "source_type", ["LEM", "VLM", "sensor", "simulator", "human", "literature"]
    )
    def test_valid_all_source_types(self, source_type: str):
        prov = ProvenanceRecord(
            source_id=f"SRC-{source_type}-001",
            source_type=source_type,  # type: ignore[arg-type]
            timestamp=datetime.now(timezone.utc),
            confidence=0.80,
        )
        assert prov.source_type == source_type

    def test_valid_creation_all_required_fields(self):
        prov = ProvenanceRecord(
            source_id="LEM-MALAY-2024-001",
            source_type="LEM",
            timestamp=datetime.now(timezone.utc),
            confidence=0.82,
        )
        assert prov.source_id == "LEM-MALAY-2024-001"
        assert prov.source_type == "LEM"
        assert prov.confidence == 0.82
        assert prov.checksum is None
        assert prov.citation is None
        # Default floor_check populated
        assert "F1_amanah" in prov.floor_check
        assert "F9_anti_hantu" in prov.floor_check
        assert all(isinstance(v, bool) for v in prov.floor_check.values())

    def test_optional_checksum(self):
        prov = ProvenanceRecord(
            source_id="SRC-001",
            source_type="sensor",
            timestamp=datetime.now(timezone.utc),
            confidence=0.90,
            checksum="a3f2c1b4e8d9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6",
        )
        assert prov.checksum is not None

    def test_invalid_source_type_raises(self):
        with pytest.raises(ValidationError):
            ProvenanceRecord(
                source_id="SRC-001",
                source_type="unknown_type",  # type: ignore[arg-type]
                timestamp=datetime.now(timezone.utc),
                confidence=0.80,
            )

    def test_confidence_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            ProvenanceRecord(
                source_id="SRC-001",
                source_type="LEM",
                timestamp=datetime.now(timezone.utc),
                confidence=1.5,  # > 1.0
            )

    def test_empty_source_id_raises(self):
        with pytest.raises(ValidationError):
            ProvenanceRecord(
                source_id="",
                source_type="LEM",
                timestamp=datetime.now(timezone.utc),
                confidence=0.80,
            )

    def test_source_id_whitespace_stripped(self):
        """source_id_no_whitespace validator strips surrounding whitespace."""
        prov = ProvenanceRecord(
            source_id="  LEM-001  ",
            source_type="LEM",
            timestamp=datetime.now(timezone.utc),
            confidence=0.80,
        )
        assert prov.source_id == "LEM-001"

    def test_round_trip(self):
        prov = _make_provenance()
        data = prov.model_dump()
        restored = ProvenanceRecord(**data)
        assert restored.source_id == prov.source_id
        assert restored.confidence == prov.confidence


# ---------------------------------------------------------------------------
# GeoQuantity
# ---------------------------------------------------------------------------


class TestGeoQuantity:

    def test_valid_creation(self):
        qty = _make_geo_quantity()
        assert qty.value == 0.18
        assert qty.units == "fraction"
        assert qty.quantity_type == "porosity"
        assert qty.uncertainty == 0.08
        assert not qty.f7_override

    @pytest.mark.parametrize("uncertainty", [0.03, 0.07, 0.10, 0.15])
    def test_f7_compliant_uncertainty(self, uncertainty: float):
        """Values in [0.03, 0.15] must pass the F7 validator."""
        qty = _make_geo_quantity(uncertainty=uncertainty)
        assert qty.uncertainty == uncertainty

    @pytest.mark.parametrize("bad_uncertainty", [0.00, 0.01, 0.02, 0.16, 0.20, 0.50])
    def test_f7_violation_raises(self, bad_uncertainty: float):
        """Uncertainty outside [0.03, 0.15] raises ValidationError (F7)."""
        with pytest.raises(ValidationError, match="F7 violation"):
            _make_geo_quantity(uncertainty=bad_uncertainty)

    def test_f7_override_allows_out_of_band(self):
        """f7_override=True with justification allows unusual uncertainty."""
        qty = GeoQuantity(
            value=0.02,
            units="fraction",
            quantity_type="porosity",
            coordinates=_make_coordinate(),
            timestamp=datetime.now(timezone.utc),
            uncertainty=0.25,  # outside band
            provenance=_make_provenance(),
            f7_override=True,
            override_justification="Lab measurement with certified uncertainty of 25% for tight carbonate.",
        )
        assert qty.f7_override is True
        assert qty.uncertainty == 0.25

    def test_f7_override_without_justification_raises(self):
        """f7_override=True without justification must raise ValidationError."""
        with pytest.raises(ValidationError, match="override_justification"):
            GeoQuantity(
                value=0.02,
                units="fraction",
                quantity_type="porosity",
                coordinates=_make_coordinate(),
                timestamp=datetime.now(timezone.utc),
                uncertainty=0.25,
                provenance=_make_provenance(),
                f7_override=True,
                override_justification=None,
            )

    def test_round_trip(self):
        qty = _make_geo_quantity()
        data = qty.model_dump()
        restored = GeoQuantity(**data)
        assert restored.value == qty.value
        assert restored.units == qty.units
        assert restored.uncertainty == qty.uncertainty


# ---------------------------------------------------------------------------
# GeoPrediction
# ---------------------------------------------------------------------------


class TestGeoPrediction:

    def test_valid_creation(self):
        pred = _make_geo_prediction()
        assert pred.target == "net_pay_m"
        assert pred.expected_range == (15.0, 45.0)
        assert pred.units == "m"
        assert pred.confidence == 0.72
        assert pred.method == "LEM_ensemble"
        assert pred.supporting_quantities == []
        assert pred.time_window is None

    def test_valid_with_supporting_quantities(self):
        qty = _make_geo_quantity()
        pred = GeoPrediction(
            target="porosity",
            location=_make_coordinate(),
            expected_range=(0.10, 0.25),
            units="fraction",
            confidence=0.80,
            supporting_quantities=[qty],
            method="seismic_inversion",
        )
        assert len(pred.supporting_quantities) == 1

    def test_range_order_valid(self):
        """min <= max must hold."""
        pred = _make_geo_prediction(lo=10.0, hi=10.0)  # equal is valid
        assert pred.expected_range == (10.0, 10.0)

    def test_range_inverted_raises(self):
        """min > max raises ValidationError."""
        with pytest.raises(ValidationError, match="expected_range min"):
            _make_geo_prediction(lo=50.0, hi=10.0)

    @pytest.mark.parametrize(
        "method", ["LEM_ensemble", "seismic_inversion", "analogue_matching", "basin_simulation"]
    )
    def test_various_methods(self, method: str):
        _make_geo_prediction()
        # Re-create with different method
        pred2 = GeoPrediction(
            target="net_pay_m",
            location=_make_coordinate(),
            expected_range=(15.0, 45.0),
            units="m",
            confidence=0.72,
            method=method,
        )
        assert pred2.method == method

    def test_confidence_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            _make_geo_prediction(confidence=1.5)

    def test_round_trip(self):
        pred = _make_geo_prediction()
        data = pred.model_dump()
        restored = GeoPrediction(**data)
        assert restored.target == pred.target
        assert restored.expected_range == pred.expected_range
        assert restored.confidence == pred.confidence


# ---------------------------------------------------------------------------
# GeoInsight
# ---------------------------------------------------------------------------


class TestGeoInsight:

    def test_valid_creation(self):
        insight = _make_geo_insight()
        assert insight.text == "Net pay estimated at 25–45 m with moderate confidence."
        assert insight.status == "supported"
        assert insight.risk_level == "medium"
        assert insight.requires_human_signoff is True
        # insight_id should be a valid UUID4
        uuid.UUID(insight.insight_id, version=4)

    def test_insight_id_auto_generated(self):
        i1 = _make_geo_insight()
        i2 = _make_geo_insight()
        assert i1.insight_id != i2.insight_id  # unique per instance

    @pytest.mark.parametrize("status", ["supported", "ambiguous", "contradicted", "unverified"])
    def test_valid_status_values(self, status: str):
        insight = GeoInsight(
            text="Net pay estimated at 25 m in the test zone.",
            status=status,  # type: ignore[arg-type]
            risk_level="low",
            requires_human_signoff=False,
        )
        assert insight.status == status

    def test_f13_high_risk_requires_signoff(self):
        """F13: high risk must have requires_human_signoff=True."""
        with pytest.raises(ValidationError, match="F13 violation"):
            GeoInsight(
                text="Net pay estimated at 25 m — drastic decision required.",
                status="supported",
                risk_level="high",
                requires_human_signoff=False,  # violation
            )

    def test_f13_critical_risk_requires_signoff(self):
        """F13: critical risk must have requires_human_signoff=True."""
        with pytest.raises(ValidationError, match="F13 violation"):
            GeoInsight(
                text="Critical formation pressure at 50 MPa — emergency shutdown risk.",
                status="supported",
                risk_level="critical",
                requires_human_signoff=False,  # violation
            )

    def test_f13_high_risk_with_signoff_passes(self):
        insight = GeoInsight(
            text="Net pay estimated at 25 m — drastic decision required.",
            status="supported",
            risk_level="high",
            requires_human_signoff=True,
        )
        assert insight.risk_level == "high"
        assert insight.requires_human_signoff is True

    def test_f13_critical_risk_with_signoff_passes(self):
        insight = GeoInsight(
            text="Critical formation pressure at 50 MPa — emergency shutdown risk.",
            status="supported",
            risk_level="critical",
            requires_human_signoff=True,
        )
        assert insight.risk_level == "critical"

    def test_low_risk_no_signoff_passes(self):
        insight = GeoInsight(
            text="Net pay estimated at 25 m — low-risk interpretation.",
            status="supported",
            risk_level="low",
            requires_human_signoff=False,
        )
        assert insight.requires_human_signoff is False

    def test_text_too_short_raises(self):
        with pytest.raises(ValidationError):
            GeoInsight(
                text="Short",  # < 10 chars
                status="supported",
                risk_level="low",
                requires_human_signoff=False,
            )

    def test_floor_verdicts_default(self):
        insight = _make_geo_insight()
        assert "F1_amanah" in insight.floor_verdicts
        assert "F13_sovereign" in insight.floor_verdicts
        assert all(isinstance(v, bool) for v in insight.floor_verdicts.values())

    def test_round_trip(self):
        insight = _make_geo_insight()
        data = insight.model_dump()
        restored = GeoInsight(**data)
        assert restored.insight_id == insight.insight_id
        assert restored.text == insight.text
        assert restored.status == insight.status


# ---------------------------------------------------------------------------
# GeoRequest
# ---------------------------------------------------------------------------


class TestGeoRequest:

    def test_valid_creation(self):
        req = _make_geo_request()
        assert req.prospect_name == "Blok Selatan"
        assert req.basin == "Malay Basin"
        assert req.play_type == "structural"
        assert req.risk_tolerance == "medium"
        assert req.requester_id == "USER-geo-test-001"
        assert "seismic_3d" in req.available_data
        # request_id auto-generated as valid UUID
        uuid.UUID(req.request_id, version=4)

    def test_request_id_unique(self):
        r1 = _make_geo_request()
        r2 = _make_geo_request()
        assert r1.request_id != r2.request_id

    @pytest.mark.parametrize("risk_tolerance", ["low", "medium", "high"])
    def test_risk_tolerance_values(self, risk_tolerance: str):
        req = GeoRequest(
            query="Evaluate porosity of Test Prospect.",
            prospect_name="Test Prospect",
            location=_make_coordinate(),
            basin="Test Basin",
            play_type="structural",
            risk_tolerance=risk_tolerance,  # type: ignore[arg-type]
            requester_id="USER-001",
        )
        assert req.risk_tolerance == risk_tolerance

    def test_invalid_risk_tolerance_raises(self):
        with pytest.raises(ValidationError):
            GeoRequest(
                query="Evaluate porosity of Test Prospect.",
                prospect_name="Test Prospect",
                location=_make_coordinate(),
                basin="Test Basin",
                play_type="structural",
                risk_tolerance="extreme",  # type: ignore[arg-type]
                requester_id="USER-001",
            )

    def test_query_too_short_raises(self):
        with pytest.raises(ValidationError):
            GeoRequest(
                query="Hi",  # < 5 chars
                prospect_name="Test",
                location=_make_coordinate(),
                basin="Test Basin",
                play_type="structural",
                risk_tolerance="low",
                requester_id="USER-001",
            )

    def test_empty_available_data(self):
        req = GeoRequest(
            query="Evaluate porosity of Test Prospect.",
            prospect_name="Test Prospect",
            location=_make_coordinate(),
            basin="Test Basin",
            play_type="structural",
            risk_tolerance="low",
            requester_id="USER-001",
        )
        assert req.available_data == []

    def test_timestamp_auto_set(self):
        req = _make_geo_request()
        assert isinstance(req.timestamp, datetime)

    def test_round_trip(self):
        req = _make_geo_request()
        data = req.model_dump()
        restored = GeoRequest(**data)
        assert restored.request_id == req.request_id
        assert restored.prospect_name == req.prospect_name
        assert restored.basin == req.basin


# ---------------------------------------------------------------------------
# GeoResponse
# ---------------------------------------------------------------------------


class TestGeoResponse:

    def test_valid_creation_minimal(self):
        req = _make_geo_request()
        resp = GeoResponse(
            request_id=req.request_id,
            verdict="PARTIAL",
            confidence_aggregate=0.63,
        )
        assert resp.verdict == "PARTIAL"
        assert resp.confidence_aggregate == 0.63
        assert resp.insights == []
        assert resp.predictions == []
        assert resp.provenance_chain == []
        assert resp.audit_log == []
        assert resp.human_signoff_required is False
        uuid.UUID(resp.response_id, version=4)

    @pytest.mark.parametrize("verdict", ["SEAL", "PARTIAL", "SABAR", "VOID"])
    def test_valid_verdict_values(self, verdict: str):
        req = _make_geo_request()
        resp = GeoResponse(
            request_id=req.request_id,
            verdict=verdict,  # type: ignore[arg-type]
            confidence_aggregate=0.50,
        )
        assert resp.verdict == verdict

    def test_invalid_verdict_raises(self):
        req = _make_geo_request()
        with pytest.raises(ValidationError):
            GeoResponse(
                request_id=req.request_id,
                verdict="UNKNOWN",  # type: ignore[arg-type]
                confidence_aggregate=0.50,
            )

    def test_confidence_out_of_range_raises(self):
        req = _make_geo_request()
        with pytest.raises(ValidationError):
            GeoResponse(
                request_id=req.request_id,
                verdict="SEAL",
                confidence_aggregate=1.5,  # > 1.0
            )

    def test_with_insights_and_predictions(self):
        req = _make_geo_request()
        insight = _make_geo_insight()
        pred = _make_geo_prediction()
        prov = _make_provenance()
        resp = GeoResponse(
            request_id=req.request_id,
            verdict="SEAL",
            confidence_aggregate=0.88,
            insights=[insight],
            predictions=[pred],
            provenance_chain=[prov],
            human_signoff_required=True,
            arifos_telemetry={
                "pipeline": "000→111→333→555→777→888→999",
                "stage": "999 SEAL",
                "floors": ["F1", "F2", "F4", "F7", "F13"],
                "confidence": 0.88,
                "verdict": "SEAL",
                "seal": "DITEMPA BUKAN DIBERI",
            },
        )
        assert len(resp.insights) == 1
        assert len(resp.predictions) == 1
        assert len(resp.provenance_chain) == 1
        assert resp.human_signoff_required is True
        assert resp.arifos_telemetry["seal"] == "DITEMPA BUKAN DIBERI"

    def test_response_id_unique(self):
        req = _make_geo_request()
        r1 = GeoResponse(request_id=req.request_id, verdict="SEAL", confidence_aggregate=0.90)
        r2 = GeoResponse(request_id=req.request_id, verdict="SEAL", confidence_aggregate=0.90)
        assert r1.response_id != r2.response_id

    def test_round_trip(self):
        req = _make_geo_request()
        resp = GeoResponse(
            request_id=req.request_id,
            verdict="PARTIAL",
            confidence_aggregate=0.63,
        )
        data = resp.model_dump()
        restored = GeoResponse(**data)
        assert restored.response_id == resp.response_id
        assert restored.verdict == resp.verdict
        assert restored.confidence_aggregate == resp.confidence_aggregate


# ---------------------------------------------------------------------------
# export_json_schemas()
# ---------------------------------------------------------------------------


class TestExportJsonSchemas:

    EXPECTED_KEYS = {
        "CoordinatePoint",
        "ProvenanceRecord",
        "GeoQuantity",
        "GeoPrediction",
        "GeoInsight",
        "GeoRequest",
        "GeoResponse",
    }

    def test_returns_dict(self):
        schemas = export_json_schemas()
        assert isinstance(schemas, dict)

    def test_expected_keys_present(self):
        schemas = export_json_schemas()
        assert self.EXPECTED_KEYS.issubset(set(schemas.keys()))

    def test_each_value_is_dict(self):
        schemas = export_json_schemas()
        for name, schema in schemas.items():
            assert isinstance(schema, dict), f"Schema for {name} is not a dict"

    def test_schemas_have_type_field(self):
        """Each JSON schema must contain 'type' or '$defs' at the top level."""
        schemas = export_json_schemas()
        for name, schema in schemas.items():
            has_type = "type" in schema or "$defs" in schema or "properties" in schema
            assert has_type, f"Schema for {name} missing type/properties/$defs"

    def test_count_matches_expected(self):
        schemas = export_json_schemas()
        assert len(schemas) == len(self.EXPECTED_KEYS)

    def test_coordinate_point_schema_has_lat_lon(self):
        schemas = export_json_schemas()
        cp_schema = schemas["CoordinatePoint"]
        props = cp_schema.get("properties", {})
        assert "latitude" in props
        assert "longitude" in props

    def test_geo_response_schema_has_verdict(self):
        schemas = export_json_schemas()
        gr_schema = schemas["GeoResponse"]
        props = gr_schema.get("properties", {})
        assert "verdict" in props
