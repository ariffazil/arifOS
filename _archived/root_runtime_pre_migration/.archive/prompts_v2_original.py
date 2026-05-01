"""
arifosmcp/runtime/prompts_v2.py — arifOS MCP v2 Prompt Templates

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
        "default_tools": ["arifos.v2.route", "arifos.v2.sense", "arifos.v2.mind", "arifos.v2.heart", "arifos.v2.judge"],
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
        "default_tools": ["arifos.v2.heart", "arifos.v2.judge"],
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
        "default_tools": ["arifos.v2.route", "arifos.v2.ops", "arifos.v2.judge"],
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
        "default_tools": ["arifos.v2.route"],
        "tool_choice": "auto",
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
1. arifos.v2.route — Determine correct metabolic lane
2. arifos.v2.sense — Ground in physical reality, verify facts
3. arifos.v2.mind — Structured reasoning with uncertainty bands
4. arifos.v2.heart — Safety critique and adversarial review
5. arifos.v2.judge — Final constitutional verdict

For each step:
- Record the tool call
- Note uncertainty (Ω₀) and clarity (ΔS) metrics
- Flag any floor violations

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
1. arifos.v2.heart — Identify ethical risks, dignity violations
2. arifos.v2.judge — Constitutional verdict

Report:
- floors_violated: list of F1-F13 violations found
- severity: CRITICAL | HIGH | MEDIUM | LOW
- remediation: required actions
- audit_hash: unique identifier for this audit
"""


def _execution_planning_prompt(task: str, constraints: dict | None = None) -> str:
    """Execution planning with cost estimation."""
    constraints_str = f"\nConstraints: {constraints}" if constraints else ""
    return f"""You are planning safe execution of a task.

Task: {task}{constraints_str}

Execute:
1. arifos.v2.route — Determine execution lane
2. arifos.v2.ops — Calculate thermodynamic costs, entropy
3. arifos.v2.judge — Pre-execution constitutional approval

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

Use arifos.v2.route only if constitutional risk detected.
Otherwise answer immediately.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

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

    registered = ["constitutional.analysis", "governance.audit", "execution.planning", "minimal.response"]
    logger.info(f"Registered {len(registered)} v2 prompts: {registered}")
    return registered


__all__ = [
    "V2_PROMPT_SPECS",
    "register_v2_prompts",
    "_constitutional_analysis_prompt",
    "_governance_audit_prompt",
    "_execution_planning_prompt",
    "_minimal_response_prompt",
]
