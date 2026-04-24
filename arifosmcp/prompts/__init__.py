"""
arifOS Prompts — Constitutional Context Injection
═════════════════════════════════════════════════

Registers canonical prompts:
  system      — Constitutional system context
  judge       — 888_JUDGE verdict engine context
  init        — 000_INIT session anchor context
  meta-skills — AGI→ASI→APEX structural capacities
"""
from __future__ import annotations

from fastmcp import FastMCP

from .system import register_system_prompt
from .judge import register_judge_prompt
from .init import register_init_prompt
from .meta_skills import register_meta_skill_prompts

CANONICAL_PROMPTS = ("system", "judge", "init", "rsi", "ortho", "epistemic", "governance", "entropy")


def register_prompts(mcp: FastMCP) -> list[str]:
    """Register all canonical prompts."""
    registered: list[str] = []
    registered.extend(register_system_prompt(mcp))
    registered.extend(register_judge_prompt(mcp))
    registered.extend(register_init_prompt(mcp))
    registered.extend(register_meta_skill_prompts(mcp))
    return registered
