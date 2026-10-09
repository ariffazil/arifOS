from __future__ import annotations

from dataclasses import replace
from datetime import date

from arifosmcp.registry import get_registry
from arifosmcp.registry.prompt_registry import PromptAliasSpec
from arifosmcp.registry.singularity_gate import (
    EXPECTED_CANONICAL_PROMPTS,
    validate_prompt_singularity,
)


def test_current_prompt_surface_is_singular() -> None:
    """The live registry, runtime tuple, and docs must agree with zero drift."""
    assert validate_prompt_singularity(today=date(2026, 9, 18)) == []


def test_registry_matches_runtime_canonical_prompts() -> None:
    """Registry canonical surface is derived from, and equals, the runtime tuple."""
    registry = get_registry()
    assert registry.canonical_sequence == EXPECTED_CANONICAL_PROMPTS
    assert set(registry.specs) == set(EXPECTED_CANONICAL_PROMPTS)


def test_expired_alias_fails_gate() -> None:
    """A declared alias past its removal epoch must be flagged (synthetic fixture)."""
    registry = get_registry()
    expired_alias = PromptAliasSpec(
        id="999_legacy_probe",
        canonical_id=EXPECTED_CANONICAL_PROMPTS[0],
        removal_epoch="2026-07-23",
    )
    expired_registry = replace(
        registry,
        aliases={**registry.aliases, expired_alias.id: expired_alias},
    )

    violations = validate_prompt_singularity(
        registry=expired_registry,
        today=date(2026, 7, 24),
    )

    assert any(f"alias {expired_alias.id!r} expired" in violation for violation in violations)


def test_compatibility_specs_are_registry_backed() -> None:
    from arifosmcp.specs.prompt_specs import PROMPT_NAMES

    assert PROMPT_NAMES == get_registry().canonical_sequence
