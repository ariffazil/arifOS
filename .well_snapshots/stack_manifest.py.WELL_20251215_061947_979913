"""
stack_manifest.py — arifOS v38.2 Stack Manifest Loader

Provides a thin Python wrapper around the aggregated v38.2 stack spec in
`spec/arifos_v38_2_stack.json`.

The JSON file is a read-only meta-manifest that ties together:
- Pipeline v38Omega (000–999 stages)
- Constitutional floors v38Omega
- GENIUS LAW v38Omega
- Memory stack v38 (EUREKA + time governance)
- Cooling Ledger + Phoenix-72
- Runtime manifest references
- W@W prompt governance floors

This module does NOT change runtime behaviour. It simply exposes a
structured way for tools and notebooks to introspect the v38.2 stack
from Python, similar to `runtime_manifest.py` for v35/v37.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# CONSTANTS
# =============================================================================

_BASE_DIR = Path(__file__).parent.parent

# Canonical path to the v38.2 stack manifest JSON
DEFAULT_STACK_MANIFEST_PATH: Path = _BASE_DIR / "spec" / "arifos_v38_2_stack.json"


# =============================================================================
# LOADER
# =============================================================================

def load_stack_manifest(path: Optional[Path] = None) -> Dict[str, Any]:
  """
  Load the arifOS v38.2 stack manifest JSON.

  Args:
      path: Optional path to a stack manifest JSON file. If None, loads
            the canonical `spec/arifos_v38_2_stack.json`.

  Returns:
      Parsed stack manifest as a dictionary.

  Raises:
      FileNotFoundError: If the manifest file does not exist.
      ValueError: If JSON parsing fails or basic validation fails.
  """
  manifest_path = Path(path) if path is not None else DEFAULT_STACK_MANIFEST_PATH

  if not manifest_path.exists():
    raise FileNotFoundError(f"Stack manifest file not found: {manifest_path}")

  with manifest_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

  _validate_stack_manifest(data)

  # Attach runtime metadata for convenience
  data["_manifest_path"] = str(manifest_path)
  return data


def _validate_stack_manifest(manifest: Dict[str, Any]) -> None:
  """
  Perform minimal structural validation on the stack manifest.

  This validation is intentionally light-weight: the underlying specs
  (pipeline, floors, GENIUS LAW, memory, ledger) remain the single
  source of truth and have their own tests.

  Raises:
      ValueError: If required keys are missing or malformed.
  """
  required_top_level = {"version", "arifos_version", "stack_type", "components"}
  missing = required_top_level - set(manifest.keys())
  if missing:
    raise ValueError(f"Stack manifest missing required keys: {missing}")

  if not isinstance(manifest.get("components"), dict):
    raise ValueError("Stack manifest 'components' must be a dictionary")


# =============================================================================
# HELPERS
# =============================================================================

def get_component_ids(stack: Dict[str, Any]) -> List[str]:
  """
  Return the list of component IDs defined in the stack manifest.

  Args:
      stack: Parsed stack manifest dictionary.

  Returns:
      List of component IDs (e.g., ['pipeline', 'floors', 'genius_law', ...]).
  """
  return list(stack.get("components", {}).keys())


def get_component(stack: Dict[str, Any], component_id: str) -> Dict[str, Any]:
  """
  Get a specific component definition from the stack manifest.

  Args:
      stack: Parsed stack manifest dictionary.
      component_id: Component key (e.g., 'pipeline', 'memory_stack').

  Returns:
      Component definition dictionary.

  Raises:
      KeyError: If the component is not defined.
  """
  components = stack.get("components", {})
  if component_id not in components:
    raise KeyError(f"Component not found in stack manifest: {component_id}")
  return components[component_id]


__all__ = [
  "DEFAULT_STACK_MANIFEST_PATH",
  "load_stack_manifest",
  "get_component_ids",
  "get_component",
]

