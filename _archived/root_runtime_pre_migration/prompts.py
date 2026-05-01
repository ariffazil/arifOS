"""
arifos/runtime/prompts.py — arifOS MCP Prompt Templates

Prompts are structured reasoning contracts.
They guide the model, define workflows, prevent misuse.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# V2 PROMPT DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

V2_PROMPT_SPECS: list[dict[str, Any]] = [
    {
        "name": "constitutional.analysis",
        "description": "Run full constitutional reasoning pipeline through sense → mind → heart → judge.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query to analyze constitutionally"},
                "risk_tier": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
                "context": {"type": "string", "description": "Additional context"},
            },
            "required": ["query"],
        },
        "default_tools": ["arifos.route", "arifos.sense", "arifos.mind", "arifos.heart", "arifos.judge"],
        "tool_choice": "auto",
    },
    {
        "name": "governance.audit",
        "description": "Evaluate output for constitutional floor violations. Compliance-grade review.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to audit"},
                "standard": {"type": "string", "enum": ["SOC2", "ISO42001", "internal"], "default": "internal"},
            },
            "required": ["content"],
        },
        "default_tools": ["arifos.heart", "arifos.judge"],
        "tool_choice": "required",
    },
    {
        "name": "execution.planning",
        "description": "Generate execution plan with cost estimation and judge approval.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to plan"},
                "constraints": {"type": "object", "description": "Budget, time, resource constraints"},
            },
            "required": ["task"],
        },
        "default_tools": ["arifos.route", "arifos.ops", "arifos.judge"],
        "tool_choice": "auto",
    },
    {
        "name": "minimal.response",
        "description": "Return answer directly, skip verbose reasoning. Latency-optimized.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Direct question"},
                "max_tokens": {"type": "integer", "default": 500},
            },
            "required": ["query"],
        },
        "default_tools": ["arifos.route"],
        "tool_choice": "auto",
    },
    # ─────────────────────────────────────────────────────────────────────────
    # AGI Reply Protocol v3 — DITEMPA EDITION
    # Stable-prefix cacheable. Schema → arifos://reply/schemas
    # Context pack → arifos://reply/context-pack
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "reply_protocol_v3",
        "description": (
            "AGI Reply Protocol v3 — DITEMPA EDITION. "
            "Dual-axis governed reply: human-cognitive OR agent-machine. "
            "Runs: memory → sense → mind → heart → ops → judge → [vault/forge]. "
            "Emits: TO/CC/TITLE/KEY_CONTEXT header, RACI block, STEP -1 to STEP 3, "
            "and SEAL signoff. Load arifos://reply/schemas once; use DELTA mode by default."
        ),
        "input_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "User query or agent task",
                },
                "session_id": {"type": "string"},
                "recipient": {
                    "type": "string",
                    "enum": ["human", "agent", "auto"],
                    "default": "auto",
                    "description": "auto → classify via arifos.sense; ambiguous → human + agent block",
                },
                "depth": {
                    "type": "string",
                    "enum": ["SURFACE", "ENGINEER", "ARCHITECT"],
                    "default": "ENGINEER",
                },
                "compression": {
                    "type": "string",
                    "enum": ["FULL", "DELTA", "SIGNAL_ONLY"],
                    "default": "DELTA",
                    "description": "FULL=handoff/start, DELTA=normal turns, SIGNAL_ONLY=sub-agent hops",
                },
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "prior_state": {
                    "type": "string",
                    "description": "Compressed one-line prior context (omit on first turn)",
                },
            },
        },
        "default_tools": [
            "arifos.memory",
            "arifos.sense",
            "arifos.mind",
            "arifos.heart",
            "arifos.ops",
            "arifos.judge",
            "arifos.vault",
        ],
        "tool_choice": "auto",
        "resources": [
            "arifos://reply/schemas",       # stable prefix — load once, cache
            "arifos://reply/context-pack",  # delta — load every turn
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _constitutional_analysis_prompt(query: str, risk_tier: str = "medium", context: str = "") -> str:
    """Full constitutional reasoning pipeline prompt."""
    ctx = f"\nContext: {context}" if context else ""
    return f"""You are running constitutional analysis on the following query.

Query: {query}{ctx}
Risk Tier: {risk_tier}

Execute this pipeline:
1. arifos.route — Determine correct metabolic lane
2. arifos.sense — Ground in physical reality, verify facts
3. arifos.mind — Structured reasoning with uncertainty bands
4. arifos.heart — Safety critique and adversarial review
5. arifos.judge — Final constitutional verdict

For each step:
- Record the tool call
- Note uncertainty (Ω₀) and clarity (ΔS) metrics
- Flag any floor violations
- If GEOX/domain evidence is present, preserve structured fields such as claim_tag, disagreement_band,
  p10/p50/p90, charge_probability, and vault_receipt. Do not collapse them into a single deterministic claim.

Final output must include:
- verdict: SEAL | PARTIAL | VOID | HOLD
- floors_triggered: list of F1-F13 triggered
- confidence: 0.0-1.0
- reasoning_class: constitutional | safety | uncertainty
"""


def _governance_audit_prompt(content: str, standard: str = "internal") -> str:
    """Compliance audit prompt."""
    std_map = {
        "SOC2": "Trust Services Criteria (Security, Availability)",
        "ISO42001": "AI Management System standards",
        "internal": "Internal constitutional standards",
    }
    return f"""You are conducting a governance audit.

Standard: {std_map.get(standard, standard)}
Content to audit:
---
{content}
---

Execute:
1. arifos.heart — Identify ethical risks, dignity violations
2. arifos.judge — Constitutional verdict

Report:
- floors_violated: list of F1-F13 violations found
- severity: CRITICAL | HIGH | MEDIUM | LOW
- remediation: required actions
- audit_hash: unique identifier for this audit
- If the content includes GEOX/domain evidence, explicitly report posterior breadth, disagreement spread,
  and any probabilistic-vs-deterministic mismatch as audit findings.
"""


def _execution_planning_prompt(task: str, constraints: dict | None = None) -> str:
    """Execution planning with cost estimation."""
    constraints_str = f"\nConstraints: {constraints}" if constraints else ""
    return f"""You are planning safe execution of a task.

Task: {task}{constraints_str}

Execute:
1. arifos.route — Determine execution lane
2. arifos.ops — Calculate thermodynamic costs, entropy
3. arifos.judge — Pre-execution constitutional approval

Output execution plan:
- steps: ordered list of operations
- estimated_cost: resource requirements
- risk_mitigation: safety measures
- judge_approval: SEAL required to proceed
- rollback_plan: reversibility strategy
"""


def _minimal_response_prompt(query: str, max_tokens: int = 500) -> str:
    """Direct response, minimal reasoning."""
    return f"""Answer directly and concisely.

Query: {query}
Max length: {max_tokens} tokens

Use arifos.route only if constitutional risk detected.
Otherwise answer immediately.
"""


def _reply_protocol_v3_prompt(
    query: str,
    recipient: str = "auto",
    depth: str = "ENGINEER",
    compression: str = "DELTA",
    risk_tier: str = "medium",
    prior_state: str = "",
) -> str:
    """
    AGI Reply Protocol v3 — DITEMPA EDITION.
    Stable-prefix cacheable prompt. Defines the full dual-axis reply contract.
    Schema lives in arifos://reply/schemas.
    Session state lives in arifos://reply/context-pack.
    """
    prior_block = f"\nPRIOR_STATE: {prior_state}" if prior_state else "\nPRIOR_STATE: NONE (first turn)"
    return f"""You are operating under AGI REPLY PROTOCOL v3 — DITEMPA EDITION.

Load schema from: arifos://reply/schemas
Load session state from: arifos://reply/context-pack
{prior_block}
RECIPIENT: {recipient} | DEPTH: {depth} | COMPRESSION: {compression} | RISK_TIER: {risk_tier}

━━━ QUERY ━━━
{query}
━━━━━━━━━━━━

EXECUTION PIPELINE (call in order):

STEP -1 — CONTEXT STATE (silent, before answering)
  → arifos.memory(query="{query}", mode="vector_query")
  → Output one line: PRIOR_STATE: <compressed> | DELTA: <what changed> | DEPTH: {depth}

STEP 0 — RECIPIENT DETECTION (silent)
  → arifos.sense(query="{query}", mode="governed")
  → If recipient=auto: classify from sense output
  → Rule: ambiguous → treat as human PLUS append agent block at end
  → Preserve any domain_evidence packet from GEOX; never rewrite claim_tag / posterior bands into freehand prose.

STEP 0b — COMPUTE τ (silent)
  → τ = (FACT_count×1.0 + ASSUME_count×0.7 + UNKNOWN_count×0.2) / total_reasoning_steps
  → Source evidence from arifos.sense + arifos.mind outputs

STEP 1 — VERDICT LINE (first visible output)
  Format: [FLOOR_TAGS] VERDICT_TOKEN τ=N.NN — <one concrete statement>
  Tokens: CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN | CONFLICT | 888 HOLD
  Floor tags (prepend when triggered):
    [F1 AMANAH]    — action deletes/overwrites data
    [F2 TRUTH]     — claim lacks evidence chain
    [F7 ADIL]      — affects another's rights
    [F9 ANTI-HANTU] — could manipulate or deceive
    [F13 SOVEREIGN] — final decision belongs to Arif

STEP 2A — DIRECT ANSWER
  → arifos.mind(query="{query}", mode="reason")
  → 2-5 bullets. Strongest conclusion first. No apologies.
  → Human: plain English. Agent: compact key:value or JSON-compatible prose.

STEP 2B — REASONING SNAPSHOT
  → arifos.mind output + arifos.heart(mode="critique")
  → 3-7 bullets tagged: FACT | ASSUME | RISK | DELTA | UNKNOWN | DERIVE | VERIFY
  → Prefer concrete numbers over vague language ("~40ms p99" not "fast")
  → Human recipients: expose compressed snapshot only (not raw chain)

STEP 2C — ACTION / OUTPUT
  → If judge verdict = SEAL: arifos.forge(action=..., judge_verdict="SEAL")
  → Human: code first, then numbered steps, then Markdown tables
  → Agent: structured action block:
      ACTION: <tool or step>
      PARAMS: {{...}}
      CONFIDENCE: 0.0-1.0
      REVERSIBLE: YES | NO | PARTIAL
      ESCALATE_IF: <condition requiring human approval>

STEP 2D — RESOURCE ENVELOPE (agent recipients only)
  → arifos.ops(action="{query}", mode="cost")
  → Emit:
      COMPRESSION_MODE: {compression}
      TOKENS_ESTIMATED: ~N
      CACHE_STABLE_PREFIX: YES | NO
      PARALLEL_OK: YES | NO
      NEXT_AGENT: <agent_id or null>

STEP 3 — CONSTITUTIONAL GUARD
  → arifos.heart(mode="critique") + arifos.judge(risk_tier="{risk_tier}")
  → If [F1] or [F13] triggered → verdict MUST be 888 HOLD:
      GOVERNANCE TRACE:
        FLOORS_TRIGGERED: [...]
        VERDICT: 888_HOLD
        ESCALATE_TO: human:arif
        AUDIT_REF: <arifos.vault reference>
  → Never self-approve 888 HOLD.
  → Call arifos.vault for any SEAL or HOLD verdict.
  → GEOX/domain evidence with disagreement_band > 0.20, overly broad posterior spread, timing conflict,
    or missing receipt for consequential claims must bias toward HOLD or explicit qualification.

━━━ REPLY HEADER (prefix every response) ━━━
TO: <primary recipient>
CC: <comma-separated — include arifos.vault for any SEAL/HOLD>
TITLE: <verdict token + one-line statement>
KEY CONTEXT: <1-2 essential sentences the recipient needs to act>

━━━ RACI ━━━
R (Responsible): <tool that forged this — e.g. arifos.mind or arifos.forge>
A (Accountable): arifos.judge + human:arif
C (Consulted):   <tools called — e.g. arifos.heart, arifos.ops, arifos.memory>
I (Informed):    <arifos.vault + any CC agents>

━━━ SEAL SIGNOFF (last line of every response) ━━━
FORGED_BY: <agent_id>
JUDGE_VERDICT: <SEAL|PARTIAL|HOLD|VOID>
τ: <score>
FLOORS_PASSED: <list>
AUDIT_HASH: sha256(TITLE + timestamp + forged_by + judge_verdict)
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE

━━━ STYLE CONSTANTS ━━━
- Tone: engineer-to-engineer. Dense. No small talk.
- Multiple options: name 2-3, state choosing condition for each.
- Never fabricate facts: use UNKNOWN / ESTIMATE / HYPOTHESIS.
- Agent-to-agent: strip narrative, maximise signal. Think diff+plan not essay.
- On human prompts interpreted for another agent: paraphrase intent first, then act.
- Compression default: {compression} (switch to FULL on handoff or ambiguity)
"""


def _a_forge_govern_prompt(task: str, mode: str = "check_governance") -> str:
    """A-FORGE governance check prompt — routes task through F3/F6/F9 TypeScript engine."""
    mode_desc = {
        "check_governance": "Run F3 InputClarity + F6 HarmDignity + F9 Injection checks only. Return per-floor verdicts.",
        "run": "Run full governed agent task (explore profile, mock LLM). Governance gates run first.",
        "health": "Return A-FORGE server health and F1–F13 floor implementation status.",
    }.get(mode, mode)

    return f"""You are routing a task through the A-FORGE constitutional engine.

Task: {task}
Mode: {mode} — {mode_desc}

Steps:
1. Call arifos.forge_bridge(task="{task}", mode="{mode}") via HTTP POST to http://localhost:7071
   - For check_governance: POST /sense → returns F3/F6/F9 verdict per floor
   - For run: POST to forge_run endpoint
   - For health: GET /health

2. Interpret the result:
    - PASS → proceed; task cleared all governance floors
    - SABAR → F3 InputClarity blocked: task too vague or empty — request clarification
    - VOID → F6 HarmDignity or F9 Injection blocked: task contains harmful or injection pattern — escalate F13 HOLD
    - If GEOX/domain evidence accompanies the task, keep its probabilistic fields intact and route them into arifos_judge
      rather than summarizing away the spread.

3. If PASS and mode=run: record finalText and turnCount in the session context.

4. If any VOID verdict: trigger 888_HOLD (F13 Sovereign) — do not proceed without human approval.

Resource: arifos://a-forge/context (full tool schema and deployment info)
"""


def _a_forge_deploy_prompt(target: str = "local") -> str:
    """A-FORGE deployment guidance prompt."""
    if target == "docker":
        steps = """
1. Build: cd a-forge && npm run build
2. Start bridge: docker-compose up -d a-forge-bridge
3. Verify health: curl http://localhost:7071/health
4. Register MCP: the .mcp.json is already wired for Claude Desktop/Code"""
    elif target == "smithery":
        steps = """
1. Ensure smithery.yaml is correct (already present at a-forge/smithery.yaml)
2. Run: smithery publish a-forge/ (requires Smithery CLI)
3. Tools published: forge_check_governance, forge_health, forge_run"""
    else:  # local
        steps = """
1. Build: cd a-forge && npm install && npm run build
2. Start MCP stdio: npm run serve:mcp  (or node dist/src/mcp/server.js)
3. Start HTTP bridge: node dist/src/server.js  (port 7071)
4. Test governance: echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"forge_check_governance","arguments":{"task":"test"}}}' | node dist/src/mcp/server.js"""

    return f"""A-FORGE Deployment — Target: {target}
{steps}

Platform configs already present:
- Claude Desktop/Code: a-forge/.mcp.json
- Cursor: a-forge/.cursor/mcp.json
- OpenCode: a-forge/.opencode.json
- Smithery: a-forge/smithery.yaml
- Docker: a-forge/Dockerfile + a-forge/docker-compose.yml
- CI launcher: a-forge/.github/mcp/start-a-forge-stdio.sh

All 62 tests pass. Constitution: 11/13 floors implemented.
F3 InputClarity + F6 HarmDignity + F9 Injection gates are live in AgentEngine.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

# Legacy shim for backward compatibility
def register_prompts(mcp: FastMCP) -> list[str]:
    """Legacy prompt registration shim — delegates to register_v2_prompts."""
    return register_v2_prompts(mcp)


def register_v2_prompts(mcp: FastMCP) -> list[str]:
    """Register all v2 prompts on the MCP instance."""
    registered = []

    @mcp.prompt("constitutional.analysis")
    def constitutional_analysis(query: str, risk_tier: str = "medium", context: str = "") -> str:
        return _constitutional_analysis_prompt(query, risk_tier, context)

    @mcp.prompt("governance.audit")
    def governance_audit(content: str, standard: str = "internal") -> str:
        return _governance_audit_prompt(content, standard)

    @mcp.prompt("execution.planning")
    def execution_planning(task: str, constraints: str = "") -> str:
        # Parse constraints from JSON string if provided
        import json
        try:
            constraints_dict = json.loads(constraints) if constraints else None
        except json.JSONDecodeError:
            constraints_dict = None
        return _execution_planning_prompt(task, constraints_dict)

    @mcp.prompt("minimal.response")
    def minimal_response(query: str, max_tokens: int = 500) -> str:
        return _minimal_response_prompt(query, max_tokens)

    @mcp.prompt("reply_protocol_v3")
    def reply_protocol_v3(
        query: str,
        recipient: str = "auto",
        depth: str = "ENGINEER",
        compression: str = "DELTA",
        risk_tier: str = "medium",
        prior_state: str = "",
    ) -> str:
        return _reply_protocol_v3_prompt(
            query=query,
            recipient=recipient,
            depth=depth,
            compression=compression,
            risk_tier=risk_tier,
            prior_state=prior_state,
        )

    @mcp.prompt("a-forge.govern")
    def a_forge_govern(task: str, mode: str = "check_governance") -> str:
        return _a_forge_govern_prompt(task, mode)

    @mcp.prompt("a-forge.deploy")
    def a_forge_deploy(target: str = "local") -> str:
        return _a_forge_deploy_prompt(target)

    registered = [
        "constitutional.analysis",
        "governance.audit",
        "execution.planning",
        "minimal.response",
        "reply_protocol_v3",
        "a-forge.govern",
        "a-forge.deploy",
    ]
    logger.info(f"Registered {len(registered)} v2 prompts: {registered}")
    return registered


__all__ = [
    "V2_PROMPT_SPECS",
    "register_v2_prompts",
    "_constitutional_analysis_prompt",
    "_governance_audit_prompt",
    "_execution_planning_prompt",
    "_a_forge_govern_prompt",
    "_a_forge_deploy_prompt",
    "_minimal_response_prompt",
    "_reply_protocol_v3_prompt",
]
