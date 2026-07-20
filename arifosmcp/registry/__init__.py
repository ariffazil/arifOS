"""
arifOS Registry Package — single source of truth for prompt metadata.

Forged 2026-07-07 by FORGE (000Ω) under F13 SOVEREIGN directive.
Consolidates: runtime/prompts.py, runtime/prompt.py (deleted post-migration).

DITEMPA BUKAN DIBERI — Registry is forged, not given.
"""

from .prompt_registry import (
    REGISTRY_PATH,
    PromptRegistry,
    PromptSpec,
    get_prompt_specs_for_charter,
    get_registry,
    load_registry,
    reload_registry,
)

__all__ = [
    "PromptSpec",
    "PromptRegistry",
    "load_registry",
    "get_registry",
    "reload_registry",
    "get_prompt_specs_for_charter",
    "REGISTRY_PATH",
]
