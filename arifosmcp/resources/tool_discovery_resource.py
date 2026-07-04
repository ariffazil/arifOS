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

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL DISCOVERY — PUBLIC SURFACE ONLY (PEP 20: explicit, flat, sparse)
# ═══════════════════════════════════════════════════════════════════════════════
# Live kernel exposes 7 public verbs. This file mirrors that surface.
# Internal tools (arif_bridge, arif_memory, arif_measure, arif_forge,
# arif_kernel_intercept) are NOT listed here.
# arif_compose is listed — it is exposed via expanded45 surface.
# They exist in capability_registry.py for kernel use only.
#
# PEP 20 applied:
#   "One obvious way"    — each tool has ONE canonical name, aliases collapse to it
#   "Explicit > implicit" — tier, decision_class, blast_radius declared
#   "Sparse > dense"     — minimal fields, no philosophy
#   "Flat > nested"      — 10 tools, not 19
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_DISCOVERY: dict[str, dict[str, Any]] = {
    # ── CORE SEVEN (public verbs) ──────────────────────────────────────────
    "arif_init": {
        "tier": "PUBLIC",
        "category": "session",
        "decision_class": "C2",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": False,
        "output_type": "session_state",
        "floor_enforced": "F1",
        "use_when": "Starting or resuming a governed constitutional session.",
        "do_not_use_when": "Session already active. Use other tools directly.",
        "aliases": ["arif_session_init", "session_init"],
        "keywords": ["start", "begin", "initialize", "session", "resume"],
        "examples": ["Start a new session", "Initialize arifOS"],
    },
    "arif_observe": {
        "tier": "PUBLIC",
        "category": "observation",
        "decision_class": "C1",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": True,
        "output_type": "evidence_bundle",
        "floor_enforced": "F2",
        "use_when": "Searching web, fetching URLs, checking vitals, mapping repos.",
        "do_not_use_when": "Domain calculation needed — use arif_route to GEOX/WEALTH/WELL.",
        "aliases": ["arif_fetch", "arif_explore", "arif_search"],
        "keywords": ["search", "fetch", "observe", "vitals", "repo", "url", "web"],
        "examples": ["Search the web for X", "Fetch this URL", "Check system vitals"],
    },
    "arif_think": {
        "tier": "PUBLIC",
        "category": "reasoning",
        "decision_class": "C2",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": True,
        "output_type": "reasoning_bundle",
        "floor_enforced": "F7",
        "use_when": "Analyzing, planning, reflecting, verifying, or critiquing.",
        "do_not_use_when": "Need binding judgment — use arif_judge instead.",
        "aliases": ["arif_critique", "arif_reason", "arif_analyze", "arif_plan"],
        "keywords": ["think", "reason", "analyze", "plan", "reflect", "critique"],
        "examples": ["Analyze the trade-offs", "Create a plan", "Critique this proposal"],
    },
    "arif_route": {
        "tier": "PUBLIC",
        "category": "routing",
        "decision_class": "C1",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": True,
        "output_type": "routing_decision",
        "floor_enforced": "F4",
        "use_when": "You know what you want but not which organ to call.",
        "do_not_use_when": "You know the exact tool — call it directly via arif_act.",
        "aliases": ["arif_triage", "arif_delegate"],
        "keywords": ["route", "organ", "delegate", "which", "where"],
        "examples": ["Route this to GEOX", "Which organ handles geology?"],
    },
    "arif_judge": {
        "tier": "PUBLIC",
        "category": "judgment",
        "decision_class": "C3",
        "blast_radius": "MEDIUM",
        "mutation": False,
        "requires_session": True,
        "output_type": "verdict",
        "floor_enforced": "F13",
        "use_when": "A decision needs constitutional arbitration and binding judgment.",
        "do_not_use_when": "Routine observation or reasoning — use arif_observe/arif_think.",
        "aliases": ["arif_verdict"],
        "keywords": ["judge", "verdict", "decide", "approve", "reject"],
        "examples": ["Judge this proposal", "Should we proceed?"],
    },
    "arif_act": {
        "tier": "PUBLIC",
        "category": "execution",
        "decision_class": "C4",
        "blast_radius": "HIGH",
        "mutation": True,
        "requires_session": True,
        "output_type": "execution_receipt",
        "floor_enforced": "F1",
        "use_when": "After arif_judge issues SEAL. Execute the approved action.",
        "do_not_use_when": "No valid SEAL verdict. Call arif_judge first.",
        "aliases": ["arif_forge", "arif_execute"],
        "keywords": ["execute", "build", "deploy", "forge", "act", "run"],
        "examples": ["Execute the approved plan", "Build and deploy"],
    },
    "arif_seal": {
        "tier": "PUBLIC",
        "category": "sealing",
        "decision_class": "C4",
        "blast_radius": "CRITICAL",
        "mutation": True,
        "requires_session": True,
        "output_type": "vault_receipt",
        "floor_enforced": "F13",
        "use_when": "Final, irreversible records that must be preserved forever.",
        "do_not_use_when": "Draft or tentative work — not ready to seal.",
        "aliases": ["arif_finalize"],
        "keywords": ["seal", "finalize", "immutable", "audit", "ledger"],
        "examples": ["Seal this verdict", "Write to audit ledger"],
    },
    # ── INTERNAL-EXPOSED (expanded45 surface, registered at runtime) ──────────
    "arif_compose": {
        "tier": "INTERNAL",
        "category": "reply",
        "decision_class": "C2",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": True,
        "output_type": "composed_message",
        "floor_enforced": None,
        "use_when": "Final response composition before presenting to Arif.",
        "do_not_use_when": "During mid-pipeline reasoning or planning.",
        "aliases": ["arif_reply_compose"],
        "keywords": ["compose", "reply", "format", "output"],
        "examples": ["Compose final answer", "Format response"],
    },
    # ── DIAGNOSTIC (callable, system health only) ──────────────────────────
    "arif_canary": {
        "tier": "DIAGNOSTIC",
        "category": "diagnostic",
        "decision_class": "C1",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": False,
        "output_type": "diagnostic_report",
        "floor_enforced": None,
        "use_when": "Debugging MCP connections or verifying protocol versions.",
        "do_not_use_when": "Normal operation — this is for debugging only.",
        "aliases": [],
        "keywords": ["canary", "diagnostic", "probe", "test"],
        "examples": ["Test MCP connection", "Verify protocol version"],
    },
    "arif_conformance_report": {
        "tier": "DIAGNOSTIC",
        "category": "diagnostic",
        "decision_class": "C2",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": False,
        "output_type": "conformance_report",
        "floor_enforced": None,
        "use_when": "Verifying constitutional compliance or auditing the kernel.",
        "do_not_use_when": "Normal operation — this is for auditing only.",
        "aliases": [],
        "keywords": ["conformance", "compliance", "audit"],
        "examples": ["Run conformance report", "Audit the kernel"],
    },
    "arif_vault_query": {
        "tier": "DIAGNOSTIC",
        "category": "memory",
        "decision_class": "C1",
        "blast_radius": "LOW",
        "mutation": False,
        "requires_session": False,
        "output_type": "vault_entries",
        "floor_enforced": None,
        "use_when": "Searching the audit trail or querying historical records.",
        "do_not_use_when": "Need to write — use arif_seal instead.",
        "aliases": ["vault_query"],
        "keywords": ["vault", "audit", "history", "sealed", "records"],
        "examples": ["Search vault for recent seals", "Query audit history"],
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
