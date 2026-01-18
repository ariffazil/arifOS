"""Spec binding validation (v42.1).

Loads and validates required spec files, computes hashes, and returns
payloads used by runtime bootstrap, @EYE, and ledger enrichment.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any

import yaml


class SpecValidationError(Exception):
    """Raised when spec binding validation fails."""


def _hash_file(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def _load_file(path: Path) -> Any:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_paths(rel_path: str) -> List[Path]:
    """Return candidate absolute paths for a repo-relative spec path."""
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / rel_path,  # repo root/spec/...
        here.parents[2] / rel_path,  # arifos_core/spec/...
    ]
    return [p for p in candidates if p.exists()]


def validate_spec_binding(
    spec_paths: List[str] | None = None,
    epsilon_map_key: str = "epsilon_map",
) -> Dict[str, Any]:
    """
    Validate required spec files and return binding payload.

    Raises:
        SpecValidationError on missing file or malformed content.
    """
    # Load binding spec first (declares required files)
    binding_rel = "spec/v42/spec_binding.json"
    binding_candidates = _candidate_paths(binding_rel)
    if not binding_candidates:
        raise SpecValidationError(f"spec binding not found: {binding_rel}")
    binding_path = binding_candidates[0]
    binding_spec = _load_file(binding_path)

    required = binding_spec.get("required_spec_files", [])
    if spec_paths is None:
        spec_paths = required
    else:
        # merge custom list with required to ensure coverage
        for r in required:
            if r not in spec_paths:
                spec_paths.append(r)

    spec_hashes: Dict[str, str] = {}
    loaded_specs: Dict[str, Any] = {}

    for rel in spec_paths:
        candidates = _candidate_paths(rel)
        if not candidates:
            if binding_spec.get("hash_policy", {}).get("fail_on_missing_spec", True):
                raise SpecValidationError(f"required spec missing: {rel}")
            else:
                continue
        path = candidates[0]
        try:
            loaded_specs[rel] = _load_file(path)
            spec_hashes[rel] = _hash_file(path)
        except Exception as exc:  # noqa: BLE001
            raise SpecValidationError(f"failed to load spec {rel}: {exc}") from exc

    if epsilon_map_key not in binding_spec:
        raise SpecValidationError("epsilon_map missing in spec_binding.json")

    epsilon_map = binding_spec[epsilon_map_key]
    version_map = {rel: spec.get("version", "unknown") for rel, spec in loaded_specs.items()}

    payload = {
        "spec_hashes": spec_hashes,
        "epsilon_map": epsilon_map,
        "version_map": version_map,
        # Placeholder zkPC receipt for runtime; real proof can be attached later.
        "zkpc_receipt": {"id": "zkpc-spec-binding-v42.1", "valid": True},
    }
    return payload


__all__ = ["validate_spec_binding", "SpecValidationError"]
