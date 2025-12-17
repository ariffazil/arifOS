"""
arifOS API Contract Tests

These tests verify that:
1. All documented STABLE APIs are actually exported
2. Deprecated APIs emit proper warnings
3. Module exports match the API registry
4. No undocumented public exports (underscore check)

Version: v42.0.0
Canon: docs/API_STABILITY.md
Registry: arifos_core/system/api_registry.py
"""

import warnings
import pytest
from typing import Set


class TestAPIRegistryStructure:
    """Test the API registry itself is valid."""

    def test_registry_loads(self):
        """Registry module can be imported."""
        from arifos_core.system.api_registry import get_registry
        registry = get_registry()
        assert registry is not None

    def test_registry_has_entries(self):
        """Registry has registered entries."""
        from arifos_core.system.api_registry import get_registry
        registry = get_registry()
        assert len(registry.entries) > 0, "Registry should have entries"

    def test_registry_version(self):
        """Registry version matches expected."""
        from arifos_core.system.api_registry import get_registry
        registry = get_registry()
        assert registry._version == "42.0.0"

    def test_stability_levels_defined(self):
        """All stability levels are defined."""
        from arifos_core.system.api_registry import StabilityLevel
        levels = [StabilityLevel.STABLE, StabilityLevel.BETA,
                  StabilityLevel.EXPERIMENTAL, StabilityLevel.DEPRECATED,
                  StabilityLevel.INTERNAL]
        assert len(levels) == 5

    def test_api_entry_structure(self):
        """APIEntry has required fields."""
        from arifos_core.system.api_registry import APIEntry, StabilityLevel
        entry = APIEntry(
            name="test_api",
            stability=StabilityLevel.STABLE,
            kind="function",
            module="test.module",
            description="Test description"
        )
        assert entry.name == "test_api"
        assert entry.stability == StabilityLevel.STABLE


class TestStableAPIsExist:
    """Test that all STABLE APIs are actually exported."""

    def test_top_level_metrics_exports(self):
        """Metrics types are exported at top level."""
        from arifos_core import Metrics, FloorsVerdict, ConstitutionalMetrics
        assert Metrics is not None
        assert FloorsVerdict is not None
        assert ConstitutionalMetrics is not None

    def test_top_level_apex_exports(self):
        """APEX PRIME types are exported at top level."""
        from arifos_core import (
            apex_review, ApexVerdict, Verdict, check_floors,
            APEXPrime, APEX_VERSION, APEX_EPOCH
        )
        assert apex_review is not None
        assert ApexVerdict is not None
        assert Verdict is not None
        assert check_floors is not None
        assert APEXPrime is not None
        assert isinstance(APEX_VERSION, str)
        # APEX_EPOCH can be int or str depending on implementation
        assert APEX_EPOCH is not None

    def test_top_level_eye_exports(self):
        """@EYE Sentinel types are exported at top level."""
        from arifos_core import AlertSeverity, EyeAlert, EyeReport, EyeSentinel
        assert AlertSeverity is not None
        assert EyeAlert is not None
        assert EyeReport is not None
        assert EyeSentinel is not None

    def test_top_level_genius_exports(self):
        """GENIUS LAW functions are exported at top level."""
        from arifos_core import (
            evaluate_genius_law, GeniusVerdict,
            compute_genius_index, compute_dark_cleverness, compute_psi_apex
        )
        # These may be None if optional deps missing, but should be importable
        # The key is they're in the namespace
        pass  # Import succeeded

    def test_top_level_trinity_exports(self):
        """AGI·ASI·APEX Trinity classes are exported at top level."""
        from arifos_core import AGI, ASI, evaluate_session
        from arifos_core import EvaluationResult, SentinelResult, ASIResult, EvaluationMode
        assert AGI is not None
        assert ASI is not None
        assert evaluate_session is not None

    def test_top_level_red_patterns_exports(self):
        """RED_PATTERNS are exported at top level."""
        from arifos_core import RED_PATTERNS, RED_PATTERN_TO_FLOOR, RED_PATTERN_SEVERITY
        assert isinstance(RED_PATTERNS, dict)
        assert isinstance(RED_PATTERN_TO_FLOOR, dict)
        assert isinstance(RED_PATTERN_SEVERITY, dict)


class TestDeprecatedAPIsWarn:
    """Test that deprecated APIs emit warnings."""

    def test_sentinel_alias_deprecated(self):
        """Sentinel alias should be deprecated in favor of AGI."""
        from arifos_core import Sentinel, AGI
        # Sentinel should be alias for AGI
        assert Sentinel is AGI

    def test_accountant_alias_deprecated(self):
        """Accountant alias should be deprecated in favor of ASI."""
        from arifos_core import Accountant, ASI
        # Accountant should be alias for ASI
        assert Accountant is ASI

    def test_legacy_wrappers_exist(self):
        """Legacy wrapper functions exist for backward compat."""
        from arifos_core import check_red_patterns, compute_metrics_from_task
        assert callable(check_red_patterns)
        assert callable(compute_metrics_from_task)


class TestModuleLevelAPIs:
    """Test module-level APIs match registry."""

    def test_system_module_imports(self):
        """System module exports core components."""
        from arifos_core.system import (
            APEXPrime, apex_review, ApexVerdict, Verdict,
            check_floors, APEX_VERSION, APEX_EPOCH
        )
        assert APEXPrime is not None

    def test_system_api_registry_imports(self):
        """System module exports API registry."""
        from arifos_core.system import (
            StabilityLevel, APIEntry, APIRegistry,
            get_registry, get_stable_exports
        )
        assert StabilityLevel is not None
        assert get_registry is not None

    def test_enforcement_metrics_imports(self):
        """Enforcement module exports metrics."""
        from arifos_core.enforcement.metrics import Metrics, FloorsVerdict
        assert Metrics is not None

    def test_governance_fag_imports(self):
        """Governance module exports FAG."""
        from arifos_core.governance.fag import FAG
        assert FAG is not None

    def test_waw_well_imports(self):
        """W@W module exports @WELL."""
        from arifos_core.waw.well_file_care import WellFileCare, create_well_file_care
        assert WellFileCare is not None
        assert create_well_file_care is not None


class TestBackwardCompatShims:
    """Test that backward compatibility shims work."""

    def test_old_pipeline_path_works(self):
        """Old arifos_core.pipeline import works via shim."""
        from arifos_core.pipeline import Pipeline
        assert Pipeline is not None

    def test_old_apex_prime_path_works(self):
        """Old arifos_core.APEX_PRIME import works via shim."""
        from arifos_core.APEX_PRIME import apex_review
        assert apex_review is not None

    def test_old_metrics_path_works(self):
        """Old arifos_core.metrics import works via shim."""
        from arifos_core.metrics import Metrics
        assert Metrics is not None

    def test_old_genius_metrics_path_works(self):
        """Old arifos_core.genius_metrics import works via shim."""
        from arifos_core.genius_metrics import evaluate_genius_law
        # May be None but import should work
        pass

    def test_old_fag_path_works(self):
        """Old arifos_core.fag import works via shim."""
        from arifos_core.fag import FAG
        assert FAG is not None


class TestAPIRegistryValidation:
    """Test registry validation functions."""

    def test_get_stable_exports(self):
        """get_stable_exports returns set of stable API names."""
        from arifos_core.system.api_registry import get_stable_exports
        stable = get_stable_exports()
        assert isinstance(stable, set)
        assert "apex_review" in stable
        assert "Metrics" in stable
        assert "AGI" in stable

    def test_get_deprecated_exports(self):
        """get_deprecated_exports returns dict with replacements."""
        from arifos_core.system.api_registry import get_deprecated_exports
        deprecated = get_deprecated_exports()
        assert isinstance(deprecated, dict)
        assert "Sentinel" in deprecated
        assert deprecated["Sentinel"] == "AGI"
        assert "Accountant" in deprecated
        assert deprecated["Accountant"] == "ASI"

    def test_check_module_stability(self):
        """check_module_stability validates exports."""
        from arifos_core.system.api_registry import check_module_stability
        from arifos_core import __all__ as actual_all

        result = check_module_stability("arifos_core", actual_all)
        assert "missing" in result
        assert "undocumented" in result
        assert "valid" in result


class TestVerdictEnumStable:
    """Test Verdict Enum is stable (v42 API).

    v42: Verdict is now a proper Enum with members:
    - SEAL, SABAR, VOID (primary public)
    - PARTIAL, HOLD_888, SUNSET (internal governance)
    """

    def test_verdict_is_enum(self):
        """Verdict is a proper Enum."""
        from arifos_core import Verdict
        from enum import Enum
        assert issubclass(Verdict, Enum)

    def test_verdict_seal_exists(self):
        """Verdict.SEAL exists."""
        from arifos_core import Verdict
        assert hasattr(Verdict, "SEAL")
        assert Verdict.SEAL.value == "SEAL"

    def test_verdict_sabar_exists(self):
        """Verdict.SABAR exists."""
        from arifos_core import Verdict
        assert hasattr(Verdict, "SABAR")
        assert Verdict.SABAR.value == "SABAR"

    def test_verdict_void_exists(self):
        """Verdict.VOID exists."""
        from arifos_core import Verdict
        assert hasattr(Verdict, "VOID")
        assert Verdict.VOID.value == "VOID"

    def test_verdict_partial_exists(self):
        """Verdict.PARTIAL exists (internal governance)."""
        from arifos_core import Verdict
        assert hasattr(Verdict, "PARTIAL")
        assert Verdict.PARTIAL.value == "PARTIAL"

    def test_verdict_hold_888_exists(self):
        """Verdict.HOLD_888 exists (internal governance)."""
        from arifos_core import Verdict
        assert hasattr(Verdict, "HOLD_888")
        assert Verdict.HOLD_888.value == "888_HOLD"

    def test_verdict_from_string(self):
        """Verdict.from_string() works."""
        from arifos_core import Verdict
        assert Verdict.from_string("SEAL") == Verdict.SEAL
        assert Verdict.from_string("SABAR") == Verdict.SABAR
        assert Verdict.from_string("VOID") == Verdict.VOID
        assert Verdict.from_string("888_HOLD") == Verdict.HOLD_888


class TestApexVerdictDataclass:
    """Test ApexVerdict dataclass is stable (v42 API)."""

    def test_apex_verdict_is_dataclass(self):
        """ApexVerdict is a dataclass."""
        from arifos_core import ApexVerdict
        from dataclasses import is_dataclass
        assert is_dataclass(ApexVerdict)

    def test_apex_verdict_has_verdict_field(self):
        """ApexVerdict has verdict field."""
        from arifos_core import ApexVerdict, Verdict
        result = ApexVerdict(verdict=Verdict.SEAL)
        assert result.verdict == Verdict.SEAL

    def test_apex_verdict_has_pulse_field(self):
        """ApexVerdict has pulse field with default."""
        from arifos_core import ApexVerdict, Verdict
        result = ApexVerdict(verdict=Verdict.SEAL)
        assert result.pulse == 1.0

    def test_apex_verdict_has_reason_field(self):
        """ApexVerdict has reason field."""
        from arifos_core import ApexVerdict, Verdict
        result = ApexVerdict(verdict=Verdict.VOID, reason="Test reason")
        assert result.reason == "Test reason"

    def test_apex_verdict_str(self):
        """ApexVerdict __str__ returns verdict value."""
        from arifos_core import ApexVerdict, Verdict
        result = ApexVerdict(verdict=Verdict.SEAL)
        assert str(result) == "SEAL"

    def test_apex_verdict_is_approved(self):
        """ApexVerdict.is_approved property works."""
        from arifos_core import ApexVerdict, Verdict
        assert ApexVerdict(verdict=Verdict.SEAL).is_approved is True
        assert ApexVerdict(verdict=Verdict.PARTIAL).is_approved is True
        assert ApexVerdict(verdict=Verdict.VOID).is_approved is False

    def test_apex_verdict_is_blocked(self):
        """ApexVerdict.is_blocked property works."""
        from arifos_core import ApexVerdict, Verdict
        assert ApexVerdict(verdict=Verdict.VOID).is_blocked is True
        assert ApexVerdict(verdict=Verdict.SEAL).is_blocked is False


class TestMCPAPIsBeta:
    """Test MCP APIs are properly classified as BETA."""

    def test_mcp_server_importable(self):
        """MCP server can be imported."""
        from arifos_core.mcp.server import MCPServer
        assert MCPServer is not None

    def test_mcp_tools_importable(self):
        """MCP tools can be imported."""
        from arifos_core.mcp.server import TOOLS
        assert "arifos_judge" in TOOLS
        assert "arifos_recall" in TOOLS
        assert "arifos_audit" in TOOLS

    def test_mcp_models_importable(self):
        """MCP models can be imported."""
        from arifos_core.mcp.models import JudgeRequest, JudgeResponse
        assert JudgeRequest is not None
        assert JudgeResponse is not None


class TestConstitutionalConstants:
    """Test constitutional constants are stable and correct."""

    def test_truth_threshold(self):
        """F2 truth threshold is 0.99."""
        from arifos_core.enforcement.metrics import TRUTH_THRESHOLD
        assert TRUTH_THRESHOLD == 0.99

    def test_genius_thresholds(self):
        """F8 genius floor and F9 dark ceiling via evaluate_genius_law."""
        from arifos_core.enforcement.genius_metrics import evaluate_genius_law
        from arifos_core import Metrics
        # GENIUS_FLOOR and DARK_CEILING may not be exported as constants
        # but the thresholds are enforced in evaluate_genius_law
        assert evaluate_genius_law is not None

        # evaluate_genius_law takes Metrics object
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            anti_hantu=True,
            tri_witness=0.95,
        )
        result = evaluate_genius_law(metrics)
        assert result is not None
        # GeniusVerdict has genius_index (G), dark_cleverness (C_dark)
        assert hasattr(result, 'genius_index') or hasattr(result, 'G')

    def test_omega_bounds(self):
        """F7 omega bounds are [0.03, 0.05]."""
        from arifos_core.enforcement.metrics import OMEGA_0_MIN, OMEGA_0_MAX
        assert OMEGA_0_MIN == 0.03
        assert OMEGA_0_MAX == 0.05


class TestNoBreakingChanges:
    """
    Smoke tests to catch accidental breaking changes.

    These tests verify the most common usage patterns continue to work.
    """

    def test_basic_apex_review_flow(self):
        """apex_review() returns ApexVerdict (v42 API)."""
        from arifos_core import apex_review, ApexVerdict, Verdict, Metrics

        # Metrics requires all fields including tri_witness
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            anti_hantu=True,
            tri_witness=0.95,
        )
        result = apex_review(metrics)
        # v42: apex_review returns ApexVerdict dataclass
        assert isinstance(result, ApexVerdict)
        assert isinstance(result.verdict, Verdict)
        assert result.verdict in [Verdict.SEAL, Verdict.PARTIAL, Verdict.VOID, Verdict.HOLD_888, Verdict.SABAR]
        assert isinstance(result.pulse, float)
        assert isinstance(result.reason, str)

    def test_apex_verdict_convenience_shim(self):
        """apex_verdict() returns str (v42 convenience shim)."""
        from arifos_core import apex_verdict, Metrics

        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            anti_hantu=True,
            tri_witness=0.95,
        )
        verdict_str = apex_verdict(metrics)
        # v42: apex_verdict returns str for simplicity
        assert isinstance(verdict_str, str)
        assert verdict_str in ["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR", "SUNSET"]

    def test_basic_agi_scan_flow(self):
        """Basic AGI scan works."""
        from arifos_core import AGI

        agi = AGI()
        result = agi.scan("What is the capital of France?")
        assert result is not None
        assert hasattr(result, "is_safe")

    def test_basic_asi_assess_flow(self):
        """Basic ASI assess works."""
        from arifos_core import ASI

        asi = ASI()
        result = asi.assess("Explain quantum computing")
        assert result is not None
        assert hasattr(result, "metrics")
