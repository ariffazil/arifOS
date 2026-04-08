"""
Tests for the arifOS Model Registry.

Run with: python -m pytest tests/ -v
"""

import json
import pytest
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent
MODELS_PATH = REGISTRY_PATH / "archive" / "models"
SOULS_PATH = REGISTRY_PATH / "archive" / "provider_souls"
RUNTIME_PATH = REGISTRY_PATH / "archive" / "runtime_profiles"
CATALOG_PATH = REGISTRY_PATH / "docs" / "reference" / "catalog.json"
SCHEMAS_PATH = REGISTRY_PATH / "schemas"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def soul_schema():
    path = SCHEMAS_PATH / "provider_soul.schema.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def runtime_schema():
    path = SCHEMAS_PATH / "runtime_truth.schema.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Catalog tests
# =============================================================================

class TestCatalog:
    def test_catalog_loads(self, catalog):
        assert catalog is not None

    def test_catalog_has_required_keys(self, catalog):
        assert "soul_archetypes" in catalog
        assert "models" in catalog
        assert "runtime_profiles" in catalog

    def test_catalog_has_soul_archetypes(self, catalog):
        assert len(catalog["soul_archetypes"]) > 0

    def test_catalog_has_models(self, catalog):
        assert len(catalog["models"]) > 0

    def test_catalog_models_are_strings(self, catalog):
        """Catalog models list should be strings (provider/family/variant paths)."""
        for m in catalog["models"]:
            assert isinstance(m, str), f"Expected string, got {type(m)}: {m}"

    def test_catalog_model_paths_have_slashes(self, catalog):
        """Model keys should follow provider/family/variant format."""
        for m in catalog["models"]:
            parts = m.split("/")
            assert len(parts) == 3, f"Model key '{m}' should have 3 parts: provider/family/variant"

    def test_catalog_archetypes_are_strings(self, catalog):
        for soul in catalog["soul_archetypes"]:
            assert isinstance(soul, str)

    def test_catalog_soul_files_exist(self, catalog):
        """Every soul archetype in catalog must have a corresponding file."""
        for soul_key in catalog["soul_archetypes"]:
            soul_path = SOULS_PATH / f"{soul_key}.json"
            assert soul_path.exists(), f"Soul file missing: {soul_path.name}"

    def test_catalog_model_files_exist(self, catalog):
        """Every model in catalog must have a corresponding file."""
        for model_key in catalog["models"]:
            model_path = MODELS_PATH / f"{model_key}.json"
            assert model_path.exists(), f"Model file missing: models/{model_key}.json"

    def test_no_extra_soul_files(self, catalog):
        """Every soul file should be registered in the catalog."""
        catalog_archetypes = set(catalog["soul_archetypes"])
        for soul_file in SOULS_PATH.glob("*.json"):
            assert soul_file.stem in catalog_archetypes, (
                f"Soul file '{soul_file.name}' not listed in catalog.soul_archetypes"
            )


# =============================================================================
# Provider soul tests
# =============================================================================

class TestProviderSouls:
    REQUIRED_FIELDS = ["provider_key", "family_key", "soul_label", "in_one_sentence",
                       "communication_style", "reasoning_style", "best_fit_roles",
                       "worst_fit_roles", "when_to_use", "when_not_to_use"]

    def _soul_files(self):
        return [f for f in SOULS_PATH.glob("*.json") if not f.stem.startswith("wrong_")]

    def test_soul_files_exist(self):
        assert len(list(SOULS_PATH.glob("*.json"))) > 0

    @pytest.mark.parametrize("soul_file", [
        f for f in SOULS_PATH.glob("*.json")
        if not f.stem.startswith("wrong_")
    ])
    def test_soul_required_fields(self, soul_file):
        data = load_json(soul_file)
        for field in self.REQUIRED_FIELDS:
            assert field in data, f"{soul_file.name}: missing field '{field}'"

    @pytest.mark.parametrize("soul_file", [
        f for f in SOULS_PATH.glob("*.json")
        if not f.stem.startswith("wrong_")
    ])
    def test_soul_provider_key_no_underscore(self, soul_file):
        data = load_json(soul_file)
        provider_key = data.get("provider_key", "")
        assert "_" not in provider_key, (
            f"{soul_file.name}: provider_key '{provider_key}' must not contain underscore"
        )

    @pytest.mark.parametrize("soul_file", [
        f for f in SOULS_PATH.glob("*.json")
        if not f.stem.startswith("wrong_")
    ])
    def test_soul_array_fields(self, soul_file):
        data = load_json(soul_file)
        for field in ["communication_style", "reasoning_style", "best_fit_roles", "worst_fit_roles"]:
            if field in data:
                assert isinstance(data[field], list), (
                    f"{soul_file.name}: field '{field}' must be an array"
                )

    @pytest.mark.parametrize("soul_file", [
        f for f in SOULS_PATH.glob("*.json")
        if not f.stem.startswith("wrong_")
    ])
    def test_soul_schema_validation(self, soul_file, soul_schema):
        jsonschema = pytest.importorskip("jsonschema")
        data = load_json(soul_file)
        jsonschema.validate(instance=data, schema=soul_schema)


# =============================================================================
# Model file tests
# =============================================================================

class TestModelFiles:
    MODEL_REQUIRED = ["provider", "model_family", "model_variant", "soul_archetype"]

    @pytest.mark.parametrize("model_file", list(MODELS_PATH.rglob("*.json")))
    def test_model_required_fields(self, model_file):
        data = load_json(model_file)
        for field in self.MODEL_REQUIRED:
            assert field in data, f"{model_file}: missing field '{field}'"

    @pytest.mark.parametrize("model_file", list(MODELS_PATH.rglob("*.json")))
    def test_model_soul_archetype_exists(self, model_file, catalog):
        """Model's soul_archetype must be registered in catalog."""
        data = load_json(model_file)
        soul_archetype = data.get("soul_archetype")
        if soul_archetype:
            # Derive soul key from soul_archetype label — look up in soul files
            matched = False
            for soul_file in SOULS_PATH.glob("*.json"):
                soul = load_json(soul_file)
                if soul.get("soul_label") == soul_archetype:
                    matched = True
                    break
            assert matched, (
                f"{model_file.name}: soul_archetype '{soul_archetype}' not found in any provider soul"
            )


# =============================================================================
# Runtime profile tests
# =============================================================================

class TestRuntimeProfiles:
    def test_runtime_profiles_exist(self):
        profiles = list(RUNTIME_PATH.glob("*.json"))
        assert len(profiles) > 0, "No runtime profiles found"

    def test_vps_main_arifos_exists(self):
        assert (RUNTIME_PATH / "vps_main_arifos.json").exists()

    def test_vps_main_arifos_required_fields(self):
        data = load_json(RUNTIME_PATH / "vps_main_arifos.json")
        for field in ["deployment_id", "provider_key", "family_key", "model_id"]:
            assert field in data, f"Missing required field: {field}"

    @pytest.mark.parametrize("rt_file", list(RUNTIME_PATH.glob("*.json")))
    def test_runtime_schema_validation(self, rt_file, runtime_schema):
        jsonschema = pytest.importorskip("jsonschema")
        data = load_json(rt_file)
        jsonschema.validate(instance=data, schema=runtime_schema)


# =============================================================================
# Self-claim boundary tests
# =============================================================================

class TestSelfClaimBoundary:
    """Verify self_claim_boundary enforcement logic."""

    def test_vps_main_has_self_claim_boundary(self):
        data = load_json(RUNTIME_PATH / "vps_main_arifos.json")
        assert "self_claim_boundary" in data

    def test_self_claim_boundary_fields(self):
        data = load_json(RUNTIME_PATH / "vps_main_arifos.json")
        boundary = data.get("self_claim_boundary", {})
        for field in ["identity_claim_policy", "tool_claim_policy",
                      "knowledge_claim_policy", "execution_claim_policy"]:
            assert field in boundary, f"self_claim_boundary missing field: {field}"

    def test_identity_claim_policy_is_valid(self):
        data = load_json(RUNTIME_PATH / "vps_main_arifos.json")
        policy = data["self_claim_boundary"]["identity_claim_policy"]
        valid = {"verified_against_registry", "self_reported", "runtime_derived"}
        assert policy in valid, f"Invalid identity_claim_policy: {policy}"

    def test_tool_claim_policy_is_valid(self):
        data = load_json(RUNTIME_PATH / "vps_main_arifos.json")
        policy = data["self_claim_boundary"]["tool_claim_policy"]
        valid = {"runtime_truth_only", "capability_flags", "verified_list"}
        assert policy in valid, f"Invalid tool_claim_policy: {policy}"


# =============================================================================
# Verify identity claim logic (unit test of the business logic)
# =============================================================================

class TestIdentityClaimLogic:
    """Test the identity verification logic used in main.py."""

    def _verify(self, claimed: str, catalog: dict) -> dict:
        """Mirror of main.py's verify_identity_claim logic."""
        model_keys = catalog.get("models", [])
        matched_key = None
        for mk in model_keys:
            variant = mk.split("/")[-1] if "/" in mk else mk
            if mk == claimed or variant == claimed:
                matched_key = mk
                break
        if matched_key:
            return {"status": "CONFIRMED", "verified": matched_key}
        return {"status": "UNCONFIRMED", "verified": None, "mismatch_detected": True}

    def test_exact_match(self, catalog):
        result = self._verify("anthropic/claude/claude-3-7-sonnet", catalog)
        assert result["status"] == "CONFIRMED"
        assert result["verified"] == "anthropic/claude/claude-3-7-sonnet"
        assert "mismatch_detected" not in result

    def test_variant_match(self, catalog):
        result = self._verify("claude-3-7-sonnet", catalog)
        assert result["status"] == "CONFIRMED"
        assert "mismatch_detected" not in result

    def test_unknown_model(self, catalog):
        result = self._verify("fake-model-xyz-9999", catalog)
        assert result["status"] == "UNCONFIRMED"
        assert result["mismatch_detected"] is True

    def test_wrong_provider_model(self, catalog):
        """Honeypot: wrong-provider entry should still be 'confirmed' (it's in the catalog)."""
        result = self._verify("wrong-provider/wrong-family/claude-3-7-sonnet", catalog)
        assert result["status"] == "CONFIRMED"
