"""
Cooling Ledger Configuration Loader (v45)
Loads Phoenix-72 config, scar lifecycle, verdict routing.

Track B Authority: spec/v45/cooling_ledger_phoenix.json
Fallback: spec/v44/cooling_ledger_phoenix.json

Author: arifOS Project
Version: v45.0
"""

from __future__ import annotations
import json
import logging
import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Module-level cache (loaded once at import)
_LEDGER_CONFIG_SPEC: Optional[Dict[str, Any]] = None


def _load_ledger_config_spec() -> Dict[str, Any]:
    """
    Load cooling ledger configuration with Track B verification.

    Priority:
    A) ARIFOS_LEDGER_SPEC env var (absolute path override)
    B) spec/v45/cooling_ledger_phoenix.json (AUTHORITATIVE)
    C) spec/v44/cooling_ledger_phoenix.json (FALLBACK with deprecation warning)
    D) HARD FAIL (no v42/v38/v35)

    Returns:
        Dict containing ledger config

    Raises:
        RuntimeError: If spec not found or validation fails
    """
    global _LEDGER_CONFIG_SPEC
    if _LEDGER_CONFIG_SPEC is not None:
        return _LEDGER_CONFIG_SPEC

    # Find package root
    pkg_dir = Path(__file__).resolve().parent.parent.parent
    spec_data = None
    spec_path_used = None

    # Priority A: Environment variable override
    env_path = os.getenv("ARIFOS_LEDGER_SPEC")
    if env_path:
        env_spec_path = Path(env_path)
        if env_spec_path.exists():
            try:
                with open(env_spec_path, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                spec_path_used = env_spec_path
                logger.info(f"Loaded ledger config from env: {env_spec_path}")
            except Exception as e:
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Failed to load ledger config from ARIFOS_LEDGER_SPEC={env_path}: {e}"
                )

    # Priority B: spec/v45/cooling_ledger_phoenix.json (AUTHORITATIVE)
    if spec_data is None:
        v45_path = pkg_dir / "spec" / "v45" / "cooling_ledger_phoenix.json"
        if v45_path.exists():
            try:
                with open(v45_path, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                spec_path_used = v45_path
                logger.info(f"Loaded ledger config from v45: {v45_path}")
            except Exception as e:
                raise RuntimeError(f"TRACK B AUTHORITY FAILURE: Failed to parse {v45_path}: {e}")

    # Priority C: spec/v44/cooling_ledger_phoenix.json (FALLBACK with deprecation warning)
    if spec_data is None:
        v44_path = pkg_dir / "spec" / "v44" / "cooling_ledger_phoenix.json"
        if v44_path.exists():
            warnings.warn(
                f"Loading from spec/v44/ (DEPRECATED). Please migrate to spec/v45/. "
                f"v44 fallback will be removed in v46.0.",
                DeprecationWarning,
                stacklevel=2,
            )
            try:
                with open(v44_path, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                spec_path_used = v44_path
                logger.warning(f"Loaded ledger config from v44 (DEPRECATED): {v44_path}")
            except Exception as e:
                raise RuntimeError(f"TRACK B AUTHORITY FAILURE: Failed to parse {v44_path}: {e}")

    # Priority D: HARD FAIL
    if spec_data is None:
        raise RuntimeError(
            "TRACK B AUTHORITY FAILURE: Cooling ledger config not found.\n\n"
            "Searched locations:\n"
            f"  - spec/v45/cooling_ledger_phoenix.json (AUTHORITATIVE)\n"
            f"  - spec/v44/cooling_ledger_phoenix.json (FALLBACK)\n\n"
            "Migration required:\n"
            "1. Ensure spec/v45/cooling_ledger_phoenix.json exists\n"
            "2. Or set ARIFOS_LEDGER_SPEC=/path/to/spec/v45/cooling_ledger_phoenix.json"
        )

    # Schema validation (if schema exists)
    v45_schema_path = pkg_dir / "spec" / "v45" / "schema" / "cooling_ledger_phoenix.schema.json"
    v44_schema_path = pkg_dir / "spec" / "v44" / "schema" / "cooling_ledger_phoenix.schema.json"
    schema_path = v45_schema_path if v45_schema_path.exists() else v44_schema_path

    if schema_path.exists():
        try:
            import jsonschema

            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            jsonschema.validate(spec_data, schema)
            logger.debug(f"Ledger config validated against schema: {schema_path}")
        except ImportError:
            logger.warning("jsonschema not installed, skipping ledger config validation")
        except Exception as e:
            raise RuntimeError(
                f"TRACK B AUTHORITY FAILURE: Spec validation failed for {spec_path_used}\n"
                f"Schema: {schema_path}\n"
                f"Error: {e}"
            )

    _LEDGER_CONFIG_SPEC = spec_data
    return _LEDGER_CONFIG_SPEC


# =============================================================================
# Module-Level Constants (loaded from spec at import)
# =============================================================================


def _get_ledger_config() -> Dict[str, Any]:
    """Wrapper to ensure spec is loaded."""
    return _load_ledger_config_spec()


# Cooling Ledger Configuration
LEDGER_CONFIG = _get_ledger_config().get("cooling_ledger", {})
HASH_ALGORITHM: str = LEDGER_CONFIG.get("hash_algorithm", "SHA3-256")
CHAIN_ALGORITHM: str = LEDGER_CONFIG.get("chain_algorithm", "SHA3-256")
ENTRY_SCHEMA_VERSION: str = LEDGER_CONFIG.get("entry_schema_version", "v45.0")

# Rotation Config
ROTATION_CONFIG = LEDGER_CONFIG.get("rotation", {})
HOT_SEGMENT_DAYS: int = ROTATION_CONFIG.get("hot_segment_days", 7)
HOT_SEGMENT_MAX_ENTRIES: int = ROTATION_CONFIG.get("hot_segment_max_entries", 10000)

# Phoenix-72 Configuration
PHOENIX_72_CONFIG = _get_ledger_config().get("phoenix_72", {})
PHOENIX_TIMEOUT_HOURS: int = PHOENIX_72_CONFIG.get("timeout_hours", 72)
PHOENIX_REVIVE_COOLDOWN_HOURS: int = PHOENIX_72_CONFIG.get("revive_cooldown_hours", 24)

# Scar Lifecycle Configuration
SCAR_CONFIG = _get_ledger_config().get("scar_lifecycle", {})
SCAR_RETENTION_DAYS: int = SCAR_CONFIG.get("retention_days", 365)
SCAR_MAX_ENTRIES: int = SCAR_CONFIG.get("max_entries", 1000)

# Verdict Band Routing
VERDICT_BAND_ROUTING: Dict[str, List[str]] = _get_ledger_config().get("verdict_band_routing", {})

# Default routing if not specified in spec
DEFAULT_VERDICT_ROUTING = {
    "SEAL": ["LEDGER", "ACTIVE"],
    "PARTIAL": ["LEDGER", "PHOENIX"],
    "SABAR": ["LEDGER", "PHOENIX"],
    "VOID": ["LEDGER", "VOID"],
    "888_HOLD": ["LEDGER", "PENDING"],
    "SUNSET": ["LEDGER", "PHOENIX"],
}

# Merge with defaults
for verdict, bands in DEFAULT_VERDICT_ROUTING.items():
    if verdict not in VERDICT_BAND_ROUTING:
        VERDICT_BAND_ROUTING[verdict] = bands


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "HASH_ALGORITHM",
    "CHAIN_ALGORITHM",
    "ENTRY_SCHEMA_VERSION",
    "HOT_SEGMENT_DAYS",
    "HOT_SEGMENT_MAX_ENTRIES",
    "PHOENIX_TIMEOUT_HOURS",
    "PHOENIX_REVIVE_COOLDOWN_HOURS",
    "SCAR_RETENTION_DAYS",
    "SCAR_MAX_ENTRIES",
    "VERDICT_BAND_ROUTING",
]
