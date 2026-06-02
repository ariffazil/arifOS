"""Canonical prompt registry for arifOS MCP."""

from __future__ import annotations

from arifosmcp.prompts import register_prompts

__all__ = ["CANONICAL_PROMPTS", "register_prompts", "V2_PROMPT_SPECS", "register_v2_prompts"]

CANONICAL_PROMPTS = (
    "system",
    "judge",
    "init",
    "888_deliberation",
    "rsi",
    "ortho",
    "epistemic",
    "governance",
    "entropy",
)

V2_PROMPT_SPECS = (
    {
        "name": "system",
        "description": "Constitutional system context — arifOS F1-F13 governance floor",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "judge",
        "description": "888_JUDGE verdict engine context — deliberative decision protocol",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "init",
        "description": "000_INIT session anchor context — temporal + identity grounding",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "888_deliberation",
        "description": "APEX deliberation ritual — prepares a sovereign judgment case",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "rsi",
        "description": "Recursive Self-Improvement meta-skill — AGI reflection protocol",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "ortho",
        "description": "Orthogonal correction meta-skill — drift detection and correction",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "epistemic",
        "description": "Epistemic hygiene meta-skill — uncertainty and confidence framing",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "governance",
        "description": "Governance awareness meta-skill — constitutional floor context",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "entropy",
        "description": "Entropy management meta-skill — disorder detection and ordering",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
)


def register_v2_prompts(mcp):
    """Stub — delegate to register_prompts."""
    from arifosmcp.prompts import register_prompts

    return register_prompts(mcp)
