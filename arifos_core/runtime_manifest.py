"""
runtime_manifest.py — arifOS Runtime Manifest Loader (v35Omega)

Provides utilities to load and validate the canonical runtime manifest
that describes the complete arifOS v35Omega constitutional cage.

The manifest is DESCRIPTIVE ONLY - this loader does not change behavior.

Usage:
    from arifos_core.runtime_manifest import load_runtime_manifest

    manifest = load_runtime_manifest()
    print(manifest["version"])  # "35Omega"
    print(manifest["floors"]["truth"]["threshold"])  # 0.99

External tools and notebooks can use the manifest to:
- Discover floor thresholds and check functions
- Understand pipeline stages and routing
- Import AAA engines, W@W organs, @EYE views dynamically
- Find the caged harness entry point

Author: arifOS Project
Version: v35Omega
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# PyYAML is optional - fall back to JSON if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None  # type: ignore


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_MANIFEST_PATH_YAML = Path(__file__).parent.parent / "spec" / "arifos_runtime_manifest_v35Omega.yaml"
DEFAULT_MANIFEST_PATH_JSON = Path(__file__).parent.parent / "spec" / "arifos_runtime_manifest_v35Omega.json"

# Default to JSON if YAML not available
DEFAULT_MANIFEST_PATH = DEFAULT_MANIFEST_PATH_YAML if HAS_YAML else DEFAULT_MANIFEST_PATH_JSON

REQUIRED_TOP_LEVEL_KEYS: Set[str] = {
    "version",
    "epoch",
    "status",
    "floors",
    "pipeline",
    "engines",
    "waw",
    "eye_sentinel",
    "metrics",
    "ledger",
    "harness",
}

REQUIRED_FLOOR_IDS: Set[str] = {
    "truth",
    "delta_s",
    "peace_squared",
    "kappa_r",
    "omega_0",
    "amanah",
    "rasa",
    "tri_witness",
    "anti_hantu",
}


# =============================================================================
# MANIFEST LOADER
# =============================================================================

def load_runtime_manifest(
    path: Optional[Path] = None,
    validate: bool = True,
) -> Dict[str, Any]:
    """
    Load the arifOS runtime manifest from YAML or JSON.

    Args:
        path: Path to manifest file. Defaults to spec/arifos_runtime_manifest_v35Omega.yaml
              (or .json if PyYAML not installed)
        validate: Whether to perform basic validation (default True)

    Returns:
        Parsed manifest as a dictionary

    Raises:
        FileNotFoundError: If manifest file does not exist
        ValueError: If YAML/JSON parsing fails or validation fails

    Example:
        manifest = load_runtime_manifest()
        print(manifest["floors"]["truth"]["threshold"])  # 0.99
    """
    if path is None:
        # Try YAML first if available, then JSON
        if HAS_YAML and DEFAULT_MANIFEST_PATH_YAML.exists():
            path = DEFAULT_MANIFEST_PATH_YAML
        elif DEFAULT_MANIFEST_PATH_JSON.exists():
            path = DEFAULT_MANIFEST_PATH_JSON
        else:
            path = DEFAULT_MANIFEST_PATH_YAML  # Will raise FileNotFoundError

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        if path.suffix in (".yaml", ".yml"):
            if not HAS_YAML:
                raise ImportError(
                    "PyYAML is required to load YAML manifest. "
                    "Install with: pip install pyyaml"
                )
            manifest = yaml.safe_load(f)
        else:
            manifest = json.load(f)

    if validate:
        validate_manifest(manifest)

    return manifest


def validate_manifest(manifest: Dict[str, Any]) -> None:
    """
    Perform basic validation on the manifest structure.

    Checks:
    - Required top-level keys are present
    - All 9 floors are defined
    - Pipeline stages include 000 and 999
    - Version matches expected format

    Args:
        manifest: Parsed manifest dictionary

    Raises:
        ValueError: If validation fails
    """
    # Check required top-level keys
    missing_keys = REQUIRED_TOP_LEVEL_KEYS - set(manifest.keys())
    if missing_keys:
        raise ValueError(f"Manifest missing required keys: {missing_keys}")

    # Check version format
    version = manifest.get("version", "")
    if not version or "Omega" not in version:
        raise ValueError(f"Invalid version format: {version}")

    # Check floors
    floors = manifest.get("floors", {})
    missing_floors = REQUIRED_FLOOR_IDS - set(floors.keys())
    if missing_floors:
        raise ValueError(f"Manifest missing required floors: {missing_floors}")

    # Check pipeline stages
    pipeline = manifest.get("pipeline", {})
    stages = pipeline.get("stages", {})
    if "000" not in stages:
        raise ValueError("Pipeline missing stage 000 (VOID)")
    if "999" not in stages:
        raise ValueError("Pipeline missing stage 999 (SEAL)")

    # Check engines
    engines = manifest.get("engines", {})
    required_engines = {"arif", "adam", "apex"}
    missing_engines = required_engines - set(engines.keys())
    if missing_engines:
        raise ValueError(f"Manifest missing required engines: {missing_engines}")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_floor_threshold(
    manifest: Dict[str, Any],
    floor_id: str,
) -> Any:
    """
    Get the threshold value for a specific floor.

    Args:
        manifest: Loaded manifest dictionary
        floor_id: Floor identifier (e.g., "truth", "omega_0")

    Returns:
        Threshold value (float, bool, or dict for range-based floors)

    Raises:
        KeyError: If floor not found
    """
    floor = manifest["floors"].get(floor_id)
    if floor is None:
        raise KeyError(f"Floor not found: {floor_id}")

    # Handle range-based thresholds (omega_0)
    if "threshold_min" in floor and "threshold_max" in floor:
        return {"min": floor["threshold_min"], "max": floor["threshold_max"]}

    return floor.get("threshold")


def get_pipeline_stages(manifest: Dict[str, Any]) -> List[str]:
    """
    Get ordered list of all pipeline stage codes.

    Args:
        manifest: Loaded manifest dictionary

    Returns:
        List of stage codes in order (e.g., ["000", "111", ..., "999"])
    """
    stages = manifest.get("pipeline", {}).get("stages", {})
    return sorted(stages.keys())


def get_eye_views(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get list of all @EYE Sentinel views.

    Args:
        manifest: Loaded manifest dictionary

    Returns:
        List of view definitions with name, module, class, description
    """
    return manifest.get("eye_sentinel", {}).get("views", [])


def get_waw_organs(manifest: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Get all W@W Federation organs.

    Args:
        manifest: Loaded manifest dictionary

    Returns:
        Dict mapping organ name to organ definition
    """
    return manifest.get("waw", {}).get("organs", {})


def get_harness_entry(manifest: Dict[str, Any]) -> Dict[str, str]:
    """
    Get the caged harness entry point information.

    Args:
        manifest: Loaded manifest dictionary

    Returns:
        Dict with module, entry_function, result_class
    """
    harness = manifest.get("harness", {})
    return {
        "module": harness.get("module", ""),
        "entry_function": harness.get("entry_function", ""),
        "result_class": harness.get("result_class", ""),
    }


# =============================================================================
# DYNAMIC IMPORT HELPERS
# =============================================================================

def import_module_from_manifest(
    manifest: Dict[str, Any],
    component: str,
    subcomponent: Optional[str] = None,
) -> Any:
    """
    Dynamically import a module referenced in the manifest.

    Args:
        manifest: Loaded manifest dictionary
        component: Top-level component ("engines", "waw", "eye_sentinel", etc.)
        subcomponent: Optional subcomponent (e.g., "arif" for engines)

    Returns:
        Imported module

    Raises:
        KeyError: If component/subcomponent not found
        ImportError: If module import fails

    Example:
        # Import ARIFEngine module
        arif_mod = import_module_from_manifest(manifest, "engines", "arif")
    """
    comp = manifest.get(component, {})

    if subcomponent:
        # Navigate to subcomponent
        if component == "engines":
            module_path = comp.get(subcomponent, {}).get("module")
        elif component == "waw":
            module_path = comp.get("organs", {}).get(subcomponent, {}).get("module")
        elif component == "eye_sentinel":
            # Find view by name
            views = comp.get("views", [])
            view = next((v for v in views if v.get("name") == subcomponent), None)
            if view is None:
                raise KeyError(f"View not found: {subcomponent}")
            module_path = view.get("module")
        else:
            raise KeyError(f"Unknown component: {component}")
    else:
        # Get module from component directly
        if component == "metrics":
            module_path = comp.get("module")
        elif component == "harness":
            module_path = comp.get("module")
        elif component == "waw":
            module_path = comp.get("federation", {}).get("module")
        elif component == "eye_sentinel":
            module_path = comp.get("coordinator", {}).get("module")
        else:
            module_path = comp.get("entry_module") or comp.get("module")

    if not module_path:
        raise KeyError(f"Module path not found for {component}/{subcomponent}")

    return importlib.import_module(module_path)


def get_class_from_manifest(
    manifest: Dict[str, Any],
    component: str,
    subcomponent: Optional[str] = None,
) -> type:
    """
    Dynamically get a class referenced in the manifest.

    Args:
        manifest: Loaded manifest dictionary
        component: Top-level component
        subcomponent: Optional subcomponent

    Returns:
        The class object

    Example:
        # Get ARIFEngine class
        ARIFEngine = get_class_from_manifest(manifest, "engines", "arif")
        engine = ARIFEngine()
    """
    comp = manifest.get(component, {})

    # Get class name
    if subcomponent:
        if component == "engines":
            class_name = comp.get(subcomponent, {}).get("class")
        elif component == "waw":
            class_name = comp.get("organs", {}).get(subcomponent, {}).get("class")
        elif component == "eye_sentinel":
            views = comp.get("views", [])
            view = next((v for v in views if v.get("name") == subcomponent), None)
            if view is None:
                raise KeyError(f"View not found: {subcomponent}")
            class_name = view.get("class")
        else:
            raise KeyError(f"Unknown component: {component}")
    else:
        if component == "metrics":
            class_name = comp.get("dataclass")
        elif component == "harness":
            class_name = comp.get("result_class")
        elif component == "waw":
            class_name = comp.get("federation", {}).get("class")
        elif component == "eye_sentinel":
            class_name = comp.get("coordinator", {}).get("class")
        elif component == "pipeline":
            class_name = comp.get("entry_class")
        else:
            class_name = comp.get("class")

    if not class_name:
        raise KeyError(f"Class name not found for {component}/{subcomponent}")

    module = import_module_from_manifest(manifest, component, subcomponent)
    return getattr(module, class_name)


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Main loader
    "load_runtime_manifest",
    "validate_manifest",
    "DEFAULT_MANIFEST_PATH",
    "DEFAULT_MANIFEST_PATH_YAML",
    "DEFAULT_MANIFEST_PATH_JSON",
    "HAS_YAML",
    # Helpers
    "get_floor_threshold",
    "get_pipeline_stages",
    "get_eye_views",
    "get_waw_organs",
    "get_harness_entry",
    # Dynamic import
    "import_module_from_manifest",
    "get_class_from_manifest",
]
