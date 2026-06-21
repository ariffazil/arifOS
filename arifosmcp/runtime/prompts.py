# Runtime prompt registry — must match arifosmcp.prompts.CANONICAL_PROMPTS
# 2026-06-21: APEX Theory upgrade — 7 prompts (000/111/333/555/666/777/999)
CANONICAL_PROMPTS = (
    "000_init",
    "111_sense",
    "333_reason",
    "555_judge",
    "666_critique",
    "777_forge",
    "999_seal",
)

V2_PROMPT_SPECS = (
    {
        "name": "000_init",
        "description": "000_INIT — Threshold. Identity binding, reality grounding, floor acceptance.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "111_sense",
        "description": "111_SENSE — Witness. Open observation, pattern detection, evidence gathering with epistemic labels.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "333_reason",
        "description": "333_REASON — Mind. Abstraction, abduction (N≥3 hypotheses), synthesis, proposal.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "555_judge",
        "description": "555_JUDGE — Constitutional evaluator. Truth, reversibility, dignity, universality tests. SEAL/SABAR/HOLD/VOID.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "666_critique",
        "description": "666_CRITIQUE — Pre-forge mirror. Consequence scan, blast radius, alternatives, ethical ground.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "777_forge",
        "description": "777_FORGE — Builder. Authorize, execute smallest reversible step, verify, rollback on failure.",
        "input_schema": {},
        "default_tools": [],
        "tool_choice": "auto",
    },
    {
        "name": "999_seal",
        "description": "999_SEAL — Closer. Golden path verification, immutable VAULT999 write. IRREVERSIBLE.",
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
