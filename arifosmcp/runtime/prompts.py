# Fix the runtime/prompts.py stub to have proper V2_PROMPT_SPECS

CANONICAL_PROMPTS = (
    "arif_system",
    "arif_judge",
    "arif_init",
    "rsi",
    "ortho",
    "epistemic",
    "governance",
    "entropy",
)

# Proper prompt specs that public_registry.py expects
V2_PROMPT_SPECS = (
    {
        "name": "arif_system",
        "description": "Constitutional system context — arifOS F1-F13 governance floor",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "arif_judge",
        "description": "888_JUDGE verdict engine context — deliberative decision protocol",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "arif_init",
        "description": "000_INIT session anchor context — temporal + identity grounding",
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


def register_v2_tools(mcp, **kwargs):
    """Stub — use register_tools from runtime/tools.py instead."""
    return []
