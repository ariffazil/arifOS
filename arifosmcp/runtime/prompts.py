# Runtime prompt registry — must match arifosmcp.prompts.CANONICAL_PROMPTS
# 2026-06-26: RSI fix — critique (555) before judge (666). Golden path order.
CANONICAL_PROMPTS = (
    "arifosmcp_loop_engineer",
    "000_init",
    "111_sense",
    "333_reason",
    "555_critique",
    "666_judge",
    "777_forge",
    "999_seal",
)

V2_PROMPT_SPECS = (
    {
        "name": "arifosmcp_loop_engineer",
        "description": "Entry guard. Intent classification + session state initialization.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "000_init",
        "description": "000_INIT — THE ANCHOR. Identity binding, reality grounding, floor acceptance. Cross-session memory.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "111_sense",
        "description": "111_SENSE — THE WITNESS. Open observation, pattern detection, evidence gathering with epistemic labels. F2 computed.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "333_reason",
        "description": "333_REASON — THE MIND. Abstraction, abduction (N≥3 hypotheses), synthesis, proposal. F7 computed.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "555_critique",
        "description": "555_CRITIQUE — THE MIRROR. Consequence scan, blast radius, perspective shift, dignity check, alternatives. F5/F6 computed.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "666_judge",
        "description": "666_JUDGE — THE GATE. Four tests (Truth, Reversibility, Dignity, Universality) + F1-F13 floor matrix. SEAL/SABAR/HOLD/VOID.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "777_forge",
        "description": "777_FORGE — THE HAMMER. Structural enforcement gate. Execute, verify, rollback. Blocked without 666 SEAL + 555 FORGE_READY.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "999_seal",
        "description": "999_SEAL — THE RECORD. Golden path verification, immutable VAULT999 write, assumption ledger. IRREVERSIBLE.",
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
