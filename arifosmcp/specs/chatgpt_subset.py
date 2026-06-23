"""
arifOS MCP ChatGPT Subset Adapter
═══════════════════════════════════════════════════════════════════════════════

Apps SDK-safe subset of arifOS capabilities.

Phase 1 (Current): Read-only health checks
Phase 2 (Future): Write-path with explicit L11/L13 review

Principles:
- Only read-only tools in Phase 1
- No vault sealing without human approval
- No VPS execution paths
- Clean mapping from canonical contracts to Apps SDK shapes
"""

from __future__ import annotations

from typing import Any

from arifosmcp.specs.contracts import (
    ConstitutionalHealthView,
    VerdictCode,
)
from arifosmcp.specs.resource_specs import get_resource_spec
from arifosmcp.specs.tool_specs import get_tool_spec

# ═══════════════════════════════════════════════════════════════════════════════
# CHATGPT-SAFE SUBSETS
# ═══════════════════════════════════════════════════════════════════════════════

# Tools exposed to ChatGPT (read-only in Phase 1)
CHATGPT_TOOL_NAMES: tuple[str, ...] = (
    "get_constitutional_health",  # Data tool: health card
    "render_vault_seal",  # Render tool: widget UI
    "list_recent_verdicts",  # Read-only vault summary
)

# Resources exposed to ChatGPT
CHATGPT_RESOURCE_URIS: tuple[str, ...] = (
    "arifos://doctrine",
    "arifos://vitals",
    "arifos://schema",
    "arifos://forge",
)

# Prompts exposed to ChatGPT
CHATGPT_PROMPT_NAMES: tuple[str, ...] = (
    "prompt_init_anchor",
    "prompt_sense_reality",
    "prompt_reason_synthesis",
    "prompt_human_explainer",
)


# ════════════════════════════════════════════════════════════════════════════════
# CHATGPT-TOOL ALIASES (added 2026-06-03 — ChatGPT connector backward-compat)
# ════════════════════════════════════════════════════════════════════════════════
#
# Maps legacy/phantom tool names that may appear in stale ChatGPT connector
# manifests to the canonical arifOS tool names + default arguments.
#
# Use case: ChatGPT connector caches an older arifOS manifest. The user
# refreshes the connector (Option A) AND we ship alias resolution
# (Option B) so legacy names still resolve during the transition.
#
# 4 phantom tools are INTENTIONALLY ABSENT (REFUSED) — they would be
# F7 (no system destruction) or L13 (sovereign veto) violations:
#   - arif_run        : would be an executor, F7 STEWARDSHIP
#   - arif_exec       : would be an executor, F7 STEWARDSHIP
#   - arif_sudo       : would bypass authority, L13 SOVEREIGN
#   - arif_systemctl  : would mutate production, F7 + L13

CHATGPT_TOOL_ALIASES: dict[str, dict[str, str]] = {
    # floor_status → kernel_route with mode=floor_status (read-only)
    "arif_floor_status": {
        "canonical_tool": "arif_kernel_route",
        "mode": "floor_status",
        "rationale": "Floor status is a read-only view of the F1-L13 kernel state.",
    },
    # apex_judge → gateway_connect routing to APEX deliberation engine
    "arif_apex_judge": {
        "canonical_tool": "arif_gateway_connect",
        "target_agent": "apex",
        "mode": "route",
        "rationale": "APEX 888 JUDGE is reachable via gateway_connect (port 3002).",
    },
    # vault_integrity → memory_recall with read-only dry_run trace
    "arif_vault_integrity": {
        "canonical_tool": "arif_memory_recall",
        "mode": "trace",
        "dry_run": "true",
        "rationale": "Vault integrity is a read-only trace of the sealed ledger; "
        "memory_recall(mode=trace, dry_run=true) is the safe path.",
    },
}

# Phantom tools that will never be aliased (constitution refuses them)
CHATGPT_REFUSED_TOOLS: frozenset[str] = frozenset(
    {
        "arif_run",  # F7 — would be an executor
        "arif_exec",  # F7 — would be an executor
        "arif_sudo",  # L13 — would bypass authority
        "arif_systemctl",  # F7 + L13 — would mutate production
    }
)


def resolve_chatgpt_alias(tool_name: str) -> dict[str, str] | None:
    """Resolve a legacy/phantom tool name to canonical arifOS tool + args.

    Returns the alias mapping dict (with `canonical_tool` + args) if found.
    Returns None if the tool name is not a known alias.

    Refused tools (arif_run, arif_exec, arif_sudo, arif_systemctl) return
    None — the caller should reject them with a constitutional HOLD and
    return a 9-signal verdict of KHIANAT (betrayed) / BANGANG (foolish).

    Example:
        >>> resolve_chatgpt_alias("arif_floor_status")
        {"canonical_tool": "arif_kernel_route", "mode": "floor_status", ...}
        >>> resolve_chatgpt_alias("arif_run")
        None  # refused by F7/L13
    """
    if tool_name in CHATGPT_REFUSED_TOOLS:
        return None
    return CHATGPT_TOOL_ALIASES.get(tool_name)


def is_chatgpt_refused_tool(tool_name: str) -> bool:
    """Check if a tool name is constitutionally refused (F7/L13)."""
    return tool_name in CHATGPT_REFUSED_TOOLS


# ═══════════════════════════════════════════════════════════════════════════════
# SAFETY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════


def is_chatgpt_safe_tool(tool_name: str) -> bool:
    """Check if a tool is safe for ChatGPT Apps SDK exposure."""
    return tool_name in CHATGPT_TOOL_NAMES


def is_chatgpt_safe_resource(uri: str) -> bool:
    """Check if a resource is safe for ChatGPT Apps SDK exposure."""
    return uri in CHATGPT_RESOURCE_URIS


def is_chatgpt_safe_prompt(prompt_name: str) -> bool:
    """Check if a prompt is safe for ChatGPT Apps SDK exposure."""
    return prompt_name in CHATGPT_PROMPT_NAMES


def validate_chatgpt_safety() -> dict[str, Any]:
    """
    Validate that ChatGPT subset is actually safe.

    Returns audit report with any violations found.
    """
    violations = []

    # Check that no non-readonly tools slipped in
    for tool_name in CHATGPT_TOOL_NAMES:
        spec = get_tool_spec(tool_name)
        if spec and not spec.read_only_hint:
            violations.append(
                {
                    "type": "tool_not_readonly",
                    "name": tool_name,
                    "severity": "high",
                    "message": f"Tool {tool_name} is not marked read_only but is in ChatGPT subset",
                }
            )

    # Check that no high-auth resources slipped in
    for uri in CHATGPT_RESOURCE_URIS:
        spec = get_resource_spec(uri)
        if spec and spec.auth_required not in ("anonymous", "anchored"):
            violations.append(
                {
                    "type": "resource_high_auth",
                    "uri": uri,
                    "severity": "medium",
                    "message": f"Resource {uri} requires {spec.auth_required} but is in ChatGPT subset",
                }
            )

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "tool_count": len(CHATGPT_TOOL_NAMES),
        "resource_count": len(CHATGPT_RESOURCE_URIS),
        "prompt_count": len(CHATGPT_PROMPT_NAMES),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CHATGPT-SPECIFIC TOOL SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════


def get_constitutional_health_schema() -> dict[str, Any]:
    """
    Schema for get_constitutional_health tool.

    Returns structured health card with human-readable labels.
    """
    return {
        "name": "get_constitutional_health",
        "title": "Constitutional Health Check",
        "description": (
            "Get current constitutional health snapshot. "
            "Returns floor scores, verdict, and attestation status. "
            "Read-only — safe for all sessions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "PARTIAL", "VOID", "SABAR"],
                    "default": "SEAL",
                    "description": "Requested verdict mode",
                },
                "include_history": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include recent verdict history",
                },
            },
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
        },
    }


def render_vault_seal_schema() -> dict[str, Any]:
    """
    Schema for render_vault_seal tool.

    Render tool that returns widget URL for ChatGPT UI.
    Widget hosted on https://mcp.a-forge.io with CSP headers.
    """
    WIDGET_URL = "https://mcp.a-forge.io/widget/vault-seal"

    return {
        "name": "render_vault_seal",
        "title": "Render Vault Seal",
        "description": (
            "Display constitutional health as interactive widget. "
            "Served from https://mcp.a-forge.io with strict CSP."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "seal_data": {
                    "type": "object",
                    "description": "Constitutional health data to render",
                }
            },
        },
        "annotations": {
            "readOnlyHint": True,
        },
        "_meta": {
            "ui": {"resourceUri": WIDGET_URL, "visibility": "user"},
            "openai": {"outputTemplate": WIDGET_URL},
        },
    }


def list_recent_verdicts_schema() -> dict[str, Any]:
    """
    Schema for list_recent_verdicts tool.

    Read-only summary of recent vault entries.
    """
    return {
        "name": "list_recent_verdicts",
        "title": "Recent Verdicts",
        "description": (
            "List recent constitutional verdicts (last 100). "
            "Read-only audit log with anonymized metrics. "
            "No sensitive data exposed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
                "verdict_filter": {
                    "type": "string",
                    "enum": ["all", "SEAL", "PARTIAL", "VOID", "SABAR", "HOLD"],
                    "default": "all",
                },
            },
        },
        "annotations": {
            "readOnlyHint": True,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CHATGPT MANIFEST
# ═══════════════════════════════════════════════════════════════════════════════


def _live_surface_tool_schemas() -> list[dict[str, Any]]:
    """
    Derive ChatGPT-compatible tool schemas from the live arifOS public surface.

    This keeps the ChatGPT Apps SDK manifest synchronized with the canonical
    MCP wire surface (short names + SDK long-name aliases + canary probe).
    """
    from arifosmcp.runtime.public_registry import public_tool_specs

    schemas: list[dict[str, Any]] = []
    for spec in public_tool_specs("canonical13"):
        input_schema = getattr(spec, "input_schema", None) or {"type": "object", "properties": {}}
        schemas.append(
            {
                "name": spec.name,
                "title": spec.name,
                "description": spec.description,
                "inputSchema": input_schema,
                "annotations": {"readOnlyHint": getattr(spec, "access", "public") != "sovereign"},
            }
        )
    return schemas


def get_chatgpt_manifest() -> dict[str, Any]:
    """
    Build complete ChatGPT Apps SDK manifest.

    This is the contract between arifOS and OpenAI's platform.
    The executable tool list is derived from the live public MCP surface so
    the connector never drifts from the canonical wire names.
    """
    live_tools = _live_surface_tool_schemas()
    live_tool_names = [t["name"] for t in live_tools]
    chatgpt_tools = [
        get_constitutional_health_schema(),
        render_vault_seal_schema(),
        list_recent_verdicts_schema(),
    ]
    return {
        "schema_version": "2026.04.06",
        "name": "arifOS Constitutional Health",
        "description": (
            "Constitutional AI governance health checks via arifOS. "
            "Inspect floor scores, verdicts, and attestation status. "
            "Phase 1: Read-only. Phase 2: Write with L11/L13 review."
        ),
        "vendor": {"name": "Muhammad Arif bin Fazil", "url": "https://arif-fazil.com"},
        "capabilities": {
            "tools": list(CHATGPT_TOOL_NAMES) + live_tool_names,
            "resources": list(CHATGPT_RESOURCE_URIS),
            "prompts": list(CHATGPT_PROMPT_NAMES),
        },
        "tools": chatgpt_tools + live_tools,
        "resources": [
            {
                "uri": uri,
                "name": get_resource_spec(uri).name if get_resource_spec(uri) else uri,
            }
            for uri in CHATGPT_RESOURCE_URIS
        ],
        "safety": {
            "phase": 1,
            "read_only": True,
            "888_hold_active": True,
            "max_risk_tier": "medium",
            "requires_human_approval_for_write": True,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAPPING TO CANONICAL CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════


def map_chatgpt_health_to_canonical(
    chatgpt_health: dict[str, Any],
) -> ConstitutionalHealthView:
    """
    Map ChatGPT health response to canonical ConstitutionalHealthView.

    This ensures ChatGPT and internal APIs speak the same contract.
    """
    return ConstitutionalHealthView(
        session_id=chatgpt_health.get("session_id", "anonymous"),
        timestamp=chatgpt_health.get("timestamp", ""),
        truth_score=chatgpt_health.get("truth_score", 0.95),
        humility_level=chatgpt_health.get("humility_level", 0.05),
        entropy_delta=chatgpt_health.get("entropy_delta", 0.0),
        harmony_ratio=chatgpt_health.get("harmony_ratio", 1.0),
        reality_index=chatgpt_health.get("reality_index", 0.9),
        witness_strength=chatgpt_health.get("witness_strength", 0.0),
        verdict=VerdictCode(chatgpt_health.get("verdict", "SABAR")),
        verdict_label=_verdict_to_label(chatgpt_health.get("verdict", "SABAR")),
        attestation=chatgpt_health.get("attestation"),
    )


def _verdict_to_label(verdict: str) -> str:
    """Convert verdict code to human label."""
    labels = {
        "SEAL": "Aligned",
        "PARTIAL": "Partial",
        "VOID": "Rejected",
        "SABAR": "Pending",
        "HOLD": "Escalated",
    }
    return labels.get(verdict, "Unknown")


__all__ = [
    # Subsets
    "CHATGPT_TOOL_NAMES",
    "CHATGPT_RESOURCE_URIS",
    "CHATGPT_PROMPT_NAMES",
    # Aliases (added 2026-06-03 — ChatGPT connector backward-compat)
    "CHATGPT_TOOL_ALIASES",
    "CHATGPT_REFUSED_TOOLS",
    "resolve_chatgpt_alias",
    "is_chatgpt_refused_tool",
    # Safety checks
    "is_chatgpt_safe_tool",
    "is_chatgpt_safe_resource",
    "is_chatgpt_safe_prompt",
    "validate_chatgpt_safety",
    # Schemas
    "get_constitutional_health_schema",
    "render_vault_seal_schema",
    "list_recent_verdicts_schema",
    # Manifest
    "get_chatgpt_manifest",
    # Mapping
    "map_chatgpt_health_to_canonical",
]
