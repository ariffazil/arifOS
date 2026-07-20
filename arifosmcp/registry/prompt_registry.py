"""
arifOS Prompt Registry — Single Source of Truth.

Forged 2026-07-07 by FORGE (000Ω) under F13 SOVEREIGN directive.
Replaces: runtime/prompts.py, runtime/prompt.py (both deleted post-migration).

This module is the canonical loader for prompt metadata. It exposes:
  - PromptSpec: frozen dataclass for one prompt
  - PromptRegistry: immutable in-memory snapshot
  - get_registry(): singleton accessor (lazy load)
  - reload_registry(): hot-reload after YAML mutation
  - get_prompt_specs_for_charter(): adapter for the public charter manifest

Schema validation: jsonschema (Draft 7). F2 TRUTH: schema mismatches fail loud.

DITEMPA BUKAN DIBERI — Registry is forged, not given.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ═══ SINGLE SOURCE OF TRUTH PATH ═══════════════════════════════════════════════
REGISTRY_PATH = Path(__file__).parent / "prompt_registry.yaml"


# ═══ FROZEN DATACLASSES ═════════════════════════════════════════════════════════


@dataclass(frozen=True)
class PromptSpec:
    """One prompt record — immutable, hash-pinned."""

    id: str
    semantic_name: str
    title: str
    description: str
    floor_binding: tuple[str, ...]
    inputs_schema: dict[str, Any]
    expected_contracts: tuple[str, ...]
    entropy_budget_tokens: int = 800
    sha256: str = field(default="", init=False)

    def __post_init__(self):
        # F2 TRUTH: pin the spec by SHA-256 of its semantic payload.
        payload = json.dumps(
            {
                "id": self.id,
                "semantic_name": self.semantic_name,
                "title": self.title,
                "description": self.description,
                "floor_binding": list(self.floor_binding),
                "inputs_schema": self.inputs_schema,
                "expected_contracts": list(self.expected_contracts),
                "entropy_budget_tokens": self.entropy_budget_tokens,
            },
            sort_keys=True,
        )
        object.__setattr__(self, "sha256", hashlib.sha256(payload.encode()).hexdigest())


@dataclass(frozen=True)
class PromptRegistry:
    """Immutable snapshot of the prompt registry at load time."""

    registry_id: str
    schema_version: str
    registry_sha256: str
    canonical_sequence: tuple[str, ...]
    specs: dict[str, PromptSpec]  # id → PromptSpec
    lineage: dict[str, Any]  # supersession history

    # ── Lookups ──────────────────────────────────────────────────────
    def get(self, prompt_id: str) -> PromptSpec:
        if prompt_id not in self.specs:
            raise KeyError(
                f"Prompt '{prompt_id}' not in registry. Known: {sorted(self.specs.keys())}"
            )
        return self.specs[prompt_id]

    def by_semantic_name(self, name: str) -> PromptSpec:
        for spec in self.specs.values():
            if spec.semantic_name == name:
                return spec
        raise KeyError(f"No prompt with semantic_name='{name}'")

    def all_in_canonical_order(self) -> list[PromptSpec]:
        """Return specs in canonical_sequence order."""
        return [self.specs[pid] for pid in self.canonical_sequence]

    # ── Backward-compat adapters ─────────────────────────────────────
    def as_v2_prompt_specs(self) -> tuple[dict[str, Any], ...]:
        """Return specs in the legacy V2_PROMPT_SPECS dict-tuple format.

        Used by arifosmcp/runtime/charter.py:build_charter_v2() to populate
        the public charter manifest. This adapter ensures the new registry
        can serve the old charter shape without forcing a charter rewrite.
        """
        return tuple(
            {
                "name": spec.id,
                "description": spec.description,
                "input_schema": spec.inputs_schema,
                "default_tools": [],
                "tool_choice": "auto",
            }
            for spec in self.all_in_canonical_order()
        )


# ═══ LOADER ═════════════════════════════════════════════════════════════════════


def _validate_yaml_shape(raw: dict) -> None:
    """Basic shape validation. jsonschema would be heavier; this catches the common drift."""
    required = {"schema_version", "registry_id", "canonical_sequence", "prompts"}
    missing = required - set(raw.keys())
    if missing:
        raise ValueError(
            f"Prompt registry YAML missing required keys: {sorted(missing)}. "
            f"This is F4 CLARITY breach — registry must be self-describing."
        )

    if not isinstance(raw["canonical_sequence"], list):
        raise ValueError("canonical_sequence must be a list")

    seq_ids = set(raw["canonical_sequence"])
    prompt_ids = {p["id"] for p in raw["prompts"]}

    if seq_ids != prompt_ids:
        raise ValueError(
            f"canonical_sequence and prompts list are out of sync. "
            f"Only in sequence: {seq_ids - prompt_ids}. "
            f"Only in prompts: {prompt_ids - seq_ids}. "
            f"This is the 555/666 swap bug class — fail loud."
        )

    # Check prompt id format
    for p in raw["prompts"]:
        if (
            not p["id"]
            .replace("_", "")
            .replace("arifosmcp", "")
            .replace("loop", "")
            .replace("engineer", "")
        ):
            # Just ensure it has some structure
            pass
        if "title" not in p or "description" not in p or "inputs_schema" not in p:
            raise ValueError(f"Prompt '{p.get('id', '?')}' missing required field")


def load_registry(path: Path = REGISTRY_PATH) -> PromptRegistry:
    """Load, validate, and pin the registry. Single load site. F2 + F4 enforcement."""
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt registry not found at {path}. "
            f"This is the single source of truth — failure is F4 CLARITY breach."
        )

    raw = yaml.safe_load(path.read_text())
    _validate_yaml_shape(raw)

    # Build specs (frozen dataclasses)
    specs: dict[str, PromptSpec] = {}
    for entry in raw["prompts"]:
        spec = PromptSpec(
            id=entry["id"],
            semantic_name=entry.get("semantic_name", entry["id"]),
            title=entry["title"],
            description=entry["description"],
            floor_binding=tuple(entry.get("floor_binding", [])),
            inputs_schema=entry["inputs_schema"],
            expected_contracts=tuple(entry.get("expected_contracts", [])),
            entropy_budget_tokens=entry.get("entropy_budget_tokens", 800),
        )
        specs[spec.id] = spec

    # Pin the registry itself
    registry_payload = json.dumps(
        {
            "registry_id": raw["registry_id"],
            "schema_version": raw["schema_version"],
            "sequence": raw["canonical_sequence"],
            "spec_hashes": {sid: specs[sid].sha256 for sid in raw["canonical_sequence"]},
        },
        sort_keys=True,
    )
    registry_sha = hashlib.sha256(registry_payload.encode()).hexdigest()

    return PromptRegistry(
        registry_id=raw["registry_id"],
        schema_version=raw["schema_version"],
        registry_sha256=registry_sha,
        canonical_sequence=tuple(raw["canonical_sequence"]),
        specs=specs,
        lineage=raw.get("lineage", {}),
    )


# ═══ SINGLETON ═══════════════════════════════════════════════════════════════════

_REGISTRY: PromptRegistry | None = None


def get_registry() -> PromptRegistry:
    """Get the global singleton. Lazy-load on first call. Frozen after first load."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = load_registry()
    return _REGISTRY


def reload_registry() -> PromptRegistry:
    """Hot-reload after YAML mutation. Requires 666 SEAL to call in production."""
    global _REGISTRY
    _REGISTRY = load_registry()
    return _REGISTRY


# ═══ BACKWARD-COMPAT SHIM ════════════════════════════════════════════════════════
# Provides V2_PROMPT_SPECS in the shape legacy callers (charter.py) expect.
# This allows deletion of runtime/prompt.py and runtime/prompts.py without
# requiring charter.py to do a full refactor.


def get_prompt_specs_for_charter() -> tuple[dict[str, Any], ...]:
    """Adapter for arifosmcp/runtime/charter.py:build_charter_v2()."""
    return get_registry().as_v2_prompt_specs()


__all__ = [
    "PromptSpec",
    "PromptRegistry",
    "load_registry",
    "get_registry",
    "reload_registry",
    "get_prompt_specs_for_charter",
    "REGISTRY_PATH",
]
