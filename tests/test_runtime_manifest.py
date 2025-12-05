"""
test_runtime_manifest.py — Tests for arifOS Runtime Manifest

These tests verify:
1. Manifest file parses cleanly
2. Floor thresholds match metrics.py constants
3. Pipeline stages include 000 and 999
4. Referenced modules exist and can be imported
5. Harness entry point is callable

Tests are READ-ONLY: they detect drift but do not auto-fix.
"""

import importlib
import pytest
from pathlib import Path

from arifos_core.runtime_manifest import (
    load_runtime_manifest,
    validate_manifest,
    get_floor_threshold,
    get_pipeline_stages,
    get_eye_views,
    get_waw_organs,
    get_harness_entry,
    import_module_from_manifest,
    get_class_from_manifest,
    DEFAULT_MANIFEST_PATH,
    DEFAULT_MANIFEST_PATH_YAML,
    DEFAULT_MANIFEST_PATH_JSON,
    HAS_YAML,
)

# Import metrics constants for comparison
from arifos_core.metrics import (
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    TRI_WITNESS_THRESHOLD,
    PSI_THRESHOLD,
)


# =============================================================================
# MANIFEST LOADING TESTS
# =============================================================================


class TestManifestLoading:
    """Tests for manifest file loading."""

    def test_manifest_file_exists(self):
        """Manifest file should exist at expected path."""
        assert DEFAULT_MANIFEST_PATH.exists(), f"Manifest not found: {DEFAULT_MANIFEST_PATH}"

    def test_manifest_loads_without_error(self):
        """Manifest should load and parse as valid YAML."""
        manifest = load_runtime_manifest()
        assert manifest is not None
        assert isinstance(manifest, dict)

    def test_manifest_has_version(self):
        """Manifest should have version field."""
        manifest = load_runtime_manifest()
        assert "version" in manifest
        assert "Omega" in manifest["version"]

    def test_manifest_has_epoch(self):
        """Manifest should have epoch field."""
        manifest = load_runtime_manifest()
        assert "epoch" in manifest
        assert manifest["epoch"] == 35

    def test_manifest_has_status(self):
        """Manifest should have status field."""
        manifest = load_runtime_manifest()
        assert "status" in manifest
        assert manifest["status"] == "SEALED"

    def test_validate_manifest_passes(self):
        """Validation should pass for the canonical manifest."""
        manifest = load_runtime_manifest(validate=False)
        # Should not raise
        validate_manifest(manifest)


# =============================================================================
# FLOOR THRESHOLD DRIFT TESTS
# =============================================================================


class TestFloorThresholdDrift:
    """Tests that manifest thresholds match metrics.py constants."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_truth_threshold_matches(self, manifest):
        """Manifest truth threshold should match TRUTH_THRESHOLD constant."""
        manifest_value = manifest["floors"]["truth"]["threshold"]
        assert manifest_value == TRUTH_THRESHOLD, (
            f"DRIFT DETECTED: manifest truth={manifest_value}, "
            f"metrics.py TRUTH_THRESHOLD={TRUTH_THRESHOLD}"
        )

    def test_delta_s_threshold_matches(self, manifest):
        """Manifest delta_s threshold should match DELTA_S_THRESHOLD constant."""
        manifest_value = manifest["floors"]["delta_s"]["threshold"]
        assert manifest_value == DELTA_S_THRESHOLD, (
            f"DRIFT DETECTED: manifest delta_s={manifest_value}, "
            f"metrics.py DELTA_S_THRESHOLD={DELTA_S_THRESHOLD}"
        )

    def test_peace_squared_threshold_matches(self, manifest):
        """Manifest peace_squared threshold should match PEACE_SQUARED_THRESHOLD constant."""
        manifest_value = manifest["floors"]["peace_squared"]["threshold"]
        assert manifest_value == PEACE_SQUARED_THRESHOLD, (
            f"DRIFT DETECTED: manifest peace_squared={manifest_value}, "
            f"metrics.py PEACE_SQUARED_THRESHOLD={PEACE_SQUARED_THRESHOLD}"
        )

    def test_kappa_r_threshold_matches(self, manifest):
        """Manifest kappa_r threshold should match KAPPA_R_THRESHOLD constant."""
        manifest_value = manifest["floors"]["kappa_r"]["threshold"]
        assert manifest_value == KAPPA_R_THRESHOLD, (
            f"DRIFT DETECTED: manifest kappa_r={manifest_value}, "
            f"metrics.py KAPPA_R_THRESHOLD={KAPPA_R_THRESHOLD}"
        )

    def test_omega_0_min_matches(self, manifest):
        """Manifest omega_0 min threshold should match OMEGA_0_MIN constant."""
        manifest_value = manifest["floors"]["omega_0"]["threshold_min"]
        assert manifest_value == OMEGA_0_MIN, (
            f"DRIFT DETECTED: manifest omega_0_min={manifest_value}, "
            f"metrics.py OMEGA_0_MIN={OMEGA_0_MIN}"
        )

    def test_omega_0_max_matches(self, manifest):
        """Manifest omega_0 max threshold should match OMEGA_0_MAX constant."""
        manifest_value = manifest["floors"]["omega_0"]["threshold_max"]
        assert manifest_value == OMEGA_0_MAX, (
            f"DRIFT DETECTED: manifest omega_0_max={manifest_value}, "
            f"metrics.py OMEGA_0_MAX={OMEGA_0_MAX}"
        )

    def test_tri_witness_threshold_matches(self, manifest):
        """Manifest tri_witness threshold should match TRI_WITNESS_THRESHOLD constant."""
        manifest_value = manifest["floors"]["tri_witness"]["threshold"]
        assert manifest_value == TRI_WITNESS_THRESHOLD, (
            f"DRIFT DETECTED: manifest tri_witness={manifest_value}, "
            f"metrics.py TRI_WITNESS_THRESHOLD={TRI_WITNESS_THRESHOLD}"
        )

    def test_psi_threshold_matches(self, manifest):
        """Manifest psi threshold should match PSI_THRESHOLD constant."""
        manifest_value = manifest["vitality"]["threshold"]
        assert manifest_value == PSI_THRESHOLD, (
            f"DRIFT DETECTED: manifest psi={manifest_value}, "
            f"metrics.py PSI_THRESHOLD={PSI_THRESHOLD}"
        )

    def test_metrics_threshold_constants_match(self, manifest):
        """Manifest metrics.threshold_constants should match metrics.py."""
        constants = manifest["metrics"]["threshold_constants"]
        assert constants["TRUTH_THRESHOLD"] == TRUTH_THRESHOLD
        assert constants["DELTA_S_THRESHOLD"] == DELTA_S_THRESHOLD
        assert constants["PEACE_SQUARED_THRESHOLD"] == PEACE_SQUARED_THRESHOLD
        assert constants["KAPPA_R_THRESHOLD"] == KAPPA_R_THRESHOLD
        assert constants["OMEGA_0_MIN"] == OMEGA_0_MIN
        assert constants["OMEGA_0_MAX"] == OMEGA_0_MAX
        assert constants["TRI_WITNESS_THRESHOLD"] == TRI_WITNESS_THRESHOLD
        assert constants["PSI_THRESHOLD"] == PSI_THRESHOLD


# =============================================================================
# PIPELINE STAGE TESTS
# =============================================================================


class TestPipelineStages:
    """Tests for pipeline stage definitions."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_stage_000_exists(self, manifest):
        """Pipeline should include stage 000 (VOID)."""
        stages = manifest["pipeline"]["stages"]
        assert "000" in stages

    def test_stage_999_exists(self, manifest):
        """Pipeline should include stage 999 (SEAL)."""
        stages = manifest["pipeline"]["stages"]
        assert "999" in stages

    def test_all_ten_stages_defined(self, manifest):
        """Pipeline should define all 10 stages (000-999)."""
        stages = manifest["pipeline"]["stages"]
        expected_stages = {"000", "111", "222", "333", "444", "555", "666", "777", "888", "999"}
        actual_stages = set(stages.keys())
        assert actual_stages == expected_stages, f"Missing stages: {expected_stages - actual_stages}"

    def test_stage_000_is_void(self, manifest):
        """Stage 000 should be named VOID."""
        assert manifest["pipeline"]["stages"]["000"]["name"] == "VOID"

    def test_stage_888_is_judge(self, manifest):
        """Stage 888 should be named JUDGE."""
        assert manifest["pipeline"]["stages"]["888"]["name"] == "JUDGE"

    def test_stage_999_is_seal(self, manifest):
        """Stage 999 should be named SEAL."""
        assert manifest["pipeline"]["stages"]["999"]["name"] == "SEAL"

    def test_get_pipeline_stages_returns_ordered_list(self, manifest):
        """get_pipeline_stages should return ordered stage codes."""
        stages = get_pipeline_stages(manifest)
        assert stages == ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]

    def test_class_a_routing_defined(self, manifest):
        """Class A (fast track) routing should be defined."""
        routing = manifest["pipeline"]["routing"]
        assert "class_a" in routing
        assert routing["class_a"]["track"] == "fast"

    def test_class_b_routing_defined(self, manifest):
        """Class B (deep track) routing should be defined."""
        routing = manifest["pipeline"]["routing"]
        assert "class_b" in routing
        assert routing["class_b"]["track"] == "deep"


# =============================================================================
# ENGINE MODULE TESTS
# =============================================================================


class TestEngineModules:
    """Tests that engine modules can be imported."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_arif_engine_module_exists(self, manifest):
        """ARIF engine module should be importable."""
        module_path = manifest["engines"]["arif"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None

    def test_arif_engine_class_exists(self, manifest):
        """ARIFEngine class should exist in module."""
        ARIFEngine = get_class_from_manifest(manifest, "engines", "arif")
        assert ARIFEngine is not None
        assert ARIFEngine.__name__ == "ARIFEngine"

    def test_adam_engine_module_exists(self, manifest):
        """ADAM engine module should be importable."""
        module_path = manifest["engines"]["adam"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None

    def test_adam_engine_class_exists(self, manifest):
        """ADAMEngine class should exist in module."""
        ADAMEngine = get_class_from_manifest(manifest, "engines", "adam")
        assert ADAMEngine is not None
        assert ADAMEngine.__name__ == "ADAMEngine"

    def test_apex_engine_module_exists(self, manifest):
        """APEX engine module should be importable."""
        module_path = manifest["engines"]["apex"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None

    def test_apex_engine_class_exists(self, manifest):
        """ApexEngine class should exist in module."""
        ApexEngine = get_class_from_manifest(manifest, "engines", "apex")
        assert ApexEngine is not None
        assert ApexEngine.__name__ == "ApexEngine"


# =============================================================================
# W@W ORGAN MODULE TESTS
# =============================================================================


class TestWAWOrganModules:
    """Tests that W@W organ modules can be imported."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_all_five_organs_defined(self, manifest):
        """All 5 W@W organs should be defined."""
        organs = get_waw_organs(manifest)
        expected_organs = {"well", "rif", "wealth", "geox", "prompt"}
        actual_organs = set(organs.keys())
        assert actual_organs == expected_organs

    def test_well_organ_importable(self, manifest):
        """@WELL organ module should be importable."""
        WellOrgan = get_class_from_manifest(manifest, "waw", "well")
        assert WellOrgan is not None
        assert WellOrgan.__name__ == "WellOrgan"

    def test_rif_organ_importable(self, manifest):
        """@RIF organ module should be importable."""
        RifOrgan = get_class_from_manifest(manifest, "waw", "rif")
        assert RifOrgan is not None
        assert RifOrgan.__name__ == "RifOrgan"

    def test_wealth_organ_importable(self, manifest):
        """@WEALTH organ module should be importable."""
        WealthOrgan = get_class_from_manifest(manifest, "waw", "wealth")
        assert WealthOrgan is not None
        assert WealthOrgan.__name__ == "WealthOrgan"

    def test_geox_organ_importable(self, manifest):
        """@GEOX organ module should be importable."""
        GeoxOrgan = get_class_from_manifest(manifest, "waw", "geox")
        assert GeoxOrgan is not None
        assert GeoxOrgan.__name__ == "GeoxOrgan"

    def test_prompt_organ_importable(self, manifest):
        """@PROMPT organ module should be importable."""
        PromptOrgan = get_class_from_manifest(manifest, "waw", "prompt")
        assert PromptOrgan is not None
        assert PromptOrgan.__name__ == "PromptOrgan"

    def test_federation_core_importable(self, manifest):
        """WAWFederationCore should be importable."""
        WAWFederationCore = get_class_from_manifest(manifest, "waw")
        assert WAWFederationCore is not None
        assert WAWFederationCore.__name__ == "WAWFederationCore"


# =============================================================================
# @EYE SENTINEL VIEW TESTS
# =============================================================================


class TestEyeSentinelViews:
    """Tests that @EYE Sentinel views can be imported."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_eleven_views_defined(self, manifest):
        """All 10+1 @EYE views should be defined."""
        views = get_eye_views(manifest)
        assert len(views) == 11

    def test_eye_sentinel_coordinator_importable(self, manifest):
        """EyeSentinel coordinator should be importable."""
        EyeSentinel = get_class_from_manifest(manifest, "eye_sentinel")
        assert EyeSentinel is not None
        assert EyeSentinel.__name__ == "EyeSentinel"

    def test_all_views_importable(self, manifest):
        """All @EYE views should be importable."""
        views = get_eye_views(manifest)
        for view in views:
            module = importlib.import_module(view["module"])
            cls = getattr(module, view["class"])
            assert cls is not None, f"View {view['name']} class not found"

    def test_blocking_rule_defined(self, manifest):
        """Blocking rule should be defined."""
        rule = manifest["eye_sentinel"]["blocking_rule"]
        assert "BLOCK" in rule
        assert "SABAR" in rule


# =============================================================================
# METRICS MODULE TESTS
# =============================================================================


class TestMetricsModule:
    """Tests for metrics module references."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_metrics_module_importable(self, manifest):
        """Metrics module should be importable."""
        module = import_module_from_manifest(manifest, "metrics")
        assert module is not None

    def test_metrics_dataclass_exists(self, manifest):
        """Metrics dataclass should exist."""
        Metrics = get_class_from_manifest(manifest, "metrics")
        assert Metrics is not None
        assert Metrics.__name__ == "Metrics"

    def test_check_functions_exist(self, manifest):
        """All check functions should exist in metrics module."""
        module = import_module_from_manifest(manifest, "metrics")
        check_functions = manifest["metrics"]["check_functions"]
        for func_name in check_functions:
            assert hasattr(module, func_name), f"Check function {func_name} not found"
            func = getattr(module, func_name)
            assert callable(func), f"{func_name} is not callable"


# =============================================================================
# HARNESS ENTRY POINT TESTS
# =============================================================================


class TestHarnessEntryPoint:
    """Tests for caged harness entry point."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_harness_module_importable(self, manifest):
        """Harness module should be importable."""
        module = import_module_from_manifest(manifest, "harness")
        assert module is not None

    def test_cage_llm_response_callable(self, manifest):
        """cage_llm_response entry function should be callable."""
        module = import_module_from_manifest(manifest, "harness")
        entry_func = manifest["harness"]["entry_function"]
        func = getattr(module, entry_func)
        assert callable(func)

    def test_caged_result_class_exists(self, manifest):
        """CagedResult class should exist."""
        module = import_module_from_manifest(manifest, "harness")
        result_class = manifest["harness"]["result_class"]
        cls = getattr(module, result_class)
        assert cls is not None

    def test_get_harness_entry_returns_correct_info(self, manifest):
        """get_harness_entry should return correct module and function."""
        entry = get_harness_entry(manifest)
        assert entry["module"] == "scripts.arifos_caged_llm_demo"
        assert entry["entry_function"] == "cage_llm_response"
        assert entry["result_class"] == "CagedResult"


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestHelperFunctions:
    """Tests for manifest helper functions."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_get_floor_threshold_truth(self, manifest):
        """get_floor_threshold should return correct truth threshold."""
        threshold = get_floor_threshold(manifest, "truth")
        assert threshold == 0.99

    def test_get_floor_threshold_omega_returns_range(self, manifest):
        """get_floor_threshold should return range for omega_0."""
        threshold = get_floor_threshold(manifest, "omega_0")
        assert threshold == {"min": 0.03, "max": 0.05}

    def test_get_floor_threshold_invalid_raises(self, manifest):
        """get_floor_threshold should raise KeyError for invalid floor."""
        with pytest.raises(KeyError):
            get_floor_threshold(manifest, "invalid_floor")


# =============================================================================
# LEDGER MODULE TESTS
# =============================================================================


class TestLedgerModules:
    """Tests for ledger/vault/phoenix module references."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_cooling_ledger_module_importable(self, manifest):
        """Cooling ledger module should be importable."""
        module_path = manifest["ledger"]["cooling_ledger"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None

    def test_vault999_seal_json_path_valid(self, manifest):
        """Vault999 seal JSON path should exist."""
        seal_path = manifest["ledger"]["vault999"]["seal_json"]
        full_path = Path(__file__).parent.parent / seal_path
        assert full_path.exists(), f"Vault999 seal not found: {full_path}"

    def test_phoenix72_module_importable(self, manifest):
        """Phoenix72 module should be importable."""
        module_path = manifest["ledger"]["phoenix72"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None


# =============================================================================
# CANON FILE REFERENCE TESTS
# =============================================================================


class TestCanonFileReferences:
    """Tests that referenced canon files exist."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest()

    def test_runtime_law_files_exist(self, manifest):
        """All referenced runtime law canon files should exist."""
        canon_files = manifest["canon_files"]["runtime_law"]
        root = Path(__file__).parent.parent
        for file_path in canon_files:
            full_path = root / file_path
            assert full_path.exists(), f"Canon file not found: {file_path}"

    def test_constitutional_floors_json_exists(self, manifest):
        """constitutional_floors.json should exist."""
        machine_readable = manifest["canon_files"]["machine_readable"]
        root = Path(__file__).parent.parent
        for file_path in machine_readable:
            if file_path.endswith(".json"):
                full_path = root / file_path
                assert full_path.exists(), f"Machine-readable file not found: {file_path}"
