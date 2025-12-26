"""
test_runtime_manifest.py — Tests for arifOS Runtime Manifest

These tests verify:
1. Manifest file parses cleanly
2. Floor thresholds match metrics.py constants
3. Pipeline stages include 000 and 999
4. Referenced modules exist and can be imported
5. Harness entry point is callable

NOTE: As of v37, the default epoch is now v37 (unified LAW+SPEC+CODE).
      Tests for v35-specific manifest structure explicitly load epoch="v35".
      The v37 default epoch tests are in TestV37DefaultEpoch.

Tests are READ-ONLY: they detect drift but do not auto-fix.
"""

import importlib
import pytest
from pathlib import Path

from arifos_core.system.runtime_manifest import (
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
from arifos_core.enforcement.metrics import (
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    TRI_WITNESS_THRESHOLD,
    PSI_THRESHOLD,
)

LEGACY_CANON_PATH_MAP = {
    "canon/000_ARIFOS_CANON_v35Omega.md": "archive/v35_0_0/canon/0_ARIFOS_CANON_v35Omega.md",
    "canon/001_APEX_META_CONSTITUTION_v35Omega.md": "archive/v35_0_0/canon/1_APEX_META_CONSTITUTION_v35Omega.md",
    "canon/002_APEX_TRINITY_v35Omega.md": "archive/v35_0_0/canon/2_APEX_TRINITY_v35Omega.md",
    "canon/010_DeltaOmegaPsi_UNIFIED_FIELD_v35Omega.md": "archive/v35_0_0/canon/0_DeltaOmegaPsi_UNIFIED_FIELD_v35Omega.md",
    "canon/020_ANTI_HANTU_v35Omega.md": "archive/v35_0_0/canon/0_ANTI_HANTU_v35Omega.md",
    "canon/021_ANTI_HANTU_SUPPLEMENT_v35Omega.md": "archive/v35_0_0/canon/1_ANTI_HANTU_SUPPLEMENT_v35Omega.md",
    "canon/030_EYE_SENTINEL_v35Omega.md": "archive/v35_0_0/canon/0_EYE_SENTINEL_v35Omega.md",
    "canon/100_AAA_ENGINES_SPEC_v35Omega.md": "archive/v35_0_0/canon/0_AAA_ENGINES_SPEC_v35Omega.md",
    "canon/880_000-999_METABOLIC_CANON_v35Omega.md": "archive/v35_0_0/canon/0_000-999_METABOLIC_CANON_v35Omega.md",
    "canon/888_APEX_PRIME_CANON_v35Omega.md": "archive/v35_0_0/canon/8_APEX_PRIME_CANON_v35Omega.md",
    "canon/99__README_Vault999_v35Omega.md": "archive/v35_0_0/canon/__README_Vault999_v35Omega.md",
    "canon/99_Vault999_Seal_v35Omega.json": "archive/v35_0_0/canon/_Vault999_Seal_v35Omega.json",
}


def resolve_legacy_canon_path(repo_root: Path, canon_path: str) -> Path:
    """Resolve v35 canon paths to archive locations when migrated."""
    full_path = repo_root / canon_path
    if full_path.exists():
        return full_path
    mapped = LEGACY_CANON_PATH_MAP.get(canon_path)
    if mapped:
        return repo_root / mapped
    return full_path


# =============================================================================
# V35 LEGACY MANIFEST TESTS
# =============================================================================
# These tests are specific to v35Omega manifest structure.
# They explicitly load epoch="v35" to test legacy compatibility.
# =============================================================================


# =============================================================================
# MANIFEST LOADING TESTS (v35 Legacy)
# =============================================================================


class TestManifestLoadingV35:
    """Tests for v35 legacy manifest file loading."""

    def test_v35_manifest_file_exists(self):
        """v35 Manifest file should exist at expected path."""
        assert DEFAULT_MANIFEST_PATH.exists(), f"v35 Manifest not found: {DEFAULT_MANIFEST_PATH}"

    def test_v35_manifest_loads_without_error(self):
        """v35 Manifest should load and parse as valid YAML."""
        manifest = load_runtime_manifest(epoch="v35")
        assert manifest is not None
        assert isinstance(manifest, dict)

    def test_v35_manifest_has_version(self):
        """v35 Manifest should have version field with Omega."""
        manifest = load_runtime_manifest(epoch="v35")
        assert "version" in manifest
        assert "Omega" in manifest["version"]

    def test_v35_manifest_has_epoch(self):
        """v35 Manifest should have epoch field == 35."""
        manifest = load_runtime_manifest(epoch="v35")
        assert "epoch" in manifest
        assert manifest["epoch"] == 35

    def test_v35_manifest_has_status(self):
        """v35 Manifest should have status field == SEALED."""
        manifest = load_runtime_manifest(epoch="v35")
        assert "status" in manifest
        assert manifest["status"] == "SEALED"

    def test_v35_validate_manifest_passes(self):
        """Validation should pass for the canonical v35 manifest."""
        manifest = load_runtime_manifest(epoch="v35", validate=False)
        # Should not raise
        validate_manifest(manifest, epoch="v35")


# =============================================================================
# FLOOR THRESHOLD DRIFT TESTS (v35 Legacy)
# =============================================================================


class TestFloorThresholdDriftV35:
    """Tests that v35 manifest thresholds match metrics.py constants."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

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
# PIPELINE STAGE TESTS (v35 Legacy)
# =============================================================================


class TestPipelineStagesV35:
    """Tests for v35 pipeline stage definitions."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

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
# ENGINE MODULE TESTS (v35 Legacy)
# =============================================================================


class TestEngineModulesV35:
    """Tests that v35 engine modules can be imported."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

    def test_arif_engine_module_exists(self, manifest):
        """ARIF engine module should be importable."""
        module_path = manifest["engines"]["agi"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None

    def test_arif_engine_class_exists(self, manifest):
        """AGIEngine class should exist in module."""
        AGIEngine = get_class_from_manifest(manifest, "engines", "agi")
        assert AGIEngine is not None
        assert AGIEngine.__name__ == "AGIEngine"

    def test_adam_engine_module_exists(self, manifest):
        """ADAM engine module should be importable."""
        module_path = manifest["engines"]["asi"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None

    def test_adam_engine_class_exists(self, manifest):
        """ASIEngine class should exist in module."""
        ASIEngine = get_class_from_manifest(manifest, "engines", "asi")
        assert ASIEngine is not None
        assert ASIEngine.__name__ == "ASIEngine"

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
# W@W ORGAN MODULE TESTS (v35 Legacy)
# =============================================================================


class TestWAWOrganModulesV35:
    """Tests that v35 W@W organ modules can be imported."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

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
# @EYE SENTINEL VIEW TESTS (v35 Legacy)
# =============================================================================


class TestEyeSentinelViewsV35:
    """Tests that v35 @EYE Sentinel views can be imported."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

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
# METRICS MODULE TESTS (v35 Legacy)
# =============================================================================


class TestMetricsModuleV35:
    """Tests for v35 metrics module references."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

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
# HARNESS ENTRY POINT TESTS (v35 Legacy)
# =============================================================================


class TestHarnessEntryPointV35:
    """Tests for v35 caged harness entry point."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

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
# HELPER FUNCTION TESTS (v35 Legacy)
# =============================================================================


class TestHelperFunctionsV35:
    """Tests for v35 manifest helper functions."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

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
# LEDGER MODULE TESTS (v35 Legacy)
# =============================================================================


class TestLedgerModulesV35:
    """Tests for v35 ledger/vault/phoenix module references."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

    def test_cooling_ledger_module_importable(self, manifest):
        """Cooling ledger module should be importable."""
        module_path = manifest["ledger"]["cooling_ledger"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None

    def test_vault999_seal_json_path_valid(self, manifest):
        """Vault999 seal JSON path should exist."""
        seal_path = manifest["ledger"]["vault999"]["seal_json"]
        full_path = resolve_legacy_canon_path(Path(__file__).parent.parent, seal_path)
        assert full_path.exists(), f"Vault999 seal not found: {full_path}"

    def test_phoenix72_module_importable(self, manifest):
        """Phoenix72 module should be importable."""
        module_path = manifest["ledger"]["phoenix72"]["module"]
        module = importlib.import_module(module_path)
        assert module is not None


# =============================================================================
# CANON FILE REFERENCE TESTS (v35 Legacy)
# =============================================================================


class TestCanonFileReferencesV35:
    """Tests that v35 referenced canon files exist."""

    @pytest.fixture
    def manifest(self):
        return load_runtime_manifest(epoch="v35")

    def test_runtime_law_files_exist(self, manifest):
        """All referenced runtime law canon files should exist."""
        canon_files = manifest["canon_files"]["runtime_law"]
        root = Path(__file__).parent.parent
        for file_path in canon_files:
            full_path = resolve_legacy_canon_path(root, file_path)
            assert full_path.exists(), f"Canon file not found: {file_path}"

    def test_constitutional_floors_json_exists(self, manifest):
        """constitutional_floors.json should exist."""
        machine_readable = manifest["canon_files"]["machine_readable"]
        root = Path(__file__).parent.parent
        for file_path in machine_readable:
            if file_path.endswith(".json"):
                full_path = root / file_path
                assert full_path.exists(), f"Machine-readable file not found: {file_path}"


# =============================================================================
# V37 DEFAULT EPOCH TESTS
# =============================================================================


class TestV37DefaultEpoch:
    """Tests that v37 is the default epoch when ARIFOS_RUNTIME_EPOCH is unset."""

    def test_default_epoch_is_v37_when_env_unset(self):
        """
        When ARIFOS_RUNTIME_EPOCH is not set, the default epoch should be v37.

        This test verifies the v37 unified runtime is the mainline default.
        """
        import os
        from arifos_core.system.runtime_manifest import (
            get_active_epoch,
            is_v37_epoch,
            is_legacy_epoch,
            DEFAULT_EPOCH,
            EPOCH_ENV_VAR,
        )

        # Save original env value
        original_value = os.environ.get(EPOCH_ENV_VAR)

        try:
            # Clear the environment variable
            if EPOCH_ENV_VAR in os.environ:
                del os.environ[EPOCH_ENV_VAR]

            # Verify DEFAULT_EPOCH constant is v45
            assert DEFAULT_EPOCH == "v45", f"DEFAULT_EPOCH should be 'v45', got '{DEFAULT_EPOCH}'"

            # Verify get_active_epoch returns v45
            active_epoch = get_active_epoch()
            assert active_epoch == "v45", f"Active epoch should be 'v45' when env unset, got '{active_epoch}'"

            # Verify is_v37_epoch returns False (v45 is active)
            assert is_v37_epoch() is False, "is_v37_epoch() should be False when v45 active"

            # Verify is_legacy_epoch returns False (because v45 is not legacy)
            # v35, v36.3, v37, v44 ARE legacy.
            assert is_legacy_epoch() is False, "is_legacy_epoch() should be False for v45"

        finally:
            # Restore original env value
            if original_value is not None:
                os.environ[EPOCH_ENV_VAR] = original_value
            elif EPOCH_ENV_VAR in os.environ:
                del os.environ[EPOCH_ENV_VAR]

    def test_v35_selectable_via_env(self):
        """v35 should be selectable via ARIFOS_RUNTIME_EPOCH for legacy testing."""
        import os
        from arifos_core.system.runtime_manifest import (
            get_active_epoch,
            is_v37_epoch,
            is_legacy_epoch,
            EPOCH_ENV_VAR,
        )

        original_value = os.environ.get(EPOCH_ENV_VAR)

        try:
            os.environ[EPOCH_ENV_VAR] = "v35"

            assert get_active_epoch() == "v35"
            assert is_v37_epoch() is False
            assert is_legacy_epoch() is True

        finally:
            if original_value is not None:
                os.environ[EPOCH_ENV_VAR] = original_value
            elif EPOCH_ENV_VAR in os.environ:
                del os.environ[EPOCH_ENV_VAR]

    def test_v36_3_selectable_via_env(self):
        """v36.3 should be selectable via ARIFOS_RUNTIME_EPOCH for legacy testing."""
        import os
        from arifos_core.system.runtime_manifest import (
            get_active_epoch,
            is_v37_epoch,
            is_legacy_epoch,
            EPOCH_ENV_VAR,
        )

        original_value = os.environ.get(EPOCH_ENV_VAR)

        try:
            os.environ[EPOCH_ENV_VAR] = "v36.3"

            assert get_active_epoch() == "v36.3"
            assert is_v37_epoch() is False
            assert is_legacy_epoch() is True

        finally:
            if original_value is not None:
                os.environ[EPOCH_ENV_VAR] = original_value
            elif EPOCH_ENV_VAR in os.environ:
                del os.environ[EPOCH_ENV_VAR]

    def test_v37_manifest_loads_by_default(self):
        """When env unset, load_runtime_manifest should load v37 manifest."""
        import os
        from arifos_core.system.runtime_manifest import load_runtime_manifest, EPOCH_ENV_VAR

        original_value = os.environ.get(EPOCH_ENV_VAR)

        try:
            if EPOCH_ENV_VAR in os.environ:
                del os.environ[EPOCH_ENV_VAR]

            manifest = load_runtime_manifest()

            assert manifest["version"] == "35Omega", \
                "v45 epoch uses v35Omega JSON structure (descriptive base)"
            assert manifest["epoch"] == 35, \
                "v45 uses v35 epoch spec file (epoch 35)"
            
            assert manifest.get("_runtime_epoch") == "v45"

        finally:
            if original_value is not None:
                os.environ[EPOCH_ENV_VAR] = original_value
            elif EPOCH_ENV_VAR in os.environ:
                del os.environ[EPOCH_ENV_VAR]

    def test_legacy_epochs_set_contains_v35_and_others(self):
        """LEGACY_EPOCHS should contain v35, v36.3, v37, v44."""
        from arifos_core.system.runtime_manifest import LEGACY_EPOCHS

        assert "v35" in LEGACY_EPOCHS
        assert "v36.3" in LEGACY_EPOCHS
        assert "v37" in LEGACY_EPOCHS
        assert "v44" in LEGACY_EPOCHS
