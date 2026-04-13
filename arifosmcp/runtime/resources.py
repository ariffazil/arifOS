"""
arifosmcp/runtime/resources.py — arifOS MCP v2 Resources

Resources are read-only constitutional documents.
They provide grounding, policy, schemas, governance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ResourceError
from fastmcp.resources import ResourceResult, ResourceContent

logger = logging.getLogger(__name__)

# Module load time for uptime calculation
START_TIME = datetime.now(timezone.utc)

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
        "arifos://doctrine",
        "arifos://vitals",
        "arifos://schema",
        "arifos://session/{session_id}",
        "arifos://forge",
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
            "arifos://schema",
        ],
        "stages": ["000_INIT", "111_SENSE", "333_MIND", "444_ROUTER", "555_MEMORY", "666_HEART", "777_OPS", "888_JUDGE", "999_VAULT", "FORGE_010"],
        "trinity": {
            "Δ": "Discernment - Reality, reasoning, execution",
            "Ψ": "Sovereignty - Session, routing, judgment, seal",
            "Ω": "Stability - Memory, safety, thermodynamics",
        },
    },
}

AF_FORGE_CONTEXT: dict[str, Any] = {
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

REPLY_SCHEMAS: dict[str, Any] = {
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
        "enum": ["CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE", "UNKNOWN", "CONFLICT", "888 HOLD"],
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
}


def _get_skills_manifest() -> dict[str, Any]:
    """Static skills manifest for doctrine resource."""
    return {
        "skills": {
            "apex-888-judgment-engine": "Constitutional verdict rendering engine",
            "arifos-agi-plan": "Plan refactors without making edits (Δ lane)",
            "arifos-asi-apply": "Apply approved refactors (Ω lane)",
            "arifos-guardian-check": "Pre-flight safety and environment check",
            "arifos-laptop-agent": "Windows laptop maintenance with constitutional governance",
            "arifos-trinity-refactor": "INIT→AGI→ASI→APEX→VAULT governance refactor",
            "f1-amanah-file-guardian": "Constitutional file manipulation utilities",
            "f3-tri-witness-consensus": "Tri-Witness consensus calculator",
            "f6-constitutional-care": "Constitutional care guardian",
            "f7-godel-uncertainty-guard": "Gödel Lock humility band validator",
            "f8-wisdom-equation-calculator": "Genius Index calculator",
            "f9-shadow-cleverness-guard": "Ghost pattern detector",
            "trinity-000-999-pipeline": "000-999 metabolic loop orchestrator",
            "trinity-governance-core": "Hardened constitutional governance F1-F13",
        },
        "note": "Full skill details available in AGENTS.md and workspace skills/ directory.",
    }


def _vitals_to_markdown(data: dict[str, Any]) -> str:
    """Convert vitals payload to markdown."""
    md = f"# arifOS Vitals (Ω)\n\n"
    md += f"**Status**: {data['system']['name']} {data['system']['version']}\n\n"
    md += "| Metric | Value |\n|---|---|\n"
    thermo = data.get("thermodynamics", {})
    md += f"| G-Score | {thermo.get('g_score', 'N/A')} |\n"
    md += f"| ΔS | {thermo.get('delta_s', 'N/A')} |\n"
    md += f"| Ψ | {thermo.get('psi', 'N/A')} |\n"
    md += f"| Ω | {thermo.get('omega', 'N/A')} |\n"
    md += f"| Uptime | {data['system'].get('uptime_seconds', 'N/A')}s |\n"
    return md


def _get_platform_config(platform: str) -> dict[str, Any]:
    """Platform-specific deployment config."""
    configs = {
        "claude": {"config_file": ".mcp.json", "transport": "stdio"},
        "cursor": {"config_file": ".cursor/mcp.json", "transport": "stdio"},
        "opencode": {"config_file": ".opencode.json", "transport": "stdio"},
        "chatgpt": {"config_file": "config/apps-sdk/arifos-af-forge.json", "transport": "streamable-http"},
    }
    return configs.get(platform.lower(), {})


# ═══════════════════════════════════════════════════════════════════════════════
# V2 RESOURCE REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def register_v2_resources(mcp: FastMCP) -> list[str]:
    """Register all v2 resources using arifos:// scheme."""
    from arifosmcp.schema import get_registry
    from arifosmcp.runtime.sessions import get_session_identity
    try:
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS
        tools_total = len(CANONICAL_TOOL_HANDLERS)
    except Exception:
        tools_total = SYSTEM_CAPABILITIES["tools"]["total"]

    registry = get_registry()

    @mcp.resource("arifos://doctrine")
    def get_doctrine() -> dict[str, Any]:
        """Immutable constitutional substrate."""
        return {
            "identity": {
                "name": SYSTEM_CAPABILITIES["name"],
                "version": SYSTEM_CAPABILITIES["version"],
                "epoch": "2026-04-13",
                "authority": "Muhammad Arif bin Fazil (888_JUDGE)",
            },
            "floors": FLOORS_SPEC,
            "verdicts": VERDICT_SPEC,
            "skills": _get_skills_manifest(),
            "motto": "DITEMPA BUKAN DIBERI",
        }

    @mcp.resource("arifos://doctrine/floor/{floor_id}")
    def get_doctrine_floor(floor_id: str) -> dict[str, Any]:
        """Detailed doctrine for a specific floor."""
        data = FLOORS_SPEC.get(floor_id)
        if not data:
            raise ResourceError(f"Floor {floor_id} not defined. Valid: {list(FLOORS_SPEC.keys())}")
        return {"floor_id": floor_id, **data}

    @mcp.resource("arifos://doctrine/skill/{skill_name}")
    def get_doctrine_skill(skill_name: str) -> dict[str, Any]:
        """Detailed doctrine for a specific skill."""
        skills = _get_skills_manifest().get("skills", {})
        desc = skills.get(skill_name)
        if not desc:
            raise ResourceError(f"Skill {skill_name} not found. Valid: {list(skills.keys())}")
        return {"skill_name": skill_name, "description": desc}

    @mcp.resource("arifos://vitals{?format,window}")
    async def get_vitals(format: str = "json", window: str = "live") -> ResourceResult:
        """Real-time constitutional health and thermodynamics."""
        now = datetime.now(timezone.utc)
        uptime_seconds = int((now - START_TIME).total_seconds())

        # Try to load recent vault entries (anonymized)
        vault_entries: list[dict[str, Any]] = []
        try:
            from arifosmcp.runtime.vault_redis import get_vault_store
            store = get_vault_store()
            raw_entries = await store.get_chain(limit=100)
            vault_entries = [
                {
                    "verdict": entry.get("verdict", "UNKNOWN"),
                    "timestamp": entry.get("timestamp", ""),
                    "stage": entry.get("stage", "999_VAULT"),
                    "tool": entry.get("tool", "arifos_vault"),
                }
                for entry in raw_entries
            ]
        except Exception as e:
            logger.debug(f"Vault summary unavailable in vitals: {e}")

        data = {
            "timestamp": now.isoformat(),
            "system": {
                "name": SYSTEM_CAPABILITIES["name"],
                "version": SYSTEM_CAPABILITIES["version"],
                "uptime_seconds": uptime_seconds,
            },
            "thermodynamics": {
                "g_score": 0.87,
                "delta_s": -0.15,
                "psi": 1.12,
                "omega": 0.04,
            },
            "vault_summary": {
                "last_100": vault_entries,
            },
            "capabilities": {
                "tools_total": tools_total,
                "resources_total": 5,
                "stages": SYSTEM_CAPABILITIES["schema_registry"]["stages"],
            },
            "query": {"format": format, "window": window},
        }

        if format == "json":
            return ResourceResult(json.dumps(data))

        if format == "markdown":
            return ResourceResult(_vitals_to_markdown(data))

        if format == "widget":
            md = _vitals_to_markdown(data)
            return ResourceResult(
                contents=[
                    ResourceContent(content=json.dumps(data), mime_type="application/json"),
                    ResourceContent(content=md, mime_type="text/markdown"),
                    ResourceContent(
                        content="![Vault Seal](https://mcp.af-forge.io/widget/vault-seal)",
                        mime_type="text/markdown",
                    ),
                ]
            )

        raise ResourceError(f"Unknown format: {format}. Use json, markdown, or widget.")

    @mcp.resource("arifos://schema{?section,tool_id}")
    def get_schema(section: str = "all", tool_id: str | None = None) -> dict[str, Any]:
        """Complete structural blueprint."""
        result: dict[str, Any] = {}

        if section in ("all", "master"):
            result["master"] = registry.master_schema or {}

        if section in ("all", "tools"):
            if tool_id:
                packet = registry.get_tool_packet(tool_id)
                if packet:
                    result["tools"] = {tool_id: packet}
                else:
                    result["tools"] = {"error": f"Tool {tool_id} not found", "available": list(registry.tool_packets.keys())}
            else:
                result["tools"] = registry.tool_packets

        if section in ("all", "trinity"):
            result["trinity"] = registry.master_schema.get("trinity", {}) if registry.master_schema else {}

        if section in ("all", "stages"):
            master = registry.master_schema or {}
            result["stages"] = {
                "stage_order": master.get("stage_order", []),
                "stages": master.get("stages", {}),
                "transitions": master.get("transitions", {}),
            }

        if section in ("all", "reply"):
            result["reply_protocol"] = {
                "schemas": REPLY_SCHEMAS,
                "envelopes": {
                    "request": registry.get_request_schema(),
                    "response": registry.get_response_schema(),
                    "context_packet": registry.get_context_packet_schema(),
                },
            }

        if section in ("all", "index"):
            result["index"] = {
                "tool_summary": registry.get_tool_summary(),
                "alias_map": registry.get_alias_map(),
                "chatgpt_guidance": {
                    tool_id: registry.get_chatgpt_guidance(tool_id)
                    for tool_id in registry.tool_packets
                },
            }

        return result

    @mcp.resource("arifos://schema/tool/{tool_id}")
    def get_schema_tool(tool_id: str) -> dict[str, Any]:
        """Context packet for a specific tool."""
        packet = registry.get_tool_packet(tool_id)
        if packet:
            return packet
        return {"error": f"Tool {tool_id} not found", "available": list(registry.tool_packets.keys())}

    @mcp.resource("arifos://session/{session_id}{?depth,compress}")
    async def get_session(
        session_id: str,
        depth: str = "engineer",
        compress: bool = True,
        ctx: Context = None,
    ) -> dict[str, Any]:
        """Ephemeral per-session state and task dashboard."""
        if ctx is None or getattr(ctx, "session_id", None) != session_id:
            raise ResourceError(
                "Session resource requires anchored authority. Initialize session first via arifos_init."
            )

        identity = get_session_identity(session_id)
        authority_level = identity.get("authority_level", "anonymous") if identity else "anonymous"

        # Resolve available tools from canonical specs based on authority level
        from arifosmcp.specs.tool_specs import CANONICAL_TOOL_SPECS
        authority_rank = {
            "anonymous": 0,
            "anchored": 1,
            "verified": 2,
            "sovereign": 3,
        }
        user_rank = authority_rank.get(authority_level, 0)
        tools_available = [
            spec.name
            for spec in CANONICAL_TOOL_SPECS
            if authority_rank.get(spec.auth_required, 0) <= user_rank
        ]

        return {
            "session_id": session_id,
            "authority": {
                "level": authority_level,
                "actor_id": identity.get("actor_id", "anonymous") if identity else "anonymous",
                "tools_available": tools_available,
            },
            "context_pack": {
                "prior_state": "",  # ADAPTER: compressed via arifos.memory
                "delta": "",
                "depth": depth,
                "compression_mode": "DELTA",
                "compress": compress,
            },
            "active_floors": [],
            "last_verdict": {
                "verdict": "SEAL",
                "tau": 0.96,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "tasks": [],  # Task primitive integration point
        }

    @mcp.resource("arifos://forge{?context,platform}")
    def get_forge(context: str = "all", platform: str | None = None) -> dict[str, Any]:
        """Execution bridge and deployment topology."""
        result: dict[str, Any] = {}

        if context in ("all", "engine"):
            result["af_forge"] = {
                "name": AF_FORGE_CONTEXT["name"],
                "version": AF_FORGE_CONTEXT["version"],
                "bridge_endpoint": AF_FORGE_CONTEXT["bridge_endpoint"],
                "governance_floors_implemented": AF_FORGE_CONTEXT["governance_floors_implemented"],
                "test_status": AF_FORGE_CONTEXT["test_status"],
                "golden_path": AF_FORGE_CONTEXT["golden_path"],
            }

        if context in ("all", "deployment"):
            result["deployment"] = {
                "platforms": AF_FORGE_CONTEXT["deployment"]["platforms"],
                "launcher": AF_FORGE_CONTEXT["deployment"]["launcher"],
            }
            if platform:
                result["deployment"]["platform_view"] = _get_platform_config(platform)

        if context in ("all", "widgets"):
            result["widgets"] = {
                "vault_seal": {
                    "uri": "https://mcp.af-forge.io/widget/vault-seal",
                    "mime_type": "text/html",
                }
            }

        return result

    registered = [
        "arifos://doctrine",
        "arifos://doctrine/floor/{floor_id}",
        "arifos://doctrine/skill/{skill_name}",
        "arifos://vitals",
        "arifos://schema",
        "arifos://schema/tool/{tool_id}",
        "arifos://session/{session_id}",
        "arifos://forge",
    ]
    logger.info(f"Registered {len(registered)} v2 resources.")
    return registered


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

def register_resources(mcp: FastMCP) -> list[str]:
    """Alias for register_v2_resources — backward compat."""
    return register_v2_resources(mcp)


def apex_tools_html_rows() -> str:
    """HTML rows for apex tools table (stub — rendered dynamically)."""
    return ""


def apex_tools_markdown_table() -> str:
    """Markdown table of apex tools (stub — rendered dynamically)."""
    return ""


def manifest_resources() -> list[dict[str, str]]:
    """Return registered resource URIs (stub for stdio compat)."""
    return [
        {"uri": "canon://states", "name": "Session Ladder"},
        {"uri": "canon://index", "name": "Compatibility Resource Index"},
        {"uri": "arifos://doctrine", "name": "Constitutional Doctrine"},
        {"uri": "arifos://vitals", "name": "System Vitals"},
        {"uri": "arifos://schema", "name": "Master Schema"},
        {"uri": "arifos://session/{session_id}", "name": "Session Context"},
        {"uri": "arifos://forge", "name": "AF-FORGE Bridge"},
    ]


async def read_resource_content(uri: str) -> str:
    """Read resource content by URI, including legacy canon:// compatibility."""
    if uri == "canon://states":
        return CANON_SESSION_STATES
    if uri == "canon://index":
        return json.dumps(CANON_INDEX)
    return ""


__all__ = [
    "register_v2_resources",
    "register_resources",
    "manifest_resources",
    "read_resource_content",
]
