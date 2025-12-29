"""
runtime_manifest.py — arifOS Runtime Manifest Loader (v45 default)

Provides utilities to load and validate the canonical runtime manifest
that describes the complete arifOS constitutional cage.

DEFAULT EPOCH: v45 (ΔΩΨ Trinity + Lane-Aware Truth Routing + Sovereign Witness)

Supports multiple epochs via ARIFOS_RUNTIME_EPOCH environment variable:
- "v45": Default - ΔΩΨ Trinity with lane-scoped enforcement
- "v37": Unified runtime with full memory stack integration
- "v35" or "v35Omega": Legacy runtime (for regression/research only)
- "v36.3" or "v36.3Omega": Legacy spec layer (for regression/research only)

The manifest is DESCRIPTIVE ONLY - this loader does not change behavior.

Usage:
    from arifos_core.system.runtime_manifest import load_runtime_manifest, get_active_epoch

    # Load default (v45) manifest
    manifest = load_runtime_manifest()
    print(manifest["version"])  # "v45"

    # Check active epoch
    epoch = get_active_epoch()  # "v45" by default

    # Load legacy epoch manifest (for regression testing)
    manifest_v37 = load_runtime_manifest(epoch="v37")
    manifest_v35 = load_runtime_manifest(epoch="v35")

    # Check if running legacy epoch
    from arifos_core.system.runtime_manifest import is_legacy_epoch
    if is_legacy_epoch():
        print("Running in legacy mode")

External tools and notebooks can use the manifest to:
- Discover floor thresholds and check functions
- Understand pipeline stages and routing
- Import AAA engines, W@W organs, @EYE views dynamically
- Find the caged harness entry point

Author: arifOS Project
Version: v45
"""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set, Union

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

# Epoch type alias
EpochType = Literal["v35", "v36.3", "v37", "v44", "v45"]

# Environment variable for epoch selection
EPOCH_ENV_VAR = "ARIFOS_RUNTIME_EPOCH"

# Default epoch: v45 (Sovereign Witness + v42 spec structure)
# v35, v36.3, v37, v44 are legacy epochs, selectable via ARIFOS_RUNTIME_EPOCH env var
DEFAULT_EPOCH: EpochType = "v45"

# Legacy epochs (for is_legacy_epoch helper)
LEGACY_EPOCHS: Set[EpochType] = {"v35", "v36.3", "v37", "v44"}

# Base paths
# v42: File moved from arifos_core/ to arifos_core/system/, need to go up 2 levels
_BASE_DIR = Path(__file__).parent.parent.parent

# Manifest paths by epoch
MANIFEST_PATHS: Dict[EpochType, Dict[str, Path]] = {
    "v35": {
        "yaml": _BASE_DIR / "spec" / "arifos_runtime_manifest_v35Omega.yaml",
        "json": _BASE_DIR / "spec" / "arifos_runtime_manifest_v35Omega.json",
    },
    "v36.3": {
        "json": _BASE_DIR
        / "archive"
        / "versions"
        / "v36_3_omega"
        / "v36.3O"
        / "spec"
        / "arifos_runtime_manifest_v36.3O.json",
    },
    "v37": {
        "json": _BASE_DIR
        / "archive"
        / "versions"
        / "v36_3_omega"
        / "v36.3O"
        / "spec"
        / "arifos_runtime_manifest_v37.json",
    },
    "v44": {
        # v44 uses v42 spec structure (TEARFRAME is code-driven)
        "json": _BASE_DIR / "spec" / "arifos_runtime_manifest_v35Omega.json",
    },
    "v45": {
        # v45 (Sovereign Witness) uses v42 spec structure + new code modules
        # Manifest is descriptive; code enforces new logic (Firewall, EvidencePack, Seal)
        "json": _BASE_DIR / "spec" / "arifos_runtime_manifest_v35Omega.json",
    },
}

# Legacy aliases for backwards compatibility
DEFAULT_MANIFEST_PATH_YAML = MANIFEST_PATHS["v35"]["yaml"]
DEFAULT_MANIFEST_PATH_JSON = MANIFEST_PATHS["v35"]["json"]
DEFAULT_MANIFEST_PATH = DEFAULT_MANIFEST_PATH_YAML if HAS_YAML else DEFAULT_MANIFEST_PATH_JSON

# Required keys for v35 manifests (strict validation)
REQUIRED_TOP_LEVEL_KEYS_V35: Set[str] = {
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

# Required keys for v36.3+ manifests (relaxed - different structure)
REQUIRED_TOP_LEVEL_KEYS_V36: Set[str] = {
    "version",
    "epoch",
    "status",
    "floors",
    "pipeline",
    "engines",
    "waw",
    "eye_sentinel",
    "ledger",
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

# Epoch aliases for normalization
EPOCH_ALIASES: Dict[str, EpochType] = {
    "v35": "v35",
    "v35omega": "v35",
    "v35Omega": "v35",
    "35Omega": "v35",
    "v36.3": "v36.3",
    "v36.3omega": "v36.3",
    "v36.3Omega": "v36.3",
    "v36.3O": "v36.3",
    "v37": "v37",
    "v44": "v44",
    "v45.0": "v44",
    "v45": "v45",
    "v45.0": "v45",
}


# =============================================================================
# EPOCH SELECTION
# =============================================================================


def normalize_epoch(epoch: str) -> EpochType:
    """
    Normalize epoch string to canonical form.

    Args:
        epoch: Epoch string (e.g., "v35", "v35Omega", "v36.3", "v37")

    Returns:
        Canonical epoch: "v35" | "v36.3" | "v37"

    Raises:
        ValueError: If epoch is not recognized
    """
    normalized = EPOCH_ALIASES.get(epoch)
    if normalized is None:
        valid = list(set(EPOCH_ALIASES.values()))
        raise ValueError(f"Epoch {epoch} not found in registry. Available epochs: {valid}")
    return normalized


def get_active_epoch() -> EpochType:
    """
    Get the currently active epoch from environment or default.

    Reads ARIFOS_RUNTIME_EPOCH environment variable.
    Falls back to "v35" if not set.

    Returns:
        Active epoch: "v35" | "v36.3" | "v37"
    """
    env_epoch = os.environ.get(EPOCH_ENV_VAR, "")
    if env_epoch:
        try:
            return normalize_epoch(env_epoch)
        except ValueError:
            # Invalid env value - fall back to default with warning
            import warnings

            warnings.warn(
                f"Invalid {EPOCH_ENV_VAR}={env_epoch}, using default: {DEFAULT_EPOCH}",
                UserWarning,
            )
    return DEFAULT_EPOCH


def set_active_epoch(epoch: Union[str, EpochType]) -> EpochType:
    """
    Set the active epoch via environment variable.

    Args:
        epoch: Epoch to activate

    Returns:
        Normalized epoch that was set
    """
    normalized = normalize_epoch(epoch)
    os.environ[EPOCH_ENV_VAR] = normalized
    return normalized


def get_manifest_path_for_epoch(epoch: EpochType) -> Path:
    """
    Get the manifest file path for a specific epoch.

    Args:
        epoch: Canonical epoch ("v35" | "v36.3" | "v37")

    Returns:
        Path to manifest file

    Raises:
        FileNotFoundError: If no manifest exists for epoch
    """
    paths = MANIFEST_PATHS.get(epoch, {})

    # Prefer YAML for v35 if available, otherwise JSON
    if epoch == "v35":
        if HAS_YAML and paths.get("yaml", Path()).exists():
            return paths["yaml"]
        if paths.get("json", Path()).exists():
            return paths["json"]
    else:
        # v36.3 and v37 are JSON only
        if paths.get("json", Path()).exists():
            return paths["json"]

    raise FileNotFoundError(f"Manifest file for epoch {epoch} not located. Check spec/ directory.")


# =============================================================================
# MANIFEST LOADER
# =============================================================================


def load_runtime_manifest(
    path: Optional[Path] = None,
    validate: bool = True,
    epoch: Optional[Union[str, EpochType]] = None,
) -> Dict[str, Any]:
    """
    Load the arifOS runtime manifest from YAML or JSON.

    Args:
        path: Path to manifest file. If None, uses epoch-based path.
        validate: Whether to perform basic validation (default True)
        epoch: Specific epoch to load ("v35", "v36.3", "v37").
               If None, uses ARIFOS_RUNTIME_EPOCH env var or default.

    Returns:
        Parsed manifest as a dictionary

    Raises:
        FileNotFoundError: If manifest file does not exist
        ValueError: If YAML/JSON parsing fails or validation fails

    Example:
        # Load active epoch manifest
        manifest = load_runtime_manifest()

        # Load specific epoch
        manifest_v37 = load_runtime_manifest(epoch="v37")

        # Load from specific path
        manifest = load_runtime_manifest(path=Path("custom_manifest.json"))
    """
    # Determine which epoch to load
    if epoch is not None:
        resolved_epoch = normalize_epoch(epoch)
    else:
        resolved_epoch = get_active_epoch()

    # Determine path
    if path is None:
        path = get_manifest_path_for_epoch(resolved_epoch)
    else:
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Manifest path {path} does not exist.")

    with path.open("r", encoding="utf-8") as f:
        if path.suffix in (".yaml", ".yml"):
            if not HAS_YAML:
                raise ImportError(
                    "PyYAML is required to load YAML manifest. Install with: pip install pyyaml"
                )
            manifest = yaml.safe_load(f)
        else:
            manifest = json.load(f)

    if validate:
        validate_manifest(manifest, epoch=resolved_epoch)

    # Add runtime metadata
    manifest["_runtime_epoch"] = resolved_epoch
    manifest["_manifest_path"] = str(path)

    return manifest


def validate_manifest(
    manifest: Dict[str, Any],
    epoch: Optional[EpochType] = None,
) -> None:
    """
    Perform basic validation on the manifest structure.

    Checks:
    - Required top-level keys are present
    - Version matches expected format
    - For v35: All 9 floors are defined, pipeline stages include 000 and 999

    Args:
        manifest: Parsed manifest dictionary
        epoch: Expected epoch (for validation rules)

    Raises:
        ValueError: If validation fails
    """
    # Determine validation rules based on epoch
    if epoch in ("v36.3", "v37"):
        required_keys = REQUIRED_TOP_LEVEL_KEYS_V36
        # v36.3/v37 manifests have different floor structure (mapping-based)
        validate_floors = False
        validate_engines = False
    else:
        required_keys = REQUIRED_TOP_LEVEL_KEYS_V35
        validate_floors = True
        validate_engines = True

    # Check required top-level keys
    missing_keys = required_keys - set(manifest.keys())
    if missing_keys:
        raise ValueError(f"Manifest incomplete. Required fields absent: {missing_keys}")

    # Check version format (relaxed for v36.3/v37)
    version = manifest.get("version", "")
    if not version:
        raise ValueError("Manifest file does not specify version field.")

    # v35 strict check
    if epoch == "v35" and "Omega" not in version:
        raise ValueError(f"Version field '{version}' does not match v35 schema pattern.")

    # Check floors (v35 only)
    if validate_floors:
        floors = manifest.get("floors", {})
        missing_floors = REQUIRED_FLOOR_IDS - set(floors.keys())
        if missing_floors:
            raise ValueError(f"Manifest incomplete. Floor definitions absent: {missing_floors}")

    # Check pipeline stages
    pipeline = manifest.get("pipeline", {})
    stages = pipeline.get("stages", {})

    # v36.3/v37 use list format
    if isinstance(stages, list):
        stage_ids = {s.get("id") for s in stages}
    else:
        stage_ids = set(stages.keys())

    if "000" not in stage_ids:
        raise ValueError("Pipeline configuration incomplete: Stage 000 (VOID) not defined.")
    if "999" not in stage_ids:
        raise ValueError("Pipeline configuration incomplete: Stage 999 (SEAL) not defined.")

    # Check engines (v35 only)
    if validate_engines:
        engines = manifest.get("engines", {})
        required_engines = {"agi", "asi", "apex"}
        missing_engines = required_engines - set(engines.keys())
        if missing_engines:
            raise ValueError(f"Manifest incomplete. Engine definitions absent: {missing_engines}")


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
    floors = manifest.get("floors", {})

    # v36.3/v37 use mapping structure
    if "mapping" in floors:
        # Look up by floor ID (F1, F2, etc.) or metrics_field
        for fid, fdata in floors.get("mapping", {}).items():
            if fdata.get("metrics_field") == floor_id:
                # Return from spec file - for now, return None (spec-driven)
                return None
        raise KeyError(f"Floor {floor_id} not registered in mapping table.")

    # v35 direct structure
    floor = floors.get(floor_id)
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

    # v36.3/v37 use list format
    if isinstance(stages, list):
        return [s.get("id") for s in stages if s.get("id")]

    # v35 dict format
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


def is_v37_epoch(manifest: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if the current/given manifest is v37 epoch.

    Args:
        manifest: Optional manifest dict. If None, checks active epoch.

    Returns:
        True if v37 epoch is active
    """
    if manifest is not None:
        return manifest.get("_runtime_epoch") == "v37"
    return get_active_epoch() == "v37"


def is_v36_or_newer(manifest: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if the current/given manifest is v36.3 or v37.

    Args:
        manifest: Optional manifest dict. If None, checks active epoch.

    Returns:
        True if v36.3 or v37 epoch is active
    """
    if manifest is not None:
        return manifest.get("_runtime_epoch") in ("v36.3", "v37")
    return get_active_epoch() in ("v36.3", "v37")


def is_legacy_epoch(epoch: Optional[Union[str, EpochType]] = None) -> bool:
    """
    Check if an epoch is a legacy epoch (v35 or v36.3).

    Legacy epochs are maintained for regression testing and research only.
    The mainline runtime is v37.

    Args:
        epoch: Epoch to check. If None, checks the currently active epoch.

    Returns:
        True if the epoch is v35 or v36.3 (legacy)
    """
    if epoch is None:
        epoch = get_active_epoch()
    else:
        epoch = normalize_epoch(epoch)
    return epoch in LEGACY_EPOCHS


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
        # Import AGIEngine module
        agi_mod = import_module_from_manifest(manifest, "engines", "agi")
    """
    comp = manifest.get(component, {})

    if subcomponent:
        # Navigate to subcomponent
        if component == "engines":
            # v36.3/v37 use nested AAA structure
            if "AAA" in comp:
                module_path = comp.get("AAA", {}).get(subcomponent.upper(), {}).get("module")
            else:
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
            module_path = comp.get("coordinator", {}).get("module") or comp.get("module")
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
        # Get AGIEngine class
        AGIEngine = get_class_from_manifest(manifest, "engines", "agi")
        engine = AGIEngine()
    """
    comp = manifest.get(component, {})

    # Get class name
    if subcomponent:
        if component == "engines":
            # v36.3/v37 use nested AAA structure
            if "AAA" in comp:
                class_name = comp.get("AAA", {}).get(subcomponent.upper(), {}).get("class")
            else:
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
            class_name = comp.get("dataclass") or comp.get("metrics_dataclass", {}).get("class")
        elif component == "harness":
            class_name = comp.get("result_class")
        elif component == "waw":
            class_name = comp.get("federation", {}).get("class")
        elif component == "eye_sentinel":
            class_name = comp.get("coordinator", {}).get("class") or comp.get("class")
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
    # Epoch management
    "EpochType",
    "EPOCH_ENV_VAR",
    "DEFAULT_EPOCH",
    "LEGACY_EPOCHS",
    "normalize_epoch",
    "get_active_epoch",
    "set_active_epoch",
    "get_manifest_path_for_epoch",
    "is_v37_epoch",
    "is_v36_or_newer",
    "is_legacy_epoch",
    # Main loader
    "load_runtime_manifest",
    "validate_manifest",
    "MANIFEST_PATHS",
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
