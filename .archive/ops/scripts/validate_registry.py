#!/usr/bin/env python3
"""
Registry Validation Script
Low-risk, high-reward: Catches inconsistencies before they break init_anchor.

Usage: python scripts/validate_registry.py
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

REGISTRY_DIR = Path(__file__).parent.parent
SOULS_DIR = REGISTRY_DIR / "provider_souls"
MODELS_DIR = REGISTRY_DIR / "models"
RUNTIME_DIR = REGISTRY_DIR / "runtime_profiles"
SCHEMAS_DIR = REGISTRY_DIR / "schemas"
CATALOG_PATH = REGISTRY_DIR / "catalog.json"


def load_json(path):
    """Load JSON file with proper encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_provider_soul(file_path, schema=None):
    """Validate a single provider soul file."""
    errors = []
    filename = Path(file_path).stem

    # Skip validation for test fixtures (files starting with 'wrong_')
    if filename.startswith("wrong_"):
        return []

    try:
        data = load_json(file_path)
    except Exception as e:
        return [f"JSON parse error: {e}"]

    # Required fields
    required = ["provider_key", "family_key", "soul_label"]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check provider_key doesn't contain underscore (should be clean)
    provider_key = data.get("provider_key", "")
    if "_" in provider_key:
        errors.append(f"Provider key '{provider_key}' contains underscore")

    # Check arrays are actually arrays
    array_fields = ["communication_style", "reasoning_style", "best_fit_roles", "worst_fit_roles"]
    for field in array_fields:
        if field in data and not isinstance(data[field], list):
            errors.append(f"Field '{field}' should be an array")

    # JSON Schema validation
    if schema and HAS_JSONSCHEMA:
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema violation: {e.message}")

    return errors


def validate_catalog():
    """Validate catalog.json matches provider_souls/*.json and models/."""
    errors = []

    catalog = load_json(CATALOG_PATH)
    catalog_archetypes = set(catalog.get("soul_archetypes", []))
    catalog_models = catalog.get("models", [])

    # Check soul archetype files
    actual_files = {f.stem for f in SOULS_DIR.glob("*.json")}
    missing_files = catalog_archetypes - actual_files
    extra_files = actual_files - catalog_archetypes
    if missing_files:
        errors.append(f"In catalog but no file: {missing_files}")
    if extra_files:
        errors.append(f"Has file but not in catalog: {extra_files}")

    # Check model files exist
    for model_key in catalog_models:
        model_path = MODELS_DIR / f"{model_key}.json"
        if not model_path.exists():
            errors.append(f"Model file not found: {model_path.relative_to(REGISTRY_DIR)}")

    return errors, catalog


def validate_runtime_profiles(schema=None):
    """Validate runtime_profiles/*.json against schema."""
    errors = []
    for rt_file in sorted(RUNTIME_DIR.glob("*.json")):
        try:
            data = load_json(rt_file)
            if schema and HAS_JSONSCHEMA:
                jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append((rt_file.name, f"Schema violation: {e.message}"))
        except Exception as e:
            errors.append((rt_file.name, str(e)))
    return errors


def main():
    """Run all validations."""
    all_errors = []

    if not HAS_JSONSCHEMA:
        print("⚠️  jsonschema not installed — schema validation skipped. Run: pip install jsonschema")

    print("🔍 Validating arifOS Model Registry...\n")

    # Load schemas (best-effort)
    soul_schema = runtime_schema = None
    try:
        soul_schema = load_json(SCHEMAS_DIR / "provider_soul.schema.json")
        runtime_schema = load_json(SCHEMAS_DIR / "runtime_truth.schema.json")
    except Exception as e:
        print(f"⚠️  Could not load schemas: {e}")

    # 1. Validate each provider soul
    print("1. Checking provider_souls/*.json files...")
    for soul_file in sorted(SOULS_DIR.glob("*.json")):
        errors = validate_provider_soul(soul_file, schema=soul_schema)
        if errors:
            all_errors.append(f"\n❌ {soul_file.name}:")
            for err in errors:
                all_errors.append(f"   - {err}")
        else:
            tag = " (honeypot)" if soul_file.stem.startswith("wrong_") else ""
            print(f"   ✅ {soul_file.name}{tag}")

    # 2. Validate catalog
    print("\n2. Checking catalog.json consistency...")
    errors, catalog = validate_catalog()
    if errors:
        all_errors.append("\n❌ catalog.json:")
        for err in errors:
            all_errors.append(f"   - {err}")
    else:
        archetype_count = len(catalog.get("soul_archetypes", []))
        model_count = len(catalog.get("models", []))
        print(f"   ✅ catalog.json: {archetype_count} archetypes, {model_count} models")

    # 3. Validate runtime profiles
    print("\n3. Checking runtime_profiles/*.json files...")
    rt_errors = validate_runtime_profiles(schema=runtime_schema)
    if rt_errors:
        for name, err in rt_errors:
            all_errors.append(f"\n❌ {name}: {err}")
    else:
        rt_count = len(list(RUNTIME_DIR.glob("*.json")))
        print(f"   ✅ {rt_count} runtime profile(s) valid")

    # Summary
    print("\n" + "=" * 50)
    if all_errors:
        error_count = sum(1 for e in all_errors if e.startswith("\n❌"))
        print(f"❌ VALIDATION FAILED: {error_count} file(s) with errors")
        for err in all_errors:
            print(err)
        return 1
    else:
        print("✅ ALL VALIDATIONS PASSED")
        print(f"   - {len(list(SOULS_DIR.glob('*.json')))} provider souls")
        print(f"   - {len(catalog.get('soul_archetypes', []))} archetypes in catalog")
        print(f"   - {len(catalog.get('models', []))} models in catalog")
        print(f"   - {len(list(RUNTIME_DIR.glob('*.json')))} runtime profile(s)")
        return 0


if __name__ == "__main__":
    sys.exit(main())

