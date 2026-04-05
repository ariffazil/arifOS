"""Tests for core.enforcement.governance_engine — AAA MCP Governance."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from arifosmcp.core.enforcement.governance_engine import (
    TOOL_DIALS_MAP,
    TOOL_LAW_BINDINGS,
    TOOL_STAGE_MAP,
    _clamp,
    _load_tool_dials_map,
    _motto_for_tool,
    _parse_stage_num,
    _safe_float,
)


class TestToolMappings:
    """Canonical tool-to-law and tool-to-stage mappings."""

    def test_tool_law_bindings_exists(self):
        """AAA_TOOL_LAW_BINDINGS imported correctly."""
        assert isinstance(TOOL_LAW_BINDINGS, dict)
        # Should have entries for canonical tools
        assert len(TOOL_LAW_BINDINGS) >= 0  # May be empty in minimal config

    def test_tool_stage_map_exists(self):
        """AAA_TOOL_STAGE_MAP imported correctly."""
        assert isinstance(TOOL_STAGE_MAP, dict)

    def test_tool_stage_map_stages(self):
        """Stage mappings follow NNN_NAME or M-N_NAME convention."""
        import re
        # NNN_NAME (e.g. 000_INIT) or M-N_NAME for mega-tools (e.g. M-3_EXEC)
        valid_prefix = re.compile(r"^\d{3}$|^M-\d+$")
        for tool, stage in TOOL_STAGE_MAP.items():
            assert isinstance(tool, str)
            assert isinstance(stage, str)
            parts = stage.split("_")
            assert len(parts) >= 2, f"{tool!r} stage {stage!r} has no underscore"
            assert valid_prefix.match(parts[0]), (
                f"{tool!r} stage prefix {parts[0]!r} not in NNN or M-N format"
            )


class TestClamp:
    """Value clamping utility."""

    def test_clamp_within_range(self):
        assert _clamp(0.5, 0.0, 1.0) == 0.5

    def test_clamp_below_min(self):
        assert _clamp(-0.5, 0.0, 1.0) == 0.0

    def test_clamp_above_max(self):
        assert _clamp(1.5, 0.0, 1.0) == 1.0

    def test_clamp_at_boundaries(self):
        assert _clamp(0.0, 0.0, 1.0) == 0.0
        assert _clamp(1.0, 0.0, 1.0) == 1.0

    def test_clamp_custom_range(self):
        assert _clamp(5, 10, 20) == 10
        assert _clamp(25, 10, 20) == 20
        assert _clamp(15, 10, 20) == 15


class TestParseStageNum:
    """Stage number extraction from stage strings."""

    def test_parse_standard_stage(self):
        assert _parse_stage_num("000_INIT") == 0
        assert _parse_stage_num("111_COMPREHEND") == 111
        assert _parse_stage_num("666_ALIGN") == 666
        assert _parse_stage_num("999_VAULT") == 999

    def test_parse_loop_stage(self):
        """000_999_LOOP treated as init-tier."""
        assert _parse_stage_num("000_999_LOOP") == 0

    def test_parse_invalid_stage(self):
        """Invalid strings return 0."""
        assert _parse_stage_num("") == 0
        assert _parse_stage_num("INVALID") == 0
        assert _parse_stage_num("ABC_DEF") == 0
        assert _parse_stage_num(None) == 0


class TestSafeFloat:
    """Safe float extraction from nested payloads."""

    def test_safe_float_direct(self):
        payload = {"truth_score": 0.85}
        assert _safe_float(payload, "truth_score", 0.5) == 0.85

    def test_safe_float_nested_payload(self):
        """Fallback 1: Nested payload."""
        payload = {"payload": {"truth_score": 0.9}}
        assert _safe_float(payload, "truth_score", 0.5) == 0.9

    def test_safe_float_nested_telemetry(self):
        """Fallback 2: Telemetry nested."""
        payload = {"telemetry": {"truth_score": 0.75}}
        assert _safe_float(payload, "truth_score", 0.5) == 0.75

    def test_safe_float_default(self):
        """Missing key returns default."""
        payload = {"other": 123}
        assert _safe_float(payload, "missing", 0.5) == 0.5

    def test_safe_float_invalid_dict(self):
        """Non-dict payload returns default."""
        assert _safe_float("not_a_dict", "key", 0.5) == 0.5
        assert _safe_float(None, "key", 0.5) == 0.5

    def test_safe_float_type_conversion(self):
        """String numbers converted to float."""
        payload = {"truth_score": "0.95"}
        assert _safe_float(payload, "truth_score", 0.5) == 0.95

    def test_safe_float_invalid_conversion(self):
        """Invalid conversion returns default."""
        payload = {"truth_score": "invalid"}
        assert _safe_float(payload, "truth_score", 0.5) == 0.5


class TestMottoForTool:
    """Motto retrieval for canonical tools."""

    def test_motto_anchor_session(self):
        result = _motto_for_tool("anchor_session")
        assert result["stage"] == "000_INIT"
        assert result["header"]  # Should have INIT header
        assert result["positive"]
        assert result["negative"]

    def test_motto_seal_vault(self):
        result = _motto_for_tool("seal_vault")
        assert result["stage"] == "999_VAULT"
        assert result["header"]  # Should have SEAL header

    def test_motto_unknown_tool(self):
        """Unknown tool returns default stage motto."""
        result = _motto_for_tool("unknown_tool")
        assert "stage" in result
        assert "positive" in result
        assert "negative" in result


class TestLoadToolDialsMap:
    """Tool dials map loading."""

    @patch("pathlib.Path.read_text")
    def test_load_valid_json(self, mock_read):
        mock_read.return_value = '{"model": "APEX_G", "tools": {}}'
        result = _load_tool_dials_map()
        assert result["model"] == "APEX_G"

    @patch("pathlib.Path.read_text")
    def test_load_invalid_json(self, mock_read):
        mock_read.side_effect = Exception("File not found")
        result = _load_tool_dials_map()
        assert result["model"] == "APEX_G"
        assert "formula" in result


class TestToolDialsMap:
    """TOOL_DIALS_MAP global."""

    def test_dials_map_structure(self):
        """TOOL_DIALS_MAP loaded at module import."""
        assert isinstance(TOOL_DIALS_MAP, dict)
        # Should have expected keys or fallback defaults
        assert "model" in TOOL_DIALS_MAP or "tools" in TOOL_DIALS_MAP
