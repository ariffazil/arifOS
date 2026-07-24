from __future__ import annotations

from dataclasses import replace
from datetime import date

from arifosmcp.registry import get_registry
from arifosmcp.registry.singularity_gate import (
    EXPECTED_CANONICAL_PROMPTS,
    validate_prompt_singularity,
)


def test_current_prompt_surface_is_singular() -> None:
    assert validate_prompt_singularity(today=date(2026, 7, 24)) == []


def test_registry_has_exactly_ten_canonical_prompts() -> None:
    registry = get_registry()
    assert registry.canonical_sequence == EXPECTED_CANONICAL_PROMPTS
    assert set(registry.specs) == set(EXPECTED_CANONICAL_PROMPTS)


def test_expired_alias_fails_gate() -> None:
    registry = get_registry()
    alias_id = next(iter(registry.aliases))
    expired_alias = replace(registry.aliases[alias_id], removal_epoch="2026-07-23")
    expired_registry = replace(
        registry,
        aliases={**registry.aliases, alias_id: expired_alias},
    )

    violations = validate_prompt_singularity(
        registry=expired_registry,
        today=date(2026, 7, 24),
    )

    assert any(f"alias {alias_id!r} expired" in violation for violation in violations)


def test_compatibility_specs_are_registry_backed() -> None:
    from arifosmcp.specs.prompt_specs import PROMPT_NAMES

    assert PROMPT_NAMES == get_registry().canonical_sequence
