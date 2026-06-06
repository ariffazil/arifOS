# Runtime prompt registry — must match arifosmcp.prompts.CANONICAL_PROMPTS
# 2026-06-04: AAA Trinity upgrade — 2 gateways (000+999) + 3 lanes (111/444/888)
CANONICAL_PROMPTS = (
    "000_init",
    "111_agi",
    "444_asi",
    "888_apex",
    "999_seal",
)

V2_PROMPT_SPECS = (
    {
        "name": "000_init",
        "description": "000_INIT — Session anchor and constitutional gateway. "
        "Identity binding (L11), entropy baseline, session manifest, F1-L13 confirmation.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "111_agi",
        "description": "111_AGI — Tactical intelligence (AGI lane, stages 111-555). "
        "PROPOSE. Abstraction + abduction + synthesis. EVOI discipline. C_dark guard.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "444_asi",
        "description": "444_ASI — Strategic judgment (ASI lane, stages 666-888). "
        "JUDGE. Attestation chain + F1-L13 floor-by-floor + orthogonal transfer + deliberation.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "888_apex",
        "description": "888_APEX — Authority resolution (APEX lane, stages 888-999). "
        "AUTHORIZE. Governance separation + generality test + verdict verification + pre-forge checklist.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "999_seal",
        "description": "999_SEAL — Vault closure and constitutional exit. "
        "Golden path verification + actor chain + evidence chain + floor compliance + VAULT999 write.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
)


def register_v2_prompts(mcp):
    from arifosmcp.prompts import register_prompts

    return register_prompts(mcp)


def register_v2_tools(mcp, **kwargs):
    return []
