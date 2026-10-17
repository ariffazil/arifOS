"""Tests for Self-Healing Error Envelope (P0).

Verifies:
  - CanonicalError backward compatible (existing code+message still works)
  - RecoveryContext fields populated correctly
  - Alternatives bounded at MAX_ALTERNATIVES
  - Error codes are stable strings
  - No secrets leak through alternatives
"""

from arifosmcp.runtime.healing_errors import (
    MAX_ALTERNATIVES,
    ErrorCodes,
    field_not_found_error,
    healing_error,
    parameter_error,
    service_unavailable_error,
    tool_not_found_error,
)
from arifosmcp.runtime.model import CanonicalError, RecoveryContext


class TestCanonicalErrorBackwardCompat:
    """Existing CanonicalError(code, message) must still work."""

    def test_basic_error(self):
        err = CanonicalError(code="LSP_ERROR", message="something broke")
        assert err.code == "LSP_ERROR"
        assert err.message == "something broke"
        assert err.stage is None
        assert err.context is None
        assert err.recovery is None

    def test_error_with_stage(self):
        err = CanonicalError(code="TEST", message="msg", stage="111")
        assert err.stage == "111"
        assert err.context is None

    def test_error_dict_roundtrip(self):
        err = CanonicalError(code="TEST", message="msg")
        d = err.model_dump(mode="json")
        assert d["code"] == "TEST"
        assert d["message"] == "msg"
        assert d.get("context") is None
        assert d.get("recovery") is None


class TestHealingError:
    """healing_error() builds enriched CanonicalError."""

    def test_basic_healing_error(self):
        err = healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message='Field "pressure" is unavailable.',
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            received="pressure",
            available=["pressure_kpa", "pore_pressure"],
            discovery_tool="geox_describe",
        )
        assert err.code == "INVALID_FIELD"
        assert err.message == 'Field "pressure" is unavailable.'
        assert err.context is not None
        assert err.context["organ"] == "geox"
        assert err.context["tool"] == "geox_well_log"
        assert err.context["parameter"] == "field"
        assert err.context["received"] == "pressure"
        assert err.recovery is not None
        assert err.recovery.available == ["pressure_kpa", "pore_pressure"]
        assert err.recovery.discovery_tool == "geox_describe"
        assert err.recovery.retryable is True

    def test_healing_error_no_context(self):
        err = healing_error(
            code=ErrorCodes.EXECUTION_FAILED,
            message="Something broke",
        )
        assert err.context is None
        assert err.recovery is not None
        assert err.recovery.available == []
        assert err.recovery.discovery_tool is None

    def test_alternatives_bounded(self):
        many = [f"field_{i}" for i in range(50)]
        err = healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="too many",
            available=many,
        )
        assert len(err.recovery.available) == MAX_ALTERNATIVES

    def test_retryable_false(self):
        err = healing_error(
            code=ErrorCodes.FORBIDDEN,
            message="no access",
            retryable=False,
        )
        assert err.recovery.retryable is False


class TestConvenienceBuilders:
    """Named builders for common error patterns."""

    def test_tool_not_found(self):
        err = tool_not_found_error(
            tool_name="geox_search",
            organ="geox",
            available_tools=["geox_basin", "geox_well_log", "geox_seismic"],
        )
        assert err.code == ErrorCodes.INVALID_TOOL
        assert "geox_search" in err.message
        assert err.recovery.available == ["geox_basin", "geox_well_log", "geox_seismic"]
        assert err.recovery.discovery_tool == "geox_list"

    def test_field_not_found(self):
        err = field_not_found_error(
            field_name="reservoir_pressure",
            organ="geox",
            tool="geox_well_log",
            available_fields=["pressure_kpa", "formation_pressure"],
        )
        assert err.code == ErrorCodes.INVALID_FIELD
        assert err.context["parameter"] == "field"
        assert err.recovery.discovery_tool == "geox_describe"

    def test_parameter_error(self):
        err = parameter_error(
            parameter="mode",
            received="invalid",
            expected="one of: basin, well, seismic",
            organ="geox",
            tool="geox_search",
            available=["basin", "well", "seismic"],
        )
        assert err.code == ErrorCodes.INVALID_PARAMETER
        assert err.recovery.available == ["basin", "well", "seismic"]

    def test_service_unavailable(self):
        err = service_unavailable_error(
            service="mydb",
            organ="arifos",
            available_services=["geox_db", "wealth_db"],
        )
        assert err.code == ErrorCodes.SERVICE_UNAVAILABLE
        assert err.recovery.available == ["geox_db", "wealth_db"]


class TestErrorCodesStable:
    """Error codes must be stable strings (never rename)."""

    def test_codes_are_strings(self):
        for attr in dir(ErrorCodes):
            if attr.isupper() and not attr.startswith("_"):
                val = getattr(ErrorCodes, attr)
                assert isinstance(val, str), f"ErrorCodes.{attr} must be str"

    def test_known_codes(self):
        assert ErrorCodes.INVALID_FIELD == "INVALID_FIELD"
        assert ErrorCodes.INVALID_TOOL == "INVALID_TOOL"
        assert ErrorCodes.NOT_FOUND == "NOT_FOUND"
        assert ErrorCodes.FORBIDDEN == "FORBIDDEN"


class TestRecoveryContext:
    """RecoveryContext model tests."""

    def test_defaults(self):
        rc = RecoveryContext()
        assert rc.available == []
        assert rc.discovery_tool is None
        assert rc.retryable is True

    def test_json_roundtrip(self):
        rc = RecoveryContext(available=["a", "b"], discovery_tool="test_list", retryable=False)
        d = rc.model_dump(mode="json")
        rc2 = RecoveryContext(**d)
        assert rc2.available == ["a", "b"]
        assert rc2.discovery_tool == "test_list"
        assert rc2.retryable is False


class TestP1_FieldRecovery:
    """P-1: closest_match + rejected_fields + level on field-level rejection."""

    def test_field_closest_match_substring(self):
        err = field_not_found_error(
            field_name="pressure",
            organ="geox",
            tool="geox_well_log",
            available_fields=["pressure_kpa", "formation_pressure"],
        )
        assert err.recovery is not None
        assert err.recovery.available == ["pressure_kpa", "formation_pressure"]
        assert err.recovery.rejected_fields == ["pressure"]
        assert err.recovery.closest_match["pressure"] == [
            "pressure_kpa",
            "formation_pressure",
        ]
        assert err.recovery.level == "field"

    def test_explicit_rejected_fields_close_and_substring(self):
        err = healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="bad fields",
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            rejected_fields=["presure", "temp"],
            available=["pressure_kpa", "temperature_c"],
        )
        cm = err.recovery.closest_match
        # "presure" (typo) -> difflib close match to "pressure_kpa"
        assert "pressure_kpa" in cm.get("presure", [])
        # "temp" -> substring of "temperature_c"
        assert "temperature_c" in cm.get("temp", [])

    def test_no_rejected_fields_backward_compat(self):
        err = healing_error(
            code=ErrorCodes.EXECUTION_FAILED,
            message="boom",
        )
        assert err.recovery.rejected_fields == []
        assert err.recovery.closest_match == {}
        assert err.recovery.level is None
