# Runtime prompt registry — must match arifosmcp.prompts.CANONICAL_PROMPTS
# Auto-synced with prompts/__init__.py on 2026-06-04 (RSI upgrade)

CANONICAL_PROMPTS = (
    "111_abstraction",
    "222_attestation",
    "333_abduction",
    "444_orthogonal",
    "555_generality",
)

# Prompt specs for public_registry.py introspection
V2_PROMPT_SPECS = (
    {
        "name": "111_abstraction",
        "description": "111_ABSTRACTION — Reduce complexity to essential structure (SENSE stage). "
        "6-level abstraction ladder, identity preservation, thermodynamic compression, F10 ontology.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "222_attestation",
        "description": "222_ATTESTATION — Bind claims to evidence; escape the Gödel Lock (EVIDENCE stage). "
        "8-step attestation chain, truth taxonomy, witness triad, F02/F03/F11/F12 compliance.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "333_abduction",
        "description": "333_ABDUCTION — Generate and rank competing explanations (MIND stage). "
        "7-step abduction cycle, N≥3 hypotheses, C_dark integration, active falsification.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "444_orthogonal",
        "description": "444_ORTHOGONAL — Transfer structure across unrelated domains (HEART stage). "
        "7-step transfer protocol, Ω_ortho coefficient, cross-domain archetypes, F10 ontology guard.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "555_generality",
        "description": "555_GENERALITY — Universal principles; domain independence (ROUTE/MEMORY stage). "
        "5-level generality ladder, 6 tests (domain/scale/time/adversary/inversion/minimality).",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
)


def register_v2_prompts(mcp):
    """Delegate to canonical prompt registration."""
    from arifosmcp.prompts import register_prompts

    return register_prompts(mcp)


def register_v2_tools(mcp, **kwargs):
    """Stub — use register_tools from runtime/tools.py instead."""
    return []
