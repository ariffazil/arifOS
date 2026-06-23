"""
arifOS Tool Discovery — LLM-Optimized Tool Selection
═══════════════════════════════════════════════════════

Provides clear "use when" guidance for LLMs to select the correct arifOS tool.
Each tool entry includes:
  - description: What the tool does (1-2 sentences)
  - use_when: Clear trigger phrases for LLMs
  - do_not_use_when: When NOT to use this tool
  - aliases: Common alternative names LLMs might try
  - keywords: Search terms for discovery
  - examples: Example queries that should trigger this tool

DITEMPA BUKAN DIBERI — Discovered, not guessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArifToolDiscovery:
    """LLM-optimized tool discovery metadata."""

    name: str
    description: str
    use_when: str
    do_not_use_when: str
    aliases: list[str]
    keywords: list[str]
    examples: list[str]
    category: str
    modes: list[str] | None = None
    requires_session: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL DISCOVERY REGISTRY — 19 arifOS MCP Tools
# ═══════════════════════════════════════════════════════════════════════════════

ARIF_TOOL_DISCOVERY: dict[str, ArifToolDiscovery] = {
    # ── SESSION & IDENTITY ─────────────────────────────────────────────────────
    "arif_init": ArifToolDiscovery(
        name="arif_init",
        description="Start or resume a governed constitutional session. MUST be called first before any other tool.",
        use_when="Beginning a new conversation, starting a task, resuming a session, or binding to a constitutional context. Keywords: 'start session', 'initialize', 'begin', 'new conversation', 'resume'.",
        do_not_use_when="Already in an active session. Use other tools directly.",
        aliases=[
            "arif_session_init",
            "arifos_init",
            "session_init",
            "init_session",
            "start_session",
        ],
        keywords=["init", "session", "start", "begin", "resume", "initialize", "bootstrap", "bind"],
        examples=[
            "Start a new session",
            "Initialize arifOS",
            "Begin a governed conversation",
            "Resume my previous session",
        ],
        category="session",
        modes=["init", "light", "resume", "validate", "epoch_open", "epoch_seal", "opt_out"],
        requires_session=False,
    ),
    # ── OBSERVATION & SENSING ──────────────────────────────────────────────────
    "arif_observe": ArifToolDiscovery(
        name="arif_observe",
        description="Search the web, ingest URLs, check system vitals, or map a repository.",
        use_when="User wants to search the web, fetch a URL, check system health, or explore a repo. Keywords: 'search', 'find', 'look up', 'fetch URL', 'check vitals'.",
        do_not_use_when="User wants to reason about data already gathered (use arif_think) or route to specific organ (use arif_route).",
        aliases=["arif_search", "arif_web_search", "search", "web_search", "fetch"],
        keywords=["search", "web", "fetch", "url", "ingest", "vitals", "health", "repo", "map"],
        examples=[
            "Search the web for latest geophysics papers",
            "Fetch this URL: https://example.com",
            "Check system vitals",
            "Map the arifOS repository",
        ],
        category="observation",
        modes=["search", "ingest", "compass", "atlas", "entropy_dS", "vitals", "repo_map"],
    ),
    "arif_explore": ArifToolDiscovery(
        name="arif_explore",
        description="Multimodal reality observation — web search, URL ingestion, geospatial compass, entropy monitoring.",
        use_when="User wants comprehensive sensing across multiple dimensions. Similar to arif_observe but more detailed.",
        do_not_use_when="User wants simple search (use arif_observe) or specific organ data (use arif_route).",
        aliases=["arif_sense", "arif_multimodal", "explore", "sense"],
        keywords=["explore", "sense", "multimodal", "observe", "compass", "atlas", "entropy"],
        examples=[
            "Explore this topic comprehensively",
            "Get a multimodal view of this area",
            "Check entropy of the current session",
        ],
        category="observation",
        modes=["search", "ingest", "compass", "atlas", "entropy_dS", "vitals"],
    ),
    "arif_fetch": ArifToolDiscovery(
        name="arif_fetch",
        description="Fetch content from a URL. Returns page content as text.",
        use_when="User provides a specific URL and wants its content. Keywords: 'fetch', 'get page', 'download', 'read URL'.",
        do_not_use_when="User wants to search the web (use arif_observe) or analyze multiple sources (use arif_explore).",
        aliases=["fetch_url", "get_url", "download", "read_url"],
        keywords=["fetch", "url", "page", "download", "read", "content", "html", "markdown"],
        examples=[
            "Fetch this page: https://example.com",
            "Get the content of this URL",
            "Read this webpage",
        ],
        category="observation",
        modes=["fetch"],
    ),
    # ── REASONING & PLANNING ───────────────────────────────────────────────────
    "arif_think": ArifToolDiscovery(
        name="arif_think",
        description="Multi-step reasoning, planning, and reflection with confidence labeling.",
        use_when="User wants to analyze, plan, reflect, verify, or critique something. Keywords: 'think', 'analyze', 'plan', 'reason', 'reflect', 'verify'.",
        do_not_use_when="User wants to search for information (use arif_observe) or execute actions (use arif_forge).",
        aliases=["arif_reason", "arif_analyze", "arif_plan", "think", "reason", "analyze", "plan"],
        keywords=[
            "think",
            "reason",
            "analyze",
            "plan",
            "reflect",
            "verify",
            "critique",
            "strategy",
        ],
        examples=[
            "Think about this problem",
            "Analyze the trade-offs",
            "Create a plan for this task",
            "Reflect on what we've learned",
        ],
        category="reasoning",
        modes=[
            "reason",
            "reflect",
            "verify",
            "critique",
            "axioms",
            "plan",
            "plan_review",
            "plan_approve",
            "refactor_plan",
            "metabolize",
        ],
    ),
    "arif_critique": ArifToolDiscovery(
        name="arif_critique",
        description="Assess ethical risks and human impact before acting.",
        use_when="Before irreversible, sensitive, or dignity-affecting actions. Keywords: 'critique', 'ethical', 'risk', 'dignity', 'impact'.",
        do_not_use_when="User wants general reasoning (use arif_think) or execution (use arif_forge).",
        aliases=["arif_ethical_check", "arif_risk_assess", "critique", "ethical_check"],
        keywords=[
            "critique",
            "ethical",
            "risk",
            "dignity",
            "impact",
            "sensitive",
            "irreversible",
            "maruah",
        ],
        examples=[
            "Is this action ethical?",
            "What are the risks?",
            "Check dignity impact",
            "Red-team this proposal",
        ],
        category="reasoning",
        modes=["critique", "simulate", "redteam", "maruah", "deescalate", "empathy"],
    ),
    # ── ROUTING & TRIAGE ───────────────────────────────────────────────────────
    "arif_route": ArifToolDiscovery(
        name="arif_route",
        description="Canonical intent router. Routes natural-language intent to the correct federation organ.",
        use_when="User wants to do something but you're not sure which organ (GEOX, WEALTH, WELL, A-FORGE) handles it. Keywords: 'route', 'which organ', 'delegate', 'forward'.",
        do_not_use_when="You know the specific organ and tool (use arif_bridge_connect directly).",
        aliases=["arif_delegate", "arif_forward", "route", "delegate"],
        keywords=["route", "organ", "delegate", "forward", "which", "where", "dispatch"],
        examples=[
            "Route this to the right organ",
            "Which organ handles geology?",
            "Delegate this task",
        ],
        category="routing",
    ),
    "arif_triage": ArifToolDiscovery(
        name="arif_triage",
        description="Constitutional preflight check. Returns kernel status, current holds, and correct lane.",
        use_when="Before executing any significant action. Check if there are holds or blocks. Keywords: 'triage', 'preflight', 'check', 'status'.",
        do_not_use_when="User wants to start a session (use arif_init) or get detailed status (use arif_measure).",
        aliases=["arif_preflight", "arif_check", "triage", "preflight"],
        keywords=["triage", "preflight", "check", "status", "hold", "block", "lane"],
        examples=[
            "Check if we can proceed",
            "Any holds on this action?",
            "Run preflight check",
        ],
        category="routing",
        modes=["status", "preflight", "triage"],
    ),
    "arif_bridge_connect": ArifToolDiscovery(
        name="arif_bridge_connect",
        description="Direct organ tool call. Bypasses intent routing — caller must specify organ and tool_name.",
        use_when="You know exactly which organ and tool to call. Keywords: 'call organ', 'bridge', 'direct call', 'GEOX tool', 'WEALTH tool'.",
        do_not_use_when="You're unsure which organ handles the task (use arif_route instead).",
        aliases=["arif_call_organ", "arif_direct_call", "bridge_connect", "call_tool"],
        keywords=["bridge", "organ", "direct", "call", "geox", "wealth", "well", "forge", "tool"],
        examples=[
            "Call geox_basin on GEOX",
            "Direct call to WEALTH organ",
            "Bridge to WELL for vitality check",
        ],
        category="routing",
    ),
    # ── MEMORY ─────────────────────────────────────────────────────────────────
    "arif_memory": ArifToolDiscovery(
        name="arif_memory",
        description="Federated memory tool — recall, inspect, attest, remember, promote, revise, forget.",
        use_when="User wants to store, retrieve, or manage memory across the federation. Keywords: 'remember', 'recall', 'forget', 'memory', 'store'.",
        do_not_use_when="User wants to query VAULT999 specifically (use hermes_vault_query).",
        aliases=["arif_remember", "arif_recall", "memory", "remember", "recall"],
        keywords=["memory", "remember", "recall", "forget", "store", "attest", "promote", "revise"],
        examples=[
            "Remember this for later",
            "What do we know about X?",
            "Forget this information",
            "Promote this to long-term memory",
        ],
        category="memory",
        modes=["recall", "inspect", "attest", "remember", "promote", "revise", "forget"],
    ),
    # ── JUDGMENT & SEALING ─────────────────────────────────────────────────────
    "arif_judge": ArifToolDiscovery(
        name="arif_judge",
        description="Render final constitutional verdict on a proposed action.",
        use_when="A decision needs arbitration and binding judgment. Keywords: 'judge', 'verdict', 'decide', 'approve', 'reject'.",
        do_not_use_when="User wants to reason about options (use arif_think) or critique (use arif_critique).",
        aliases=["arif_verdict", "arif_decide", "judge", "verdict", "decide"],
        keywords=[
            "judge",
            "verdict",
            "decide",
            "approve",
            "reject",
            "seal",
            "hold",
            "constitutional",
        ],
        examples=[
            "Judge this proposal",
            "Issue a verdict",
            "Should we proceed?",
        ],
        category="judgment",
        modes=["judge", "validate", "hold", "rules", "armor", "probe", "notify"],
    ),
    "arif_seal": ArifToolDiscovery(
        name="arif_seal",
        description="Seal a verdict or outcome to the immutable audit ledger.",
        use_when="Final, irreversible records that must be preserved forever. Keywords: 'seal', 'finalize', 'immutable', 'audit'.",
        do_not_use_when="User wants to draft or review (use arif_think) or get a verdict (use arif_judge).",
        aliases=["arif_finalize", "arif_audit_seal", "seal", "finalize"],
        keywords=["seal", "finalize", "immutable", "audit", "ledger", "permanent", "record"],
        examples=[
            "Seal this verdict",
            "Make this permanent",
            "Write to the audit ledger",
        ],
        category="judgment",
        modes=["seal", "verify", "ledger", "changelog", "audit"],
    ),
    # ── EXECUTION ──────────────────────────────────────────────────────────────
    "arif_forge": ArifToolDiscovery(
        name="arif_forge",
        description="Execute approved builds, deployments, or system changes.",
        use_when="After judge has issued a SEAL verdict and you need to execute. Keywords: 'execute', 'build', 'deploy', 'forge', 'run'.",
        do_not_use_when="User wants to plan (use arif_think) or get approval (use arif_judge) first.",
        aliases=[
            "arif_execute",
            "arif_build",
            "arif_deploy",
            "forge",
            "execute",
            "build",
            "deploy",
        ],
        keywords=["forge", "execute", "build", "deploy", "run", "change", "mutate", "write"],
        examples=[
            "Execute the approved plan",
            "Build and deploy",
            "Forge this change",
        ],
        category="execution",
        modes=["engineer", "query", "write", "generate", "commit", "recall", "dry_run"],
    ),
    # ── MEASUREMENT ────────────────────────────────────────────────────────────
    "arif_measure": ArifToolDiscovery(
        name="arif_measure",
        description="Check system health, thermodynamic state, and resource metrics.",
        use_when="User wants to check health, vitals, cost, or system state. Keywords: 'health', 'vitals', 'metrics', 'status', 'cost'.",
        do_not_use_when="User wants to start a session (use arif_init) or do a preflight check (use arif_triage).",
        aliases=["arif_health", "arif_vitals", "arif_metrics", "health", "vitals", "metrics"],
        keywords=["health", "vitals", "metrics", "status", "cost", "predict", "topology", "drift"],
        examples=[
            "Check system health",
            "What are the current vitals?",
            "Show me the metrics",
        ],
        category="measurement",
        modes=[
            "health",
            "vitals",
            "cost",
            "genius",
            "psi_le",
            "omega",
            "landauer",
            "topology",
            "drift",
        ],
    ),
    "arif_canary": ArifToolDiscovery(
        name="arif_canary",
        description="Unified transport diagnostic probe. Liveness checks, protocol verification, schema testing.",
        use_when="Debugging MCP connections, verifying protocol versions, or testing schema round-trips. Keywords: 'diagnostic', 'probe', 'test connection', 'verify protocol'.",
        do_not_use_when="User wants normal tool operations (use the appropriate tool directly).",
        aliases=["arif_diagnostic", "arif_probe", "arif_test", "canary", "diagnostic", "probe"],
        keywords=[
            "canary",
            "diagnostic",
            "probe",
            "test",
            "verify",
            "protocol",
            "schema",
            "transport",
        ],
        examples=[
            "Test the MCP connection",
            "Verify protocol version",
            "Run diagnostic probe",
        ],
        category="diagnostic",
        modes=[
            "ping",
            "schema_echo",
            "version_echo",
            "transport_echo",
            "initialize_probe",
            "conformance_report",
        ],
    ),
    "arif_conformance_report": ArifToolDiscovery(
        name="arif_conformance_report",
        description="Run the ARIF Conformance Spine against the live kernel. Proves arifOS is a governed runtime.",
        use_when="Verifying constitutional compliance, auditing the kernel, or proving governance. Keywords: 'conformance', 'compliance', 'audit', 'verify governance'.",
        do_not_use_when="User wants normal operations (use appropriate tool).",
        aliases=["arif_audit", "arif_compliance", "conformance", "compliance"],
        keywords=["conformance", "compliance", "audit", "governance", "verify", "proof", "kernel"],
        examples=[
            "Run conformance report",
            "Verify governance compliance",
            "Audit the kernel",
        ],
        category="diagnostic",
    ),
    # ── COMPOSITION ────────────────────────────────────────────────────────────
    "arif_compose": ArifToolDiscovery(
        name="arif_compose",
        description="Compose the final response for the user. Call LAST after reasoning and judgment.",
        use_when="Ready to formulate the final answer for the user. Keywords: 'compose', 'format', 'respond', 'answer'.",
        do_not_use_when="Still gathering information or reasoning (use arif_think first).",
        aliases=["arif_respond", "arif_format", "arif_answer", "compose", "respond", "format"],
        keywords=["compose", "format", "respond", "answer", "final", "output", "present"],
        examples=[
            "Compose the final answer",
            "Format the response",
            "Present the findings",
        ],
        category="composition",
        modes=["compose", "summarize", "cite", "tone_shift"],
    ),
    # ── KERNEL INTERCEPT ───────────────────────────────────────────────────────
    "arif_kernel_intercept": ArifToolDiscovery(
        name="arif_kernel_intercept",
        description="Minimum constitutional kernel interceptor. Low-level governance check.",
        use_when="Need to verify an action against constitutional floors before execution. Keywords: 'intercept', 'constitutional check', 'floor check'.",
        do_not_use_when="User wants normal operations (use appropriate tool).",
        aliases=["arif_constitutional_check", "kernel_intercept", "intercept"],
        keywords=["intercept", "constitutional", "floor", "check", "kernel", "governance"],
        examples=[
            "Check constitutional compliance",
            "Verify floor requirements",
        ],
        category="governance",
    ),
    # ── VAULT QUERY ────────────────────────────────────────────────────────────
    "hermes_vault_query": ArifToolDiscovery(
        name="hermes_vault_query",
        description="Query VAULT999 audit ledger. Search sealed records by keyword, organ, or date.",
        use_when="User wants to search the audit trail, find past seals, or query historical records. Keywords: 'vault', 'audit', 'history', 'sealed', 'past'.",
        do_not_use_when="User wants to create new memories (use arif_memory) or seal new records (use arif_seal).",
        aliases=["arif_vault_query", "vault_query", "audit_query", "search_vault"],
        keywords=["vault", "audit", "history", "sealed", "past", "records", "ledger", "query"],
        examples=[
            "Search the vault for recent seals",
            "What was sealed yesterday?",
            "Query audit history for GEOX",
        ],
        category="memory",
        modes=["recent", "search", "organ", "date"],
        requires_session=False,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# DISCOVERY API
# ═══════════════════════════════════════════════════════════════════════════════


def get_tool_discovery(tool_name: str) -> ArifToolDiscovery | None:
    """Get discovery metadata for a tool. Resolves aliases."""
    # Direct match
    if tool_name in ARIF_TOOL_DISCOVERY:
        return ARIF_TOOL_DISCOVERY[tool_name]

    # Alias match
    for td in ARIF_TOOL_DISCOVERY.values():
        if tool_name in td.aliases:
            return td

    return None


def resolve_tool_name(name: str) -> str | None:
    """Resolve a tool name or alias to the canonical name."""
    # Direct match
    if name in ARIF_TOOL_DISCOVERY:
        return name

    # Alias match
    for td in ARIF_TOOL_DISCOVERY.values():
        if name in td.aliases:
            return td.name

    return None


def get_all_discoveries() -> dict[str, ArifToolDiscovery]:
    """Get all tool discovery metadata."""
    return ARIF_TOOL_DISCOVERY.copy()


def find_tools_by_keyword(keyword: str) -> list[ArifToolDiscovery]:
    """Find tools matching a keyword."""
    keyword_lower = keyword.lower()
    return [
        td
        for td in ARIF_TOOL_DISCOVERY.values()
        if keyword_lower in td.keywords
        or keyword_lower in td.description.lower()
        or keyword_lower in td.use_when.lower()
        or keyword_lower in td.aliases
    ]


def find_tools_by_query(query: str) -> list[ArifToolDiscovery]:
    """Find tools matching a natural language query."""
    query_lower = query.lower()
    matches = []
    for td in ARIF_TOOL_DISCOVERY.values():
        # Check keywords
        if any(kw in query_lower for kw in td.keywords):
            matches.append(td)
            continue
        # Check aliases
        if any(alias in query_lower for alias in td.aliases):
            matches.append(td)
            continue
        # Check examples
        if any(ex.lower() in query_lower for ex in td.examples):
            matches.append(td)
            continue
        # Check use_when keywords
        use_words = td.use_when.lower().split()
        if any(word in query_lower for word in use_words if len(word) > 3):
            matches.append(td)
    return matches


def format_discovery_for_llm(tool_name: str) -> str:
    """Format discovery metadata as LLM-friendly text."""
    td = get_tool_discovery(tool_name)
    if not td:
        return f"Tool '{tool_name}' not found. Did you mean: {', '.join(suggest_tools(tool_name))}?"

    modes_str = ""
    if td.modes:
        modes_str = f"\n  Modes: {', '.join(td.modes)}"

    aliases_str = ""
    if td.aliases:
        aliases_str = f"\n  Also known as: {', '.join(td.aliases[:5])}"

    return f"""Tool: {td.name}
Category: {td.category}
Description: {td.description}
Use when: {td.use_when}
Do NOT use when: {td.do_not_use_when}
Examples:
{chr(10).join(f"  - {ex}" for ex in td.examples)}{modes_str}{aliases_str}"""


def suggest_tools(query: str, max_results: int = 3) -> list[str]:
    """Suggest tools based on a query."""
    matches = find_tools_by_query(query)
    return [td.name for td in matches[:max_results]]


def format_all_discoveries_for_llm() -> str:
    """Format all discoveries as LLM-friendly text."""
    categories = {}
    for td in ARIF_TOOL_DISCOVERY.values():
        categories.setdefault(td.category, []).append(td)

    result = "arifOS Tools — Quick Reference\n"
    result += "=" * 50 + "\n\n"

    for category, tools in sorted(categories.items()):
        result += f"【{category.upper()}】\n"
        for td in tools:
            result += f"\n  {td.name}\n"
            result += f"    {td.description}\n"
            result += f"    Use when: {td.use_when[:100]}...\n"
            if td.aliases:
                result += f"    Aliases: {', '.join(td.aliases[:3])}\n"
        result += "\n"

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCE — Tool Discovery
# ═══════════════════════════════════════════════════════════════════════════════


def get_tool_discovery_resource() -> dict[str, Any]:
    """Return tool discovery as MCP resource for LLMs."""
    return {
        "uri": "arif://tools/discovery",
        "name": "arifOS Tool Discovery",
        "description": "Quick reference for selecting the correct arifOS tool. Use this when unsure which tool to call.",
        "mimeType": "application/json",
        "text": {
            "tools": [
                {
                    "name": td.name,
                    "category": td.category,
                    "description": td.description,
                    "use_when": td.use_when,
                    "do_not_use_when": td.do_not_use_when,
                    "aliases": td.aliases,
                    "keywords": td.keywords,
                    "examples": td.examples,
                    "modes": td.modes,
                }
                for td in ARIF_TOOL_DISCOVERY.values()
            ]
        },
    }


def get_tool_aliases_map() -> dict[str, str]:
    """Return a map of all aliases to canonical names."""
    alias_map = {}
    for td in ARIF_TOOL_DISCOVERY.values():
        for alias in td.aliases:
            alias_map[alias] = td.name
    return alias_map
