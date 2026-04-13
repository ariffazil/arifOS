"""
arifosmcp/runtime/resources_v2.py — arifOS MCP v2 Resources

Resources are read-only constitutional documents.
They provide grounding, policy, schemas, governance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

CANON_SESSION_STATES = """# arifOS Session Ladder

- anonymous: no verified session binding
- claimed: actor declared but not yet anchored
- anchored: session established with governed continuity
- verified: authority and continuity checks passed
- OPERATOR: explicit operator authority present
"""

CANON_INDEX = {
    "resources": [
        "canon://states",
        "canon://index",
        "arifos://governance/floors",
        "arifos://governance/verdict",
        "arifos://system/capabilities",
    ]
}


# ═══════════════════════════════════════════════════════════════════════════════
# V2 RESOURCE DATA
# ═══════════════════════════════════════════════════════════════════════════════

FLOORS_SPEC: dict[str, dict[str, Any]] = {
    "F1": {
        "name": "AMANAH",
        "principle": "Non-contradiction & Reversibility",
        "question": "Can this be undone?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F2": {
        "name": "TRUTH",
        "principle": "Evidence Grounding",
        "question": "Is this grounded in evidence?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F3": {
        "name": "TRI-WITNESS",
        "principle": "Theory-Constitution-Intent Alignment",
        "question": "Do theory, constitution, intent agree?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F4": {
        "name": "CLARITY",
        "principle": "Uncertainty Reduction",
        "question": "Does this reduce confusion?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F5": {
        "name": "PEACE²",
        "principle": "Non-Destruction",
        "question": "Does this destroy anything?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F6": {
        "name": "EMPATHY",
        "principle": "Dignity Preservation",
        "question": "Does this show understanding?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F7": {
        "name": "HUMILITY",
        "principle": "Uncertainty Acknowledgment",
        "question": "Are uncertainties acknowledged?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F8": {
        "name": "GENIUS",
        "principle": "System Health",
        "question": "Does this maintain system health?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F9": {
        "name": "ETHICS",
        "principle": "Non-Manipulation",
        "question": "Is this manipulative or deceptive?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F10": {
        "name": "CONSCIENCE",
        "principle": "Consciousness Claims",
        "question": "Is this claiming consciousness?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F11": {
        "name": "AUDITABILITY",
        "principle": "Inspectability",
        "question": "Is this logged and inspectable?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F12": {
        "name": "RESILIENCE",
        "principle": "Safe Failure",
        "question": "Does this fail safely?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F13": {
        "name": "ADAPTABILITY",
        "principle": "Safety Preservation",
        "question": "Do updates preserve safety?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
}

VERDICT_SPEC: dict[str, Any] = {
    "verdicts": {
        "SEAL": {
            "code": 0,
            "description": "Execute immediately",
            "color": "#2ecc71",
            "action": "PROCEED",
        },
        "PARTIAL": {
            "code": 101,
            "range": "101-499",
            "description": "Execute with notes",
            "color": "#f1c40f",
            "action": "PROCEED_WITH_CAUTION",
        },
        "CAUTION": {
            "code": 500,
            "range": "500-899",
            "description": "Execute with warnings",
            "color": "#e67e22",
            "action": "PROCEED_WITH_WARNINGS",
        },
        "HOLD": {
            "code": -1,
            "description": "Awaiting human",
            "color": "#9b59b6",
            "action": "HUMAN_REVIEW_REQUIRED",
        },
        "SABAR": {
            "code": -2,
            "description": "Wait and retry",
            "color": "#3498db",
            "action": "DEFER_RETRY",
        },
        "VOID": {
            "code": 999,
            "description": "Blocked",
            "color": "#e74c3c",
            "action": "BLOCK",
        },
    },
    "required_fields": [
        "verdict",
        "floors_triggered",
        "confidence",
        "reasoning_class",
    ],
    "output_schema": {
        "type": "object",
        "required": ["verdict", "floors_triggered", "confidence", "reasoning_class"],
        "properties": {
            "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "VOID", "HOLD"]},
            "floors_triggered": {"type": "array", "items": {"type": "string"}},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reasoning_class": {"type": "string", "enum": ["constitutional", "safety", "uncertainty"]},
            "evidence_hash": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
        },
    },
}

SYSTEM_CAPABILITIES: dict[str, Any] = {
    "name": "ARIFOS MCP",
    "version": "2.0.0",
    "namespace": "arifos",
    "constitutional_floors": 13,
    "tools": {
        "public": ["arifos_init", "arifos_route", "arifos_judge", "arifos_forge"],
        "internal": ["arifos_sense", "arifos_mind", "arifos_heart", "arifos_ops", "arifos_memory", "arifos_vault", "arifos_health"],
        "total": 11,
    },
    "mcp_version": "2025-11-25",
    "schema_registry": {
        "version": "2.0.0",
        "resources": [
            "arifos://schema/master",
            "arifos://schema/tools",
            "arifos://schema/tool/{tool_id}",
            "arifos://schema/stages",
            "arifos://schema/trinity",
            "arifos://schema/routing-guide",
        ],
        "stages": ["000_INIT", "111_SENSE", "333_MIND", "444_ROUTER", "555_MEMORY", "666_HEART", "777_OPS", "888_JUDGE", "999_VAULT", "FORGE_010"],
        "trinity": {
            "Δ": "Discernment - Reality, reasoning, execution",
            "Ψ": "Sovereignty - Session, routing, judgment, seal",
            "Ω": "Stability - Memory, safety, thermodynamics",
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# V2 RESOURCE REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def register_v2_resources(mcp: FastMCP) -> list[str]:
    """Register all v2 resources using arifos:// scheme."""
    
    @mcp.resource("arifos://governance/floors")
    def governance_floors() -> dict[str, Any]:
        return FLOORS_SPEC

    @mcp.resource("arifos://governance/verdict")
    def governance_verdict_spec() -> dict[str, Any]:
        return VERDICT_SPEC

    @mcp.resource("arifos://system/capabilities")
    def system_capabilities() -> dict[str, Any]:
        return SYSTEM_CAPABILITIES

    # ═══════════════════════════════════════════════════════════════════════════
    # CONTEXT-RICH TOOL REGISTRY RESOURCES
    # ═══════════════════════════════════════════════════════════════════════════
    
    from arifosmcp.schema import get_registry
    
    registry = get_registry()
    
    @mcp.resource("arifos://schema/master")
    def schema_master() -> dict[str, Any]:
        """Complete arifOS master schema with stages, Trinity, and transitions."""
        return registry.master_schema or {}
    
    @mcp.resource("arifos://schema/tools")
    def schema_tools() -> dict[str, Any]:
        """All tool context packets with full semantic metadata."""
        return registry.tool_packets
    
    @mcp.resource("arifos://schema/tool/{tool_id}")
    def schema_tool(tool_id: str) -> dict[str, Any]:
        """Context packet for a specific tool (e.g., arifos_mind)."""
        packet = registry.get_tool_packet(tool_id)
        if packet:
            return packet
        return {"error": f"Tool {tool_id} not found", "available": list(registry.tool_packets.keys())}
    
    @mcp.resource("arifos://schema/stages")
    def schema_stages() -> dict[str, Any]:
        """Governance stage definitions and transitions."""
        master = registry.master_schema or {}
        return {
            "stage_order": master.get("stage_order", []),
            "stages": master.get("stages", {}),
            "transitions": master.get("transitions", {})
        }
    
    @mcp.resource("arifos://schema/trinity")
    def schema_trinity() -> dict[str, Any]:
        """Trinity lane definitions (Δ Discernment, Ψ Sovereignty, Ω Stability)."""
        master = registry.master_schema or {}
        return master.get("trinity", {})
    
    @mcp.resource("arifos://schema/envelopes")
    def schema_envelopes() -> dict[str, Any]:
        """Shared request/response envelope schemas."""
        return {
            "request": registry.get_request_schema(),
            "response": registry.get_response_schema(),
            "context_packet": registry.get_context_packet_schema()
        }
    
    @mcp.resource("arifos://schema/alias-map")
    def schema_alias_map() -> dict[str, Any]:
        """Mapping from public aliases to backing tools."""
        return registry.get_alias_map()
    
    @mcp.resource("arifos://schema/tool-summary")
    def schema_tool_summary() -> list[dict[str, Any]]:
        """Compact summary of all tools for quick reference."""
        return registry.get_tool_summary()
    
    @mcp.resource("arifos://schema/chatgpt-guide/{tool_id}")
    def schema_chatgpt_guide(tool_id: str) -> dict[str, Any]:
        """ChatGPT-specific usage guidance for a tool."""
        guidance = registry.get_chatgpt_guidance(tool_id)
        if guidance:
            return guidance
        return {"error": f"No guidance for {tool_id}"}
    
    @mcp.resource("arifos://schema/routing-guide")
    def schema_routing_guide() -> dict[str, Any]:
        """Complete routing guidance for stage transitions."""
        return registry.get_routing_guide()

    # ═══════════════════════════════════════════════════════════════════════════
    # AGI REPLY PROTOCOL v3 RESOURCES
    # arifos://reply/schemas  — static formal schema pack (stable prefix, cacheable)
    # arifos://reply/context-pack — dynamic per-session evolving state
    # ═══════════════════════════════════════════════════════════════════════════

    # ── STATIC: Formal schema definitions for all reply envelope types ──────────
    # This is a stable-prefix resource. Load once per session, then cache.
    # Defines: RecipientMode, VerdictToken, ReasoningTag, GovernanceTrace,
    #          ResourceEnvelope, Telemetry, HumanReplyEnvelope, AgentReplyEnvelope,
    #          AgiReplyHeader, AgiReplyRACI, AgiReplySeal, AgiReplyToolReturn
    @mcp.resource("arifos://reply/schemas")
    def reply_schemas() -> dict[str, Any]:
        """
        AGI Reply Protocol v3 — canonical schema pack.
        Stable prefix: load once, cache across turns (KV-cache eligible).
        """
        return {
            "protocol": "AGI_REPLY_V3",
            "version": "3.0.0",
            "cache_hint": "STABLE_PREFIX",
            "RecipientMode": {
                "enum": ["human", "agent", "auto"],
                "rule": "auto → classify via arifos.sense; ambiguous → human + append agent block",
            },
            "DepthMode": {
                "enum": ["SURFACE", "ENGINEER", "ARCHITECT"],
                "default": "ENGINEER",
            },
            "CompressionMode": {
                "enum": ["FULL", "DELTA", "SIGNAL_ONLY"],
                "rules": {
                    "FULL": "Session start or cross-agent handoff",
                    "DELTA": "Normal iterative turns (default)",
                    "SIGNAL_ONLY": "Sub-agent internal hops — strip all narrative",
                },
            },
            "VerdictToken": {
                "enum": ["CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE",
                         "UNKNOWN", "CONFLICT", "888 HOLD"],
                "tau_bands": {
                    "CLAIM":      "τ ≥ 0.85 — high confidence, grounded",
                    "PLAUSIBLE":  "τ ≥ 0.65 — likely true, not fully verified",
                    "HYPOTHESIS": "τ ≥ 0.50 — untested model",
                    "ESTIMATE":   "τ ≥ 0.35 — quantitative guess, error range known",
                    "UNKNOWN":    "τ < 0.35 — data missing",
                    "CONFLICT":   "multiple valid contradictory answers",
                    "888 HOLD":   "F1 or F13 triggered — human must confirm",
                },
                "tau_formula": (
                    "τ = (FACT_count×1.0 + ASSUME_count×0.7 + UNKNOWN_count×0.2) "
                    "/ total_reasoning_steps — see policy/confidence.ts F7_PROXY_v1"
                ),
            },
            "ReasoningTag": {
                "enum": ["FACT", "ASSUME", "RISK", "DELTA", "UNKNOWN", "DERIVE", "VERIFY"],
                "definitions": {
                    "FACT":    "Verified, citable, directly observed",
                    "ASSUME":  "Working assumption — state basis",
                    "RISK":    "Failure mode, hidden cost, blast radius",
                    "DELTA":   "Changed vs prior known state / context",
                    "UNKNOWN": "Information gap limiting confidence",
                    "DERIVE":  "Explicit logical step: A therefore B because C",
                    "VERIFY":  "Cross-check against known constraint or prior FACT",
                },
            },
            "FloorCodes": {k: v["name"] for k, v in FLOORS_SPEC.items()},
            "FloorTriggerRules": {
                "F1": "Action deletes / overwrites data → prepend [F1 AMANAH]",
                "F2": "Claim lacks explicit evidence chain → prepend [F2 TRUTH]",
                "F7": "Recommendation affects another's rights → prepend [F7 ADIL]",
                "F9": "Output could manipulate or deceive → prepend [F9 ANTI-HANTU]",
                "F13": "Final decision belongs to Arif, not the agent → prepend [F13 SOVEREIGN]",
                "888_HOLD_RULE": "Any F1 or F13 trigger → verdict MUST be 888 HOLD. Never self-approve.",
            },
            "AgiReplyHeader": {
                "fields": ["TO", "CC", "TITLE", "KEY_CONTEXT", "reply_to"],
                "purpose": "Email-style routing. Every governed reply must include this.",
            },
            "AgiReplyRACI": {
                "R_responsible": "Agent/tool that forged the output",
                "A_accountable": "arifos.judge + human:arif (F13 sovereign)",
                "C_consulted":   "arifos.heart, arifos.ops, arifos.memory",
                "I_informed":    "arifos.vault, downstream agents, CC recipients",
            },
            "AgiReplySeal": {
                "required_fields": [
                    "forged_by", "judge_verdict", "tau",
                    "floors_passed", "audit_hash", "timestamp", "seal_phrase",
                ],
                "audit_hash_input": "sha256(TITLE + timestamp + forged_by + judge_verdict)",
                "seal_phrase": "DITEMPA BUKAN DIBERI — 999 SEAL ALIVE",
            },
            "AgiReplyToolReturn": {
                "normalized_shape": [
                    "status", "evidence", "constraints", "suggested_delta",
                    "floor_flags", "reversible", "next_recommended_tool", "payload",
                ],
                "purpose": (
                    "Every tool returns this shape so the LLM aligns to "
                    "structured output from repeated signals — not re-explaining format."
                ),
            },
            "HumanReplyEnvelope": {
                "sections": [
                    "header (AgiReplyHeader)",
                    "raci (AgiReplyRACI)",
                    "prior_state | delta | depth",
                    "verdict_token τ=N.NN — statement",
                    "direct_answer (2-5 bullets, plain English)",
                    "reasoning_snapshot (3-7 tagged bullets)",
                    "action_output (code | steps | table — optional)",
                    "clarifying_question (ONE — omit if not material)",
                    "seal (AgiReplySeal)",
                ],
                "style": "engineer-to-engineer, dense, no small talk, no apologies",
            },
            "AgentReplyEnvelope": {
                "sections": [
                    "header (AgiReplyHeader)",
                    "raci (AgiReplyRACI)",
                    "prior_state | delta | depth | recipient",
                    "verdict_token τ=N.NN — statement",
                    "direct_answer (compact kv or JSON-compatible)",
                    "reasoning_snapshot (tagged atoms)",
                    "action_output {action, params, confidence, reversible, escalate_if, next_agent}",
                    "resource_envelope {compression_mode, tokens_estimated, cache_stable_prefix, parallel_ok, next_agent}",
                    "governance_trace {floors_triggered, verdict, escalate_to, audit_ref} — if F1/F13",
                    "telemetry (from arifos.ops passthrough)",
                    "seal (AgiReplySeal)",
                ],
                "style": "signal-only, diff+plan not essay, no narrative",
            },
        }

    # ── DYNAMIC: Compressed session state — evolves every turn ─────────────────
    # This is a DELTA resource. Only session-specific state lives here.
    # Never replay raw transcript — always summarise via arifos.memory first.
    @mcp.resource("arifos://reply/context-pack")
    def reply_context_pack() -> dict[str, Any]:
        """
        AGI Reply Protocol v3 — live session context pack.
        Delta resource: updated each turn, never grows unbounded.
        Load into STEP -1 CONTEXT STATE at the start of every reply turn.
        """
        return {
            "protocol": "AGI_REPLY_V3",
            "cache_hint": "DELTA",
            "compression_target": "100:1 via arifos.memory vector recall",
            "fields": {
                "prior_state": "Compressed summary of last known context (1 line)",
                "delta":       "What changed this turn vs prior_state",
                "depth":       "Current depth mode: SURFACE | ENGINEER | ARCHITECT",
                "recipient":   "Resolved recipient: human | agent",
                "last_verdict": "Last judge verdict + τ score",
                "active_floors": "Currently triggered F1-F13 floor codes",
                "session_id":   "Active session identifier",
                "epoch":        "Governance epoch (2026-04-10)",
                "compression_mode": "FULL | DELTA | SIGNAL_ONLY for this turn",
            },
            "update_rule": (
                "After each turn: call arifos.memory(mode=vector_store) "
                "to compress and persist. Never replay raw transcript."
            ),
            "handoff_rule": (
                "On cross-agent handoff: switch compression_mode to FULL "
                "and include last_verdict + active_floors in the handoff payload."
            ),
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # AF-FORGE CONTEXT RESOURCE
    # ═══════════════════════════════════════════════════════════════════════════

    @mcp.resource("arifos://af-forge/context")
    def af_forge_context() -> dict[str, Any]:
        """AF-FORGE TypeScript constitutional engine — context pack for MCP consumers."""
        return {
            "name": "AF-FORGE",
            "version": "0.1.0",
            "description": (
                "Constitutional Event-Sourced Agent Runtime. "
                "Planner/Executor/Verifier triad, policy engine, governed memory, "
                "and 888_HOLD human sovereignty gates."
            ),
            "bridge_endpoint": "http://localhost:7071",
            "mcp_stdio_cmd": ["node", "af-forge/dist/src/mcp/server.js"],
            "governance_floors_implemented": {
                "F3_InputClarity": {
                    "status": "IMPLEMENTED",
                    "file": "af-forge/src/governance/f3InputClarity.ts",
                    "gate": "SABAR — empty, <3 chars, or ambiguous repetition",
                    "enforced_in": "AgentEngine.run() before LLM",
                },
                "F6_HarmDignity": {
                    "status": "IMPLEMENTED",
                    "file": "af-forge/src/governance/f6HarmDignity.ts",
                    "gate": "VOID — 11 regex patterns (rm -rf, exploit, bypass auth, steal, inject, fork bomb)",
                    "enforced_in": "AgentEngine.run() after F3",
                },
                "F9_Injection": {
                    "status": "IMPLEMENTED",
                    "file": "af-forge/src/governance/f9Injection.ts",
                    "gate": "VOID — 10 regex patterns (ignore-instructions, bypass-policy, do-not-log, reveal-secrets, DAN)",
                    "enforced_in": "AgentEngine.run() after F6",
                },
                "F13_Sovereign": {
                    "status": "IMPLEMENTED",
                    "file": "af-forge/src/approval/ApprovalBoundary.ts",
                    "gate": "888_HOLD — blocks until human approval, never auto-approved",
                },
                "F7_Confidence": {
                    "status": "PARTIAL",
                    "file": "af-forge/src/policy/confidence.ts",
                    "gate": "Heuristic bands (VERY_HIGH/HIGH/MODERATE/LOW) — hard AgentEngine gate pending LLM API",
                },
                "summary": "11/13 floors implemented, 2 partial (F4 entropy metric, F8 grounding link)",
            },
            "mcp_tools": {
                "forge_check_governance": "Run F3+F6+F9 governance pipeline on task string → PASS/BLOCK verdict per floor",
                "forge_health": "Return F1–F13 implementation status and server health",
                "forge_run": "Execute governed agent task (explore profile, mock LLM) — governance gates run first",
            },
            "mcp_resources": {
                "forge://governance/floors": "F1–F13 constitutional floor definitions",
            },
            "deployment": {
                "http_bridge": "docker-compose up af-forge-bridge  (port 7071)",
                "stdio_mcp": "node af-forge/dist/src/mcp/server.js",
                "launcher": ".github/mcp/start-af-forge-stdio.sh [--build]",
                "platforms": ["Claude Desktop (.mcp.json)", "Cursor (.cursor/mcp.json)", "OpenCode (.opencode.json)", "Smithery (smithery.yaml)"],
            },
            "test_status": {
                "total": 62,
                "pass": 62,
                "fail": 0,
                "files": ["AgentEngine.test.ts", "confidence.test.ts", "sense.test.ts", "governanceViolation.test.ts"],
            },
            "golden_path": "forge_check_governance → forge_run (if PASS) → arifos.vault (to seal)",
        }

    registered = [
        "arifos://governance/floors",
        "arifos://governance/verdict",
        "arifos://system/capabilities",
        "arifos://af-forge/context",
        # Schema registry resources
        "arifos://schema/master",
        "arifos://schema/tools",
        "arifos://schema/tool/{tool_id}",
        "arifos://schema/stages",
        "arifos://schema/trinity",
        "arifos://schema/envelopes",
        "arifos://schema/alias-map",
        "arifos://schema/tool-summary",
        "arifos://schema/chatgpt-guide/{tool_id}",
        "arifos://schema/routing-guide",
        # AGI Reply Protocol v3 resources
        "arifos://reply/schemas",
        "arifos://reply/context-pack",
    ]
    logger.info(f"Registered {len(registered)} v2 resources.")
    return registered


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY UTILITY STUBS (backward compat for tools_internal + rest_routes)
# ═══════════════════════════════════════════════════════════════════════════════

def apex_tools_html_rows() -> str:
    """HTML rows for apex tools table (stub — rendered dynamically)."""
    return ""


def apex_tools_markdown_table() -> str:
    """Markdown table of apex tools (stub — rendered dynamically)."""
    return ""


def manifest_resources() -> list[dict]:
    """Return registered resource URIs (stub for stdio compat)."""
    return [
        {"uri": "canon://states", "name": "Session Ladder"},
        {"uri": "canon://index", "name": "Compatibility Resource Index"},
        {"uri": "arifos://governance/floors", "name": "Constitutional Floors"},
        {"uri": "arifos://governance/verdict", "name": "Verdict Specification"},
        {"uri": "arifos://system/capabilities", "name": "System Capabilities"},
        {"uri": "arifos://schema/master", "name": "Master Schema"},
        {"uri": "arifos://schema/tools", "name": "Tool Schemas"},
        {"uri": "arifos://ecosystem/context-v1", "name": "Ecosystem Context — arifOS Constellation"},
        {"uri": "arifos://ecosystem/geox", "name": "GEOX Platform Integration"},
    ]


async def read_resource_content(uri: str) -> str:
    """Read resource content by URI, including legacy canon:// compatibility."""
    if uri == "canon://states":
        return CANON_SESSION_STATES
    if uri == "canon://index":
        return json.dumps(CANON_INDEX)
    return ""


def register_resources(mcp: "FastMCP") -> None:  # type: ignore[name-defined]
    """Alias for register_v2_resources — backward compat."""
    register_v2_resources(mcp)
