"""
arifOS MCP Tool Discovery Resource
═══════════════════════════════════════════════════════════════

Exposes tool discovery metadata as an MCP resource so LLMs can
find the right tool quickly.

DITEMPA BUKAN DIBERI — Discovered, not guessed.
"""

from __future__ import annotations

from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL DISCOVERY METADATA
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_DISCOVERY: dict[str, dict[str, Any]] = {
    "arif_init": {
        "use_when": "Starting a new conversation, initializing a session, or resuming a previous session.",
        "aliases": [
            "arif_session_init",
            "arifos_init",
            "session_init",
            "start_session",
            "begin_session",
        ],
        "keywords": ["start", "begin", "initialize", "session", "resume", "bootstrap"],
        "examples": [
            "Start a new session",
            "Initialize arifOS",
            "Begin a governed conversation",
            "Resume my previous session",
        ],
        "category": "session",
        "read_only": False,
    },
    "arif_observe": {
        "use_when": "Searching the web, fetching URLs, checking system vitals, or mapping a repository.",
        "aliases": ["arif_search", "arif_web_search", "search", "web_search"],
        "keywords": ["search", "web", "fetch", "url", "vitals", "health", "repo", "map", "ingest"],
        "examples": [
            "Search the web for X",
            "Fetch this URL",
            "Check system vitals",
            "Map the repository",
        ],
        "category": "observation",
        "read_only": True,
    },
    "arif_fetch": {
        "use_when": "Fetching content from a specific URL to read its contents.",
        "aliases": ["fetch_url", "get_url", "read_url", "download_url"],
        "keywords": ["fetch", "url", "page", "download", "read", "content"],
        "examples": [
            "Fetch this page: https://example.com",
            "Get the content of this URL",
            "Read this webpage",
        ],
        "category": "observation",
        "read_only": True,
    },
    "arif_explore": {
        "use_when": "Multimodal reality observation — comprehensive sensing across web, URL, geospatial, entropy.",
        "aliases": ["arif_sense", "arif_multimodal", "explore", "sense"],
        "keywords": ["explore", "sense", "multimodal", "observe", "compass", "atlas", "entropy"],
        "examples": [
            "Explore this topic comprehensively",
            "Get a multimodal view",
            "Check entropy of session",
        ],
        "category": "observation",
        "read_only": True,
    },
    "arif_think": {
        "use_when": "Analyzing, planning, reflecting, verifying, or critiquing something.",
        "aliases": [
            "arif_reason",
            "arif_analyze",
            "arif_plan",
            "think",
            "reason",
            "analyze",
            "plan",
        ],
        "keywords": [
            "think",
            "reason",
            "analyze",
            "plan",
            "reflect",
            "verify",
            "critique",
            "strategy",
        ],
        "examples": [
            "Think about this problem",
            "Analyze the trade-offs",
            "Create a plan",
            "Reflect on what we learned",
        ],
        "category": "reasoning",
        "read_only": True,
    },
    "arif_critique": {
        "use_when": "Before irreversible, sensitive, or dignity-affecting actions. Assess ethical risks.",
        "aliases": ["arif_ethical_check", "arif_risk_assess", "critique"],
        "keywords": [
            "critique",
            "ethical",
            "risk",
            "dignity",
            "impact",
            "sensitive",
            "irreversible",
        ],
        "examples": [
            "Is this action ethical?",
            "What are the risks?",
            "Check dignity impact",
            "Red-team this proposal",
        ],
        "category": "reasoning",
        "read_only": True,
    },
    "arif_route": {
        "use_when": "You know what you want but not which tool or organ to call.",
        "aliases": ["arif_delegate", "arif_forward", "route", "delegate"],
        "keywords": ["route", "organ", "delegate", "forward", "which", "where", "dispatch"],
        "examples": [
            "Route this to the right organ",
            "Which organ handles geology?",
            "Delegate this task",
        ],
        "category": "routing",
        "read_only": True,
    },
    "arif_triage": {
        "use_when": "Before executing significant actions. Check for holds or blocks.",
        "aliases": ["arif_preflight", "arif_check", "triage", "preflight"],
        "keywords": ["triage", "preflight", "check", "status", "hold", "block", "lane"],
        "examples": [
            "Check if we can proceed",
            "Any holds on this action?",
            "Run preflight check",
        ],
        "category": "routing",
        "read_only": True,
    },
    "arif_bridge_connect": {
        "use_when": "You know exactly which organ and tool to call. Direct organ tool call.",
        "aliases": [
            "arif_call_organ",
            "arif_direct_call",
            "bridge_connect",
            "call_tool",
            "arif_bridge",
        ],
        "keywords": ["bridge", "organ", "direct", "call", "geox", "wealth", "well", "forge"],
        "examples": [
            "Call geox_basin on GEOX",
            "Direct call to WEALTH organ",
            "Bridge to WELL for vitality check",
        ],
        "category": "routing",
        "read_only": False,
    },
    "arif_memory": {
        "use_when": "Storing, retrieving, or managing memory across the federation.",
        "aliases": ["arif_remember", "arif_recall", "memory", "remember", "recall"],
        "keywords": ["memory", "remember", "recall", "forget", "store", "attest", "promote"],
        "examples": [
            "Remember this for later",
            "What do we know about X?",
            "Forget this information",
        ],
        "category": "memory",
        "read_only": False,
    },
    "arif_judge": {
        "use_when": "A decision needs arbitration and binding judgment.",
        "aliases": ["arif_verdict", "arif_decide", "judge", "verdict", "decide"],
        "keywords": ["judge", "verdict", "decide", "approve", "reject", "seal", "hold"],
        "examples": [
            "Judge this proposal",
            "Issue a verdict",
            "Should we proceed?",
        ],
        "category": "judgment",
        "read_only": True,
    },
    "arif_seal": {
        "use_when": "Final, irreversible records that must be preserved forever.",
        "aliases": ["arif_finalize", "arif_audit_seal", "seal", "finalize"],
        "keywords": ["seal", "finalize", "immutable", "audit", "ledger", "permanent"],
        "examples": [
            "Seal this verdict",
            "Make this permanent",
            "Write to audit ledger",
        ],
        "category": "judgment",
        "read_only": False,
    },
    "arif_forge": {
        "use_when": "After judge has issued a SEAL verdict and you need to execute.",
        "aliases": ["arif_execute", "arif_build", "arif_deploy", "forge", "execute", "build"],
        "keywords": ["forge", "execute", "build", "deploy", "run", "change", "mutate"],
        "examples": [
            "Execute the approved plan",
            "Build and deploy",
            "Forge this change",
        ],
        "category": "execution",
        "read_only": False,
    },
    "arif_compose": {
        "use_when": "Ready to formulate the final answer for the user. Call LAST.",
        "aliases": ["arif_respond", "arif_format", "arif_answer", "compose", "respond"],
        "keywords": ["compose", "format", "respond", "answer", "final", "output"],
        "examples": [
            "Compose the final answer",
            "Format the response",
            "Present the findings",
        ],
        "category": "composition",
        "read_only": True,
    },
    "arif_measure": {
        "use_when": "Checking health, vitals, cost, or system state.",
        "aliases": ["arif_health", "arif_vitals", "arif_metrics", "health", "vitals"],
        "keywords": ["health", "vitals", "metrics", "status", "cost", "predict", "topology"],
        "examples": [
            "Check system health",
            "What are the current vitals?",
            "Show me the metrics",
        ],
        "category": "measurement",
        "read_only": True,
    },
    "arif_canary": {
        "use_when": "Debugging MCP connections, verifying protocol versions, or testing schema round-trips.",
        "aliases": ["arif_diagnostic", "arif_probe", "arif_test", "canary", "diagnostic"],
        "keywords": ["canary", "diagnostic", "probe", "test", "verify", "protocol", "schema"],
        "examples": [
            "Test the MCP connection",
            "Verify protocol version",
            "Run diagnostic probe",
        ],
        "category": "diagnostic",
        "read_only": True,
    },
    "arif_conformance_report": {
        "use_when": "Verifying constitutional compliance, auditing the kernel, or proving governance.",
        "aliases": ["arif_audit", "arif_compliance", "conformance", "compliance"],
        "keywords": ["conformance", "compliance", "audit", "governance", "verify", "proof"],
        "examples": [
            "Run conformance report",
            "Verify governance compliance",
            "Audit the kernel",
        ],
        "category": "diagnostic",
        "read_only": True,
    },
    "hermes_vault_query": {
        "use_when": "Searching the audit trail, finding past seals, or querying historical records.",
        "aliases": ["arif_vault_query", "vault_query", "audit_query", "search_vault"],
        "keywords": ["vault", "audit", "history", "sealed", "past", "records", "ledger"],
        "examples": [
            "Search the vault for recent seals",
            "What was sealed yesterday?",
            "Query audit history for GEOX",
        ],
        "category": "memory",
        "read_only": True,
    },
    "arif_kernel_intercept": {
        "use_when": "Need to verify an action against constitutional floors before execution.",
        "aliases": ["arif_constitutional_check", "kernel_intercept", "intercept"],
        "keywords": ["intercept", "constitutional", "floor", "check", "kernel"],
        "examples": [
            "Check constitutional compliance",
            "Verify floor requirements",
        ],
        "category": "governance",
        "read_only": True,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# RESOLUTION API
# ═══════════════════════════════════════════════════════════════════════════════


def resolve_tool_name(name: str) -> str | None:
    """Resolve a tool name or alias to the canonical name."""
    # Direct match
    if name in TOOL_DISCOVERY:
        return name

    # Alias match
    for canonical, meta in TOOL_DISCOVERY.items():
        if name in meta.get("aliases", []):
            return canonical

    return None


def find_tools_by_query(query: str) -> list[str]:
    """Find tools matching a natural language query."""
    query_lower = query.lower()
    matches = []

    for canonical, meta in TOOL_DISCOVERY.items():
        score = 0

        # Check keywords
        for kw in meta.get("keywords", []):
            if kw in query_lower:
                score += 2

        # Check aliases
        for alias in meta.get("aliases", []):
            if alias in query_lower:
                score += 3

        # Check examples
        for ex in meta.get("examples", []):
            if ex.lower() in query_lower:
                score += 2

        # Check use_when
        use_words = meta.get("use_when", "").lower().split()
        for word in use_words:
            if len(word) > 3 and word in query_lower:
                score += 1

        if score > 0:
            matches.append((canonical, score))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches]


def get_tool_info(tool_name: str) -> dict[str, Any] | None:
    """Get discovery info for a tool."""
    canonical = resolve_tool_name(tool_name)
    if canonical and canonical in TOOL_DISCOVERY:
        return {"canonical_name": canonical, **TOOL_DISCOVERY[canonical]}
    return None


def format_tool_discovery_for_llm() -> str:
    """Format all tool discovery as LLM-friendly text."""
    categories = {}
    for canonical, meta in TOOL_DISCOVERY.items():
        cat = meta.get("category", "other")
        categories.setdefault(cat, []).append((canonical, meta))

    lines = ["arifOS Tool Quick Reference", "=" * 40, ""]

    for cat, tools in sorted(categories.items()):
        lines.append(f"【{cat.upper()}】")
        for canonical, meta in tools:
            aliases = meta.get("aliases", [])
            alias_str = f" (also: {', '.join(aliases[:3])})" if aliases else ""
            lines.append(f"  {canonical}{alias_str}")
            lines.append(f"    {meta['use_when']}")
        lines.append("")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCE DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_DISCOVERY_RESOURCE = {
    "uri": "arif://tools/discovery",
    "name": "arifOS Tool Discovery",
    "description": (
        "Quick reference for selecting the correct arifOS tool. "
        "Use this when unsure which tool to call. "
        "Each tool has 'use_when' guidance, aliases, and examples."
    ),
    "mimeType": "application/json",
}


def get_tool_discovery_resource_text() -> dict[str, Any]:
    """Return the tool discovery resource content."""
    return {
        "tools": [
            {
                "canonical_name": canonical,
                **meta,
            }
            for canonical, meta in TOOL_DISCOVERY.items()
        ],
        "alias_map": {
            alias: canonical
            for canonical, meta in TOOL_DISCOVERY.items()
            for alias in meta.get("aliases", [])
        },
        "note": "For full constitutional affordance (purpose, do_not_use_when, L0-L5 agency, decision thresholds, blast radius) call arif://tools/affordance or use get_full_affordance in runtime.",
    }


# ── New: full affordance contracts resource for metacognitive agents ─────────
try:
    from arifosmcp.runtime.tools import get_full_affordance, AGENCY_LEVELS, DECISION_THRESHOLDS
except Exception:

    def get_full_affordance(n):
        return {"tool_name": n, "purpose": "unavailable at discovery load"}

    AGENCY_LEVELS = {}
    DECISION_THRESHOLDS = {}

TOOL_AFFORDANCE_RESOURCE = {
    "uri": "arif://tools/affordance",
    "name": "arifOS Constitutional Affordance Contracts",
    "description": (
        "Full metacognitive contract per tool: purpose, use_when, do_not_use_when, "
        "agency_level (L0-OBSERVE to L5-IRREVERSIBLE), blast_radius, requires_human_confirmation, "
        "decision_thresholds, and merged power surface. Call BEFORE any tool invocation. "
        "Answers: What is it for? When NOT to use? What will change? How confident + next safe step?"
    ),
    "mimeType": "application/json",
}


def get_full_affordance_resource_text() -> dict[str, Any]:
    """Expose the complete affordance + purpose contracts for every known tool."""
    # Seed with known from discovery + dynamic lookup for runtime ones
    known = list(TOOL_DISCOVERY.keys()) + [
        "arif_ping",
        "arif_kernel_status",
        "arif_seal",
        "arif_forge_execute",
        "arif_judge",
        "arif_critique",
        "arif_think",
        "arif_memory",
    ]
    contracts = {}
    for name in sorted(set(known)):
        try:
            contracts[name] = get_full_affordance(name)
        except Exception:
            contracts[name] = {"tool_name": name, "error": "lookup_failed"}

    # Special section: the Core 7 (kernel 7 tools) — these have the strongest contracts
    from arifosmcp.constitutional_map import CORE_SEVEN, CORE_SEVEN_LABELS

    core7 = {}
    for name in CORE_SEVEN:
        core7[name] = contracts.get(name, get_full_affordance(name))
        core7[name]["core_label"] = CORE_SEVEN_LABELS.get(name, name)

    return {
        "standard": "arifOS-metacognitive-affordance-v1",
        "contracts": contracts,
        "core_seven": core7,  # The 7 tools done properly
        "agency_levels": AGENCY_LEVELS,
        "decision_thresholds": DECISION_THRESHOLDS,
        "usage": {
            "pre_call": "Retrieve this resource or call get_full_affordance(name). Build why_this_tool object.",
            "post_call": "Inspect response.metacognition + next_safe_action. Update your internal state.",
            "l5_rule": "Any tool with agency_level containing L5 MUST trigger 888_HOLD + explicit human ack.",
            "core_loop": "For serious work, follow the Core 7 pipeline in order. Each step should produce its metacognitive fields.",
        },
    }
