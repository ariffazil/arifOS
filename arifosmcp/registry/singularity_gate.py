"""Prompt singularity checks for canonical identity, expiry, and authority."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from arifosmcp.registry.prompt_registry import PromptRegistry, get_registry

EXPECTED_CANONICAL_PROMPTS = (
    "🌱 BOOT",
    "🌊 WITNESS",
    "🧠 REASON",
    "⚖ MARUAH",
    "🔍 PREFLIGHT",
    "🔒 JUDGE",
    "🔥 FORGE",
    "💎 SEAL",
    "🌀 SABAR",
    "📜 REPLY",
)

REFERENCE_ONLY_DOCS = (
    "README.md",
    "AGENTS.md",
    "system-prompts.yaml",
    "execution-controller.py",
    "A-ARCHITECT.md",
    "A-ENGINEER.md",
    "A-AUDITOR.md",
    "A-VALIDATOR.md",
    "A-ORCHESTRATOR.md",
    "accountability-matrix.yaml",
    "agent-identity.yaml",
    "capability.charter.yaml",
    "event-bus.yaml",
)

FORBIDDEN_RUNTIME_TEXT = (
    "You are 888_JUDGE",
    "You are 999_SEAL",
    "human role is reduced to",
    "You are the autonomous middle",
    "Call arif_act",
    "Call arif_heart_critique",
    "Call forge_vault",
)


def validate_prompt_singularity(
    *,
    registry: PromptRegistry | None = None,
    today: date | None = None,
    repo_root: Path | None = None,
) -> list[str]:
    """Return invariant violations. An empty list means the gate passes."""
    registry = registry or get_registry()
    today = today or date.today()
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    violations: list[str] = []

    if registry.canonical_sequence != EXPECTED_CANONICAL_PROMPTS:
        violations.append(
            "canonical_sequence must equal the 10-prompt sigil surface: "
            f"{registry.canonical_sequence!r}"
        )
    if set(registry.specs) != set(EXPECTED_CANONICAL_PROMPTS):
        violations.append("registry prompts must contain exactly the 10 canonical prompt IDs")

    for alias in registry.aliases.values():
        try:
            removal_epoch = date.fromisoformat(alias.removal_epoch)
        except ValueError:
            violations.append(f"alias {alias.id!r} has invalid removal_epoch")
            continue
        if removal_epoch <= today:
            violations.append(
                f"alias {alias.id!r} expired on {alias.removal_epoch}; remove it from runtime"
            )

    from arifosmcp.prompts import CANONICAL_PROMPTS

    expected_live = set(registry.canonical_sequence) | set(registry.aliases)
    if set(CANONICAL_PROMPTS) != expected_live:
        missing = sorted(expected_live - set(CANONICAL_PROMPTS))
        extra = sorted(set(CANONICAL_PROMPTS) - expected_live)
        violations.append(f"runtime prompt tuple drift: missing={missing}, extra={extra}")

    runtime_paths = (
        repo_root / "arifosmcp/prompts/__init__.py",
        repo_root / "arifosmcp/runtime/fastmcp_ext/prompts.py",
    )
    runtime_text = "\n".join(path.read_text(encoding="utf-8") for path in runtime_paths)
    for alias in registry.aliases.values():
        name_marker = f'name="{alias.id}"'
        start = runtime_text.find(name_marker)
        if start < 0:
            violations.append(f"runtime is missing alias decorator {alias.id!r}")
            continue
        metadata = runtime_text[start : start + 1_500]
        if f'"deprecated_alias_of": "{alias.canonical_id}"' not in metadata:
            violations.append(f"runtime alias {alias.id!r} does not target {alias.canonical_id!r}")
        if f'"removal_epoch": "{alias.removal_epoch}"' not in metadata:
            violations.append(
                f"runtime alias {alias.id!r} does not match removal epoch {alias.removal_epoch}"
            )

    for path in runtime_paths:
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_RUNTIME_TEXT:
            if forbidden in text:
                violations.append(f"{path.relative_to(repo_root)} contains {forbidden!r}")

    docs_root = repo_root / "docs/agents"
    for relative in REFERENCE_ONLY_DOCS:
        path = docs_root / relative
        prefix = path.read_text(encoding="utf-8")[:500]
        if "REFERENCE-ONLY" not in prefix or "NOT RUNTIME AUTHORITY" not in prefix:
            violations.append(f"docs/agents/{relative} lacks the reference-only authority banner")

    return violations


def assert_prompt_singularity(
    *,
    registry: PromptRegistry | None = None,
    today: date | None = None,
    repo_root: Path | None = None,
) -> None:
    """Raise with a stable, CI-friendly report when any invariant fails."""
    violations = validate_prompt_singularity(
        registry=registry,
        today=today,
        repo_root=repo_root,
    )
    if violations:
        raise AssertionError("Prompt singularity gate failed:\n- " + "\n- ".join(violations))


__all__ = [
    "EXPECTED_CANONICAL_PROMPTS",
    "assert_prompt_singularity",
    "validate_prompt_singularity",
]
